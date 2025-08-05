# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is the MealRec+ dataset repository - a meal recommendation dataset with meal-course affiliation for personalization and healthiness evaluation. The repository contains two dataset variants (MealRec+H and MealRec+L) along with Python utilities for data loading and healthiness evaluation.

## Common Development Commands

Since this is a research dataset repository, there are no build/test commands. The main operations are:

- **Load data**: `python3 MealRec+/data_load.py` - Loads and processes the dataset files
- **Evaluate healthiness metrics**: `python3 healthiness_eval.py` - Evaluates FSA/WHO healthiness scores and ranking exposure

## Dataset Structure

The repository contains two main dataset variants:
- `MealRec+H/` - High-density dataset (0.77% user-meal interaction density)
- `MealRec+L/` - Low-density dataset (0.17% user-meal interaction density)

Each dataset contains:
- **Interaction data**: user-course, user-meal (train/tune/test splits)
- **Affiliation data**: meal-course, course-category mappings
- **Healthiness data**: FSA and WHO scores for users, meals, and courses
- **Metadata**: course information, user mappings

## Key Python Components

### Data Loading (`MealRec+/data_load.py`)
- **BasicDataset**: Base class for all dataset types
- **MealTrainDataset/MealTestDataset**: Handle user-meal interactions for training/testing
- **ItemDataset**: Handles user-course interactions 
- **AffiliationDataset**: Manages meal-course affiliations
- **CategoryDataset**: Manages course-category mappings
- **get_dataset()**: Main function to load all dataset components

### Healthiness Evaluation (`healthiness_eval.py`)
- **NutritionMetric**: Calculates FSA/WHO healthiness scores and ranking exposure fairness
- **NutritionData()**: Loads healthiness score data from files

## Data Format Notes

- All interaction files use tab-separated format: `[index1]\t[index2]`
- Healthiness files contain one score per line (line index = entity index)
- Category mapping: {0: appetizers, 1: main dishes, 2: desserts}
- Dataset sizes are hardcoded in BasicDataset.__load_data_size()

## Dependencies

The code requires:
- PyTorch
- NumPy  
- SciPy (for sparse matrices)