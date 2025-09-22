"""AgbIntegration tools."""

from typing import Optional, Type

from langchain_core.callbacks import (
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

import os


class WriteFileInput(BaseModel):
    """Input schema for writing file to AGB session."""

    path: str = Field(..., description="Path where to write the file")
    content: str = Field(..., description="Content to write to the file")
    mode: str = Field(default="overwrite", description="Write mode ('overwrite' or 'append')")


class WriteFileTool(BaseTool):  # type: ignore[override]
    """Tool for writing files in AGB session.

    Setup:
        Install ``agb`` package and set environment variable ``AGB_API_KEY``.

        .. code-block:: bash

            pip install agb
            export AGB_API_KEY="your-api-key"

    Instantiation:
        .. code-block:: python

            from agb import AGB
            from langchain_agb_integration.tools import WriteFileTool
            
            agb = AGB()
            result = agb.create()
            session = result.session

            tool = WriteFileTool(
                session=session
            )

    Invocation with args:
        .. code-block:: python

            tool.invoke({"path": "/tmp/test.txt", "content": "Hello World"})

        .. code-block:: python

            # Output: "File written successfully to /tmp/test.txt"

    """  # noqa: E501

    name: str = "write_file"
    """The name that is passed to the model when performing tool calling."""
    description: str = "Write content to a file in the AGB session"
    """The description that is passed to the model when performing tool calling."""
    args_schema: Type[BaseModel] = WriteFileInput
    """The schema that is passed to the model when performing tool calling."""

    session: object
    """AGB session object"""

    def _run(
        self, 
        path: str, 
        content: str, 
        mode: str = "overwrite",
        *, 
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Write content to a file in the AGB session."""
        try:
            result = self.session.file_system.write_file(path, content, mode)
            if result.success:
                return f"File written successfully to {path} with mode '{mode}'"
            else:
                return f"Failed to write file: {result.error_message}"
        except Exception as e:
            return f"Error occurred while writing file: {str(e)}"


class ReadFileInput(BaseModel):
    """Input schema for reading file from AGB session."""

    path: str = Field(..., description="Path of the file to read")


class ReadFileTool(BaseTool):  # type: ignore[override]
    """Tool for reading files in AGB session.

    Setup:
        Install ``agb`` package and set environment variable ``AGB_API_KEY``.

        .. code-block:: bash

            pip install agb
            export AGB_API_KEY="your-api-key"

    Instantiation:
        .. code-block:: python

            from agb import AGB
            from langchain_agb_integration.tools import ReadFileTool
            
            agb = AGB()
            result = agb.create()
            session = result.session

            tool = ReadFileTool(
                session=session
            )

    Invocation with args:
        .. code-block:: python

            tool.invoke({"path": "/tmp/test.txt"})

        .. code-block:: python

            # Output: "File content:\\n<file_content>"

    """  # noqa: E501

    name: str = "read_file"
    """The name that is passed to the model when performing tool calling."""
    description: str = "Read content from a file in the AGB session"
    """The description that is passed to the model when performing tool calling."""
    args_schema: Type[BaseModel] = ReadFileInput
    """The schema that is passed to the model when performing tool calling."""

    session: object
    """AGB session object"""

    def _run(
        self, 
        path: str, 
        *, 
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Read content from a file in the AGB session."""
        try:
            result = self.session.file_system.read_file(path)
            if result.success:
                return f"File content:\n{result.content}"
            else:
                return f"Failed to read file: {result.error_message}"
        except Exception as e:
            return f"Error occurred while reading file: {str(e)}"


class RunCodeInput(BaseModel):
    """Input schema for running code in AGB session."""

    code: str = Field(..., description="The code to execute")
    language: str = Field(..., description="The programming language of the code. Supported languages are: 'python', 'javascript'")
    timeout_s: int = Field(default=300, description="The timeout for the code execution in seconds")


class RunCodeTool(BaseTool):  # type: ignore[override]
    """Tool for running code in AGB session.

    Setup:
        Install ``agb`` package and set environment variable ``AGB_API_KEY``.

        .. code-block:: bash

            pip install agb
            export AGB_API_KEY="your-api-key"

    Instantiation:
        .. code-block:: python

            from agb import AGB
            from langchain_agb_integration.tools import RunCodeTool
            
            agb = AGB()
            result = agb.create()
            session = result.session

            tool = RunCodeTool(
                session=session
            )

    Invocation with args:
        .. code-block:: python

            tool.invoke({"code": "print('Hello World')", "language": "python"})

        .. code-block:: python

            # Output: "Code execution result:\\n<code_output>"

    """  # noqa: E501

    name: str = "run_code"
    """The name that is passed to the model when performing tool calling."""
    description: str = "Execute code in the AGB session. Supported languages are: python, javascript"
    """The description that is passed to the model when performing tool calling."""
    args_schema: Type[BaseModel] = RunCodeInput
    """The schema that is passed to the model when performing tool calling."""

    session: object
    """AGB session object"""

    def _run(
        self, 
        code: str, 
        language: str,
        timeout_s: int = 300,
        *, 
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Execute code in the AGB session."""
        try:
            result = self.session.code.run_code(code, language, timeout_s)
            if result.success:
                return f"Code execution result:\n{result.result}"
            else:
                return f"Code execution failed with error: {result.error_message}"
        except Exception as e:
            return f"Error occurred while executing code: {str(e)}"


class ExecuteCommandInput(BaseModel):
    """Input schema for executing command in AGB session."""

    command: str = Field(..., description="Shell command to execute")
    timeout_ms: int = Field(default=1000, description="Timeout for command execution in milliseconds")


class ExecuteCommandTool(BaseTool):  # type: ignore[override]
    """Tool for executing shell commands in AGB session.

    Setup:
        Install ``agb`` package and set environment variable ``AGB_API_KEY``.

        .. code-block:: bash

            pip install agb
            export AGB_API_KEY="your-api-key"

    Instantiation:
        .. code-block:: python

            from agb import AGB
            from langchain_agb_integration.tools import ExecuteCommandTool
            
            agb = AGB()
            result = agb.create()
            session = result.session

            tool = ExecuteCommandTool(
                session=session
            )

    Invocation with args:
        .. code-block:: python

            tool.invoke({"command": "ls -la", "timeout_ms": 1000})

        .. code-block:: python

            # Output: "Command output:\n<command_output>"

    """  # noqa: E501

    name: str = "execute_command"
    """The name that is passed to the model when performing tool calling."""
    description: str = "Execute a shell command in the AGB session"
    """The description that is passed to the model when performing tool calling."""
    args_schema: Type[BaseModel] = ExecuteCommandInput
    """The schema that is passed to the model when performing tool calling."""

    session: object
    """AGB session object"""

    def _run(
        self, 
        command: str, 
        timeout_ms: int = 1000,
        *, 
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Execute a shell command in the AGB session."""
        try:
            result = self.session.command.execute_command(command, timeout_ms)
            if result.success:
                return f"Command output:\n{result.output}"
            else:
                return f"Command failed with error: {result.error_message}"
        except Exception as e:
            return f"Error occurred while executing command: {str(e)}"