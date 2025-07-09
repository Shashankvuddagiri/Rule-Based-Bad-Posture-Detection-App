from flask import Flask, jsonify
from flask_cors import CORS
import cv2
import mediapipe as mp

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
            # Convert landmarks to a list of dicts for JSON serialization
            return [
                {
                    "x": lm.x,
                    "y": lm.y,
                    "z": lm.z,
                    "visibility": lm.visibility
                }
                for lm in results.pose_world_landmarks.landmark
            ]
        else:
            return None

@app.route('/api/test_pose')
def test_pose():
    landmarks = process_image('backend/test_squat.jpg')  # Adjust path if needed
    if landmarks:
        return jsonify({"landmarks": landmarks})
    else:
        return jsonify({"message": "No landmarks found"}), 404

@app.route('/api/health')
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(debug=True) 