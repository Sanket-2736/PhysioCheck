import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../../api/axios";

export default function PatientPhysicianProfile() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [physician, setPhysician] = useState(null);
  const [loading, setLoading] = useState(true);
  const [subscribing, setSubscribing] = useState(false);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await api.get(`/physicians`);
        const found = res.data.physicians.find(
          (p) => p.physician_id === Number(id)
        );
        setPhysician(found);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [id]);

  const handleSubscribe = async () => {
    try {
      setSubscribing(true);
      await api.post(`/subscription/subscribe/${physician.physician_id}`);
      alert("Subscription request sent!");
      navigate("/patient");
    } catch (err) {
      alert("Failed to subscribe");
    } finally {
      setSubscribing(false);
    }
  };

  if (loading) return <div>Loading profile...</div>;
  if (!physician) return <div>Physician not found</div>;

  return (
    <div className="max-w-3xl mx-auto bg-white rounded-lg shadow p-6">
      <div className="flex items-center gap-6">
        <img
          src={physician.profile_photo || "/default-avatar.png"}
          alt="profile"
          className="w-28 h-28 rounded-full object-cover"
        />
        <div>
          <h1 className="text-2xl font-bold">{physician.full_name}</h1>
          <p className="text-gray-600">{physician.specialization}</p>
          <p className="text-sm text-gray-500">
            {physician.years_experience} years experience
          </p>
        </div>
      </div>

      <button
        disabled={subscribing}
        onClick={handleSubscribe}
        className="mt-6 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
      >
        {subscribing ? "Sending request..." : "Subscribe"}
      </button>
    </div>
  );
}
