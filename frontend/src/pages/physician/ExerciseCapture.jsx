import { useEffect, useRef, useState } from "react";
import { Pose } from "@mediapipe/pose";
import { drawConnectors, drawLandmarks } from "@mediapipe/drawing_utils";
import { Camera } from "@mediapipe/camera_utils";

export default function ExerciseRepCaptureWithPose({ exerciseId, token }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const cameraRef = useRef(null);

  const [frames, setFrames] = useState([]);
  const [log, setLog] = useState("");
  const [capturing, setCapturing] = useState(false);

  const appendLog = (msg) =>
    setLog((prev) => prev + msg + "\n");

  /* ================= ANGLE UTILS ================= */

  const angle = (a, b, c) => {
    const ab = { x: a.x - b.x, y: a.y - b.y };
    const cb = { x: c.x - b.x, y: c.y - b.y };

    const dot = ab.x * cb.x + ab.y * cb.y;
    const magA = Math.hypot(ab.x, ab.y);
    const magC = Math.hypot(cb.x, cb.y);

    return Math.acos(dot / (magA * magC)) * (180 / Math.PI);
  };

  /* ================= MEDIAPIPE INIT ================= */

  useEffect(() => {
    const pose = new Pose({
      locateFile: (file) =>
        `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`,
    });

    pose.setOptions({
      modelComplexity: 1,
      smoothLandmarks: true,
      enableSegmentation: false,
      minDetectionConfidence: 0.5,
      minTrackingConfidence: 0.5,
    });

    pose.onResults(onResults);

    cameraRef.current = new Camera(videoRef.current, {
      onFrame: async () => {
        await pose.send({ image: videoRef.current });
      },
      width: 640,
      height: 480,
    });

    return () => cameraRef.current?.stop();
  }, []);

  /* ================= RESULTS HANDLER ================= */

  const onResults = (results) => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    canvas.width = 640;
    canvas.height = 480;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(results.image, 0, 0, canvas.width, canvas.height);

    if (!results.poseLandmarks) return;

    drawConnectors(ctx, results.poseLandmarks, Pose.POSE_CONNECTIONS, {
      color: "#00FF00",
      lineWidth: 4,
    });
    drawLandmarks(ctx, results.poseLandmarks, {
      color: "#FF0000",
      lineWidth: 2,
    });

    if (!capturing) return;

    const lm = results.poseLandmarks;

    // Example joints
    const leftShoulder = lm[11];
    const leftElbow = lm[13];
    const leftWrist = lm[15];

    const shoulderAngle = angle(leftElbow, leftShoulder, {
      x: leftShoulder.x,
      y: leftShoulder.y - 0.1,
    });

    const elbowAngle = angle(leftShoulder, leftElbow, leftWrist);

    setFrames((prev) => [
      ...prev,
      {
        timestamp: Date.now() / 1000,
        joints: {
          left_shoulder: leftShoulder,
          left_elbow: leftElbow,
          left_wrist: leftWrist,
        },
        angles: {
          left_shoulder: shoulderAngle,
          left_elbow: elbowAngle,
        },
      },
    ]);
  };

  /* ================= CONTROLS ================= */

  const start = async () => {
    setFrames([]);
    setCapturing(true);
    await cameraRef.current.start();
    appendLog("📸 Capture started with MediaPipe");
  };

  const stop = async () => {
    setCapturing(false);
    await cameraRef.current.stop();
    appendLog(`📤 Sending ${frames.length} frames`);
    await sendFrames();
  };

  /* ================= SEND FRAMES ================= */

  const sendFrames = async () => {
    const res = await fetch(
      `http://localhost:8000/exercises/${exerciseId}/capture-rep`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ frames }),
      }
    );

    const data = await res.json();
    appendLog("✅ Backend response:");
    appendLog(JSON.stringify(data, null, 2));
  };

  return (
    <div className="text-white space-y-4">
      <h2 className="text-2xl font-bold">Capture Demo Rep</h2>

      <div className="relative w-[640px] h-[480px]">
        <video ref={videoRef} className="hidden" />
        <canvas
          ref={canvasRef}
          className="absolute top-0 left-0 border"
        />
      </div>

      <div className="flex gap-4">
        <button
          onClick={start}
          className="px-4 py-2 bg-green-600 rounded"
        >
          Start Capture
        </button>

        <button
          onClick={stop}
          className="px-4 py-2 bg-red-600 rounded"
        >
          Stop & Send
        </button>
      </div>

      <pre className="bg-black text-green-400 p-4 rounded text-sm">
        {log}
      </pre>
    </div>
  );
}
