# AI Meal Planning Agent
*Educational Demo: RAG + Tool Calls + AI Agents*

## 🎓 What This Project Demonstrates

This is an **educational AI system** that shows how modern AI agents work using **real meal planning data**. Perfect for learning:

1. **RAG (Retrieval-Augmented Generation)** - How AI searches through real data
2. **LLM Tool Calls** - How AI agents use specialized functions  
3. **AI Agent Architecture** - How everything connects together

Uses the **real MealRec+ research dataset** with 17K+ recipes and health scores.

## 🚀 Quick Start

**Prerequisites**: Get a Together.ai API key (cheaper than OpenAI)

```bash
# 1. Set your API key
cp .env.example .env
# Edit .env and add: TOGETHER_API_KEY=your-key-here

# 2. Run the demo
python3 src/main.py
```

## 🏗️ System Flow

```
User: "I want a healthy 3-course meal"
    ↓
📱 AI Agent (LLM) analyzes request
    ↓
🔧 Calls Tools: filter_courses, generate_meal_plan
    ↓
🗃️ Tools query Meal Database (17K recipes)
    ↓
📊 Returns: Appetizer + Main + Dessert with health scores
```

## 📁 Project Structure

### 🔥 **Core Files** (Start Here)
```
src/main.py              # ← ENTRY POINT - Run this!
src/core/chatbot.py      # ← AI Agent brain (LLM + tools)
src/data/database.py     # ← Meal Database (loads real data)
src/tools/registry.py    # ← Tool system (10 specialized tools)
```

### 📂 **Supporting Files**
```
src/tools/
├── filtering.py         # Find recipes by category/health
├── meal_planning.py     # Generate complete meals
├── health.py           # Health score analysis
├── analysis.py         # Recipe recommendations
└── user.py            # User preference tracking

src/demo/
├── examples.py         # Pre-built conversations
└── interactive.py      # Live chat mode
```

### 📊 **Data Files** (Read-Only)
```
MealRec+/MealRec+H/     # Real research dataset
├── course_category.txt  # 17K recipe categories
├── healthiness/        # FSA/WHO health scores
└── meal_course.txt     # 76K meal compositions
```

## 🎯 How It Works

### 1. **Meal Database** loads real data
- 17,091 recipes with health scores
- 76,059 meal combinations from real users
- Categories: Appetizers, Main courses, Desserts

### 2. **Tool Registry** provides 10 specialized functions
- `filter_courses` - Find recipes by criteria
- `generate_meal_plan` - Create complete meals
- `calculate_health_score` - Analyze nutrition
- `swap_for_healthier` - Find better alternatives
- ...and 6 more tools

### 3. **AI Agent** orchestrates everything
- Uses Together.ai LLM (Llama-3-8b by default)
- Analyzes user requests
- Calls appropriate tools
- Returns natural responses

## 🔧 Key Components Deep Dive

### The AI Agent (`src/core/chatbot.py`)
```python
# The brain - decides which tools to use
chatbot = MealPlanningChatbot(meal_db, tool_registry, api_key)
response = chatbot.chat("I want a healthy main course")
```

### The Database (`src/data/database.py`) 
```python
# Loads all 17K recipes from MealRec+ files
meal_db = MealDatabase()
recipes = meal_db.retrieve_recipes(category=1, max_fsa_score=6.0)
```

### The Tools (`src/tools/registry.py`)
```python
# 10 specialized functions the AI can call
tool_registry = ToolRegistry(meal_db)
result = tool_registry.execute_tool("filter_courses", criteria={
    "category": "main",
    "max_fsa_score": 6.0
})
```

## 📈 What You'll Learn

### **RAG Concepts**
- How AI searches through structured data
- Building knowledge bases from real datasets
- Retrieval strategies and filtering

### **Tool Calling Patterns**
- Function schemas for LLMs
- Parameter validation
- Tool orchestration

### **AI Agent Design**
- Request analysis and intent recognition
- Multi-step reasoning
- Combining LLM intelligence with structured data

## 🎪 Demo Modes

**Example Conversations** - See pre-built interactions
```bash
# Choose option 1 when prompted
python3 src/main.py
```

**Interactive Mode** - Chat with the AI agent
```bash
# Choose option 2 when prompted
python3 src/main.py
```

## 💡 Technical Details

- **LLM**: Together.ai (meta-llama/Llama-3-8b-chat-hf)
- **Dataset**: Real MealRec+ research data (17K+ recipes)
- **Architecture**: Modular design with clear separation
- **Tool System**: 10 specialized functions
- **Health Scores**: FSA & WHO nutritional ratings

## 🔍 File Importance Guide

| Priority | Files | Purpose |
|----------|-------|---------|
| 🔥 **ESSENTIAL** | `src/main.py`, `src/core/chatbot.py` | Entry point & AI brain |
| 🔥 **ESSENTIAL** | `src/data/database.py`, `src/tools/registry.py` | Data & tool system |
| 📘 **IMPORTANT** | `src/tools/*.py` | Individual tool implementations |
| 📘 **IMPORTANT** | `src/demo/*.py` | Demo modes & examples |
| 📂 **SUPPORTING** | `src/data/models.py`, `src/core/schemas.py` | Data structures |
| 📊 **DATA** | `MealRec+/` | Research dataset (read-only) |

## 🎓 Educational Use

Perfect for teaching:
- **AI Engineering** - Real-world agent architecture
- **RAG Systems** - Knowledge base construction
- **LLM Integration** - Function calling patterns
- **Data Science** - Working with research datasets

---

## 📚 Dataset Citation

This project uses the MealRec+ research dataset:

**Ming Li, Lin Li, Xiaohui Tao, and Jimmy Xiangji Huang. 2024. MealRec+: A Meal Recommendation Dataset with Meal-Course Affiliation for Personalization and Healthiness. In Proceedings of the 47th International ACM SIGIR Conference on Research and Development in Information Retrieval (SIGIR '24), July 14–18, 2024, Washington, DC, USA.**