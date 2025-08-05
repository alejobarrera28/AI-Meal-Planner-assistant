# AI Meal Planning Agent - Educational Demo
*RAG + Tool Calls + AI Agents Demonstration*

## 🎓 Educational Purpose

This project demonstrates three key AI concepts using the **real MealRec+ dataset**:

1. **RAG (Retrieval-Augmented Generation)**: Using structured data as knowledge base
2. **Tool Calls**: Structured function interfaces for AI agents  
3. **AI Agents**: Reasoning chains and decision-making patterns

Perfect for lectures on practical AI agent implementation!

## 🏗️ Architecture Overview

```
User Query → AI Agent → Tool Calls → RAG Database → Real MealRec+ Data
     ↓
Agent Reasoning → Recipe Recommendations → Structured Response
```

## 📊 Real Dataset Integration

Uses **actual MealRec+ files**:
- `course_category.txt` - Recipe classifications (17,091 courses)
- `course_fsa.txt` - FSA health scores (lower = healthier)  
- `course_who.txt` - WHO health scores (lower = healthier)
- `meal_course.txt` - Multi-course meal compositions (76,059 meals)

## 🚀 Quick Demo

**Prerequisites**: You need an OpenAI API key
```bash
export OPENAI_API_KEY="your-api-key-here"
python3 src/main.py
```

Example output:
```
🎓 EDUCATIONAL DEMO: RAG + Tool Calls + AI Agents
==============================================================

1️⃣ INITIALIZING RAG DATABASE
🔍 Loading MealRec+ RAG database from: MealRec+/MealRec+H
📊 RAG Database loaded:
   - 17091 recipes indexed
   - 17091 course categories  
   - 76059 meal compositions

2️⃣ SETTING UP TOOL CALLS
🔧 Demo Tool Call: search_healthy_recipes
   Found: 5 recipes
   Reasoning: Retrieved 5 recipes from main courses category with FSA health score ≤ 8.0

3️⃣ INITIALIZING AI AGENT
🤖 AI Agent initialized with LLM capabilities

4️⃣ AGENT REASONING DEMONSTRATIONS
🤖 Agent Test 1: 'I want a healthy main course'
--------------------------------------------------
🎯 Agent Processing: 'I want a healthy main course'
📝 Parsed request: {'categories': ['main'], 'health_preference': 'healthy', 'meal_type': 'single'}
🔧 Tool results: Found 2 relevant data points
📊 Agent made 2 tool calls
🔍 Retrieved 5 recipes from RAG
💭 Reasoning: [LLM-generated reasoning based on health scores and user preferences]
🍽️  Recommended: 1 recipes
   - [LLM-selected recipe based on optimal health scores]
```

## 🔧 Core Components

### 1. RAG Database (`src/data/database.py`)
```python
from data.database import MealRecRAGDatabase

# Loads real MealRec+ dataset files
rag_db = MealRecRAGDatabase()

# Retrieval with filtering
result = rag_db.retrieve_recipes(category=1, max_fsa_score=8.0, limit=10)
```

### 2. Tool Calls (`src/tools/`)
```python
from tools.registry import ToolRegistry

tool_registry = ToolRegistry(rag_db)

# Execute structured function calls
result = tool_registry.execute_tool("filter_courses", criteria={
    "category": "main", 
    "max_fsa_score": 6.0
})
```

### 3. AI Agent (`src/core/chatbot.py`)
```python
from core.chatbot import MealPlanningChatbot

chatbot = MealPlanningChatbot(rag_db, tool_registry, openai_api_key)

# LLM reasoning with tool calls: Query → Tools → Response
chatbot.chat("I want a healthy 3-course meal")
```

## 🎯 Learning Objectives

### RAG Concepts
- Knowledge base construction from structured data
- Semantic retrieval with filtering criteria
- Context-aware information gathering

### Tool Call Patterns  
- Structured function interfaces
- Parameter validation and parsing
- Result formatting for agent consumption

### AI Agent Design
- Request parsing and intent recognition
- Multi-step reasoning chains
- Tool orchestration and decision making
- LLM-powered intelligent reasoning

