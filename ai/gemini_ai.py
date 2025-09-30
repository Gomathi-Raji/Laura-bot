from config import get_model
import re
import json
import random
from typing import Dict, List, Any, Optional

# Import education modules
try:
    from education_modules import get_education_module, list_available_subjects
    EDUCATION_MODULES_AVAILABLE = True
except ImportError:
    EDUCATION_MODULES_AVAILABLE = False
    print("⚠️ Education modules not available. Using fallback AI generation.")

# Fallback responses for when API is unavailable
FALLBACK_RESPONSES = {
    'general': [
        "I'm currently experiencing some connectivity issues, but I'm still here to help! Please try again in a moment.",
        "My AI service is temporarily busy. Let me know what you'd like to learn about and I'll assist you shortly!",
        "I'm having trouble connecting to my knowledge base right now. Please wait a moment and try again."
    ],
    'quiz': [
        "I'd love to create a quiz for you, but I'm having connectivity issues. Here's a sample question:\n\nWhat is 2 + 2?\nA) 3\nB) 4\nC) 5\nD) 6\n\nAnswer: B) 4",
        "Quiz generation is temporarily unavailable. Try asking me to explain a topic instead!",
        "I'm unable to generate a custom quiz right now, but I can help explain concepts if you'd like!"
    ],
    'explanation': [
        "I'd like to explain that topic for you, but I'm experiencing some technical difficulties. Please try again shortly!",
        "My explanation service is temporarily unavailable. Is there a specific concept you'd like me to help with when I'm back online?",
        "I'm having trouble accessing my knowledge base for explanations. Please check back in a moment!"
    ]
}

def get_fallback_response(response_type='general'):
    """Get a random fallback response when API is unavailable"""
    return random.choice(FALLBACK_RESPONSES.get(response_type, FALLBACK_RESPONSES['general']))

def clean_response(text):
    # Remove leading bullet characters like "*", "-", etc.
    cleaned_lines = []
    for line in text.splitlines():
        cleaned_line = re.sub(r"^\s*[\\-\•]\s", "", line)  # removes leading bullets with optional whitespace
        cleaned_lines.append(cleaned_line)
    return "\n".join(cleaned_lines)

def get_response(prompt):
    try:
        model = get_model()
        if model is None:
            return get_fallback_response('general')
        response = model.generate_content(prompt)
        return clean_response(response.text)
    except Exception as e:
        print(f"⚠️ AI Response Error: {e}")
        return get_fallback_response('general')
    except Exception as e:
        print(f"⚠️ AI API Error: {str(e)}")
        if "quota" in str(e).lower() or "rate" in str(e).lower():
            return "🔄 I'm currently experiencing high demand. Please wait a moment and try again. My learning features will be back shortly!"
        elif "network" in str(e).lower() or "connection" in str(e).lower():
            return "🌐 I'm having connectivity issues. Please check your internet connection and try again."
        else:
            return get_fallback_response('general')


# ====== EDUCATIONAL AI FUNCTIONS ======

def get_tutor_response(query: str, subject: str = "", context: str = "") -> str:
    """Get educational response from AI tutor"""
    try:
        educational_prompt = f"""
        You are Zara, a friendly and knowledgeable personal learning assistant. 
        You specialize in making learning engaging and accessible for students of all ages.
        
        Subject Focus: {subject if subject else 'General Education'}
        Student Query: {query}
    Context: {context if context else 'General learning session'}
    
    Please provide:
    1. A clear, easy-to-understand explanation
    2. Practical examples when applicable
    3. Encouragement and motivation
    4. Follow-up questions to check understanding
    
        Keep your response concise but comprehensive, and always maintain an encouraging tone.
        If the question is beyond the subject scope, gently guide back to the topic.
        """
        
        return get_response(educational_prompt)
    except Exception as e:
        print(f"⚠️ Tutor AI Error: {str(e)}")
        return f"🎓 I'm experiencing some technical difficulties right now, but I'm still here to help you learn about {subject}! Please try asking your question again in a moment."


