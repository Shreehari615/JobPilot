"""
sync_real_jobs.py – Cleans old mock data and populates JobPilot AI with 100% REAL live market jobs.
Fetches active tech and engineering jobs from Remotive, Arbeitnow, and Jobicy APIs with real working URLs.
"""
import os
import sys

# Ensure backend directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine, Base
from app.models import Job, JobSkill, JobSource, SavedJob, Recommendation, JobDuplicate
from app.services.job_service import collect_and_store_jobs
from app.job_sources.api_source import RemotiveSource, ArbeitnowSource, JobicySource
from app.utils.logger import get_logger

logger = get_logger("sync_real_jobs")

def run_sync(purge_seed: bool = True):
    print("=" * 60)
    print("   JobPilot AI – Real Market Jobs Synchronizer")
    print("=" * 60)

    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        if purge_seed:
            print("\n[1/3] Removing old mock/seed jobs with broken links...")
            seed_jobs = db.query(Job).filter(Job.is_seed_data == True).all()
            seed_ids = [j.id for j in seed_jobs]
            print(f"      Found {len(seed_ids)} mock seed jobs to remove.")

            if seed_ids:
                # Remove related child records first if any
                db.query(JobSkill).filter(JobSkill.job_id.in_(seed_ids)).delete(synchronize_session=False)
                db.query(SavedJob).filter(SavedJob.job_id.in_(seed_ids)).delete(synchronize_session=False)
                db.query(Recommendation).filter(Recommendation.job_id.in_(seed_ids)).delete(synchronize_session=False)
                db.query(JobDuplicate).filter(
                    (JobDuplicate.primary_job_id.in_(seed_ids)) | (JobDuplicate.duplicate_job_id.in_(seed_ids))
                ).delete(synchronize_session=False)
                db.query(Job).filter(Job.id.in_(seed_ids)).delete(synchronize_session=False)
                db.commit()
                print("      Mock seed jobs purged successfully.")

        print("\n[2/3] Fetching real live market jobs from active APIs...")
        stats = collect_and_store_jobs(db, max_per_source=40)
        print(f"      Collection Stats: {stats}")

        print("\n[3/3] Verifying real jobs in database:")
        real_jobs = db.query(Job).filter(Job.is_active == True).order_by(Job.posted_date.desc()).limit(15).all()
        print(f"      Total active jobs in database: {db.query(Job).filter(Job.is_active == True).count()}")
        print("-" * 60)
        for idx, job in enumerate(real_jobs, 1):
            print(f"  {idx:02d}. [{job.company}] {job.title}")
            print(f"      Location: {job.location} | Source: {job.source.name if job.source else 'Unknown'}")
            print(f"      URL: {job.original_url}")
            skills = [s.skill_name for s in job.skills[:4]]
            if skills:
                print(f"      Skills: {', '.join(skills)}")
            print("-" * 60)

        print("\nReal job synchronization completed successfully!")
    except Exception as e:
        print(f"\nError during sync: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    run_sync(purge_seed=True)
