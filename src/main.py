from dotenv import load_dotenv
load_dotenv()

import os
import uvicorn

from starlette.applications import Starlette
from starlette.routing import  Route

from controller.health import health

from core.MCPService import MCPService

def main():
    # 启动主应用API
    application = Starlette(
        debug=True,
        routes=[
            Route("/health", health),

            Route("/mcp/addserver", MCPService.addserver, methods=["POST"]),
            Route("/mcp/listserver", MCPService.listserver, methods=["POST"]),
            Route("/mcp/deleteserver", MCPService.deleteserver, methods=["POST"]),
            MCPService.getMCPMount()
        ],
        lifespan=MCPService.getMCPLifeSpan()
    )
    uvicorn.run(application, host=os.getenv("MCPICKLE_HOST"), port=int(os.getenv("MCPICKLE_PORT")))


if __name__ == '__main__':
    main()