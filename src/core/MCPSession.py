from contextlib import AsyncExitStack
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp.client.sse import sse_client

class MCPToolModel():
    def __init__(self, mcpName: str, name: str, description: str, inputSchema: dict):
        self.mcpName = mcpName
        self.name = name
        self.description = description
        self.inputSchema = inputSchema


    def dict_for_available_tool(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.inputSchema,
                "strict": False
            }
        }

    def dict_for_embedding(self) -> dict:
        return {
            "tool_name": self.mcpName + "_" + self.name,
            "tool_description": self.description,
            "tool_argments": self.inputSchema,
        }
    
    @staticmethod
    def from_dict(tool_dict: dict):
        return MCPToolModel(
            name=tool_dict["tool_name"],
            description=tool_dict["tool_description"],
            inputSchema=tool_dict["tool_argments"]["properties"],
            outputSchema=tool_dict["tool_argments"]["required"]
        )


class MCPSession():
    def __init__(self, name: str, method: str, url: str, headers: dict):
        self.sessionName = name
        self.method = method
        self.mcpServerUrl = url
        self.headers = headers

        self.exit_stack = AsyncExitStack()
        self.mcpClientSession: ClientSession = None
        # Tools(support), Resources, Prompts....
        self.isInitialized = False
        self.available_tools = []


    def returnMetaDataDict(self) -> dict:
        return {
            "name": self.sessionName,
            "method": self.method,
            "url": self.mcpServerUrl,
            "available_tools": [tool.dict_for_available_tool() for tool in self.available_tools],
        }


    async def connected_to_server(self, auto_update_tools: bool = True):
        if self.method == "sse":
            transport = await self.exit_stack.enter_async_context(sse_client(self.mcpServerUrl, headers=self.headers))
            self.stdio, self.write = transport
        elif self.method == "streamablehttp":
            transport = await self.exit_stack.enter_async_context(streamablehttp_client(self.mcpServerUrl, headers=self.headers))
            self.stdio, self.write, _ = transport
        else:
            raise ValueError("MCP Connected Method not support, only Support 'sse' and 'streamablehttp")

        session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        await session.initialize()
        self.mcpClientSession = session

        # After initialize
        # timestamp = int(time.time() * 1000)
        # unique_str = f"{timestamp}_{self.sessionName}".encode('utf-8')
        # session_id_hash = hashlib.sha256(unique_str).hexdigest()[:16]
        # self.sessionId = session_id_hash
        # self.initTime = timestamp
        # self.newestUseTime = timestamp
        self.isInitialized = True

        # List Tools
        if auto_update_tools:
            await self.update_available_tools()
    
    async def update_available_tools(self):
        if not self.isInitialized:
            raise RuntimeError("MCP Session not initialized")
        response = await self.mcpClientSession.list_tools()
        tools = response.tools
        # print("Connected to server with tools: \n", "\n".join([f"{tool.name}" for tool in tools]))
        self.available_tools = [MCPToolModel(self.sessionName, tool.name, tool.description, tool.inputSchema) for tool in tools]

    async def call_tool(self, tool_name: str, arguments: dict) -> dict:
        # Extract the real tool name by removing the prefix
        if not self.isInitialized:
            raise RuntimeError("MCP Session not initialized")
        # TODO: Check the tool exist and arguments is valid
        tool_from_available_tools = [tool for tool in self.available_tools if tool.name == tool_name]
        if len(tool_from_available_tools) == 0:
            raise ValueError(f"Tool {tool_name} not found")
        result = await self.mcpClientSession.call_tool(tool_name, arguments)
        return result
        
        
    def disconnectSession(self):
        self.isInitialized = False
        self.exit_stack.aclose()