from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
import os

from langchain_openai import ChatOpenAI

os.environ['OPENAI_API_BASE'] = 'http://localhost:11434/v1'
os.environ['OPENAI_MODEL_NAME'] = 'llama2'
os.environ['OPENAI_API_KEY'] = 'sk-xx'
os.environ['SERPER_API_KEY'] = 'fe99a9880f576713b83a4ba2a8a86b0874053a79'

llm = ChatOpenAI(
    model='llama2',
    base_url='http://localhost:11434/v1'
)

search_tool = SerperDevTool()

researcher = Agent(
    role='Senior Researcher',
    goal='Discover in {topic}',
    verbose=True,
    memory=True,
    backstory=(
        'driven by innovation'
    ),
    tools=[search_tool],
    llm=llm,
    allow_delegation=False
)

research_task = Task(
    description=(
        'identify big trend in {topic}'
    ),
    expected_output='this is the summary',
    tools=[search_tool],
    agent=researcher
)

writer = Agent(
    role='Senior Writer',
    goal='narrate in {topic}',
    verbose=True,
    memory=True,
    backstory=(
        'driven by innovation'
    ),
    tools=[search_tool],
    llm=llm,
    allow_delegation=False
)

write_task = Task(
    description=(
        'create topic on {topic}'
    ),
    expected_output='4 para',
    tools=[search_tool],
    agent=writer,
    async_execution=False,
    output_file='a.md'
)

crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    process=Process.sequential
)

result = crew.kickoff()

# Assuming there is a method to set input or parameters before kickoff
crew.set_input({'topic': 'ai'})
result = crew.kickoff()

