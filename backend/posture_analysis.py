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
    return [lm.x, lm.y, lm.z]

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

# 1️⃣ Squat posture analysis
def analyze_squat_posture(landmarks, side='LEFT', back_angle_thresh=150, knee_toe_margin=0.0):
    """
    Analyze squat posture. Returns feedback messages.
    - back_angle_thresh: minimum allowed back angle (degrees)
    - knee_toe_margin: how much knee can be ahead of toe (meters)
    """
    feedback = []
    s = side.upper()
    shoulder = get_xyz(landmarks, POSE_LANDMARKS[f'{s}_SHOULDER'])
    hip = get_xyz(landmarks, POSE_LANDMARKS[f'{s}_HIP'])
    knee = get_xyz(landmarks, POSE_LANDMARKS[f'{s}_KNEE'])
    foot = get_xyz(landmarks, POSE_LANDMARKS[f'{s}_FOOT_INDEX'])
    # Back angle (shoulder-hip-knee)
    back_angle = calculate_angle(shoulder, hip, knee)
    if back_angle < back_angle_thresh:
        feedback.append("Straighten your back")
    # Knee past toe (x-axis)
    if knee[0] > foot[0] + knee_toe_margin:
        feedback.append("Knees are past toes")
    return feedback

# 2️⃣ Desk posture analysis
def analyze_desk_posture(landmarks, side='LEFT', neck_angle_thresh=150, back_angle_thresh=160):
    """
    Analyze desk posture. Returns feedback messages.
    """
    feedback = []
    s = side.upper()
    ear = get_xyz(landmarks, POSE_LANDMARKS[f'{s}_EAR'])
    shoulder = get_xyz(landmarks, POSE_LANDMARKS[f'{s}_SHOULDER'])
    hip = get_xyz(landmarks, POSE_LANDMARKS[f'{s}_HIP'])
    knee = get_xyz(landmarks, POSE_LANDMARKS[f'{s}_KNEE'])
    # Neck angle (ear-shoulder-hip)
    neck_angle = calculate_angle(ear, shoulder, hip)
    if neck_angle < neck_angle_thresh:
        feedback.append("Lift your head")
    # Back angle (shoulder-hip-knee)
    back_angle = calculate_angle(shoulder, hip, knee)
    if back_angle < back_angle_thresh:
        feedback.append("Keep your back straighter")
    return feedback

# 3️⃣ Pushup posture analysis
def analyze_pushup_posture(landmarks, side='LEFT', elbow_angle_range=(80, 100), back_angle_thresh=165):
    """
    Analyze pushup posture. Returns feedback messages.
    - elbow_angle_range: (min, max) allowed elbow angle at bottom (degrees)
    - back_angle_thresh: minimum allowed back angle (degrees)
    """
    feedback = []
    s = side.upper()
    shoulder = get_xyz(landmarks, POSE_LANDMARKS[f'{s}_SHOULDER'])
    elbow = get_xyz(landmarks, POSE_LANDMARKS[f'{s}_ELBOW'])
    wrist = get_xyz(landmarks, POSE_LANDMARKS[f'{s}_WRIST'])
    hip = get_xyz(landmarks, POSE_LANDMARKS[f'{s}_HIP'])
    knee = get_xyz(landmarks, POSE_LANDMARKS[f'{s}_KNEE'])
    ankle = get_xyz(landmarks, POSE_LANDMARKS[f'{s}_ANKLE'])
    # Elbow angle (shoulder-elbow-wrist)
    elbow_angle = calculate_angle(shoulder, elbow, wrist)
    if not (elbow_angle_range[0] <= elbow_angle <= elbow_angle_range[1]):
        feedback.append("Adjust elbow bend")
    # Back alignment (shoulder-hip-ankle)
    back_angle = calculate_angle(shoulder, hip, ankle)
    if back_angle < back_angle_thresh:
        feedback.append("Keep your back straight")
    # Hip drop (hip.y > shoulder.y or hip.y > knee.y)
    if hip[1] > shoulder[1] or hip[1] > knee[1]:
        feedback.append("Don’t drop your hips")
    return feedback

