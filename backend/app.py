from flask import Flask, jsonify
from flask_cors import CORS
import cv2
import mediapipe as mp
from posture_analysis import (
    analyze_squat_posture,
    analyze_desk_posture,
    analyze_pushup_posture,
    analyze_lunge_posture,
    analyze_yoga_tpose
)

app = Flask(__name__)
CORS(app)

def process_image(image_path):
    mp_pose = mp.solutions.pose
    with mp_pose.Pose(static_image_mode=True) as pose:
        image = cv2.imread(image_path)
        if image is None:
            return None
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)
        if results.pose_world_landmarks:
            return results.pose_world_landmarks.landmark
        else:
            return None

@app.route('/api/test_pose')
def test_pose():
    landmarks = process_image('backend/test_squat.jpg')  # Adjust path if needed
    if landmarks:
        # Run all posture analysis functions
        squat_feedback = analyze_squat_posture(landmarks)
        desk_feedback = analyze_desk_posture(landmarks)
        pushup_feedback = analyze_pushup_posture(landmarks)
        lunge_feedback = analyze_lunge_posture(landmarks)
        yoga_feedback = analyze_yoga_tpose(landmarks)
        return jsonify({
            "squat_feedback": squat_feedback,
            "desk_feedback": desk_feedback,
            "pushup_feedback": pushup_feedback,
            "lunge_feedback": lunge_feedback,
            "yoga_tpose_feedback": yoga_feedback
        })
    else:
        return jsonify({"message": "No landmarks found"}), 404

@app.route('/api/health')
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(debug=True) 