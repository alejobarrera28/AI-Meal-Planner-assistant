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

```bash
python3 meal_rag_agent.py
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
🤖 AI Agent initialized with rule-based reasoning

4️⃣ AGENT REASONING DEMONSTRATIONS
🤖 Agent Test 1: 'I want a healthy main course'
--------------------------------------------------
🎯 Agent Processing: 'I want a healthy main course'
📝 Parsed request: {'categories': ['main'], 'health_preference': 'healthy', 'meal_type': 'single'}
🔧 Tool results: Found 2 relevant data points
📊 Agent made 2 tool calls
🔍 Retrieved 5 recipes from RAG
💭 Reasoning: Used rule-based selection to find 1 recipes matching your healthy health preference  
🍽️  Recommended: 1 recipes
   - Grilled Herb Chicken (main, Health: FSA 6.2, WHO 5.8)
```

## 🔧 Core Components

### 1. RAG Database (`MealRecRAGDatabase`)
```python
# Loads real MealRec+ dataset files
rag_db = MealRecRAGDatabase("MealRec+/MealRec+H")

# Retrieval with filtering
result = rag_db.retrieve_recipes(
    category=1,  # main courses
    max_fsa_score=8.0,  # healthy threshold
    limit=10
)
```

### 2. Tool Calls (`MealPlanningTools`)
```python
tools = MealPlanningTools(rag_db)

# Structured function calls
recipes = tools.search_healthy_recipes(
    category="main", 
    health_preference="healthy"
)

# Health analysis
metrics = tools.calculate_health_metrics(["Grilled Herb Chicken"])
```

### 3. AI Agent (`MealPlanningAgent`)
```python
agent = MealPlanningAgent(rag_db, openai_api_key="optional")

# Reasoning chain: Parse → Tools → Reasoning → Response
result = agent.plan_meal("I want a healthy 3-course meal")
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
- Fallback strategies (rule-based vs LLM)

## 📈 Dataset Statistics

- **17,091 recipes** across 3 categories
- **76,059 meal compositions** showing real user preferences
- **Health scores**: FSA & WHO ratings for every recipe
- **Categories**: 0=Appetizer, 1=Main Course, 2=Dessert

## 🔬 Advanced Features

### Multi-Course Planning
```python
# Agent can plan complete meals
result = agent.plan_meal("Plan a healthy 3-course meal")
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
# Easy to add new tools
def new_tool(self, param: str) -> Dict[str, Any]:
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

- **Pure Python**: No complex dependencies
- **Real Data**: Actual MealRec+ research dataset
- **Modular Design**: Clear separation of RAG/Tools/Agent
- **Educational Focus**: Extensive logging and reasoning chains
- **LLM Optional**: Works with or without OpenAI API

## 🔍 Code Structure

```
meal_rag_agent.py
├── MealRecipe (dataclass)      # Structured data representation
├── MealRecRAGDatabase          # RAG knowledge base  
├── MealPlanningTools           # Tool call interfaces
├── MealPlanningAgent           # AI agent with reasoning
└── demo_educational_system()   # Complete demonstration
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
