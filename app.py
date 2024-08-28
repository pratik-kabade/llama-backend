from llama_index.llms.ollama import Ollama
llm = Ollama(model="llama2", request_timeout=60.0, temperature=0)

description='Client has found that some of the rural areas are missing zip codes and this causes an issue trying to use autopop when entering a listing.'

prompt = f'Identify issue according to this {description}, and on its basis provide rules for resolution and also generate sql query to perform this action'

response = llm.stream_complete(prompt)
for r in response:
    print(r.delta, end="")
