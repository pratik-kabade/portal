import sys
from llm_settings import LLM

# llm_instance = LLM(llm_model='llama3', debug_mode=True)

if len(sys.argv) > 1:
    q = sys.argv[1]
    # print(f"Received argument: {q}")
else:
    # print("No argument provided")
    q='list all the paths mentioned here'




llm_instance = LLM(llm_model='llama3')
print(llm_instance.rag_model(
    # 'AUSF UE Authentication.pdf', 
    'asuf.txt', 
    # 'this document is about api, i need you to create testcases on how to test those api and do this for each of the api'
    # 'list all the api paths mentioned here'
    q
    ))


# https://jdegre.github.io/editor/?url=https://raw.githubusercontent.com/jdegre/5GC_APIs/master/TS29509_Nausf_UEAuthentication.yaml
# python3 test.py 'give me all the list of the get put post delete routes mentioned here and also give me steps to test that route do that for all the routes'