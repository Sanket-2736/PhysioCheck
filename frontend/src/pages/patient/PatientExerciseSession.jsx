import React, { useEffect, useRef, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../../api/axios";

export default function PatientExerciseSession() {
  const { patientExerciseId } = useParams();
  const navigate = useNavigate();

  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const intervalRef = useRef(null);

  const [sessionId, setSessionId] = useState(null);
  const [exerciseId, setExerciseId] = useState(null);

  const [repCount, setRepCount] = useState(0);
  const [status, setStatus] = useState("INITIALIZING");
  const [error, setError] = useState("");
  const [ending, setEnding] = useState(false);

  /* ================= START SESSION ================= */
  const startSession = async () => {
    try {
      const res = await api.post(
        `/patient/exercises/${patientExerciseId}/start`
      );

      setSessionId(res.data.session_id);
      setExerciseId(res.data.exercise_id);
      setStatus("RUNNING");
    } catch (err) {
      console.error(err);
      setError("Failed to start exercise session");
    }
  };

  /* ================= CAMERA SETUP ================= */
  const startCamera = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: true
    });

    videoRef.current.srcObject = stream;
    streamRef.current = stream;

    await videoRef.current.play();
  };

  /* ================= CAPTURE & SEND FRAME ================= */
  const captureFrame = async () => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0);

    canvas.toBlob(async (blob) => {
      if (!blob) return;

      const formData = new FormData();
      formData.append("file", blob);

      try {
        const res = await api.post(
          `/exercises/${exerciseId}/sessions/${sessionId}/frame`,
          formData,
          { headers: { "Content-Type": "multipart/form-data" } }
        );

        if (res.data.repCount !== undefined) {
          setRepCount(res.data.repCount);
        }

        if (res.data.status) {
          setStatus(res.data.status);
        }

        if (res.data.status === "COMPLETED") {
          endSession();
        }
      } catch (err) {
        console.error(err);
      }
    }, "image/jpeg");
  };

  /* ================= END SESSION ================= */
  const endSession = async () => {
    if (ending) return;
    setEnding(true);

    clearInterval(intervalRef.current);
    streamRef.current?.getTracks().forEach((t) => t.stop());

    try {
      const res = await api.post(
        `/exercises/${exerciseId}/sessions/${sessionId}/end`
      );

      navigate("/patient/rehab-plan", {
        state: { summary: res.data }
      });
    } catch (err) {
      console.error(err);
      setError("Failed to end session");
    }
  };

  /* ================= EFFECT ================= */
  useEffect(() => {
    startSession();

    return () => {
      clearInterval(intervalRef.current);
      streamRef.current?.getTracks().forEach((t) => t.stop());
    };
  }, []);

  useEffect(() => {
    if (!sessionId || !exerciseId) return;

    startCamera().then(() => {
      intervalRef.current = setInterval(captureFrame, 700);
    });
  }, [sessionId, exerciseId]);

  /* ================= UI ================= */
  if (error) {
    return <div className="text-red-400">{error}</div>;
  }

  return (
    <div className="max-w-4xl mx-auto text-white space-y-6">
      <h1 className="text-2xl font-bold">Exercise Session</h1>

      <div className="relative bg-black rounded-lg overflow-hidden">
        <video
          ref={videoRef}
          className="w-full h-auto"
          playsInline
          muted
        />
        <canvas ref={canvasRef} className="hidden" />
      </div>

      <div className="bg-slate-800 p-4 rounded-lg flex justify-between items-center">
        <div>
          <p className="text-sm text-slate-400">Reps</p>
          <p className="text-xl font-bold">{repCount}</p>
        </div>

        <div>
          <p className="text-sm text-slate-400">Status</p>
          <p className="text-lg font-semibold">{status}</p>
        </div>

        <button
          onClick={endSession}
          className="bg-red-600 px-4 py-2 rounded"
        >
          End Session
        </button>
      </div>
    </div>
  );
}