def generate_quiz(subject: str, topic: str, difficulty: int = 1, num_questions: int = 5) -> Dict[str, Any]:
    """Generate a quiz with multiple choice questions"""
    try:
        difficulty_levels = {
            1: "beginner level with basic concepts",
            2: "intermediate level with moderate complexity", 
            3: "advanced level with challenging concepts",
            4: "expert level with complex problem-solving",
            5: "mastery level with real-world applications"
        }
        
        difficulty_desc = difficulty_levels.get(difficulty, "intermediate level")
        
        quiz_prompt = f"""
    Create a {num_questions}-question multiple choice quiz on {subject} - {topic} at {difficulty_desc}.
    
    Return ONLY a JSON object with this exact structure:
    {{
        "subject": "{subject}",
        "topic": "{topic}",
        "difficulty": {difficulty},
        "questions": [
            {{
                "question": "Question text here",
                "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
                "correct_answer": "A",
                "explanation": "Why this is correct"
            }}
        ]
        }}
        
        Make questions engaging and educational. Include clear explanations for correct answers.
        """
        
        # Try structured education modules first
        if EDUCATION_MODULES_AVAILABLE:
            education_module = get_education_module(subject)
            if education_module:
                try:
                    # Use structured module for quiz generation
                    if hasattr(education_module, 'generate_quiz_questions'):
                        structured_questions = education_module.generate_quiz_questions(topic, difficulty, num_questions)
                        if structured_questions and not any('error' in q for q in structured_questions):
                            return {
                                "subject": subject,
                                "topic": topic,
                                "difficulty": difficulty,
                                "questions": structured_questions,
                                "source": "structured_module"
                            }
                except Exception as e:
                    print(f"⚠️ Structured module error: {e}")
        
        # Fallback to AI generation
        response = get_response(quiz_prompt)
        # Try to extract JSON from response
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        
        if json_start != -1 and json_end > json_start:
            json_str = response[json_start:json_end]
            quiz_data = json.loads(json_str)
            quiz_data["source"] = "ai_generated"
            return quiz_data
        else:
            # Fallback: create a simple quiz
            return create_fallback_quiz(subject, topic, difficulty, num_questions)
            
    except (json.JSONDecodeError, Exception) as e:
        print(f"⚠️ Quiz generation error: {e}")
        return create_fallback_quiz(subject, topic, difficulty, num_questions)
