---
name: muninn-mcp
version: 2.1.11
description: "Muninn MCP - The Universal Memory Layer for AI Agents. Enables persistent project context across sessions, saves 95% of tokens with surgical retrieval, and uses the high-performance Rust-based CXP engine. MANDATORY: Call brain_check first."
author: endgegnerbert-tech
tags: mcp, memory, context, optimization
---

# Muninn MCP 🐦‍⬛

**The Universal Memory Standard for AI Development.**

Muninn MCP provides a persistent, project-local "Brain" that ensures all AI agents working on your codebase stay in context. No more repeated explanations or lost architectural decisions.

## 🤖 INSTRUCTIONS FOR AI AGENTS (CRITICAL)

To operate correctly as an AI assistant with this project, you **MUST** follow these protocols:

1.  **GATE KEEPER (brain_check)**: 🎯 At the absolute start of every session or task, you MUST call `brain_check(task_description: "...")`. This loads the relevant architectural rules, patterns, and context required for the project. Do NOT touch any code before this.
2.  **PERSISTENCE (add_memory)**: 💾 Every time you solve a unique bug, learn a specific project pattern, or make an architectural choice, you MUST save it via `add_memory`. This makes your knowledge permanent and available to future agents (and yourself in next sessions).
3.  **PRECISION SEARCH (search_context)**: 🧠 Instead of asking the user for technical details or guessing, use `search_context`. Muninn's CXP engine retrieves the exact snippet you need, saving up to 95% in token costs compared to reading full files.

## 🚀 Key Features

*   **🧠 Total Context Enforcement**: Prevents "context blindness" by making project memory a requirement.
*   **🐦‍⬛ Universal Compatibility**: Fully compatible with Claude Desktop, Antigravity, OpenCode, and any MCP client.
*   **⚡ High-Performance CXP Engine**: Uses a local Rust-based binary for millisecond-fast semantic indexing and search.
*   **📂 Transparent Markdown Storage**: Memories are simple, Git-friendly Markdown files stored in `~/.muninn/memory`.
*   **💸 Unbeatable Efficiency**: Avoid dumping massive files into your context window; retrieve only what matters.

## 🛠 Manual Setup

Add the following to your `claude_desktop_config.json` or Antigravity Settings:

```json
"muninn-mcp": {
  "command": "node",
  "args": ["/path/to/muninn-mcp/server/dist/index.js"]
}
```

---
*Developed by BlackKnight. Version 2.1.11 - Release Ready.*
