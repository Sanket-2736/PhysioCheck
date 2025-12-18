import React, { useEffect, useState } from "react";
import api from "../../api/axios";

export default function PhysicianPatients() {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchPatients = async () => {
      try {
        const res = await api.get("/subscription/patients");
        setPatients(res.data.patients || []);
      } catch (err) {
        console.error(err);
        setError("Failed to load patients");
      } finally {
        setLoading(false);
      }
    };

    fetchPatients();
  }, []);

  if (loading) {
    return <div className="text-slate-300">Loading patients...</div>;
  }

  if (error) {
    return <div className="text-red-400">{error}</div>;
  }

  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">My Patients</h1>

      {patients.length === 0 ? (
        <p className="text-slate-400">
          You currently have no assigned patients.
        </p>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {patients.map((p) => (
            <PatientCard key={p.patient_id} patient={p} />
          ))}
        </div>
      )}
    </div>
  );
}

/* -------------------- */
/* Patient Card         */
/* -------------------- */
function PatientCard({ patient }) {
  return (
    <div className="bg-white text-black rounded-lg shadow p-5">
      <div className="flex items-center gap-4 mb-4">
        <img
          src={patient.profile_photo || "/default-avatar.png"}
          alt="patient"
          className="w-14 h-14 rounded-full object-cover"
        />
        <div>
          <h2 className="font-semibold text-lg">
            {patient.full_name || "Unnamed Patient"}
          </h2>
          <p className="text-sm text-gray-500">{patient.email}</p>
        </div>
      </div>

      <div className="text-sm text-gray-700 space-y-1">
        <p>
          <span className="font-medium">Age:</span>{" "}
          {patient.age || "—"}
        </p>
        <p>
          <span className="font-medium">Gender:</span>{" "}
          {patient.gender || "—"}
        </p>
      </div>

      <button
        disabled
        className="mt-4 w-full py-2 bg-blue-600 text-white rounded-lg opacity-70 cursor-not-allowed"
      >
        Assigned Patient
      </button>
    </div>
  );
}
