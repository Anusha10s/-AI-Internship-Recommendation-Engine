let currentStudentId = null;
let realTimeInterval = null;

function getRecommendations() {
    const studentId = document.getElementById('studentSelect').value;
    if (!studentId) { alert('Please select a student.'); return; }
    
    currentStudentId = studentId;
    document.getElementById('studentInfo').style.display = 'none';
    document.getElementById('recommendations').style.display = 'none';
    document.getElementById('loading').style.display = 'block';
    
    fetch('/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ student_id: studentId })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('loading').style.display = 'none';
        if (data.error) { alert(data.error); return; }
        
        document.getElementById('studentName').textContent = data.student.name;
        document.getElementById('studentDomain').textContent = data.student.domain;
        document.getElementById('studentSkills').textContent = data.student.skills.join(', ');
        document.getElementById('studentInfo').style.display = 'block';
        
        displayRecs('collaborativeRecs', data.collaborative, 'predicted_score', '⭐');
        displayRecs('contentRecs', data.content_based, 'similarity_score', '% match');
        displayRecs('hybridRecs', data.hybrid, 'combined_score', '⭐');
        displayRecs('deepLearningRecs', data.deep_learning, 'predicted_rating', '⭐');
        
        document.getElementById('recommendations').style.display = 'block';
    })
    .catch(error => { document.getElementById('loading').style.display = 'none'; alert('Error!'); console.error(error); });
}

function displayRecs(containerId, recs, scoreKey, label) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';
    if (!recs || recs.length === 0) {
        container.innerHTML = '<p style="color:rgba(255,255,255,0.4);">No recommendations available.</p>';
        return;
    }
    recs.forEach(rec => {
        container.innerHTML += `
            <div class="rec-item">
                <div>
                    <div class="title">${rec.title}</div>
                    <div class="company">${rec.company} • ${rec.domain}</div>
                </div>
                <div class="score">${label} ${rec[scoreKey] || 'N/A'}</div>
            </div>
        `;
    });
}

function startRealTime() {
    const studentId = document.getElementById('studentSelect').value;
    if (!studentId) { alert('Please select a student.'); return; }
    
    fetch('/real_time/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ student_id: studentId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('realtimeStatus').style.display = 'flex';
            document.getElementById('realtimeStatus').innerHTML = `
                <p>⚡ Real-time active for ${document.getElementById('studentSelect').selectedOptions[0].text}</p>
                <button onclick="stopRealTime()" class="btn-stop">⏹ Stop</button>
            `;
            // Auto-refresh every 3 seconds
            if (realTimeInterval) clearInterval(realTimeInterval);
            realTimeInterval = setInterval(fetchRealtimeUpdate, 3000);
        }
    });
}

function stopRealTime() {
    fetch('/real_time/stop', { method: 'POST' })
        .then(() => {
            if (realTimeInterval) clearInterval(realTimeInterval);
            realTimeInterval = null;
            document.getElementById('realtimeStatus').style.display = 'none';
        });
}

function fetchRealtimeUpdate() {
    fetch('/real_time/update')
        .then(response => response.json())
        .then(data => {
            if (data.error) return;
            displayRecs('collaborativeRecs', data.collaborative, 'predicted_score', '⭐');
            displayRecs('contentRecs', data.content_based, 'similarity_score', '% match');
            displayRecs('hybridRecs', data.hybrid, 'combined_score', '⭐');
            displayRecs('deepLearningRecs', data.deep_learning, 'predicted_rating', '⭐');
        })
        .catch(error => console.error('Real-time error:', error));
}

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('studentSelect').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') getRecommendations();
    });
});