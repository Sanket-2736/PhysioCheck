import { useEffect, useRef, useState } from "react";
import api from "../../api/axios";

export default function ExerciseRepCapture({ exerciseId }) {
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const timerRef = useRef(null);

  const [frames, setFrames] = useState([]);
  const [log, setLog] = useState("");
  const [capturing, setCapturing] = useState(false);

  const appendLog = (msg) =>
    setLog((prev) => prev + msg + "\n");

  /* ================= START CAPTURE ================= */
  const startCapture = async () => {
    setFrames([]);
    appendLog("📸 Starting capture...");

    const stream = await navigator.mediaDevices.getUserMedia({
      video: true,
    });

    streamRef.current = stream;
    videoRef.current.srcObject = stream;

    timerRef.current = setInterval(captureFrame, 100);
    setCapturing(true);
  };

  /* ================= STOP CAPTURE ================= */
  const stopCapture = async () => {
    clearInterval(timerRef.current);

    streamRef.current.getTracks().forEach((t) => t.stop());
    setCapturing(false);

    appendLog(`📤 Sending ${frames.length} frames...`);
    await sendFrames();
  };

  /* ================= CAPTURE FRAME ================= */
  const captureFrame = () => {
    setFrames((prev) => [
      ...prev,
      {
        timestamp: Date.now() / 1000,

        // dummy structure (backend replaces with MediaPipe)
        joints: {
          left_shoulder: { x: 0.4, y: 0.3 },
          left_elbow: { x: 0.45, y: 0.45 },
        },
        angles: {
          left_shoulder: 40 + Math.random() * 60,
          left_elbow: 30 + Math.random() * 40,
        },
      },
    ]);
  };

  /* ================= SEND TO BACKEND ================= */
  const sendFrames = async () => {
    try {
      const res = await api.post(
        `/exercises/${exerciseId}/capture-rep`,
        { frames }
      );

      appendLog("✅ Backend response:");
      appendLog(JSON.stringify(res.data, null, 2));
    } catch (err) {
      appendLog("❌ Error sending frames");
      console.error(err);
    }
  };

  /* ================= CLEANUP ================= */
  useEffect(() => {
    return () => {
      clearInterval(timerRef.current);
      streamRef.current?.getTracks().forEach((t) => t.stop());
    };
  }, []);

  return (
    <div className="max-w-3xl mx-auto text-white space-y-4">
      <h1 className="text-2xl font-bold">
        Capture Demo Rep (Exercise #{exerciseId})
      </h1>

      <video
        ref={videoRef}
        autoPlay
        playsInline
        className="w-full max-w-md border border-slate-600 rounded"
      />

      <div className="flex gap-4">
        {!capturing ? (
          <button
            onClick={startCapture}
            className="px-4 py-2 bg-green-600 rounded"
          >
            Start Capture
          </button>
        ) : (
          <button
            onClick={stopCapture}
            className="px-4 py-2 bg-red-600 rounded"
          >
            Stop & Send
          </button>
        )}
      </div>

      <pre className="bg-black text-green-400 p-4 rounded text-sm overflow-auto">
        {log}
      </pre>
    </div>
  );
}
