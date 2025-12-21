import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../api/axios";

/* ================= CONSTANTS ================= */

// Categories (sent directly to backend)
const EXERCISE_CATEGORIES = [
  "Upper Body",
  "Lower Body",
  "Full Body",
  "Core",
  "Rehabilitation",
  "Mobility"
];

// MediaPipe-consistent joints
const MEDIAPIPE_BODY_PARTS = [
  { label: "Nose", value: "nose" },

  { label: "Left Shoulder", value: "left_shoulder" },
  { label: "Right Shoulder", value: "right_shoulder" },

  { label: "Left Elbow", value: "left_elbow" },
  { label: "Right Elbow", value: "right_elbow" },

  { label: "Left Wrist", value: "left_wrist" },
  { label: "Right Wrist", value: "right_wrist" },

  { label: "Left Hip", value: "left_hip" },
  { label: "Right Hip", value: "right_hip" },

  { label: "Left Knee", value: "left_knee" },
  { label: "Right Knee", value: "right_knee" },

  { label: "Left Ankle", value: "left_ankle" },
  { label: "Right Ankle", value: "right_ankle" }
];

export default function MyExercises() {
  const [exercises, setExercises] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // 🔥 Create exercise state (matches backend schema exactly)
  const [form, setForm] = useState({
    name: "",
    category: "",
    difficulty: "beginner",
    target_body_parts: []
  });

  const [image, setImage] = useState(null);
  const [creating, setCreating] = useState(false);

  const navigate = useNavigate();

  /* ================= FETCH EXERCISES ================= */
  const fetchExercises = async () => {
    try {
      const res = await api.get("/exercises/my-exercises");
      setExercises(res.data.exercises || []);
    } catch (err) {
      console.error(err);
      setError("Failed to load exercises");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExercises();
  }, []);

  /* ================= CREATE EXERCISE ================= */
  const handleCreateExercise = async (e) => {
    e.preventDefault();
    setCreating(true);
    setError("");

    try {
      if (!image) {
        setError("Target image is required");
        setCreating(false);
        return;
      }

      if (form.target_body_parts.length === 0) {
        setError("Select at least one target body part");
        setCreating(false);
        return;
      }

      const formData = new FormData();
      formData.append("name", form.name);
      formData.append("category", form.category);
      formData.append("difficulty", form.difficulty);
      formData.append(
        "target_body_parts",
        JSON.stringify(form.target_body_parts)
      );
      formData.append("target_image", image);

      // ❗ DO NOT set Content-Type manually
      await api.post("/exercises/create", formData);

      // Reset form
      setForm({
        name: "",
        category: "",
        difficulty: "beginner",
        target_body_parts: []
      });
      setImage(null);

      fetchExercises();
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "Failed to create exercise");
    } finally {
      setCreating(false);
    }
  };

  /* ================= DELETE EXERCISE ================= */
  const handleDeleteExercise = async (exerciseId) => {
    const confirmDelete = window.confirm(
      "Are you sure you want to delete this exercise? This action cannot be undone."
    );

    if (!confirmDelete) return;

    try {
      await api.delete(`/exercises/${exerciseId}`);
      fetchExercises();
    } catch (err) {
      console.error(err);
      setError("Failed to delete exercise");
    }
  };

  /* ================= UI STATES ================= */
  if (loading) {
    return <div className="text-slate-300">Loading exercises...</div>;
  }

  return (
    <div className="max-w-6xl mx-auto text-white space-y-8">
      <h1 className="text-2xl font-bold">My Exercises</h1>

      {/* ================= CREATE EXERCISE ================= */}
      <div className="bg-slate-800 rounded-lg p-6 shadow space-y-4">
        <h2 className="text-lg font-semibold">Create New Exercise</h2>

        {error && <p className="text-red-400 text-sm">{error}</p>}

        <form onSubmit={handleCreateExercise} className="grid md:grid-cols-2 gap-4">
          {/* Name */}
          <input
            type="text"
            placeholder="Exercise name"
            className="bg-slate-900 p-2 rounded"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            required
          />

          {/* Category */}
          <select
            className="bg-slate-900 p-2 rounded"
            value={form.category}
            onChange={(e) => setForm({ ...form, category: e.target.value })}
            required
          >
            <option value="">Select category</option>
            {EXERCISE_CATEGORIES.map((cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
          </select>

          {/* Difficulty */}
          <select
            className="bg-slate-900 p-2 rounded"
            value={form.difficulty}
            onChange={(e) => setForm({ ...form, difficulty: e.target.value })}
          >
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>

          {/* Target body parts */}
          <div className="md:col-span-2">
            <p className="text-sm text-slate-400 mb-2">
              Target Body Parts
            </p>

            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
              {MEDIAPIPE_BODY_PARTS.map((part) => (
                <label
                  key={part.value}
                  className="flex items-center gap-2 text-sm bg-slate-900 p-2 rounded cursor-pointer"
                >
                  <input
                    type="checkbox"
                    value={part.value}
                    checked={form.target_body_parts.includes(part.value)}
                    onChange={(e) => {
                      const value = e.target.value;
                      setForm((prev) => ({
                        ...prev,
                        target_body_parts: prev.target_body_parts.includes(value)
                          ? prev.target_body_parts.filter((p) => p !== value)
                          : [...prev.target_body_parts, value]
                      }));
                    }}
                  />
                  {part.label}
                </label>
              ))}
            </div>
          </div>

          {/* Image */}
          <input
            type="file"
            accept="image/*"
            className="md:col-span-2"
            onChange={(e) => setImage(e.target.files[0])}
            required
          />

          <button
            type="submit"
            disabled={creating}
            className="md:col-span-2 py-2 bg-green-600 hover:bg-green-700 rounded transition disabled:opacity-50"
          >
            {creating ? "Creating..." : "Create Exercise"}
          </button>
        </form>
      </div>

      {/* ================= EXERCISE LIST ================= */}
      {exercises.length === 0 ? (
        <p className="text-slate-400">
          You haven’t created any exercises yet.
        </p>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {exercises.map((exercise) => (
            <ExerciseCard
              key={exercise.id}
              exercise={exercise}
              onCapture={() =>
                navigate(`/physician/exercises/${exercise.id}/capture`)
              }
              onDelete={() => handleDeleteExercise(exercise.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

/* ================= EXERCISE CARD ================= */
function ExerciseCard({ exercise, onCapture, onDelete }) {
  return (
    <div className="bg-slate-800 rounded-lg p-5 space-y-4 shadow">
      <div>
        <h2 className="text-lg font-semibold">{exercise.name}</h2>
        <p className="text-sm text-slate-400">
          Category: {exercise.category}
        </p>
        <p className="text-sm text-slate-400">
          Difficulty: {exercise.difficulty}
        </p>
      </div>

      <div className="flex gap-2">
        <button
          onClick={onCapture}
          className="flex-1 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition"
        >
          Capture Demo Rep
        </button>

        <button
          onClick={onDelete}
          className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg transition"
          title="Delete exercise"
        >
          🗑
        </button>
      </div>
    </div>
  );
}
