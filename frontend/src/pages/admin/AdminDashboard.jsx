import { Navigate } from "react-router-dom";
import { useAuthAdmin } from "../../context/AuthAdminContext";
import api from "../../api/axios";
import { useEffect, useState } from "react";
import { toast } from "react-toastify";

export default function AdminDashboard() {
  const { admin, loading, logout } = useAuthAdmin();

  const [stats, setStats] = useState(null);
  const [analytics, setAnalytics] = useState([]);
  const [report, setReport] = useState(null);
  const [selectedPhysician, setSelectedPhysician] = useState("");

  useEffect(() => {
    if (admin) {
      fetchStats();
      fetchAnalytics();
    }
  }, [admin]);

  const fetchStats = async () => {
    try {
      const res = await api.get("/admin/stats");
      setStats(res.data);
    } catch {
      toast.error("Failed to load admin stats");
    }
  };

  const fetchAnalytics = async () => {
    try {
      const res = await api.get("/admin/analytics/physicians");
      setAnalytics(res.data.analytics);
    } catch {
      toast.error("Failed to load physician analytics");
    }
  };

  const fetchPhysicianReport = async () => {
    if (!selectedPhysician) {
      toast.warn("Select a physician");
      return;
    }

    try {
      const res = await api.get(
        `/admin/reports/physician/${selectedPhysician}`
      );
      setReport(res.data);
      toast.success("Report generated");
    } catch {
      toast.error("Failed to generate report");
    }
  };

  /* ---------------- AUTH GUARDS ---------------- */

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900 text-white">
        Checking admin access...
      </div>
    );
  }

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

  /* ---------------- UI ---------------- */

  return (
    <div className="min-h-screen bg-slate-900 p-8 text-white space-y-12">
      {/* HEADER */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Admin Dashboard</h1>

        <button
          onClick={logout}
          className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg font-semibold"
        >
          Logout
        </button>
      </div>

      {/* STATS */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard title="Total Users" value={stats.total_users} />
        <StatCard title="Patients" value={stats.total_patients} />
        <StatCard title="Physicians" value={stats.total_physicians} />
        <StatCard
          title="Pending Physicians"
          value={stats.pending_physicians}
          color="yellow"
        />
        <StatCard
          title="Verified Physicians"
          value={stats.verified_physicians}
          color="green"
        />
        <StatCard title="Rehab Plans" value={stats.total_rehab_plans} />
        <StatCard title="Sessions" value={stats.total_sessions} />
      </div>

      {/* PHYSICIAN ANALYTICS */}
      <section>
        <h2 className="text-xl font-semibold mb-4">
          Physician Performance Analytics
        </h2>

        <div className="overflow-x-auto bg-slate-800 rounded-xl">
          <table className="w-full text-left">
            <thead className="bg-slate-700 text-slate-200">
              <tr>
                <th className="p-4">Physician ID</th>
                <th className="p-4">Patients</th>
                <th className="p-4">Sessions</th>
                <th className="p-4">Completed</th>
                <th className="p-4">Completion %</th>
              </tr>
            </thead>

            <tbody>
              {analytics.map((a) => (
                <tr
                  key={a.physician_id}
                  className="border-b border-slate-700 hover:bg-slate-700/40"
                >
                  <td className="p-4">{a.physician_id}</td>
                  <td className="p-4">{a.total_patients}</td>
                  <td className="p-4">{a.total_sessions}</td>
                  <td className="p-4">{a.completed_sessions}</td>
                  <td className="p-4 font-semibold">
                    {a.completion_rate.toFixed(1)}%
                  </td>
                </tr>
              ))}

              {analytics.length === 0 && (
                <tr>
                  <td colSpan="5" className="p-6 text-center text-slate-400">
                    No analytics available
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      {/* PHYSICIAN REPORT */}
      <section>
        <h2 className="text-xl font-semibold mb-4">
          Generate Physician Report
        </h2>

        <div className="flex flex-wrap gap-4 items-center">
          <select
            value={selectedPhysician}
            onChange={(e) => setSelectedPhysician(e.target.value)}
            className="bg-slate-800 border border-slate-700 px-4 py-2 rounded-lg"
          >
            <option value="">Select Physician ID</option>
            {analytics.map((a) => (
              <option key={a.physician_id} value={a.physician_id}>
                {a.physician_id}
              </option>
            ))}
          </select>

          <button
            onClick={fetchPhysicianReport}
            className="bg-blue-600 hover:bg-blue-700 px-5 py-2 rounded-lg font-semibold"
          >
            Generate Report
          </button>
        </div>

        {report && (
          <div className="mt-6 bg-slate-800 rounded-xl p-6 space-y-2">
            <p>
              <span className="text-slate-400">Physician ID:</span>{" "}
              {report.physician_id}
            </p>
            <p>
              <span className="text-slate-400">Total Sessions:</span>{" "}
              {report.total_sessions}
            </p>
            <p>
              <span className="text-slate-400">Completed Sessions:</span>{" "}
              {report.completed_sessions}
            </p>
            <p>
              <span className="text-slate-400">Generated At:</span>{" "}
              {new Date(report.generated_at).toLocaleString()}
            </p>
          </div>
        )}
      </section>
    </div>
  );
}

/* ------------------ */
/* STAT CARD          */
/* ------------------ */
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
