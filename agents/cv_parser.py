from crewai import Agent

cv_parser_agent = Agent(
    role="CV Analyzer",
    goal="Extract skills, experience and education from CVs",
    backstory="Expert HR AI recruiter",
    verbose=True
)