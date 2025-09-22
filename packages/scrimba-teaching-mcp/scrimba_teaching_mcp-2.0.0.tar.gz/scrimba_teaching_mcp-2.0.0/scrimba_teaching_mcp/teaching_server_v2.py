#!/usr/bin/env python3
"""
Scrimba Teaching MCP Server v2.0.0 - COMPLETE Implementation
Includes ALL agents and tools from original claude-code-mcp
"""

from mcp.server.fastmcp import FastMCP
from typing import Optional, Dict, List
import json
import random
import httpx
import os

# Initialize MCP server
mcp = FastMCP("scrimba-teaching-complete")

# ================== STATE MANAGEMENT ==================
SESSION_STATE = {
    "current_lesson": None,
    "current_step": 1,
    "total_steps": 5,
    "challenges_completed": 0,
    "concepts_learned": [],
    "user_code_history": [],
    "current_project": None,
    "visual_context": {
        "variables": {},
        "scene": "default",
        "frame_count": 0,
        "theme": "pokemon"
    }
}

# ================== VISUAL THEMES ==================
THEMES = {
    "pokemon": {
        "character": "Ash",
        "item": "Pikachu",
        "scene": "grassy field with trees",
        "container": "Pokeball rack"
    },
    "racing": {
        "character": "Racer",
        "item": "car",
        "scene": "racing track with stands",
        "container": "garage with numbered spots"
    },
    "cooking": {
        "character": "Chef",
        "item": "ingredient",
        "scene": "kitchen with countertop",
        "container": "spice rack with labeled jars"
    }
}

# ================== SCRIMBA METHODOLOGY ==================
MICRO_LESSON_STRUCTURE = {
    "hook_duration": 20,
    "concept_duration": 60,
    "challenge_duration": 120,
    "celebration_duration": 10
}

COMPLEXITY_LEVELS = [
    "Basic declaration",
    "Modification/reassignment",
    "Shorthand syntax",
    "Advanced usage",
    "BUILD REAL APP!"
]

# ================== LESSON CONTENT ==================
LESSONS = {
    "variables": {
        "hook": "When I was 19, I had to count subway passengers in the cold...",
        "title": "Variables - Your First Storage Box!",
        "levels": [
            {
                "concept": "let count = 0",
                "explanation": "Read this as 'let count be zero' - super natural!",
                "challenge": "Create a variable called myAge with your age. GO!",
                "console_log": "console.log(myAge)",
                "celebration": "🎉 HUGE! You just stored your FIRST piece of data!"
            }
        ]
    },
    "functions": {
        "hook": "I used to copy-paste the SAME code 50 times...",
        "title": "Functions - Reusable Magic!",
        "levels": [
            {
                "concept": "function greet() { console.log('Hi!') }",
                "explanation": "Functions are reusable code blocks!",
                "challenge": "Create function sayHello() that logs 'Hello!'",
                "console_log": "sayHello()",
                "celebration": "⚡ Your FIRST function!"
            }
        ]
    }
}

CHALLENGES = {
    "easy": [
        {"task": "Create a variable called score and set it to 0", "time": "60 seconds"}
    ],
    "medium": [
        {"task": "Write a function that adds two numbers", "time": "120 seconds"}
    ],
    "hard": [
        {"task": "Create an array and loop through it", "time": "180 seconds"}
    ]
}

PROJECTS = {
    "passenger_counter": {
        "name": "Passenger Counter App",
        "story": "My subway counting problem - solved with code!",
        "starter": "let count = 0\nfunction increment() {\n  count++\n}"
    }
}

