from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from .tools.serper_tool import serper_tool
from typing import List


@CrewBase
class WorldEconomicsCrew():
    """WorldEconomics crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def user_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['user_analyst'],
            verbose=True
        )

    @agent
    def data_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['data_researcher'],
            tools=[serper_tool],
            verbose=True
        )

    @agent
    def economic_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['economic_analyst'],
            verbose=True
        )

    @agent
    def response_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['response_writer'],
            verbose=True
        )


    @task
    def user_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['user_analysis_task'],
            output_file='user_analysis_report.md'
            
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'],
            context=[self.user_analysis_task()],
            output_file='research_task_report.md'
        )

    @task
    def analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['analysis_task'],
            context=[self.research_task()],
            output_file="analysis_task_report.md"
        )

    @task
    def reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_task'],
            context=[self.user_analysis_task(),self.analysis_task()],
            output_file='final_report.md'
        )


    @crew
    def crew(self) -> Crew:
        """Creates the WorldEconomics crew"""
        

        return Crew(
            agents=[
                self.user_analyst(),
                self.data_researcher(),
                self.economic_analyst(),
                self.response_writer()
            ],
            tasks=[
                self.user_analysis_task(),
                self.research_task(),
                self.analysis_task(),
                self.reporting_task()
            ],
            process=Process.sequential,
            verbose=True,
        )