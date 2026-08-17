import asyncio
import json
import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from fastmcp import Client

load_dotenv()

# -------------------------------------
# OpenAI
# -------------------------------------

openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# -------------------------------------
# MCP Client
# -------------------------------------

mcp_client = Client("github_mcp_server.py")


# -------------------------------------
# MCP Helper Functions
# -------------------------------------

async def get_tools():

    async with mcp_client:

        tools = await mcp_client.list_tools()

        return tools
    



async def call_tool(tool_name, arguments):

    async with mcp_client:

        result = await mcp_client.call_tool(
            tool_name,
            arguments
        )

        return result


# -------------------------------------
# Streamlit UI
# -------------------------------------

st.set_page_config(
    page_title="GitPilot",
    page_icon="🐙",
    layout="wide"
)

st.title("🐙 GitPilot")
st.caption("GitHub Assistant powered by MCP")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Render history

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Prompt

prompt = st.chat_input(
    "Ask anything about your GitHub..."
)

if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        placeholder = st.empty()

        try:

            tools = asyncio.run(get_tools())

            for tool in tools:
                print("TOOL:", tool)
                print("DICT:", vars(tool))

            openai_tools = []

            for tool in tools:

                openai_tools.append(
                    {
                        "type": "function",
                        "name": tool.name,
                        "description": tool.description or "",
                        "parameters": (
                            tool.inputSchema
                            if hasattr(tool, "inputSchema")
                            else {
                                "type": "object",
                                "properties": {}
                            }
                        )
                    }
                )

            response = openai_client.responses.create(
                model="gpt-4.1-mini",
                instructions="""
            You are a GitHub assistant.

            The user has already authenticated with GitHub.

            Never ask for GitHub credentials.

            When a tool can answer the question,
            ALWAYS call the appropriate tool.

            Use:
            - list_repositories
            - my_profile
            - latest_commits

            before answering.
            """,
                input=prompt,
                tools=openai_tools
            )

            print("\n========== OPENAI RESPONSE ==========")

            for item in response.output:
                 print(item)

            print("=====================================\n")

            tool_call = None

            for item in response.output:

                if item.type == "function_call":

                    tool_call = item
                    break

            if tool_call:

                args = json.loads(
                    tool_call.arguments
                )

                tool_result = asyncio.run(
                    call_tool(
                        tool_call.name,
                        args
                    )
                )
                print("\n========== AVAILABLE TOOLS ==========")

                for tool in tools:
                    print(tool.name)

                print("=====================================\n")

                final_response = (
                    openai_client.responses.create(
                        model="gpt-4.1-mini",
                        previous_response_id=response.id,
                        input=[
                            {
                                "type":
                                "function_call_output",
                                "call_id":
                                tool_call.call_id,
                                "output":
                                json.dumps(
                                    tool_result,
                                    default=str
                                )
                            }
                        ]
                    )
                )

                answer = (
                    final_response.output_text
                )

            else:

                answer = response.output_text

            placeholder.markdown(answer)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer
                }
            )

        except Exception as ex:

            st.error(str(ex))