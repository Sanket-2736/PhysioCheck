import React, { useEffect, useState } from "react";
import api from "../../api/axios";

export default function PhysicianList() {
  const [physicians, setPhysicians] = useState([]);
  const [myPhysicianId, setMyPhysicianId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  /* ================= FETCH DATA ================= */
  const fetchData = async () => {
    try {
      const [physiciansRes, meRes] = await Promise.all([
        api.get("/physician"),
        api.get("/patient/me")
      ]);

      setPhysicians(physiciansRes.data.physicians || []);
      setMyPhysicianId(meRes.data.patient?.physician_id || null);
    } catch (err) {
      console.error(err);
      setError("Failed to load physicians");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  /* ================= ACTIONS ================= */
  const sendRequest = async (physicianId) => {
    try {
      await api.post(`/subscription/request/${physicianId}`);
      alert("Subscription request sent");
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to send request");
    }
  };

  const unsubscribe = async () => {
    if (!window.confirm("Unsubscribe from your physician?")) return;

    await api.post("/subscription/unsubscribe");
    setMyPhysicianId(null);
  };

  /* ================= UI STATES ================= */
  if (loading) {
    return <div className="text-slate-300">Loading physicians...</div>;
  }

  if (error) {
    return <div className="text-red-400">{error}</div>;
  }

  return (
    <div className="max-w-6xl mx-auto text-white space-y-6">
      <h1 className="text-2xl font-bold">Physicians</h1>

      {physicians.length === 0 ? (
        <p className="text-slate-400">No physicians available.</p>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {physicians.map((physician) => (
            <PhysicianCard
              key={physician.physician_id}
              physician={physician}
              isSubscribed={myPhysicianId === physician.physician_id}
              onSubscribe={() => sendRequest(physician.physician_id)}
              onUnsubscribe={unsubscribe}
            />
          ))}
        </div>
      )}
    </div>
  );
}

/* ================= CARD ================= */
function PhysicianCard({
  physician,
  isSubscribed,
  onSubscribe,
  onUnsubscribe
}) {
  return (
    <div className="bg-slate-800 rounded-lg p-5 space-y-4 shadow">
      <div className="flex items-center gap-4">
        <img
          src={physician.profile_photo || "/default-avatar.png"}
          alt="physician"
          className="w-14 h-14 rounded-full object-cover"
        />

        <div>
          <h2 className="text-lg font-semibold">
            {physician.full_name}
          </h2>
          <p className="text-sm text-slate-400">
            {physician.specialization || "Physician"}
          </p>
        </div>
      </div>

      <p className="text-sm text-slate-300">
        {physician.bio || "No bio provided."}
      </p>

      <p className="text-sm text-slate-400">
        Experience:{" "}
        <span className="text-white">
          {physician.years_experience || 0} years
        </span>
      </p>

      {isSubscribed ? (
        <button
          onClick={onUnsubscribe}
          className="w-full py-2 bg-red-600 hover:bg-red-700 rounded"
        >
          Unsubscribe
        </button>
      ) : (
        <button
          onClick={onSubscribe}
          className="w-full py-2 bg-blue-600 hover:bg-blue-700 rounded"
        >
          Send Subscription Request
        </button>
      )}
    </div>
  );
}
