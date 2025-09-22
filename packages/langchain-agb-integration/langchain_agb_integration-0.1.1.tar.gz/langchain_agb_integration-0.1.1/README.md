# langchain-agb-integration

This package contains the LangChain integration with AGB platform, providing tools for file operations, code execution, and command execution within a secure cloud environment.

## Installation

```bash
pip install -U langchain-agb-integration
```

You also need to install the `agb` package to interact with the AGB platform:

```bash
pip install -U agb
```

## Configuration

To use the AGB integration, you need to configure your AGB API key as an environment variable:

```bash
export AGB_API_KEY="your-api-key"
```

You can obtain your API key from the AGB platform dashboard.

## Tools

The integration provides several tools that allow you to interact with the AGB platform:

### WriteFileTool
Write content to a file in the AGB session with either overwrite or append mode.

### ReadFileTool
Read content from a file in the AGB session.

### RunCodeTool
Execute Python or JavaScript code in a secure cloud environment with configurable timeout.

### ExecuteCommandTool
Execute shell commands in the AGB session with timeout control.

## Toolkit

The `AgbIntegrationToolkit` provides all the tools in a single package that can be easily added to LangChain agents:

```python
from agb import AGB
from langchain_agb_integration import AgbIntegrationToolkit

# Create AGB session
agb = AGB()
result = agb.create()
session = result.session

# Create toolkit
toolkit = AgbIntegrationToolkit(session=session)
tools = toolkit.get_tools()

# Use with LangChain agents
from langchain.agents import AgentExecutor, create_tool_calling_agent

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
```

## Individual Tool Usage

You can also use tools individually:

```python
from agb import AGB
from langchain_agb_integration.tools import WriteFileTool, ReadFileTool, RunCodeTool, ExecuteCommandTool

# Create AGB session
agb = AGB()
result = agb.create()
session = result.session

# Create individual tools
write_tool = WriteFileTool(session=session)
read_tool = ReadFileTool(session=session)
code_tool = RunCodeTool(session=session)
command_tool = ExecuteCommandTool(session=session)

# Use tools
write_tool.invoke({"path": "/tmp/test.txt", "content": "Hello World", "mode": "overwrite"})
read_tool.invoke({"path": "/tmp/test.txt"})
code_tool.invoke({"code": "print('Hello from Python!')", "language": "python"})
command_tool.invoke({"command": "ls -la", "timeout_ms": 1000})
```