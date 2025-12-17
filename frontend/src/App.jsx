import React from "react";
import { Route, Routes } from "react-router-dom";

import Login from "./pages/Login";
import Signup from "./pages/Signup";

// 🔐 Admin auth + layout
import { AuthAdminProvider } from "./context/AuthAdminContext";
import AdminLayout from "./layouts/AdminLayout";

// 📊 Admin pages
import AdminDashboard from "./pages/admin/AdminDashboard";
import AdminPhysicians from "./pages/admin/AdminPhysicians";
import AdminPhysicianProfile from "./pages/admin/AdminPhysicianProfile";
import AdminPhysicianPatients from "./pages/admin/AdminPhysicianPatients";
import AdminUsers from "./pages/admin/AdminUsers";
import AdminAuditLogs from "./pages/admin/AdminAuditLogs";
import AdminLogin from "./pages/admin/AdminLogin";

function App() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<Signup />} />
      <Route path="/login" element={<Login />} />

      {/* Admin login (outside protected layout) */}
      <Route path="/admin/login" element={<AdminLogin />} />

      {/* ================= ADMIN ROUTES ================= */}
      <Route
        path="/admin"
        element={
          <AuthAdminProvider>
            <AdminLayout />
          </AuthAdminProvider>
        }
      >
        {/* index = /admin */}
        <Route index element={<AdminDashboard />} />

        {/* relative paths */}
        <Route path="dashboard" element={<AdminDashboard />} />
        <Route path="physicians" element={<AdminPhysicians />} />
        <Route path="physicians/:id" element={<AdminPhysicianProfile />} />
        <Route path="physicians/:id/patients" element={<AdminPhysicianPatients />} />
        <Route path="audit-logs" element={<AdminAuditLogs />} />
        <Route path="users" element={<AdminUsers />} />
      </Route>
    </Routes>
  );
}
export default App;
