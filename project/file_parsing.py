import os
import argparse
import time
import json
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, load_index_from_storage, StorageContext
from llama_index.core.embeddings import resolve_embed_model
from llama_index.llms.ollama import Ollama
import logging
import sys
from llama_parse import LlamaParse

os.environ["LLAMA_CLOUD_API_KEY"] = "llx-TuxnaMbo4c7TYeo9EjxpZX4oPMxEDAsX4a8AuxogvurFbklO"

BASE_DIR = 'data/'
file_path = f"{BASE_DIR}Alarms.csv"
persist_dir = f"{BASE_DIR}vectordb/"

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

Settings.embed_model = resolve_embed_model("local:BAAI/bge-small-en-v1.5")

Settings.llm = Ollama(model="llama2", request_timeout=60.0, temperature=0)

documents = LlamaParse(result_type="text").load_data(file_path)

if not os.path.exists(os.path.join(persist_dir, "default__vector_store.json")):
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=persist_dir)
else:
    storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
    index = load_index_from_storage(storage_context=storage_context)

query_engine = index.as_query_engine()
response = query_engine.query("what is the firstoccurence of NANP?")
print(response)
