# Muninn MCP
**Universal Context Protocol for AI Agents**

[![Status](https://img.shields.io/badge/status-stable-success)](https://github.com/blackknight/muninn-mcp)
![Version](https://img.shields.io/badge/version-2.1.10-green)
[![Powered By: CXP](https://img.shields.io/badge/Powered%20By-CXP-blue)](https://github.com/blackknight/cxp)

**Muninn MCP** (Old Norse: *Memory*) is the universal memory layer for your AI stack. It serves as a persistent, project-local "Brain" that ensures your AI agents never lose context.

Inspired by Odin's raven, it gathers project knowledge and architectural decisions, making them available to any agent you use—whether it's Claude Desktop, Antigravity, or OpenCode.

---

## 🚀 Why Muninn MCP?

> "The hardest part of AI development isn't writing code—it's maintaining context."

*   **Brain-First Enforcement**: Agents are instructed to check the "Brain" before every task.
*   **Massive Token Savings**: Instead of dumping your entire codebase, Muninn surgically injects the top-N relevant context pieces, saving up to 95% on tokens.
*   **Universal Persistence**: Memories stay with your project in the `.muninn/` folder and `~/.muninn/memory`.
*   **Transparent & Human-Readable**: All memories are stored as standard Markdown files. You own your context.

---

## 🛠 Setup

### 1. Requirements
*   **Node.js**: v18 or higher.
*   **CXP Engine**: Included in the `bin/` directory for fast indexing.

### 2. Installation
```bash
git clone https://github.com/blackknight/muninn-mcp.git
cd muninn-mcp/server
npm install
npm run build
```

### 3. Agent Configuration
Add the server to your MCP client configuration:

**Claude Desktop (`claude_desktop_config.json`)**
```json
{
  "mcpServers": {
    "muninn": {
      "command": "node",
      "args": ["/path/to/muninn-mcp/server/dist/index.js"]
    }
  }
}
```

---

## 🧠 How It Works

1.  **Index**: Run `reindex_context(project_path="...")` to index your project.
2.  **Verify**: The agent calls `brain_check` at the start of a task.
3.  **Retrieve**: Relevant snippets are injected into the prompt.
4.  **Learn**: The agent calls `add_memory` to save new decisions or patterns.

---

## 🏗 Features

*   **🐦‍⬛ Universal Memory**: One brain for ALL your tools.
*   **📂 Transparent Storage**: Edit memories manually in `~/.muninn/memory`.
*   **⚡ Rust-Powered Search**: Millisecond-fast semantic search via the CXP protocol.
*   **🔌 Plug & Play**: Works with any MCP-compliant agent.

---

## 📜 License

Copyright (c) 2026 **BlackKnight**.

All rights reserved. This project is currently in private beta.

---
*Built with passion by BlackKnight.*