# 4️⃣ Lunge posture analysis
def analyze_lunge_posture(landmarks, side='LEFT', knee_ankle_margin=0.05, torso_angle_thresh=160, back_leg_angle_thresh=140):
    """
    Analyze lunge posture. Returns feedback messages.
    - knee_ankle_margin: allowed margin for knee ahead of ankle (meters)
    - torso_angle_thresh: minimum allowed torso upright angle (degrees)
    - back_leg_angle_thresh: minimum allowed back leg extension angle (degrees)
    """
    feedback = []
    s = side.upper()
    knee = get_xyz(landmarks, POSE_LANDMARKS[f'{s}_KNEE'])
    ankle = get_xyz(landmarks, POSE_LANDMARKS[f'{s}_ANKLE'])
    shoulder = get_xyz(landmarks, POSE_LANDMARKS[f'{s}_SHOULDER'])
    hip = get_xyz(landmarks, POSE_LANDMARKS[f'{s}_HIP'])
    # Front knee vs ankle x
    if knee[0] > ankle[0] + knee_ankle_margin:
        feedback.append("Knee is past ankle")
    # Torso upright (shoulder-hip-knee)
    torso_angle = calculate_angle(shoulder, hip, knee)
    if torso_angle < torso_angle_thresh:
        feedback.append("Keep your torso upright")
    # Back leg extension (hip-knee-ankle)
    back_leg_angle = calculate_angle(hip, knee, ankle)
    if back_leg_angle < back_leg_angle_thresh:
        feedback.append("Straighten back leg")
    return feedback

# 5️⃣ Yoga T-pose analysis
def analyze_yoga_tpose(landmarks, arm_angle_thresh=170, shoulder_hip_y_margin=0.05, symmetry_thresh=10):
    """
    Analyze yoga T-pose. Returns feedback messages.
    - arm_angle_thresh: minimum allowed arm straightness (degrees)
    - shoulder_hip_y_margin: allowed y-difference for shoulder elevation (meters)
    - symmetry_thresh: max allowed angle difference between arms (degrees)
    """
    feedback = []
    # Left and right arms
    l_shoulder = get_xyz(landmarks, POSE_LANDMARKS['LEFT_SHOULDER'])
    l_elbow = get_xyz(landmarks, POSE_LANDMARKS['LEFT_ELBOW'])
    l_wrist = get_xyz(landmarks, POSE_LANDMARKS['LEFT_WRIST'])
    r_shoulder = get_xyz(landmarks, POSE_LANDMARKS['RIGHT_SHOULDER'])
    r_elbow = get_xyz(landmarks, POSE_LANDMARKS['RIGHT_ELBOW'])
    r_wrist = get_xyz(landmarks, POSE_LANDMARKS['RIGHT_WRIST'])
    l_hip = get_xyz(landmarks, POSE_LANDMARKS['LEFT_HIP'])
    r_hip = get_xyz(landmarks, POSE_LANDMARKS['RIGHT_HIP'])
    # Arm horizontal alignment (shoulder-elbow-wrist)
    l_arm_angle = calculate_angle(l_shoulder, l_elbow, l_wrist)
    r_arm_angle = calculate_angle(r_shoulder, r_elbow, r_wrist)
    if l_arm_angle < arm_angle_thresh:
        feedback.append("Keep left arm straight")
    if r_arm_angle < arm_angle_thresh:
        feedback.append("Keep right arm straight")
    # Shoulder elevation
    if abs(l_shoulder[1] - l_hip[1]) > shoulder_hip_y_margin:
        feedback.append("Relax your left shoulder")
    if abs(r_shoulder[1] - r_hip[1]) > shoulder_hip_y_margin:
        feedback.append("Relax your right shoulder")
    # Symmetry
    if abs(l_arm_angle - r_arm_angle) > symmetry_thresh:
        feedback.append("Keep both arms level")
    return feedback 