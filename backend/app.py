from flask import Flask, jsonify, request
from flask_cors import CORS
import cv2
import mediapipe as mp
import numpy as np
import base64
from posture_analysis import (
    analyze_squat_posture,
    analyze_desk_posture,
    analyze_pushup_posture,
    analyze_lunge_posture,
    analyze_yoga_tpose
)

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])  # Allow frontend dev server

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

@app.route('/api/process_frame', methods=['POST'])
def process_frame():
    data = request.get_json()
    if not data or 'image' not in data or 'mode' not in data:
        return jsonify({"status": "error", "message": "Missing image or mode"}), 400
    # Decode base64 image
    try:
        img_bytes = base64.b64decode(data['image'])
        np_arr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    except Exception as e:
        return jsonify({"status": "error", "message": f"Image decode failed: {str(e)}"}), 400
    # Run pose detection
    mp_pose = mp.solutions.pose
    with mp_pose.Pose(static_image_mode=True) as pose:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(img_rgb)
        if results.pose_world_landmarks:
            landmarks = results.pose_world_landmarks.landmark
            # Choose analysis function
            mode = data['mode'].lower()
            if mode == 'squat':
                feedback = analyze_squat_posture(landmarks)
            elif mode == 'desk':
                feedback = analyze_desk_posture(landmarks)
            elif mode == 'pushup':
                feedback = analyze_pushup_posture(landmarks)
            elif mode == 'lunge':
                feedback = analyze_lunge_posture(landmarks)
            elif mode == 'yoga_tpose':
                feedback = analyze_yoga_tpose(landmarks)
            else:
                feedback = ["Unknown mode"]
            # Landmarks as list of dicts
            landmarks_list = [
                {"x": lm.x, "y": lm.y, "z": lm.z, "visibility": lm.visibility}
                for lm in landmarks
            ]
            return jsonify({
                "status": "success",
                "feedback": feedback,
                "landmarks": landmarks_list
            })
        else:
            return jsonify({"status": "no_pose_detected"})

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