def create_fallback_quiz(subject: str, topic: str, difficulty: int, num_questions: int) -> Dict[str, Any]:
    """Create a fallback quiz when AI generation fails"""
    
    sample_questions = {
        "Math": {
            "Algebra": [
                {
                    "question": "What is the value of x in the equation 2x + 5 = 15?",
                    "options": ["A) 5", "B) 10", "C) 15", "D) 20"],
                    "correct_answer": "A",
                    "explanation": "Subtract 5 from both sides: 2x = 10, then divide by 2: x = 5"
                }
            ],
            "Geometry": [
                {
                    "question": "What is the area of a circle with radius 3?",
                    "options": ["A) 6π", "B) 9π", "C) 18π", "D) 12π"],
                    "correct_answer": "B", 
                    "explanation": "Area = πr² = π(3)² = 9π"
                }
            ]
        },
        "Science": {
            "Physics": [
                {
                    "question": "What is the speed of light in vacuum?",
                    "options": ["A) 300,000 km/s", "B) 300,000,000 m/s", "C) 186,000 miles/s", "D) All of the above"],
                    "correct_answer": "D",
                    "explanation": "The speed of light is approximately 300,000 km/s, 300,000,000 m/s, or 186,000 miles/s"
                }
            ]
        },
        "Languages": {
            "English": [
                {
                    "question": "Which is the correct past tense of 'go'?",
                    "options": ["A) goed", "B) went", "C) gone", "D) going"],
                    "correct_answer": "B",
                    "explanation": "'Went' is the correct past tense form of the irregular verb 'go'"
                }
            ]
        }
    }
    
    # Get sample questions for the subject/topic
    questions = []
    if subject in sample_questions and topic in sample_questions[subject]:
        base_questions = sample_questions[subject][topic]
        questions = base_questions * (num_questions // len(base_questions) + 1)
        questions = questions[:num_questions]
    else:
        # Create generic question
        questions = [{
            "question": f"This is a sample question about {topic} in {subject}",
            "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
            "correct_answer": "A",
            "explanation": "This is a sample explanation"
        }] * num_questions
    
    return {
        "subject": subject,
        "topic": topic, 
        "difficulty": difficulty,
        "questions": questions
    }


def generate_explanation(topic: str, subject: str = "", student_level: str = "beginner") -> str:
    """Generate detailed explanation for a topic"""
    try:
        explanation_prompt = f"""
        You are Zara, an expert tutor. Explain the concept of "{topic}" in {subject if subject else 'general studies'}.
        
        Student Level: {student_level}
        
        Provide:
        1. Simple definition in easy words
        2. Real-world examples or analogies
        3. Key points to remember
        4. Common mistakes to avoid
        5. Practice suggestions
        
        Make it engaging and easy to understand. Use analogies and examples that relate to everyday life.
        """
        
        # Try structured education modules first
        if EDUCATION_MODULES_AVAILABLE:
            education_module = get_education_module(subject)
            if education_module:
                try:
                    # Convert student_level to difficulty number
                    difficulty_map = {"beginner": 1, "intermediate": 2, "advanced": 3}
                    difficulty = difficulty_map.get(student_level, 1)
                    
                    if hasattr(education_module, 'get_science_fact'):
                        # Science module
                        fact = education_module.get_science_fact(subject, difficulty, topic)
                        if 'error' not in fact:
                            return f"📚 **{topic} Explanation:**\n\n{fact['fact']}\n\n**Example:** {fact['example']}\n\n💡 This is a fundamental concept in {subject}. Try to think of other examples in your daily life!"
                    
                    elif hasattr(education_module, 'get_practice_problem'):
                        # Math module  
                        overview = education_module.get_topic_overview(topic, difficulty)
                        if 'error' not in overview:
                            problem = education_module.get_practice_problem(topic, difficulty)
                            if 'error' not in problem:
                                return f"📚 **{topic} Explanation:**\n\nThis topic covers: {', '.join(overview['concepts'])}\n\n**Example Problem:** {problem['problem']}\n**Solution:** {problem['solution']}\n**Explanation:** {problem['explanation']}\n\n💡 Practice similar problems to master this concept!"
                except Exception as e:
                    print(f"⚠️ Structured explanation error: {e}")
        
        # Fallback to AI generation
        return get_response(explanation_prompt)
    except Exception as e:
        print(f"⚠️ Explanation generation error: {e}")
        return f"📚 I'd love to explain '{topic}' for you, but I'm experiencing some technical difficulties. Here's a basic overview: {topic} is an important concept in {subject}. Please try asking again in a moment for a detailed explanation!"


def generate_flashcard(subject: str, topic: str, difficulty: int = 1) -> Dict[str, str]:
    """Generate a flashcard for spaced repetition learning"""
    
    flashcard_prompt = f"""
    Create a flashcard for {subject} - {topic} at difficulty level {difficulty}/5.
    
    Return ONLY a JSON object:
    {{
        "front": "Question or concept to test",
        "back": "Answer or explanation",
        "hint": "Optional hint to help remember"
    }}
    
    Make it concise but comprehensive for quick review.
    """
    
    try:
        response = get_response(flashcard_prompt)
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        
        if json_start != -1 and json_end > json_start:
            json_str = response[json_start:json_end]
            return json.loads(json_str)
    except:
        pass
    
    # Fallback flashcard
    return {
        "front": f"What is an important concept in {topic}?",
        "back": f"This is a key concept in {subject} - {topic}",
        "hint": f"Think about the basics of {topic}"
    }


def generate_practice_problems(subject: str, topic: str, difficulty: int = 1, count: int = 3) -> List[Dict[str, str]]:
    """Generate practice problems for homework help"""
    
    problems_prompt = f"""
    Create {count} practice problems for {subject} - {topic} at difficulty level {difficulty}/5.
    
    Return ONLY a JSON array:
    [
        {{
            "problem": "Problem statement",
            "solution_steps": ["Step 1", "Step 2", "Step 3"],
            "final_answer": "Final answer",
            "difficulty_rating": {difficulty}
        }}
    ]
    
    Include step-by-step solutions to help students learn the process.
    """
    
    try:
        response = get_response(problems_prompt)
        json_start = response.find('[')
        json_end = response.rfind(']') + 1
        
        if json_start != -1 and json_end > json_start:
            json_str = response[json_start:json_end]
            return json.loads(json_str)
    except:
        pass
    
    # Fallback problems
    return [{
        "problem": f"Solve a problem related to {topic} in {subject}",
        "solution_steps": ["Identify the key information", "Apply relevant concepts", "Calculate the result"],
        "final_answer": "Answer will depend on the specific problem",
        "difficulty_rating": difficulty
    }] * count


def check_homework_answer(student_answer: str, correct_answer: str, subject: str, topic: str) -> Dict[str, Any]:
    """Check and provide feedback on homework answers"""
    
    feedback_prompt = f"""
    A student submitted this answer for a {subject} - {topic} question:
    Student Answer: "{student_answer}"
    Correct Answer: "{correct_answer}"
    
    Provide feedback as JSON:
    {{
        "is_correct": true/false,
        "score_percentage": 0-100,
        "feedback": "Encouraging feedback explaining what's correct/incorrect",
        "suggestions": ["Specific suggestions for improvement"],
        "related_concepts": ["Related topics to review"]
    }}
    
    Be encouraging and constructive in feedback, even for incorrect answers.
    """
    
    try:
        response = get_response(feedback_prompt)
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        
        if json_start != -1 and json_end > json_start:
            json_str = response[json_start:json_end]
            return json.loads(json_str)
    except:
        pass
    
    # Simple fallback feedback
    is_correct = student_answer.lower().strip() == correct_answer.lower().strip()
    return {
        "is_correct": is_correct,
        "score_percentage": 100 if is_correct else 50,
        "feedback": "Great job!" if is_correct else "Good attempt! Let's work on getting the correct answer.",
        "suggestions": ["Review the topic again", "Practice similar problems"],
        "related_concepts": [topic]
    }


def get_study_recommendations(weak_topics: List[str], strong_topics: List[str], user_preferences: Dict = None) -> List[str]:
    """Generate personalized study recommendations"""
    
    prefs = user_preferences or {}
    
    recommendations_prompt = f"""
    Generate 5 personalized study recommendations for a student with:
    Weak topics: {weak_topics}
    Strong topics: {strong_topics}
    Preferences: {prefs}
    
    Provide practical, actionable advice for improvement.
    Focus on making learning engaging and building on strengths.
    
    Return as a simple list of recommendations.
    """
    
    response = get_response(recommendations_prompt)
    
    # Extract recommendations from response
    recommendations = []
    for line in response.split('\n'):
        line = line.strip()
        if line and not line.startswith('#'):
            # Remove numbering and bullet points
            clean_line = re.sub(r'^\d+\.\s*', '', line)
            clean_line = re.sub(r'^[\-\*\•]\s*', '', clean_line)
            if clean_line:
                recommendations.append(clean_line)
    
    return recommendations[:5] if recommendations else [
        "Practice daily for consistent improvement",
        "Focus on understanding concepts rather than memorization", 
        "Use active learning techniques like teaching others",
        "Take regular breaks to maintain focus",
        "Review and reinforce your strong topics while working on weak areas"
    ]


def generate_motivational_message(user_progress: Dict, context: str = "") -> str:
    """Generate encouraging message based on user progress"""
    
    motivation_prompt = f"""
    Generate an encouraging message for a student with this progress:
    {user_progress}
    
    Context: {context}
    
    Be positive, specific to their achievements, and motivating for continued learning.
    Keep it personal and friendly, as if from Zara, their learning assistant.
    """
    
    return get_response(motivation_prompt)