"""
Deep Learning Recommendation - Neural Network Version
Task ID: AI-SS-002
Student Code: DAS006438
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

# Try to import TensorFlow, fallback to simple version if not available
try:
    import tensorflow as tf
    from tensorflow.keras import layers, Model
    from tensorflow.keras.layers import Input, Embedding, Flatten, Dense, Concatenate, Dropout
    from tensorflow.keras.optimizers import Adam
    TENSORFLOW_AVAILABLE = True
    print("✅ TensorFlow loaded successfully!")
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("⚠️ TensorFlow not available. Using fallback.")

class DeepLearningRecommender:
    def __init__(self, students_df, internships_df, ratings_df):
        self.students_df = students_df
        self.internships_df = internships_df
        self.ratings_df = ratings_df
        
        self.student_ids = students_df['student_id'].unique()
        self.internship_ids = internships_df['internship_id'].unique()
        
        self.student_encoder = LabelEncoder()
        self.internship_encoder = LabelEncoder()
        
        self.student_encoder.fit(self.student_ids)
        self.internship_encoder.fit(self.internship_ids)
        
        self.n_students = len(self.student_ids)
        self.n_internships = len(self.internship_ids)
        
        if TENSORFLOW_AVAILABLE:
            self.prepare_data()
            self.build_model()
            self.train_model()
    
    def prepare_data(self):
        interactions = []
        for _, row in self.ratings_df.iterrows():
            student_id = row['student_id']
            internship_id = row['internship_id']
            rating = row['rating']
            
            student_idx = self.student_encoder.transform([student_id])[0]
            internship_idx = self.internship_encoder.transform([internship_id])[0]
            
            interactions.append({
                'student_idx': student_idx,
                'internship_idx': internship_idx,
                'rating': rating
            })
        
        self.interactions_df = pd.DataFrame(interactions)
        self.X = self.interactions_df[['student_idx', 'internship_idx']].values
        self.y = self.interactions_df['rating'].values
        
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=0.2, random_state=42
        )
    
    def build_model(self):
        if not TENSORFLOW_AVAILABLE:
            return
        
        student_input = Input(shape=(1,), name='student_input')
        internship_input = Input(shape=(1,), name='internship_input')
        
        student_embedding = Embedding(
            input_dim=self.n_students,
            output_dim=50,
            name='student_embedding'
        )(student_input)
        student_embedding = Flatten()(student_embedding)
        
        internship_embedding = Embedding(
            input_dim=self.n_internships,
            output_dim=50,
            name='internship_embedding'
        )(internship_input)
        internship_embedding = Flatten()(internship_embedding)
        
        concat = Concatenate()([student_embedding, internship_embedding])
        
        dense1 = Dense(128, activation='relu')(concat)
        dropout1 = Dropout(0.2)(dense1)
        dense2 = Dense(64, activation='relu')(dropout1)
        dropout2 = Dropout(0.2)(dense2)
        dense3 = Dense(32, activation='relu')(dropout2)
        
        output = Dense(1, activation='linear', name='output')(dense3)
        
        self.model = Model(
            inputs=[student_input, internship_input],
            outputs=output
        )
        
        self.model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
    
    def train_model(self, epochs=30, batch_size=16):
        if not TENSORFLOW_AVAILABLE:
            return
        
        train_students = self.X_train[:, 0]
        train_internships = self.X_train[:, 1]
        
        self.history = self.model.fit(
            [train_students, train_internships],
            self.y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=0.1,
            verbose=1
        )
    
    def predict_rating(self, student_id, internship_id):
        if not TENSORFLOW_AVAILABLE:
            return 3.5
        
        try:
            student_idx = self.student_encoder.transform([student_id])[0]
            internship_idx = self.internship_encoder.transform([internship_id])[0]
            
            prediction = self.model.predict(
                [[student_idx], [internship_idx]],
                verbose=0
            )[0][0]
            
            return max(1, min(5, prediction))
        except:
            return 3.5
    
    def get_recommendations(self, student_id, top_n=3):
        if student_id not in self.student_encoder.classes_:
            return []
        
        recommendations = []
        for internship_id in self.internship_ids:
            predicted_rating = self.predict_rating(student_id, internship_id)
            internship = self.internships_df[
                self.internships_df['internship_id'] == internship_id
            ].iloc[0]
            
            recommendations.append({
                'internship_id': internship_id,
                'title': internship['title'],
                'company': internship['company'],
                'domain': internship['domain'],
                'predicted_rating': round(predicted_rating, 2)
            })
        
        recommendations.sort(key=lambda x: x['predicted_rating'], reverse=True)
        return recommendations[:top_n]