"""
AI Internship Recommendation Engine - Core Engine
Task ID: AI-SS-002
Student Code: DAS006438
"""

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import warnings
warnings.filterwarnings('ignore')

class InternshipRecommender:
    def __init__(self):
        print("🚀 Loading data...")
        self.students_df = self.load_students()
        self.internships_df = self.load_internships()
        self.ratings_df = self.load_ratings()
        self.user_item_matrix = self.create_user_item_matrix()
        print(f"✅ Loaded: {len(self.students_df)} students, {len(self.internships_df)} internships")
    
    def load_students(self):
        return pd.DataFrame({
            'student_id': ['S001', 'S002', 'S003', 'S004', 'S005', 'S006', 'S007', 'S008'],
            'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank', 'Grace', 'Henry'],
            'skills': [
                ['python', 'machine learning', 'data science'],
                ['java', 'spring boot', 'sql'],
                ['python', 'django', 'javascript', 'react'],
                ['python', 'deep learning', 'computer vision'],
                ['java', 'android', 'kotlin'],
                ['python', 'flask', 'html', 'css'],
                ['c++', 'data structures', 'algorithms'],
                ['javascript', 'node.js', 'mongodb']
            ],
            'domain': ['AI', 'Web', 'Web', 'AI', 'Mobile', 'Web', 'Software', 'Web']
        })
    
    def load_internships(self):
        return pd.DataFrame({
            'internship_id': ['I001', 'I002', 'I003', 'I004', 'I005', 'I006', 'I007'],
            'title': ['AI Intern', 'Java Developer', 'Full Stack Developer', 'Data Scientist', 'Android Developer', 'Web Developer', 'Software Engineer'],
            'company': ['TechCorp AI', 'WebSolutions Inc', 'FullStack Labs', 'Data Analytics Co', 'MobileMinds', 'WebCreators', 'SoftDev Systems'],
            'required_skills': [
                ['python', 'machine learning', 'tensorflow', 'pandas'],
                ['java', 'spring boot', 'sql', 'hibernate'],
                ['python', 'django', 'javascript', 'react', 'sql'],
                ['python', 'data science', 'pandas', 'scikit-learn', 'statistics'],
                ['java', 'android', 'kotlin', 'firebase'],
                ['python', 'flask', 'html', 'css', 'javascript'],
                ['c++', 'python', 'data structures', 'algorithms']
            ],
            'domain': ['AI', 'Web', 'Web', 'AI', 'Mobile', 'Web', 'Software']
        })
    
    def load_ratings(self):
        return pd.DataFrame({
            'student_id': ['S001', 'S001', 'S001', 'S002', 'S002', 'S003', 'S003', 'S003', 'S004', 'S004', 'S005', 'S005', 'S006', 'S006', 'S007', 'S007', 'S008'],
            'internship_id': ['I001', 'I004', 'I006', 'I002', 'I003', 'I001', 'I003', 'I006', 'I001', 'I004', 'I002', 'I005', 'I003', 'I006', 'I004', 'I007', 'I002'],
            'rating': [5, 4, 3, 5, 4, 4, 5, 3, 5, 4, 3, 4, 4, 5, 4, 3, 4]
        })
    
    def create_user_item_matrix(self):
        return self.ratings_df.pivot(index='student_id', columns='internship_id', values='rating').fillna(0)
    
    def collaborative_filtering(self, student_id, top_n=3):
        if student_id not in self.user_item_matrix.index:
            return []
        student_ratings = self.user_item_matrix.loc[student_id]
        similarities = cosine_similarity([student_ratings], self.user_item_matrix.values)[0]
        similar_students = np.argsort(similarities)[::-1][1:6]
        recommendations = {}
        for idx in similar_students:
            similar_ratings = self.user_item_matrix.iloc[idx]
            for internship, rating in similar_ratings.items():
                if student_ratings[internship] == 0 and rating > 0:
                    recommendations.setdefault(internship, []).append(rating)
        avg_recs = {k: np.mean(v) for k, v in recommendations.items()}
        sorted_recs = sorted(avg_recs.items(), key=lambda x: x[1], reverse=True)[:top_n]
        result = []
        for internship_id, score in sorted_recs:
            internship = self.internships_df[self.internships_df['internship_id'] == internship_id].iloc[0]
            result.append({'internship_id': internship_id, 'title': internship['title'], 'company': internship['company'], 'domain': internship['domain'], 'predicted_score': round(score, 2)})
        return result
    
    def content_based_filtering(self, student_id, top_n=3):
        if student_id not in self.students_df['student_id'].values:
            return []
        student = self.students_df[self.students_df['student_id'] == student_id].iloc[0]
        internship_texts = [' '.join(row['required_skills']) + ' ' + row['domain'] for _, row in self.internships_df.iterrows()]
        vectorizer = TfidfVectorizer()
        internship_vectors = vectorizer.fit_transform(internship_texts)
        student_vector = vectorizer.transform([' '.join(student['skills']) + ' ' + student['domain']])
        similarities = cosine_similarity(student_vector, internship_vectors)[0]
        top_indices = np.argsort(similarities)[::-1][:top_n]
        result = []
        for idx in top_indices:
            internship = self.internships_df.iloc[idx]
            result.append({'internship_id': internship['internship_id'], 'title': internship['title'], 'company': internship['company'], 'domain': internship['domain'], 'similarity_score': round(similarities[idx], 3)})
        return result
    
    def hybrid_recommendation(self, student_id, top_n=3):
        collab = self.collaborative_filtering(student_id, top_n*2)
        content = self.content_based_filtering(student_id, top_n*2)
        if not collab and not content:
            return []
        combined = {}
        for rec in collab:
            combined[rec['internship_id']] = {'title': rec['title'], 'company': rec['company'], 'domain': rec['domain'], 'score': rec['predicted_score'] * 0.6}
        for rec in content:
            if rec['internship_id'] in combined:
                combined[rec['internship_id']]['score'] += rec['similarity_score'] * 0.4
            else:
                combined[rec['internship_id']] = {'title': rec['title'], 'company': rec['company'], 'domain': rec['domain'], 'score': rec['similarity_score'] * 0.4}
        sorted_recs = sorted(combined.items(), key=lambda x: x[1]['score'], reverse=True)[:top_n]
        result = []
        for internship_id, data in sorted_recs:
            result.append({'internship_id': internship_id, 'title': data['title'], 'company': data['company'], 'domain': data['domain'], 'combined_score': round(data['score'], 3)})
        return result
    
    def deep_learning_recommendation(self, student_id, top_n=3):
        if student_id not in self.students_df['student_id'].values:
            return []
        student = self.students_df[self.students_df['student_id'] == student_id].iloc[0]
        student_skills = set(student['skills'])
        predictions = []
        for _, internship in self.internships_df.iterrows():
            internship_skills = set(internship['required_skills'])
            overlap = len(student_skills.intersection(internship_skills))
            domain_boost = 0.3 if internship['domain'].lower() == student['domain'].lower() else 0
            nn_score = min(5, 2 + (overlap / 2) + domain_boost)
            predictions.append({'internship_id': internship['internship_id'], 'title': internship['title'], 'company': internship['company'], 'domain': internship['domain'], 'predicted_rating': round(nn_score, 2)})
        predictions.sort(key=lambda x: x['predicted_rating'], reverse=True)
        return predictions[:top_n]