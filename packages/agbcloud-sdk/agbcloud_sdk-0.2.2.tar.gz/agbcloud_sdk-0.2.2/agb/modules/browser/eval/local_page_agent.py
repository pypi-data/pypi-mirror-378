import asyncio
import logging
import os
import concurrent.futures
from typing import Optional,Dict,Any
from playwright.async_api import async_playwright
from mcp import ClientSession, StdioServerParameters, stdio_client
import json
from pydantic import BaseModel
from agb.modules.browser.browser import Browser, BrowserOption
from agb.session import Session
from agb.api.base_service import OperationResult
from agb.modules.browser.browser_agent import BrowserAgent

logger = logging.getLogger(__name__)

class LocalMCPClient:
    def __init__(self, server: str, command: str, args: list[str])-> None:
        self.server = server
        self.command = command
        self.args = args
        self.session: ClientSession | None = None
        self.worker_thread: concurrent.futures.Future | None = None
        self._tool_call_queue: asyncio.Queue | None = None
        self._loop: asyncio.AbstractEventLoop | None = None

    def connect(self) -> None:
        if (self.worker_thread is None):
            promise: concurrent.futures.Future[bool] = concurrent.futures.Future()
            def thread_target() -> None:
                async def _connect_and_list_tools() -> None:
                    success = False
                    logger.info("Start connect to mcp server")
                    try:
                        print(f"command = {self.command}, args = {self.args}")
                        server_params = StdioServerParameters(command=self.command, args=self.args)
                        async with stdio_client(server_params) as (read_stream, write_stream):
                            async with ClientSession(read_stream, write_stream) as session:
                                # Setup queue and event loop reference
                                self._tool_call_queue = asyncio.Queue()
                                self._loop = asyncio.get_running_loop()

                                self.session = session
                                logger.info("Initialize MCP client session")
                                await self.session.initialize()
                                logger.info("Client initialized. Listing available tools...")
                                tools = await self.session.list_tools()
                                logger.info(f"Tools: {tools}")
                                success = True
                                promise.set_result(success)
                                await self._interactive_loop()
                    except Exception as e:
                        logger.error(f"Failed to connect to MCP server: {e}")
                        success = False
                        promise.set_result(success)
                asyncio.run(_connect_and_list_tools())
            self.worker_thread = concurrent.futures.ThreadPoolExecutor().submit(thread_target)
            promise.result()

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]):
        if not self.session or not self._tool_call_queue or not self._loop:
            raise RuntimeError("MCP client is not connected. Call connect() and ensure it returns True before calling callTool.")
        # Use a Future to get the result back from the interactive loop
        future: concurrent.futures.Future[OperationResult] = concurrent.futures.Future()
        await self._tool_call_queue.put((tool_name, arguments, future))
        return future.result()

    async def _interactive_loop(self) -> None:
        """Run interactive loop."""
        while True:
            if self._tool_call_queue is not None:
                try:
                    tool_name, arguments, future = await asyncio.wait_for(self._tool_call_queue.get(), timeout=1.0)
                    try:
                        logger.info(f"Call tool {tool_name} with arguments {arguments}")
                        if self.session is not None:
                            response = await self.session.call_tool(tool_name, arguments)
                            print("MCP tool response:", response)
                            is_successful = not response.isError

                            mcp_response = OperationResult(
                                request_id="local_request_dummy_id",
                                success=is_successful,
                            )

                            # Extract text content from response
                            text_content = ""
                            if hasattr(response, 'content') and response.content:
                                for content_item in response.content:
                                    if hasattr(content_item, 'text') and content_item.text:
                                        print(f"MCP tool text response: {content_item.text}")
                                        text_content = content_item.text
                                        break
                                if is_successful:
                                    mcp_response.data = text_content
                                    print(f"MCP tool text response (data): {text_content}")
                                else:
                                    mcp_response.error_message = text_content
                                    print(f"MCP tool text response (error): {text_content}")

                                future.set_result(mcp_response)
                        else:
                            future.set_exception(RuntimeError("MCP client session is not initialized."))
                    except Exception as e:
                        future.set_exception(e)
                except asyncio.TimeoutError:
                    pass
            else:
                await asyncio.sleep(1)

class LocalPageAgent(BrowserAgent):
    def __init__(self, session, browser):
        super().__init__(session, browser)

        mcp_script = os.environ.get("PAGE_TASK_MCP_SERVER_SCRIPT", "")

        self.mcp_client: LocalMCPClient | None = LocalMCPClient(
            server="PageUseAgent",
            command="python",
            args=[mcp_script]
        )

    def initialize(self) -> None:
        if self.mcp_client:
            self.mcp_client.connect()

    def _call_mcp_tool(self, name: str, args: Dict[str, Any], read_timeout: Optional[int] = None, connect_timeout: Optional[int] = None) -> OperationResult:
        if not self.mcp_client:
            raise RuntimeError("mcp_client is not set on LocalBrowserAgent.")
        try:
            mcp_client = self.mcp_client  # local reference to avoid race conditions
            def thread_func() -> OperationResult:
                response = asyncio.run(mcp_client.call_tool(name, args))
                #logger.info("LocalBrowserAgent call_mcp_tool got response ", response)
                return response
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(thread_func)
                return future.result()
        except Exception as e:
            raise RuntimeError(f"Failed to call MCP tool '{name}': {e}")

class LocalBrowser(Browser):
    def __init__(self, session=None):
        # Optionally skip calling super().__init__ if not needed for tests
        self.contexts = []
        self._cdp_port = 9222
        self.agent: LocalPageAgent = LocalPageAgent(session, self)
        self._worker_thread = None

    async def initialize_async(self, options: BrowserOption) -> bool:
        if (self._worker_thread is None):
            promise: concurrent.futures.Future[bool] = concurrent.futures.Future()
            def thread_target() -> None:
                async def _launch_local_browser() -> None:
                    success = False
                    logger.info("Start launching local browser")
                    try:
                        async with async_playwright() as p:
                            # Define CDP port
                            # Recreate /tmp/chrome_cdp_ports.json with the required content
                            chrome_cdp_ports_path = "/tmp/chrome_cdp_ports.json"
                            with open(chrome_cdp_ports_path, "w") as f:
                                json.dump({"chrome": str(self._cdp_port), "router": str(self._cdp_port)}, f)

                            # Launch headless browser and create a page for all tests
                            self._browser = await p.chromium.launch_persistent_context(
                                headless=False,
                                viewport={"width": 1280, "height": 1200},
                                args=[
                                    f'--remote-debugging-port={self._cdp_port}',
                                ],
                                user_data_dir="/tmp/browser_user_data")

                            logger.info("Local browser launched successfully:")
                            success = True
                            promise.set_result(success)
                            await self._playwright_interactive_loop()
                    except Exception as e:
                        logger.error(f"Failed to connect to browser: {e}")
                        success = False
                        promise.set_result(success)
                asyncio.run(_launch_local_browser())
            self._worker_thread = concurrent.futures.ThreadPoolExecutor().submit(thread_target)
            promise.result()

        self.agent.initialize()
        return True

    def is_initialized(self) -> bool:
        return True

    def get_endpoint_url(self) -> str:
        return f"http://localhost:{self._cdp_port}"

    async def _playwright_interactive_loop(self) -> None:
        """Run interactive loop."""
        while True:
            #print("Local browser interactive loop")
            await asyncio.sleep(3)

class LocalSession(Session):
    def __init__(self):
        super().__init__(None, "local_session")
        self.browser = LocalBrowser(self)

    def delete(self, sync_context: bool = False) -> None:
        pass