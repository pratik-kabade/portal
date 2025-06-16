from LLM import LLM

llm_model = 'llama3.1:8b'
llm_instance = LLM(llm_model=llm_model)

q='Users should be able to create and manage work orders'

ans=llm_instance.rag_model('data.csv', f'give me test steps and test cases for {q}?')
print(ans)
