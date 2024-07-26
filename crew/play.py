from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
import os

from langchain_openai import OpenAI

# Set environment variables
os.environ['OPENAI_API_BASE'] = 'http://localhost:11434/v1'
os.environ['OPENAI_MODEL_NAME'] = 'llama2'
os.environ['OPENAI_API_KEY'] = 'sk-xx'
os.environ['SERPER_API_KEY'] = 'TODO'

# Initialize the language model
llm = OpenAI(
    model_name='llama2',
    api_base='http://localhost:11434/v1',
    api_key=os.environ['OPENAI_API_KEY']
)

# Initialize the search tool
searchtool = SerperDevTool()

# Define the first agent
writer = Agent(
    name='WriterAgent',
    tools=[searchtool],
    llm=llm
)

# Define the second agent
reviewer = Agent(
    name='ReviewerAgent',
    tools=[searchtool],
    llm=llm
)

# Define the first task for writing
write_task = Task(
    description='create topic on {topic}',
    expected_output='4 para',
    tools=[searchtool],
    agent=writer,
    async_execution=False,
    output_file='a.md'
)

# Define the second task for reviewing
review_task = Task(
    description='review the content in {input_file}',
    expected_output='2 para review',
    tools=[searchtool],
    agent=reviewer,
    async_execution=False,
    input_file='a.md',
    output_file='review.md'
)

# Initialize the crew with agents and tasks
crew = Crew(
    agents=[writer, reviewer],
    tasks=[write_task, review_task],
    process=Process.sequential
)

# Kick off the tasks and print the result
result = crew.kickoff(input={'topic': 'ai'})
print(result)
