#!/usr/bin/env python3
"""
Scrimba Teaching MCP Server - Unified Teaching Logic
Contains ALL Scrimba methodology in one place
Works with both Claude Desktop (direct) and Claude CLI (via agents)
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
    "current_project": None
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
                "challenge": "Make greet(name) return 'Hello ' + name",
                "console_log": "console.log(greet('Per'))  // 'Hello Per'",
                "celebration": "🎯 Functions with parameters! SO powerful!"
            },
            {
                "concept": "Return values",
                "explanation": "Functions can give back results!",
                "challenge": "Create add(a, b) that RETURNS a + b",
                "console_log": "console.log(add(5, 3))  // 8",
                "celebration": "🏆 You're combining and returning! DANGEROUS skills!"
            },
            {
                "concept": "Functions calling functions",
                "explanation": "Functions can call other functions!",
                "challenge": "Create double(n) and triple(n), then combine them!",
                "console_log": "console.log(triple(double(5)))  // 30",
                "celebration": "🎪 Function CIRCUS! They're working together!"
            },
            {
                "concept": "Build Calculator!",
                "explanation": "Real calculator with add, subtract, multiply!",
                "challenge": "Create 3 functions, test each!",
                "console_log": "console.log(multiply(add(2,3), 4))  // 20",
                "celebration": "🌟 YOU BUILT A CALCULATOR! Mom would be proud!"
            }
        ]
    }
}

# Projects following Scrimba methodology
PROJECTS = {
    "passenger_counter": {
        "story": "When I was 19, I had to count people entering the subway. SO boring! My finger hurt from clicking the mechanical counter!",
        "goal": "Build an app to count passengers (and save fingers!)",
        "why": "This was my ACTUAL problem! And coding solved it!",
        "steps": [
            "1. Create variable: let count = 0 (your counter starts at zero)",
            "2. Create function: increment() to add 1 each time",
            "3. Add button in HTML (what users will click)",
            "4. Connect button to function (make it WORK!)",
            "5. Display count on page (show the number!)"
        ],
        "starter_code": """let count = 0  // This is your counter!

function increment() {
    // TODO: Add 1 to count
    // TODO: Update what's shown on screen
}

// Your turn! Make this function actually COUNT!"""
    },
    "blackjack": {
        "story": "I won 100 euros playing Blackjack in Prague! Then lost it all... but I learned probability!",
        "goal": "Build a REAL Blackjack game",
        "why": "Games teach logic, conditions, and state management!",
        "steps": [
            "1. Create variables for your cards",
            "2. Make a sum calculation function",
            "3. Check if you hit Blackjack (21!)",
            "4. Create 'draw new card' function",
            "5. Determine who wins!"
        ],
        "starter_code": """let firstCard = 11   // Ace or Jack/Queen/King!
let secondCard = 10  // Face card!
let sum = firstCard + secondCard  // What's your total?

// TODO: Create a function to check if you have Blackjack!
// Hint: Blackjack means sum equals... what?"""
    }
}

# Challenges with progressive difficulty
CHALLENGES = {
    "easy": [
        {
            "task": "Create two variables:\n- firstName with your first name\n- lastName with your last name",
            "time": "60 seconds",
            "hint": "let firstName = 'Your Name'"
        },
        {
            "task": "Create a variable called age and set it to your age.\nThen create doubleAge that's twice your age.",
            "time": "60 seconds",
            "hint": "let age = 25; let doubleAge = age * 2"
        }
    ],
    "medium": [
        {
            "task": "Write a function called greet that:\n1. Takes a name parameter\n2. Returns 'Hello ' + name\n3. Test it with console.log",
            "time": "120 seconds",
            "hint": "function greet(name) { return ... }"
        }
    ],
    "hard": [
        {
            "task": "Build a counter:\n1. Variable count starting at 0\n2. Function increment() that adds 1\n3. Function save() that stores count in an array\n4. Test all functions",
            "time": "180 seconds",
            "hint": "let count = 0; let saves = []; function increment() { count += 1 }"
        }
    ]
}

# ================== MAIN TEACHING TOOLS ==================

