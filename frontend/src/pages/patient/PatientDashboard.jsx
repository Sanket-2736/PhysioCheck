import React, { useEffect, useState } from "react";
import api from "../../api/axios";
import SubscriptionStatusCard from "../../components/patient/SubscriptionStatusCard";

export default function PatientDashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMe = async () => {
      try {
        const res = await api.get("/auth/me");
        setData(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchMe();
  }, []);

  if (loading) return <div>Loading dashboard...</div>;

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold">Patient Dashboard</h1>

      <SubscriptionStatusCard patient={data} />
    </div>
  );
}