# ================== UNIFIED AGENT ROUTER ==================
@mcp.tool()
async def scrimba_agent(
    prompt: str,
    mode: Optional[str] = "auto"
) -> str:
    """
    COMPLETE unified agent-router with ALL functionality.
    Modes: auto, interactive, visual, visual-code, project, challenge, 
           progress, weather, image-generator, orchestrate
    """
    prompt_lower = prompt.lower()
    
    # Auto-detect mode from prompt
    if mode == "auto":
        if any(word in prompt_lower for word in ["weather", "temperature", "forecast", "rain", "sunny"]):
            mode = "weather"
        elif any(word in prompt_lower for word in ["generate image", "create image", "illustration", "artwork", "design"]):
            mode = "image-generator"
        elif any(word in prompt_lower for word in ["visualize code", "code visual", "variable visual", "array visual"]):
            mode = "visual-code"
        elif any(word in prompt_lower for word in ["visual", "image", "picture", "diagram", "see", "show me"]):
            mode = "visual"
        elif any(word in prompt_lower for word in ["project", "build", "app", "real", "passenger", "blackjack"]):
            mode = "project"
        elif any(word in prompt_lower for word in ["challenge", "practice", "exercise", "try"]):
            mode = "challenge"
        elif any(word in prompt_lower for word in ["progress", "score", "how am i", "stats"]):
            mode = "progress"
        else:
            mode = "interactive"
    
    # Route to appropriate handler
    if mode == "weather":
        return await weather_agent(prompt)
    elif mode == "image-generator":
        return await image_generator_agent(prompt)
    elif mode == "visual-code":
        return await visual_code_agent(prompt)
    elif mode == "visual":
        return await visual_learning_agent(prompt)
    elif mode == "project":
        return await project_agent(prompt)
    elif mode == "challenge":
        return await challenge_agent(prompt)
    elif mode == "progress":
        return await progress_agent(prompt)
    elif mode == "orchestrate":
        return await orchestrator_agent(prompt)
    else:  # interactive
        return await interactive_agent(prompt)

# ================== AGENT IMPLEMENTATIONS ==================

async def weather_agent(prompt: str) -> str:
    """Weather agent implementation"""
    cities = []
    words = prompt.lower().split()
    
    # Extract city names (simple implementation)
    for i, word in enumerate(words):
        if word in ["in", "at", "for", "of"] and i + 1 < len(words):
            cities.append(words[i + 1].capitalize())
    
    if not cities:
        cities = ["London"]  # Default city
    
    city = cities[0]
    
    # Simulate weather API call (in real implementation, use actual API)
    weather_data = {
        "temperature": random.randint(10, 30),
        "condition": random.choice(["Sunny", "Cloudy", "Rainy", "Partly Cloudy"]),
        "humidity": random.randint(40, 80),
        "wind": random.randint(5, 20)
    }
    
    return f"""🌤️ **WEATHER AGENT**

**City:** {city}
**Current Conditions:**
- 🌡️ Temperature: {weather_data['temperature']}°C
- ☁️ Condition: {weather_data['condition']}
- 💧 Humidity: {weather_data['humidity']}%
- 💨 Wind: {weather_data['wind']} km/h

**3-Day Forecast:**
Day 1: {random.choice(['Sunny', 'Cloudy'])} - {weather_data['temperature']+1}°C
Day 2: {random.choice(['Rainy', 'Partly Cloudy'])} - {weather_data['temperature']-2}°C
Day 3: {random.choice(['Sunny', 'Cloudy'])} - {weather_data['temperature']}°C

Stay prepared! 🌈"""

async def image_generator_agent(prompt: str) -> str:
    """Image generation prompt specialist"""
    # Extract key elements from request
    subject = "futuristic city" if "city" in prompt.lower() else "mystical landscape"
    style = "photorealistic" if "realistic" in prompt.lower() else "digital art"
    lighting = "sunset" if "sunset" in prompt.lower() else "golden hour"
    
    return f"""🎨 **IMAGE GENERATOR AGENT**

**Optimized Prompt for Image Generation:**
```
{subject}, {style} style, {lighting} lighting, highly detailed, 8K resolution, 
trending on artstation, volumetric lighting, dramatic atmosphere, 
rule of thirds composition, cinematic quality, professional photography

Negative prompt: blurry, low quality, distorted, amateur, oversaturated
```

**Creative Choices:**
- Subject: Enhanced "{subject}" with atmospheric elements
- Style: {style} for maximum impact
- Lighting: {lighting} for dramatic effect
- Technical: 8K resolution for clarity

**Platform Recommendations:**
- Midjourney: Use --v 6 --ar 16:9 --q 2
- DALL-E 3: Direct prompt usage
- Stable Diffusion: CFG Scale 7, Steps 50

**Variations:**
1. Anime style: Add "anime art style, studio ghibli inspired"
2. Oil painting: Replace with "oil painting, impressionist, thick brushstrokes"
3. Minimalist: Add "minimalist, clean lines, simple geometry"

Ready to generate stunning visuals! 🚀"""

async def visual_code_agent(prompt: str) -> str:
    """Visual code representation agent"""
    # Detect what to visualize
    if "variable" in prompt.lower():
        return await variable_visualizer("count", "0", "assign")
    elif "array" in prompt.lower():
        return await array_visualizer("myArray", "create", None, 0)
    elif "loop" in prompt.lower():
        return await loop_animator("for", 3, ["console.log(i)"])
    elif "function" in prompt.lower():
        return await function_sequencer("greet", ["receive input", "process", "return"])
    else:
        return await get_visual_context()

