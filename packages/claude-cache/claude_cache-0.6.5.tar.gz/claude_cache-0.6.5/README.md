# Claude Cache 🧠

```
                              claude
 ██████╗ █████╗  ██████╗██╗  ██╗███████╗
██╔════╝██╔══██╗██╔════╝██║  ██║██╔════╝
██║     ███████║██║     ███████║█████╗
██║     ██╔══██║██║     ██╔══██║██╔══╝
╚██████╗██║  ██║╚██████╗██║  ██║███████╗
 ╚═════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝
```

[![PyPI version](https://badge.fury.io/py/claude-cache.svg)](https://pypi.org/project/claude-cache/)
[![Python Support](https://img.shields.io/pypi/pyversions/claude-cache)](https://pypi.org/project/claude-cache/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Give your AI coding assistant perfect recall. Claude Cache automatically learns from every successful solution and provides instant access to your accumulated knowledge directly within Claude Code.**

## Why Claude Cache?

Every developer loses hours re-solving problems they've already fixed. Claude Cache acts as your AI's intelligent memory system:

- **🔄 Never Repeat Yourself**: Automatically captures successful solutions and patterns
- **🔍 Find Instantly**: Semantic search understands context and meaning, not just keywords
- **⚡ Zero Context Switching**: Access everything directly in Claude Code via native MCP tools
- **🏗️ Cross-Project Intelligence**: Patterns learned in one project become available everywhere
- **📚 Documentation Memory**: Index and instantly search any documentation you work with

## Real-World Impact

```python
# Monday: Spend 2 hours debugging JWT refresh tokens
# Save the solution when it works

# Friday: Hit the same issue again
/mcp__cache__query "JWT refresh failing"
# → Instantly get your exact solution with full context
```

## Native Claude Code Tools

Type `/` in Claude Code to access these powerful tools:

### `/mcp__cache__query`
Search your entire knowledge base instantly
```
Example: /mcp__cache__query "authentication JWT"
Returns: Your previous JWT implementations with context
```

### `/mcp__cache__learn`
Save successful solutions for future use
```
Example: /mcp__cache__learn
  solution: "Fixed CORS with proxy middleware"
  tags: "cors,api,middleware"
```

### `/mcp__cache__suggest`
Get proactive recommendations based on current context
```
Example: /mcp__cache__suggest "working on API endpoints"
Returns: Relevant patterns from your knowledge base
```

### `/mcp__cache__stats`
Monitor your growing knowledge base
```
Shows: Total patterns, projects, search capabilities
```

### `/mcp__cache__browse`
Index documentation for instant access
```
Example: /mcp__cache__browse "https://docs.example.com"
Result: Documentation indexed and searchable
```

## Quick Setup

### Installation
```bash
# Complete setup with MCP integration (Recommended)
pip install "claude-cache[mcp]"

# Enhanced with semantic search
pip install "claude-cache[enhanced]"

# Basic CLI tools
pip install claude-cache
```

### Claude Code Integration
Add to your `.claude.json`:
```json
{
  "mcpServers": {
    "cache": {
      "type": "stdio",
      "command": "cache-mcp"
    }
  }
}
```

Restart Claude Code and type `/` to see your new tools!

## How It Works

Claude Cache creates an intelligent layer between you and your AI:

1. **🎯 Automatic Learning**: Detects successful patterns through natural language ("that worked!") and execution monitoring
2. **🧠 Smart Retrieval**: Three-tier search system with semantic understanding, TF-IDF fallback, and pattern matching
3. **🔒 Privacy First**: All data stored locally in `~/.claude/knowledge/` - works completely offline

## Perfect For

- **Solo Developers**: Build a personal knowledge base of solutions
- **Development Teams**: Share successful patterns and best practices
- **Learning**: Capture and revisit complex problem-solving approaches
- **Productivity**: Eliminate repetitive problem-solving across projects

## Real-World Examples

### Authentication Debugging
```python
# Monday: Spend 2 hours debugging JWT refresh tokens
# Save the solution automatically when it works

# Friday: Hit the same issue
/mcp__cache__query "JWT refresh failing"
# → Instantly get your exact solution with context
```

### API Pattern Reuse
```python
# Project A: Build a perfect rate limiter
# Claude Cache automatically captures the pattern

# Project B: Need rate limiting
/mcp__cache__suggest "API middleware"
# → Get your rate limiter pattern with implementation details
```

### Team Knowledge Sharing
```python
# Senior dev solves complex database optimization
/mcp__cache__learn "Optimized query with indexes"

# Junior dev hits performance issue
/mcp__cache__query "slow database query"
# → Finds senior dev's solution with explanation
```

## Performance

- **Speed**: <100ms query response for 10K+ patterns
- **Accuracy**: 60-90% relevance in semantic matching
- **Storage**: Efficient SQLite with optional vector embeddings
- **Privacy**: Zero external API calls, completely local

## CLI Usage

For terminal power users:

```bash
# Start monitoring (runs in background)
cache start

# Manual pattern save
cache learn "Solution description" --tags "tag1,tag2"

# Search patterns
cache query "search term"

# Index documentation
cache browse https://docs.example.com

# View statistics
cache stats
```

## Architecture

```
Claude Cache/
├── Knowledge Base (SQLite)
│   ├── Success Patterns
│   ├── Error Resolutions
│   ├── Documentation
│   └── Cross-Project Index
├── Vector Search Engine
│   ├── Semantic Embeddings (optional)
│   └── TF-IDF Fallback
├── MCP Server
│   └── Native Claude Code Tools
└── Auto-Learning System
    ├── Intent Detection
    ├── Execution Monitor
    └── Pattern Extractor
```

## Contributing

We welcome contributions! Areas of interest:
- Additional MCP tools
- Better pattern extraction algorithms
- Support for more development environments
- Team collaboration features

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

Built with love for the developer community. Special thanks to all early adopters and contributors who helped shape Claude Cache into what it is today.

---

**Transform your coding workflow.** Install Claude Cache today and give your AI the perfect memory it deserves.

*Claude Cache is an independent tool for enhancing Claude Code, not an official Anthropic product.*