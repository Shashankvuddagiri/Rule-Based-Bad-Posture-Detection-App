import React, { useRef, useState, useCallback, useEffect } from "react";
import Webcam from "react-webcam";
import axios from "axios";

const MODES = [
  { value: "squat", label: "Squat" },
  { value: "desk", label: "Desk Sitting" },
  { value: "pushup", label: "Pushup" },
  { value: "lunge", label: "Lunge" },
  { value: "yoga_tpose", label: "Yoga T-Pose" }
];

const PostureCam = () => {
  const webcamRef = useRef(null);
  const [mode, setMode] = useState(MODES[0].value);
  const [feedbackMessages, setFeedbackMessages] = useState([]);
  const [uploadedImage, setUploadedImage] = useState(null);
  const [uploadedVideo, setUploadedVideo] = useState(null);

  // Optional: Canvas for drawing overlays
  const canvasRef = useRef(null);

  // Periodic frame capture and backend call
  const captureFrame = useCallback(async () => {
    if (webcamRef.current) {
      const screenshot = webcamRef.current.getScreenshot();
      if (!screenshot) return;
      // Remove the data URL prefix to get only the base64 string
      const base64 = screenshot.replace(/^data:image\/\w+;base64,/, "");
      try {
        const response = await axios.post("http://localhost:5000/api/process_frame", {
          image: base64,
          mode: mode
        });
        if (response.data && response.data.feedback) {
          setFeedbackMessages(response.data.feedback);
          // Optionally, you can use response.data.landmarks for drawing on canvas
        } else if (response.data && response.data.status === "no_pose_detected") {
          setFeedbackMessages(["No pose detected"]);
        } else {
          setFeedbackMessages(["Unexpected response from backend"]);
        }
      } catch (error) {
        setFeedbackMessages([`Error: ${error.message}`]);
      }
    }
  }, [mode]);

  useEffect(() => {
    const interval = setInterval(() => {
      captureFrame();
    }, 2000); // every 2 seconds
    return () => clearInterval(interval);
  }, [captureFrame]);

  // Handle manual image upload
  const handleImageUpload = (e) => {
    if (e.target.files && e.target.files[0]) {
      setUploadedImage(URL.createObjectURL(e.target.files[0]));
      setUploadedVideo(null);
    }
  };

  // Handle manual video upload
  const handleVideoUpload = (e) => {
    if (e.target.files && e.target.files[0]) {
      setUploadedVideo(URL.createObjectURL(e.target.files[0]));
      setUploadedImage(null);
    }
  };

  return (
    <div style={{ maxWidth: 600, margin: "0 auto", padding: 20 }}>
      <h2>Posture Detection App</h2>
      <div style={{ marginBottom: 16 }}>
        <label>
          Select Mode:{" "}
          <select value={mode} onChange={e => setMode(e.target.value)}>
            {MODES.map(m => (
              <option key={m.value} value={m.value}>{m.label}</option>
            ))}
          </select>
        </label>
      </div>
      <div style={{ marginBottom: 16, position: "relative", width: 400 }}>
        <Webcam
          audio={false}
          ref={webcamRef}
          screenshotFormat="image/jpeg"
          width={400}
          videoConstraints={{ facingMode: "user" }}
        />
        {/* Canvas overlay for future drawing */}
        <canvas
          ref={canvasRef}
          width={400}
          height={300}
          style={{
            position: "absolute",
            left: 0,
            top: 0,
            pointerEvents: "none"
          }}
        />
      </div>
      <div style={{ marginBottom: 16 }}>
        <label>
          Upload Image:{" "}
          <input type="file" accept="image/*" onChange={handleImageUpload} />
        </label>
        {uploadedImage && (
          <div>
            <img src={uploadedImage} alt="Uploaded" style={{ maxWidth: 400, marginTop: 8 }} />
          </div>
        )}
      </div>
      <div style={{ marginBottom: 16 }}>
        <label>
          Upload Video:{" "}
          <input type="file" accept="video/*" onChange={handleVideoUpload} />
        </label>
        {uploadedVideo && (
          <div>
            <video src={uploadedVideo} controls style={{ maxWidth: 400, marginTop: 8 }} />
          </div>
        )}
      </div>
      <div>
        <h3>Feedback</h3>
        {feedbackMessages.length === 0 ? (
          <p>No feedback yet.</p>
        ) : (
          <ul>
            {feedbackMessages.map((msg, idx) => (
              <li key={idx}>{msg}</li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default PostureCam;
