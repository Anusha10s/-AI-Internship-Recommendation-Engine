"""
User Feedback Integration
Task ID: AI-SS-002
Student Code: DAS006438
"""

from datetime import datetime

class FeedbackAnalyzer:
    def __init__(self):
        self.feedback_data = []
    
    def add_feedback(self, user_id, internship_id, rating, comment, tags=None):
        feedback = {
            'user_id': user_id,
            'internship_id': internship_id,
            'rating': rating,
            'comment': comment,
            'tags': tags or [],
            'timestamp': datetime.now().isoformat(),
            'sentiment': self.analyze_sentiment(comment)
        }
        self.feedback_data.append(feedback)
        return feedback
    
    def analyze_sentiment(self, text):
        text_lower = text.lower()
        positive_words = ['great', 'good', 'excellent', 'amazing', 'awesome', 'love']
        negative_words = ['bad', 'poor', 'terrible', 'awful', 'hate']
        
        positive_score = sum(1 for w in positive_words if w in text_lower)
        negative_score = sum(1 for w in negative_words if w in text_lower)
        
        if positive_score > negative_score:
            return 'positive'
        elif negative_score > positive_score:
            return 'negative'
        else:
            return 'neutral'
    
    def get_feedback_stats(self):
        if not self.feedback_data:
            return {'total_feedback': 0, 'average_rating': 0}
        
        ratings = [f['rating'] for f in self.feedback_data]
        return {
            'total_feedback': len(self.feedback_data),
            'average_rating': sum(ratings) / len(ratings) if ratings else 0
        }
    
    def get_recommendations_with_feedback(self, recommendations):
        enhanced = []
        for rec in recommendations:
            rec_copy = rec.copy()
            feedback_list = [f for f in self.feedback_data if f['internship_id'] == rec['internship_id']]
            if feedback_list:
                avg_rating = sum(f['rating'] for f in feedback_list) / len(feedback_list)
                rec_copy['user_rating'] = round(avg_rating, 2)
                rec_copy['feedback_count'] = len(feedback_list)
            else:
                rec_copy['user_rating'] = 'No feedback'
                rec_copy['feedback_count'] = 0
            enhanced.append(rec_copy)
        return enhanced