import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../api/axios";

export default function PatientRehabPlan() {
  const [exercises, setExercises] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const navigate = useNavigate();

  /* ================= FETCH ASSIGNED EXERCISES ================= */
  const fetchExercises = async () => {
    try {
      const res = await api.get("/patient/exercises");
      setExercises(res.data.exercises || []);
    } catch (err) {
      console.error(err);
      setError("Failed to load rehab plan");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExercises();
  }, []);

  /* ================= UI STATES ================= */
  if (loading) {
    return <div className="text-slate-300">Loading rehab plan...</div>;
  }

  if (error) {
    return <div className="text-red-400">{error}</div>;
  }

  return (
    <div className="max-w-4xl mx-auto text-white space-y-6">
      <h1 className="text-2xl font-bold">My Rehab Plan</h1>

      {exercises.length === 0 ? (
        <p className="text-slate-400">
          No exercises assigned yet. Please check back later.
        </p>
      ) : (
        <div className="space-y-4">
          {exercises.map((ex) => (
            <ExerciseCard
              key={ex.patient_exercise_id}
              exercise={ex}
              onStart={() =>
                navigate(
                  `/patient/rehab-plan/${ex.patient_exercise_id}/start`
                )
              }
            />
          ))}
        </div>
      )}
    </div>
  );
}

/* ================= EXERCISE CARD ================= */
function ExerciseCard({ exercise, onStart }) {
  return (
    <div className="bg-slate-800 rounded-lg p-5 shadow flex justify-between items-center">
      <div className="space-y-1">
        <h2 className="text-lg font-semibold">{exercise.name}</h2>

        <p className="text-sm text-slate-400">
          Sets: <span className="text-white">{exercise.sets}</span>
        </p>
        <p className="text-sm text-slate-400">
          Reps: <span className="text-white">{exercise.reps}</span>
        </p>
        <p className="text-sm text-slate-400">
          Frequency/day:{" "}
          <span className="text-white">
            {exercise.frequency_per_day}
          </span>
        </p>
      </div>

      <button
        onClick={onStart}
        className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded transition"
      >
        Start
      </button>
    </div>
  );
}
