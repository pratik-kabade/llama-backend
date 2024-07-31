from llama_index.core.tools import FunctionTool 
from llama_index.core.agent import ReActAgent 
from llama_index.llms.ollama import Ollama 
from llama_index.core import Settings 
import nest_asyncio 

from tool import initialize_tool

nest_asyncio.apply()

persist_dir1 = "./data/vectordb1"
filepath1 = './data/file_1.pdf'
tool_name1 = "Ram"
tool_description1 = "A RAG engine that tells about Ram"

tool1 = initialize_tool(persist_dir1, filepath1, tool_name1, tool_description1)

persist_dir2 = "./data/vectordb2"
filepath2 = './data/file_2.pdf'
tool_name2 = "Shyam"
tool_description2 = "A RAG engine that tells about Shyam"

tool2 = initialize_tool(persist_dir2, filepath2, tool_name2, tool_description2)



llm = Ollama(model="llama2", request_timeout=120.0, temperature=0)
Settings.llm = llm

agent = ReActAgent.from_tools([tool1, tool2], verbose=True)
response = agent.chat("Who is Ram and Shyam? Use tool1 for Ram and tool2 for Shyam")
print("Agent Response:", response)
