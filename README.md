# 🥒 MCPickle
A Plug-and-Play RAG Orchestrator for Model Context Protocol Tools

MCPickle is a lightweight, open-source platform that helps Large Language Models (LLMs) dynamically retrieve, select, and invoke MCP (Model Context Protocol) tools — all through an intelligent RAG (Retrieval-Augmented Generation) pipeline.

With too many tools to manage and too little time to wire them together, MCPickle acts as your RAG-based router and tool sommelier: just describe your intent, and it’ll fetch the right MCP server for the job.

### ⚡ Features
- 🧠 Intent-to-Tool retrieval via vector search + LLM planning
- 🧩 Support for modular MCP tool descriptors (YAML/JSON)
- 🔌 Plug-and-play interface: bring your own tools or auto-discover them
- 🗂️ Built-in metadata registry for scalable tool orchestration
- 🧪 Developer-friendly: test calls, log flows, and monitor usage
- 🌱 Ready to grow: works out of the box, designed for extension

Whether you’re building agentic pipelines, AI copilots, or autonomous toolchains — MCPickle gives your LLM the context muscle it needs.


## 📚 Getting Started

### How to run
1. Clone this repo, and run ``pip install -r requirements.txt``
2. Set up your Embedding model and rerank model's url and api key in ``.env``
3. Run ``python main.py`` to start the server
4. Add your other MCP server by requsting ``/mcp/addserver`` 
```shell
curl -X POST http://127.0.0.1:8001/mcp/addserver --data '{"name": "NewMCPServer", "method": "streamablehttp", "url": "http://127.0.0.1:8000/mcp"}'
# Now we only support SSE and StreamableHTTP, but we will support more in the future
```
5. Add this server to your LLM App such as Cherry Studio、claude...
6. Have fun

### Other Things
We will support more features in the future, such as:
- [ ] Add Stdio method support for MCP server and MCPickle
- [ ] An web dashboard for MCPickle that you could manage your MCP server and MCP tool easily
- [ ] ......

Stay tuned for more updates!
