"""
Personal Learning Assistant - Tracking & Progress Module
=======================================================
Tracks user learning progress, quiz scores, session data, and educational metrics.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
from dataclasses import dataclass, asdict


@dataclass
class LearningSession:
    """Data class for learning session"""
    session_id: str
    user_name: str
    subject: str
    topic: str
    start_time: str
    end_time: Optional[str] = None
    duration_minutes: float = 0.0
    interactions: int = 0
    quiz_score: Optional[float] = None
    completed: bool = False
    difficulty_level: int = 1


@dataclass
class QuizResult:
    """Data class for quiz results"""
    quiz_id: str
    session_id: str
    subject: str
    topic: str
    total_questions: int
    correct_answers: int
    score_percentage: float
    time_taken_seconds: float
    difficulty_level: int
    timestamp: str


@dataclass
class UserProgress:
    """Data class for overall user progress"""
    user_name: str
    total_sessions: int
    total_time_minutes: float
    subjects_studied: List[str]
    average_quiz_score: float
    current_streak: int
    best_streak: int
    last_activity: str
    achievements: List[str]
    weak_topics: List[str]
    strong_topics: List[str]


class LearningTracker:
    """Main class for tracking learning progress and analytics"""
    
    def __init__(self, data_dir: str = "learning_data"):
        self.data_dir = data_dir
        self.sessions_file = os.path.join(data_dir, "learning_sessions.json")
        self.quizzes_file = os.path.join(data_dir, "quiz_results.json")
        self.progress_file = os.path.join(data_dir, "user_progress.json")
        self.achievements_file = os.path.join(data_dir, "achievements.json")
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize data files
        self._initialize_files()
        
        # Load current data
        self.sessions = self._load_sessions()
        self.quiz_results = self._load_quiz_results()
        self.user_progress = self._load_user_progress()
        
        print("📊 Learning Tracker initialized")
    
    def _initialize_files(self):
        """Initialize JSON files if they don't exist"""
        files_to_init = [
            (self.sessions_file, []),
            (self.quizzes_file, []),
            (self.progress_file, {}),
            (self.achievements_file, self._get_default_achievements())
        ]
        
        for file_path, default_data in files_to_init:
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump(default_data, f, indent=2)
    
    def _get_default_achievements(self) -> Dict:
        """Get default achievements configuration"""
        return {
            "First Quiz": {"description": "Complete your first quiz", "unlocked": False},
            "Perfect Score": {"description": "Score 100% on a quiz", "unlocked": False},
            "Study Streak": {"description": "Study for 7 consecutive days", "unlocked": False},
            "Math Master": {"description": "Complete 10 math quizzes", "unlocked": False},
            "Language Learner": {"description": "Complete 10 language exercises", "unlocked": False},
            "Science Explorer": {"description": "Complete 10 science quizzes", "unlocked": False},
            "Quick Learner": {"description": "Complete a quiz in under 2 minutes", "unlocked": False},
            "Persistent Student": {"description": "Study for 5 hours total", "unlocked": False},
            "Knowledge Seeker": {"description": "Ask 100 questions", "unlocked": False},
            "Improvement": {"description": "Improve quiz score by 20%", "unlocked": False}
        }
    
    def _load_sessions(self) -> List[LearningSession]:
        """Load learning sessions from file"""
        try:
            with open(self.sessions_file, 'r') as f:
                data = json.load(f)
                return [LearningSession(**session) for session in data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _load_quiz_results(self) -> List[QuizResult]:
        """Load quiz results from file"""
        try:
            with open(self.quizzes_file, 'r') as f:
                data = json.load(f)
                return [QuizResult(**quiz) for quiz in data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _load_user_progress(self) -> Dict[str, UserProgress]:
        """Load user progress from file"""
        try:
            with open(self.progress_file, 'r') as f:
                data = json.load(f)
                return {username: UserProgress(**progress) for username, progress in data.items()}
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_sessions(self):
        """Save learning sessions to file"""
        with open(self.sessions_file, 'w') as f:
            json.dump([asdict(session) for session in self.sessions], f, indent=2)
    
    def _save_quiz_results(self):
        """Save quiz results to file"""
        with open(self.quizzes_file, 'w') as f:
            json.dump([asdict(quiz) for quiz in self.quiz_results], f, indent=2)
    
    def _save_user_progress(self):
        """Save user progress to file"""
        with open(self.progress_file, 'w') as f:
            json.dump({username: asdict(progress) for username, progress in self.user_progress.items()}, f, indent=2)
    
    def start_learning_session(self, user_name: str, subject: str, topic: str, difficulty: int = 1) -> str:
        """Start a new learning session"""
        session_id = f"{user_name}_{subject}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        session = LearningSession(
            session_id=session_id,
            user_name=user_name,
            subject=subject,
            topic=topic,
            start_time=datetime.now().isoformat(),
            difficulty_level=difficulty
        )
        
        self.sessions.append(session)
        self._save_sessions()
        
        print(f"📚 Started learning session: {subject} - {topic}")
        return session_id
    
    def end_learning_session(self, session_id: str, interactions: int = 0) -> bool:
        """End a learning session"""
        for session in self.sessions:
            if session.session_id == session_id:
                session.end_time = datetime.now().isoformat()
                session.interactions = interactions
                session.completed = True
                
                # Calculate duration
                start_time = datetime.fromisoformat(session.start_time)
                end_time = datetime.fromisoformat(session.end_time)
                session.duration_minutes = (end_time - start_time).total_seconds() / 60
                
                self._save_sessions()
                self._update_user_progress(session.user_name)
                
                print(f"✅ Ended learning session: {session.duration_minutes:.1f} minutes")
                return True
        
        return False
    
    def record_quiz_result(self, session_id: str, subject: str, topic: str, 
                          total_questions: int, correct_answers: int, 
                          time_taken_seconds: float, difficulty: int = 1) -> str:
        """Record quiz result"""
        quiz_id = f"quiz_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        score_percentage = (correct_answers / total_questions) * 100
        
        quiz_result = QuizResult(
            quiz_id=quiz_id,
            session_id=session_id,
            subject=subject,
            topic=topic,
            total_questions=total_questions,
            correct_answers=correct_answers,
            score_percentage=score_percentage,
            time_taken_seconds=time_taken_seconds,
            difficulty_level=difficulty,
            timestamp=datetime.now().isoformat()
        )
        
        self.quiz_results.append(quiz_result)
        self._save_quiz_results()
        
        # Update session with quiz score
        for session in self.sessions:
            if session.session_id == session_id:
                session.quiz_score = score_percentage
                break
        
        self._save_sessions()
        self._update_user_progress(self._get_user_from_session(session_id))
        self._check_achievements(self._get_user_from_session(session_id), quiz_result)
        
        print(f"📝 Quiz recorded: {correct_answers}/{total_questions} ({score_percentage:.1f}%)")
        return quiz_id
    
    def _get_user_from_session(self, session_id: str) -> str:
        """Get username from session ID"""
        for session in self.sessions:
            if session.session_id == session_id:
                return session.user_name
        return "Unknown"
    
    def _update_user_progress(self, user_name: str):
        """Update overall user progress"""
        user_sessions = [s for s in self.sessions if s.user_name == user_name]
        user_quizzes = [q for q in self.quiz_results if self._get_user_from_session(q.session_id) == user_name]
        
        if not user_sessions:
            return
        
        # Calculate metrics
        total_sessions = len(user_sessions)
        total_time = sum(s.duration_minutes for s in user_sessions if s.duration_minutes > 0)
        subjects_studied = list(set(s.subject for s in user_sessions))
        
        avg_quiz_score = 0
        if user_quizzes:
            avg_quiz_score = sum(q.score_percentage for q in user_quizzes) / len(user_quizzes)
        
        # Calculate streak
        current_streak = self._calculate_streak(user_name)
        best_streak = self._calculate_best_streak(user_name)
        
        # Identify weak and strong topics
        weak_topics, strong_topics = self._analyze_topics(user_name)
        
        # Create or update progress
        progress = UserProgress(
            user_name=user_name,
            total_sessions=total_sessions,
            total_time_minutes=total_time,
            subjects_studied=subjects_studied,
            average_quiz_score=avg_quiz_score,
            current_streak=current_streak,
            best_streak=best_streak,
            last_activity=datetime.now().isoformat(),
            achievements=self._get_user_achievements(user_name),
            weak_topics=weak_topics,
            strong_topics=strong_topics
        )
        
        self.user_progress[user_name] = progress
        self._save_user_progress()
    
    def _calculate_streak(self, user_name: str) -> int:
        """Calculate current learning streak"""
        user_sessions = [s for s in self.sessions if s.user_name == user_name and s.completed]
        if not user_sessions:
            return 0
        
        # Sort by start time
        sorted_sessions = sorted(user_sessions, key=lambda x: x.start_time, reverse=True)
        
        streak = 0
        current_date = datetime.now().date()
        
        for session in sorted_sessions:
            session_date = datetime.fromisoformat(session.start_time).date()
            days_diff = (current_date - session_date).days
            
            if days_diff == streak:
                streak += 1
                current_date = session_date
            elif days_diff > streak + 1:
                break
        
        return streak
    
    def _calculate_best_streak(self, user_name: str) -> int:
        """Calculate best streak ever achieved"""
        # Simplified calculation - could be enhanced
        return max(self._calculate_streak(user_name), 
                  self.user_progress.get(user_name, UserProgress("", 0, 0, [], 0, 0, 0, "", [], [], [])).best_streak)
    
    def _analyze_topics(self, user_name: str) -> tuple:
        """Analyze weak and strong topics based on quiz performance"""
        user_quizzes = [q for q in self.quiz_results if self._get_user_from_session(q.session_id) == user_name]
        
        if not user_quizzes:
            return [], []
        
        # Group by topic and calculate average scores
        topic_scores = {}
        for quiz in user_quizzes:
            if quiz.topic not in topic_scores:
                topic_scores[quiz.topic] = []
            topic_scores[quiz.topic].append(quiz.score_percentage)
        
        # Calculate averages
        topic_averages = {topic: sum(scores)/len(scores) for topic, scores in topic_scores.items()}
        
        # Classify as weak (< 70%) or strong (> 85%)
        weak_topics = [topic for topic, avg in topic_averages.items() if avg < 70]
        strong_topics = [topic for topic, avg in topic_averages.items() if avg > 85]
        
        return weak_topics, strong_topics
    
    def _get_user_achievements(self, user_name: str) -> List[str]:
        """Get list of achieved accomplishments for user"""
        # This would be populated by _check_achievements
        return []
    
    def _check_achievements(self, user_name: str, quiz_result: QuizResult):
        """Check and unlock achievements"""
        try:
            with open(self.achievements_file, 'r') as f:
                achievements = json.load(f)
            
            unlocked = False
            
            # Check various achievement conditions
            if quiz_result.score_percentage == 100 and not achievements["Perfect Score"]["unlocked"]:
                achievements["Perfect Score"]["unlocked"] = True
                unlocked = True
                print("🏆 Achievement Unlocked: Perfect Score!")
            
            if quiz_result.time_taken_seconds < 120 and not achievements["Quick Learner"]["unlocked"]:
                achievements["Quick Learner"]["unlocked"] = True
                unlocked = True
                print("🏆 Achievement Unlocked: Quick Learner!")
            
            # Check subject-specific achievements
            user_quizzes = [q for q in self.quiz_results if self._get_user_from_session(q.session_id) == user_name]
            subject_counts = {}
            for quiz in user_quizzes:
                subject_counts[quiz.subject] = subject_counts.get(quiz.subject, 0) + 1
            
            for subject, count in subject_counts.items():
                achievement_key = f"{subject.title()} Master"
                if count >= 10 and achievement_key in achievements and not achievements[achievement_key]["unlocked"]:
                    achievements[achievement_key]["unlocked"] = True
                    unlocked = True
                    print(f"🏆 Achievement Unlocked: {achievement_key}!")
            
            if unlocked:
                with open(self.achievements_file, 'w') as f:
                    json.dump(achievements, f, indent=2)
                    
        except Exception as e:
            print(f"Error checking achievements: {e}")
    
    def get_user_stats(self, user_name: str) -> Dict[str, Any]:
        """Get comprehensive user statistics"""
        if user_name not in self.user_progress:
            return {"error": "User not found"}
        
        progress = self.user_progress[user_name]
        user_sessions = [s for s in self.sessions if s.user_name == user_name]
        user_quizzes = [q for q in self.quiz_results if self._get_user_from_session(q.session_id) == user_name]
        
        return {
            "user_name": user_name,
            "total_sessions": progress.total_sessions,
            "total_time_hours": round(progress.total_time_minutes / 60, 2),
            "subjects_studied": progress.subjects_studied,
            "average_quiz_score": round(progress.average_quiz_score, 1),
            "current_streak": progress.current_streak,
            "best_streak": progress.best_streak,
            "total_quizzes": len(user_quizzes),
            "weak_topics": progress.weak_topics,
            "strong_topics": progress.strong_topics,
            "last_activity": progress.last_activity,
            "recent_sessions": [asdict(s) for s in user_sessions[-5:]],
            "recent_quizzes": [asdict(q) for q in user_quizzes[-5:]]
        }
    
    def get_learning_analytics(self, user_name: str = None) -> Dict[str, Any]:
        """Get learning analytics and trends"""
        if user_name:
            sessions = [s for s in self.sessions if s.user_name == user_name]
            quizzes = [q for q in self.quiz_results if self._get_user_from_session(q.session_id) == user_name]
        else:
            sessions = self.sessions
            quizzes = self.quiz_results
        
        if not sessions:
            return {"error": "No data available"}
        
        # Create DataFrames for analysis
        sessions_df = pd.DataFrame([asdict(s) for s in sessions])
        quizzes_df = pd.DataFrame([asdict(q) for q in quizzes]) if quizzes else pd.DataFrame()
        
        analytics = {
            "total_sessions": len(sessions),
            "total_time_hours": sessions_df['duration_minutes'].sum() / 60,
            "average_session_duration": sessions_df['duration_minutes'].mean(),
            "subjects_distribution": sessions_df['subject'].value_counts().to_dict(),
            "difficulty_distribution": sessions_df['difficulty_level'].value_counts().to_dict(),
        }
        
        if not quizzes_df.empty:
            analytics.update({
                "total_quizzes": len(quizzes),
                "average_quiz_score": quizzes_df['score_percentage'].mean(),
                "quiz_score_trend": quizzes_df.groupby(quizzes_df['timestamp'].str[:10])['score_percentage'].mean().to_dict(),
                "subject_performance": quizzes_df.groupby('subject')['score_percentage'].mean().to_dict()
            })
        
        return analytics
    
    def export_progress_report(self, user_name: str) -> Dict[str, Any]:
        """Export comprehensive progress report"""
        stats = self.get_user_stats(user_name)
        analytics = self.get_learning_analytics(user_name)
        
        report = {
            "report_generated": datetime.now().isoformat(),
            "user_stats": stats,
            "analytics": analytics,
            "recommendations": self._generate_recommendations(user_name)
        }
        
        # Save report to file
        report_file = os.path.join(self.data_dir, f"{user_name}_progress_report.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Progress report exported: {report_file}")
        return report
    
    def _generate_recommendations(self, user_name: str) -> List[str]:
        """Generate personalized learning recommendations"""
        if user_name not in self.user_progress:
            return ["Start your learning journey today!"]
        
        progress = self.user_progress[user_name]
        recommendations = []
        
        # Based on weak topics
        if progress.weak_topics:
            recommendations.append(f"Focus on improving: {', '.join(progress.weak_topics[:3])}")
        
        # Based on streak
        if progress.current_streak == 0:
            recommendations.append("Try to study daily to build a learning streak")
        elif progress.current_streak < 7:
            recommendations.append("Keep up the daily study habit to reach a 7-day streak")
        
        # Based on quiz performance
        if progress.average_quiz_score < 70:
            recommendations.append("Practice more quizzes to improve your scores")
        elif progress.average_quiz_score > 90:
            recommendations.append("Try increasing difficulty level for more challenge")
        
        # Based on subjects
        if len(progress.subjects_studied) < 3:
            recommendations.append("Explore new subjects to broaden your knowledge")
        
        return recommendations if recommendations else ["Great job! Keep up the excellent work!"]


# Global tracker instance
learning_tracker = LearningTracker()


# Utility functions for easy integration
def start_session(user_name: str, subject: str, topic: str, difficulty: int = 1) -> str:
    """Start a learning session"""
    return learning_tracker.start_learning_session(user_name, subject, topic, difficulty)


def end_session(session_id: str, interactions: int = 0) -> bool:
    """End a learning session"""
    return learning_tracker.end_learning_session(session_id, interactions)


def record_quiz(session_id: str, subject: str, topic: str, total: int, correct: int, time_taken: float, difficulty: int = 1) -> str:
    """Record quiz result"""
    return learning_tracker.record_quiz_result(session_id, subject, topic, total, correct, time_taken, difficulty)


def get_stats(user_name: str) -> Dict[str, Any]:
    """Get user statistics"""
    return learning_tracker.get_user_stats(user_name)


if __name__ == "__main__":
    print("🎓 Learning Tracker Module")
    print("=" * 30)
    
    # Demo usage
    tracker = LearningTracker()
    
    # Start a session
    session_id = tracker.start_learning_session("Alice", "Math", "Algebra", 2)
    
    # Record a quiz
    quiz_id = tracker.record_quiz_result(session_id, "Math", "Algebra", 10, 8, 180, 2)
    
    # End session
    tracker.end_learning_session(session_id, 5)
    
    # Get stats
    stats = tracker.get_user_stats("Alice")
    print("📊 User Stats:", stats)
    
    print("✅ Learning Tracker ready for integration!")