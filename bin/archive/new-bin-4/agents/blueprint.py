import sys
from llama_index.core.tools import FunctionTool
from llama_index.core.agent import ReActAgent
from llama_index.llms.ollama import Ollama
from llama_index.core import Settings
from llama_index.core.embeddings import resolve_embed_model

def a():
    return 10

def b(value):
    print(f"Received input value: {value}")
    return 20

toola = FunctionTool.from_defaults(
    fn=a,
    description='Run function "a", which returns a value.'
)

toolb = FunctionTool.from_defaults(
    fn=b,
    description='Run function "b", which expects an input value and returns new and input value.'
)

Settings.llm = Ollama(model="llama3", request_timeout=60.0, temperature=0)
Settings.embed_model = resolve_embed_model("local:BAAI/bge-small-en-v1.5")

agent = ReActAgent.from_tools(
    tools=[toola, toolb],
    llm=Settings.llm,
    verbose=True
)

# prompt = sys.argv[1]
prompt = 'print hello world '
response1 = agent.chat(prompt)

print('response1: ', response1)


# python3 main.py "Use toola to run function a and toolb to run function b with input value '30'."
# response1:  
#  The output of tool "a" is 10, 
#  and the output of tool "b" with input value "30" is 20.

# python3 blueprint.py "Use toola and toolb to return 2 values"
#  response1:  The two values returned are 10 and 20.