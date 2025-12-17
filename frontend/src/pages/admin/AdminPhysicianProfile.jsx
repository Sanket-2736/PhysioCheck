import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../../api/axios";
import { toast } from "react-toastify";

export default function AdminPhysicianProfile() {
  const { id } = useParams(); // physician user_id
  const navigate = useNavigate();

  const [physician, setPhysician] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const res = await api.get(`/admin/physicians/${id}`);
      setPhysician(res.data.physician);
    } catch (err) {
      toast.error("Failed to load physician profile");
      navigate("/admin/physicians");
    } finally {
      setLoading(false);
    }
  };

  const approvePhysician = async () => {
    if (!confirm("Approve this physician?")) return;

    try {
      await api.post(`/admin/physicians/${id}/approve`);
      toast.success("Physician approved");
      navigate("/admin/physicians");
    } catch {
      toast.error("Approval failed");
    }
  };

  const rejectPhysician = async () => {
    if (!confirm("Reject and permanently remove this physician?")) return;

    try {
      await api.post(`/admin/physicians/${id}/reject`);
      toast.success("Physician rejected");
      navigate("/admin/physicians");
    } catch {
      toast.error("Rejection failed");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900 text-white">
        Loading profile...
      </div>
    );
  }

  if (!physician) return null;

  return (
    <div className="min-h-screen bg-slate-900 text-white p-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Physician Profile</h1>

        <button
          onClick={() => navigate("/admin/physicians")}
          className="bg-slate-700 hover:bg-slate-600 px-4 py-2 rounded-lg"
        >
          ← Back
        </button>
      </div>

      {/* Profile Card */}
      <div className="bg-slate-800 rounded-2xl p-8 shadow-lg grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left: Images */}
        <div className="space-y-6">
          <ImageBlock
            title="Profile Photo"
            src={physician.profile_photo}
          />
          <ImageBlock
            title="Credential Proof"
            src={physician.credential_photo}
          />
        </div>

        {/* Right: Details */}
        <div className="lg:col-span-2 space-y-6">
          <Info label="Full Name" value={physician.full_name} />
          <Info label="Email" value={physician.email} />
          <Info label="Specialization" value={physician.specialization} />
          <Info label="License ID" value={physician.license_id} />
          <Info
            label="Years of Experience"
            value={physician.years_experience}
          />
          <Info
            label="Verification Status"
            value={physician.is_verified ? "Verified" : "Pending"}
            highlight={!physician.is_verified}
          />

          {!physician.is_verified && (
            <div className="flex gap-4 pt-4">
              <button
                onClick={approvePhysician}
                className="bg-green-600 hover:bg-green-700 px-6 py-2 rounded-lg font-semibold"
              >
                Approve
              </button>

              <button
                onClick={rejectPhysician}
                className="bg-red-600 hover:bg-red-700 px-6 py-2 rounded-lg font-semibold"
              >
                Reject
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/* ------------------ */
/* Helper Components  */
/* ------------------ */

function Info({ label, value, highlight }) {
  return (
    <div>
      <p className="text-sm text-slate-400">{label}</p>
      <p
        className={`text-lg font-semibold ${
          highlight ? "text-yellow-400" : ""
        }`}
      >
        {value || "—"}
      </p>
    </div>
  );
}

function ImageBlock({ title, src }) {
  return (
    <div>
      <p className="text-sm text-slate-400 mb-2">{title}</p>
      {src ? (
        <img
          src={src}
          alt={title}
          className="rounded-xl border border-slate-700 w-full object-cover"
        />
      ) : (
        <div className="bg-slate-700 rounded-xl p-6 text-center text-slate-400">
          Not uploaded
        </div>
      )}
    </div>
  );
}