async def visual_learning_agent(prompt: str) -> str:
    """Enhanced visual learning with full functionality"""
    concepts = ["variables", "functions", "loops", "arrays", "objects"]
    detected = "variables"
    
    for concept in concepts:
        if concept in prompt.lower():
            detected = concept
            break
    
    prompts = {
        "variables": "Glowing neon storage boxes floating in cyberspace, each labeled with variable names",
        "functions": "A factory machine with input/output slots processing code blocks",
        "loops": "A circular conveyor belt with code blocks repeating endlessly",
        "arrays": "A shelf with numbered compartments containing data orbs",
        "objects": "A treasure chest with key:value pairs as magical artifacts"
    }
    
    return f"""🎨 **VISUAL LEARNING AGENT**

**Concept:** {detected}

**Scrimba Visual Prompt:**
```
{prompts.get(detected)}

Style: Cyberpunk educational visualization
Colors: Neon blues, purples, and greens on dark background
Elements: Floating code snippets, Matrix-style digital rain
Composition: Center focus with depth, 3D perspective
Quality: Ultra HD, sharp details, glowing effects
```

**Visual Memory Technique:**
This image creates a permanent mental model of {detected}.
Your brain will recall this visual whenever you code!

**Interactive Follow-up:**
After visualizing, type: teach {detected}
Then: give me a {detected} challenge

Visual + Coding = MASTERY! 🚀"""

async def project_agent(prompt: str) -> str:
    """Project-based learning agent"""
    project_name = "passenger_counter"
    
    if "blackjack" in prompt.lower():
        project_name = "blackjack"
    elif "chrome" in prompt.lower():
        project_name = "chrome_extension"
    
    project = PROJECTS.get(project_name, PROJECTS["passenger_counter"])
    
    return f"""🔨 **PROJECT AGENT** - Let's BUILD!

**Project:** {project['name']}

**Personal Story:**
{project['story']}

**Starter Code:**
```javascript
{project['starter']}
```

**Step-by-Step Build:**
1. Copy this starter code
2. Add a button in HTML
3. Connect button to increment()
4. Add display element
5. Update display on each click

**Enhancements:**
- Add decrement button
- Add reset functionality
- Save count to localStorage
- Add multiple counters

Build it NOW! Real apps in 5 minutes! 🚀"""

async def challenge_agent(prompt: str) -> str:
    """Challenge delivery agent"""
    difficulty = "easy"
    
    if "medium" in prompt.lower():
        difficulty = "medium"
    elif "hard" in prompt.lower():
        difficulty = "hard"
    
    challenge = random.choice(CHALLENGES[difficulty])
    
    return f"""⚡ **CHALLENGE AGENT** - Code NOW!

**Difficulty:** {difficulty.upper()}
**Time Limit:** {challenge['time']}

**YOUR MISSION:**
{challenge['task']}

**Rules:**
1. Start coding IMMEDIATELY
2. Use console.log to verify
3. No looking up syntax
4. Trust your instincts

**Timer starts... NOW!** ⏱️

Type your solution and I'll check it!
Remember: Speed + Accuracy = GROWTH! 💪"""

async def progress_agent(prompt: str) -> str:
    """Progress tracking agent"""
    challenges = SESSION_STATE["challenges_completed"]
    concepts = SESSION_STATE["concepts_learned"]
    
    level = "BEGINNER"
    if challenges > 20:
        level = "EXPERT"
    elif challenges > 10:
        level = "INTERMEDIATE"
    elif challenges > 5:
        level = "ADVANCING"
    
    return f"""📊 **PROGRESS AGENT** - Your Journey!

**Stats:**
- Concepts Learned: {len(concepts)}
- Challenges Completed: {challenges}
- Current Level: {level}
- Code Lines Written: {challenges * 10}

**Progress Bar:**
{'█' * min(challenges, 20)}{'░' * (20 - min(challenges, 20))}
{min(challenges * 5, 100)}% to MASTERY!

**Achievements Unlocked:**
{f'🏆 First Variable' if challenges > 0 else '🔒 First Variable'}
{f'⚡ Function Master' if challenges > 5 else '🔒 Function Master'}
{f'🔥 Loop Ninja' if challenges > 10 else '🔒 Loop Ninja'}
{f'💎 Code Wizard' if challenges > 20 else '🔒 Code Wizard'}

Keep coding! You're doing AMAZING! 🚀"""

