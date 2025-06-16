import sys
from llama_index.core.tools import FunctionTool
from llama_index.core.agent import ReActAgent
from llama_index.llms.ollama import Ollama
from llama_index.core import Settings
from llama_index.core.embeddings import resolve_embed_model
from project.util.jirautil import createNewissue, get_userstories, get_projects

# Define Jira functions
def create_jira_issue(summary: str, description: str, issuetype: str):
    """Create a new issue in Jira with a given summary, description, and issue type."""
    return createNewissue(summary, description, issuetype)

def fetch_userstories(projectkey: str):
    """Fetch all user stories for a specific Jira project key."""
    return get_userstories(projectkey)

def fetch_projects():
    """Fetch all projects available in Jira."""
    projects = get_projects()
    return projects

def save_file(text):
    """Save content to a text file."""
    print('Saving file...')
    text = str(text)
    with open('filename.txt', 'w') as file:
        file.write(text)
    return "File saved successfully."

# Wrap functions with FunctionTool
create_issue_tool = FunctionTool.from_defaults(
    fn=create_jira_issue,
    description="Create a new issue in Jira. Expects a summary, description, and issue type."
)

fetch_userstories_tool = FunctionTool.from_defaults(
    fn=fetch_userstories,
    description="Fetch all user stories for a specific Jira project. Expects a project key."
)

fetch_projects_tool = FunctionTool.from_defaults(
    fn=fetch_projects,
    description="Fetch all projects from Jira and return their names as a formatted string."
)

save_content_tool = FunctionTool.from_defaults(
    fn=save_file,
    description="Save text content to a file. Expects string input text content."
)

# Configure LLM settings
Settings.llm = Ollama(model="llama3", request_timeout=60.0, temperature=0)
Settings.embed_model = resolve_embed_model("local:BAAI/bge-small-en-v1.5")

# Create the agent with all tools
agent = ReActAgent.from_tools(
    tools=[create_issue_tool, fetch_userstories_tool, fetch_projects_tool, save_content_tool],  
    llm=Settings.llm,
    verbose=True  # Keep verbose to see the decision-making process
)

# Take input from command line
prompt = "First, use the tool to fetch all projects from Jira. After fetching, use the tool to save the projects to a text file."
response1 = agent.chat(prompt)

print('response1: ', response1)
