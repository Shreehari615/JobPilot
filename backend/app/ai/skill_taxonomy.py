"""
Comprehensive skill taxonomy for JobPilot AI.
Contains 700+ skills across 10 categories with synonym normalization.
Extensible: add new skills/synonyms without changing business logic.
"""
from __future__ import annotations

import re
from typing import Dict, List, Optional, Set, Tuple

# ── Canonical skill name → category ──────────────────────────────────
SKILL_TAXONOMY: Dict[str, str] = {
    # ── Programming Languages ─────────────────────────────────────────
    "Python": "languages", "Java": "languages", "C": "languages",
    "C++": "languages", "C#": "languages", "Go": "languages",
    "Rust": "languages", "Kotlin": "languages", "Swift": "languages",
    "JavaScript": "languages", "TypeScript": "languages",
    "PHP": "languages", "Ruby": "languages", "Scala": "languages",
    "R": "languages", "MATLAB": "languages", "Perl": "languages",
    "Shell": "languages", "Bash": "languages", "PowerShell": "languages",
    "Dart": "languages", "Lua": "languages", "Haskell": "languages",
    "Elixir": "languages", "Erlang": "languages",

    # ── Web Frontend ──────────────────────────────────────────────────
    "React": "web", "Angular": "web", "Vue.js": "web",
    "Next.js": "web", "Nuxt.js": "web", "Svelte": "web",
    "HTML": "web", "CSS": "web", "SASS": "web", "SCSS": "web",
    "Tailwind CSS": "web", "Bootstrap": "web", "Material UI": "web",
    "jQuery": "web", "Redux": "web", "Webpack": "web", "Vite": "web",
    "GraphQL": "web", "REST API": "web", "WebSocket": "web",

    # ── Web Backend ───────────────────────────────────────────────────
    "Node.js": "web", "Express.js": "web", "FastAPI": "web",
    "Django": "web", "Flask": "web", "Spring Boot": "web",
    "Spring": "web", "Laravel": "web", "Rails": "web",
    "ASP.NET": "web", "NestJS": "web", "Gin": "web",
    "gRPC": "web", "Microservices": "web", "REST": "web",

    # ── AI / ML ───────────────────────────────────────────────────────
    "Machine Learning": "ai_ml", "Deep Learning": "ai_ml",
    "Natural Language Processing": "ai_ml", "NLP": "ai_ml",
    "Computer Vision": "ai_ml", "Image Processing": "ai_ml",
    "YOLO": "ai_ml", "Reinforcement Learning": "ai_ml",
    "TensorFlow": "ai_ml", "PyTorch": "ai_ml", "Keras": "ai_ml",
    "Scikit-learn": "ai_ml", "XGBoost": "ai_ml", "LightGBM": "ai_ml",
    "Pandas": "ai_ml", "NumPy": "ai_ml", "Matplotlib": "ai_ml",
    "Seaborn": "ai_ml", "OpenCV": "ai_ml", "Hugging Face": "ai_ml",
    "Transformers": "ai_ml", "BERT": "ai_ml", "GPT": "ai_ml",
    "LLM": "ai_ml", "Generative AI": "ai_ml", "MLflow": "ai_ml",
    "Data Science": "ai_ml", "Data Analysis": "ai_ml",
    "Data Visualization": "ai_ml", "Statistics": "ai_ml",
    "Time Series": "ai_ml", "Recommendation Systems": "ai_ml",
    "spaCy": "ai_ml", "NLTK": "ai_ml", "Langchain": "ai_ml",
    "RAG": "ai_ml", "Vector Database": "ai_ml",

    # ── Databases ─────────────────────────────────────────────────────
    "MySQL": "databases", "PostgreSQL": "databases",
    "MongoDB": "databases", "Redis": "databases",
    "Cassandra": "databases", "Elasticsearch": "databases",
    "SQLite": "databases", "Oracle": "databases", "SQL Server": "databases",
    "DynamoDB": "databases", "Firebase": "databases",
    "DBMS": "databases", "RDBMS": "databases",
    "Neo4j": "databases", "InfluxDB": "databases",
    "SQL": "databases", "NoSQL": "databases",
    "Pinecone": "databases", "Weaviate": "databases",
    "ChromaDB": "databases", "Qdrant": "databases",

    # ── Cloud & DevOps ────────────────────────────────────────────────
    "AWS": "cloud", "Azure": "cloud", "Google Cloud": "cloud",
    "GCP": "cloud", "Kubernetes": "cloud", "Docker": "cloud",
    "Terraform": "cloud", "Ansible": "cloud", "Jenkins": "cloud",
    "GitHub Actions": "cloud", "GitLab CI": "cloud", "CircleCI": "cloud",
    "Helm": "cloud", "Prometheus": "cloud", "Grafana": "cloud",
    "Linux": "cloud", "Nginx": "cloud", "Apache": "cloud",
    "CI/CD": "cloud", "DevOps": "cloud", "SRE": "cloud",
    "Serverless": "cloud", "Lambda": "cloud", "CloudFormation": "cloud",
    "Vercel": "cloud", "Netlify": "cloud",
    "Pulumi": "cloud", "Vagrant": "cloud",

    # ── Mobile ────────────────────────────────────────────────────────
    "Android": "mobile", "iOS": "mobile", "React Native": "mobile",
    "Flutter": "mobile", "Xamarin": "mobile", "Ionic": "mobile",

    # ── Data Engineering ──────────────────────────────────────────────
    "Apache Spark": "data_eng", "Kafka": "data_eng", "Hadoop": "data_eng",
    "Airflow": "data_eng", "dbt": "data_eng", "Snowflake": "data_eng",
    "BigQuery": "data_eng", "Redshift": "data_eng", "ETL": "data_eng",
    "Data Pipeline": "data_eng", "PySpark": "data_eng",
    "Databricks": "data_eng", "Delta Lake": "data_eng",

    # ── Tools & Practices ─────────────────────────────────────────────
    "Git": "tools", "GitHub": "tools", "GitLab": "tools",
    "Jira": "tools", "Confluence": "tools", "Agile": "tools",
    "Scrum": "tools", "Kanban": "tools", "TDD": "tools",
    "Unit Testing": "tools", "Pytest": "tools", "Jest": "tools",
    "Postman": "tools", "Swagger": "tools",
    "VS Code": "tools", "IntelliJ": "tools",
    "Data Structures": "tools", "Algorithms": "tools",
    "Object-Oriented Programming": "tools", "SDLC": "tools",
    "Cursor": "tools", "Claude": "tools", "NotebookLM": "tools",
    "Antigravity": "tools",

    # ── Security ─────────────────────────────────────────────────────
    "Cybersecurity": "security", "Penetration Testing": "security",
    "OWASP": "security", "OAuth": "security", "JWT": "security",
    "Encryption": "security", "Firewall": "security",
    "Network Security": "security", "SOC": "security",

    # ── Finance & Accounting ──────────────────────────────────────────
    "Financial Analysis": "finance", "Accounting": "finance",
    "Bookkeeping": "finance", "Financial Modeling": "finance",
    "Auditing": "finance", "Tax Compliance": "finance",
    "GST": "finance", "Budgeting": "finance", "Payroll": "finance",
    "QuickBooks": "finance", "Tally": "finance", "SAP FICO": "finance",
    "Wealth Management": "finance", "Risk Analysis": "finance",
    "Financial Reporting": "finance", "Accounts Payable": "finance",
    "Accounts Receivable": "finance", "Cost Accounting": "finance",

    # ── Sales & Business Development ─────────────────────────────────
    "B2B Sales": "sales", "B2C Sales": "sales",
    "Lead Generation": "sales", "Inside Sales": "sales",
    "CRM": "sales", "Salesforce": "sales", "HubSpot": "sales",
    "Negotiation": "sales", "Account Management": "sales",
    "Cold Calling": "sales", "Pipeline Management": "sales",
    "Client Relations": "sales", "Solution Selling": "sales",
    "Business Development": "sales",

    # ── Marketing & Advertising ───────────────────────────────────────
    "Digital Marketing": "marketing", "SEO": "marketing",
    "SEM": "marketing", "Content Marketing": "marketing",
    "Social Media Marketing": "marketing", "Copywriting": "marketing",
    "Google Ads": "marketing", "Meta Ads": "marketing",
    "Email Marketing": "marketing", "Brand Strategy": "marketing",
    "Market Research": "marketing", "Google Analytics": "marketing",
    "Public Relations": "marketing", "Content Writing": "marketing",

    # ── Human Resources ───────────────────────────────────────────────
    "Talent Acquisition": "hr", "Recruitment": "hr",
    "Employee Relations": "hr", "HR Policies": "hr",
    "Onboarding": "hr", "Performance Management": "hr",
    "Payroll Administration": "hr", "HRIS": "hr",
    "Workday": "hr", "BambooHR": "hr", "Labor Law": "hr",
    "Employee Engagement": "hr", "Human Resources": "hr",

    # ── Operations & Logistics ────────────────────────────────────────
    "Supply Chain Management": "operations", "Logistics": "operations",
    "Operations Management": "operations", "Procurement": "operations",
    "Inventory Management": "operations", "Vendor Management": "operations",
    "Six Sigma": "operations", "Lean Manufacturing": "operations",
    "ERP": "operations", "SAP": "operations",
    "Warehouse Management": "operations",

    # ── Healthcare & Medical ──────────────────────────────────────────
    "Patient Care": "healthcare", "Nursing": "healthcare",
    "Clinical Research": "healthcare", "Pharmacology": "healthcare",
    "Medical Records": "healthcare", "HIPAA": "healthcare",
    "Patient Assessment": "healthcare", "First Aid": "healthcare",
    "CPR": "healthcare", "BLS": "healthcare", "Phlebotomy": "healthcare",
    "Triage": "healthcare", "Healthcare Management": "healthcare",

    # ── Creative & Design ─────────────────────────────────────────────
    "Graphic Design": "creative", "UI/UX Design": "creative",
    "Figma": "creative", "Adobe Photoshop": "creative",
    "Adobe Illustrator": "creative", "Adobe Premiere Pro": "creative",
    "After Effects": "creative", "Video Editing": "creative",
    "Canva": "creative", "Wireframing": "creative",

    # ── Customer Support ──────────────────────────────────────────────
    "Customer Service": "customer_service", "Technical Support": "customer_service",
    "Helpdesk": "customer_service", "Zendesk": "customer_service",
    "Freshdesk": "customer_service", "Customer Experience": "customer_service",
    "Call Center Operations": "customer_service", "Conflict Resolution": "customer_service",
    "Ticketing Systems": "customer_service",

    # ── Education & Teaching ──────────────────────────────────────────
    "Curriculum Development": "education", "Classroom Management": "education",
    "Lesson Planning": "education", "Instructional Design": "education",
    "E-Learning": "education", "Educational Assessment": "education",
    "Tutoring": "education", "Pedagogy": "education",

    # ── Legal & Compliance ────────────────────────────────────────────
    "Legal Research": "legal", "Contract Drafting": "legal",
    "Contract Negotiation": "legal", "Compliance": "legal",
    "Due Diligence": "legal", "Corporate Law": "legal",
    "Intellectual Property": "legal", "Regulatory Affairs": "legal",

    # ── Business & Management ─────────────────────────────────────────
    "Project Management": "business", "Leadership": "business",
    "Strategic Planning": "business", "Business Analysis": "business",
    "Problem Solving": "business", "Team Collaboration": "business",
    "Time Management": "business", "Public Speaking": "business",
}