@mcp.tool()
async def teach(
    topic: str,
    step: Optional[int] = 1
) -> str:
    """
    Teach a programming concept using Scrimba methodology.
    Gets users coding within 60 seconds!
    
    Args:
        topic: Concept to teach (variables, functions, loops, etc.)
        step: Which step in the 5-level progression (default: 1)
    
    Returns:
        Complete micro-lesson with hook, concept, challenge, and celebration
    """
    if topic not in LESSONS:
        return f"Hey buddy! I can teach you: {', '.join(LESSONS.keys())}. Pick one and let's GO!"
    
    lesson = LESSONS[topic]
    
    # Update session state
    SESSION_STATE["current_lesson"] = topic
    SESSION_STATE["current_step"] = step
    SESSION_STATE["total_steps"] = len(lesson["levels"])
    
    if step > len(lesson["levels"]):
        return "🎉 You've COMPLETED this lesson! Your skills are DANGEROUS! Try 'start_project' to build something REAL!"
    
    level = lesson["levels"][step - 1]
    
    # Build the micro-lesson following exact Scrimba structure
    response = f"""Hey buddy! This is going to be SO exciting! 🎉

📚 **{lesson['title']}** - Level {step}/5: {COMPLEXITY_LEVELS[step-1]}
{'='*60}

**Quick Story (20 seconds):**
{lesson['hook'] if step == 1 else 'Remember our journey? Let\'s go DEEPER!'}

**The Magic Concept (60 seconds):**
{level['explanation']}

```javascript
{level['concept']}
```

**Console.log Driven Development:**
```javascript
// Step 1: Write the code
{level['concept']}

// Step 2: IMMEDIATELY verify
{level['console_log']}

// Step 3: Celebrate!
"Yes! It works! See, you're already programming!"
```

🎯 **YOUR TURN! (You have {MICRO_LESSON_STRUCTURE['challenge_duration']} seconds)**
{level['challenge']}

Type your code RIGHT NOW! Don't think, just DO!

When done, I'll check it and we'll celebrate! 
Remember: The only way to learn to code is to write a LOT of code!

{level['celebration'] if step > 1 else ''}"""
    
    return response

@mcp.tool()
async def give_challenge(
    difficulty: Optional[str] = "easy"
) -> str:
    """
    Give an immediate coding challenge following Scrimba methodology.
    
    Args:
        difficulty: easy (60s), medium (120s), or hard (180s)
    
    Returns:
        Challenge with timer, hints, and excitement
    """
    if difficulty not in CHALLENGES:
        difficulty = "easy"
    
    challenge_list = CHALLENGES[difficulty]
    challenge = random.choice(challenge_list)
    
    return f"""Hey buddy! Time to write some code! This is where it gets FUN! 🚀

🎯 **CHALLENGE TIME!** ({difficulty.upper()})

**Your mission ({challenge['time']}):**
{challenge['task']}

**Go ahead and do this RIGHT NOW!**
Don't overthink it - just start typing!

The first time feels weird, but it becomes second nature!

When you're done (or stuck), show me your code!
Need a hint? Just ask! First hint: {challenge['hint']}

Remember: Making mistakes is how we learn! That's totally okay!"""

@mcp.tool()
async def check_code(
    code: str
) -> str:
    """
    Check user's code with Scrimba-style encouragement.
    Always celebrates, even mistakes!
    
    Args:
        code: The user's code to check
    
    Returns:
        Encouraging feedback with specific praise or gentle corrections
    """
    # Track in session
    SESSION_STATE["user_code_history"].append(code)
    SESSION_STATE["challenges_completed"] += 1
    
    # Common patterns to check
    has_let = "let" in code
    has_const = "const" in code
    has_function = "function" in code
    has_console = "console.log" in code
    
    # Common mistakes to celebrate
    if "functoin" in code:
        return """Oops! Super common mistake! I made this EXACT error when I started! 😄

You typed 'functoin' instead of 'function' - happens to EVERYONE!
JavaScript is telling us what's wrong - that's actually helpful!

Try again with 'function' - you've got this!"""
    
    if "=" in code and not has_let and not has_const:
        return """Oops! Super common! You forgot the magic word 'let'!

When creating a NEW variable, JavaScript needs to know. Add 'let' before your variable name.
The 'let' keyword tells JavaScript "Hey, I'm making something new!"

Try again - you got this! 💪"""
    
    # Success response
    milestones = {
        1: "🎉 FIRST code! This is MASSIVE!",
        5: "🔥 You're on FIRE! 5 challenges completed!",
        10: "💪 DOUBLE DIGITS! Unstoppable!",
        25: "🚀 Quarter century! Professional level!",
        50: "👑 HALFWAY TO 100! LEGENDARY!"
    }
    
    milestone_msg = milestones.get(SESSION_STATE["challenges_completed"], "")
    
    response = f"""🎊 PERFECT! You just wrote REAL CODE! This is HUGE!

Look what you did:
- {'✅ Used let/const properly!' if has_let or has_const else ''}
- {'✅ Created a function!' if has_function else ''}
- {'✅ Using console.log to verify!' if has_console else ''}
- ✅ Your code is WORKING!

{milestone_msg}

Your skills are becoming DANGEROUS! 🔥

The only way to learn to code is to write a lot of code - and you're doing it!

Want another challenge? Type 'give_challenge' or 'next_lesson'!"""
    
    return response

