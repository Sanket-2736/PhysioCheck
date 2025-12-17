import { Navigate } from "react-router-dom";
import { useAuthAdmin } from "../../context/AuthAdminContext";
import api from "../../api/axios";
import { useEffect, useState } from "react";
import { toast } from "react-toastify";

export default function AdminDashboard() {
  const { admin, loading, logout } = useAuthAdmin();
  const [stats, setStats] = useState(null);

  useEffect(() => {
    if (admin) fetchStats();
  }, [admin]);

  const fetchStats = async () => {
    try {
      const res = await api.get("/admin/stats");
      setStats(res.data);
    } catch (err) {
      toast.error("Failed to load admin stats");
    }
  };

  // ⏳ Auth loading
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900 text-white">
        Checking admin access...
      </div>
    );
  }

  // 🔒 Not admin → kick out
  if (!admin) {
    return <Navigate to="/" />;
  }

  if (!stats) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900 text-white">
        Loading dashboard...
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 p-8 text-white">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Admin Dashboard</h1>

        <button
          onClick={logout}
          className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg font-semibold"
        >
          Logout
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard title="Total Users" value={stats.total_users} />
        <StatCard title="Patients" value={stats.total_patients} />
        <StatCard title="Physicians" value={stats.total_physicians} />
        <StatCard title="Pending Physicians" value={stats.pending_physicians} color="yellow" />
        <StatCard title="Verified Physicians" value={stats.verified_physicians} color="green" />
        <StatCard title="Rehab Plans" value={stats.total_rehab_plans} />
        <StatCard title="Sessions" value={stats.total_sessions} />
      </div>
    </div>
  );
}

function StatCard({ title, value, color = "blue" }) {
  const colors = {
    blue: "border-blue-500 text-blue-400",
    green: "border-green-500 text-green-400",
    yellow: "border-yellow-500 text-yellow-400",
  };

  return (
    <div className={`bg-slate-800 p-6 rounded-xl border-l-4 ${colors[color]}`}>
      <p className="text-sm text-slate-400">{title}</p>
      <p className="text-3xl font-bold mt-2">{value}</p>
    </div>
  );
}
