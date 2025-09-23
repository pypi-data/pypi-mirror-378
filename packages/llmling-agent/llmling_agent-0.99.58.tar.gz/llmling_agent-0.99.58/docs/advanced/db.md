# Agent Logging & Memory Management

LLMling-agent provides flexible storage and memory management for agent interactions through SQLModel with SQLite.

## Storage System

### What Gets Logged

- **Conversations**: Basic metadata like agent name, start time
- **Messages**: Complete message history including:
  - Content
  - Role (user/assistant/system)
  - Model used
  - Token usage and costs
  - Timestamp
  - Message forwarding chains
- **Commands**: Command history with session context
- **Tool Usage**: Tool calls with arguments and results

### Storage Location

The SQLite database is stored using platformdirs:
```python
# Default location:
# Linux: ~/.local/share/llmling/history.db
# Windows: %LOCALAPPDATA%\llmling\history.db
# macOS: ~/Library/Application Support/llmling/history.db
```

## Memory Configuration

Agents can be configured with sophisticated memory management:

```yaml
agents:
  assistant:
    model: openai:gpt-5-mini
    session:
      enable: true              # Enable/disable memory tracking
      max_tokens: 4000         # Rolling window token limit
      max_messages: 100        # Rolling window message limit
      provider: "sql"          # Optional storage provider override
      session:                 # Initial session loading
        name: my_session       # Optional session identifier
        since: 1h             # Only messages from last hour
        roles:                # Only specific message types
          - user
          - assistant
        contains: "analysis"  # Filter by content
        include_forwarded: true
```

Or via code:
```python
from llmling_agent_config.session import MemoryConfig, SessionQuery

# Configure memory management
memory_cfg = MemoryConfig(
    enable=True,
    max_tokens=4000,          # Rolling window of max 4000 tokens
    max_messages=100,         # Keep last 100 messages
    session=SessionQuery(     # Initial session loading
        name="my_session",
        since="1h",
        roles={"user", "assistant"}
    )
)

# Use in agent creation
agent = Agent(..., session=memory_cfg)
```

### Memory Management Features

- **Rolling Window**: Maintain a limited context window by:
  - Token count (`max_tokens`)
  - Message count (`max_messages`)
- **Initial Loading**: Load specific parts of previous conversations
- **Provider Selection**: Choose storage backend per agent
- **Selective History**: Filter what gets stored and loaded

## Session Recovery

Sessions can be recovered in multiple ways:

### Simple Recovery
```yaml
agents:
  assistant:
    session: "my_session_name"  # Simple session identifier
```

### Query-Based Recovery
```yaml
agents:
  assistant:
    session:
      name: my_session_name    # Optional session identifier
      agents:                  # Filter by specific agents
        - assistant
        - analyst
      since: 1h               # Only messages from last hour
      contains: "analysis"    # Filter by content
      roles:                  # Only specific message types
        - user
        - assistant
      include_forwarded: true # Include forwarded messages
```

### Programmatic Recovery
```python
# Store session ID for later
session = agent.conversation.id

# Simple recovery by ID
async with Agent(..., session=session) as agent:
    # Conversation history is automatically loaded
    ...

# Advanced query-based recovery
query = SessionQuery(
    name="my_session",
    since="1h",
    roles={"user", "assistant"},
    contains="analysis"
)
async with Agent(..., session=query) as agent:
    # Filtered conversation history is loaded
    ...
```

## Storage Providers

Multiple storage providers are available:

```yaml
storage:
  providers:
    - type: sql               # SQLite database (default)
      url: sqlite:///history.db
      pool_size: 5
      auto_migration: true

    - type: text_file        # Text log file
      path: "chat.log"
      format: chronological
      encoding: utf-8

    - type: file            # Structured file storage
      path: "history.json"
      format: json

    - type: memory         # In-memory storage (testing)

  # Global settings
  default_provider: sql    # Provider for history queries
  log_messages: true      # Whether to log messages
  log_conversations: true # Whether to log conversations
  log_tool_calls: true   # Whether to log tool calls
  log_commands: true     # Whether to log commands
  log_context: true      # Whether to log context additions
```

Storage can be configured globally and overridden per agent through the memory configuration.