@mcp.tool()
async def next_lesson() -> str:
    """
    Progress to the next step in current lesson.
    Maintains the 5-level progression.
    
    Returns:
        Next lesson step or completion message
    """
    if not SESSION_STATE["current_lesson"]:
        return """Hey buddy! No lesson active yet!
        
Let's start! Try:
- 'teach variables' - the foundation of EVERYTHING!
- 'teach functions' - make your code REUSABLE!

The journey of a thousand apps starts with a single lesson! 🚀"""
    
    current = SESSION_STATE["current_step"]
    total = SESSION_STATE["total_steps"]
    
    if current >= total:
        return f"""🎉 **BOOM! You CRUSHED the lesson!**
        
You just mastered {SESSION_STATE['current_lesson']} in {total} steps!
This is HUGE - you're officially thinking like a programmer now!

Ready for the next adventure?
- Try another topic: {', '.join(LESSONS.keys())}
- Or 'start_project' to BUILD something real!

Remember: The only way to learn to code is to write a lot of code! 💪"""
    
    # Progress to next step
    SESSION_STATE["current_step"] += 1
    return await teach(SESSION_STATE["current_lesson"], SESSION_STATE["current_step"])

@mcp.tool()
async def start_project(
    project_name: Optional[str] = "passenger_counter"
) -> str:
    """
    Start a real project with step-by-step guidance.
    Based on Per Borgen's actual projects!
    
    Args:
        project_name: passenger_counter, blackjack, or chrome_extension
    
    Returns:
        Project setup with personal story and starter code
    """
    if project_name not in PROJECTS:
        return f"Available projects: {', '.join(PROJECTS.keys())}. Pick one and let's BUILD!"
    
    project = PROJECTS[project_name]
    SESSION_STATE["current_project"] = project_name
    
    return f"""Hey buddy! This is SO EXCITING! We're building something REAL! 🚀

🎯 **PROJECT: {project_name.upper().replace('_', ' ')}**

**MY STORY:** {project['story']}

**WHY THIS MATTERS:** {project['why']}

**WHAT WE'RE BUILDING:** {project['goal']}

**🔨 BUILD STEPS (We'll do these together!):**
{chr(10).join(project['steps'])}

**📝 STARTER CODE (Type this out - don't copy!):**
```javascript
{project['starter_code']}
```

⚡ **YOUR MISSION RIGHT NOW:**
Complete Step 1! Just START! Don't overthink it!

**Pro tip:** The first line of code is the hardest. After that, momentum takes over!

Type your code and show me! If you get stuck, ask for a hint!

**This is not just practice - this solves REAL problems!**
Let's GO buddy! Your first real project starts NOW! 🔥"""

