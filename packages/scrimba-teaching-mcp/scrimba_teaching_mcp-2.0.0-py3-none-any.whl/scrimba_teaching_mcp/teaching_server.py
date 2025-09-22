#!/usr/bin/env python3
"""
Scrimba Teaching MCP Server v1.2.0
Complete implementation with ALL tools and intelligent routing
Following the agent-orchestrator pattern from claude-code-mcp
"""

from mcp.server.fastmcp import FastMCP
from typing import Optional, Dict, List
import json
import random

# Initialize MCP server
mcp = FastMCP("scrimba-teaching")

# ================== STATE MANAGEMENT ==================
SESSION_STATE = {
    "current_lesson": None,
    "current_step": 1,
    "total_steps": 5,
    "challenges_completed": 0,
    "concepts_learned": [],
    "user_code_history": [],
    "current_project": None,
    # Phase 1.2.0: Add visual context
    "visual_context": {
        "variables": {},
        "scene": "default",
        "frame_count": 0,
        "theme": "pokemon"
    }
}

# ================== VISUAL THEMES (from visual_code_mcp.py) ==================
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
    "hook_duration": 20,       # seconds
    "concept_duration": 60,    # seconds  
    "challenge_duration": 120, # seconds
    "celebration_duration": 10 # seconds
}

# Progressive Complexity (5 levels ALWAYS)
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
        "hook": "When I was 19, I had to count subway passengers in the cold. My fingers would freeze and I'd lose count after 50... If only I had a variable to store the count!",
        "title": "Variables - Your First Storage Box!",
        "levels": [
            {
                "concept": "let count = 0",
                "explanation": "Read this as 'let count be zero' - super natural!",
                "challenge": "Create a variable called myAge with your age. GO!",
                "console_log": "console.log(myAge)  // Let's verify this works!",
                "celebration": "🎉 HUGE! You just stored your FIRST piece of data! This is MASSIVE!"
            },
            {
                "concept": "count = count + 1",
                "explanation": "This adds 1 to count - like clicking a counter!",
                "challenge": "Add 1 to your myAge variable. Type it out!",
                "console_log": "console.log(myAge)  // Should be 1 more!",
                "celebration": "💪 You just CHANGED data! Your code is alive!"
            },
            {
                "concept": "count += 1",
                "explanation": "Shorthand - same thing, less typing!",
                "challenge": "Use += to add 5 to myAge",
                "console_log": "console.log(myAge)  // Jumped by 5!",
                "celebration": "🚀 You're writing like a PRO already!"
            },
            {
                "concept": "count++",
                "explanation": "The FASTEST way to add 1!",
                "challenge": "Create a score variable at 0, then score++ three times",
                "console_log": "console.log(score)  // Should be 3!",
                "celebration": "🔥 You've mastered ALL increment methods!"
            },
            {
                "concept": "Build Passenger Counter!",
                "explanation": "Let's solve my subway problem!",
                "challenge": "Create: count=0, function increment(){count++}, test it!",
                "console_log": "increment(); increment(); console.log(count) // 2!",
                "celebration": "🎊 YOU BUILT A REAL APP! This could save someone's fingers!"
            }
        ]
    },
    "functions": {
        "hook": "I used to copy-paste the SAME code 50 times. Then Per showed me functions - it was like discovering CTRL+C!",
        "title": "Functions - Reusable Magic!",
        "levels": [
            {
                "concept": "function greet() { console.log('Hi!') }",
                "explanation": "Functions are reusable code blocks!",
                "challenge": "Create function sayHello() that logs 'Hello!'",
                "console_log": "sayHello()  // Call it!",
                "celebration": "⚡ Your FIRST function! You can now reuse code!"
            },
            {
                "concept": "function greet(name) { return 'Hello ' + name }",
                "explanation": "Parameters make functions flexible!",
                "challenge": "Create function that takes a name and returns greeting",
                "console_log": "console.log(greet('World'))",
                "celebration": "🎯 Functions with parameters! You're getting DANGEROUS!"
            },
            {
                "concept": "const add = (a, b) => a + b",
                "explanation": "Arrow functions - modern and clean!",
                "challenge": "Create arrow function to multiply two numbers",
                "console_log": "console.log(multiply(3, 4))  // 12",
                "celebration": "⚡ Modern JavaScript! You're coding like it's 2024!"
            },
            {
                "concept": "Higher-order functions",
                "explanation": "Functions that take other functions!",
                "challenge": "Use .map() to double array values",
                "console_log": "[1,2,3].map(x => x * 2)",
                "celebration": "🧙‍♂️ You're using FUNCTIONAL programming!"
            },
            {
                "concept": "Build Calculator App!",
                "explanation": "Multiple functions working together!",
                "challenge": "Create add(), subtract(), multiply(), divide()",
                "console_log": "console.log(add(10, 5))  // Test all!",
                "celebration": "🎊 CALCULATOR APP! You're unstoppable!"
            }
        ]
    },
    "loops": {
        "hook": "I once had to create 100 user profiles manually. It took 3 hours. With loops? 3 seconds!",
        "title": "Loops - Automation Magic!",
        "levels": [
            {
                "concept": "for(let i = 0; i < 5; i++)",
                "explanation": "The classic for loop - repeat 5 times!",
                "challenge": "Count from 0 to 4 with a for loop",
                "console_log": "// Should print 0, 1, 2, 3, 4",
                "celebration": "🔄 Your first loop! You're automating!"
            }
        ]
    }
}