# ── Synonym normalization map (alias → canonical) ─────────────────────
SKILL_SYNONYMS: Dict[str, str] = {
    # JavaScript variants
    "js": "JavaScript", "javascript": "JavaScript", "ecmascript": "JavaScript",
    "es6": "JavaScript", "es2015": "JavaScript",
    # TypeScript
    "ts": "TypeScript", "typescript": "TypeScript",
    # React
    "reactjs": "React", "react.js": "React", "react js": "React",
    # Angular
    "angularjs": "Angular", "angular.js": "Angular",
    # Vue
    "vuejs": "Vue.js", "vue js": "Vue.js", "vue": "Vue.js",
    # Node
    "nodejs": "Node.js", "node": "Node.js", "node js": "Node.js",
    # Express
    "express": "Express.js", "expressjs": "Express.js",
    # Python
    "py": "Python", "python3": "Python",
    # PostgreSQL
    "postgres": "PostgreSQL", "postgresql": "PostgreSQL", "psql": "PostgreSQL",
    # MongoDB
    "mongo": "MongoDB", "mongodb": "MongoDB",
    # MySQL
    "mysql": "MySQL",
    # Redis
    "redis": "Redis",
    # Machine Learning
    "ml": "Machine Learning", "machine learning": "Machine Learning",
    # Deep Learning
    "dl": "Deep Learning", "deep learning": "Deep Learning",
    # NLP
    "nlp": "NLP", "natural language processing": "NLP",
    # TensorFlow
    "tensorflow": "TensorFlow", "tf": "TensorFlow",
    # PyTorch
    "pytorch": "PyTorch", "torch": "PyTorch",
    # Scikit-learn
    "sklearn": "Scikit-learn", "scikit learn": "Scikit-learn",
    "scikit-learn": "Scikit-learn",
    # AWS
    "amazon web services": "AWS", "aws": "AWS",
    # Google Cloud
    "gcp": "Google Cloud", "google cloud platform": "Google Cloud",
    # CSS variants
    "css3": "CSS", "css2": "CSS",
    # HTML variants
    "html5": "HTML", "html4": "HTML",
    # Docker
    "docker": "Docker",
    # Kubernetes
    "k8s": "Kubernetes", "kubernetes": "Kubernetes",
    # Git
    "git": "Git",
    # SQL
    "sql": "SQL", "structured query language": "SQL",
    # Java
    "java": "Java",
    # Spring
    "spring": "Spring", "spring boot": "Spring Boot",
    # Django
    "django": "Django",
    # Flask
    "flask": "Flask",
    # FastAPI
    "fastapi": "FastAPI",
    # C variants
    "c language": "C", "c programming": "C",
    "c++": "C++", "cpp": "C++",
    "c#": "C#", "csharp": "C#", "c sharp": "C#",
    # Tailwind
    "tailwind": "Tailwind CSS", "tailwindcss": "Tailwind CSS",
    # Next.js
    "nextjs": "Next.js", "next js": "Next.js",
    # Pandas
    "pandas": "Pandas",
    # NumPy
    "numpy": "NumPy",
    # OpenCV
    "opencv": "OpenCV", "open cv": "OpenCV",
    # Spark
    "spark": "Apache Spark", "pyspark": "PySpark",
    # Kafka
    "kafka": "Kafka", "apache kafka": "Kafka",
    # Elasticsearch
    "elastic search": "Elasticsearch", "elastic": "Elasticsearch",
    # GraphQL
    "graphql": "GraphQL",
    # REST
    "rest": "REST API", "restful": "REST API", "restful api": "REST API",
    "rest apis": "REST API", "restful apis": "REST API",
    # CI/CD
    "cicd": "CI/CD", "ci cd": "CI/CD",
    # Generative AI
    "genai": "Generative AI", "gen ai": "Generative AI",
    # LLM
    "llm": "LLM", "large language model": "LLM",
    # RAG
    "rag": "RAG", "retrieval augmented generation": "RAG",
    "retrieval-augmented generation": "RAG",
    # Agile
    "agile": "Agile", "agile methodology": "Agile",
    # Tailwind CSS
    "tailwind css": "Tailwind CSS",
    # Data Structures & Algorithms
    "data structures": "Data Structures", "data structure": "Data Structures",
    "dsa": "Data Structures", "data structures and algorithms": "Data Structures",
    "algorithms": "Algorithms", "algorithm": "Algorithms",
    # Object-Oriented Programming & SDLC
    "oop": "Object-Oriented Programming", "oops": "Object-Oriented Programming",
    "object-oriented programming": "Object-Oriented Programming",
    "object oriented programming": "Object-Oriented Programming",
    "sdlc": "SDLC", "software development life cycle": "SDLC",
    "software development lifecycle": "SDLC",
    # DBMS
    "dbms": "DBMS", "rdbms": "DBMS", "database management system": "DBMS",
    "database management systems": "DBMS",
    # AI / ML
    "image processing": "Image Processing", "yolo": "YOLO",
    # Cloud & DevOps
    "vercel": "Vercel", "netlify": "Netlify",
    # Developer Tools
    "cursor": "Cursor", "claude": "Claude", "notebooklm": "NotebookLM",
    "antigravity": "Antigravity", "vscode": "VS Code",
    "visual studio code": "VS Code",
    # Golang
    "golang": "Go", "go language": "Go", "go programming": "Go",
    # Finance & Accounting
    "financial analysis": "Financial Analysis", "accounting": "Accounting",
    "bookkeeping": "Bookkeeping", "financial modeling": "Financial Modeling",
    "auditing": "Auditing", "tax compliance": "Tax Compliance",
    "taxation": "Tax Compliance", "gst": "GST", "budgeting": "Budgeting",
    "payroll": "Payroll", "quickbooks": "QuickBooks", "tally": "Tally",
    "tally erp": "Tally", "tally prime": "Tally", "sap fico": "SAP FICO",
    "wealth management": "Wealth Management", "risk analysis": "Risk Analysis",
    "financial reporting": "Financial Reporting", "accounts payable": "Accounts Payable",
    "accounts receivable": "Accounts Receivable", "cost accounting": "Cost Accounting",
    # Sales & BD
    "b2b sales": "B2B Sales", "b2c sales": "B2C Sales", "lead generation": "Lead Generation",
    "inside sales": "Inside Sales", "crm": "CRM", "salesforce": "Salesforce",
    "hubspot": "HubSpot", "negotiation": "Negotiation", "account management": "Account Management",
    "cold calling": "Cold Calling", "pipeline management": "Pipeline Management",
    "client relations": "Client Relations", "solution selling": "Solution Selling",
    "business development": "Business Development", "bde": "Business Development",
    # Marketing & Creative
    "digital marketing": "Digital Marketing", "seo": "SEO", "sem": "SEM",
    "content marketing": "Content Marketing", "social media marketing": "Social Media Marketing",
    "smm": "Social Media Marketing", "copywriting": "Copywriting",
    "google ads": "Google Ads", "meta ads": "Meta Ads", "facebook ads": "Meta Ads",
    "email marketing": "Email Marketing", "brand strategy": "Brand Strategy",
    "market research": "Market Research", "google analytics": "Google Analytics",
    "public relations": "Public Relations", "content writing": "Content Writing",
    "graphic design": "Graphic Design", "ui/ux": "UI/UX Design", "ui/ux design": "UI/UX Design",
    "ui ux": "UI/UX Design", "ui design": "UI/UX Design", "ux design": "UI/UX Design",
    "figma": "Figma", "photoshop": "Adobe Photoshop", "adobe photoshop": "Adobe Photoshop",
    "illustrator": "Adobe Illustrator", "adobe illustrator": "Adobe Illustrator",
    "premiere pro": "Adobe Premiere Pro", "after effects": "After Effects",
    "video editing": "Video Editing", "canva": "Canva", "wireframing": "Wireframing",
    # Human Resources
    "talent acquisition": "Talent Acquisition", "recruitment": "Recruitment",
    "recruiting": "Recruitment", "employee relations": "Employee Relations",
    "hr policies": "HR Policies", "onboarding": "Onboarding",
    "performance management": "Performance Management", "payroll administration": "Payroll Administration",
    "hris": "HRIS", "workday": "Workday", "bamboohr": "BambooHR",
    "labor law": "Labor Law", "employee engagement": "Employee Engagement",
    "human resources": "Human Resources", "hr": "Human Resources",
    # Operations & Supply Chain
    "supply chain management": "Supply Chain Management", "supply chain": "Supply Chain Management",
    "logistics": "Logistics", "operations management": "Operations Management",
    "procurement": "Procurement", "inventory management": "Inventory Management",
    "vendor management": "Vendor Management", "six sigma": "Six Sigma",
    "lean manufacturing": "Lean Manufacturing", "erp": "ERP", "sap": "SAP",
    "warehouse management": "Warehouse Management",
    # Healthcare
    "patient care": "Patient Care", "nursing": "Nursing", "clinical research": "Clinical Research",
    "pharmacology": "Pharmacology", "medical records": "Medical Records", "hipaa": "HIPAA",
    "patient assessment": "Patient Assessment", "first aid": "First Aid", "cpr": "CPR",
    "bls": "BLS", "phlebotomy": "Phlebotomy", "triage": "Triage",
    "healthcare management": "Healthcare Management",
    # Customer Support
    "customer service": "Customer Service", "technical support": "Technical Support",
    "helpdesk": "Helpdesk", "zendesk": "Zendesk", "freshdesk": "Freshdesk",
    "customer experience": "Customer Experience", "cx": "Customer Experience",
    "call center": "Call Center Operations", "call center operations": "Call Center Operations",
    "conflict resolution": "Conflict Resolution", "ticketing systems": "Ticketing Systems",
    # Education
    "curriculum development": "Curriculum Development", "classroom management": "Classroom Management",
    "lesson planning": "Lesson Planning", "instructional design": "Instructional Design",
    "e-learning": "E-Learning", "educational assessment": "Educational Assessment",
    "tutoring": "Tutoring", "pedagogy": "Pedagogy",
    # Legal & Compliance
    "legal research": "Legal Research", "contract drafting": "Contract Drafting",
    "contract negotiation": "Contract Negotiation", "compliance": "Compliance",
    "due diligence": "Due Diligence", "corporate law": "Corporate Law",
    "intellectual property": "Intellectual Property", "regulatory affairs": "Regulatory Affairs",
    # Business & General
    "project management": "Project Management", "leadership": "Leadership",
    "strategic planning": "Strategic Planning", "business analysis": "Business Analysis",
    "problem solving": "Problem Solving", "team collaboration": "Team Collaboration",
    "time management": "Time Management", "public speaking": "Public Speaking",
}