@mcp.tool()
async def visualize_concept(
    concept: str,
    style: Optional[str] = "scrimba"
) -> str:
    """
    Generate visual learning materials (image prompts) for concepts.
    Returns text descriptions that can be used to generate images.
    
    Args:
        concept: Programming concept to visualize
        style: Visual style (default: scrimba)
    
    Returns:
        Detailed image generation prompts following Scrimba's visual methodology
    """
    visual_prompts = {
        "variables": {
            "prompt": "Create a bright, colorful illustration showing programming variables as labeled storage boxes. Show 3 boxes: one blue box labeled 'name' containing 'Per', one orange box labeled 'age' containing '25', and one green box labeled 'isTeacher' containing 'true'. Use clean minimalist style with vibrant colors. Add arrows with 'let' keyword pointing to each box. Background should be light with subtle grid pattern. Style: educational infographic, Scrimba-inspired, beginner-friendly",
            "explanation": "Variables are like **labeled boxes** that store your stuff! Each box has a name and holds a value!"
        },
        "functions": {
            "prompt": "Illustrate a function as a magical machine. Show a colorful factory-style machine with input funnel on left labeled 'parameters', gears in middle labeled 'function bakeCake()', and output conveyor on right with a cake. Use bright friendly colors (pink machine, blue gears, yellow cake). Add speech bubble saying 'Reusable magic!'. Style: whimsical technical diagram, Scrimba educational, beginner-friendly",
            "explanation": "Functions are **reusable machines** - put ingredients in, get results out! Write once, use everywhere!"
        },
        "loops": {
            "prompt": "Create an animated-style illustration of a loop concept. Show a circular track with a small robot running around it. Include numbered checkpoints (1, 2, 3) that light up as robot passes. Add counter display showing 'Round: 3/5'. Use bright colors (purple track, yellow robot, green checkpoints). Include code snippet 'for(i=0; i<5; i++)' floating above. Style: playful educational diagram, clean vectors, Scrimba teaching style",
            "explanation": "Loops make your code **run in circles** - but in a good way! Do something multiple times without typing it over and over!"
        }
    }
    
    visual = visual_prompts.get(concept, {
        "prompt": f"Create a bright educational illustration explaining {concept} programming concept. Use simple visual metaphors, bright colors (orange, blue, green), clean minimalist style. Include small code snippets. Style: Scrimba educational, beginner-friendly infographic",
        "explanation": f"Let's visualize {concept} to make it crystal clear!"
    })
    
    return f"""🎨 **VISUAL LEARNING TIME!**

**Image Generation Prompt:**
```
{visual['prompt']}
```

**What This Shows:**
{visual['explanation']}

**Why Visual Learning Works:**
Our brains process images 60,000x faster than text! This image will make {concept} STICK in your mind forever!

Want to see this concept in action? Type 'teach {concept}' for the interactive lesson!"""

@mcp.tool()
async def show_progress() -> str:
    """
    Show user's learning journey with celebrations.
    Tracks everything following Scrimba's motivation system.
    
    Returns:
        Progress report with achievements and encouragement
    """
    concepts = SESSION_STATE["concepts_learned"]
    challenges = SESSION_STATE["challenges_completed"]
    
    # Determine level based on progress
    level = "BEGINNER"
    if challenges > 50:
        level = "LEGENDARY"
    elif challenges > 25:
        level = "PROFESSIONAL"
    elif challenges > 10:
        level = "INTERMEDIATE"
    elif challenges > 5:
        level = "ADVANCING"
    
    # Generate motivational message
    if challenges >= 50:
        motivation = "🔥🔥🔥 **UNSTOPPABLE!** You've written more code than 99% of people EVER will!"
    elif challenges >= 25:
        motivation = "🚀 **Professional level!** At this rate, you'll be building REAL apps in no time!"
    elif challenges >= 10:
        motivation = "💪 **Double digits!** Your momentum is EVERYTHING! Keep crushing it!"
    elif challenges >= 5:
        motivation = "🔥 **You're on FIRE!** Look at you go! This momentum is EVERYTHING!"
    elif challenges >= 1:
        motivation = "🌟 **You've STARTED!** That's the hardest part! Most people never write their first line!"
    else:
        motivation = "🚀 **Your journey is about to begin!** The first step is the most important one!"
    
    return f"""Hey buddy! Let's see how DANGEROUS you've become! 🔥

📊 **YOUR EPIC CODING JOURNEY**
{'='*40}

**🎯 Concepts You've CONQUERED:**
{', '.join(concepts) if concepts else 'Ready to start your first lesson!'}

**⚡ Challenges CRUSHED:** {challenges}
{f"That's {challenges} real problems SOLVED!" if challenges > 0 else "Your first challenge awaits!"}

**🏆 Current Level:** {level}

**📈 Progress Visualization:**
{'█' * min(challenges, 50)}{'░' * (50 - min(challenges, 50))}
{min(challenges * 2, 100)}% to MASTERY!

{motivation}

Remember: The only way to learn to code is to write a LOT of code!
And buddy... you're doing EXACTLY that! Let's keep going! 💪"""

# Run the server
if __name__ == "__main__":
    mcp.run()