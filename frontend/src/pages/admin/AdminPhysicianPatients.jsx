import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../../api/axios";
import { toast } from "react-toastify";

export default function AdminPhysicianPatients() {
  const { id } = useParams(); // physician user_id
  const navigate = useNavigate();

  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPatients();
  }, []);

  const fetchPatients = async () => {
    try {
      const res = await api.get(`/admin/physicians/${id}/patients`);
      setPatients(res.data.patients);
    } catch (err) {
      toast.error("Failed to load patients");
      navigate("/admin/physicians");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900 text-white">
        Loading patients...
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 text-white p-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Physician’s Patients</h1>

        <button
          onClick={() => navigate("/admin/physicians")}
          className="bg-slate-700 hover:bg-slate-600 px-4 py-2 rounded-lg"
        >
          ← Back
        </button>
      </div>

      {/* Patients Table */}
      <div className="bg-slate-800 rounded-xl overflow-x-auto">
        <table className="w-full text-left">
          <thead className="bg-slate-700 text-slate-200">
            <tr>
              <th className="p-4">Name</th>
              <th className="p-4">Email</th>
              <th className="p-4">Age</th>
              <th className="p-4">Gender</th>
              <th className="p-4">Injury</th>
              <th className="p-4">Goals</th>
            </tr>
          </thead>

          <tbody>
            {patients.map((p) => (
              <tr
                key={p.patient_id}
                className="border-b border-slate-700 hover:bg-slate-700/40"
              >
                <td className="p-4 font-semibold">{p.full_name}</td>
                <td className="p-4 text-slate-300">{p.email}</td>
                <td className="p-4">{p.age}</td>
                <td className="p-4 capitalize">{p.gender}</td>
                <td className="p-4 max-w-xs truncate">
                  {p.injury_description || "—"}
                </td>
                <td className="p-4 max-w-xs truncate">
                  {p.goals || "—"}
                </td>
              </tr>
            ))}

            {patients.length === 0 && (
              <tr>
                <td
                  colSpan="6"
                  className="p-6 text-center text-slate-400"
                >
                  No patients assigned to this physician
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
