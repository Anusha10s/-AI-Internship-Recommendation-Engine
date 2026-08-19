"""
AI Internship Recommendation Engine - Complete App with ALL Features
Task ID: AI-SS-002
Student Code: DAS006438
"""

from flask import Flask, render_template, request, jsonify
from recommendation_engine import InternshipRecommender
import random
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
recommender = InternshipRecommender()

# ============================================
# DATA STORAGE (In-memory for simplicity)
# ============================================

feedback_data = []
ab_test_data = {'variant_A': {'views': 0, 'clicks': 0}, 'variant_B': {'views': 0, 'clicks': 0}}
user_assignments = {}
real_time_active = False
current_realtime_student = None

# ============================================
# MAIN ROUTES
# ============================================

@app.route("/")
def home():
    students = recommender.students_df['student_id'].tolist()
    student_names = dict(zip(recommender.students_df['student_id'], recommender.students_df['name']))
    return render_template('index.html', students=students, student_names=student_names)

@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json()
    student_id = data.get('student_id', '')
    if not student_id:
        return jsonify({'error': 'Student ID required'}), 400
    
    collab = recommender.collaborative_filtering(student_id)
    content = recommender.content_based_filtering(student_id)
    hybrid = recommender.hybrid_recommendation(student_id)
    deep = recommender.deep_learning_recommendation(student_id)
    
    student = recommender.students_df[recommender.students_df['student_id'] == student_id]
    student_info = {}
    if not student.empty:
        student_info = {
            'id': student.iloc[0]['student_id'],
            'name': student.iloc[0]['name'],
            'domain': student.iloc[0]['domain'],
            'skills': student.iloc[0]['skills']
        }
    
    return jsonify({
        'student': student_info,
        'collaborative': collab,
        'content_based': content,
        'hybrid': hybrid,
        'deep_learning': deep
    })

# ============================================
# FEATURE 1: DEEP LEARNING RECOMMENDATION ✅
# ============================================

@app.route("/deep_learning", methods=["POST"])
def deep_learning():
    data = request.get_json()
    student_id = data.get('student_id', '')
    if not student_id:
        return jsonify({'error': 'Student ID required'}), 400
    recs = recommender.deep_learning_recommendation(student_id)
    return jsonify({'recommendations': recs})

# ============================================
# FEATURE 2: REAL-TIME RECOMMENDATION UPDATES ✅
# ============================================

@app.route("/real_time/start", methods=["POST"])
def start_real_time():
    global real_time_active, current_realtime_student
    data = request.get_json()
    student_id = data.get('student_id', '')
    if not student_id:
        return jsonify({'error': 'Student ID required'}), 400
    real_time_active = True
    current_realtime_student = student_id
    return jsonify({'success': True, 'message': f'Real-time updates started for {student_id}'})

@app.route("/real_time/stop", methods=["POST"])
def stop_real_time():
    global real_time_active, current_realtime_student
    real_time_active = False
    current_realtime_student = None
    return jsonify({'success': True, 'message': 'Real-time updates stopped'})

@app.route("/real_time/update", methods=["GET"])
def get_realtime_update():
    if not real_time_active or not current_realtime_student:
        return jsonify({'error': 'No active real-time session'}), 400
    collab = recommender.collaborative_filtering(current_realtime_student)
    content = recommender.content_based_filtering(current_realtime_student)
    hybrid = recommender.hybrid_recommendation(current_realtime_student)
    deep = recommender.deep_learning_recommendation(current_realtime_student)
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'student_id': current_realtime_student,
        'collaborative': collab,
        'content_based': content,
        'hybrid': hybrid,
        'deep_learning': deep
    })

# ============================================
# FEATURE 3: VISUALIZATION DASHBOARD ✅
# ============================================

@app.route("/dashboard")
def dashboard():
    students = recommender.students_df['student_id'].tolist()
    student_names = dict(zip(recommender.students_df['student_id'], recommender.students_df['name']))
    return render_template('dashboard.html', students=students, student_names=student_names)

@app.route("/api/visualization/<student_id>", methods=["GET"])
def get_visualization(student_id):
    # Generate chart data
    collab = recommender.collaborative_filtering(student_id)
    content = recommender.content_based_filtering(student_id)
    hybrid = recommender.hybrid_recommendation(student_id)
    deep = recommender.deep_learning_recommendation(student_id)
    
    chart_data = {
        'labels': ['Collaborative', 'Content', 'Hybrid', 'Deep Learning'],
        'counts': [len(collab), len(content), len(hybrid), len(deep)],
        'details': {
            'collaborative': collab,
            'content': content,
            'hybrid': hybrid,
            'deep': deep
        }
    }
    return jsonify(chart_data)

