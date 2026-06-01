
import re

def extract_skills(text):

    predefined_skills = [

        "Python",
        "Django",
        "Flask",
        "SQL",
        "PostgreSQL",
        "Git",
        "GitHub",
        "Docker",
        "AWS",
        "Machine Learning",
        "Pandas",
        "NumPy",
        "React",
        "JavaScript",
        "REST API"
    ]

    found_skills = []

    for skill in predefined_skills:

        pattern = re.compile(
            re.escape(skill),
            re.IGNORECASE
        )

        if pattern.search(text):

            found_skills.append(skill)

    return found_skills

