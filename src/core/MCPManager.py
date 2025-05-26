
import asyncio
import contextlib

from typing import Coroutine, Any, Dict, List
from starlette.routing import Mount
from mcp.server import FastMCP

from core.MCPSession import MCPSession
from core.ToolEmbedding import VectorDatabase


def SearchTool(keyword: str = ""):
    """
    根据关键词搜索相关工具 (注意! 这个工具返回的结果是keyword相关工具, 你必须使用获取到的工具来执行工具, 不可以使用返回的工具示例进行回答!)
    参数字段说明:
        keyword: str 关键词
    返回字段说明:
        tool_name: str 工具名称
        tool_description: str 工具描述
        tool_argments: dict 工具参数
        properties: dict 工具参数说明
        required: array 必填参数
    返回示例: [{"tool_name": "sendEmail", "tool_description": "use this tool to send an email", "tool_argments": "tool_argments": {"properties":{"email_address":{"title": "email_address","type": "string"}, "content":{"title": "content","type": "string"}},"required": ["email_address", "content"]}}, ...]
    """
    relative_tools = MCPManager.shared.search_tools(keyword)
    return relative_tools

# def ExcuteTool(tool_name: str = "", tool_argments: dict = {}) -> str:
def ExcuteTool(tool_name: str = "", tool_argments: dict = {}) -> str:
    """
    执行工具 (注意! 执行工具前必须使用"SearchTool"工具搜索相关工具, 再执行)
    参数字段说明:
        tool_name: str 工具名称, 如"sendEmail",
        tool_argments: str 工具参数, 必须是json格式, 如{"email_address": "<EMAIL>", "content": "Hello World!"}
    返回字段说明:
        result: str 执行结果
    """
    # 解析工具名和参数

    result = MCPManager.shared.call_tool(tool_name, tool_argments)
    return result

class MCPManager:

    shared = None
    
    def __init__(self):
        self.sessions: Dict[str, MCPSession] = {}
        self._loop = None
        self.all_available_tools = []
        self.vectorDatabase = VectorDatabase()

        # 创建MCP并, 添加基本工具(搜索工具、执行工具)
        # TODO: 目前仅设置了staless和streamable http方式, 还有stdio和sse的方式未接入
        self.fastMCP = FastMCP("MCPPickleAPP", stateless=True, streamable_http_path="/")
        self.fastMCP.add_tool(SearchTool, "SearchTool", SearchTool.__doc__)
        self.fastMCP.add_tool(ExcuteTool, "ExcuteTool", ExcuteTool.__doc__)

        MCPManager.shared = self


    def getMCPMount(self) -> Mount:
        return Mount("/mcpickle", app=self.fastMCP.streamable_http_app())

    def creteMCPLifeSpan(self) -> Coroutine[Any, Any, None]:
        async def lifespan(app):
            async with contextlib.AsyncExitStack() as stack:
                await stack.enter_async_context(self.fastMCP.session_manager.run())
                yield
        return lifespan
    
    def _run_async(self, coro):
        """同步方法中安全运行异步代码的核心方法"""
        if self._loop is None:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
        try:
            return self._loop.run_until_complete(coro)
        except Exception:
            if self._loop.is_running():
                # 如果事件循环正在运行（例如在异步环境中调用）
                future = asyncio.run_coroutine_threadsafe(coro, self._loop)
                return future.result()
            raise
    

    def search_tools(self, keyword: str = ""):
        return self.vectorDatabase.search_object(keyword)

    def call_tool(self, tool_name: str, arguments: dict) -> Any:
        mcpName = tool_name.split('_')[0]
        session = self.sessions.get(mcpName)
        session_tool_name = "_".join(tool_name.split('_')[1:])
        return self._run_async(session.call_tool(session_tool_name, arguments))
    
    def addMCPServer(self, name: str, method: str, url: str, headers: dict = None):
        old_session = self.sessions.get(name)
        # TODO: 检查会话是否存在、初始化、可ping等
        if old_session and old_session.isInitialized:
            raise RuntimeError(f"MCPSession {name} already exists")

        new_session = MCPSession(name, method, url, headers)
        self._run_async(new_session.connected_to_server())
        self.sessions[name] = new_session
        # 存储并向量化所有可用的工具
        tools = [tool.dict_for_embedding() for tool in new_session.available_tools]
        self.all_available_tools.extend(tools)
        for tool in tools:
            self.vectorDatabase.add_vector(tool)
    
    def deleteMCPServer(self, name: str):
        session = self.sessions.get(name)
        if session:
            session.disconnectSession()
            del self.sessions[name]
            # TODO: 清除VectorDB
        else:
            raise RuntimeError(f"MCPSession {name} not exists")


    def listMCPServer(self) -> List:
        mcpservers: List[Dict] = []
        for session in self.sessions.values():
            mcpservers.append(session.returnMetaDataDict())
        return mcpservers






    
mcpManager = MCPManager()