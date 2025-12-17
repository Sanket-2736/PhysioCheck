import { useEffect, useState } from "react";
import api from "../../api/axios";
import { toast } from "react-toastify";

export default function AdminUsers() {
  const [users, setUsers] = useState([]);
  const [loadingId, setLoadingId] = useState(null);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const res = await api.get("/admin/users");
      setUsers(res.data?.patients || []);
    } catch {
      toast.error("Failed to load users");
      setUsers([]);
    }
  };

  const toggleUser = async (u) => {
    try {
      setLoadingId(u.user_id);

      // 🔥 Optimistic UI update
      setUsers((prev) =>
        prev.map((p) =>
          p.user_id === u.user_id
            ? { ...p, is_active: !p.is_active }
            : p
        )
      );

      if (u.is_active) {
        await api.patch(`/admin/users/${u.user_id}/disable`);
        toast.success("User disabled");
      } else {
        await api.patch(`/admin/users/${u.user_id}/enable`);
        toast.success("User enabled");
      }
    } catch {
      toast.error("Action failed");
      fetchUsers(); // rollback from server
    } finally {
      setLoadingId(null);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white p-8">
      <h1 className="text-3xl font-bold mb-6">Users</h1>

      <div className="bg-slate-800 rounded-xl overflow-x-auto">
        <table className="w-full">
          <thead className="bg-slate-700">
            <tr>
              <th className="p-4 text-left">Name</th>
              <th className="p-4 text-left">Email</th>
              <th className="p-4 text-left">Gender</th>
              <th className="p-4 text-left">Status</th>
              <th className="p-4 text-left">Action</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr
                key={u.user_id}
                className="border-b border-slate-700"
              >
                <td className="p-4">{u.full_name}</td>
                <td className="p-4">{u.email}</td>
                <td className="p-4 capitalize">{u.gender}</td>
                <td className="p-4">
                  <span
                    className={`px-2 py-1 rounded text-sm ${
                      u.is_active
                        ? "bg-green-600/20 text-green-400"
                        : "bg-red-600/20 text-red-400"
                    }`}
                  >
                    {u.is_active ? "Active" : "Disabled"}
                  </span>
                </td>
                <td className="p-4">
                  <button
                    disabled={loadingId === u.user_id}
                    onClick={() => toggleUser(u)}
                    className={`px-4 py-1 rounded font-medium transition ${
                      u.is_active
                        ? "bg-red-600 hover:bg-red-700"
                        : "bg-green-600 hover:bg-green-700"
                    } disabled:opacity-50`}
                  >
                    {loadingId === u.user_id
                      ? "Processing..."
                      : u.is_active
                      ? "Disable"
                      : "Enable"}
                  </button>
                </td>
              </tr>
            ))}

            {users.length === 0 && (
              <tr>
                <td
                  colSpan="5"
                  className="p-6 text-center text-slate-400"
                >
                  No users found
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
