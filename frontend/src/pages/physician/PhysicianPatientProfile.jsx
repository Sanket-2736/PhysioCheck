import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../../api/axios";

/* ================= ASSIGN EXERCISE MODAL ================= */
function AssignExerciseModal({ planId, onClose, onAssigned }) {
  const [exercises, setExercises] = useState([]);
  const [selectedExercise, setSelectedExercise] = useState("");

  const [targetSets, setTargetSets] = useState(1);
  const [targetReps, setTargetReps] = useState(5);
  const [maxDuration, setMaxDuration] = useState(30);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  /* Fetch physician-created exercises */
  useEffect(() => {
    api.get("/exercises/my-exercises").then((res) => {
      setExercises(res.data.exercises || []);
    });
  }, []);

  const assignExercise = async () => {
    if (!selectedExercise) return;

    setLoading(true);
    setError("");

    try {
      await api.post(`/rehab/plans/${planId}/exercises`, {
        exercise_id: Number(selectedExercise),
        target_sets: Number(targetSets),
        target_reps: Number(targetReps),
        max_duration: Number(maxDuration)
      });

      onAssigned();
      onClose();
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "Failed to assign exercise");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="bg-slate-800 p-6 rounded-lg w-full max-w-md text-white space-y-4">
        <h2 className="text-xl font-bold">Assign Exercise</h2>

        {error && <p className="text-red-400 text-sm">{error}</p>}

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

        <div className="grid grid-cols-3 gap-2">
          <input
            type="number"
            min="1"
            value={targetSets}
            onChange={(e) => setTargetSets(e.target.value)}
            className="bg-slate-700 p-2 rounded"
            placeholder="Sets"
          />
          <input
            type="number"
            min="1"
            value={targetReps}
            onChange={(e) => setTargetReps(e.target.value)}
            className="bg-slate-700 p-2 rounded"
            placeholder="Reps"
          />
          <input
            type="number"
            min="5"
            value={maxDuration}
            onChange={(e) => setMaxDuration(e.target.value)}
            className="bg-slate-700 p-2 rounded"
            placeholder="Max sec"
          />
        </div>

        <button
          onClick={assignExercise}
          disabled={!selectedExercise || loading}
          className="w-full bg-green-600 py-2 rounded disabled:opacity-50"
        >
          {loading ? "Assigning..." : "Assign Exercise"}
        </button>

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

/* ================= MAIN PAGE ================= */
export default function PhysicianPatientProfile() {
  const { id } = useParams(); // patient_id
  const navigate = useNavigate();

  const [patient, setPatient] = useState(null);
  const [rehabPlan, setRehabPlan] = useState(null);
  const [assignedExercises, setAssignedExercises] = useState([]);

  const [loading, setLoading] = useState(true);
  const [showAssignModal, setShowAssignModal] = useState(false);

  /* ================= FETCH ALL ================= */
  const fetchAll = async () => {
    try {
      const patientRes = await api.get(`/physician/patients/${id}`);
      setPatient(patientRes.data.patient);

      const planRes = await api.get(
        `/rehab/patients/${id}/plans/current`
      );
      setRehabPlan(planRes.data.rehab_plan);

      if (planRes.data.rehab_plan) {
        const exRes = await api.get(
          `/rehab/plans/${planRes.data.rehab_plan.id}/exercises`
        );
        setAssignedExercises(exRes.data.exercises || []);
      } else {
        setAssignedExercises([]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAll();
  }, [id]);

  /* ================= ACTIONS ================= */
  const createRehabPlan = async () => {
    await api.post(`/rehab/patients/${id}/plans`, {
      notes: "Initial rehab plan"
    });
    fetchAll();
  };

  const deassignExercise = async (planExerciseId) => {
    if (!window.confirm("Remove this exercise from rehab plan?")) return;

    await api.post(
      `/rehab/plans/${rehabPlan.id}/exercises/${planExerciseId}/remove`
    );
    fetchAll();
  };

  /* ================= UI ================= */
  if (loading) {
    return <div className="text-slate-300">Loading patient...</div>;
  }

  if (!patient) {
    return <div className="text-red-400">Patient not found</div>;
  }

  return (
    <div className="max-w-4xl mx-auto text-white">
      <button
        onClick={() => navigate(-1)}
        className="mb-6 text-blue-400 hover:underline"
      >
        ← Back
      </button>

      <div className="bg-slate-800 rounded-lg p-6 space-y-6">

        {/* HEADER */}
        <div className="flex items-center gap-4">
          <img
            src={patient.profile_photo || "/default-avatar.png"}
            alt="patient"
            className="w-20 h-20 rounded-full object-cover"
          />

          <div className="flex-1">
            <h1 className="text-2xl font-bold">{patient.full_name}</h1>
            <p className="text-slate-400">{patient.email}</p>
          </div>

          {!rehabPlan ? (
            <button
              onClick={createRehabPlan}
              className="bg-green-600 px-4 py-2 rounded"
            >
              Create Rehab Plan
            </button>
          ) : (
            <button
              onClick={() => setShowAssignModal(true)}
              className="bg-blue-600 px-4 py-2 rounded"
            >
              Assign Exercise
            </button>
          )}
        </div>

        {/* ASSIGNED EXERCISES */}
        {rehabPlan && (
          <div>
            <h3 className="text-lg font-semibold mb-3">
              Assigned Exercises
            </h3>

            {assignedExercises.length === 0 ? (
              <p className="text-slate-400">No exercises assigned yet.</p>
            ) : (
              <div className="space-y-3">
                {assignedExercises.map((ex) => (
                  <div
                    key={ex.plan_exercise_id}
                    className="bg-slate-700 p-4 rounded flex justify-between items-center"
                  >
                    <div>
                      <p className="font-medium">{ex.exercise_name}</p>
                      <p className="text-sm text-slate-400">
                        {ex.target_sets} × {ex.target_reps} | {ex.max_duration}s
                      </p>
                    </div>

                    <button
                      onClick={() =>
                        deassignExercise(ex.plan_exercise_id)
                      }
                      className="text-red-400 hover:text-red-300"
                    >
                      Remove
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {showAssignModal && rehabPlan && (
        <AssignExerciseModal
          planId={rehabPlan.id}
          onClose={() => setShowAssignModal(false)}
          onAssigned={fetchAll}
        />
      )}
    </div>
  );
}
