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

import { AuthPatientProvider } from "./context/AuthPatientContext";
import PatientLayout from "./layouts/PatientLayout";

import PatientDashboard from "./pages/patient/PatientDashboard";
import PatientProfile from "./pages/patient/PatientProfile";
import PhysicianList from "./pages/patient/PhysicianList";
import PatientPhysicianProfile from "./pages/patient/PatientPhysicianProfile";

/* ================= PHYSICIAN ================= */

// 🔐 Physician auth + layout
import { AuthPhysicianProvider } from "./context/AuthPhysicianContext";
import { PhysicianNotificationProvider } from "./context/PhysicianNotificationContext";

// 👨‍⚕️ Physician pages
import PhysicianDashboard from "./pages/physician/PhysicianDashboard";
import PhysicianPatientProfile from "./pages/physician/PhysicianPatientProfile";
import PhysicianPatients from "./pages/physician/PhysicianPatients";
import PhysicianRequests from "./pages/physician/PhysicianRequests";
import PhysicianProfile from "./pages/physician/PhysicianProfile";
import PhysicianLayout from "./layouts/PhysicianLayout";
import MyExercises from "./pages/physician/MyExercises";
import ExerciseCapture from "./pages/physician/ExerciseCapture";
import PatientRehabPlan from "./pages/patient/PatientRehabPlan";
import PatientExerciseSession from "./pages/patient/PatientExerciseSession";
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
          path="rehab-plan/:patientExerciseId/start"
          element={<PatientExerciseSession />}
        />
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
        <Route path="rehab-plan" element={<PatientRehabPlan />} />
        <Route path="me" element={<PatientProfile />} />
        <Route path="physicians" element={<PhysicianList />} />
        <Route path="physicians/:id" element={<PatientPhysicianProfile />} />
        <Route path="physicians" element={<PhysicianList />} />

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
        <Route path="patients/:id" element={<PhysicianPatientProfile />} />
        <Route path="requests" element={<PhysicianRequests />} />
        <Route path="me" element={<PhysicianProfile />} />
        <Route path="exercises" element={<MyExercises />} />
        <Route
          path="exercises/:exerciseId/capture"
          element={<ExerciseCapture />}
        />
      </Route>

    </Routes>
  );
}

export default App;