# ── Related skills for partial-match (Phase II expansible) ───────────
RELATED_SKILLS: Dict[str, List[str]] = {
    "Python": ["R", "Julia", "Scala"],
    "JavaScript": ["TypeScript", "Node.js"],
    "TypeScript": ["JavaScript"],
    "React": ["Vue.js", "Angular", "Svelte"],
    "Vue.js": ["React", "Angular"],
    "Angular": ["React", "Vue.js"],
    "TensorFlow": ["PyTorch", "Keras"],
    "PyTorch": ["TensorFlow", "Keras"],
    "Machine Learning": ["Deep Learning", "Data Science"],
    "Deep Learning": ["Machine Learning", "NLP", "Computer Vision"],
    "NLP": ["Machine Learning", "Deep Learning", "spaCy", "NLTK"],
    "MySQL": ["PostgreSQL", "SQL", "Oracle"],
    "PostgreSQL": ["MySQL", "SQL", "SQLite"],
    "MongoDB": ["Cassandra", "Firebase", "DynamoDB"],
    "AWS": ["Azure", "Google Cloud"],
    "Azure": ["AWS", "Google Cloud"],
    "Google Cloud": ["AWS", "Azure"],
    "Docker": ["Kubernetes", "Podman"],
    "Kubernetes": ["Docker", "Helm"],
    "Django": ["Flask", "FastAPI"],
    "Flask": ["Django", "FastAPI"],
    "FastAPI": ["Flask", "Django"],
    "Node.js": ["Express.js", "NestJS"],
    "Apache Spark": ["PySpark", "Hadoop"],
    "Git": ["GitHub", "GitLab"],
    # Cross-industry relations
    "Accounting": ["Bookkeeping", "Auditing", "Financial Reporting", "Tally"],
    "Financial Analysis": ["Financial Modeling", "Budgeting", "Risk Analysis"],
    "Digital Marketing": ["SEO", "SEM", "Content Marketing", "Social Media Marketing", "Google Ads"],
    "SEO": ["SEM", "Digital Marketing", "Google Analytics"],
    "Talent Acquisition": ["Recruitment", "Onboarding", "HR Policies"],
    "Recruitment": ["Talent Acquisition", "Technical Recruiting", "HRIS"],
    "B2B Sales": ["Lead Generation", "Inside Sales", "CRM", "Salesforce", "Negotiation"],
    "Supply Chain Management": ["Logistics", "Procurement", "Inventory Management"],
    "Nursing": ["Patient Care", "Patient Assessment", "Triage", "BLS", "CPR"],
    "Graphic Design": ["UI/UX Design", "Figma", "Adobe Photoshop", "Adobe Illustrator"],
    "Customer Service": ["Technical Support", "Helpdesk", "Zendesk", "Customer Experience"],
}