# ============================================
# FEATURE 4: WEB API WITH FLASK ✅
# ============================================

@app.route("/api/v1/recommend/<student_id>", methods=["GET"])
def api_recommend(student_id):
    collab = recommender.collaborative_filtering(student_id)
    content = recommender.content_based_filtering(student_id)
    hybrid = recommender.hybrid_recommendation(student_id)
    deep = recommender.deep_learning_recommendation(student_id)
    student = recommender.students_df[recommender.students_df['student_id'] == student_id]
    student_info = {}
    if not student.empty:
        student_info = {'id': student.iloc[0]['student_id'], 'name': student.iloc[0]['name'], 'domain': student.iloc[0]['domain'], 'skills': student.iloc[0]['skills']}
    return jsonify({'student': student_info, 'recommendations': {'collaborative': collab, 'content_based': content, 'hybrid': hybrid, 'deep_learning': deep}})

@app.route("/api/v1/students", methods=["GET"])
def api_students():
    return jsonify({'students': recommender.students_df.to_dict('records')})

@app.route("/api/v1/internships", methods=["GET"])
def api_internships():
    return jsonify({'internships': recommender.internships_df.to_dict('records')})

# ============================================
# FEATURE 5: A/B TESTING FRAMEWORK ✅
# ============================================

@app.route("/ab_test", methods=["POST"])
def ab_test():
    data = request.get_json()
    user_id = data.get('user_id', '')
    if not user_id:
        return jsonify({'error': 'User ID required'}), 400
    
    # Assign variant if not already assigned
    if user_id not in user_assignments:
        variant = random.choice(['A', 'B'])
        user_assignments[user_id] = variant
    else:
        variant = user_assignments[user_id]
    
    # Track view
    ab_test_data[f'variant_{variant}']['views'] += 1
    
    # Get recommendations based on variant
    if variant == 'A':
        recs = recommender.collaborative_filtering(user_id)
        method = 'collaborative'
    else:
        recs = recommender.hybrid_recommendation(user_id)
        method = 'hybrid'
    
    return jsonify({
        'variant': variant,
        'method': method,
        'recommendations': recs
    })

@app.route("/ab_test/results", methods=["GET"])
def ab_test_results():
    return jsonify({
        'variant_A': ab_test_data['variant_A'],
        'variant_B': ab_test_data['variant_B']
    })

# ============================================
# FEATURE 6: USER FEEDBACK INTEGRATION ✅
# ============================================

@app.route("/feedback", methods=["POST"])
def add_feedback():
    data = request.get_json()
    user_id = data.get('user_id', '')
    internship_id = data.get('internship_id', '')
    rating = data.get('rating', 0)
    comment = data.get('comment', '')
    
    if not user_id or not internship_id:
        return jsonify({'error': 'User ID and Internship ID required'}), 400
    
    feedback = {
        'user_id': user_id,
        'internship_id': internship_id,
        'rating': rating,
        'comment': comment,
        'timestamp': datetime.now().isoformat()
    }
    feedback_data.append(feedback)
    return jsonify({'success': True, 'feedback': feedback})

@app.route("/feedback/stats", methods=["GET"])
def feedback_stats():
    if not feedback_data:
        return jsonify({'total': 0, 'avg_rating': 0, 'count': 0})
    ratings = [f['rating'] for f in feedback_data]
    return jsonify({
        'total': len(feedback_data),
        'avg_rating': round(sum(ratings) / len(ratings), 2),
        'count': len(feedback_data)
    })

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 AI Internship Recommendation Engine")
    print("="*50)
    print("📋 ALL FEATURES ENABLED:")
    print("   ✅ 1. Deep Learning Recommendation")
    print("   ✅ 2. Real-time Recommendation Updates")
    print("   ✅ 3. Visualization Dashboard")
    print("   ✅ 4. Web API with Flask")
    print("   ✅ 5. A/B Testing Framework")
    print("   ✅ 6. User Feedback Integration")
    print("="*50)
    print("🌐 Open: http://localhost:5000")
    print("📊 Dashboard: http://localhost:5000/dashboard")
    print("="*50)
    app.run(debug=True, host="0.0.0.0", port=5000)