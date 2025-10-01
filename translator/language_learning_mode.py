import google.generativeai as genai
import json
import os
from datetime import datetime
import random

# Configure Gemini API
genai.configure(api_key="AIzaSyBif5c4kQOeJKpo-aRNQva86h1ldss_ggE")

class LanguageLearningMode:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-2.5-flash-exp")
        self.learning_progress_file = "language_learning_progress.json"
        self.learned_words = self.load_progress()
        self.current_session = {
            'translations': [],
            'corrections': [],
            'practice_words': []
        }
        
        # Language mappings for UI
        self.language_names = {
            'tamil': 'தமிழ்',
            'english': 'English',
            'hindi': 'हिंदी'
        }
        
        # Common learning phrases for practice
        self.practice_phrases = {
            'tamil': [
                'வணக்கம்', 'நன்றி', 'என் பெயர்', 'எப்படி இருக்கிறீர்கள்?', 
                'எனக்கு புரியவில்லை', 'மீண்டும் சொல்லுங்கள்', 'மன்னிக்கவும்',
                'நான் சாப்பிட வேண்டும்', 'எங்கே செல்கிறீர்கள்?', 'நல்ல காலை'
            ],
            'english': [
                'Hello', 'Thank you', 'My name is', 'How are you?',
                'I don\'t understand', 'Please repeat', 'Sorry',
                'I want to eat', 'Where are you going?', 'Good morning'
            ],
            'hindi': [
                'नमस्ते', 'धन्यवाद', 'मेरा नाम', 'आप कैसे हैं?',
                'मुझे समझ नहीं आया', 'कृपया दोहराएं', 'माफ़ करें',
                'मैं खाना चाहता हूं', 'आप कहाँ जा रहे हैं?', 'सुप्रभात'
            ]
        }

    def load_progress(self):
        """Load learning progress from file"""
        if os.path.exists(self.learning_progress_file):
            try:
                with open(self.learning_progress_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_progress(self):
        """Save learning progress to file"""
        try:
            with open(self.learning_progress_file, 'w', encoding='utf-8') as f:
                json.dump(self.learned_words, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving progress: {e}")

    def translate_with_learning(self, text, source_lang, target_lang):
        """Enhanced translation with learning features"""
        try:
            # Create detailed prompt for better learning
            prompt = f"""
            Translate '{text}' from {source_lang} to {target_lang}.
            
            Provide the response in this JSON format:
            {{
                "translation": "translated text",
                "pronunciation": "pronunciation guide if applicable",
                "grammar_note": "brief grammar explanation",
                "cultural_context": "cultural context if relevant",
                "difficulty_level": "beginner/intermediate/advanced"
            }}
            """
            
            response = self.model.generate_content(prompt)
            
            # Try to parse as JSON, fallback to simple text
            try:
                result = json.loads(response.text.strip())
                translation = result.get('translation', response.text.strip())
            except:
                translation = response.text.strip()
                result = {
                    "translation": translation,
                    "pronunciation": "",
                    "grammar_note": "",
                    "cultural_context": "",
                    "difficulty_level": "beginner"
                }
            
            # Track the translation for learning
            self.track_translation(text, translation, source_lang, target_lang, result)
            
            return result
            
        except Exception as e:
            return {
                "translation": f"Translation error: {str(e)}",
                "pronunciation": "",
                "grammar_note": "",
                "cultural_context": "",
                "difficulty_level": "beginner"
            }

    def track_translation(self, original, translation, source_lang, target_lang, details):
        """Track translations for learning analytics"""
        key = f"{source_lang}_{target_lang}"
        if key not in self.learned_words:
            self.learned_words[key] = []
        
        # Add new learning entry
        learning_entry = {
            'original': original,
            'translation': translation,
            'timestamp': datetime.now().isoformat(),
            'details': details,
            'practice_count': 0,
            'mastery_level': 0
        }
        
        self.learned_words[key].append(learning_entry)
        self.current_session['translations'].append(learning_entry)
        
        # Save progress
        self.save_progress()

    def get_practice_suggestion(self, language_pair):
        """Get suggested words/phrases for practice"""
        source_lang, target_lang = language_pair.split('_')
        
        # Mix of common phrases and previously learned words
        suggestions = []
        
        # Add common practice phrases
        if source_lang in self.practice_phrases:
            suggestions.extend(random.sample(
                self.practice_phrases[source_lang], 
                min(3, len(self.practice_phrases[source_lang]))
            ))
        
        # Add previously learned words that need practice
        if language_pair in self.learned_words:
            practice_needed = [
                item for item in self.learned_words[language_pair]
                if item.get('practice_count', 0) < 3
            ]
            if practice_needed:
                suggestions.extend([
                    item['original'] for item in 
                    random.sample(practice_needed, min(2, len(practice_needed)))
                ])
        
        return suggestions

    def generate_quiz(self, source_lang, target_lang, num_questions=5):
        """Generate a quiz based on learned words"""
        language_pair = f"{source_lang}_{target_lang}"
        
        if language_pair not in self.learned_words or len(self.learned_words[language_pair]) < 3:
            return None
        
        # Select random words from learned vocabulary
        learned_items = self.learned_words[language_pair]
        quiz_items = random.sample(learned_items, min(num_questions, len(learned_items)))
        
        quiz = {
            'questions': [],
            'source_lang': source_lang,
            'target_lang': target_lang,
            'created_at': datetime.now().isoformat()
        }
        
        for item in quiz_items:
            question = {
                'question': f"Translate: {item['original']}",
                'correct_answer': item['translation'],
                'source_text': item['original'],
                'options': self.generate_multiple_choice_options(
                    item['translation'], language_pair
                )
            }
            quiz['questions'].append(question)
        
        return quiz

    def generate_multiple_choice_options(self, correct_answer, language_pair):
        """Generate multiple choice options for quiz"""
        options = [correct_answer]
        
        # Add some random wrong answers from the same language
        if language_pair in self.learned_words:
            other_translations = [
                item['translation'] for item in self.learned_words[language_pair]
                if item['translation'] != correct_answer
            ]
            
            # Add 2-3 wrong options
            num_wrong = min(3, len(other_translations))
            if num_wrong > 0:
                options.extend(random.sample(other_translations, num_wrong))
        
        # Shuffle options
        random.shuffle(options)
        return options

    def get_learning_stats(self):
        """Get learning statistics"""
        stats = {
            'total_translations': 0,
            'languages_practiced': [],
            'session_count': len(self.current_session['translations']),
            'mastery_breakdown': {'beginner': 0, 'intermediate': 0, 'advanced': 0}
        }
        
        for language_pair, translations in self.learned_words.items():
            stats['total_translations'] += len(translations)
            if language_pair not in stats['languages_practiced']:
                stats['languages_practiced'].append(language_pair)
            
            # Count by difficulty
            for item in translations:
                difficulty = item.get('details', {}).get('difficulty_level', 'beginner')
                if difficulty in stats['mastery_breakdown']:
                    stats['mastery_breakdown'][difficulty] += 1
        
        return stats

    def simple_translate(self, text, source_lang, target_lang):
        """Simple translation for backward compatibility"""
        try:
            prompt = f"Translate this {source_lang} text to {target_lang} without explanation: '{text}'"
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Translation error: {str(e)}"

# Initialize global language learning instance
language_learner = LanguageLearningMode()

# Backward compatibility functions
def translate_tamil_to_hindi(text):
    return language_learner.simple_translate(text, "Tamil", "Hindi")

def translate_tamil_to_english(text):
    return language_learner.simple_translate(text, "Tamil", "English")

def translate_hindi_to_tamil(text):
    return language_learner.simple_translate(text, "Hindi", "Tamil")

def translate_english_to_tamil(text):
    return language_learner.simple_translate(text, "English", "Tamil")

def translate_hindi_to_english(text):
    return language_learner.simple_translate(text, "Hindi", "English")

def translate_english_to_hindi(text):
    return language_learner.simple_translate(text, "English", "Hindi")