from crewai import Crew
from agents.ranking import ranking_agent

def create_crew(task):

    crew = Crew(
        agents=[ranking_agent],
        tasks=[task],
        verbose=True
    )

    return crew