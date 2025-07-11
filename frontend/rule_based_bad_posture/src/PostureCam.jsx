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

const POSE_CONNECTIONS = [
  [0,1],[1,2],[2,3],[3,7],
  [0,4],[4,5],[5,6],[6,8],
  [9,10],
  [11,12],[11,13],[13,15],[15,17],[15,19],[15,21],[17,19],[12,14],[14,16],[16,18],[16,20],[16,22],[18,20],
  [11,23],[12,24],[23,24],[23,25],[24,26],[25,27],[27,29],[27,31],[29,31],[26,28],[28,30],[28,32],[30,32]
];

function drawSkeleton(ctx, landmarks, width, height) {
  if (!landmarks || landmarks.length === 0) return;
  ctx.clearRect(0, 0, width, height);
  ctx.strokeStyle = "#4F8EF7";
  ctx.lineWidth = 2;
  POSE_CONNECTIONS.forEach(([start, end]) => {
    const lmStart = landmarks[start];
    const lmEnd = landmarks[end];
    if (lmStart && lmEnd) {
      ctx.beginPath();
      ctx.moveTo(lmStart.x * width, lmStart.y * height);
      ctx.lineTo(lmEnd.x * width, lmEnd.y * height);
      ctx.stroke();
    }
  });
  ctx.fillStyle = "#F7B32B";
  landmarks.forEach(lm => {
    ctx.beginPath();
    ctx.arc(lm.x * width, lm.y * height, 4, 0, 2 * Math.PI);
    ctx.fill();
  });
}

const FEEDBACK_TOOLTIPS = {
  'good': 'Your posture is correct for this rule.',
  'straighten': 'Try to keep your back or limb straighter.',
  'lift': 'Lift your head or body part as indicated.',
  'adjust': 'Adjust the angle of your joint or limb.',
  'past': 'Your joint is past a recommended position.',
  'drop': 'Don’t drop your hips or body part.',
  'relax': 'Relax your shoulders or other body part.',
  'keep': 'Maintain the recommended alignment.',
  'no feedback': 'No issues detected for this rule.'
};

function getTooltip(message) {
  const lower = message.toLowerCase();
  for (const key in FEEDBACK_TOOLTIPS) {
    if (lower.includes(key)) return FEEDBACK_TOOLTIPS[key];
  }
  return 'See details for this feedback.';
}

const FeedbackCard = ({ message, confidence }) => {
  const isGood = message.toLowerCase().includes("good") || message.toLowerCase().includes("no feedback");
  const isWarning = message.toLowerCase().includes("needs") || message.toLowerCase().includes("straighten") || message.toLowerCase().includes("lift") || message.toLowerCase().includes("adjust") || message.toLowerCase().includes("past") || message.toLowerCase().includes("drop") || message.toLowerCase().includes("relax") || message.toLowerCase().includes("keep");
  const tooltip = getTooltip(message);
  return (
    <div
      className="feedback-card"
      style={{
        background: isGood ? "#e8fbe8" : isWarning ? "#fffbe6" : "#ffeaea",
        color: isGood ? "#2e7d32" : isWarning ? "#bfa100" : "#c62828",
        border: `1px solid ${isGood ? '#b2dfdb' : isWarning ? '#ffe082' : '#ffcdd2'}`,
        borderRadius: 12,
        padding: 16,
        margin: 8,
        display: 'flex',
        alignItems: 'center',
        gap: 12,
        position: 'relative',
        cursor: 'help',
        boxShadow: '0 2px 8px rgba(80,120,200,0.07)'
      }}
      title={tooltip + (confidence !== undefined ? `\nConfidence: ${Math.round(confidence * 100)}%` : '')}
    >
      <span style={{fontSize: 26}}>{isGood ? '✅' : isWarning ? '⚠️' : '❌'}</span>
      <span style={{flex:1}}>{message}</span>
      {confidence !== undefined && (
        <span style={{ fontSize: 14, color: '#888', fontWeight: 500 }}>
          {`Confidence: ${(confidence * 100).toFixed(0)}%`}
        </span>
      )}
    </div>
  );
};