def normalize_skill(raw: str) -> Optional[str]:
    """
    Normalize a raw skill string to its canonical form.
    Returns None if not recognized.
    """
    cleaned = raw.strip().lower()
    # Check synonyms first (case-insensitive)
    if cleaned in SKILL_SYNONYMS:
        return SKILL_SYNONYMS[cleaned]
    # Check canonical names (case-insensitive)
    for canonical in SKILL_TAXONOMY.keys():
        if canonical.lower() == cleaned:
            return canonical
    return None


def get_skill_category(skill: str) -> Optional[str]:
    """Return the category of a normalized skill."""
    return SKILL_TAXONOMY.get(skill)


def get_related_skills(skill: str) -> List[str]:
    """Return related/synonymous skills for partial matching."""
    return RELATED_SKILLS.get(skill, [])


# ── Sensitive Skill Rules (Requiring Token Boundaries & Context) ──────
SENSITIVE_SKILL_RULES: List[Tuple[str, re.Pattern]] = [
    # C language: must not match single letter 'c' in normal words/grades/headings
    (
        "C",
        re.compile(
            r"(?:"
            r"(?i:programming\s+languages?|languages?)\s*:[^.\n]*?(?<![\w#+])C(?![\w#+])|"
            r"(?<![\w#+])C\s*\((?:Basic|Intermediate|Advanced|Proficient)\)|"
            r"(?<![\w#+])C\s*/\s*C\+\+|(?![\w#+])C\+\+\s*/\s*C(?![\w#+])|"
            r"(?i:\bANSI\s+C\b)|"
            r"(?i:\bC\s+(?:language|programming)\b)|"
            r"(?i:(?<![\w#+])(?:python|java|c\+\+|c#|rust|go|swift|kotlin|sql|ruby)\s*,\s*)C(?![\w#+])|"
            r"(?<![\w#+])C\s*,\s*(?i:(?:python|java|c\+\+|c#|rust|go|swift|kotlin|sql|ruby)(?![\w#+]))"
            r")"
        ),
    ),
    # R language: must not match middle initials or college acronyms (e.g. S R N M N College)
    (
        "R",
        re.compile(
            r"(?:"
            r"(?i:\b[Rr]\s+(?:programming|language|script|studio)\b)|"
            r"(?i:programming\s+languages?|languages?)\s*:[^.\n]*?(?<![\w#+])R(?![\w#+])|"
            r"(?i:(?<![\w#+])(?:python|sql|matlab|scala|julia|sas|spss)\s*[,/&]\s*)R(?![\w#+])|"
            r"(?<![\w#+])R\s*[,/&]\s*(?i:(?:python|sql|matlab|scala|julia|sas|spss)(?![\w#+]))"
            r")"
        ),
    ),
    # Go language: must not match English verb 'go' or inside 'algorithms'
    (
        "Go",
        re.compile(
            r"(?:"
            r"\bgolang\b|"
            r"\bgo\s+(?:language|programming)\b|"
            r"(?:programming\s+languages?|languages?)\s*:[^.\n]*?(?<![\w#+])Go(?![\w#+])|"
            r"(?<![\w#+])(?:python|java|rust|c\+\+|c#|ruby)\s*[,/]\s*Go\b|"
            r"\bGo\s*[,/]\s*(?:python|java|rust|c\+\+|c#|ruby)(?![\w#+])"
            r")",
            re.IGNORECASE,
        ),
    ),
    # Gin web framework: must not match inside 'engineered'
    (
        "Gin",
        re.compile(
            r"(?:"
            r"\bgin\s+(?:framework|web\s+framework|gonic)\b|"
            r"\bgin-gonic\b|"
            r"(?<![\w#+])(?:go|golang)\s*[,/]\s*Gin(?![\w#+])|"
            r"(?<![\w#+])Gin\s*[,/]\s*(?:go|golang)(?![\w#+])"
            r")",
            re.IGNORECASE,
        ),
    ),
    # RAG (Retrieval-Augmented Generation): must not match inside 'storage'
    (
        "RAG",
        re.compile(
            r"(?:"
            r"(?i:\bretrieval[\s-]augmented\s+generation\b)|"
            r"(?<![\w#+])RAG(?![\w#+])"
            r")"
        ),
    ),
    # REST API: must not match lowercase 'rest' ("the rest of...")
    (
        "REST API",
        re.compile(
            r"(?:"
            r"\brest\s*apis?\b|"
            r"\brestful(?:\s*apis?)?\b|"
            r"\brest-api\b|"
            r"(?<![\w#+])REST(?![\w#+])"
            r")",
            re.IGNORECASE,
        ),
    ),
    # CI/CD: boundary matching with dash/slash
    (
        "CI/CD",
        re.compile(
            r"(?:"
            r"(?<![\w#+])ci\s*[/–-]\s*cd(?![\w#+])|"
            r"\bcicd\b"
            r")",
            re.IGNORECASE,
        ),
    ),
    # C++ & C#
    ("C++", re.compile(r"(?<![\w#+])(?:c\+\+|cpp)(?![\w#+])", re.IGNORECASE)),
    ("C#", re.compile(r"(?<![\w#+])(?:c#|csharp|c\s+sharp)(?![\w#+])", re.IGNORECASE)),
    # TypeScript: must not match lowercase 'ts' inside 'projects', 'datasets'
    ("TypeScript", re.compile(r"(?<![\w#+])(?:typescript|TS)(?![\w#+])")),
    # JavaScript: must not match lowercase 'js'
    ("JavaScript", re.compile(r"(?<![\w#+])(?:javascript|ecmascript|es6|es2015|JS)(?![\w#+])")),
    # Deep Learning: must not match lowercase 'dl' inside 'sdlc'
    ("Deep Learning", re.compile(r"(?<![\w#+])(?:deep\s+learning|DL)(?![\w#+])")),
    # Machine Learning: must not match lowercase 'ml' inside 'html'
    ("Machine Learning", re.compile(r"(?<![\w#+])(?:machine\s+learning|ML)(?![\w#+])")),
    # TensorFlow: must not match lowercase 'tf' inside 'platform'
    ("TensorFlow", re.compile(r"(?<![\w#+])(?:tensorflow|TF)(?![\w#+])")),
    # Human Resources: must not match 'hr' inside 'chrome', 'three'
    ("Human Resources", re.compile(r"(?<![\w#+])(?:human\s+resources|HR)(?![\w#+])")),
    # UI/UX Design
    ("UI/UX Design", re.compile(r"(?<![\w#+])(?:UI\s*/\s*UX|UI/UX|UIUX|UX\s*/\s*UI|UI\s+Design|UX\s+Design)(?![\w#+])", re.IGNORECASE)),
    # Public Relations
    ("Public Relations", re.compile(r"(?<![\w#+])(?:public\s+relations|PR)(?![\w#+])")),
    # SEO & SEM
    ("SEO", re.compile(r"(?<![\w#+])(?:search\s+engine\s+optimization|SEO)(?![\w#+])", re.IGNORECASE)),
    ("SEM", re.compile(r"(?<![\w#+])(?:search\s+engine\s+marketing|SEM)(?![\w#+])", re.IGNORECASE)),
    # CRM & ERP
    ("CRM", re.compile(r"(?<![\w#+])(?:customer\s+relationship\s+management|CRM)(?![\w#+])", re.IGNORECASE)),
    ("ERP", re.compile(r"(?<![\w#+])(?:enterprise\s+resource\s+planning|ERP)(?![\w#+])", re.IGNORECASE)),
    # GST
    ("GST", re.compile(r"(?<![\w#+])(?:goods\s+and\s+services\s+tax|GST)(?![\w#+])", re.IGNORECASE)),
    # CPR & BLS
    ("CPR", re.compile(r"(?<![\w#+])CPR(?![\w#+])")),
    ("BLS", re.compile(r"(?<![\w#+])BLS(?![\w#+])")),
]

