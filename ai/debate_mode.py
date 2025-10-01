import google.generativeai as genai
import json
import os
from datetime import datetime
import random
from typing import Dict, List, Any, Optional
from config import get_model

class DebateMode:
    def __init__(self):
        self.model = get_model()
        self.debate_history_file = "debate_history.json"
        self.current_debate = {
            'topic': '',
            'user_position': '',
            'ai_position': '',
            'arguments': [],
            'counter_arguments': [],
            'debate_flow': [],
            'score': {'user': 0, 'ai': 0},
            'round': 0,
            'status': 'not_started'
        }
        self.debate_statistics = self.load_debate_stats()
        
        # Debate topics and categories
        self.debate_categories = {
            'technology': [
                'Is artificial intelligence more beneficial or harmful to society?',
                'Should social media platforms be held responsible for user content?',
                'Is remote work better than office work?',
                'Should robots replace human workers in dangerous jobs?',
                'Is cryptocurrency the future of money?'
            ],
            'education': [
                'Should traditional education be replaced by online learning?',
                'Is homework necessary for student success?',
                'Should students be allowed to use AI tools for assignments?',
                'Is competitive grading beneficial or harmful?',
                'Should financial literacy be mandatory in schools?'
            ],
            'environment': [
                'Is nuclear energy necessary for fighting climate change?',
                'Should plastic bags be completely banned?',
                'Is individual action or government policy more important for environmental protection?',
                'Should we prioritize economic growth or environmental protection?',
                'Is space exploration worth the environmental cost?'
            ],
            'society': [
                'Should universal basic income be implemented?',
                'Is censorship ever justified in democratic societies?',
                'Should voting be mandatory for all citizens?',
                'Is fast food advertising harmful to public health?',
                'Should public transportation be free for everyone?'
            ],
            'ethics': [
                'Is it ethical to use animals for scientific research?',
                'Should genetic engineering of humans be allowed?',
                'Is it right to prioritize saving human lives over animal lives?',
                'Should wealthy countries be required to accept more refugees?',
                'Is capital punishment ever justified?'
            ]
        }
        
        # Debate roles and personas
        self.ai_personas = {
            'analytical': {
                'name': 'The Analyst',
                'style': 'logical, data-driven, methodical',
                'approach': 'Uses statistics, research, and systematic reasoning'
            },
            'passionate': {
                'name': 'The Advocate',
                'style': 'emotional, persuasive, empathetic',
                'approach': 'Appeals to values, emotions, and human experiences'
            },
            'devil_advocate': {
                'name': 'The Skeptic',
                'style': 'challenging, questioning, contrarian',
                'approach': 'Points out flaws, asks difficult questions, challenges assumptions'
            },
            'balanced': {
                'name': 'The Moderator',
                'style': 'fair, balanced, comprehensive',
                'approach': 'Considers multiple perspectives and seeks middle ground'
            }
        }

    def load_debate_stats(self):
        """Load debate statistics from file"""
        if os.path.exists(self.debate_history_file):
            try:
                with open(self.debate_history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {'total_debates': 0, 'user_wins': 0, 'ai_wins': 0, 'draws': 0, 'topics_debated': []}
        return {'total_debates': 0, 'user_wins': 0, 'ai_wins': 0, 'draws': 0, 'topics_debated': []}

    def save_debate_stats(self):
        """Save debate statistics to file"""
        try:
            with open(self.debate_history_file, 'w', encoding='utf-8') as f:
                json.dump(self.debate_statistics, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving debate stats: {e}")

    def start_debate(self, topic: str = None, user_position: str = None, ai_persona: str = 'balanced'):
        """Initialize a new debate session"""
        if not topic:
            # Suggest a random topic
            category = random.choice(list(self.debate_categories.keys()))
            topic = random.choice(self.debate_categories[category])
        
        self.current_debate = {
            'topic': topic,
            'user_position': user_position or '',
            'ai_position': '',
            'ai_persona': ai_persona,
            'arguments': [],
            'counter_arguments': [],
            'debate_flow': [],
            'score': {'user': 0, 'ai': 0},
            'round': 0,
            'status': 'topic_set',
            'start_time': datetime.now().isoformat()
        }
        
        return {
            'topic': topic,
            'message': f"Great! Let's debate: '{topic}'. Which side would you like to argue?",
            'suggested_positions': self.generate_position_options(topic)
        }

    def generate_position_options(self, topic: str):
        """Generate pro/con position options for a topic"""
        try:
            prompt = f"""
            For the debate topic: "{topic}"
            
            Generate two clear position options (Pro and Con) that someone could argue.
            Return as JSON:
            {{
                "pro": "Clear pro position statement",
                "con": "Clear con position statement"
            }}
            
            Make positions specific and debatable.
            """
            
            response = self.model.generate_content(prompt)
            try:
                result = json.loads(response.text.strip())
                return result
            except:
                # Fallback positions
                return {
                    "pro": f"I support/agree with the topic: {topic}",
                    "con": f"I oppose/disagree with the topic: {topic}"
                }
                
        except Exception as e:
            return {
                "pro": f"I support the position in: {topic}",
                "con": f"I oppose the position in: {topic}"
            }

    def set_user_position(self, position: str):
        """Set user's debate position and generate AI counter-position"""
        self.current_debate['user_position'] = position
        
        # Generate AI position (opposite stance)
        ai_position = self.generate_ai_position(self.current_debate['topic'], position)
        self.current_debate['ai_position'] = ai_position
        self.current_debate['status'] = 'positions_set'
        
        return {
            'user_position': position,
            'ai_position': ai_position,
            'message': f"Perfect! You're arguing: {position}\nI'll argue: {ai_position}\n\nLet's begin! Present your opening argument.",
            'debate_ready': True
        }

    def generate_ai_position(self, topic: str, user_position: str):
        """Generate AI's counter-position based on user's position"""
        try:
            persona = self.ai_personas.get(self.current_debate.get('ai_persona', 'balanced'))
            
            prompt = f"""
            Topic: {topic}
            User's position: {user_position}
            
            As {persona['name']} with a {persona['style']} approach, generate a clear counter-position that opposes the user's stance.
            Be specific and create a strong opposing viewpoint that can be defended with arguments.
            
            Return only the position statement, no explanation.
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            return f"I disagree with your position and will argue the opposing view on: {topic}"

    def process_user_argument(self, user_argument: str):
        """Process user's argument and generate AI counter-argument"""
        self.current_debate['round'] += 1
        
        # Store user argument
        argument_entry = {
            'round': self.current_debate['round'],
            'speaker': 'user',
            'argument': user_argument,
            'timestamp': datetime.now().isoformat()
        }
        self.current_debate['arguments'].append(argument_entry)
        self.current_debate['debate_flow'].append(argument_entry)
        
        # Generate AI counter-argument
        ai_response = self.generate_ai_counter_argument(user_argument)
        
        counter_entry = {
            'round': self.current_debate['round'],
            'speaker': 'ai',
            'argument': ai_response['argument'],
            'reasoning': ai_response.get('reasoning', ''),
            'timestamp': datetime.now().isoformat()
        }
        self.current_debate['counter_arguments'].append(counter_entry)
        self.current_debate['debate_flow'].append(counter_entry)
        
        # Evaluate arguments
        evaluation = self.evaluate_round(user_argument, ai_response['argument'])
        
        return {
            'ai_argument': ai_response['argument'],
            'ai_reasoning': ai_response.get('reasoning', ''),
            'round_evaluation': evaluation,
            'round_number': self.current_debate['round'],
            'continue_debate': self.current_debate['round'] < 5  # Limit to 5 rounds
        }

    def generate_ai_counter_argument(self, user_argument: str):
        """Generate AI counter-argument with reasoning"""
        try:
            persona = self.ai_personas.get(self.current_debate.get('ai_persona', 'balanced'))
            
            prompt = f"""
            Debate Topic: {self.current_debate['topic']}
            My Position: {self.current_debate['ai_position']}
            User's Argument: {user_argument}
            
            As {persona['name']} with a {persona['style']} style:
            1. Counter the user's argument effectively
            2. Present evidence or reasoning supporting my position
            3. Use the approach: {persona['approach']}
            
            Return JSON:
            {{
                "argument": "Your main counter-argument (2-3 sentences)",
                "reasoning": "Your supporting reasoning or evidence",
                "rhetorical_strategy": "What debate technique you used"
            }}
            
            Be engaging but respectful. Make strong points but acknowledge valid aspects of their argument if any.
            """
            
            response = self.model.generate_content(prompt)
            try:
                result = json.loads(response.text.strip())
                return result
            except:
                return {
                    'argument': response.text.strip(),
                    'reasoning': 'Generated counter-argument',
                    'rhetorical_strategy': 'Direct rebuttal'
                }
                
        except Exception as e:
            return {
                'argument': f"I respectfully disagree with your point. Let me present an alternative perspective on {self.current_debate['topic']}.",
                'reasoning': 'Fallback response due to technical issue',
                'rhetorical_strategy': 'Polite disagreement'
            }

    def evaluate_round(self, user_argument: str, ai_argument: str):
        """Evaluate the strength of arguments in current round"""
        try:
            prompt = f"""
            Evaluate this debate round objectively:
            
            Topic: {self.current_debate['topic']}
            User Argument: {user_argument}
            AI Argument: {ai_argument}
            
            Rate each argument on:
            1. Logic and reasoning (1-10)
            2. Evidence and support (1-10)
            3. Persuasiveness (1-10)
            4. Addressing the topic (1-10)
            
            Return JSON:
            {{
                "user_scores": {{"logic": 8, "evidence": 7, "persuasiveness": 9, "relevance": 8}},
                "ai_scores": {{"logic": 7, "evidence": 8, "persuasiveness": 7, "relevance": 9}},
                "round_winner": "user/ai/tie",
                "feedback": "Brief constructive feedback for both arguments",
                "strongest_point": "What was the strongest point made this round"
            }}
            
            Be fair and objective in evaluation.
            """
            
            response = self.model.generate_content(prompt)
            try:
                evaluation = json.loads(response.text.strip())
                
                # Update scores
                if evaluation['round_winner'] == 'user':
                    self.current_debate['score']['user'] += 1
                elif evaluation['round_winner'] == 'ai':
                    self.current_debate['score']['ai'] += 1
                
                return evaluation
            except:
                return {
                    'user_scores': {'logic': 7, 'evidence': 7, 'persuasiveness': 7, 'relevance': 7},
                    'ai_scores': {'logic': 7, 'evidence': 7, 'persuasiveness': 7, 'relevance': 7},
                    'round_winner': 'tie',
                    'feedback': 'Both arguments presented valid points',
                    'strongest_point': 'Good debate round'
                }
                
        except Exception as e:
            return {
                'user_scores': {'logic': 6, 'evidence': 6, 'persuasiveness': 6, 'relevance': 6},
                'ai_scores': {'logic': 6, 'evidence': 6, 'persuasiveness': 6, 'relevance': 6},
                'round_winner': 'tie',
                'feedback': 'Unable to evaluate due to technical issue',
                'strongest_point': 'Debate continues'
            }

    def end_debate(self):
        """End current debate and provide final evaluation"""
        if self.current_debate['status'] == 'not_started':
            return {'error': 'No active debate to end'}
        
        final_evaluation = self.generate_final_evaluation()
        
        # Update statistics
        self.debate_statistics['total_debates'] += 1
        self.debate_statistics['topics_debated'].append({
            'topic': self.current_debate['topic'],
            'date': datetime.now().isoformat(),
            'winner': final_evaluation['overall_winner']
        })
        
        if final_evaluation['overall_winner'] == 'user':
            self.debate_statistics['user_wins'] += 1
        elif final_evaluation['overall_winner'] == 'ai':
            self.debate_statistics['ai_wins'] += 1
        else:
            self.debate_statistics['draws'] += 1
        
        self.save_debate_stats()
        
        # Reset current debate
        self.current_debate = {
            'topic': '',
            'user_position': '',
            'ai_position': '',
            'arguments': [],
            'counter_arguments': [],
            'debate_flow': [],
            'score': {'user': 0, 'ai': 0},
            'round': 0,
            'status': 'not_started'
        }
        
        return final_evaluation

    def generate_final_evaluation(self):
        """Generate comprehensive final evaluation of the debate"""
        try:
            prompt = f"""
            Provide a comprehensive final evaluation of this debate:
            
            Topic: {self.current_debate['topic']}
            User Position: {self.current_debate['user_position']}
            AI Position: {self.current_debate['ai_position']}
            Total Rounds: {self.current_debate['round']}
            Current Score - User: {self.current_debate['score']['user']}, AI: {self.current_debate['score']['ai']}
            
            Arguments made:
            {json.dumps(self.current_debate['debate_flow'], indent=2)}
            
            Provide JSON evaluation:
            {{
                "overall_winner": "user/ai/draw",
                "final_score": {{"user": 0, "ai": 0}},
                "user_strengths": ["strength1", "strength2"],
                "user_improvements": ["area1", "area2"],
                "ai_strengths": ["strength1", "strength2"],
                "debate_quality": "excellent/good/fair/poor",
                "key_insights": ["insight1", "insight2"],
                "learning_outcomes": ["what was learned"],
                "summary": "Brief summary of the debate"
            }}
            
            Be constructive and educational in feedback.
            """
            
            response = self.model.generate_content(prompt)
            try:
                evaluation = json.loads(response.text.strip())
                return evaluation
            except:
                return {
                    'overall_winner': 'draw',
                    'final_score': self.current_debate['score'],
                    'user_strengths': ['Good participation', 'Engaging arguments'],
                    'user_improvements': ['Continue practicing', 'Research more evidence'],
                    'ai_strengths': ['Logical reasoning', 'Counter-arguments'],
                    'debate_quality': 'good',
                    'key_insights': ['Different perspectives explored'],
                    'learning_outcomes': ['Better understanding of the topic'],
                    'summary': f'Interesting debate about {self.current_debate["topic"]}'
                }
                
        except Exception as e:
            return {
                'overall_winner': 'draw',
                'final_score': self.current_debate['score'],
                'user_strengths': ['Active participation'],
                'user_improvements': ['Keep practicing'],
                'ai_strengths': ['Consistent responses'],
                'debate_quality': 'good',
                'key_insights': ['Good debate experience'],
                'learning_outcomes': ['Practice makes perfect'],
                'summary': f'Debate session completed on: {self.current_debate["topic"]}'
            }

    def get_debate_suggestions(self, category: str = None):
        """Get debate topic suggestions"""
        if category and category in self.debate_categories:
            topics = self.debate_categories[category]
        else:
            # Mix topics from all categories
            topics = []
            for cat_topics in self.debate_categories.values():
                topics.extend(cat_topics)
        
        return {
            'categories': list(self.debate_categories.keys()),
            'suggested_topics': random.sample(topics, min(5, len(topics))),
            'random_topic': random.choice(topics)
        }

    def get_debate_stats(self):
        """Get debate statistics"""
        stats = self.debate_statistics.copy()
        
        # Calculate win rate
        total = stats['total_debates']
        if total > 0:
            stats['user_win_rate'] = round((stats['user_wins'] / total) * 100, 1)
            stats['ai_win_rate'] = round((stats['ai_wins'] / total) * 100, 1)
            stats['draw_rate'] = round((stats['draws'] / total) * 100, 1)
        else:
            stats['user_win_rate'] = 0
            stats['ai_win_rate'] = 0
            stats['draw_rate'] = 0
        
        # Recent topics
        stats['recent_topics'] = stats['topics_debated'][-5:] if len(stats['topics_debated']) > 5 else stats['topics_debated']
        
        return stats

    def get_current_status(self):
        """Get current debate status"""
        return {
            'status': self.current_debate['status'],
            'topic': self.current_debate.get('topic', ''),
            'round': self.current_debate.get('round', 0),
            'score': self.current_debate.get('score', {'user': 0, 'ai': 0}),
            'positions': {
                'user': self.current_debate.get('user_position', ''),
                'ai': self.current_debate.get('ai_position', '')
            }
        }

# Global instance
debate_mode = DebateMode()