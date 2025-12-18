import { createContext, useContext, useEffect, useState } from "react";
import api from "../api/axios";

const PhysicianNotificationContext = createContext(null);

export function PhysicianNotificationProvider({ children }) {
  const [pendingCount, setPendingCount] = useState(0);
  const [loading, setLoading] = useState(true);

  const fetchPendingRequests = async () => {
    try {
      const res = await api.get("/subscription/physician/requests");
      setPendingCount(res.data.requests?.length || 0);
    } catch (err) {
      console.error("Failed to fetch physician notifications", err);
      setPendingCount(0);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPendingRequests(); // initial fetch

    // 🔁 Poll every 15 seconds
    const interval = setInterval(fetchPendingRequests, 15000);

    return () => clearInterval(interval);
  }, []);

  return (
    <PhysicianNotificationContext.Provider
      value={{
        pendingCount,
        loading,
        refreshNotifications: fetchPendingRequests,
      }}
    >
      {children}
    </PhysicianNotificationContext.Provider>
  );
}

export function usePhysicianNotifications() {
  const ctx = useContext(PhysicianNotificationContext);
  if (!ctx) {
    throw new Error(
      "usePhysicianNotifications must be used inside PhysicianNotificationProvider"
    );
  }
  return ctx;
}
