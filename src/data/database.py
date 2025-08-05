"""
Meal Database - Knowledge Base for meal planning
Loads and queries the MealRec+ dataset
"""

import os
from typing import Dict, List, Optional, Any
from .models import MealRecipe, QueryResult


class MealDatabase:
    """Knowledge Base using MealRec+ dataset files"""

    def __init__(self, data_path: str = "MealRec+/MealRec+H"):
        self.data_path = data_path
        print(f"🔍 Loading MealRec+ database from: {data_path}")

        # Load ALL real dataset components
        self.course_categories = self._load_course_categories()
        self.course_fsa_scores = self._load_health_scores("fsa")
        self.course_who_scores = self._load_health_scores("who")
        self.meal_course_mapping = self._load_meal_course_mapping()
        self.course_to_index = self._load_course_to_index()
        self.user_course_interactions = self._load_user_course_interactions()
        self.user_meal_interactions = self._load_user_meal_interactions()

        self.real_course_metadata = None

        # Create structured knowledge base using ONLY real data
        self.recipes_db = self._build_real_recipe_database()

        print(f"📊 Database loaded: {len(self.recipes_db)} recipes indexed")
        print(f"   - {len(self.course_categories)} course categories")
        print(f"   - {len(self.meal_course_mapping)} meal compositions")
        print(f"   - {len(self.user_course_interactions)} user-course interactions")
        print(f"   - Course metadata: Not available (using course IDs only)")

    def _load_course_categories(self) -> Dict[int, int]:
        """Load course category mapping from real data"""
        categories = {}
        file_path = os.path.join(self.data_path, "course_category.txt")

        try:
            with open(file_path, "r") as f:
                for line in f:
                    parts = line.strip().split("\t")
                    if len(parts) >= 2:
                        course_idx = int(parts[0])
                        category = int(parts[1])
                        categories[course_idx] = category
        except Exception as e:
            print(f"⚠️  Error loading categories: {e}")

        return categories

    def _load_health_scores(self, score_type: str) -> Dict[int, float]:
        """Load FSA or WHO health scores from real data"""
        scores = {}
        file_path = os.path.join(
            self.data_path, "healthiness", f"course_{score_type}.txt"
        )

        try:
            with open(file_path, "r") as f:
                for idx, line in enumerate(f):
                    score = float(line.strip())
                    scores[idx] = score
        except Exception as e:
            print(f"⚠️  Error loading {score_type} scores: {e}")

        return scores

    def _load_meal_course_mapping(self) -> Dict[int, List[int]]:
        """Load meal-to-course relationships from real data"""
        mapping = {}
        file_path = os.path.join(self.data_path, "meal_course.txt")

        try:
            with open(file_path, "r") as f:
                for line in f:
                    parts = line.strip().split("\t")
                    if len(parts) >= 2:
                        meal_idx = int(parts[0])
                        course_idx = int(parts[1])
                        if meal_idx not in mapping:
                            mapping[meal_idx] = []
                        mapping[meal_idx].append(course_idx)
        except Exception as e:
            print(f"⚠️  Error loading meal-course mapping: {e}")

        return mapping

    def _load_course_to_index(self) -> Dict[int, int]:
        """Load course ID to index mapping from real data"""
        mapping = {}
        file_path = os.path.join(self.data_path, "meta_data", "course2index.txt")

        try:
            with open(file_path, "r") as f:
                for line in f:
                    parts = line.strip().split("\t")
                    if len(parts) >= 2:
                        course_id = int(parts[0])
                        course_idx = int(parts[1])
                        mapping[course_id] = course_idx
        except Exception as e:
            print(f"⚠️  Error loading course-to-index mapping: {e}")

        return mapping

    def _load_user_course_interactions(self) -> List[tuple]:
        """Load user-course interactions from real data"""
        interactions = []
        file_path = os.path.join(self.data_path, "user_course.txt")

        try:
            with open(file_path, "r") as f:
                for line in f:
                    parts = line.strip().split("\t")
                    if len(parts) >= 2:
                        user_idx = int(parts[0])
                        course_idx = int(parts[1])
                        interactions.append((user_idx, course_idx))
        except Exception as e:
            print(f"⚠️  Error loading user-course interactions: {e}")

        return interactions

    def _load_user_meal_interactions(self) -> Dict[str, List[tuple]]:
        """Load user-meal interactions from real data (train/test/tune)"""
        interactions = {}

        for split in ["train", "test", "tune"]:
            file_path = os.path.join(self.data_path, f"user_meal_{split}.txt")
            interactions[split] = []

            try:
                with open(file_path, "r") as f:
                    for line in f:
                        parts = line.strip().split("\t")
                        if len(parts) >= 2:
                            user_idx = int(parts[0])
                            meal_idx = int(parts[1])
                            interactions[split].append((user_idx, meal_idx))
            except Exception as e:
                print(f"⚠️  Error loading user-meal {split} interactions: {e}")

        return interactions

    def _build_real_recipe_database(self) -> Dict[int, MealRecipe]:
        """Build recipe database using MealRec+ data"""
        recipes = {}

        for course_idx in self.course_categories.keys():
            category = self.course_categories[course_idx]

            # Find real course ID from course2index mapping
            course_id = None
            for real_id, idx in self.course_to_index.items():
                if idx == course_idx:
                    course_id = real_id
                    break

            # Use course ID as name to maintain authenticity
            course_name = f"Course_{course_id}" if course_id else f"Course_{course_idx}"

            # Find meal affiliations from real data
            meal_affiliations = [
                meal_idx
                for meal_idx, courses in self.meal_course_mapping.items()
                if course_idx in courses
            ]

            recipe = MealRecipe(
                course_index=course_idx,
                course_name=course_name,
                category=category,
                fsa_health_score=self.course_fsa_scores.get(course_idx, 8.0),
                who_health_score=self.course_who_scores.get(course_idx, 7.0),
                meal_affiliations=meal_affiliations,
            )
            recipes[course_idx] = recipe

        return recipes

    def retrieve_recipes(
        self,
        category: Optional[int] = None,
        max_fsa_score: Optional[float] = None,
        limit: int = 10,
    ) -> QueryResult:
        """Find relevant recipes based on criteria"""

        matching_recipes = []

        for recipe in self.recipes_db.values():
            # Category filter
            if category is not None and recipe.category != category:
                continue

            # Health score filter (lower is healthier)
            if max_fsa_score is not None and recipe.fsa_health_score > max_fsa_score:
                continue

            matching_recipes.append(recipe)

        # Sort by health scores (lower is better)
        matching_recipes.sort(key=lambda r: r.fsa_health_score + r.who_health_score)

        # Limit results
        limited_recipes = matching_recipes[:limit]

        # Generate reasoning
        category_names = {0: "appetizers", 1: "main courses", 2: "desserts"}
        reasoning = f"Retrieved {len(limited_recipes)} recipes"
        if category is not None:
            reasoning += f" from {category_names.get(category, 'unknown')} category"
        if max_fsa_score is not None:
            reasoning += f" with FSA health score ≤ {max_fsa_score}"
        reasoning += f". Sorted by healthiness using real FSA/WHO scores."

        return QueryResult(
            recipes=limited_recipes,
            reasoning=reasoning,
            total_found=len(matching_recipes),
        )

    def get_real_data_summary(self) -> Dict[str, Any]:
        """Get summary of all real data loaded"""
        return {
            "total_courses": len(self.course_categories),
            "total_meals": len(self.meal_course_mapping),
            "user_course_interactions": len(self.user_course_interactions),
            "user_meal_train": len(self.user_meal_interactions.get("train", [])),
            "user_meal_test": len(self.user_meal_interactions.get("test", [])),
            "user_meal_tune": len(self.user_meal_interactions.get("tune", [])),
            "has_course_metadata": False,
            "course_id_range": (
                f"{min(self.course_to_index.keys())}-{max(self.course_to_index.keys())}"
                if self.course_to_index
                else "N/A"
            ),
            "health_scores_available": len(self.course_fsa_scores) > 0
            and len(self.course_who_scores) > 0,
        }
