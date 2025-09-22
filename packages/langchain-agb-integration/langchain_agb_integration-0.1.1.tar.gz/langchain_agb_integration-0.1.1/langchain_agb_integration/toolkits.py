"""AgbIntegration toolkits."""

from typing import List

from langchain_core.tools import BaseTool, BaseToolkit
from .tools import WriteFileTool, ExecuteCommandTool, ReadFileTool, RunCodeTool


class AgbIntegrationToolkit(BaseToolkit):
    """AgbIntegration toolkit.

    Setup:
        Install ``agb`` package and set environment variable ``AGB_API_KEY``.

        .. code-block:: bash

            pip install agb
            export AGB_API_KEY="your-api-key"

    Key init args:
        session: object
            AGB session object

    Instantiate:
        .. code-block:: python

            from agb import AGB
            from langchain_agb_integration import AgbIntegrationToolkit

            agb = AGB()
            result = agb.create()
            session = result.session

            toolkit = AgbIntegrationToolkit(
                session=session
            )

    Tools:
        .. code-block:: python

            toolkit.get_tools()

        .. code-block:: none

            # Returns list with WriteFileTool, ReadFileTool, RunCodeTool and ExecuteCommandTool

    Use within an agent:
        .. code-block:: python

            from langgraph.prebuilt import create_react_agent

            agent_executor = create_react_agent(llm, toolkit.get_tools())

            example_query = "Write a file '/tmp/hello.txt' with content 'Hello World'"

            events = agent_executor.stream(
                {"messages": [("user", example_query)]},
                stream_mode="values",
            )
            for event in events:
                event["messages"][-1].pretty_print()

        .. code-block:: none

             # Agent will use the tools to write files and execute commands

    """  # noqa: E501

    session: object
    """AGB session object"""

    def get_tools(self) -> List[BaseTool]:
        """Get the tools in the toolkit."""
        return [
            WriteFileTool(session=self.session),
            ReadFileTool(session=self.session),
            RunCodeTool(session=self.session),
            ExecuteCommandTool(session=self.session),
        ]