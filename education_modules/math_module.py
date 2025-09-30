"""
Math Education Module for Laura-bot Personal Learning Assistant
Provides structured mathematics content with graded difficulty levels
"""

import random
from typing import Dict, List, Any, Tuple

class MathModule:
    def __init__(self):
        self.topics = {
            "Arithmetic": {
                "difficulty_1": {
                    "concepts": ["Addition", "Subtraction", "Basic Multiplication", "Basic Division"],
                    "examples": [
                        {"problem": "5 + 3", "solution": "8", "explanation": "Add the two numbers together"},
                        {"problem": "10 - 4", "solution": "6", "explanation": "Subtract the second number from the first"},
                        {"problem": "3 × 4", "solution": "12", "explanation": "Multiply 3 by 4 to get 12"},
                        {"problem": "12 ÷ 3", "solution": "4", "explanation": "Divide 12 by 3 to get 4"}
                    ]
                },
                "difficulty_2": {
                    "concepts": ["Multi-digit Addition", "Multi-digit Subtraction", "Times Tables", "Long Division"],
                    "examples": [
                        {"problem": "247 + 186", "solution": "433", "explanation": "Add column by column from right to left"},
                        {"problem": "512 - 247", "solution": "265", "explanation": "Subtract column by column, borrowing when needed"},
                        {"problem": "7 × 8", "solution": "56", "explanation": "From times tables: 7 × 8 = 56"},
                        {"problem": "144 ÷ 12", "solution": "12", "explanation": "How many 12s go into 144? Answer: 12"}
                    ]
                }
            },
            "Algebra": {
                "difficulty_1": {
                    "concepts": ["Variables", "Simple Equations", "Basic Substitution"],
                    "examples": [
                        {"problem": "x + 5 = 12, find x", "solution": "x = 7", "explanation": "Subtract 5 from both sides: x = 12 - 5 = 7"},
                        {"problem": "2x = 10, find x", "solution": "x = 5", "explanation": "Divide both sides by 2: x = 10 ÷ 2 = 5"},
                        {"problem": "If y = 3, what is 2y + 1?", "solution": "7", "explanation": "Substitute y = 3: 2(3) + 1 = 6 + 1 = 7"}
                    ]
                },
                "difficulty_2": {
                    "concepts": ["Linear Equations", "Factoring", "Quadratic Basics"],
                    "examples": [
                        {"problem": "3x + 7 = 22, find x", "solution": "x = 5", "explanation": "Subtract 7: 3x = 15, then divide by 3: x = 5"},
                        {"problem": "Factor: x² + 5x + 6", "solution": "(x + 2)(x + 3)", "explanation": "Find two numbers that multiply to 6 and add to 5: 2 and 3"}
                    ]
                }
            },
            "Geometry": {
                "difficulty_1": {
                    "concepts": ["Shapes", "Perimeter", "Area of Rectangles"],
                    "examples": [
                        {"problem": "Area of rectangle: length=5, width=3", "solution": "15 square units", "explanation": "Area = length × width = 5 × 3 = 15"},
                        {"problem": "Perimeter of square with side=4", "solution": "16 units", "explanation": "Perimeter = 4 × side = 4 × 4 = 16"}
                    ]
                },
                "difficulty_2": {
                    "concepts": ["Circle Area", "Volume", "Pythagorean Theorem"],
                    "examples": [
                        {"problem": "Area of circle with radius=3", "solution": "28.27 square units", "explanation": "Area = π × r² = π × 3² = 9π ≈ 28.27"},
                        {"problem": "Right triangle: a=3, b=4, find c", "solution": "c = 5", "explanation": "c² = a² + b² = 9 + 16 = 25, so c = 5"}
                    ]
                }
            }
        }
    
    def get_topic_overview(self, topic: str, difficulty: int = 1) -> Dict[str, Any]:
        """Get overview of a math topic at specified difficulty"""
        if topic not in self.topics:
            return {"error": f"Topic '{topic}' not found"}
        
        difficulty_key = f"difficulty_{difficulty}"
        if difficulty_key not in self.topics[topic]:
            return {"error": f"Difficulty level {difficulty} not available for {topic}"}
        
        topic_data = self.topics[topic][difficulty_key]
        return {
            "topic": topic,
            "difficulty": difficulty,
            "concepts": topic_data["concepts"],
            "example_count": len(topic_data["examples"]),
            "description": f"{topic} at difficulty level {difficulty}"
        }
    
    def get_practice_problem(self, topic: str, difficulty: int = 1) -> Dict[str, str]:
        """Get a random practice problem from specified topic and difficulty"""
        if topic not in self.topics:
            return {"error": f"Topic '{topic}' not found"}
        
        difficulty_key = f"difficulty_{difficulty}"
        if difficulty_key not in self.topics[topic]:
            return {"error": f"Difficulty level {difficulty} not available for {topic}"}
        
        examples = self.topics[topic][difficulty_key]["examples"]
        problem = random.choice(examples)
        
        return {
            "topic": topic,
            "difficulty": difficulty,
            "problem": problem["problem"],
            "solution": problem["solution"],
            "explanation": problem["explanation"]
        }
    
    def generate_quiz_questions(self, topic: str, difficulty: int = 1, count: int = 5) -> List[Dict[str, Any]]:
        """Generate multiple choice quiz questions for a topic"""
        questions = []
        
        if topic not in self.topics:
            return [{"error": f"Topic '{topic}' not found"}]
        
        difficulty_key = f"difficulty_{difficulty}"
        if difficulty_key not in self.topics[topic]:
            return [{"error": f"Difficulty level {difficulty} not available for {topic}"}]
        
        examples = self.topics[topic][difficulty_key]["examples"]
        
        for i in range(min(count, len(examples))):
            problem = examples[i % len(examples)]
            
            # Generate multiple choice options
            correct_answer = problem["solution"]
            
            # Create incorrect options based on the problem type
            incorrect_options = self._generate_incorrect_options(correct_answer, topic)
            
            # Shuffle options
            all_options = [correct_answer] + incorrect_options
            random.shuffle(all_options)
            
            # Find correct option letter
            correct_letter = chr(65 + all_options.index(correct_answer))  # A, B, C, D
            
            questions.append({
                "question": f"Solve: {problem['problem']}",
                "options": [f"{chr(65+j)}) {opt}" for j, opt in enumerate(all_options)],
                "correct_answer": correct_letter,
                "explanation": problem["explanation"]
            })
        
        return questions
    
    def _generate_incorrect_options(self, correct_answer: str, topic: str) -> List[str]:
        """Generate plausible incorrect answers"""
        try:
            # Try to extract numeric value from correct answer
            import re
            numbers = re.findall(r'-?\d+\.?\d*', correct_answer)
            if numbers:
                base_value = float(numbers[0])
                
                # Generate nearby incorrect values
                incorrect = []
                incorrect.append(str(int(base_value + 1)))
                incorrect.append(str(int(base_value - 1)))
                
                if base_value > 2:
                    incorrect.append(str(int(base_value + 2)))
                else:
                    incorrect.append(str(int(base_value * 2)))
                
                return incorrect[:3]
        except:
            pass
        
        # Fallback generic incorrect options
        return ["Wrong answer 1", "Wrong answer 2", "Wrong answer 3"]
    
    def get_learning_path(self, current_level: int = 1) -> Dict[str, Any]:
        """Get recommended learning path based on current level"""
        paths = {
            1: {
                "recommended_topics": ["Arithmetic"],
                "focus_areas": ["Addition", "Subtraction", "Basic Multiplication"],
                "next_level": 2,
                "estimated_time": "2-3 weeks"
            },
            2: {
                "recommended_topics": ["Arithmetic", "Algebra"],
                "focus_areas": ["Multi-digit operations", "Simple equations"],
                "next_level": 3,
                "estimated_time": "3-4 weeks"
            },
            3: {
                "recommended_topics": ["Algebra", "Geometry"],
                "focus_areas": ["Linear equations", "Basic geometry"],
                "next_level": 4,
                "estimated_time": "4-5 weeks"
            }
        }
        
        return paths.get(current_level, {
            "recommended_topics": ["Advanced Mathematics"],
            "focus_areas": ["Complex problem solving"],
            "next_level": current_level + 1,
            "estimated_time": "Ongoing"
        })

# Usage example and testing
if __name__ == "__main__":
    math_module = MathModule()
    
    # Test topic overview
    print("=== Math Topic Overview ===")
    overview = math_module.get_topic_overview("Algebra", 1)
    print(f"Topic: {overview['topic']}")
    print(f"Concepts: {overview['concepts']}")
    
    # Test practice problem
    print("\n=== Practice Problem ===")
    problem = math_module.get_practice_problem("Algebra", 1)
    print(f"Problem: {problem['problem']}")
    print(f"Solution: {problem['solution']}")
    print(f"Explanation: {problem['explanation']}")
    
    # Test quiz generation
    print("\n=== Quiz Questions ===")
    questions = math_module.generate_quiz_questions("Arithmetic", 1, 2)
    for i, q in enumerate(questions, 1):
        print(f"\nQuestion {i}: {q['question']}")
        for option in q['options']:
            print(f"  {option}")
        print(f"Correct: {q['correct_answer']}")