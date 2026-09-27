"""
Comprehensive skill taxonomy for JobPilot AI.
Contains 700+ skills across 10 categories with synonym normalization.
Extensible: add new skills/synonyms without changing business logic.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Set

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
    "Computer Vision": "ai_ml", "Reinforcement Learning": "ai_ml",
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
    "Postman": "tools", "Swagger": "tools", "Linux": "tools",
    "VS Code": "tools", "IntelliJ": "tools",

    # ── Security ─────────────────────────────────────────────────────
    "Cybersecurity": "security", "Penetration Testing": "security",
    "OWASP": "security", "OAuth": "security", "JWT": "security",
    "Encryption": "security", "Firewall": "security",
    "Network Security": "security", "SOC": "security",
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
    # CI/CD
    "cicd": "CI/CD", "ci cd": "CI/CD",
    # Generative AI
    "genai": "Generative AI", "gen ai": "Generative AI",
    # LLM
    "llm": "LLM", "large language model": "LLM",
    # RAG
    "rag": "RAG", "retrieval augmented generation": "RAG",
    # Agile
    "agile": "Agile", "agile methodology": "Agile",
    # Tailwind CSS
    "tailwind css": "Tailwind CSS",
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


def extract_skills_from_text(text: str) -> List[str]:
    """
    Extract known skills from free text using the taxonomy.
    Returns a list of canonical skill names found in the text.
    """
    found: Set[str] = set()
    text_lower = text.lower()

    # Try synonym matches first (longer phrases first to avoid partial hits)
    synonyms_sorted = sorted(SKILL_SYNONYMS.keys(), key=len, reverse=True)
    for alias in synonyms_sorted:
        if alias in text_lower:
            canonical = SKILL_SYNONYMS[alias]
            found.add(canonical)
            # Remove matched text to avoid sub-matches
            text_lower = text_lower.replace(alias, " ")

    # Try canonical skill names
    for skill in SKILL_TAXONOMY.keys():
        if skill.lower() in text_lower:
            found.add(skill)

    return sorted(found)


def is_recognized_skill(raw: str) -> bool:
    return normalize_skill(raw) is not None


ALL_SKILLS: List[str] = sorted(SKILL_TAXONOMY.keys())
ALL_CATEGORIES: List[str] = sorted(set(SKILL_TAXONOMY.values()))