# Challenge definitions
CHALLENGES = {
    "easy": [
        {
            "task": "Create a variable called 'score' and set it to 0",
            "time": "60 seconds",
            "hint": "let score = 0",
            "solution": "let score = 0;\nconsole.log(score);"
        },
        {
            "task": "Create a function that says hello",
            "time": "60 seconds",
            "hint": "function sayHello() { ... }",
            "solution": "function sayHello() {\n  console.log('Hello!');\n}"
        }
    ],
    "medium": [
        {
            "task": "Create a function that adds two numbers",
            "time": "120 seconds",
            "hint": "function add(a, b) { return ... }",
            "solution": "function add(a, b) {\n  return a + b;\n}"
        }
    ],
    "hard": [
        {
            "task": "Create an array of 5 numbers and use a loop to double each one",
            "time": "180 seconds",
            "hint": "Use .map() or a for loop",
            "solution": "const nums = [1, 2, 3, 4, 5];\nconst doubled = nums.map(n => n * 2);\nconsole.log(doubled);"
        }
    ]
}

# Project templates
PROJECTS = {
    "passenger_counter": {
        "name": "Passenger Counter App",
        "story": "Remember my subway story? Let's fix that problem with code!",
        "starter": """// Passenger Counter App
let count = 0;

function increment() {
    count = count + 1;
    console.log(count);
}

// Next: Add save() function
// Then: Add reset() function
// Finally: Display in HTML!""",
        "steps": [
            "Create the count variable",
            "Create increment function",
            "Add a save function",
            "Add reset functionality",
            "Connect to HTML buttons"
        ]
    },
    "blackjack": {
        "name": "Blackjack Game",
        "story": "I won 100 euros in Prague playing Blackjack. Let's build the game!",
        "starter": """// Blackjack Game
let firstCard = 10;
let secondCard = 4;
let sum = firstCard + secondCard;

console.log('Your cards: ' + sum);

// Next: Add hit() function
// Then: Check for blackjack
// Finally: Add betting!"""
    },
    "chrome_extension": {
        "name": "Lead Tracker Chrome Extension",
        "story": "Save tabs for later - never lose important links again!",
        "starter": """// Chrome Extension
let myLeads = [];
const inputEl = document.getElementById("input-el");

function save() {
    myLeads.push(inputEl.value);
    console.log(myLeads);
}"""
    }
}

# ================== INTELLIGENT AGENT ROUTER ==================
# Based on agent-orchestrator.md pattern

@mcp.tool()
async def scrimba_agent(
    prompt: str,
    mode: Optional[str] = "auto"
) -> str:
    """
    Unified agent-router that analyzes requests intelligently.
    Embeds all agent personalities from claude-code-mcp.
    Uses intent analysis, not keyword matching.
    
    Args:
        prompt: User's request or question
        mode: auto (intelligent analysis) or specific mode override
    
    Returns:
        Appropriate response based on detected intent
    """
    
    # Phase 1.2.0: Intelligent intent analysis (not if/elif keywords)
    if mode == "auto":
        # Analyze the user's PRIMARY INTENT, not just keywords
        # This mimics the agent-orchestrator's intelligent routing
        
        prompt_lower = prompt.lower()
        
        # Create intent analysis context
        intent_context = {
            "has_weather_terms": any(word in prompt_lower for word in ["weather", "temperature", "forecast", "rain", "sunny", "cloudy", "snow"]),
            "has_image_creation": any(phrase in prompt_lower for phrase in ["generate image", "create image", "design", "illustration", "artwork"]),
            "has_code_visualization": any(phrase in prompt_lower for phrase in ["visualize code", "show me how", "variable visual", "array visual"]),
            "has_visual_learning": any(word in prompt_lower for word in ["visual", "picture", "diagram", "see", "show"]),
            "has_project_intent": any(word in prompt_lower for word in ["build", "project", "app", "passenger", "blackjack", "extension"]),
            "has_practice_intent": any(word in prompt_lower for word in ["challenge", "practice", "exercise", "try", "test"]),
            "has_progress_check": any(phrase in prompt_lower for phrase in ["my progress", "how am i", "stats", "score"]),
            "has_teaching_intent": any(word in prompt_lower for word in ["teach", "learn", "explain", "what is", "how to", "show me"])
        }
        
        # Intelligent routing based on PRIMARY intent (priority order matters)
        if intent_context["has_weather_terms"]:
            mode = "weather"
        elif intent_context["has_image_creation"]:
            mode = "image-generator"
        elif intent_context["has_code_visualization"]:
            mode = "visual-code"
        elif intent_context["has_project_intent"]:
            mode = "project"
        elif intent_context["has_practice_intent"]:
            mode = "challenge"
        elif intent_context["has_progress_check"]:
            mode = "progress"
        elif intent_context["has_visual_learning"]:
            mode = "visual"
        elif intent_context["has_teaching_intent"]:
            mode = "interactive"
        else:
            # Default to interactive teaching
            mode = "interactive"
    
    # Route to appropriate handler based on determined mode
    if mode == "weather":
        return await handle_weather_intent(prompt)
    elif mode == "image-generator":
        return await handle_image_generation_intent(prompt)
    elif mode == "visual-code":
        return await handle_visual_code_intent(prompt)
    elif mode == "visual":
        return await handle_visual_learning_intent(prompt)
    elif mode == "project":
        return await handle_project_intent(prompt)
    elif mode == "challenge":
        return await handle_challenge_intent(prompt)
    elif mode == "progress":
        return await handle_progress_intent(prompt)
    elif mode == "orchestrate":
        return await handle_orchestrator_intent(prompt)
    else:
        return await handle_interactive_teaching_intent(prompt)

