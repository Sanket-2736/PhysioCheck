import { useEffect, useState } from "react";
import api from "../../api/axios";
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";

export default function AdminPhysicians() {
  const [physicians, setPhysicians] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchPhysicians();
  }, []);

  const fetchPhysicians = async () => {
    try {
      const res = await api.get("/admin/physicians");
      setPhysicians(res.data.physicians);
    } catch (err) {
      toast.error("Failed to load physicians");
    } finally {
      setLoading(false);
    }
  };

  const approvePhysician = async (userId) => {
    if (!confirm("Approve this physician?")) return;

    try {
      await api.post(`/admin/physicians/${userId}/approve`);
      toast.success("Physician approved");
      fetchPhysicians();
    } catch {
      toast.error("Approval failed");
    }
  };

  const rejectPhysician = async (userId) => {
    if (!confirm("Reject and remove this physician?")) return;

    try {
      await api.post(`/admin/physicians/${userId}/reject`);
      toast.success("Physician rejected");
      fetchPhysicians();
    } catch {
      toast.error("Rejection failed");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900 text-white">
        Loading physicians...
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 text-white p-8">
      <h1 className="text-3xl font-bold mb-8">Physicians</h1>

      <div className="overflow-x-auto bg-slate-800 rounded-xl">
        <table className="w-full text-left">
          <thead className="bg-slate-700 text-slate-200">
            <tr>
              <th className="p-4">Name</th>
              <th className="p-4">Email</th>
              <th className="p-4">Specialization</th>
              <th className="p-4 text-center">Patients</th>
              <th className="p-4 text-center">Status</th>
              <th className="p-4 text-center">Actions</th>
            </tr>
          </thead>

          <tbody>
            {physicians.map((p) => (
              <tr
                key={p.user_id}
                className="border-b border-slate-700 hover:bg-slate-700/40"
              >
                <td className="p-4 font-semibold">{p.full_name}</td>
                <td className="p-4 text-slate-300">{p.email}</td>
                <td className="p-4">{p.specialization}</td>

                <td className="p-4 text-center">
                  <span className="bg-slate-700 px-3 py-1 rounded-full">
                    {p.patient_count}
                  </span>
                </td>

                <td className="p-4 text-center">
                  {p.is_verified ? (
                    <span className="text-green-400 font-semibold">
                      Verified
                    </span>
                  ) : (
                    <span className="text-yellow-400 font-semibold">
                      Pending
                    </span>
                  )}
                </td>

                <td className="p-4">
                  <div className="flex justify-center gap-2">
                    <button
                      onClick={() =>
                        navigate(`/admin/physicians/${p.user_id}`)
                      }
                      className="px-3 py-1 rounded bg-blue-600 hover:bg-blue-700 text-sm"
                    >
                      View Profile
                    </button>

                    <button
                      onClick={() =>
                        navigate(`/admin/physicians/${p.user_id}/patients`)
                      }
                      className="px-3 py-1 rounded bg-slate-600 hover:bg-slate-500 text-sm"
                    >
                      View Patients
                    </button>

                    {!p.is_verified && (
                      <>
                        <button
                          onClick={() => approvePhysician(p.user_id)}
                          className="px-3 py-1 rounded bg-green-600 hover:bg-green-700 text-sm"
                        >
                          Approve
                        </button>

                        <button
                          onClick={() => rejectPhysician(p.user_id)}
                          className="px-3 py-1 rounded bg-red-600 hover:bg-red-700 text-sm"
                        >
                          Reject
                        </button>
                      </>
                    )}
                  </div>
                </td>
              </tr>
            ))}

            {physicians.length === 0 && (
              <tr>
                <td colSpan="6" className="p-6 text-center text-slate-400">
                  No physicians found
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
