"""
Seed Data Source – provides realistic demo/development job data.
Clearly labeled as is_seed_data=True.
DO NOT mix with production source data.

Contains 60+ realistic Indian tech job listings across:
- Bengaluru, Mumbai, Hyderabad, Pune, Chennai, Delhi NCR, Mysuru, Kochi
- Roles: Software Engineer, Python Developer, ML Engineer, Data Scientist, etc.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List

from app.job_sources.base_source import BaseJobSource, RawJob


def _daysago(n: int) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=n)


SEED_JOBS_DATA = [
    # ── Python / Backend ──────────────────────────────────────────────
    {
        "external_id": "SEED-001",
        "title": "Python Developer",
        "company": "Infosys",
        "location": "Bengaluru",
        "description": (
            "We are looking for a Python Developer with strong expertise in FastAPI and PostgreSQL. "
            "You will design and build REST APIs, integrate third-party services, and maintain backend services. "
            "Experience with Docker and cloud deployment is a plus."
        ),
        "responsibilities": "Design REST APIs, write unit tests, code reviews, CI/CD pipeline maintenance.",
        "required_skills": ["Python", "FastAPI", "PostgreSQL", "REST API", "Git"],
        "experience_min": 1.0, "experience_max": 4.0,
        "education_required": "BTech/BE or equivalent",
        "salary_min": 600000, "salary_max": 1200000,
        "job_type": "full-time", "work_mode": "hybrid",
        "posted_date": _daysago(2),
        "original_url": "https://careers.infosys.com/job/python-developer-bengaluru",
    },
    {
        "external_id": "SEED-002",
        "title": "Senior Python Developer",
        "company": "Wipro",
        "location": "Hyderabad",
        "description": (
            "Senior Python Developer needed for building scalable microservices. "
            "Must have expertise in Django/FastAPI, PostgreSQL, Redis, and Kafka. "
            "AWS cloud experience required. Lead a team of 4-5 developers."
        ),
        "responsibilities": "Architect backend systems, mentor junior developers, performance tuning.",
        "required_skills": ["Python", "Django", "FastAPI", "PostgreSQL", "Redis", "Kafka", "AWS", "Docker"],
        "experience_min": 4.0, "experience_max": 8.0,
        "education_required": "BTech/BE in CS or equivalent",
        "salary_min": 1500000, "salary_max": 2500000,
        "job_type": "full-time", "work_mode": "hybrid",
        "posted_date": _daysago(1),
        "original_url": "https://jobs.wipro.com/senior-python-developer-hyderabad",
    },
    {
        "external_id": "SEED-003",
        "title": "Backend Developer (Node.js/Python)",
        "company": "Razorpay",
        "location": "Bengaluru",
        "description": (
            "Build high-performance payment APIs and microservices. "
            "Work with Node.js or Python backend stack. Experience with MongoDB, Redis. "
            "Fintech domain knowledge preferred."
        ),
        "responsibilities": "API development, database design, performance optimization, security hardening.",
        "required_skills": ["Node.js", "Python", "MongoDB", "Redis", "REST API", "Docker"],
        "experience_min": 2.0, "experience_max": 5.0,
        "education_required": "BTech/BE",
        "salary_min": 1000000, "salary_max": 2000000,
        "job_type": "full-time", "work_mode": "onsite",
        "posted_date": _daysago(3),
        "original_url": "https://razorpay.com/jobs/backend-developer",
    },
    # ── Full Stack ────────────────────────────────────────────────────
    {
        "external_id": "SEED-004",
        "title": "Full Stack Developer",
        "company": "Swiggy",
        "location": "Bengaluru",
        "description": (
            "Full Stack Developer for food-tech platform. Build features using React frontend "
            "and Node.js/Python backend. Work with PostgreSQL, Redis, Kubernetes. "
            "Strong DSA skills required."
        ),
        "responsibilities": "Feature development, A/B testing, system design, code reviews.",
        "required_skills": ["React", "Node.js", "Python", "PostgreSQL", "Redis", "Kubernetes", "JavaScript", "CSS"],
        "experience_min": 2.0, "experience_max": 6.0,
        "education_required": "BTech/BE",
        "salary_min": 1200000, "salary_max": 2500000,
        "job_type": "full-time", "work_mode": "hybrid",
        "posted_date": _daysago(1),
        "original_url": "https://careers.swiggy.com/full-stack-developer",
    },
    {
        "external_id": "SEED-005",
        "title": "Full Stack Developer (React + Django)",
        "company": "Freshworks",
        "location": "Chennai",
        "description": (
            "Develop SaaS features using React and Django. "
            "Work on multi-tenant architecture, REST APIs, and PostgreSQL. "
            "Experience with AWS deployment preferred."
        ),
        "responsibilities": "Feature development, UI components, REST API design, database optimization.",
        "required_skills": ["React", "Django", "Python", "PostgreSQL", "JavaScript", "HTML", "CSS", "REST API"],
        "experience_min": 1.5, "experience_max": 4.0,
        "education_required": "BTech/BE/MCA",
        "salary_min": 800000, "salary_max": 1600000,
        "job_type": "full-time", "work_mode": "hybrid",
        "posted_date": _daysago(4),
        "original_url": "https://freshworks.com/careers/full-stack-developer-chennai",
    },
    {
        "external_id": "SEED-006",
        "title": "MERN Stack Developer",
        "company": "Zoho",
        "location": "Chennai",
        "description": (
            "Build web applications using MongoDB, Express.js, React, and Node.js. "
            "Design scalable APIs, implement authentication, work on real-time features. "
            "Good knowledge of TypeScript preferred."
        ),
        "responsibilities": "Full-stack feature development, API integration, unit testing.",
        "required_skills": ["MongoDB", "Express.js", "React", "Node.js", "JavaScript", "TypeScript", "HTML", "CSS"],
        "experience_min": 1.0, "experience_max": 4.0,
        "education_required": "BE/BTech/MCA",
        "salary_min": 700000, "salary_max": 1400000,
        "job_type": "full-time", "work_mode": "onsite",
        "posted_date": _daysago(5),
        "original_url": "https://careers.zoho.com/mern-stack-developer",
    },
    # ── Frontend ──────────────────────────────────────────────────────
    {
        "external_id": "SEED-007",
        "title": "Frontend Developer (React)",
        "company": "Paytm",
        "location": "Delhi NCR",
        "description": (
            "Build responsive UIs for fintech apps using React, TypeScript, and Tailwind CSS. "
            "Performance optimization, accessibility, cross-browser compatibility required. "
            "Experience with Redux and GraphQL is a plus."
        ),
        "responsibilities": "Component development, state management, performance optimization.",
        "required_skills": ["React", "TypeScript", "JavaScript", "Tailwind CSS", "CSS", "HTML", "Redux"],
        "experience_min": 1.0, "experience_max": 4.0,
        "education_required": "BTech/BE/MCA",
        "salary_min": 800000, "salary_max": 1600000,
        "job_type": "full-time", "work_mode": "hybrid",
        "posted_date": _daysago(2),
        "original_url": "https://paytm.com/careers/frontend-developer",
    },
    {
        "external_id": "SEED-008",
        "title": "Senior React Developer",
        "company": "PhonePe",
        "location": "Bengaluru",
        "description": (
            "Lead front-end development for PhonePe's payment platform. "
            "Expert-level React.js, TypeScript, and state management. "
            "Micro-frontend architecture experience preferred."
        ),
        "responsibilities": "Architecture decisions, performance profiling, mentoring junior devs.",
        "required_skills": ["React", "TypeScript", "JavaScript", "Redux", "GraphQL", "CSS", "HTML"],
        "experience_min": 4.0, "experience_max": 8.0,
        "education_required": "BTech/BE",
        "salary_min": 1800000, "salary_max": 3500000,
        "job_type": "full-time", "work_mode": "onsite",
        "posted_date": _daysago(3),
        "original_url": "https://phonepe.com/en-in/careers/senior-react-developer",
    },
    # ── Data Science / ML ─────────────────────────────────────────────
    {
        "external_id": "SEED-009",
        "title": "Data Scientist",
        "company": "Flipkart",
        "location": "Bengaluru",
        "description": (
            "Apply ML/DL techniques to solve e-commerce problems: pricing, recommendations, demand forecasting. "
            "Work with Python, scikit-learn, TensorFlow, and Spark. "
            "Strong statistics background required."
        ),
        "responsibilities": "Model development, feature engineering, A/B testing, model deployment.",
        "required_skills": ["Python", "Machine Learning", "Deep Learning", "Scikit-learn", "TensorFlow", "Pandas", "NumPy", "SQL", "Apache Spark"],
        "experience_min": 2.0, "experience_max": 6.0,
        "education_required": "MTech/MSc/MCA in CS/Statistics/Mathematics",
        "salary_min": 1500000, "salary_max": 3000000,
        "job_type": "full-time", "work_mode": "hybrid",
        "posted_date": _daysago(1),
        "original_url": "https://careers.flipkart.com/data-scientist-bengaluru",
    },
    {
        "external_id": "SEED-010",
        "title": "Machine Learning Engineer",
        "company": "Google India",
        "location": "Hyderabad",
        "description": (
            "Design and deploy production ML systems at scale. "
            "Experience with PyTorch/TensorFlow, MLOps, and cloud ML platforms (GCP). "
            "Work on NLP, computer vision, or recommendation systems."
        ),
        "responsibilities": "ML model development, MLOps, data pipeline, model monitoring.",
        "required_skills": ["Python", "PyTorch", "TensorFlow", "Machine Learning", "Deep Learning", "NLP", "Google Cloud", "Docker", "Kubernetes", "SQL"],
        "experience_min": 3.0, "experience_max": 7.0,
        "education_required": "MTech/MSc/PhD in CS, AI, ML",
        "salary_min": 3000000, "salary_max": 6000000,
        "job_type": "full-time", "work_mode": "onsite",
        "posted_date": _daysago(2),
        "original_url": "https://careers.google.com/jobs/ml-engineer-hyderabad",
    },
    {
        "external_id": "SEED-011",
        "title": "NLP Engineer",
        "company": "Microsoft India",
        "location": "Hyderabad",
        "description": (
            "Build NLP pipelines for Azure AI services. "
            "Work on text classification, NER, summarization, and dialogue systems. "
            "Experience with transformers, BERT, GPT models required."
        ),
        "responsibilities": "NLP model development, fine-tuning transformers, API development.",
        "required_skills": ["Python", "NLP", "Deep Learning", "PyTorch", "Transformers", "BERT", "Hugging Face", "Azure", "spaCy"],
        "experience_min": 2.0, "experience_max": 6.0,
        "education_required": "MTech/MSc/MCA in CS/AI",
        "salary_min": 2000000, "salary_max": 4000000,
        "job_type": "full-time", "work_mode": "hybrid",
        "posted_date": _daysago(3),
        "original_url": "https://careers.microsoft.com/nlp-engineer-hyderabad",
    },
    {
        "external_id": "SEED-012",
        "title": "Data Analyst",
        "company": "Amazon India",
        "location": "Bengaluru",
        "description": (
            "Analyse large datasets to drive business insights for Amazon's supply chain. "
            "Expertise in SQL, Python, and data visualization tools. "
            "Experience with AWS services (Redshift, S3) preferred."
        ),
        "responsibilities": "Data analysis, dashboard creation, A/B test analysis, reporting.",
        "required_skills": ["Python", "SQL", "Data Analysis", "Pandas", "NumPy", "Matplotlib", "AWS", "Tableau"],
        "experience_min": 1.0, "experience_max": 4.0,
        "education_required": "BTech/BSc/BCA/MCA",
        "salary_min": 900000, "salary_max": 1800000,
        "job_type": "full-time", "work_mode": "hybrid",
        "posted_date": _daysago(4),
        "original_url": "https://amazon.jobs/data-analyst-bengaluru",
    },
    {
        "external_id": "SEED-013",
        "title": "AI/ML Researcher",
        "company": "Samsung R&D India",
        "location": "Bengaluru",
        "description": (
            "Research and develop next-gen AI/ML algorithms for mobile applications. "
            "Publish papers, implement prototypes, and collaborate with product teams. "
            "Experience in computer vision or NLP."
        ),
        "responsibilities": "Research, prototyping, paper writing, collaboration with engineering teams.",
        "required_skills": ["Python", "Deep Learning", "PyTorch", "TensorFlow", "Computer Vision", "NLP", "Machine Learning", "MATLAB"],
        "experience_min": 2.0, "experience_max": 7.0,
        "education_required": "MTech/MSc/PhD in CS, AI, ML",
        "salary_min": 2000000, "salary_max": 5000000,
        "job_type": "full-time", "work_mode": "onsite",
        "posted_date": _daysago(6),
        "original_url": "https://research.samsung.com/careers/ai-ml-researcher",
    },
    # ── DevOps / Cloud ────────────────────────────────────────────────
    {
        "external_id": "SEED-014",
        "title": "DevOps Engineer",
        "company": "Ola",
        "location": "Bengaluru",
        "description": (
            "Build and maintain CI/CD pipelines, manage Kubernetes clusters on AWS. "
            "Infrastructure as Code with Terraform. Monitor with Prometheus/Grafana. "
            "Strong Linux administration skills required."
        ),
        "responsibilities": "CI/CD pipeline, K8s management, IaC, monitoring, incident response.",
        "required_skills": ["Docker", "Kubernetes", "AWS", "Terraform", "CI/CD", "Linux", "Prometheus", "Grafana", "Python", "Bash"],
        "experience_min": 2.0, "experience_max": 6.0,
        "education_required": "BTech/BE in CS",
        "salary_min": 1200000, "salary_max": 2400000,
        "job_type": "full-time", "work_mode": "hybrid",
        "posted_date": _daysago(2),
        "original_url": "https://careers.ola.com/devops-engineer-bengaluru",
    },
    {
        "external_id": "SEED-015",
        "title": "Cloud Engineer (AWS)",
        "company": "Accenture",
        "location": "Pune",
        "description": (
            "Design and implement AWS cloud infrastructure for enterprise clients. "
            "Expertise in EC2, Lambda, RDS, EKS, CloudFormation. "
            "AWS certified preferred."
        ),
        "responsibilities": "Cloud architecture, migration projects, cost optimization, security compliance.",
        "required_skills": ["AWS", "Docker", "Kubernetes", "Terraform", "Python", "Linux", "CI/CD"],
        "experience_min": 2.0, "experience_max": 7.0,
        "education_required": "BTech/BE",
        "salary_min": 1000000, "salary_max": 2200000,
        "job_type": "full-time", "work_mode": "hybrid",
        "posted_date": _daysago(5),
        "original_url": "https://accenture.com/careers/cloud-engineer-pune",
    },
    # ── Software Engineering (General) ────────────────────────────────
    {
        "external_id": "SEED-016",
        "title": "Software Engineer (Java)",
        "company": "TCS",
        "location": "Mumbai",
        "description": (
            "Develop enterprise Java applications using Spring Boot and microservices. "
            "PostgreSQL/Oracle database experience. REST API design and integration. "
            "Agile/Scrum methodology."
        ),
        "responsibilities": "Feature development, code reviews, unit testing, performance optimization.",
        "required_skills": ["Java", "Spring Boot", "PostgreSQL", "REST API", "Docker", "Git", "SQL", "Agile"],
        "experience_min": 1.0, "experience_max": 5.0,
        "education_required": "BTech/BE/MCA",
        "salary_min": 600000, "salary_max": 1400000,
        "job_type": "full-time", "work_mode": "hybrid",
        "posted_date": _daysago(3),
        "original_url": "https://tcs.com/careers/java-software-engineer-mumbai",
    },
    {
        "external_id": "SEED-017",
        "title": "Junior Software Engineer",
        "company": "Capgemini",
        "location": "Pune",
        "description": (
            "Entry-level software engineering position. Work on Java or Python backend services. "
            "Learn agile methodologies, unit testing, and CI/CD practices. "
            "Good DSA skills required."
        ),
        "responsibilities": "Development, unit testing, bug fixes, code reviews.",
        "required_skills": ["Java", "Python", "SQL", "Git", "HTML", "CSS", "JavaScript"],
        "experience_min": 0.0, "experience_max": 2.0,
        "education_required": "BTech/BE/MCA (2024 or 2025 passout)",
        "salary_min": 400000, "salary_max": 800000,
        "job_type": "full-time", "work_mode": "onsite",
        "posted_date": _daysago(1),
        "original_url": "https://capgemini.com/careers/junior-software-engineer-pune",
    },
    {
        "external_id": "SEED-018",
        "title": "Software Development Engineer",
        "company": "Adobe India",
        "location": "Bengaluru",
        "description": (
            "Build creative cloud features using C++, Python, and Java. "
            "Work on multimedia processing, real-time collaboration tools. "
            "Performance-critical systems development experience preferred."
        ),
        "responsibilities": "System design, high-performance feature development, cross-platform testing.",
        "required_skills": ["C++", "Python", "Java", "Git", "Linux", "Docker", "SQL"],
        "experience_min": 2.0, "experience_max": 5.0,
        "education_required": "BTech/BE in CS",
        "salary_min": 1500000, "salary_max": 3000000,
        "job_type": "full-time", "work_mode": "hybrid",
        "posted_date": _daysago(4),
        "original_url": "https://adobe.com/careers/software-development-engineer-bengaluru",
    },
    # ── Remote Jobs ───────────────────────────────────────────────────
    {
        "external_id": "SEED-019",
        "title": "Remote Python Developer",
        "company": "Toptal",
        "location": "Remote",
        "description": (
            "Work remotely on Python projects for top-tier clients. "
            "Expertise in Django or FastAPI, PostgreSQL, Docker. "
            "Strong communication skills and ability to work independently."
        ),
        "responsibilities": "Client project delivery, API development, code quality.",
        "required_skills": ["Python", "Django", "FastAPI", "PostgreSQL", "Docker", "REST API", "Git"],
        "experience_min": 3.0, "experience_max": 10.0,
        "education_required": "BTech/BE or equivalent",
        "salary_min": 2000000, "salary_max": 5000000,
        "job_type": "contract", "work_mode": "remote",
        "posted_date": _daysago(2),
        "original_url": "https://toptal.com/jobs/remote-python-developer",
    },
    {
        "external_id": "SEED-020",
        "title": "Remote Data Scientist",
        "company": "DataAnnotation Tech",
        "location": "Remote",
        "description": (
            "Fully remote data science role. Work on ML models for NLP and computer vision. "
            "Python, scikit-learn, TensorFlow/PyTorch experience required. "
            "Flexible hours."
        ),
        "responsibilities": "Model development, dataset curation, evaluation, reporting.",
        "required_skills": ["Python", "Machine Learning", "NLP", "Scikit-learn", "PyTorch", "Pandas", "NumPy"],
        "experience_min": 1.0, "experience_max": 5.0,
        "education_required": "BTech/MSc/MCA in CS/AI",
        "salary_min": 1000000, "salary_max": 2500000,
        "job_type": "contract", "work_mode": "remote",
        "posted_date": _daysago(3),
        "original_url": "https://dataannotation.tech/jobs/remote-data-scientist",
    },
    # ── More roles ────────────────────────────────────────────────────
    {
        "external_id": "SEED-021",
        "title": "Data Engineer",
        "company": "Juspay",
        "location": "Bengaluru",
        "description": (
            "Build and maintain data pipelines for payment processing analytics. "
            "Apache Spark, Kafka, Airflow, and cloud data warehouses. "
            "Strong SQL and Python skills."
        ),
        "responsibilities": "Data pipeline development, ETL, data quality, monitoring.",
        "required_skills": ["Python", "Apache Spark", "Kafka", "Airflow", "SQL", "PostgreSQL", "AWS", "Docker"],
        "experience_min": 2.0, "experience_max": 6.0,
        "education_required": "BTech/BE/MCA",
        "salary_min": 1200000, "salary_max": 2500000,
        "job_type": "full-time", "work_mode": "hybrid",
        "posted_date": _daysago(5),
        "original_url": "https://juspay.in/careers/data-engineer",
    },
    {
        "external_id": "SEED-022",
        "title": "Generative AI Engineer",
        "company": "Persistent Systems",
        "location": "Pune",
        "description": (
            "Build LLM-powered applications using LangChain, RAG architectures, and vector databases. "
            "Experience with OpenAI/Gemini APIs, fine-tuning, and prompt engineering. "
            "Python and FastAPI for API development."
        ),
        "responsibilities": "LLM app development, RAG pipelines, vector DB integration, evaluation.",
        "required_skills": ["Python", "LLM", "Generative AI", "RAG", "Langchain", "FastAPI", "Vector Database", "Docker"],
        "experience_min": 1.0, "experience_max": 5.0,
        "education_required": "BTech/BE/MCA",
        "salary_min": 1200000, "salary_max": 3000000,
        "job_type": "full-time", "work_mode": "hybrid",
        "posted_date": _daysago(1),
        "original_url": "https://persistent.com/careers/genai-engineer-pune",
    },
    {
        "external_id": "SEED-023",
        "title": "Android Developer",
        "company": "Meesho",
        "location": "Bengaluru",
        "description": (
            "Build Android features for Meesho's social commerce platform. "
            "Kotlin, Jetpack Compose, MVVM architecture. "
            "Focus on performance, animations, and offline support."
        ),
        "responsibilities": "Feature development, performance optimization, unit testing.",
        "required_skills": ["Android", "Kotlin", "Java", "Jetpack Compose", "Git", "REST API", "SQL"],
        "experience_min": 1.0, "experience_max": 4.0,
        "education_required": "BTech/BE/MCA",
        "salary_min": 900000, "salary_max": 2000000,
        "job_type": "full-time", "work_mode": "onsite",
        "posted_date": _daysago(6),
        "original_url": "https://meesho.com/careers/android-developer",
    },
    {
        "external_id": "SEED-024",
        "title": "Software Engineer (Fresher)",
        "company": "Mphasis",
        "location": "Bengaluru",
        "description": (
            "Fresh graduate role for 2024/2025 engineering graduates. "
            "Comprehensive training in Java, Python, and cloud technologies. "
            "Good problem-solving and programming skills required."
        ),
        "responsibilities": "Learning, development tasks, testing, code reviews.",
        "required_skills": ["Java", "Python", "SQL", "HTML", "JavaScript", "Git"],
        "experience_min": 0.0, "experience_max": 1.0,
        "education_required": "BTech/BE/MCA 2024/2025 Passout",
        "salary_min": 350000, "salary_max": 500000,
        "job_type": "full-time", "work_mode": "onsite",
        "posted_date": _daysago(7),
        "original_url": "https://mphasis.com/careers/fresher-software-engineer",
    },
    {
        "external_id": "SEED-025",
        "title": "Cloud Data Engineer (GCP)",
        "company": "Siemens India",
        "location": "Pune",
        "description": (
            "Build data infrastructure on Google Cloud Platform. "
            "BigQuery, Dataflow, Pub/Sub, and Cloud Composer. "
            "Python and SQL proficiency essential."
        ),
        "responsibilities": "GCP data pipeline development, BigQuery optimization, data governance.",
        "required_skills": ["Python", "Google Cloud", "SQL", "Apache Spark", "Airflow", "Docker", "Kubernetes"],
        "experience_min": 3.0, "experience_max": 7.0,
        "education_required": "BTech/BE/MCA",
        "salary_min": 1500000, "salary_max": 3000000,
        "job_type": "full-time", "work_mode": "hybrid",
        "posted_date": _daysago(8),
        "original_url": "https://siemens.com/careers/cloud-data-engineer-pune",
    },
    {
        "external_id": "SEED-026",
        "title": "React Native Developer",
        "company": "Nykaa",
        "location": "Mumbai",
        "description": (
            "Build cross-platform mobile app features for Nykaa's beauty platform. "
            "React Native, TypeScript, Redux. "
            "Integration with REST APIs and payment gateways."
        ),
        "responsibilities": "Mobile feature development, performance optimization, app store releases.",
        "required_skills": ["React Native", "React", "TypeScript", "JavaScript", "Redux", "REST API", "Git"],
        "experience_min": 1.5, "experience_max": 5.0,
        "education_required": "BTech/BE/MCA",
        "salary_min": 900000, "salary_max": 2000000,
        "job_type": "full-time", "work_mode": "hybrid",
        "posted_date": _daysago(4),
        "original_url": "https://nykaa.com/careers/react-native-developer-mumbai",
    },
    {
        "external_id": "SEED-027",
        "title": "Cybersecurity Engineer",
        "company": "HCL Technologies",
        "location": "Noida",
        "description": (
            "Implement security solutions for enterprise clients. "
            "Vulnerability assessment, penetration testing, SIEM tools. "
            "CISSP/CEH certification preferred."
        ),
        "responsibilities": "Security assessments, incident response, compliance, threat modeling.",
        "required_skills": ["Cybersecurity", "Penetration Testing", "Python", "Linux", "Network Security", "OWASP"],
        "experience_min": 2.0, "experience_max": 7.0,
        "education_required": "BTech/BE in CS/IT",
        "salary_min": 1000000, "salary_max": 2500000,
        "job_type": "full-time", "work_mode": "hybrid",
        "posted_date": _daysago(9),
        "original_url": "https://hcltech.com/careers/cybersecurity-engineer-noida",
    },
    {
        "external_id": "SEED-028",
        "title": "Site Reliability Engineer",
        "company": "Atlassian India",
        "location": "Bengaluru",
        "description": (
            "Ensure reliability, scalability, and performance of Atlassian cloud services. "
            "SRE practices, Kubernetes, AWS, observability (Prometheus/Grafana). "
            "On-call rotation required."
        ),
        "responsibilities": "Incident management, capacity planning, automation, observability.",
        "required_skills": ["Python", "Kubernetes", "AWS", "Docker", "Linux", "Prometheus", "Grafana", "CI/CD", "Terraform"],
        "experience_min": 3.0, "experience_max": 7.0,
        "education_required": "BTech/BE in CS",
        "salary_min": 2500000, "salary_max": 5000000,
        "job_type": "full-time", "work_mode": "hybrid",
        "posted_date": _daysago(2),
        "original_url": "https://atlassian.com/company/careers/sre-bengaluru",
    },
    {
        "external_id": "SEED-029",
        "title": "Blockchain Developer",
        "company": "Polygon",
        "location": "Mumbai",
        "description": (
            "Build smart contracts and decentralized applications on Polygon blockchain. "
            "Solidity, Hardhat, Web3.js. "
            "Experience with DeFi protocols preferred."
        ),
        "responsibilities": "Smart contract development, security auditing, dApp integration.",
        "required_skills": ["Python", "JavaScript", "Node.js", "SQL", "Git", "REST API"],
        "experience_min": 1.0, "experience_max": 5.0,
        "education_required": "BTech/BE/MCA",
        "salary_min": 1200000, "salary_max": 3000000,
        "job_type": "full-time", "work_mode": "hybrid",
        "posted_date": _daysago(7),
        "original_url": "https://polygon.technology/careers/blockchain-developer",
    },
    {
        "external_id": "SEED-030",
        "title": "Python + ML Intern",
        "company": "Jio Platforms",
        "location": "Mumbai",
        "description": (
            "6-month internship in AI/ML team. "
            "Work on NLP and recommendation systems. "
            "Python, scikit-learn, and basic deep learning knowledge required."
        ),
        "responsibilities": "Data analysis, model prototyping, literature review, reporting.",
        "required_skills": ["Python", "Machine Learning", "NLP", "Scikit-learn", "Pandas", "NumPy", "SQL"],
        "experience_min": 0.0, "experience_max": 0.5,
        "education_required": "Final year BTech/MCA/MSc students",
        "salary_min": 15000, "salary_max": 30000,
        "job_type": "internship", "work_mode": "hybrid",
        "posted_date": _daysago(3),
        "original_url": "https://jio.com/careers/python-ml-intern-mumbai",
    },
    # More jobs for variety
    {
        "external_id": "SEED-031",
        "title": "Product Manager – AI/ML",
        "company": "OYO",
        "location": "Delhi NCR",
        "description": (
            "Drive AI/ML product strategy for OYO's travel platform. "
            "Work with data science and engineering teams. "
            "MBA with technical background preferred."
        ),
        "responsibilities": "Product roadmap, stakeholder management, A/B testing, data analysis.",
        "required_skills": ["Data Analysis", "Python", "SQL", "Machine Learning", "Agile"],
        "experience_min": 3.0, "experience_max": 8.0,
        "education_required": "MBA/BTech",
        "salary_min": 2000000, "salary_max": 4000000,
        "job_type": "full-time", "work_mode": "hybrid",
        "posted_date": _daysago(5),
        "original_url": "https://oyo.com/careers/product-manager-ai-ml",
    },
    {
        "external_id": "SEED-032",
        "title": "Django/Python Developer",
        "company": "BYJU's",
        "location": "Bengaluru",
        "description": (
            "Build edtech platform backend using Django and PostgreSQL. "
            "Experience with REST APIs, Celery, Redis. "
            "Agile development environment."
        ),
        "responsibilities": "Feature development, API design, performance tuning, testing.",
        "required_skills": ["Python", "Django", "PostgreSQL", "Redis", "Celery", "REST API", "Git", "Docker"],
        "experience_min": 1.0, "experience_max": 4.0,
        "education_required": "BTech/BE/MCA",
        "salary_min": 700000, "salary_max": 1500000,
        "job_type": "full-time", "work_mode": "onsite",
        "posted_date": _daysago(6),
        "original_url": "https://byjus.com/careers/django-python-developer",
    },
    {
        "external_id": "SEED-033",
        "title": "Vue.js Developer",
        "company": "Mindtree",
        "location": "Bengaluru",
        "description": (
            "Build enterprise web applications with Vue.js and Node.js. "
            "State management with Vuex, RESTful API integration. "
            "TypeScript experience preferred."
        ),
        "responsibilities": "Frontend development, component design, testing, client collaboration.",
        "required_skills": ["Vue.js", "JavaScript", "TypeScript", "Node.js", "HTML", "CSS", "REST API", "Git"],
        "experience_min": 1.5, "experience_max": 5.0,
        "education_required": "BTech/BE/MCA",
        "salary_min": 800000, "salary_max": 1600000,
        "job_type": "full-time", "work_mode": "hybrid",
        "posted_date": _daysago(4),
        "original_url": "https://mindtree.com/careers/vuejs-developer-bengaluru",
    },
    {
        "external_id": "SEED-034",
        "title": "Computer Vision Engineer",
        "company": "Ola Electric",
        "location": "Bengaluru",
        "description": (
            "Develop computer vision systems for autonomous vehicle perception. "
            "Experience with OpenCV, PyTorch, YOLO, and sensor fusion. "
            "C++ performance optimization skills."
        ),
        "responsibilities": "Perception algorithm development, model training, real-time inference optimization.",
        "required_skills": ["Python", "C++", "Computer Vision", "PyTorch", "OpenCV", "Deep Learning", "Machine Learning"],
        "experience_min": 2.0, "experience_max": 7.0,
        "education_required": "MTech/MSc/BTech in CS/EE",
        "salary_min": 2000000, "salary_max": 5000000,
        "job_type": "full-time", "work_mode": "onsite",
        "posted_date": _daysago(8),
        "original_url": "https://olaelectric.com/careers/computer-vision-engineer",
    },
    {
        "external_id": "SEED-035",
        "title": "Platform Engineer (Kubernetes/AWS)",
        "company": "Zerodha",
        "location": "Bengaluru",
        "description": (
            "Build and scale Zerodha's trading platform infrastructure. "
            "Expert Kubernetes cluster management, AWS, Terraform, and Go. "
            "High-availability and low-latency systems experience."
        ),
        "responsibilities": "Platform design, cluster management, automation, cost optimization.",
        "required_skills": ["Kubernetes", "AWS", "Docker", "Terraform", "Go", "Linux", "Python", "Prometheus"],
        "experience_min": 3.0, "experience_max": 8.0,
        "education_required": "BTech/BE in CS",
        "salary_min": 2000000, "salary_max": 4500000,
        "job_type": "full-time", "work_mode": "onsite",
        "posted_date": _daysago(5),
        "original_url": "https://zerodha.com/careers/platform-engineer",
    },
    {
        "external_id": "SEED-036",
        "title": "ETL Developer (Python/Spark)",
        "company": "Mu Sigma",
        "location": "Bengaluru",
        "description": (
            "Build ETL pipelines for large-scale analytics projects using Python and Apache Spark. "
            "Work with cloud data warehouses: Snowflake, Redshift. "
            "SQL optimization and data quality experience."
        ),
        "responsibilities": "Pipeline development, data quality checks, optimization, documentation.",
        "required_skills": ["Python", "Apache Spark", "SQL", "Airflow", "Snowflake", "AWS", "Docker"],
        "experience_min": 2.0, "experience_max": 5.0,
        "education_required": "BTech/BE/MCA",
        "salary_min": 900000, "salary_max": 2000000,
        "job_type": "full-time", "work_mode": "hybrid",
        "posted_date": _daysago(10),
        "original_url": "https://musigma.com/careers/etl-developer-bengaluru",
    },
    {
        "external_id": "SEED-037",
        "title": "Software Engineer – Golang",
        "company": "Dunzo",
        "location": "Bengaluru",
        "description": (
            "Build high-throughput Go microservices for hyperlocal delivery platform. "
            "PostgreSQL, Redis, Kafka. Docker and Kubernetes deployment. "
            "Strong concurrency and systems programming skills."
        ),
        "responsibilities": "Microservice development, API design, performance optimization.",
        "required_skills": ["Go", "PostgreSQL", "Redis", "Kafka", "Docker", "Kubernetes", "Linux", "Git"],
        "experience_min": 2.0, "experience_max": 6.0,
        "education_required": "BTech/BE in CS",
        "salary_min": 1200000, "salary_max": 2800000,
        "job_type": "full-time", "work_mode": "hybrid",
        "posted_date": _daysago(3),
        "original_url": "https://dunzo.com/careers/software-engineer-golang",
    },
    {
        "external_id": "SEED-038",
        "title": "Technical Lead – Python",
        "company": "Cognizant",
        "location": "Chennai",
        "description": (
            "Lead a team of Python developers building enterprise software. "
            "Mentor engineers, conduct code reviews, drive architecture decisions. "
            "Django/FastAPI, PostgreSQL, AWS."
        ),
        "responsibilities": "Technical leadership, architecture, code reviews, stakeholder communication.",
        "required_skills": ["Python", "Django", "FastAPI", "PostgreSQL", "AWS", "Docker", "Kubernetes", "Agile", "Git"],
        "experience_min": 6.0, "experience_max": 12.0,
        "education_required": "BTech/BE/MCA",
        "salary_min": 2000000, "salary_max": 4000000,
        "job_type": "full-time", "work_mode": "hybrid",
        "posted_date": _daysago(7),
        "original_url": "https://cognizant.com/careers/technical-lead-python-chennai",
    },
    {
        "external_id": "SEED-039",
        "title": "Data Science Intern",
        "company": "Analytics Vidhya",
        "location": "Bengaluru",
        "description": (
            "3-6 month internship in data science. "
            "Work on real ML projects with Python, scikit-learn, pandas. "
            "Freshers and final-year students encouraged to apply."
        ),
        "responsibilities": "Data analysis, ML prototypes, blog writing, community support.",
        "required_skills": ["Python", "Machine Learning", "Pandas", "NumPy", "Scikit-learn", "SQL"],
        "experience_min": 0.0, "experience_max": 1.0,
        "education_required": "Final year or recent graduate in CS/Statistics/Mathematics",
        "salary_min": 10000, "salary_max": 25000,
        "job_type": "internship", "work_mode": "hybrid",
        "posted_date": _daysago(2),
        "original_url": "https://analyticsvidhya.com/careers/data-science-intern",
    },
    {
        "external_id": "SEED-040",
        "title": "Software Engineer – VLSI/Embedded",
        "company": "Qualcomm India",
        "location": "Hyderabad",
        "description": (
            "Develop firmware and embedded software for Snapdragon chips. "
            "C/C++, ARM architecture, RTOS experience. "
            "Knowledge of communication protocols (I2C, SPI, UART)."
        ),
        "responsibilities": "Firmware development, hardware bring-up, debugging, performance optimization.",
        "required_skills": ["C", "C++", "Python", "Linux", "Git", "Shell"],
        "experience_min": 1.0, "experience_max": 5.0,
        "education_required": "BTech/BE in CS/ECE",
        "salary_min": 1200000, "salary_max": 2800000,
        "job_type": "full-time", "work_mode": "onsite",
        "posted_date": _daysago(9),
        "original_url": "https://qualcomm.com/careers/software-engineer-hyderabad",
    },
    # Kochi / Mysuru jobs
    {
        "external_id": "SEED-041",
        "title": "Python Developer (Mid-level)",
        "company": "IBS Software",
        "location": "Kochi",
        "description": (
            "Build airline industry software using Python and PostgreSQL. "
            "REST API development, Docker deployment, Agile team. "
            "Aviation/travel domain knowledge is a plus."
        ),
        "responsibilities": "Feature development, API design, testing, documentation.",
        "required_skills": ["Python", "PostgreSQL", "REST API", "Docker", "Git", "SQL", "Agile"],
        "experience_min": 2.0, "experience_max": 5.0,
        "education_required": "BTech/BE/MCA",
        "salary_min": 700000, "salary_max": 1500000,
        "job_type": "full-time", "work_mode": "onsite",
        "posted_date": _daysago(4),
        "original_url": "https://ibsplc.com/careers/python-developer-kochi",
    },
    {
        "external_id": "SEED-042",
        "title": "ML Engineer – Recommendation Systems",
        "company": "UST Global",
        "location": "Kochi",
        "description": (
            "Build recommendation systems for e-commerce clients. "
            "Python, scikit-learn, TensorFlow, and collaborative/content-based filtering. "
            "Experience with recommendation system evaluation metrics."
        ),
        "responsibilities": "Recommendation model development, A/B testing, MLOps.",
        "required_skills": ["Python", "Machine Learning", "Recommendation Systems", "Scikit-learn", "TensorFlow", "SQL", "Docker"],
        "experience_min": 2.0, "experience_max": 6.0,
        "education_required": "MTech/MSc/BTech in CS/AI",
        "salary_min": 1000000, "salary_max": 2500000,
        "job_type": "full-time", "work_mode": "hybrid",
        "posted_date": _daysago(5),
        "original_url": "https://ust.com/careers/ml-engineer-recommendation-kochi",
    },
    {
        "external_id": "SEED-043",
        "title": "Software Engineer (React + Python)",
        "company": "Infosys BPM",
        "location": "Mysuru",
        "description": (
            "Full-stack developer for BPM solutions. "
            "React frontend, Python backend (Django/FastAPI), PostgreSQL. "
            "Freshers welcome; training provided."
        ),
        "responsibilities": "Feature development, UI components, API integration, testing.",
        "required_skills": ["React", "Python", "JavaScript", "HTML", "CSS", "SQL", "Git"],
        "experience_min": 0.0, "experience_max": 3.0,
        "education_required": "BTech/BE/MCA",
        "salary_min": 450000, "salary_max": 900000,
        "job_type": "full-time", "work_mode": "onsite",
        "posted_date": _daysago(6),
        "original_url": "https://infosysbpm.com/careers/software-engineer-mysuru",
    },
    {
        "external_id": "SEED-044",
        "title": "Data Analyst (SQL + Python)",
        "company": "Delhivery",
        "location": "Delhi NCR",
        "description": (
            "Analyse logistics data to improve delivery efficiency. "
            "SQL, Python, Power BI/Tableau. "
            "Statistical analysis and data visualization expertise."
        ),
        "responsibilities": "Data analysis, reporting dashboards, KPI tracking, insight generation.",
        "required_skills": ["SQL", "Python", "Pandas", "Data Analysis", "Data Visualization", "NumPy"],
        "experience_min": 1.0, "experience_max": 4.0,
        "education_required": "BTech/BSc/BCA/MCA",
        "salary_min": 600000, "salary_max": 1200000,
        "job_type": "full-time", "work_mode": "hybrid",
        "posted_date": _daysago(3),
        "original_url": "https://delhivery.com/careers/data-analyst-delhi",
    },
    {
        "external_id": "SEED-045",
        "title": "Frontend Developer (Next.js)",
        "company": "Groww",
        "location": "Bengaluru",
        "description": (
            "Build Next.js frontend for India's leading investment platform. "
            "TypeScript, Tailwind CSS, SEO optimization, performance. "
            "Experience with financial data visualization."
        ),
        "responsibilities": "Component development, SEO, performance optimization, A/B testing.",
        "required_skills": ["Next.js", "React", "TypeScript", "JavaScript", "Tailwind CSS", "HTML", "CSS", "Git"],
        "experience_min": 1.5, "experience_max": 5.0,
        "education_required": "BTech/BE/MCA",
        "salary_min": 1000000, "salary_max": 2500000,
        "job_type": "full-time", "work_mode": "hybrid",
        "posted_date": _daysago(2),
        "original_url": "https://groww.in/careers/frontend-developer-nextjs",
    },
    {
        "external_id": "SEED-046",
        "title": "Backend Engineer (Go/Python)",
        "company": "CRED",
        "location": "Bengaluru",
        "description": (
            "Build high-performance fintech services using Go or Python. "
            "PostgreSQL, Redis, Kafka. Microservices architecture. "
            "Experience with payment systems or fintech preferred."
        ),
        "responsibilities": "API development, microservice design, performance optimization, security.",
        "required_skills": ["Go", "Python", "PostgreSQL", "Redis", "Kafka", "Docker", "Kubernetes", "SQL", "Git"],
        "experience_min": 2.0, "experience_max": 6.0,
        "education_required": "BTech/BE in CS",
        "salary_min": 1500000, "salary_max": 3500000,
        "job_type": "full-time", "work_mode": "hybrid",
        "posted_date": _daysago(1),
        "original_url": "https://cred.club/careers/backend-engineer",
    },
    {
        "external_id": "SEED-047",
        "title": "MCA Fresher – Software Developer",
        "company": "Tech Mahindra",
        "location": "Pune",
        "description": (
            "Exciting opportunity for MCA freshers in software development. "
            "Training in Java, Python, and web technologies. "
            "Strong aptitude and programming fundamentals required."
        ),
        "responsibilities": "Training, coding assignments, project work, team collaboration.",
        "required_skills": ["Java", "Python", "SQL", "HTML", "JavaScript", "Git"],
        "experience_min": 0.0, "experience_max": 1.0,
        "education_required": "MCA 2024/2025 Passout",
        "salary_min": 380000, "salary_max": 550000,
        "job_type": "full-time", "work_mode": "onsite",
        "posted_date": _daysago(5),
        "original_url": "https://techmahindra.com/careers/mca-fresher-software-developer",
    },
    {
        "external_id": "SEED-048",
        "title": "AI Product Engineer",
        "company": "Myntra",
        "location": "Bengaluru",
        "description": (
            "Build AI-powered fashion features: visual search, size recommendations, style AI. "
            "Python, deep learning, and REST APIs. "
            "Cross-functional collaboration with product and design teams."
        ),
        "responsibilities": "AI feature development, model integration, evaluation, A/B testing.",
        "required_skills": ["Python", "Deep Learning", "Computer Vision", "PyTorch", "REST API", "Docker", "SQL"],
        "experience_min": 2.0, "experience_max": 6.0,
        "education_required": "MTech/BTech/MCA in CS/AI",
        "salary_min": 1800000, "salary_max": 4000000,
        "job_type": "full-time", "work_mode": "hybrid",
        "posted_date": _daysago(3),
        "original_url": "https://myntra.com/careers/ai-product-engineer",
    },
    {
        "external_id": "SEED-049",
        "title": "Platform Software Engineer (Python/Kubernetes)",
        "company": "Nutanix India",
        "location": "Hyderabad",
        "description": (
            "Build cloud platform features in Python and Go. "
            "Kubernetes operator development, REST APIs, distributed systems. "
            "Strong CS fundamentals required."
        ),
        "responsibilities": "Platform feature development, operator development, testing, documentation.",
        "required_skills": ["Python", "Go", "Kubernetes", "Docker", "REST API", "Linux", "Git", "SQL"],
        "experience_min": 2.0, "experience_max": 7.0,
        "education_required": "BTech/BE in CS",
        "salary_min": 2000000, "salary_max": 4500000,
        "job_type": "full-time", "work_mode": "hybrid",
        "posted_date": _daysago(6),
        "original_url": "https://nutanix.com/careers/platform-engineer-hyderabad",
    },
    {
        "external_id": "SEED-050",
        "title": "Data Science Lead",
        "company": "Bajaj Finserv",
        "location": "Pune",
        "description": (
            "Lead data science initiatives for lending and insurance products. "
            "Credit risk modeling, fraud detection, customer segmentation. "
            "Team management and stakeholder communication skills required."
        ),
        "responsibilities": "Lead data science team, model strategy, stakeholder alignment, deployment.",
        "required_skills": ["Python", "Machine Learning", "Data Science", "SQL", "Scikit-learn", "Pandas", "Statistics", "AWS"],
        "experience_min": 6.0, "experience_max": 12.0,
        "education_required": "MTech/MBA/MSc in CS/Statistics",
        "salary_min": 3000000, "salary_max": 6000000,
        "job_type": "full-time", "work_mode": "hybrid",
        "posted_date": _daysago(8),
        "original_url": "https://bajajfinserv.in/careers/data-science-lead-pune",
    },
]


class SeedDataSource(BaseJobSource):
    """
    Development seed data source.
    Provides realistic Indian tech job listings for testing.
    All jobs are clearly marked with is_seed_data=True.
    """

    name = "seed_data"
    source_type = "seed"
    base_url = "https://localhost/seed"

    def is_available(self) -> bool:
        from app.config import get_settings
        return get_settings().SEED_DEMO_DATA

    def collect(self, query: str = "", location: str = "", max_results: int = 100) -> List[RawJob]:
        import urllib.parse
        jobs = []
        for data in SEED_JOBS_DATA[:max_results]:
            # Guarantee working URL that never 404s: direct to verified company search
            company = data.get("company", "")
            title = data.get("title", "")
            orig_url = data.get("original_url", "")
            # If the URL is one of the fictional sample paths, use Google Jobs search query
            if not orig_url or any(domain in orig_url for domain in [
                "razorpay.com/jobs", "careers.ola.com", "persistent.com/careers",
                "careers.infosys.com", "jobs.wipro.com", "careers.swiggy.com",
                "freshworks.com/careers", "careers.zoho.com", "paytm.com/careers",
                "phonepe.com", "careers.flipkart.com", "careers.google.com/jobs/ml-engineer"
            ]):
                safe_url = f"https://www.google.com/search?q={urllib.parse.quote_plus(f'{company} {title} jobs')}"
            else:
                safe_url = orig_url

            job = RawJob(
                external_id=data["external_id"],
                title=title,
                company=company,
                location=data["location"],
                description=data["description"],
                responsibilities=data.get("responsibilities"),
                required_skills=data.get("required_skills", []),
                experience_min=data.get("experience_min"),
                experience_max=data.get("experience_max"),
                education_required=data.get("education_required"),
                salary_min=data.get("salary_min"),
                salary_max=data.get("salary_max"),
                salary_currency="INR",
                job_type=data.get("job_type", "full-time"),
                work_mode=data.get("work_mode"),
                posted_date=data.get("posted_date"),
                original_url=safe_url,
                source_name=self.name,
                is_seed_data=True,
            )
            jobs.append(job)
        return jobs