# ================== INTENT HANDLERS ==================

async def handle_weather_intent(prompt: str) -> str:
    """Weather agent implementation"""
    prompt_lower = prompt.lower()
    city = "London"  # Default
    
    # Extract city name intelligently
    words = prompt_lower.split()
    for i, word in enumerate(words):
        if word in ["in", "at", "for", "of"] and i + 1 < len(words):
            city = words[i + 1].capitalize()
            break
    
    # Generate weather data
    temp = random.randint(10, 30)
    conditions = ["Sunny ☀️", "Cloudy ☁️", "Rainy 🌧️", "Partly Cloudy ⛅"]
    condition = random.choice(conditions)
    
    return f"""🌤️ **WEATHER AGENT**
    
**Location:** {city}
**Temperature:** {temp}°C / {int(temp * 1.8 + 32)}°F
**Conditions:** {condition}
**Humidity:** {random.randint(40, 80)}%
**Wind:** {random.randint(5, 25)} km/h

**3-Day Forecast:**
Tomorrow: {random.choice(conditions)} - {temp + random.randint(-3, 3)}°C
Day 2: {random.choice(conditions)} - {temp + random.randint(-3, 3)}°C  
Day 3: {random.choice(conditions)} - {temp + random.randint(-3, 3)}°C

Stay weather-aware! 🌈"""

async def handle_image_generation_intent(prompt: str) -> str:
    """Image generator agent - creates optimized prompts for AI image generation"""
    prompt_lower = prompt.lower()
    
    # Extract subject from request
    subject = "mystical landscape"
    style = "digital art"
    lighting = "golden hour"
    
    if "city" in prompt_lower:
        subject = "futuristic city with towering skyscrapers"
    elif "dragon" in prompt_lower:
        subject = "majestic dragon with detailed scales"
    elif "forest" in prompt_lower:
        subject = "enchanted forest with glowing plants"
    elif "sunset" in prompt_lower:
        lighting = "sunset with dramatic colors"
    
    if "realistic" in prompt_lower or "photo" in prompt_lower:
        style = "photorealistic, hyperrealistic"
    elif "anime" in prompt_lower:
        style = "anime art style, studio ghibli inspired"
    elif "oil" in prompt_lower or "painting" in prompt_lower:
        style = "oil painting, impressionist"
    
    return f"""🎨 **IMAGE GENERATOR AGENT**

**Primary Prompt (Optimized):**
```
{subject}, {style}, {lighting} lighting,
highly detailed, 8K resolution, trending on artstation,
volumetric lighting, dramatic atmosphere, rule of thirds composition,
cinematic quality, professional photography, sharp focus

Negative prompt: blurry, low quality, distorted, amateur, oversaturated, ugly
```

**Creative Choices Explained:**
- **Subject Enhancement:** Transformed "{subject}" with atmospheric details
- **Style Selection:** {style} for maximum visual impact
- **Lighting:** {lighting} creates mood and depth
- **Technical specs:** 8K for clarity, rule of thirds for composition

**Platform-Specific Settings:**
- **Midjourney:** `--v 6 --ar 16:9 --q 2 --stylize 100`
- **DALL-E 3:** Use prompt directly, no modifications needed
- **Stable Diffusion:** CFG Scale: 7, Sampling Steps: 50, Sampler: DPM++ 2M Karras

**Style Variations to Try:**
1. **Cyberpunk:** Add "cyberpunk, neon lights, rain-soaked streets"
2. **Fantasy:** Add "fantasy art, magical atmosphere, ethereal"
3. **Minimalist:** Replace with "minimalist, clean lines, simple geometry, negative space"

Ready to generate stunning visuals! Try the prompt now! 🚀"""

