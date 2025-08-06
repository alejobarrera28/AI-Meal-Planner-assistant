# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a **Simple Educational AI Meal Planning Agent** that demonstrates RAG + Tool Calls + AI Agents using the MealRec+ dataset. It's designed for beginner-friendly lectures on practical AI agent implementation.

**Total codebase: ~563 lines across 4 simple files**

## Common Development Commands

This is an educational demo project. The main operations are:

- **Run demo**: `python3 src/main.py` - Complete educational demonstration
- **Test components**: Import individual modules from the `src/` directory

## Dataset Structure

The repository uses a simplified MealRec+ dataset variant:
- `MealRec+H/` - High-density dataset for educational purposes

Contains only essential files:
- **Core data**: course_category.txt, meal_course.txt  
- **Health scores**: course_fsa.txt (in healthiness/ folder)
- **Metadata**: course2index.txt (in meta_data/ folder)

## Simple Python Structure

### Main Entry Point (`src/main.py`) - ~206 lines
- **SimpleMealPlannerBot**: Basic LLM integration with tool calling
- **Examples & Interactive Mode**: Educational demonstrations
- **Prerequisites**: Requires TOGETHER_API_KEY

### Core Components (3 files)
- **src/database.py** (~120 lines): Simple MealRec+ data loading and queries
- **src/tools.py** (~100 lines): 3 essential tools (search, filter, meal planning)
- **src/config.py** (~40 lines): Tool schemas and system prompt

## Available Tools (3 core tools)

1. **search_courses_by_category** - Find appetizers/mains/desserts
2. **filter_healthy_courses** - Find courses with good FSA scores
3. **generate_meal_plan** - Create complete meal plans

## Data Format Notes

- Course categories: {0: appetizers, 1: main dishes, 2: desserts}
- Health scores: Lower FSA scores = healthier recipes
- Database contains 942 real courses and 3,817 meals

## Dependencies

Minimal requirements:
- **openai** (required for LLM functionality)
- Standard library modules only (os, json, random)