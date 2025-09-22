# Scrimba Teaching MCP System

<!-- mcp-name: io.github.Skills03/scrimba-teaching -->

A revolutionary teaching system implementing Per Borgen's Scrimba methodology, available as MCP servers for both Claude Desktop and Claude CLI.

## 🚀 v1.1.0 - Agent-Router Update!

**NEW!** `scrimba_agent` - Unified tool that embeds agent personalities and auto-routes requests!
- Analyzes user intent automatically
- Routes to visual, interactive, project, or challenge modes
- No need for separate agents - everything in one tool!

## Architecture

```
┌─────────────────────┐     ┌────────────────────┐
│  Teaching MCP       │     │  CLI Wrapper MCP   │
│  (Pure Logic)       │     │  (Agent Support)   │
├─────────────────────┤     ├────────────────────┤
│ • scrimba_agent()   │     │ • execute_with_    │
│   (NEW! v1.1.0)     │     │   agent()          │
│ • teach()           │     │ • list_agents()    │
│ • give_challenge()  │     │                    │
│ • check_code()      │     │                    │
│ • visualize()       │     │                    │
│ • start_project()   │     │                    │
└─────────────────────┘     └────────────────────┘
         ↑                           ↑
         │                           │
    Claude Desktop              Claude CLI
    (Direct MCP)              (With Agent Support)
```

## Features

### Core Scrimba Methodology
- **60-Second Rule**: Users coding within 60 seconds
- **Micro-Lessons**: [HOOK: 20s] → [CONCEPT: 60s] → [CHALLENGE: 120s] → [CELEBRATE: 10s]
- **5-Level Progression**: Every concept taught in 5 progressive steps
- **Console.log Driven Development**: Verify everything immediately
- **Error-First Learning**: Celebrate mistakes as learning moments
- **Real Projects**: Passenger Counter, Blackjack Game, Chrome Extension

### Teaching Tools
- `teach(topic, step)` - Interactive lessons with Scrimba methodology
- `give_challenge(difficulty)` - Immediate coding challenges
- `check_code(code)` - Validation with encouragement
- `next_lesson()` - Progress through 5-level curriculum
- `start_project(name)` - Build real applications
- `visualize_concept(concept)` - Generate visual learning materials
- `show_progress()` - Track learning journey

## Installation

### For Claude Desktop

1. **Install the MCP server:**
```bash
cd scrimba-mcp-unified
pip install -e .
```

2. **Configure Claude Desktop:**
Add to your Claude Desktop configuration:
```json
{
  "mcpServers": {
    "scrimba-teaching": {
      "command": "python",
      "args": ["/path/to/teaching-server/teaching_mcp.py"]
    }
  }
}
```

3. **Start using in Claude Desktop:**
```
teach me variables
give me a challenge
check my code: let age = 25
```

### For Claude CLI

1. **Install both servers:**
```bash
cd scrimba-mcp-unified
pip install -e .
```

2. **Register MCP servers:**
The `.mcp.json` file is already configured. Claude CLI will automatically detect both servers.

3. **Option A - Direct MCP Usage:**
```bash
# Use MCP tools directly
claude "teach me variables"
claude "give me a coding challenge"
```

4. **Option B - With Agent Orchestration:**
```bash
# Create teaching agents
claude "create teaching orchestrator agent"

# Use agents for orchestration
claude @teaching-orchestrator "teach me variables"
```

## Usage Examples

### Direct Teaching (Claude Desktop & CLI)
```
User: teach me variables
Bot: [Full Scrimba micro-lesson with story, concept, and challenge]

User: let myAge = 25
Bot: [Celebration and next challenge]

User: next lesson
Bot: [Level 2 of 5-level progression]
```

### Project-Based Learning
```
User: start project passenger_counter
Bot: [Per's subway story + starter code + 5 build steps]

User: show my progress
Bot: [Visual progress bar + achievements + motivation]
```

### Visual Learning
```
User: visualize variables
Bot: [Detailed image prompt for educational visualization]
```

## Key Differences

| Feature | Claude Desktop | Claude CLI |
|---------|---------------|------------|
| Direct MCP Tools | ✅ Yes | ✅ Yes |
| Agent Support | ❌ No | ✅ Yes (via wrapper) |
| Installation | Single server | Both servers (optional) |
| Usage | Direct tools only | Tools or agents |

## Development

### Testing the Teaching Server
```bash
cd teaching-server
python teaching_mcp.py --test
```

### Testing with Claude CLI
```bash
# Test direct MCP
claude "teach me functions" --mcp-debug

# Test with agents
claude @teaching-orchestrator "teach me functions"
```

## Scrimba Methodology Details

### Micro-Lesson Structure
Every lesson follows this exact timing:
- **0-20s**: Personal story hook ("When I was 19...")
- **20-80s**: ONE concept only
- **80-200s**: Immediate practice
- **200-210s**: Celebration

### Progressive Complexity (5 Levels)
1. Basic declaration
2. Modification/reassignment
3. Shorthand syntax
4. Advanced usage
5. BUILD REAL APP!

### Language Patterns
- ALWAYS: "Hey buddy!", "This is HUGE!", "Super common!"
- NEVER: "Let me explain...", "This is wrong", "As you should know..."

### Projects
1. **Passenger Counter**: Variables & Functions
2. **Blackjack Game**: Logic & Conditionals
3. **Chrome Extension**: Advanced concepts

## Contributing

The teaching logic is centralized in `teaching_mcp.py`. To add new lessons:

1. Add to `LESSONS` dictionary with 5 levels
2. Follow exact Scrimba structure
3. Include personal stories
4. Test with both Desktop and CLI

## License

MIT - Share the Scrimba way of learning!

## Credits

Based on Per Borgen's revolutionary teaching methodology from Scrimba.
"The only way to learn to code is to write a lot of code!"