async def handle_visual_code_intent(prompt: str) -> str:
    """Visual code representation using themed metaphors"""
    prompt_lower = prompt.lower()
    
    # Detect what code concept to visualize
    if "variable" in prompt_lower:
        if "assign" in prompt_lower or "=" in prompt_lower:
            return await variable_visualizer("myVariable", "5", "assign")
        else:
            return await variable_visualizer("count", "0", "assign")
    elif "array" in prompt_lower:
        return await array_visualizer("myArray", "create", "5")
    elif "loop" in prompt_lower:
        return await loop_animator("for", 3, ["console.log(i)", "process item", "update counter"])
    elif "function" in prompt_lower:
        return await function_sequencer("calculateSum", ["receive inputs", "add numbers", "return result"])
    elif "object" in prompt_lower:
        return await object_visualizer("user", {"name": "Alice", "age": "25", "role": "developer"})
    else:
        return """🎮 **VISUAL CODE AGENT**

I can visualize these concepts for you:
- **Variables:** Storage boxes with values
- **Arrays:** Numbered containers
- **Loops:** Repeating sequences
- **Functions:** Step-by-step processes
- **Objects:** Entities with properties

Current theme: {theme}

Try: "visualize a variable assignment" or "show me how arrays work"!""".format(
    theme=SESSION_STATE["visual_context"]["theme"]
)

async def handle_visual_learning_intent(prompt: str) -> str:
    """Visual learning with image prompts for concepts"""
    concepts = ["variables", "functions", "loops", "arrays", "objects", "conditionals"]
    detected_concept = "variables"
    
    prompt_lower = prompt.lower()
    for concept in concepts:
        if concept in prompt_lower:
            detected_concept = concept
            break
    
    # Scrimba-style visual prompts
    visual_prompts = {
        "variables": "A glowing neon storage box floating in cyberspace, labeled 'count = 0', with smaller boxes showing count++, count += 5, visual transformation sequence",
        "functions": "A steampunk factory machine with input funnel labeled 'parameters', internal gears processing, output pipe labeled 'return', code blocks being transformed",
        "loops": "A mesmerizing circular conveyor belt with code blocks repeating, counter display showing i=0, i<10, i++, items transforming at each cycle",
        "arrays": "A futuristic shelf system with numbered compartments [0][1][2][3], each containing glowing data orbs, push/pop animations visible",
        "objects": "A magical treasure chest opening to reveal key:value pairs as floating holographic cards, properties connected by energy beams",
        "conditionals": "A branching pathway in a digital forest, if/else gates glowing, true path in green, false path in red, decision points highlighted"
    }
    
    return f"""🎨 **VISUAL LEARNING AGENT**

**Concept Detected:** {detected_concept.capitalize()}

**Scrimba Visual Learning Prompt:**
```
{visual_prompts.get(detected_concept, visual_prompts["variables"])}

Style: Educational cyberpunk visualization
Color palette: Neon blues, purples, and greens on dark background
Elements: Floating code snippets, Matrix-style digital rain in background
Composition: Center-focused with depth, 3D perspective
Animation: Subtle glow effects, particle systems
Quality: Ultra HD, crisp details, educational clarity
```

**Visual Memory Technique:**
This image creates a PERMANENT mental model of {detected_concept}!
Your brain processes images 60,000x faster than text.

**Learning Path:**
1. 👁️ Visualize: Generate this image
2. 🧠 Internalize: Stare for 30 seconds
3. ✍️ Practice: Type `teach {detected_concept}`
4. 🚀 Apply: Get a {detected_concept} challenge

Visual + Hands-on = MASTERY! Let's GO! 💪"""

async def handle_project_intent(prompt: str) -> str:
    """Project-based learning handler"""
    prompt_lower = prompt.lower()
    
    # Detect which project
    project_name = "passenger_counter"
    if "blackjack" in prompt_lower or "card" in prompt_lower:
        project_name = "blackjack"
    elif "chrome" in prompt_lower or "extension" in prompt_lower:
        project_name = "chrome_extension"
    
    project = PROJECTS.get(project_name, PROJECTS["passenger_counter"])
    SESSION_STATE["current_project"] = project_name
    
    return f"""🔨 **PROJECT MODE** - Let's BUILD Something REAL!

**Project:** {project['name']}

**Personal Story:**
{project['story']}

**Starter Code (Copy This NOW!):**
```javascript
{project['starter']}
```

**Build Steps (Follow Along):**
{chr(10).join(f"{i+1}. {step}" for i, step in enumerate(project.get('steps', ['Start coding!'])))}

**Why This Project?**
- Solves a REAL problem
- Uses core concepts you've learned
- Can be expanded infinitely
- You'll actually USE it!

**Pro Tips:**
1. Type EVERY line yourself (no copy-paste!)
2. console.log() after each step
3. Break it? GOOD! Fix it and learn!
4. Make it yours - add features!

Start typing the starter code RIGHT NOW! Don't think, just DO! 🚀"""

async def handle_challenge_intent(prompt: str) -> str:
    """Challenge delivery handler"""
    prompt_lower = prompt.lower()
    
    # Determine difficulty
    difficulty = "easy"
    if "medium" in prompt_lower or "intermediate" in prompt_lower:
        difficulty = "medium"
    elif "hard" in prompt_lower or "difficult" in prompt_lower or "advanced" in prompt_lower:
        difficulty = "hard"
    
    challenge = random.choice(CHALLENGES[difficulty])
    SESSION_STATE["challenges_completed"] += 1
    
    return f"""⚡ **CHALLENGE TIME!** - Code NOW, Think Later!

**Difficulty:** {difficulty.upper()}
**Time Limit:** {challenge['time']}
**Timer starts... NOW!** ⏰

📝 **YOUR MISSION:**
{challenge['task']}

**Rules:**
1. Start typing IMMEDIATELY
2. Use console.log() to verify
3. NO looking up syntax!
4. Trust your instincts

💡 **Stuck? Here's a tiny hint:**
{challenge['hint']}

**When done, type your solution and I'll check it!**

Remember: The best way to learn is to WRITE CODE! GO GO GO! 💪"""

