# Node Connection System

## Overview
LLMling provides a clean, object-oriented approach to message routing through a simple but powerful concept:
Every entity that can process messages is a message node and can be connected to other nodes.
This creates a flexible and composable system for building complex message flows.

## Core Components

### Message Nodes

Any entity that:

- Can receive and process messages (run())
- Has message_sent / message_received signals
- Can be connected to other nodes

Types of nodes:

- Agents (LLM-based , Human-in-the-loop, or Callables)
- Teams (Parallel execution groups)
- TeamRuns (Sequential execution chains)

#### Talk
The fundamental connection unit representing a one-to-many relationship between agents:

```python
class Talk:
    def __init__(
        self,
        source: MessageEmitter[Any, Any],
        targets: list[MessageNode[Any, Any]],
        connection_type: ConnectionType = "run",
        priority: int = 0,
        delay: timedelta | None = None,
        transform: AnyTransformFn | None = None,
        filter_condition: AnyFilterFn | None = None,
        stop_condition: AnyFilterFn | None = None,
        exit_condition: AnyFilterFn | None = None,
    )
```

#### Connection Types
Three different ways messages can be handled:

- `run`: Execute message as a new run in target agent
- `context`: Add message as context to target's conversation
- `forward`: Forward message directly without processing

#### Connection Management

Connections are managed by the `ConnectionManager`, which provides:

- Connection creation and cleanup
- Message routing
- Wait state management
- Statistics tracking

## YAML Configuration

Connections can be defined in agent configuration:

```yaml
agents:
  analyzer:
    # ... other config ...
    connections:
      - type: node
        name: planner
        filter_condition:
          type: word_match
          words: ["analyze", "examine"]
        stop_condition:
          type: message_count
          max_messages: 5
        transform: myapp.transforms.process_message
```

## Connection Patterns

### Agent-to-Agent
Simple connection between two agents:
```python
# Direct connection
connection = agent_a.connect_to(agent_b)
```

### Agent-to-Team
Connect an agent to multiple targets:
```python
# Create team
team = agent_b & agent_c & agent_d

# Connect agent to team
connection = agent_a.connect_to(team)
```

### Team-to-Team
Connect groups of agents:
```python
team_a = agent_1 & agent_2
team_b = agent_3 & agent_4
connection = team_a.connect_to(team_b)
```

### Complex Structures
Nodes can be combined in any way:
```python
# Create teams for parallel execution
team_1 = analyzer & planner  # Team of two agents
team_2 = validator & reporter  # Another team

# Create sequential chain
chain = processor_1 | processor_2  # Sequential processing

# Combine in any way
nested_team = Team([team_1, chain, team_2])  # Team containing teams and chains!
complex_chain = team_1 | processor | team_2  # Teams in a chain

# Connect complex structures
connection = nested_team >> final_processor
```

## Message Flow Control

### Statistics and Monitoring

Each connection tracks:

- Message count
- Token usage
- Byte count
- Timing information

### Control Mechanisms

1. **Message Filtering**:
   ```python
   # Using lambda
   # Rich context object with access to message, stats, other connections etc
   talk.when(lambda ctx: "important" in ctx.message.content)

   # Using YAML
   filter_condition:
     type: word_match
     words: ["important"]
   ```

2. **Connection Control**:
   - `stop_condition`: Disconnect this connection
   - `exit_condition`: Exit the entire process (raises SystemExit)
   - `transform`: Modify messages as they flow

3. **Flow Control**:
   - Priority-based handling
   - Delayed execution
   - Message queuing

```python
# Set up connection with control
talk = agent.connect_to(
    target,
    priority=1,
    delay=timedelta(seconds=5),
    stop_condition=lambda ctx: ctx.message.content == "STOP",
    exit_condition=lambda ctx: ctx.message.content == "EXIT"
)
```


### Team Management

TeamTalk provides aggregate operations for multiple connections:

- Collective statistics
- Group operations (pause/resume)
- Recursive target resolution

## Unique Features

1. **Object-Oriented Design**

- Each connection is a first-class object
- Strong typing and clear interfaces
- Easy to extend and customize

2. **Flexible Routing**

- Multiple connection types
- Configurable message handling
- Support for complex topologies

3. **Rich Monitoring**

- Detailed statistics
- Connection state tracking
- Performance metrics

4. **Type Safety**

- Generic type parameters for dependencies and results
- Type-safe message passing
- Proper typing for team operations

5. **Clean API**

- Operator overloading for intuitive syntax (`agent >> other_agent`)
- Chainable configuration
- Consistent interface across patterns

6. **Configuration Options**

- Programmatic setup
- YAML configuration
- Runtime modification

## Example Usage

```python
# Create agents
analyzer = Agent(name="analyzer")
planner = Agent(name="planner")
executor = Agent(name="executor")

# Create team
planning_team = planner & executor

# Set up connection with control
talk = analyzer.connect_to(
    planning_team,
    connection_type="run",
    transform=lambda ctx: preprocess_message(ctx.message),
    stop_condition=lambda ctx: ctx.message.metadata.get("complete", False),
    exit_condition=lambda ctx: ctx.message.metadata.get("error", False)
)

talk.when(lambda ctx: ctx.message.metadata.get("priority") == "high")

# Monitor
print(f"Processed {talk.stats.message_count} messages")
```
