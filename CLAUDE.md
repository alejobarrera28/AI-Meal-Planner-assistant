# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is an **Educational AI Meal Planning Agent** that demonstrates RAG + Tool Calls + AI Agents using the MealRec+ dataset. It's designed for lectures on practical AI agent implementation.

## Common Development Commands

This is an educational demo project. The main operations are:

- **Run demo**: `python3 src/main.py` - Complete educational demonstration
- **Test components**: Import individual modules from the `src/` directory

## Dataset Structure

The repository uses a simplified MealRec+ dataset variant:
- `MealRec+H/` - High-density dataset for educational purposes

Contains only essential files:
- **Core data**: course_category.txt, meal_course.txt  
- **Health scores**: course_fsa.txt, course_who.txt (in healthiness/ folder)
- **Metadata**: course2index.txt (in meta_data/ folder)

## Key Python Components

### Educational Demo (`src/main.py`)
- **Main entry point**: Complete RAG + Tool Calls + AI Agents demonstration
- **Prerequisites**: Requires OpenAI API key

### Core Modules
- **src/data/**: Database and data models for MealRec+ data
- **src/tools/**: Comprehensive tool suite for AI agents
- **src/core/**: AI chatbot with LLM-powered reasoning
- **src/demo/**: Interactive and example demonstrations

## Data Format Notes

- Course categories: {0: appetizers, 1: main dishes, 2: desserts}
- Health scores: Lower FSA/WHO scores = healthier recipes
- All files use tab-separated format where applicable

## Dependencies

The code requires:
- **openai** (required for LLM functionality)
- Standard library modules only (os, json, typing, dataclasses)