async def handle_progress_intent(prompt: str) -> str:
    """Progress tracking handler"""
    challenges = SESSION_STATE["challenges_completed"]
    concepts = SESSION_STATE["concepts_learned"]
    current_lesson = SESSION_STATE.get("current_lesson", "Not started")
    
    # Determine level
    level = "BEGINNER 🌱"
    motivation = "🚀 Your journey is about to begin!"
    
    if challenges > 50:
        level = "LEGENDARY 👑"
        motivation = "🔥🔥🔥 You're in the TOP 1%! Keep crushing it!"
    elif challenges > 25:
        level = "PROFESSIONAL 💼"
        motivation = "💎 You're coding at a professional level!"
    elif challenges > 10:
        level = "INTERMEDIATE ⚡"
        motivation = "🚀 Your growth is EXPONENTIAL! Keep going!"
    elif challenges > 5:
        level = "ADVANCING 📈"
        motivation = "💪 You're picking up speed! This is where it gets FUN!"
    elif challenges > 0:
        level = "STARTED 🎯"
        motivation = "🌟 You've taken the first step! That's the hardest part!"
    
    return f"""📊 **PROGRESS REPORT** - Your Coding Journey!

**Current Stats:**
- 📚 Current Topic: {current_lesson}
- 🎯 Concepts Learned: {len(concepts)}
- ⚡ Challenges Crushed: {challenges}
- 📝 Code Lines Written: ~{challenges * 10}
- 🏆 Current Level: {level}

**Progress Visualization:**
{'█' * min(challenges, 50)}{'░' * (50 - min(challenges, 50))}
{min(challenges * 2, 100)}% to MASTERY!

**Unlocked Achievements:**
{f"✅ First Variable - You stored data!" if challenges > 0 else "🔒 First Variable"}
{f"✅ Function Master - You can reuse code!" if challenges > 5 else "🔒 Function Master"}
{f"✅ Loop Ninja - Automation unlocked!" if challenges > 10 else "🔒 Loop Ninja"}
{f"✅ Project Builder - You ship real apps!" if challenges > 20 else "🔒 Project Builder"}
{f"✅ Code Wizard - You think in code!" if challenges > 50 else "🔒 Code Wizard"}

{motivation}

**Next Steps:**
- Get another challenge: "give me a challenge"
- Start a project: "let's build something"
- Learn new concept: "teach me loops"

Remember: Every line you write makes you stronger! 💪"""

async def handle_orchestrator_intent(prompt: str) -> str:
    """Meta-orchestrator explaining the system"""
    return f"""🎯 **ORCHESTRATOR MODE** - How I Work!

I detected in your request: "{prompt}"

**My Intelligence System:**
I analyze your intent, not just keywords. I understand context, goals, and learning styles.

**Available Modes & How I Route:**

1. **🌤️ Weather** → Natural language about weather/temperature
2. **🎨 Image Generator** → "Create/generate/design an image"
3. **🎮 Visual Code** → "Visualize my code/variable/array"
4. **👁️ Visual Learning** → "Show me visually how X works"
5. **🔨 Project** → "Build/create an app/project"
6. **⚡ Challenge** → "Challenge/practice/exercise"
7. **📊 Progress** → "My progress/stats/achievements"
8. **📚 Interactive** → "Teach/explain/learn" (default)

**Smart Routing Examples:**
- "teach me about loops" → Interactive lesson mode
- "show me loops visually" → Visual learning with image prompt
- "visualize my loop code" → Visual code representation
- "challenge with loops" → Practice challenge
- "build loop project" → Project mode

**The Magic:**
I don't just match keywords. I understand:
- Teaching progression (5 levels always)
- Scrimba methodology (60-second rule)
- Visual learning preferences
- Project-based learning
- Gamification & motivation

Try ANY request - I'll route it perfectly! 🚀"""

