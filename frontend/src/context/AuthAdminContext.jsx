import { createContext, useContext, useEffect, useState } from "react";
import api from "../api/axios";

const AuthAdminContext = createContext(null);

export function AuthAdminProvider({ children }) {
  const [admin, setAdmin] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAdminAuth();
  }, []);

  const checkAdminAuth = async () => {
    const token = localStorage.getItem("token");
    const role = localStorage.getItem("role");

    // 🔒 Basic frontend guard
    if (!token || role !== "admin") {
      setLoading(false);
      return;
    }

    try {
      // Optional: verify token via /auth/me
      const res = await api.get("/auth/me");

      if (res.data.role !== "admin") {
        logout();
        return;
      }

      setAdmin(res.data);
    } catch (err) {
      logout();
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    localStorage.removeItem("user_id");
    setAdmin(null);
    window.location.href = "/";
  };

  return (
    <AuthAdminContext.Provider
      value={{
        admin,
        loading,
        isAdminAuthenticated: !!admin,
        logout,
      }}
    >
      {children}
    </AuthAdminContext.Provider>
  );
}

export function useAuthAdmin() {
  const ctx = useContext(AuthAdminContext);
  if (!ctx) {
    throw new Error("useAuthAdmin must be used inside AuthAdminProvider");
  }
  return ctx;
}
