import React from "react";
import { Route, Routes } from "react-router-dom";

import Login from "./pages/Login";
import Signup from "./pages/Signup";

/* ================= ADMIN ================= */

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

/* ================= PATIENT ================= */

// 🔐 Patient auth + layout
import { AuthPatientProvider } from "./context/AuthPatientContext";
import PatientLayout from "./layouts/PatientLayout";

// 👤 Patient pages
import PatientDashboard from "./pages/patient/PatientDashboard";
import PatientProfile from "./pages/patient/PatientProfile";
import PhysicianList from "./pages/patient/PhysicianList";
import PhysicianProfile from "./pages/patient/PhysicianProfile";

/* ================= PHYSICIAN ================= */

// 🔐 Physician auth + layout
import { AuthPhysicianProvider } from "./context/AuthPhysicianContext";
import { PhysicianNotificationProvider } from "./context/PhysicianNotificationContext";
import PhysicianLayout from "./layouts/PhysicianLayout";

// 👨‍⚕️ Physician pages
import PhysicianDashboard from "./pages/physician/PhysicianDashboard";
import PhysicianPatients from "./pages/physician/PhysicianPatients";
import PhysicianRequests from "./pages/physician/PhysicianRequests";

function App() {
  return (
    <Routes>
      {/* ================= PUBLIC ================= */}
      <Route path="/" element={<Signup />} />
      <Route path="/login" element={<Login />} />

      {/* ================= ADMIN ================= */}
      <Route path="/admin/login" element={<AdminLogin />} />

      <Route
        path="/admin"
        element={
          <AuthAdminProvider>
            <AdminLayout />
          </AuthAdminProvider>
        }
      >
        <Route index element={<AdminDashboard />} />
        <Route path="dashboard" element={<AdminDashboard />} />
        <Route path="physicians" element={<AdminPhysicians />} />
        <Route path="physicians/:id" element={<AdminPhysicianProfile />} />
        <Route
          path="physicians/:id/patients"
          element={<AdminPhysicianPatients />}
        />
        <Route path="audit-logs" element={<AdminAuditLogs />} />
        <Route path="users" element={<AdminUsers />} />
      </Route>

      {/* ================= PATIENT ================= */}
      <Route
        path="/patient"
        element={
          <AuthPatientProvider>
            <PatientLayout />
          </AuthPatientProvider>
        }
      >
        <Route index element={<PatientDashboard />} />
        <Route path="me" element={<PatientProfile />} />
        <Route path="physicians" element={<PhysicianList />} />
        <Route path="physicians/:id" element={<PhysicianProfile />} />
      </Route>

      {/* ================= PHYSICIAN ================= */}
      <Route
        path="/physician"
        element={
          <AuthPhysicianProvider>
            <PhysicianNotificationProvider>
              <PhysicianLayout />
            </PhysicianNotificationProvider>
          </AuthPhysicianProvider>
        }
      >
        <Route index element={<PhysicianDashboard />} />
        <Route path="patients" element={<PhysicianPatients />} />
        <Route path="requests" element={<PhysicianRequests />} />
      </Route>
    </Routes>
  );
}

export default App;
