from llama_index.core.embeddings import resolve_embed_model
from llama_index.llms.ollama import Ollama
from llama_index.core import VectorStoreIndex, Settings, load_index_from_storage, StorageContext
import os
from llama_index.core.tools import QueryEngineTool
from llama_parse import LlamaParse
import nest_asyncio

nest_asyncio.apply()

os.environ["LLAMA_CLOUD_API_KEY"] = 'llx-TuxnaMbo4c7TYeo9EjxpZX4oPMxEDAsX4a8AuxogvurFbklO'

def initialize_tool(persist_dir, filepath, tool_name, tool_description):
    Settings.llm = Ollama(model='llama2', request_timeout=60.0)
    Settings.embed_model = resolve_embed_model('local:BAAI/bge-small-en-v1.5')

    if not os.path.exists(os.path.join(persist_dir, "default__vector_store.json")):
        print("Creating new index")
        documents = LlamaParse(result_type="text").load_data(filepath)
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(persist_dir=persist_dir)
    else:
        print("Loading existing index")
        storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
        index = load_index_from_storage(storage_context=storage_context)

    query_engine = index.as_query_engine()

    tool = QueryEngineTool.from_defaults(query_engine, 
        name=tool_name,
        description=tool_description,
    )
    print("Tool Initialized:", tool)
    return tool

# # Example usage:
# persist_dir = "./agents/data/vectordb2"
# filepath = './agents/data/file_2.pdf'
# tool_name = "Shyam"
# tool_description = "A RAG engine that tells about Shyam"

# tool = initialize_tool(persist_dir, filepath, tool_name, tool_description)