const PostureCam = () => {
  const webcamRef = useRef(null);
  const canvasRef = useRef(null);
  const [mode, setMode] = useState(MODES[0].value);
  const [feedbackMessages, setFeedbackMessages] = useState([]);
  const [feedbackConfidences, setFeedbackConfidences] = useState([]);
  const [uploadedImage, setUploadedImage] = useState(null);
  const [uploadedVideo, setUploadedVideo] = useState(null);
  const [showWebcam, setShowWebcam] = useState(false);
  const [cameraError, setCameraError] = useState("");
  const [processing, setProcessing] = useState(false);
  const [report, setReport] = useState(null);
  const [videoFeedback, setVideoFeedback] = useState([]);
  const [videoFrameIdx, setVideoFrameIdx] = useState(0);
  const [videoTotalFrames, setVideoTotalFrames] = useState(0);
  // Add a dedicated ref for the image canvas
  const imageCanvasRef = useRef(null);

  const handleStartCamera = () => {
    setCameraError("");
    setShowWebcam(true);
  };
  const handleUserMediaError = (err) => {
    setCameraError("Camera permission denied or not available.");
    setShowWebcam(false);
  };
  const handleImageUpload = (e) => {
    if (e.target.files && e.target.files[0]) {
      setUploadedImage(URL.createObjectURL(e.target.files[0]));
      setUploadedVideo(null);
      setShowWebcam(false);
      setFeedbackMessages([]);
      setFeedbackConfidences([]);
      setVideoFeedback([]);
    }
  };
  const handleVideoUpload = (e) => {
    if (e.target.files && e.target.files[0]) {
      setUploadedVideo(URL.createObjectURL(e.target.files[0]));
      setUploadedImage(null);
      setShowWebcam(false);
      setFeedbackMessages([]);
      setFeedbackConfidences([]);
      setVideoFeedback([]);
    }
  };
  const handleDownloadReport = () => {
    if (!report) return;
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'posture_feedback_report.json';
    a.click();
    URL.revokeObjectURL(url);
  };
  const analyzeImage = async (imageBase64) => {
    setProcessing(true);
    try {
      const response = await axios.post("http://localhost:5000/api/process_frame", {
        image: imageBase64,
        mode: mode
      });
      if (response.data && response.data.feedback) {
        setFeedbackMessages(response.data.feedback);
        setFeedbackConfidences(response.data.confidences || []);
        setReport(response.data);
        if (response.data.landmarks && canvasRef.current) {
          const ctx = canvasRef.current.getContext("2d");
          drawSkeleton(ctx, response.data.landmarks, canvasRef.current.width, canvasRef.current.height);
        }
      } else if (response.data && response.data.status === "no_pose_detected") {
        setFeedbackMessages(["No pose detected"]);
        setFeedbackConfidences([]);
        setReport(response.data);
        if (canvasRef.current) {
          const ctx = canvasRef.current.getContext("2d");
          ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
        }
      } else {
        setFeedbackMessages(["Unexpected response from backend"]);
        setFeedbackConfidences([]);
      }
    } catch (error) {
      setFeedbackMessages([`Error: ${error.message}`]);
      setFeedbackConfidences([]);
    }
    setProcessing(false);
  };
  const handleGetImageFeedback = () => {
    if (!uploadedImage) return;
    const img = new window.Image();
    img.crossOrigin = "anonymous";
    img.onload = () => {
      const canvas = document.createElement("canvas");
      canvas.width = img.width;
      canvas.height = img.height;
      const ctx = canvas.getContext("2d");
      ctx.drawImage(img, 0, 0);
      const base64 = canvas.toDataURL("image/jpeg").replace(/^data:image\/\w+;base64,/, "");
      analyzeImage(base64);
    };
    img.src = uploadedImage;
  };
  const captureFrame = useCallback(async () => {
    if (webcamRef.current && showWebcam) {
      const screenshot = webcamRef.current.getScreenshot();
      if (!screenshot) return;
      const base64 = screenshot.replace(/^data:image\/\w+;base64,/, "");
      await analyzeImage(base64);
    }
  }, [mode, showWebcam]);
  useEffect(() => {
    if (!showWebcam) return;
    const interval = setInterval(() => {
      captureFrame();
    }, 2000);
    return () => clearInterval(interval);
  }, [captureFrame, showWebcam]);
  const handleGetVideoFeedback = () => {
    if (!uploadedVideo) return;
    setProcessing(true);
    setVideoFeedback([]);
    setVideoFrameIdx(0);
    const video = document.createElement("video");
    video.src = uploadedVideo;
    video.crossOrigin = "anonymous";
    video.onloadedmetadata = () => {
      const totalFrames = Math.floor(video.duration * 5);
      setVideoTotalFrames(totalFrames);
      let currentFrame = 0;
      const canvas = document.createElement("canvas");
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext("2d");
      const processNextFrame = () => {
        if (currentFrame >= totalFrames) {
          setProcessing(false);
          return;
        }
        video.currentTime = (currentFrame / 5);
      };
      video.onseeked = async () => {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        const base64 = canvas.toDataURL("image/jpeg").replace(/^data:image\/\w+;base64,/, "");
        try {
          const response = await axios.post("http://localhost:5000/api/process_frame", {
            image: base64,
            mode: mode
          });
          setVideoFeedback(prev => [...prev, {
            feedback: response.data.feedback,
            confidences: response.data.confidences || [],
            frame: currentFrame
          }]);
        } catch (e) {
          setVideoFeedback(prev => [...prev, { feedback: ["Error processing frame"], confidences: [], frame: currentFrame }]);
        }
        setVideoFrameIdx(currentFrame + 1);
        currentFrame++;
        processNextFrame();
      };
      processNextFrame();
    };
  };

  // Draw skeleton overlay for uploaded image after feedback
  useEffect(() => {
    if (uploadedImage && report && report.landmarks && imageCanvasRef.current) {
      const img = document.getElementById('uploaded-img');
      if (img) {
        imageCanvasRef.current.width = img.width;
        imageCanvasRef.current.height = img.height;
        const ctx = imageCanvasRef.current.getContext('2d');
        drawSkeleton(ctx, report.landmarks, img.width, img.height);
      }
    }
  }, [uploadedImage, report]);

  // Draw skeleton overlay for webcam after feedback
  useEffect(() => {
    if (showWebcam && report && report.landmarks && canvasRef.current) {
      const ctx = canvasRef.current.getContext('2d');
      drawSkeleton(ctx, report.landmarks, canvasRef.current.width, canvasRef.current.height);
    }
  }, [showWebcam, report]);

  // Modern, light, responsive UI
  return (
    <div style={{ minHeight: '100vh', width: '100vw', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#232323' }}>
      <div style={{ maxWidth: 520, width: '100%', margin: "0 auto", padding: 24, background: "#f8fafc", borderRadius: 18, boxShadow: "0 4px 24px rgba(80,120,200,0.10)", fontFamily: 'Inter, Arial, sans-serif' }}>
        <h2 style={{ fontWeight: 700, fontSize: 32, marginBottom: 18, color: '#2d3a4a', letterSpacing: 0.5 }}>Posture Detection App</h2>
        <div style={{ marginBottom: 18, display: 'flex', alignItems: 'center', gap: 16 }}>
          <label style={{ fontWeight: 500, color: '#3a4a5a' }}>
            Select Mode:
            <select value={mode} onChange={e => setMode(e.target.value)} style={{ marginLeft: 8, padding: 8, borderRadius: 8, border: '1.5px solid #4F8EF7', background: '#f0f6ff', color: '#2d3a4a', fontWeight: 600, fontSize: 16, outline: 'none', boxShadow: '0 1px 4px #4f8ef71a', transition: 'border 0.2s' }}>
              {MODES.map(m => (
                <option key={m.value} value={m.value}>{m.label}</option>
              ))}
            </select>
          </label>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
          {/* Camera Panel */}
          <div style={{ marginBottom: 8 }}>
            {!showWebcam && (
              <button onClick={handleStartCamera} style={{ background: '#4F8EF7', color: '#fff', border: 'none', borderRadius: 8, padding: '12px 28px', fontWeight: 600, fontSize: 18, boxShadow: '0 2px 8px #4f8ef71a', cursor: 'pointer', marginBottom: 8 }}>Start Camera</button>
            )}
            {showWebcam && (
              <div style={{ position: "relative", width: 400, height: 300, borderRadius: 12, overflow: 'hidden', boxShadow: '0 2px 8px #4f8ef71a', background: '#fff' }}>
                <Webcam
                  audio={false}
                  ref={webcamRef}
                  screenshotFormat="image/jpeg"
                  width={400}
                  height={300}
                  videoConstraints={{ facingMode: "user" }}
                  onUserMediaError={handleUserMediaError}
                  style={{ borderRadius: 12, position: 'absolute', left: 0, top: 0, zIndex: 1 }}
                />
                <canvas
                  ref={canvasRef}
                  width={400}
                  height={300}
                  style={{
                    position: "absolute",
                    left: 0,
                    top: 0,
                    pointerEvents: "none",
                    borderRadius: 12,
                    zIndex: 2
                  }}
                />
              </div>
            )}
            {cameraError && <div style={{ color: "#c62828", marginTop: 8, fontWeight: 500 }}>{cameraError}</div>}
          </div>
          {/* Upload Panel */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8, background: '#fff', borderRadius: 12, padding: 16, boxShadow: '0 1px 4px #4f8ef71a' }}>
            <label style={{ fontWeight: 500, color: '#3a4a5a' }}>
              Upload Image: <input type="file" accept="image/*" onChange={handleImageUpload} style={{ marginLeft: 8 }} />
            </label>
            <label style={{ fontWeight: 500, color: '#3a4a5a' }}>
              Upload Video: <input type="file" accept="video/*" onChange={handleVideoUpload} style={{ marginLeft: 8 }} />
            </label>
            {uploadedImage && (
              <div style={{ marginTop: 8, position: 'relative', display: 'inline-block' }}>
                <img
                  id="uploaded-img"
                  src={uploadedImage}
                  alt="Uploaded"
                  style={{ maxWidth: 400, marginTop: 8, borderRadius: 10, boxShadow: '0 1px 4px #4f8ef71a', display: 'block', width: '100%' }}
                  onLoad={e => {
                    // Resize canvas to match image
                    if (imageCanvasRef.current) {
                      imageCanvasRef.current.width = e.target.width;
                      imageCanvasRef.current.height = e.target.height;
                    }
                  }}
                />
                <canvas
                  ref={imageCanvasRef}
                  style={{
                    position: 'absolute',
                    left: 0,
                    top: 0,
                    pointerEvents: 'none',
                    borderRadius: 10,
                    zIndex: 2,
                    width: '100%',
                    height: '100%'
                  }}
                />
                <button onClick={handleGetImageFeedback} disabled={processing} style={{ marginTop: 12, background: '#4F8EF7', color: '#fff', border: 'none', borderRadius: 8, padding: '10px 22px', fontWeight: 600, fontSize: 16, cursor: 'pointer', display: 'block' }}>Get Feedback</button>
              </div>
            )}
            {uploadedVideo && (
              <div style={{ marginTop: 8 }}>
                <video src={uploadedVideo} controls style={{ maxWidth: 400, marginTop: 8, borderRadius: 10, boxShadow: '0 1px 4px #4f8ef71a' }} />
                <button onClick={handleGetVideoFeedback} disabled={processing} style={{ marginTop: 12, background: '#4F8EF7', color: '#fff', border: 'none', borderRadius: 8, padding: '10px 22px', fontWeight: 600, fontSize: 16, cursor: 'pointer' }}>Get Feedback</button>
                {videoFeedback.length > 0 && (
                  <div style={{ marginTop: 16 }}>
                    <h4 style={{ color: '#2d3a4a', fontWeight: 600 }}>Frame-by-frame Feedback</h4>
                    <div style={{ maxHeight: 200, overflowY: 'auto', border: '1px solid #e0e7ef', borderRadius: 8, padding: 8, background: '#f8fafc' }}>
                      {videoFeedback.map((vf, idx) => (
                        <div key={idx} style={{ marginBottom: 8 }}>
                          <div style={{ fontSize: 12, color: '#888', marginBottom: 2 }}>Frame {vf.frame + 1}</div>
                          {vf.feedback.map((msg, i) => (
                            <FeedbackCard key={i} message={msg} confidence={vf.confidences[i]} />
                          ))}
                        </div>
                      ))}
                    </div>
                    <div style={{ fontSize: 12, color: '#888', marginTop: 4 }}>
                      {`Processed ${videoFrameIdx} / ${videoTotalFrames} frames`}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
          {/* Feedback Panel */}
          <div style={{ marginTop: 18, background: '#fff', borderRadius: 12, padding: 18, boxShadow: '0 1px 4px #4f8ef71a' }}>
            <h3 style={{ color: '#2d3a4a', fontWeight: 600, marginBottom: 10 }}>Feedback</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
              {feedbackMessages.length === 0 ? (
                <p style={{ color: '#888', fontWeight: 500 }}>No feedback yet.</p>
              ) : (
                feedbackMessages.map((msg, idx) => (
                  <FeedbackCard key={idx} message={msg} confidence={feedbackConfidences[idx]} />
                ))
              )}
            </div>
            {report && (
              <button onClick={handleDownloadReport} style={{ marginTop: 16, background: '#F7B32B', color: '#2d3a4a', border: 'none', borderRadius: 8, padding: '8px 18px', fontWeight: 600, fontSize: 15, cursor: 'pointer' }}>Download Feedback Report</button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PostureCam;
