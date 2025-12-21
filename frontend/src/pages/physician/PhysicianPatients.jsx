import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../api/axios";

export default function PhysicianPatients() {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const fetchPatients = async () => {
      try {
        const res = await api.get("/physician/patients");
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

  if (loading) return <div className="text-slate-300">Loading patients...</div>;
  if (error) return <div className="text-red-400">{error}</div>;

  return (
    <div className="max-w-6xl mx-auto text-white">
      <h1 className="text-2xl font-bold mb-6">My Patients</h1>

      {patients.length === 0 ? (
        <p className="text-slate-400">You currently have no assigned patients.</p>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {patients.map((p) => (
            <div
              key={p.patient_id}
              className="bg-slate-800 rounded-lg shadow p-5"
            >
              <div className="flex items-center gap-4 mb-4">
                <img
                  src={p.profile_photo || "/default-avatar.png"}
                  alt="patient"
                  className="w-14 h-14 rounded-full object-cover"
                />
                <div>
                  <h2 className="font-semibold text-lg">
                    {p.full_name || "Unnamed Patient"}
                  </h2>
                  <p className="text-sm text-slate-400">{p.email}</p>
                </div>
              </div>

              <div className="text-sm text-slate-300 space-y-1">
                <p><span className="font-medium">Age:</span> {p.age ?? "—"}</p>
                <p><span className="font-medium">Gender:</span> {p.gender ?? "—"}</p>
              </div>

              {/* ✅ VIEW PROFILE BUTTON */}
              <button
                onClick={() =>
                  navigate(`/physician/patients/${p.patient_id}`)
                }
                className="mt-4 w-full py-2 bg-blue-600 hover:bg-blue-700 rounded-lg"
              >
                View Profile
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
