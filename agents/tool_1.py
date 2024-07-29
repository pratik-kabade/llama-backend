from llama_index.core.embeddings import resolve_embed_model
from llama_index.llms.ollama import Ollama
from llama_index.core import VectorStoreIndex, Settings, load_index_from_storage, StorageContext
import os
from llama_index.core.tools import QueryEngineTool
from llama_parse import LlamaParse
import nest_asyncio

nest_asyncio.apply()

os.environ["LLAMA_CLOUD_API_KEY"] = "llx-TuxnaMbo4c7TYeo9EjxpZX4oPMxEDAsX4a8AuxogvurFbklO"

Settings.llm = Ollama(model="llama2", request_timeout=60.0)
Settings.embed_model = resolve_embed_model("local:BAAI/bge-small-en-v1.5")
persist_dir = "./agents/vectordb1"  # Use a different directory for tool1

if not os.path.exists(os.path.join(persist_dir, "default__vector_store.json")):
    print("Creating new index")
    filepath = './agents/file_1.txt'
    documents = LlamaParse(result_type="text").load_data(filepath)
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=persist_dir)
else:
    print("Loading existing index")
    storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
    index = load_index_from_storage(storage_context=storage_context)

query_engine = index.as_query_engine()

tool1 = QueryEngineTool.from_defaults(query_engine, 
    name="Ram",
    description="A RAG engine that tells about Ram",
)
print("Tool1 Initialized:", tool1)
