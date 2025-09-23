# Inheritance

LLMling supports inheritance both for individual agents and entire YAML files, making configurations more reusable and maintainable.

## Agent Inheritance

Agents can inherit configuration from other agents using the `inherits` field:

```yaml
agents:
  # Base agent configuration
  base_assistant:
    model: openai:gpt-4
    system_prompts:
      - "You are a helpful assistant."
    capabilities:
      can_load_resources: true
      can_list_resources: true

  # Specialized agent inheriting base config
  code_assistant:
    inherits: base_assistant  # Inherit from base
    description: "Specializes in code review"
    system_prompts:  # Extends base prompts
      - "Focus on code quality and best practices."
    capabilities:  # Extends base capabilities
      can_execute_code: true

  # Another specialized agent
  docs_assistant:
    inherits: base_assistant
    description: "Specializes in documentation"
    system_prompts:
      - "Focus on clear documentation."
```

Child agents:
- Inherit all fields from parent
- Can override any inherited field
- Can add new fields
- System prompts are combined

## YAML File Inheritance

Using Yamling's inheritance system, entire YAML files can inherit from other files:

```yaml
# base.yml - Base configuration
agents:
  base_agent:
    model: openai:gpt-4
    capabilities:
      can_load_resources: true

storage:
  providers:
    - type: sql
      url: sqlite:///history.db
```

```yaml
# specialized.yml - Specialized configuration
INHERIT: base.yml  # Inherit entire base configuration

agents:
  specialized_agent:
    inherits: base_agent
    description: "Specialized version"
```

### Remote File Inheritance

Yamling supports UPath, allowing inheritance from remote files:

```yaml
# Inherit from remote sources
INHERIT:
  - base.yml
  - https://example.com/base_config.yml
  - s3://my-bucket/configs/agents.yml
  - git+https://github.com/org/repo/config.yml
```


## Inheritance Resolution

### Agent Inheritance
1. Start with parent configuration
2. Recursively resolve parent inheritances
3. Apply child configuration:
   - Override simple fields
   - Merge lists (e.g., system_prompts)
   - Update dictionaries (e.g., capabilities)

### YAML File Inheritance
1. Load all inherited files in order
2. Merge configurations:
   - Later files override earlier ones
   - Lists and dictionaries are merged
   - Complex fields use smart merging


Inheritance in LLMling helps maintain DRY (Don't Repeat Yourself) configurations while allowing for flexible specialization at both the agent and file level.
