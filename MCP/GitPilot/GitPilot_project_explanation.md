# GitPilot Project Explanation

## Overview

This project is a small GitHub assistant built with MCP (Model Control Protocol), OpenAI, and Streamlit.

It contains:
- `app.py` — the Streamlit web app that accepts user prompts and calls OpenAI and MCP tools.
- `github_mcp_server.py` — the MCP server that defines GitHub-related tools.
- `mcp_client.py` — a tiny helper that creates an MCP client.
- `requirenments.txt` — the list of needed Python packages.

## Files and Explanation

### `app.py`

This file runs the web interface and uses OpenAI plus MCP tools to answer user questions.

1. `import asyncio`
   - Imports Python’s asynchronous I/O library.
   - This helps the app call the MCP server without blocking.

2. `import json`
   - Imports JSON support.
   - Used for converting tool arguments and results between JSON and Python.

3. `import os`
   - Imports operating system utilities.
   - Used to read environment variables like API keys.

4. `import streamlit as st`
   - Imports Streamlit for building the web UI.

5. `from dotenv import load_dotenv`
   - Imports a helper to load `.env` environment variables.

6. `from openai import OpenAI`
   - Imports the OpenAI client library.

7. `from fastmcp import Client`
   - Imports the MCP client to connect with the tool server.

8. `load_dotenv()`
   - Loads values from a `.env` file into the environment.

9. `openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))`
   - Creates the OpenAI client using the API key from the environment.

10. `mcp_client = Client("github_mcp_server.py")`
    - Creates an MCP client connected to the local `github_mcp_server.py` tool server.

11. `async def get_tools():`
    - Defines a function to list the available tools from the MCP server.

12. `async with mcp_client:`
    - Opens the MCP client connection and ensures cleanup.

13. `tools = await mcp_client.list_tools()`
    - Fetches the available MCP tools.

14. `async def call_tool(tool_name, arguments):`
    - Defines a function to call a specific tool by name and arguments.

15. `st.set_page_config(...)`
    - Configures the Streamlit page title, icon, and layout.

16. `st.title("🐙 GitPilot")`
    - Sets the app title.

17. `st.caption("GitHub Assistant powered by MCP")`
    - Shows a small caption.

18. `if "messages" not in st.session_state:`
    - Initializes chat history storage if it does not exist.

19. `for message in st.session_state.messages:`
    - Displays previous chat messages.

20. `prompt = st.chat_input("Ask anything about your GitHub...")`
    - Adds a user input box.

21. `if prompt:`
    - Runs when the user submits a question.

22. `st.session_state.messages.append(...)`
    - Saves the user question.

23. `tools = asyncio.run(get_tools())`
    - Fetches tool definitions from the MCP server.

24. `openai_tools.append(...)`
    - Converts each MCP tool into the format OpenAI expects.

25. `response = openai_client.responses.create(...)`
    - Sends the user question and tool definitions to the OpenAI Responses API.

26. `tool_call = None`
    - Prepares to detect if OpenAI wants to call a tool.

27. `if item.type == "function_call":`
    - Checks whether the model returned a tool call.

28. `tool_result = asyncio.run(call_tool(tool_call.name, args))`
    - Executes the requested MCP tool.

29. `final_response = openai_client.responses.create(...)`
    - Sends the tool result back to OpenAI for the final answer.

30. `placeholder.markdown(answer)`
    - Displays the assistant answer in the UI.

31. `st.error(str(ex))`
    - If anything fails, shows the error.

### `github_mcp_server.py`

This file defines the actual GitHub helper tools that the app can call.

1. `from fastmcp import FastMCP`
   - Imports the server-side MCP helper.

2. `from github import Github, Auth`
   - Imports the GitHub API client from `PyGithub`.

3. `from dotenv import load_dotenv`
   - Loads environment variables from `.env`.

4. `import os`
   - Reads environment variables like the GitHub token.

5. `load_dotenv()`
   - Loads the `.env` file.

6. `mcp = FastMCP("github")`
   - Creates the MCP server with the name `github`.

7. `auth = Auth.Token(os.getenv("GITHUB_TOKEN"))`
   - Creates GitHub authentication using `GITHUB_TOKEN` from `.env`.

8. `github = Github(auth=auth)`
   - Builds the GitHub client.

9. `@mcp.tool`
   - Marks a function as an MCP tool.

10. `def list_repositories():`
    - Defines a tool that returns the user’s GitHub repositories.

11. `repos = github.get_user().get_repos()`
    - Gets the authenticated user’s repositories.

12. `return [{...} for repo in repos]`
    - Returns a list with repository name, privacy, and URL.

13. `def my_profile():`
    - Defines a tool that returns the GitHub profile data.

14. `user = github.get_user()`
    - Gets the authenticated GitHub user.

15. `return {...}`
    - Returns login, name, followers, following, public repos, and profile URL.

16. `def latest_commits(repo_name: str):`
    - Defines a tool that fetches the latest commits for a repo.

17. `repo = github.get_user().get_repo(repo_name)`
    - Retrieves the repository object by name.

18. `commits = repo.get_commits()`
    - Fetches commit history.

19. `return [{...} for c in commits[:10]]`
    - Returns the first 10 commits with SHA and message.

20. `if __name__ == "__main__":`
    - Runs the MCP server if the file is executed directly.

21. `mcp.run()`
    - Starts the MCP tool server.

### `mcp_client.py`

1. `from fastmcp import Client`
   - Imports the MCP client class.

2. `client = Client("github_mcp_server.py")`
   - Builds a client for the local MCP server.

This file does not run by itself; it only creates the client object.

### `requirenments.txt`

This file lists the Python packages required to run the project:
- `streamlit`
- `fastmcp`
- `openai`
- `python-dotenv`
- `PyGithub`

## Important Notes

- The project expects a `.env` file with:
  - `OPENAI_API_KEY`
  - `GITHUB_TOKEN`

- `app.py` uses the OpenAI Responses API and the MCP tool definitions to answer user questions.

- `github_mcp_server.py` is the part that actually talks to GitHub and provides tools.

## Suggested Filename

I created this file as `GitPilot_project_explanation.md`.

## How to Use

1. Install the packages from `requirenments.txt`.
2. Add `.env` with your OpenAI and GitHub credentials.
3. Run the MCP server with `python github_mcp_server.py`.
4. Run the Streamlit app with `streamlit run app.py`.

If you want, I can also add a shorter `README.md` with simple run commands.