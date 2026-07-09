"""
Comprehensive skills database with 100+ skills organized by category.
"""

SKILLS_DATABASE = {
    "Programming Languages": [
        "python", "java", "javascript", "typescript", "c", "c++", "c#",
        "go", "rust", "ruby", "php", "swift", "kotlin", "scala", "r",
        "matlab", "perl", "lua", "dart", "elixir", "haskell", "julia",
        "objective-c", "assembly", "shell", "bash", "powershell"
    ],
    "Frontend": [
        "react", "angular", "vue", "vue.js", "next.js", "nuxt.js", "svelte",
        "html", "css", "sass", "scss", "less", "tailwindcss", "tailwind",
        "bootstrap", "material ui", "chakra ui", "styled-components",
        "webpack", "vite", "babel", "jquery", "redux", "zustand",
        "three.js", "d3.js", "framer motion", "storybook"
    ],
    "Backend & Frameworks": [
        "node.js", "express", "express.js", "fastapi", "django", "flask",
        "spring", "spring boot", ".net", "asp.net", "rails", "ruby on rails",
        "laravel", "nest.js", "nestjs", "gin", "fiber", "actix",
        "graphql", "rest", "restful", "grpc", "websocket", "socket.io",
        "celery", "rabbitmq", "kafka", "redis"
    ],
    "Databases": [
        "sql", "mysql", "postgresql", "postgres", "mongodb", "sqlite",
        "oracle", "sql server", "dynamodb", "cassandra", "couchdb",
        "firebase", "firestore", "supabase", "neo4j", "elasticsearch",
        "influxdb", "mariadb", "redis", "memcached"
    ],
    "Cloud & DevOps": [
        "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "k8s",
        "terraform", "ansible", "jenkins", "github actions", "gitlab ci",
        "circleci", "travis ci", "nginx", "apache", "linux", "ubuntu",
        "aws lambda", "ec2", "s3", "cloudformation", "ecs", "eks",
        "heroku", "vercel", "netlify", "digitalocean", "vagrant",
        "prometheus", "grafana", "datadog", "new relic", "helm",
        "ci/cd", "devops", "sre", "microservices", "serverless"
    ],
    "Data Science & ML": [
        "machine learning", "deep learning", "tensorflow", "pytorch",
        "keras", "scikit-learn", "sklearn", "pandas", "numpy", "scipy",
        "matplotlib", "seaborn", "plotly", "jupyter", "notebook",
        "nlp", "natural language processing", "computer vision", "opencv",
        "transformers", "hugging face", "bert", "gpt", "llm",
        "reinforcement learning", "neural networks", "cnn", "rnn", "lstm",
        "xgboost", "random forest", "regression", "classification",
        "clustering", "pca", "feature engineering", "data mining",
        "big data", "spark", "hadoop", "airflow", "dbt", "etl",
        "power bi", "tableau", "looker", "data visualization"
    ],
    "Tools & Platforms": [
        "git", "github", "gitlab", "bitbucket", "jira", "confluence",
        "slack", "trello", "asana", "notion", "figma", "sketch",
        "adobe xd", "postman", "swagger", "vs code", "intellij",
        "eclipse", "vim", "emacs", "linux", "macos", "windows",
        "agile", "scrum", "kanban", "waterfall"
    ],
    "Testing & QA": [
        "unit testing", "jest", "mocha", "pytest", "junit", "selenium",
        "cypress", "playwright", "puppeteer", "test-driven development", "tdd",
        "behavior-driven development", "bdd", "integration testing",
        "load testing", "performance testing", "qa", "quality assurance"
    ],
    "Security": [
        "cybersecurity", "penetration testing", "owasp", "encryption",
        "ssl", "tls", "oauth", "jwt", "sso", "ldap", "iam",
        "vulnerability assessment", "soc", "siem", "firewall"
    ],
    "Mobile Development": [
        "react native", "flutter", "ios", "android", "swiftui",
        "jetpack compose", "xamarin", "ionic", "cordova",
        "mobile development", "app development"
    ],
    "Soft Skills": [
        "leadership", "communication", "teamwork", "problem solving",
        "critical thinking", "project management", "time management",
        "collaboration", "mentoring", "presentation", "public speaking",
        "analytical", "strategic planning", "decision making",
        "adaptability", "creativity", "innovation"
    ]
}


def get_all_skills() -> list[str]:
    """Return a flat list of all skills across all categories."""
    all_skills = []
    for skills in SKILLS_DATABASE.values():
        all_skills.extend(skills)
    return all_skills


def get_skills_by_category() -> dict[str, list[str]]:
    """Return the full categorized skills dictionary."""
    return SKILLS_DATABASE


def get_category_for_skill(skill: str) -> str | None:
    """Return the category name for a given skill, or None if not found."""
    skill_lower = skill.lower()
    for category, skills in SKILLS_DATABASE.items():
        if skill_lower in skills:
            return category
    return None
