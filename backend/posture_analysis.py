import math

# Helper: Calculate angle (in degrees) at point b between points a, b, c
# a, b, c: [x, y, z] lists or tuples

def calculate_angle(a, b, c):
    """Calculate the angle at point b (in degrees) between points a, b, c in 3D."""
    ba = [a[i] - b[i] for i in range(3)]
    bc = [c[i] - b[i] for i in range(3)]
    dot_product = sum(ba[i] * bc[i] for i in range(3))
    mag_ba = math.sqrt(sum(ba[i] ** 2 for i in range(3)))
    mag_bc = math.sqrt(sum(bc[i] ** 2 for i in range(3)))
    if mag_ba == 0 or mag_bc == 0:
        return 0.0
    cos_angle = max(min(dot_product / (mag_ba * mag_bc), 1.0), -1.0)
    angle_rad = math.acos(cos_angle)
    return math.degrees(angle_rad)

# Helper: Get landmark as [x, y, z] from MediaPipe landmarks list

def get_xyz(landmarks, idx):
    lm = landmarks[idx]
    return [lm.x, lm.y, lm.z], lm.visibility

# MediaPipe landmark indices
POSE_LANDMARKS = {
    'NOSE': 0,
    'LEFT_EYE': 2,
    'RIGHT_EYE': 5,
    'LEFT_EAR': 7,
    'RIGHT_EAR': 8,
    'LEFT_SHOULDER': 11,
    'RIGHT_SHOULDER': 12,
    'LEFT_ELBOW': 13,
    'RIGHT_ELBOW': 14,
    'LEFT_WRIST': 15,
    'RIGHT_WRIST': 16,
    'LEFT_HIP': 23,
    'RIGHT_HIP': 24,
    'LEFT_KNEE': 25,
    'RIGHT_KNEE': 26,
    'LEFT_ANKLE': 27,
    'RIGHT_ANKLE': 28,
    'LEFT_FOOT_INDEX': 31,
    'RIGHT_FOOT_INDEX': 32,
}

def min_visibility(*vis):
    return min(vis)

# Analyze both sides for symmetric postures, return feedback and confidences

# 1️⃣ Squat posture analysis
def analyze_squat_posture(landmarks, back_angle_thresh=150, knee_toe_margin=0.0):
    feedback, confidences = [], []
    for side in ['LEFT', 'RIGHT']:
        shoulder, v1 = get_xyz(landmarks, POSE_LANDMARKS[f'{side}_SHOULDER'])
        hip, v2 = get_xyz(landmarks, POSE_LANDMARKS[f'{side}_HIP'])
        knee, v3 = get_xyz(landmarks, POSE_LANDMARKS[f'{side}_KNEE'])
        foot, v4 = get_xyz(landmarks, POSE_LANDMARKS[f'{side}_FOOT_INDEX'])
        # Back angle
        back_angle = calculate_angle(shoulder, hip, knee)
        conf = min_visibility(v1, v2, v3)
        if back_angle < back_angle_thresh:
            feedback.append(f"({side}) Straighten your back")
            confidences.append(conf)
        # Knee past toe (check y-axis: knee should not be much ahead of foot vertically)
        if knee[1] > foot[1] + knee_toe_margin:
            feedback.append(f"({side}) Knees are past toes")
            confidences.append(min_visibility(v3, v4))
    return feedback, confidences

# 2️⃣ Desk posture analysis
def analyze_desk_posture(landmarks, neck_angle_thresh=150, back_angle_thresh=160):
    feedback, confidences = [], []
    for side in ['LEFT', 'RIGHT']:
        ear, v1 = get_xyz(landmarks, POSE_LANDMARKS[f'{side}_EAR'])
        shoulder, v2 = get_xyz(landmarks, POSE_LANDMARKS[f'{side}_SHOULDER'])
        hip, v3 = get_xyz(landmarks, POSE_LANDMARKS[f'{side}_HIP'])
        knee, v4 = get_xyz(landmarks, POSE_LANDMARKS[f'{side}_KNEE'])
        neck_angle = calculate_angle(ear, shoulder, hip)
        conf1 = min_visibility(v1, v2, v3)
        if neck_angle < neck_angle_thresh:
            feedback.append(f"({side}) Lift your head")
            confidences.append(conf1)
        back_angle = calculate_angle(shoulder, hip, knee)
        conf2 = min_visibility(v2, v3, v4)
        if back_angle < back_angle_thresh:
            feedback.append(f"({side}) Keep your back straighter")
            confidences.append(conf2)
    return feedback, confidences

