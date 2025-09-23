import asyncio
import base64
import json
import logging
import shutil
import traceback
from typing import Any
import uuid


from codemie_tools.data_management.file_system.container.container import Container
from codemie_tools.data_management.file_system.container.jupyter import (
    RuntimeOutput,
    RuntimeOutputTraceback,
)
from codemie_tools.data_management.file_system.container.runtime import ContainerRuntime


logger = logging.getLogger(__name__)


class CodeExecutorV2:
    """
    The CodeExecutor class abstracts communication with code interpreters and runtimes.
    It currently supports executing Python code, with potential to expand for other languages in the future.
    """

    file_repository: Any = None

    def __init__(self, file_repository: Any):
        """
        Initializes the CodeExecutor instance.
        """
        self.file_repository = file_repository
        self.container = Container()

    def execute_python(self, code: str, user_id: str):
        return self._execute_code(code=code, user_id=user_id, language="python")

    def _execute_code(self, code: str, user_id: str, language):
        """
        Executes code in the specified language.

        Parameters:
        - code (str): The code snippet to be executed.
        - language (str): The programming language of the code.

        Returns:
        The result of the code execution if the language is supported.

        Raises:
        - UnsupportedLanguageException: If the specified language is not supported.
        """
        if language.lower() == "python":
            return asyncio.run(self._run_in_sandbox(code, user_id))
        else:
            raise ValueError(f"{language} language is not supported. Only Python is supported.")

    async def _run_in_sandbox(self, code: str, user_id: str):
        try:
            result = await self.container.run(code, user_id)
            if not result:
                return ""
        except RuntimeError:
            raise
        except asyncio.TimeoutError:
            raise RuntimeError(
                RuntimeOutput(
                    type="error", content="Code execution main loop reach a timeout"
                ).model_dump_json()
            )
        except Exception as e:
            raise RuntimeError(
                RuntimeOutputTraceback(
                    type="error",
                    content=f"Code execution main loop got unexpected error: {str(e)}",
                    traceback="".join(traceback.format_exc()),
                ).model_dump_json(),
            )

        finally:
            if rootfs := self.container.rootfs:
                try:
                    ContainerRuntime().destroy_rootfs(rootfs)
                    shutil.rmtree(rootfs)
                except Exception:
                    pass

        output = json.loads(result.decode())
        if output.get("type") == "image/png":
            if self.file_repository:
                stored_file = self.file_repository.write_file(
                    name=f"{uuid.uuid4()}.png",
                    mime_type=output["type"],
                    content=base64.b64decode(output["content"]),
                    owner=user_id,
                )
                return f"This 'sandbox:/v1/files/{stored_file.to_encoded_url()}' is image URL. You MUST not transform it. Return as it is"
            else:
                return f"This 'sandbox:/v1/files/{output.content}' is image URL. You MUST not transform it. Return as it is"

        return result.decode()
