import { createContext, useContext, useEffect, useState } from "react";
import api from "../api/axios";

const AuthPatientContext = createContext(null);

export function AuthPatientProvider({ children }) {
  const [patient, setPatient] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkPatientAuth();
  }, []);

  const checkPatientAuth = async () => {
    const token = localStorage.getItem("token");
    const role = localStorage.getItem("role");

    // ❗ Do NOT redirect here
    if (!token || role !== "patient") {
      setLoading(false);
      return;
    }

    try {
      const res = await api.get("/auth/me");

      if (res.data.role !== "patient") {
        setPatient(null);
      } else {
        setPatient(res.data);
      }
    } catch (err) {
      setPatient(null);
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    localStorage.removeItem("user_id");
    setPatient(null);
  };

  return (
    <AuthPatientContext.Provider
      value={{
        patient,
        loading,
        isPatientAuthenticated: !!patient,
        logout,
      }}
    >
      {children}
    </AuthPatientContext.Provider>
  );
}

export function useAuthPatient() {
  const ctx = useContext(AuthPatientContext);
  if (!ctx) {
    throw new Error("useAuthPatient must be used inside AuthPatientProvider");
  }
  return ctx;
}