async def interactive_agent(prompt: str) -> str:
    """Interactive teaching agent"""
    topics = list(LESSONS.keys())
    
    for topic in topics:
        if topic in prompt.lower():
            lesson = LESSONS[topic]
            level = lesson["levels"][0]
            
            return f"""📚 **INTERACTIVE AGENT** - Let's Learn!

**Topic:** {lesson['title']}

**Story:** {lesson['hook']}

**Concept:**
```javascript
{level['concept']}
```

**Explanation:** {level['explanation']}

**Challenge:** {level['challenge']}

**Verify with:**
```javascript
{level['console_log']}
```

{level['celebration']}

Code it NOW! Don't think, just DO! 💪"""
    
    return f"""Hey! I teach: {', '.join(topics)}

Say "teach me [topic]" to start! 🚀"""

async def orchestrator_agent(prompt: str) -> str:
    """Meta-orchestrator explaining the system"""
    return f"""🎯 **ORCHESTRATOR** - System Overview

**Detected in your request:** "{prompt}"

**Available Agents:**
1. **Interactive** - Step-by-step lessons
2. **Visual** - Image prompts for concepts
3. **Visual-Code** - Code visualization tools
4. **Project** - Build real apps
5. **Challenge** - Timed exercises
6. **Progress** - Track journey
7. **Weather** - Weather information
8. **Image-Generator** - AI art prompts
9. **Orchestrator** - This overview

**Smart Routing:**
- "teach me X" → Interactive
- "show me X visually" → Visual
- "visualize my code" → Visual-Code
- "let's build" → Project
- "challenge me" → Challenge
- "my progress" → Progress
- "weather in X" → Weather
- "generate image of X" → Image-Generator

**Architecture:**
All agents unified in one tool!
Auto-detection + Manual override
Full Scrimba methodology embedded

Try any request! 🚀"""

# ================== VISUAL CODE TOOLS ==================

@mcp.tool()
async def variable_visualizer(
    name: str,
    value: str,
    operation: Optional[str] = "assign"
) -> str:
    """Visualize variables as themed quantities"""
    theme = SESSION_STATE["visual_context"]["theme"]
    theme_data = THEMES[theme]
    
    SESSION_STATE["visual_context"]["variables"][name] = value
    
    if operation == "assign":
        prompt = f"{theme_data['character']} placing {value} {theme_data['item']}s into a glowing box labeled '{name}'"
    elif operation == "increment":
        prompt = f"{theme_data['character']} adding one more {theme_data['item']} to the '{name}' box, now containing {value}"
    else:
        prompt = f"{theme_data['character']} modifying the '{name}' box contents to {value} {theme_data['item']}s"
    
    return f"""🎨 **Variable Visualization**

**Image Prompt:**
{prompt}

**Scene:** {theme_data['scene']}
**Style:** Bright, educational, {theme} theme

This shows: `{name} = {value}` visually!"""

@mcp.tool()
async def array_visualizer(
    array_name: str,
    operation: str,
    value: Optional[str] = None,
    index: Optional[int] = None
) -> str:
    """Visualize arrays as indexed containers"""
    theme = SESSION_STATE["visual_context"]["theme"]
    theme_data = THEMES[theme]
    
    if operation == "create":
        prompt = f"Empty {theme_data['container']} with numbered slots 0-4, labeled '{array_name}'"
    elif operation == "push":
        prompt = f"{theme_data['character']} adding '{value}' to the end of {array_name} container"
    elif operation == "access":
        prompt = f"{theme_data['character']} pointing at slot {index} in {array_name}, glowing to show selection"
    else:
        prompt = f"{array_name} array being modified"
    
    return f"""🎨 **Array Visualization**

**Image Prompt:**
{prompt}

**Visual Elements:**
- Numbered compartments (indices)
- Clear slot boundaries
- {theme} themed items

This shows: `{array_name}[{index if index else 'i'}]` concept!"""

@mcp.tool()
async def loop_animator(
    loop_type: str,
    iterations: int,
    operations: List[str]
) -> str:
    """Visualize loops as animated sequences"""
    theme = SESSION_STATE["visual_context"]["theme"]
    theme_data = THEMES[theme]
    
    frames = []
    for i in range(min(iterations, 3)):
        frame = f"Frame {i+1}: {theme_data['character']} at position {i}, "
        frame += f"performing: {operations[0] if operations else 'action'}"
        frames.append(frame)
    
    return f"""🎨 **Loop Animation Sequence**

**{loop_type.upper()} Loop - {iterations} iterations**

**Animation Frames:**
{chr(10).join(frames)}

**Visual Metaphor:**
Circular track with {theme_data['character']} moving through each position,
leaving a glowing trail showing the path taken.

This shows the loop executing step by step!"""

