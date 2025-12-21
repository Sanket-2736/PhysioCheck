import { useEffect, useState } from "react";
import api from "../../api/axios";

export default function CreateRehabPlanModal({ patientId, onClose }) {
  const [exercises, setExercises] = useState([]);
  const [planId, setPlanId] = useState(null);

  const [selectedExercise, setSelectedExercise] = useState("");
  const [sets, setSets] = useState(3);
  const [reps, setReps] = useState(10);
  const [frequency, setFrequency] = useState(1);

  /* ================= FETCH EXERCISES ================= */
  useEffect(() => {
    api.get("/exercises").then((res) => {
      setExercises(res.data.exercises);
    });
  }, []);

  /* ================= CREATE PLAN ================= */
  const createPlan = async () => {
    const res = await api.post(
      `/physician/patients/${patientId}/rehab-plans`,
      { notes: "Initial rehab plan" }
    );
    setPlanId(res.data.rehab_plan_id);
  };

  /* ================= ASSIGN EXERCISE ================= */
  const addExercise = async () => {
    await api.post(`/rehab-plans/${planId}/assign-exercise`, {
      exercise_id: Number(selectedExercise),
      sets,
      reps,
      frequency_per_day: frequency,
    });

    alert("Exercise added to plan");
  };

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center">
      <div className="bg-slate-800 p-6 rounded-lg w-full max-w-md text-white space-y-4">

        <h2 className="text-xl font-bold">Create Rehab Plan</h2>

        {!planId ? (
          <button
            onClick={createPlan}
            className="w-full bg-green-600 py-2 rounded"
          >
            Create Plan
          </button>
        ) : (
          <>
            {/* EXERCISE SELECT */}
            <select
              value={selectedExercise}
              onChange={(e) => setSelectedExercise(e.target.value)}
              className="w-full bg-slate-700 p-2 rounded"
            >
              <option value="">Select Exercise</option>
              {exercises.map((ex) => (
                <option key={ex.id} value={ex.id}>
                  {ex.name}
                </option>
              ))}
            </select>

            {/* PARAMETERS */}
            <div className="grid grid-cols-3 gap-2">
              <input
                type="number"
                value={sets}
                onChange={(e) => setSets(e.target.value)}
                placeholder="Sets"
                className="bg-slate-700 p-2 rounded"
              />
              <input
                type="number"
                value={reps}
                onChange={(e) => setReps(e.target.value)}
                placeholder="Reps"
                className="bg-slate-700 p-2 rounded"
              />
              <input
                type="number"
                value={frequency}
                onChange={(e) => setFrequency(e.target.value)}
                placeholder="Freq/day"
                className="bg-slate-700 p-2 rounded"
              />
            </div>

            <button
              onClick={addExercise}
              disabled={!selectedExercise}
              className="w-full bg-blue-600 py-2 rounded"
            >
              Add Exercise
            </button>
          </>
        )}

        <button
          onClick={onClose}
          className="w-full text-slate-400 hover:text-white"
        >
          Close
        </button>
      </div>
    </div>
  );
}