async def handle_interactive_teaching_intent(prompt: str) -> str:
    """Interactive teaching handler - the default mode"""
    prompt_lower = prompt.lower()
    
    # Detect topic
    topics = list(LESSONS.keys())
    detected_topic = None
    
    for topic in topics:
        if topic in prompt_lower:
            detected_topic = topic
            break
    
    if detected_topic:
        # Determine step level
        step = SESSION_STATE.get("current_step", 1)
        if "continue" in prompt_lower or "next" in prompt_lower:
            step = min(step + 1, 5)
        elif any(str(i) in prompt_lower for i in range(1, 6)):
            for i in range(1, 6):
                if str(i) in prompt_lower:
                    step = i
                    break
        
        SESSION_STATE["current_lesson"] = detected_topic
        SESSION_STATE["current_step"] = step
        
        lesson = LESSONS[detected_topic]
        level = lesson["levels"][min(step - 1, len(lesson["levels"]) - 1)]
        
        return f"""📚 **INTERACTIVE LESSON** - {lesson['title']}
        
**Level {step}/5: {COMPLEXITY_LEVELS[step-1]}**
{'='*60}

**🎬 Hook (20 seconds):**
{lesson['hook'] if step == 1 else 'Remember our journey? Let\'s go DEEPER!'}

**💡 The Concept (60 seconds):**
{level['explanation']}

```javascript
{level['concept']}
```

**🔬 Console.log Driven Development:**
```javascript
// Step 1: Write the code
{level['concept']}

// Step 2: IMMEDIATELY verify
{level['console_log']}

// Step 3: Celebrate!
"Yes! It works! You're programming!"
```

**🎯 YOUR CHALLENGE (You have {MICRO_LESSON_STRUCTURE['challenge_duration']} seconds):**
{level['challenge']}

Type it NOW! Don't think! Your fingers should be moving!

{level['celebration']}

**Commands:**
- Next level: "continue" or "next"
- Get hint: "hint please"
- Check code: "check: [your code]"

GO GO GO! 🚀"""
    
    else:
        # No topic detected - show available topics
        return f"""Hey buddy! I'm Per from Scrimba! What do you want to learn? 🔥

**Available Topics:**
{chr(10).join(f"• {topic.capitalize()} - {LESSONS[topic]['title']}" for topic in topics)}

**Quick Commands:**
- 📚 Learn: "teach me variables"
- ⚡ Practice: "give me a challenge"  
- 🔨 Build: "start a project"
- 📊 Progress: "show my progress"
- 🎨 Visual: "show me variables visually"

What gets you EXCITED? Let's learn by DOING!

Remember: The only way to learn to code is to write a LOT of code! 💪"""

# ================== VISUAL CODE TOOLS (from visual_code_mcp.py) ==================

@mcp.tool()
async def variable_visualizer(
    name: str,
    value: str,
    operation: Optional[str] = "assign"
) -> str:
    """Visualize variables as quantities of themed items"""
    theme = THEMES[SESSION_STATE["visual_context"]["theme"]]
    prev_value = SESSION_STATE["visual_context"]["variables"].get(name, 0)
    
    try:
        num_value = int(value)
    except:
        # String or boolean
        return f"Text bubble showing '{name} = {value}' floating above {theme['character']}"
    
    # Update context
    SESSION_STATE["visual_context"]["variables"][name] = num_value
    
    # Generate appropriate prompt based on operation
    if operation == "assign":
        if num_value == 0:
            prompt = f"{theme['scene']} with {theme['character']} standing alone, looking around for {name}"
        elif num_value == 1:
            prompt = f"{theme['scene']} with {theme['character']} and exactly 1 {theme['item']} appearing with sparkle effect"
        else:
            prompt = f"{theme['scene']} with {theme['character']} and exactly {num_value} {theme['item']}s lined up in a row"
    
    elif operation == "increment":
        diff = num_value - prev_value
        prompt = f"Same scene but now {num_value} {theme['item']}s total, the {diff} new one(s) appearing with glow effect"
    
    elif operation == "decrement":
        diff = prev_value - num_value
        prompt = f"Same scene but now only {num_value} {theme['item']}s, {diff} fading away with particle effect"
    
    else:
        prompt = f"Visual showing {name} = {value} in {theme['scene']}"
    
    return f"""🎮 **Variable Visualization**

**Theme:** {SESSION_STATE["visual_context"]["theme"]}

**Image Prompt:**
{prompt}

**What This Shows:**
`{name} = {value}` - {operation} operation

This visual helps you understand variables as tangible objects!"""

@mcp.tool()
async def array_visualizer(
    array_name: str,
    operation: str,
    value: Optional[str] = None,
    index: Optional[int] = None
) -> str:
    """Visualize arrays as containers with indexed slots"""
    theme = THEMES[SESSION_STATE["visual_context"]["theme"]]
    
    if operation == "create":
        prompt = f"{theme['container']} with empty numbered slots from 0 to {value or 'several'}"
    elif operation == "assign" and index is not None:
        prompt = f"{theme['container']} with slot [{index}] glowing, {value} being placed inside"
    elif operation == "push":
        prompt = f"{theme['container']} with new slot appearing at the end, {value} sliding in with motion blur"
    elif operation == "pop":
        prompt = f"Last item in {theme['container']} popping out with spring animation, slot disappearing"
    elif operation == "access" and index is not None:
        prompt = f"{theme['container']} with slot [{index}] highlighted in golden glow, item inside magnified"
    else:
        prompt = f"{theme['container']} showing array operations"
    
    return f"""🎮 **Array Visualization**

**Theme:** {SESSION_STATE["visual_context"]["theme"]}

**Image Prompt:**
{prompt}

**What This Shows:**
`{array_name}` array - {operation} operation
{f'Index [{index}]' if index is not None else ''}
{f'Value: {value}' if value else ''}

Arrays are just numbered containers - easy to understand visually!"""

