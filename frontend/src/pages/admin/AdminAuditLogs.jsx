import { useEffect, useState } from "react";
import api from "../../api/axios";
import { toast } from "react-toastify";

export default function AdminAuditLogs() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    try {
      const res = await api.get("/admin/audit-logs");
      setLogs(res.data.logs);
    } catch {
      toast.error("Failed to load audit logs");
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white p-8">
      <h1 className="text-3xl font-bold mb-6">Audit Logs</h1>

      <div className="bg-slate-800 rounded-xl overflow-x-auto">
        <table className="w-full">
          <thead className="bg-slate-700">
            <tr>
              <th className="p-4">Action</th>
              <th className="p-4">Target</th>
              <th className="p-4">Description</th>
              <th className="p-4">Time</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((l) => (
              <tr key={l.id} className="border-b border-slate-700">
                <td className="p-4 font-semibold">{l.action}</td>
                <td className="p-4">
                  {l.target_type} #{l.target_id}
                </td>
                <td className="p-4">{l.description}</td>
                <td className="p-4 text-slate-400">
                  {new Date(l.created_at).toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
