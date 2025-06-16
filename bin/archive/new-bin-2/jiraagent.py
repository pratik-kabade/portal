import os
from llama_index.core import Settings, StorageContext, load_index_from_storage
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import ReActAgent
from llama_index.llms.ollama import Ollama
from llama_index.core.embeddings import resolve_embed_model
from project.util.jirautil import jirautils 

# Setting up LLM and embedding model
os.environ["LLAMA_CLOUD_API_KEY"] = "your_llama_cloud_api_key"
Settings.embed_model = resolve_embed_model("local:BAAI/bge-small-en-v1.5")
Settings.llm = Ollama(model="llama3", request_timeout=60.0, temperature=0)

# Define QueryEngineTool instances for JIRA operations
create_issue_tool = QueryEngineTool(
    query_engine=None, 
    metadata=ToolMetadata(
        name="CreateJiraIssue",
        description="Creates a new JIRA issue with a summary, description, and issue type.",
    ),
    handler=lambda input: jirautils.createNewissue(
        input.get('summary', ''),
        input.get('description', ''),
        input.get('issuetype', 'Task')
    )
)

get_issue_status_tool = QueryEngineTool(
    query_engine=None,
    metadata=ToolMetadata(
        name="GetJiraIssueStatus",
        description="Retrieves the status of a JIRA issue given its issue key.",
    ),
    handler=lambda input: jirautils.get_issue_status(input.get('issue_key', ''))
)

# Additional tools can be defined similarly...

# Create a list of tools
jira_tools = [
    create_issue_tool,
    get_issue_status_tool,
    # Add more tools as needed for other JIRA operations
]

# Initialize the agent with the defined tools
agent = ReActAgent.from_tools(
    jira_tools,
    verbose=True,
)

# # Example usage of the agent
# response = agent.chat("Create a new JIRA issue with summary 'Test Issue' and description 'This is a test issue.'")
# print(str(response))

response = agent.chat("What is the status of the JIRA issue with key 'RDKB-123'?")
print(str(response))