## 📈 Dataset Statistics

- **17,091 recipes** across 3 categories
- **76,059 meal compositions** showing real user preferences
- **Health scores**: FSA & WHO ratings for every recipe
- **Categories**: 0=Appetizer, 1=Main Course, 2=Dessert

## 🔬 Advanced Features

### Multi-Course Planning
```python
# Chatbot can plan complete meals
chatbot.chat("Plan a healthy 3-course meal")
# Returns: appetizer + main + dessert with health optimization
```

### Health Score Integration
```python
# Real health metrics from nutrition research
fsa_score = 6.2  # Food Standards Agency (lower = healthier)
who_score = 5.8  # World Health Organization (lower = healthier)
```

### Extensible Tool System
```python
# Easy to add new tools to the registry
from tools.base import BaseTool

class NewTool(BaseTool):
    def execute(self, param: str) -> Dict[str, Any]:
        return {"tool": "new_tool", "result": "data"}
```

## 🎪 Lecture Integration

Perfect for demonstrating:

1. **RAG Retrieval**: How agents access structured knowledge
2. **Function Calling**: Structured AI-to-system interfaces
3. **Agent Reasoning**: Decision trees and multi-step planning
4. **Real Data**: Working with actual research datasets
5. **Scalability**: Handling 17k+ recipes efficiently

## ⚡ Technical Implementation

- **LLM-Powered**: Uses OpenAI GPT-4 for intelligent reasoning
- **Real Data**: Actual MealRec+ research dataset
- **Modular Design**: Clear separation of RAG/Tools/Agent
- **Educational Focus**: Extensive logging and reasoning chains
- **API Required**: Requires OpenAI API key for full functionality

## 🔍 Code Structure

```
📁 AI-Meal-Planner-assistant/
├── 📁 src/                    # Main application code
│   ├── 📄 main.py            # Entry point and demo orchestration
│   ├── 📁 core/              # AI chatbot and schemas
│   │   ├── chatbot.py        # LLM-powered meal planning chatbot
│   │   └── schemas.py        # Data validation schemas
│   ├── 📁 data/              # Database and data models
│   │   ├── database.py       # RAG knowledge base (loads MealRec+ data)
│   │   └── models.py         # Data structures (MealRecipe, etc.)
│   ├── 📁 tools/             # Comprehensive tool suite
│   │   ├── registry.py       # Tool registration and execution
│   │   ├── filtering.py      # Course filtering tools
│   │   ├── meal_planning.py  # Meal generation tools
│   │   ├── health.py         # Health analysis tools
│   │   ├── user.py           # User preference tools
│   │   └── analysis.py       # Recipe analysis tools
│   └── 📁 demo/              # Demo and interaction modules
│       ├── examples.py       # Example conversations
│       └── interactive.py    # Interactive demo mode
├── 📁 MealRec+/              # Real dataset files
│   └── 📁 MealRec+H/
│       ├── course_category.txt
│       ├── healthiness/
│       └── meal_course.txt
├── 📄 requirements.txt       # Dependencies
├── 📄 CLAUDE.md             # Development instructions
└── 📄 README.md             # This file
```

---

## 📚 Original MealRec+ Dataset Information

### Citation
If you use this dataset, please cite it in your paper:

**Ming Li, Lin Li, Xiaohui Tao, and Jimmy Xiangji Huang. 2024. MealRec+: A Meal Recommendation Dataset with Meal-Course Affiliation for Personal- ization and Healthiness. In Proceedings of the 47th International ACM SIGIR Conference on Research and Development in Information Retrieval (SIGIR '24), July 14–18, 2024, Washington, DC, USA. ACM, New York, NY, USA, 11 pages. https://doi.org/10.1145/3626772.3657857**

### Contributors
- Ming Li, Wuhan University of Technology, China
- Lin Li, Wuhan University of Technology, China  
- Xiaohui Tao, University of Southern Queensland, Australia
- Jimmy Huang, York University, Canada
