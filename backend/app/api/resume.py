"""Resume upload and analysis router."""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import (
    CandidateEducation,
    CandidateExperience,
    CandidateSkill,
    Profile,
    Resume,
    User,
)
from app.schemas.schemas import CandidateSkillOut, ResumeAnalysisOut, ResumeOut
from app.services.resume_analyzer import analyze_resume
from app.utils.dependencies import get_current_user
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()
router = APIRouter(tags=["resume"])

ALLOWED_TYPES = {"application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
ALLOWED_EXTENSIONS = {".pdf", ".docx"}


def _get_file_type(filename: str, content_type: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return "pdf"
    elif ext == ".docx":
        return "docx"
    raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")


def _run_resume_analysis(resume: Resume, current_user: User, db: Session) -> ResumeAnalysisOut:
    """Execute parsing, skill extraction, and database persistence for a resume."""
    resume.status = "processing"
    db.commit()

    try:
        profile = analyze_resume(resume.file_path, resume.file_type)

        # Fallback to current user account email if email not found in resume text
        if not profile.email:
            profile.email = current_user.email

        # Store raw text and analysis result
        resume.raw_text = profile.raw_text
        resume.analysis_result = json.dumps(profile.to_dict())
        resume.status = "done"
        resume.processed_at = datetime.now(timezone.utc)

        # Update profile fields from resume
        db_profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
        if db_profile:
            if profile.name and not db_profile.full_name:
                db_profile.full_name = profile.name
            if profile.phone and not db_profile.phone:
                db_profile.phone = profile.phone
            if profile.total_experience_years:
                db_profile.experience_years = profile.total_experience_years

        # Clear and re-insert candidate skills
        db.query(CandidateSkill).filter(
            CandidateSkill.user_id == current_user.id,
            CandidateSkill.source == "resume",
        ).delete()

        from app.ai.skill_taxonomy import get_skill_category
        for skill_name in profile.skills:
            skill = CandidateSkill(
                user_id=current_user.id,
                skill_name=skill_name,
                skill_category=get_skill_category(skill_name),
                source="resume",
            )
            db.add(skill)

        # Clear and re-insert education
        db.query(CandidateEducation).filter(CandidateEducation.user_id == current_user.id).delete()
        for edu in profile.education:
            db.add(CandidateEducation(
                user_id=current_user.id,
                degree=edu.get("degree"),
                institution=edu.get("institution"),
                graduation_year=edu.get("graduation_year"),
                field_of_study=edu.get("grade") or edu.get("field_of_study"),
            ))

        # Clear and re-insert experience
        db.query(CandidateExperience).filter(CandidateExperience.user_id == current_user.id).delete()
        if profile.experience:
            for exp in profile.experience:
                db.add(CandidateExperience(
                    user_id=current_user.id,
                    job_title=exp.get("job_title"),
                    company=exp.get("company"),
                    duration_months=exp.get("duration_months", 0),
                    start_date=str(exp.get("start", "")),
                    end_date=str(exp.get("end", "")),
                ))
        elif profile.projects:
            # For candidates/freshers with academic and personal projects
            for proj in profile.projects:
                p_title = proj.get("title") if isinstance(proj, dict) else str(proj)
                p_desc = proj.get("description") if isinstance(proj, dict) else ""
                db.add(CandidateExperience(
                    user_id=current_user.id,
                    job_title=p_title,
                    company="Academic / Personal Project",
                    duration_months=6,
                    start_date="Project",
                    end_date="Completed",
                    description=p_desc,
                ))

        db.commit()

        logger.info(f"Resume analyzed for user {current_user.id}: {len(profile.skills)} skills found, {len(profile.education)} education, {len(profile.projects)} projects")

        return ResumeAnalysisOut(
            resume_id=resume.id,
            name=profile.name,
            email=profile.email,
            phone=profile.phone,
            skills=profile.skills,
            education=profile.education,
            experience=profile.experience,
            total_experience_years=profile.total_experience_years,
            job_titles=profile.job_titles,
            certifications=profile.certifications,
            projects=profile.projects,
            summary=profile.summary,
        )

    except Exception as e:
        resume.status = "error"
        db.commit()
        logger.error(f"Resume analysis failed for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail=f"Resume analysis failed: {str(e)}")


@router.post("/upload", response_model=ResumeOut, status_code=201)
async def upload_resume(
    file: UploadFile = File(...),
    auto_analyze: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Validate file type
    file_type = _get_file_type(file.filename or "", file.content_type or "")

    # Read and validate file size
    content = await file.read()
    if len(content) > settings.max_resume_bytes:
        raise HTTPException(status_code=413, detail=f"File too large. Max {settings.MAX_RESUME_SIZE_MB}MB allowed")

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Empty file")

    # Create safe stored filename
    safe_name = f"{uuid.uuid4().hex}.{file_type}"
    upload_path = Path(settings.UPLOAD_DIR)
    upload_path.mkdir(parents=True, exist_ok=True)
    file_path = upload_path / safe_name

    with open(file_path, "wb") as f:
        f.write(content)

    # Store resume record
    resume = Resume(
        user_id=current_user.id,
        filename=file.filename or safe_name,
        stored_filename=safe_name,
        file_path=str(file_path),
        file_type=file_type,
        file_size_bytes=len(content),
        status="pending",
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    logger.info(f"Resume uploaded: user={current_user.id}, file={safe_name}, type={file_type}")

    if auto_analyze:
        try:
            _run_resume_analysis(resume, current_user, db)
            db.refresh(resume)
        except Exception as e:
            logger.warning(f"Auto-analysis after upload failed: {e}")

    return resume


@router.post("/analyze", response_model=ResumeAnalysisOut)
def analyze_resume_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Analyze the most recently uploaded resume and update candidate profile."""
    resume = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id)
        .order_by(Resume.created_at.desc())
        .first()
    )
    if not resume:
        raise HTTPException(status_code=404, detail="No resume uploaded")

    return _run_resume_analysis(resume, current_user, db)


@router.get("", response_model=ResumeOut)
def get_resume(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    resume = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id)
        .order_by(Resume.created_at.desc())
        .first()
    )
    if not resume:
        raise HTTPException(status_code=404, detail="No resume found")
    return resume


@router.get("/list", response_model=list[ResumeOut])
@router.get("/all", response_model=list[ResumeOut])
def list_resumes(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).all()


@router.get("/analysis", response_model=ResumeAnalysisOut)
@router.get("/latest/analysis", response_model=ResumeAnalysisOut)
@router.get("/{resume_id}/analysis", response_model=ResumeAnalysisOut)
def get_analysis(
    resume_id: int | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Resume).filter(Resume.user_id == current_user.id, Resume.status == "done")
    if resume_id:
        query = query.filter(Resume.id == resume_id)
    resume = query.order_by(Resume.created_at.desc()).first()

    if not resume or not resume.analysis_result:
        raise HTTPException(status_code=404, detail="No analysis found. Please analyze your resume first.")

    data = json.loads(resume.analysis_result)
    if not data.get("email"):
        data["email"] = current_user.email
    return ResumeAnalysisOut(resume_id=resume.id, **data)


@router.get("/skills", response_model=list)
def get_candidate_skills(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    skills = db.query(CandidateSkill).filter(CandidateSkill.user_id == current_user.id).all()
    return [{"id": s.id, "skill_name": s.skill_name, "skill_category": s.skill_category, "source": s.source} for s in skills]


@router.delete("")
@router.delete("/")
@router.delete("/{resume_id}")
def delete_resume(
    resume_id: int | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Resume).filter(Resume.user_id == current_user.id)
    if resume_id is not None:
        resume = query.filter(Resume.id == resume_id).first()
    else:
        resume = query.order_by(Resume.created_at.desc()).first()

    if not resume:
        raise HTTPException(status_code=404, detail="No resume found")

    # Delete file from disk
    try:
        if resume.file_path and os.path.exists(resume.file_path):
            os.remove(resume.file_path)
    except Exception as e:
        logger.warning(f"Could not delete file {resume.file_path}: {e}")

    db.delete(resume)

    # If no more resumes remain for this user, clean up resume-sourced candidate skills
    remaining_resumes = db.query(Resume).filter(
        Resume.user_id == current_user.id,
        Resume.id != resume.id,
    ).count()
    if remaining_resumes == 0:
        db.query(CandidateSkill).filter(
            CandidateSkill.user_id == current_user.id,
            CandidateSkill.source == "resume",
        ).delete()

    db.commit()
    return {"message": "Resume deleted successfully"}

