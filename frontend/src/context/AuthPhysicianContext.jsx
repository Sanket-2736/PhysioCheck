import { createContext, useContext, useEffect, useState } from "react";
import api from "../api/axios";

const AuthPhysicianContext = createContext(null);

export function AuthPhysicianProvider({ children }) {
  const [physician, setPhysician] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkPhysicianAuth();
  }, []);

  const checkPhysicianAuth = async () => {
    const token = localStorage.getItem("token");
    const role = localStorage.getItem("role");

    // ❗ Do NOT redirect here
    if (!token || role !== "physician") {
      setLoading(false);
      return;
    }

    try {
      const res = await api.get("/auth/me");

      if (res.data.role !== "physician") {
        setPhysician(null);
      } else {
        setPhysician(res.data);
      }
    } catch (err) {
      setPhysician(null);
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    localStorage.removeItem("user_id");
    setPhysician(null);
  };

  return (
    <AuthPhysicianContext.Provider
      value={{
        physician,
        loading,
        isPhysicianAuthenticated: !!physician,
        logout,
      }}
    >
      {children}
    </AuthPhysicianContext.Provider>
  );
}

export function useAuthPhysician() {
  const ctx = useContext(AuthPhysicianContext);
  if (!ctx) {
    throw new Error("useAuthPhysician must be used inside AuthPhysicianProvider");
  }
  return ctx;
}
