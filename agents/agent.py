from llama_index.core.tools import FunctionTool 
from llama_index.core.agent import ReActAgent 
from llama_index.llms.ollama import Ollama 
from llama_index.core import Settings 
import nest_asyncio 

from tool_1 import tool1
from tool_2 import tool2

nest_asyncio.apply()

llm = Ollama(model="llama2", request_timeout=120.0, temperature=0)
Settings.llm = llm

agent = ReActAgent.from_tools([tool1, tool2], verbose=True)
response = agent.chat("Who is Ram and Shyam? Use tool1 for Ram and tool2 for Shyam")
print("Agent Response:", response)