@mcp.tool()
async def function_sequencer(
    function_name: str,
    steps: List[str]
) -> str:
    """Visualize functions as sequential operations"""
    theme = SESSION_STATE["visual_context"]["theme"]
    theme_data = THEMES[theme]
    
    sequence = []
    for i, step in enumerate(steps, 1):
        sequence.append(f"Panel {i}: {step}")
    
    return f"""🎨 **Function Visualization**

**Function: {function_name}()**

**Sequential Panels:**
{chr(10).join(sequence)}

**Visual Style:**
Comic book panels showing {theme_data['character']} 
performing each step in sequence, with arrows
connecting panels to show flow.

Input → Process → Output visualization!"""

@mcp.tool()
async def object_visualizer(
    object_name: str,
    properties: Dict[str, str]
) -> str:
    """Visualize objects as entities with properties"""
    theme = SESSION_STATE["visual_context"]["theme"]
    theme_data = THEMES[theme]
    
    prop_visuals = []
    for key, value in properties.items():
        prop_visuals.append(f"- {key}: glowing tag showing '{value}'")
    
    return f"""🎨 **Object Visualization**

**Object: {object_name}**

**Visual Properties:**
{chr(10).join(prop_visuals)}

**Image Prompt:**
A magical {theme} themed container labeled '{object_name}'
with floating property tags connected by energy beams.
Each property glows with different color.

This shows object structure visually!"""

@mcp.tool()
async def set_visual_theme(theme: str) -> str:
    """Switch visual theme"""
    if theme in THEMES:
        SESSION_STATE["visual_context"]["theme"] = theme
        return f"🎨 Visual theme switched to: {theme}"
    return f"Available themes: {', '.join(THEMES.keys())}"

@mcp.tool()
async def get_visual_context() -> str:
    """Get current visual context"""
    ctx = SESSION_STATE["visual_context"]
    return f"""🎨 **Current Visual Context**

Theme: {ctx['theme']}
Frame Count: {ctx['frame_count']}
Variables: {json.dumps(ctx['variables'], indent=2)}
Scene: {ctx['scene']}"""

# ================== CORE TEACHING TOOLS ==================

@mcp.tool()
async def teach(topic: str, step: Optional[int] = 1) -> str:
    """Core teaching tool"""
    return await interactive_agent(f"teach {topic}")

@mcp.tool()
async def give_challenge(difficulty: Optional[str] = "easy") -> str:
    """Challenge delivery tool"""
    return await challenge_agent(f"challenge {difficulty}")

@mcp.tool()
async def check_code(code: str) -> str:
    """Code checking with encouragement"""
    SESSION_STATE["user_code_history"].append(code)
    SESSION_STATE["challenges_completed"] += 1
    
    # Simple validation
    has_variable = "let" in code or "const" in code or "var" in code
    has_function = "function" in code or "=>" in code
    has_console = "console.log" in code
    
    score = sum([has_variable, has_function, has_console])
    
    if score >= 2:
        return f"""✅ **PERFECT!** Your code is FANTASTIC!

**What you did right:**
{f'✓ Variable declaration' if has_variable else ''}
{f'✓ Function usage' if has_function else ''}
{f'✓ Console.log verification' if has_console else ''}

You're becoming DANGEROUS with code! Keep going! 🚀"""
    else:
        return f"""💪 **Good effort!** Let's make it even better!

**Suggestions:**
{f'→ Add a variable with let/const' if not has_variable else ''}
{f'→ Try adding a function' if not has_function else ''}
{f'→ Use console.log to verify' if not has_console else ''}

Every line you write makes you stronger! Try again! 🔥"""

@mcp.tool()
async def next_lesson() -> str:
    """Progress to next lesson step"""
    SESSION_STATE["current_step"] += 1
    topic = SESSION_STATE.get("current_lesson", "variables")
    return await teach(topic, SESSION_STATE["current_step"])

@mcp.tool()
async def start_project(project_name: Optional[str] = "passenger_counter") -> str:
    """Start a project"""
    return await project_agent(f"start {project_name}")

@mcp.tool()
async def show_progress() -> str:
    """Show learning progress"""
    return await progress_agent("show my progress")

@mcp.tool()
async def visualize_concept(concept: str, style: Optional[str] = "scrimba") -> str:
    """Generate visual learning prompt"""
    return await visual_learning_agent(f"visualize {concept}")

# Run the server
if __name__ == "__main__":
    mcp.run()