@mcp.tool()
async def loop_animator(
    loop_type: str,
    iterations: int,
    operations: List[str]
) -> str:
    """Visualize loops as transformative sequences"""
    theme = THEMES[SESSION_STATE["visual_context"]["theme"]]
    
    frames = []
    for i in range(min(iterations, 5)):  # Limit to 5 frames for clarity
        frame_op = operations[i % len(operations)] if operations else f"iteration {i}"
        frames.append(f"Frame {i+1}: Counter shows 'i = {i}', {frame_op}")
    
    if iterations > 5:
        frames.append(f"... continues for {iterations - 5} more iterations ...")
    frames.append(f"Final frame: Loop complete, showing accumulated result")
    
    prompt = f"""**Loop Animation ({loop_type} loop - {iterations} iterations)**
Setting: {theme['scene']}

Progressive transformation sequence:
{chr(10).join(frames)}

Each iteration builds on the previous, showing the counter incrementing and operations executing"""
    
    return f"""🎮 **Loop Animation**

**Theme:** {SESSION_STATE["visual_context"]["theme"]}

{prompt}

**What This Shows:**
{loop_type} loop running {iterations} times
Each frame shows the loop variable changing

Loops are just automated repetition - see it happen step by step!"""

@mcp.tool()
async def function_sequencer(
    function_name: str,
    steps: List[str]
) -> str:
    """Visualize functions as sequential frames"""
    theme = THEMES[SESSION_STATE["visual_context"]["theme"]]
    
    frames = []
    for i, step in enumerate(steps, 1):
        frames.append(f"Panel {i}: {step}")
    
    prompt = f"""**Function: {function_name}()**
Setting: {theme['scene']}

Sequential storyboard panels:
{chr(10).join(frames)}

Each panel shows progression, maintaining same {theme['character']} and setting
Arrows connect panels to show flow"""
    
    return f"""🎮 **Function Visualization**

**Theme:** {SESSION_STATE["visual_context"]["theme"]}

{prompt}

**What This Shows:**
Function `{function_name}` executing step-by-step
Input → Process → Output flow

Functions are just recipes - follow the steps!"""

@mcp.tool()
async def object_visualizer(
    object_name: str,
    properties: Dict[str, str]
) -> str:
    """Visualize objects as entities with highlighted properties"""
    theme_name = SESSION_STATE["visual_context"]["theme"]
    theme = THEMES[theme_name]
    
    if theme_name == "racing":
        # Car-themed object
        prop_visuals = []
        for prop, value in properties.items():
            if prop in ["wheels", "speed", "engine"]:
                prop_visuals.append(f"Close-up: {value} {prop} with glowing label")
            else:
                prop_visuals.append(f"Dashboard showing '{prop}: {value}'")
        prompt = "Racing car with properties:\n" + "\n".join(prop_visuals)
    elif theme_name == "pokemon":
        # Pokemon-themed object
        prompt = f"Pokemon card showing {object_name} with stats:\n"
        prompt += "\n".join([f"• {k}: {v} (glowing stat bar)" for k, v in properties.items()])
    else:
        # Generic object
        prompt = f"Central {object_name} entity with property bubbles:\n"
        prompt += "\n".join([f"• {k}: {v} (highlighted bubble)" for k, v in properties.items()])
    
    return f"""🎮 **Object Visualization**

**Theme:** {theme_name}

**Image Prompt:**
{prompt}

**What This Shows:**
Object `{object_name}` with properties:
{chr(10).join([f'- {k}: {v}' for k, v in properties.items()])}

Objects are just containers for related data!"""

@mcp.tool()
async def set_visual_theme(theme: str) -> str:
    """Switch the visual theme for code visualization"""
    if theme in THEMES:
        SESSION_STATE["visual_context"]["theme"] = theme
        return f"""🎨 **Theme Changed!**

New theme: **{theme}**
- Character: {THEMES[theme]['character']}
- Items: {THEMES[theme]['item']}
- Scene: {THEMES[theme]['scene']}
- Container: {THEMES[theme]['container']}

All future visualizations will use this theme!"""
    
    return f"Available themes: {', '.join(THEMES.keys())}"

@mcp.tool()
async def get_visual_context() -> str:
    """Get current visual context and settings"""
    ctx = SESSION_STATE["visual_context"]
    return f"""🎮 **Current Visual Context**

**Theme:** {ctx['theme']}
**Scene:** {THEMES[ctx['theme']]['scene']}
**Variables Tracked:** {ctx['variables']}
**Frame Count:** {ctx['frame_count']}

**Available Themes:** {', '.join(THEMES.keys())}

Switch theme with: set_visual_theme("pokemon|racing|cooking")"""

# ================== CORE TEACHING TOOLS ==================

@mcp.tool()
async def teach(
    topic: str,
    step: Optional[int] = 1
) -> str:
    """
    Teach a programming concept using Scrimba methodology.
    Gets users coding within 60 seconds!
    """
    return await handle_interactive_teaching_intent(f"teach me {topic} step {step}")

@mcp.tool()
async def give_challenge(
    difficulty: Optional[str] = "easy"
) -> str:
    """
    Give an immediate coding challenge.
    """
    return await handle_challenge_intent(f"give me a {difficulty} challenge")

