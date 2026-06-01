from crewai import Agent

ranking_agent = Agent(
    role="Candidate Ranking Specialist",

    goal="""
    Analyze CVs against job descriptions
    and rank candidates accurately
    """,

    backstory="""
    Expert HR recruiter with deep
    understanding of technical hiring
    """,

    verbose=True,

    llm="ollama/llama3.2"
)