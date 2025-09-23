# pyass🍑/src/pyass/engines/quizzer.py

import random
from typing import List
from dataclasses import dataclass
from ..core.models import SlangFilter
from ..core.slangdb import get_slang_db

@dataclass
class QuizResult:
    score: int
    total: int
    slang_iq: int  # 0-200 scale
    feedback: str

@dataclass
class QuizQuestion:
    term: str
    correct_definition: str
    choices: List[str]
    difficulty: int  # 1-5

class Quizzer:
    """
    Adaptive slang quiz engine.
    Tracks user performance, adjusts difficulty, calculates Slang IQ.
    """

    def __init__(self):
        self.db = get_slang_db()
        self.session_stats = {
            "correct": 0,
            "total": 0,
            "difficulty_sum": 0,
            "current_difficulty": 3,
            "streak": 0,
            "longest_streak": 0
        }

    def generate_question(self, difficulty: int = 3) -> QuizQuestion:
        """Generate a quiz question at given difficulty level (1-5)"""
        # Filter by popularity (higher difficulty = lower popularity = rarer slang)
        min_pop = max(20, 100 - (difficulty * 20))
        max_pop = min(100, 100 - ((difficulty - 1) * 15))

        entries = self.db.search(SlangFilter(
            min_popularity=min_pop,
            max_popularity=max_pop,
            exclude_offensive=True
        ))

        if not entries:
            # Fallback
            entries = self.db.search(SlangFilter(exclude_offensive=True))

        if not entries:
            raise ValueError("No slang entries available for quiz")

        entry = random.choice(entries)

        # Get 3 fake definitions
        all_defs = [e.definition for e in self.db.entries if e.term != entry.term]
        fake_defs = random.sample(all_defs, min(3, len(all_defs)))
        choices = fake_defs + [entry.definition]
        random.shuffle(choices)

        return QuizQuestion(
            term=entry.term,
            correct_definition=entry.definition,
            choices=choices,
            difficulty=difficulty
        )

    def start_quiz(self, num_questions: int = 5, adaptive: bool = True) -> QuizResult:
        """Start a quiz session"""
        self.session_stats = {
            "correct": 0,
            "total": 0,
            "difficulty_sum": 0,
            "current_difficulty": 3,
            "streak": 0,
            "longest_streak": 0
        }

        print("🍑 WELCOME TO THE PYASS QUIZ 🍑")
        print("Prove you're not an NPC!\n")

        for i in range(num_questions):
            difficulty = self.session_stats["current_difficulty"] if adaptive else 3
            question = self.generate_question(difficulty)

            print(f"Q{i+1} (Difficulty {question.difficulty}/5): What does '{question.term}' mean?")
            for j, choice in enumerate(question.choices):
                print(f"  {j+1}. {choice}")

            try:
                answer = int(input("Your choice (1-4): ")) - 1
                if 0 <= answer < len(question.choices) and question.choices[answer] == question.correct_definition:
                    print("✅ SLAYYYY\n")
                    self.session_stats["correct"] += 1
                    self.session_stats["streak"] += 1
                    if self.session_stats["streak"] > self.session_stats["longest_streak"]:
                        self.session_stats["longest_streak"] = self.session_stats["streak"]

                    # Increase difficulty if correct
                    if adaptive and self.session_stats["current_difficulty"] < 5:
                        self.session_stats["current_difficulty"] += 1
                else:
                    print(f"❌ NPC behavior. Correct: {question.correct_definition}\n")
                    self.session_stats["streak"] = 0
                    # Decrease difficulty if wrong
                    if adaptive and self.session_stats["current_difficulty"] > 1:
                        self.session_stats["current_difficulty"] -= 1

                self.session_stats["total"] += 1
                self.session_stats["difficulty_sum"] += question.difficulty

            except (ValueError, IndexError):
                print("Invalid input. Skipping 😒\n")
                self.session_stats["streak"] = 0

        return self.get_result()

    def get_result(self) -> QuizResult:
        """Get final quiz result"""
        total = self.session_stats["total"]
        correct = self.session_stats["correct"]
        avg_difficulty = self.session_stats["difficulty_sum"] / total if total > 0 else 1
        longest_streak = self.session_stats["longest_streak"]

        # Calculate Slang IQ (0-200)
        # Base: percentage correct * 100
        # Bonus: average difficulty (max +50), streak bonus (max +50)
        slang_iq = int((correct / total * 100) if total > 0 else 0)
        slang_iq += int((avg_difficulty - 1) * 12.5)  # Max +50 for diff 5
        slang_iq += min(longest_streak * 10, 50)      # Max +50 for streak 5+

        slang_iq = min(max(slang_iq, 0), 200)

        # Feedback
        if slang_iq >= 180:
            feedback = "👑 SUPREME VIBES — You are the main character of the internet"
        elif slang_iq >= 150:
            feedback = "💅 SLAY QUEEN — Your rizz is immaculate"
        elif slang_iq >= 120:
            feedback = "🙂 NPC WITH POTENTIAL — Touch grass, then come back"
        elif slang_iq >= 80:
            feedback = "🤖 BASIC SIMP — You need a full vibe transfusion"
        else:
            feedback = "💀 UNALIVED INSIDE — Seek immediate glazing"

        return QuizResult(
            score=correct,
            total=total,
            slang_iq=slang_iq,
            feedback=feedback
        )

    def get_daily_challenge(self) -> QuizQuestion:
        """Get one hard question for daily challenge"""
        return self.generate_question(difficulty=5)

    def reset_stats(self):
        """Reset session stats"""
        self.session_stats = {
            "correct": 0,
            "total": 0,
            "difficulty_sum": 0,
            "current_difficulty": 3,
            "streak": 0,
            "longest_streak": 0
        }