SENSITIVE_KEYS: Set[str] = {
    "c", "r", "go", "gin", "rag", "rest", "rest api", "ci/cd",
    "ts", "js", "dl", "ml", "tf", "py", "c++", "cpp", "c#",
    "hr", "pr", "seo", "sem", "crm", "erp", "gst", "cpr", "bls",
    "ui/ux", "uiux", "cx",
}



def extract_skills_from_text(text: str) -> List[str]:
    """
    Extract known skills from free text using token-boundary matching and taxonomy.
    Prevents false substring matches (e.g. 'gin' in 'engineered', 'scala' in 'scalable',
    'rag' in 'storage', 'ts' in 'projects', single letter 'r'/'c').
    Uses span tracking so longer multi-word skills claim their span and don't trigger
    unintended sub-word matches.
    """
    if not text:
        return []

    found: Set[str] = set()
    claimed_spans: List[Tuple[int, int]] = []

    def is_span_claimed(start: int, end: int) -> bool:
        for cs, ce in claimed_spans:
            if cs <= start and end <= ce:
                return True
        return False

    # 1. First run sensitive skill rules (strict boundary / context-aware)
    for canon, pattern in SENSITIVE_SKILL_RULES:
        for m in pattern.finditer(text):
            s, e = m.span()
            if not is_span_claimed(s, e):
                found.add(canon)
                claimed_spans.append((s, e))

    # 2. Collect candidate phrases (both synonyms and canonical skills)
    # Sort by length descending so longer phrases match first and claim spans
    candidates: List[Tuple[str, str]] = []

    for alias, canon in SKILL_SYNONYMS.items():
        if alias.lower() in SENSITIVE_KEYS or len(alias) < 3:
            continue
        candidates.append((alias, canon))

    for canon in SKILL_TAXONOMY.keys():
        if canon.lower() in SENSITIVE_KEYS or len(canon) < 3:
            continue
        candidates.append((canon, canon))

    candidates.sort(key=lambda x: len(x[0]), reverse=True)

    for phrase, canonical in candidates:
        p = re.compile(r"(?<![\w#+])" + re.escape(phrase) + r"(?![\w#+])", re.IGNORECASE)
        for m in p.finditer(text):
            s, e = m.span()
            if not is_span_claimed(s, e):
                found.add(canonical)
                claimed_spans.append((s, e))

    return sorted(found)


def is_recognized_skill(raw: str) -> bool:
    return normalize_skill(raw) is not None


ALL_SKILLS: List[str] = sorted(SKILL_TAXONOMY.keys())
ALL_CATEGORIES: List[str] = sorted(set(SKILL_TAXONOMY.values()))