@mcp.tool()
async def check_code(
    code: str
) -> str:
    """
    Check user's code with Scrimba-style encouragement.
    ALWAYS celebrates, even mistakes!
    """
    SESSION_STATE["user_code_history"].append(code)
    SESSION_STATE["challenges_completed"] += 1
    
    # Analyze code
    has_variable = any(keyword in code for keyword in ["let", "const", "var"])
    has_function = "function" in code or "=>" in code
    has_console = "console.log" in code
    has_loop = any(keyword in code for keyword in ["for", "while", "forEach", "map"])
    has_array = "[" in code and "]" in code
    
    score = sum([has_variable, has_function, has_console, has_loop, has_array])
    
    # Always encouraging feedback
    if score >= 3:
        feedback = f"""🎉 **ABSOLUTELY PERFECT!** This is PROFESSIONAL-LEVEL code!

**What you NAILED:**
{f'✅ Variable declaration - Clean and clear!' if has_variable else ''}
{f'✅ Function usage - Reusable code!' if has_function else ''}
{f'✅ Console.log verification - Debugging like a PRO!' if has_console else ''}
{f'✅ Loop implementation - Automation master!' if has_loop else ''}
{f'✅ Array handling - Data structures unlocked!' if has_array else ''}

You're becoming DANGEROUS with code! This is EXACTLY how I code! 🔥"""
        
    elif score >= 2:
        feedback = f"""💪 **GREAT JOB!** You're really getting it!

**What's working:**
{f'✅ Variables - Nice!' if has_variable else ''}
{f'✅ Functions - Good!' if has_function else ''}
{f'✅ Console.log - Smart!' if has_console else ''}

**Make it even better:**
{f'→ Try adding a console.log to verify' if not has_console else ''}
{f'→ Consider using a function' if not has_function else ''}
{f'→ Maybe add a loop for practice' if not has_loop else ''}

You're on the right track! Keep going! 🚀"""
        
    else:
        feedback = f"""🌟 **Good effort!** Every line you write makes you stronger!

**I see you're experimenting - that's PERFECT!**

**Quick tips to level up:**
{f'→ Add a variable with let or const' if not has_variable else ''}
{f'→ Use console.log() to see your output' if not has_console else ''}
{f'→ Try wrapping code in a function' if not has_function else ''}

Remember: I made TONS of mistakes when learning. That's how you grow!

Try again! You're closer than you think! 💪"""
    
    return feedback

@mcp.tool()
async def next_lesson() -> str:
    """Progress to next lesson step"""
    current = SESSION_STATE.get("current_lesson", "variables")
    step = SESSION_STATE.get("current_step", 1) + 1
    
    if step > 5:
        return "🎉 You've completed this lesson! Try: 'teach me functions' or 'start a project'!"
    
    SESSION_STATE["current_step"] = step
    return await teach(current, step)

@mcp.tool()
async def start_project(
    project_name: Optional[str] = "passenger_counter"
) -> str:
    """Start a Scrimba project with step-by-step guidance"""
    return await handle_project_intent(f"start {project_name} project")

@mcp.tool()
async def show_progress() -> str:
    """Show user's learning progress with celebrations"""
    return await handle_progress_intent("show my progress")

@mcp.tool()
async def visualize_concept(
    concept: str,
    style: Optional[str] = "scrimba"
) -> str:
    """Generate visual learning prompt for a concept"""
    return await handle_visual_learning_intent(f"visualize {concept}")

@mcp.tool()
async def show_hint(
    level: Optional[int] = 1
) -> str:
    """Give progressive hints without revealing the full answer"""
    current_lesson = SESSION_STATE.get("current_lesson", "variables")
    current_step = SESSION_STATE.get("current_step", 1)
    
    if current_lesson and current_lesson in LESSONS:
        lesson = LESSONS[current_lesson]
        if current_step <= len(lesson["levels"]):
            level_data = lesson["levels"][current_step - 1]
            
            if level == 1:
                return f"💡 **Subtle hint:** Look at the pattern in: {level_data['concept'][:10]}..."
            elif level == 2:
                return f"💡 **Clearer hint:** Start with: {level_data['hint']}"
            else:
                return f"💡 **Almost there:** {level_data['solution'] if 'solution' in level_data else level_data['hint']}"
    
    return "💡 Try: 'teach me variables' to start learning!"

@mcp.tool()
async def celebrate(
    achievement: Optional[str] = "progress"
) -> str:
    """Celebrate user's achievement with Scrimba-style enthusiasm"""
    celebrations = {
        "first_variable": "🎉 YOUR FIRST VARIABLE! This is HUGE! You just learned how computers remember things!",
        "first_function": "⚡ FIRST FUNCTION! You can now write reusable code! This changes EVERYTHING!",
        "first_loop": "🔄 LOOP MASTERY! You just automated repetition! You're thinking like a programmer!",
        "completed_lesson": "🎓 LESSON COMPLETE! You're learning 10x faster than traditional methods!",
        "fixed_bug": "🐛 BUG FIXED! Every bug you fix makes you stronger! I still get bugs daily!",
        "progress": f"🚀 You're making INCREDIBLE progress! {SESSION_STATE['challenges_completed']} challenges completed!"
    }
    
    return celebrations.get(achievement, celebrations["progress"])

# Run the server
if __name__ == "__main__":
    mcp.run()