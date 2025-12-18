import React, { useEffect, useState } from "react";
import api from "../../api/axios";

export default function PatientProfile() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await api.get("/auth/me");
        setUser(res.data);
      } catch (err) {
        console.error(err);
        setError("Failed to load profile");
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);

  if (loading) return <div className="p-6">Loading profile...</div>;
  if (error) return <div className="p-6 text-red-600">{error}</div>;

  return (
    <div className="max-w-3xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">My Profile</h1>

      <div className="bg-white shadow rounded-lg p-6 space-y-6">

        {/* 👤 Profile Photo */}
        <div className="flex items-center gap-6">
          <img
            src={user.profile_photo || "/default-avatar.png"}
            alt="Profile"
            className="w-28 h-28 rounded-full object-cover border"
          />
          <div>
            <h2 className="text-xl font-semibold">{user.full_name}</h2>
            <p className="text-gray-500">{user.email}</p>
          </div>
        </div>

        {/* Details */}
        <ProfileRow label="User ID" value={user.id} />
        <ProfileRow label="Phone" value={user.phone || "—"} />
        <ProfileRow label="Age" value={user.age || "—"} />
        <ProfileRow label="Gender" value={user.gender || "—"} />
        <ProfileRow label="Height (cm)" value={user.height_cm || "—"} />
        <ProfileRow label="Weight (kg)" value={user.weight_kg || "—"} />
        <ProfileRow label="Injury" value={user.injury_description || "—"} />
        <ProfileRow label="Goals" value={user.goals || "—"} />
        <ProfileRow
          label="Account Created"
          value={new Date(user.created_at).toLocaleString()}
        />
      </div>
    </div>
  );
}

function ProfileRow({ label, value }) {
  return (
    <div className="flex justify-between border-b pb-2 text-sm">
      <span className="font-medium text-gray-600">{label}</span>
      <span className="text-gray-900">{value}</span>
    </div>
  );
}
