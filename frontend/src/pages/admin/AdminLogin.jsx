import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../api/axios";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

export default function AdminLogin() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!email || !password) {
      toast.error("Email and password are required");
      return;
    }

    try {
      setLoading(true);

      const res = await api.post("/auth/login-admin", {
        email,
        password,
      });

      localStorage.setItem("token", res.data.access_token);
      localStorage.setItem("role", "admin");
      localStorage.setItem("user_id", res.data.user_id);

      toast.success("Admin login successful");

      setTimeout(() => {
        navigate("/admin/dashboard");
      }, 700);
    } catch (err) {
      toast.error(
        err.response?.data?.detail ||
          err.response?.data?.message ||
          "Invalid admin credentials"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900">
      <ToastContainer position="top-right" />

      <form
        onSubmit={handleSubmit}
        className="w-full max-w-md bg-slate-800 p-8 rounded-2xl shadow-xl space-y-6"
      >
        <h1 className="text-2xl font-bold text-white text-center">
          Admin Login
        </h1>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1">
            Admin Email
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="input"
            placeholder="admin@physiocheck.com"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1">
            Password
          </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="input"
            placeholder="••••••••"
            required
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 py-2 rounded-lg text-white font-semibold transition disabled:opacity-50"
        >
          {loading ? "Logging in..." : "Login as Admin"}
        </button>

        <p className="text-xs text-center text-slate-400">
          Authorized administrators only
        </p>
      </form>
    </div>
  );
}
