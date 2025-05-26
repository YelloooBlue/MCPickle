from starlette.responses import PlainTextResponse, JSONResponse
from core.MCPManager import MCPManager

class MCPService:
    
    @staticmethod
    def getMCPMount():
        # return mcpManager.getMCPMount()
        return MCPManager.shared.getMCPMount()

    @staticmethod
    def getMCPLifeSpan():
        # return mcpManager.creteMCPLifeSpan()
        return MCPManager.shared.creteMCPLifeSpan()

    @staticmethod
    async def addserver(request):
        # Parse the request body to get server details
        try:
            body = await request.json()
            server_name = body.get("name")
            server_method = body.get("method")
            server_url = body.get("url")
            if not all([server_name, server_method, server_url]):
                return JSONResponse(content={"code": 400, "message": "Missing required fields", "data": {}}, status_code=400)
        except Exception as e:
            return JSONResponse(content={"code": 400, "message": f"Invalid request body: {str(e)}", "data": {}}, status_code=400)
        MCPManager.shared.addMCPServer(server_name, server_method, server_url)
        return JSONResponse(content={"code": 200, "message": "Succesfully Added Server", "data": {}})
        
    @staticmethod
    def listserver(request):
        return JSONResponse(content={"code": 200, "message": "ok", "data": MCPManager.shared.listMCPServer()})
        
    @staticmethod
    async def deleteserver(request):
        try:
            body = await request.json()
            server_name = body.get("name")
            if not all([server_name]):
                return JSONResponse(content={"code": 400, "message": "Missing required fields", "data": {}}, status_code=400)
        except Exception as e:
            return JSONResponse(content={"code": 400, "message": f"Invalid request body: {str(e)}", "data": {}}, status_code=400)
        MCPManager.shared.deleteMCPServer(server_name)
        return JSONResponse(content={"code": 200, "message": "Successfully Deleted Server", "data": {}})
        