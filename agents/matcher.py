from crewai import Agent

matching_agent = Agent(
    role="Job Matcher",
    goal="Match CVs with job descriptions",
    backstory="Expert technical recruiter",
    verbose=True
)