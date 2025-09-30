"""
Science Education Module for Laura-bot Personal Learning Assistant
Provides structured science content with graded difficulty levels
"""

import random
from typing import Dict, List, Any

class ScienceModule:
    def __init__(self):
        self.topics = {
            "Biology": {
                "difficulty_1": {
                    "concepts": ["Living vs Non-living", "Basic Body Parts", "Animals and Plants", "Food Chain Basics"],
                    "facts": [
                        {"concept": "Living Things", "fact": "All living things need air, water, food, and shelter to survive", "example": "Plants need sunlight and water to grow"},
                        {"concept": "Animals", "fact": "Animals can be grouped into mammals, birds, fish, reptiles, and amphibians", "example": "Dogs are mammals, eagles are birds"},
                        {"concept": "Plants", "fact": "Plants make their own food using sunlight through photosynthesis", "example": "Green leaves capture sunlight to make food"},
                        {"concept": "Food Chain", "fact": "Energy flows from plants to animals in a food chain", "example": "Grass → Rabbit → Fox"}
                    ]
                },
                "difficulty_2": {
                    "concepts": ["Cell Structure", "Human Body Systems", "Genetics Basics", "Ecosystems"],
                    "facts": [
                        {"concept": "Cells", "fact": "All living things are made of one or more cells", "example": "Humans have billions of cells working together"},
                        {"concept": "Digestive System", "fact": "The digestive system breaks down food to give us energy", "example": "Stomach uses acid to break down food"},
                        {"concept": "DNA", "fact": "DNA contains instructions for how living things look and function", "example": "Eye color is determined by DNA from parents"},
                        {"concept": "Ecosystem", "fact": "An ecosystem includes all living and non-living things in an area", "example": "A forest ecosystem includes trees, animals, soil, and water"}
                    ]
                }
            },
            "Chemistry": {
                "difficulty_1": {
                    "concepts": ["States of Matter", "Basic Elements", "Simple Reactions", "Mixtures"],
                    "facts": [
                        {"concept": "States of Matter", "fact": "Matter exists as solid, liquid, or gas", "example": "Ice (solid), water (liquid), steam (gas)"},
                        {"concept": "Elements", "fact": "Elements are pure substances that cannot be broken down further", "example": "Gold, oxygen, and carbon are elements"},
                        {"concept": "Chemical Reactions", "fact": "In reactions, substances change to form new substances", "example": "Iron + oxygen → rust"},
                        {"concept": "Mixtures", "fact": "Mixtures combine substances without changing them chemically", "example": "Sand mixed with water"}
                    ]
                },
                "difficulty_2": {
                    "concepts": ["Atomic Structure", "Chemical Bonds", "Acids and Bases", "Chemical Equations"],
                    "facts": [
                        {"concept": "Atoms", "fact": "Atoms are made of protons, neutrons, and electrons", "example": "Hydrogen has 1 proton and 1 electron"},
                        {"concept": "Chemical Bonds", "fact": "Atoms bond together to form molecules and compounds", "example": "H₂O - two hydrogen atoms bonded to one oxygen"},
                        {"concept": "pH Scale", "fact": "pH measures how acidic or basic a substance is (0-14)", "example": "Lemon juice is acidic (pH 2), soap is basic (pH 9)"},
                        {"concept": "Equations", "fact": "Chemical equations show what happens in reactions", "example": "2H₂ + O₂ → 2H₂O (making water)"}
                    ]
                }
            },
            "Physics": {
                "difficulty_1": {
                    "concepts": ["Forces and Motion", "Simple Machines", "Light and Sound", "Heat"],
                    "facts": [
                        {"concept": "Forces", "fact": "A force is a push or pull that can change motion", "example": "Kicking a ball applies force to make it move"},
                        {"concept": "Simple Machines", "fact": "Machines help us do work more easily", "example": "A lever helps lift heavy objects with less effort"},
                        {"concept": "Light", "fact": "Light travels in straight lines and can be reflected or refracted", "example": "Mirrors reflect light, prisms bend light into colors"},
                        {"concept": "Heat", "fact": "Heat is energy that flows from hot objects to cold objects", "example": "A hot cup warms your hands"}
                    ]
                },
                "difficulty_2": {
                    "concepts": ["Energy Types", "Electricity", "Waves", "Gravity"],
                    "facts": [
                        {"concept": "Energy", "fact": "Energy cannot be created or destroyed, only changed from one form to another", "example": "Chemical energy in food → kinetic energy for movement"},
                        {"concept": "Electricity", "fact": "Electric current is the flow of electrons through a conductor", "example": "Copper wires carry electricity in circuits"},
                        {"concept": "Waves", "fact": "Waves transfer energy without transferring matter", "example": "Sound waves carry energy through air"},
                        {"concept": "Gravity", "fact": "Gravity is a force that pulls objects toward each other", "example": "Earth's gravity keeps us on the ground"}
                    ]
                }
            }
        }
    
    def get_topic_overview(self, topic: str, difficulty: int = 1) -> Dict[str, Any]:
        """Get overview of a science topic at specified difficulty"""
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
            "fact_count": len(topic_data["facts"]),
            "description": f"{topic} at difficulty level {difficulty}"
        }
    
    def get_science_fact(self, topic: str, difficulty: int = 1, concept: str = None) -> Dict[str, str]:
        """Get a science fact from specified topic and difficulty"""
        if topic not in self.topics:
            return {"error": f"Topic '{topic}' not found"}
        
        difficulty_key = f"difficulty_{difficulty}"
        if difficulty_key not in self.topics[topic]:
            return {"error": f"Difficulty level {difficulty} not available for {topic}"}
        
        facts = self.topics[topic][difficulty_key]["facts"]
        
        if concept:
            # Find specific concept
            for fact in facts:
                if concept.lower() in fact["concept"].lower():
                    return fact
            return {"error": f"Concept '{concept}' not found in {topic}"}
        else:
            # Return random fact
            return random.choice(facts)
    
    def generate_quiz_questions(self, topic: str, difficulty: int = 1, count: int = 5) -> List[Dict[str, Any]]:
        """Generate multiple choice quiz questions for a science topic"""
        questions = []
        
        if topic not in self.topics:
            return [{"error": f"Topic '{topic}' not found"}]
        
        difficulty_key = f"difficulty_{difficulty}"
        if difficulty_key not in self.topics[topic]:
            return [{"error": f"Difficulty level {difficulty} not available for {topic}"}]
        
        facts = self.topics[topic][difficulty_key]["facts"]
        
        for i in range(min(count, len(facts))):
            fact = facts[i % len(facts)]
            
            # Create question from fact
            question_text = f"What is true about {fact['concept']}?"
            correct_answer = fact["fact"]
            
            # Generate incorrect options
            incorrect_options = self._generate_incorrect_options(fact, topic, difficulty)
            
            # Create multiple choice
            all_options = [correct_answer] + incorrect_options
            random.shuffle(all_options)
            
            correct_letter = chr(65 + all_options.index(correct_answer))
            
            questions.append({
                "question": question_text,
                "options": [f"{chr(65+j)}) {opt}" for j, opt in enumerate(all_options)],
                "correct_answer": correct_letter,
                "explanation": f"{fact['fact']} Example: {fact['example']}"
            })
        
        return questions
    
    def _generate_incorrect_options(self, fact: Dict[str, str], topic: str, difficulty: int) -> List[str]:
        """Generate plausible incorrect answers for science questions"""
        concept = fact["concept"].lower()
        
        # Generic incorrect options based on topic
        if topic == "Biology":
            incorrect_pool = [
                "Only plants need water to survive",
                "All animals are mammals",
                "Plants get energy from eating other plants",
                "Cells are only in plants, not animals"
            ]
        elif topic == "Chemistry":
            incorrect_pool = [
                "Matter can only exist as liquid",
                "Elements can be broken down into smaller parts",
                "Chemical reactions only happen in laboratories",
                "All mixtures must be heated to separate"
            ]
        elif topic == "Physics":
            incorrect_pool = [
                "Forces can only push, never pull",
                "Light always travels in curved lines",
                "Heat flows from cold to hot objects",
                "Energy can be created from nothing"
            ]
        else:
            incorrect_pool = [
                "This statement is always false",
                "This only applies to very large objects",
                "This principle was recently disproven"
            ]
        
        # Select 3 random incorrect options
        return random.sample(incorrect_pool, min(3, len(incorrect_pool)))
    
    def get_experiment_suggestion(self, topic: str, difficulty: int = 1) -> Dict[str, str]:
        """Suggest a simple experiment related to the topic"""
        experiments = {
            "Biology": {
                1: {
                    "title": "Plant Growth Experiment",
                    "materials": "2 bean seeds, 2 cups, soil, water",
                    "procedure": "Plant seeds in cups. Give one water and sunlight, keep the other in darkness. Observe growth after 1 week.",
                    "learning": "Plants need both water AND sunlight to grow properly"
                },
                2: {
                    "title": "Heart Rate Investigation",
                    "materials": "Stopwatch, notebook",
                    "procedure": "Measure your pulse at rest, then after jumping for 1 minute. Record the difference.",
                    "learning": "Exercise increases heart rate as the body needs more oxygen"
                }
            },
            "Chemistry": {
                1: {
                    "title": "States of Matter Demo",
                    "materials": "Ice cubes, hot water, clear container",
                    "procedure": "Put ice in hot water. Observe ice melting and water evaporating as steam.",
                    "learning": "The same substance (water) can exist in different states"
                },
                2: {
                    "title": "Acid-Base Indicator",
                    "materials": "Red cabbage, hot water, lemon juice, baking soda",
                    "procedure": "Make cabbage juice indicator. Test with lemon (acid) and baking soda (base). Colors change!",
                    "learning": "Natural indicators can show if substances are acidic or basic"
                }
            },
            "Physics": {
                1: {
                    "title": "Simple Lever",
                    "materials": "Ruler, pencil, small objects",
                    "procedure": "Balance ruler on pencil. Put objects on each end. Move the pencil to find balance points.",
                    "learning": "Levers help us lift heavy objects with less force"
                },
                2: {
                    "title": "Electricity from Lemon",
                    "materials": "Lemon, copper coin, zinc nail, LED light",
                    "procedure": "Insert coin and nail into lemon. Connect to LED with wires. The LED should light up!",
                    "learning": "Chemical reactions can generate electricity"
                }
            }
        }
        
        if topic in experiments and difficulty in experiments[topic]:
            return experiments[topic][difficulty]
        else:
            return {
                "title": "General Science Observation",
                "materials": "Eyes, notebook",
                "procedure": "Observe something in nature for 10 minutes. Write down what you see.",
                "learning": "Careful observation is the foundation of all science"
            }

# Usage example and testing
if __name__ == "__main__":
    science_module = ScienceModule()
    
    # Test topic overview
    print("=== Science Topic Overview ===")
    overview = science_module.get_topic_overview("Biology", 1)
    print(f"Topic: {overview['topic']}")
    print(f"Concepts: {overview['concepts']}")
    
    # Test science fact
    print("\n=== Science Fact ===")
    fact = science_module.get_science_fact("Physics", 1)
    print(f"Concept: {fact['concept']}")
    print(f"Fact: {fact['fact']}")
    print(f"Example: {fact['example']}")
    
    # Test experiment suggestion
    print("\n=== Experiment Suggestion ===")
    experiment = science_module.get_experiment_suggestion("Chemistry", 1)
    print(f"Title: {experiment['title']}")
    print(f"Materials: {experiment['materials']}")
    print(f"Learning: {experiment['learning']}")