# 3️⃣ Pushup posture analysis
def analyze_pushup_posture(landmarks, elbow_angle_range=(80, 100), back_angle_thresh=165):
    feedback, confidences = [], []
    for side in ['LEFT', 'RIGHT']:
        shoulder, v1 = get_xyz(landmarks, POSE_LANDMARKS[f'{side}_SHOULDER'])
        elbow, v2 = get_xyz(landmarks, POSE_LANDMARKS[f'{side}_ELBOW'])
        wrist, v3 = get_xyz(landmarks, POSE_LANDMARKS[f'{side}_WRIST'])
        hip, v4 = get_xyz(landmarks, POSE_LANDMARKS[f'{side}_HIP'])
        knee, v5 = get_xyz(landmarks, POSE_LANDMARKS[f'{side}_KNEE'])
        ankle, v6 = get_xyz(landmarks, POSE_LANDMARKS[f'{side}_ANKLE'])
        elbow_angle = calculate_angle(shoulder, elbow, wrist)
        conf1 = min_visibility(v1, v2, v3)
        if not (elbow_angle_range[0] <= elbow_angle <= elbow_angle_range[1]):
            feedback.append(f"({side}) Adjust elbow bend")
            confidences.append(conf1)
        back_angle = calculate_angle(shoulder, hip, ankle)
        conf2 = min_visibility(v1, v4, v6)
        if back_angle < back_angle_thresh:
            feedback.append(f"({side}) Keep your back straight")
            confidences.append(conf2)
        if hip[1] > shoulder[1] or hip[1] > knee[1]:
            feedback.append(f"({side}) Don’t drop your hips")
            confidences.append(min_visibility(v4, v1, v5))
    return feedback, confidences

# 4️⃣ Lunge posture analysis
def analyze_lunge_posture(landmarks, knee_ankle_margin=0.05, torso_angle_thresh=160, back_leg_angle_thresh=140):
    feedback, confidences = [], []
    for side in ['LEFT', 'RIGHT']:
        knee, v1 = get_xyz(landmarks, POSE_LANDMARKS[f'{side}_KNEE'])
        ankle, v2 = get_xyz(landmarks, POSE_LANDMARKS[f'{side}_ANKLE'])
        shoulder, v3 = get_xyz(landmarks, POSE_LANDMARKS[f'{side}_SHOULDER'])
        hip, v4 = get_xyz(landmarks, POSE_LANDMARKS[f'{side}_HIP'])
        if knee[1] > ankle[1] + knee_ankle_margin:
            feedback.append(f"({side}) Knee is past ankle")
            confidences.append(min_visibility(v1, v2))
        torso_angle = calculate_angle(shoulder, hip, knee)
        conf1 = min_visibility(v3, v4, v1)
        if torso_angle < torso_angle_thresh:
            feedback.append(f"({side}) Keep your torso upright")
            confidences.append(conf1)
        back_leg_angle = calculate_angle(hip, knee, ankle)
        conf2 = min_visibility(v4, v1, v2)
        if back_leg_angle < back_leg_angle_thresh:
            feedback.append(f"({side}) Straighten back leg")
            confidences.append(conf2)
    return feedback, confidences

# 5️⃣ Yoga T-pose analysis
def analyze_yoga_tpose(landmarks, arm_angle_thresh=170, shoulder_hip_y_margin=0.05, symmetry_thresh=10):
    feedback, confidences = [], []
    l_shoulder, v1 = get_xyz(landmarks, POSE_LANDMARKS['LEFT_SHOULDER'])
    l_elbow, v2 = get_xyz(landmarks, POSE_LANDMARKS['LEFT_ELBOW'])
    l_wrist, v3 = get_xyz(landmarks, POSE_LANDMARKS['LEFT_WRIST'])
    r_shoulder, v4 = get_xyz(landmarks, POSE_LANDMARKS['RIGHT_SHOULDER'])
    r_elbow, v5 = get_xyz(landmarks, POSE_LANDMARKS['RIGHT_ELBOW'])
    r_wrist, v6 = get_xyz(landmarks, POSE_LANDMARKS['RIGHT_WRIST'])
    l_hip, v7 = get_xyz(landmarks, POSE_LANDMARKS['LEFT_HIP'])
    r_hip, v8 = get_xyz(landmarks, POSE_LANDMARKS['RIGHT_HIP'])
    l_arm_angle = calculate_angle(l_shoulder, l_elbow, l_wrist)
    r_arm_angle = calculate_angle(r_shoulder, r_elbow, r_wrist)
    if l_arm_angle < arm_angle_thresh:
        feedback.append("Keep left arm straight")
        confidences.append(min_visibility(v1, v2, v3))
    if r_arm_angle < arm_angle_thresh:
        feedback.append("Keep right arm straight")
        confidences.append(min_visibility(v4, v5, v6))
    if abs(l_shoulder[1] - l_hip[1]) > shoulder_hip_y_margin:
        feedback.append("Relax your left shoulder")
        confidences.append(min_visibility(v1, v7))
    if abs(r_shoulder[1] - r_hip[1]) > shoulder_hip_y_margin:
        feedback.append("Relax your right shoulder")
        confidences.append(min_visibility(v4, v8))
    if abs(l_arm_angle - r_arm_angle) > symmetry_thresh:
        feedback.append("Keep both arms level")
        confidences.append(min_visibility(v1, v2, v3, v4, v5, v6))
    return feedback, confidences 