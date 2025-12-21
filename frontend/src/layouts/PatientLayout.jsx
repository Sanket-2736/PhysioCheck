import { Outlet, NavLink, useNavigate, Navigate } from "react-router-dom";
import {
  LayoutDashboard,
  User,
  Activity,
  Users,
  LogOut
} from "lucide-react";
import { useAuthPatient } from "../context/AuthPatientContext";

export default function PatientLayout() {
  const { patient, loading, logout } = useAuthPatient();
  const navigate = useNavigate();

  // ⏳ Wait for auth check
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900 text-white">
        Checking session...
      </div>
    );
  }

  // 🚫 Redirect if not authenticated
  if (!patient) {
    return <Navigate to="/login" replace />;
  }

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="min-h-screen flex bg-slate-900 text-white">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-800 p-6 flex flex-col">
        <h2
          className="text-2xl font-bold mb-10 cursor-pointer"
          onClick={() => navigate("/patient")}
        >
          PhysioCheck
          <span className="block text-sm text-slate-400">
            Patient Panel
          </span>
        </h2>

        {/* Navigation */}
        <nav className="flex-1 space-y-2">
          <SidebarLink
            to="."
            icon={<LayoutDashboard size={20} />}
            label="Dashboard"
            end
          />

          <SidebarLink
            to="rehab-plan"
            icon={<Activity size={20} />}
            label="My Rehab Plan"
          />

          <SidebarLink
            to="physicians"
            icon={<Users size={20} />}
            label="Physicians"
          />

          <SidebarLink
            to="me"
            icon={<User size={20} />}
            label="My Profile"
          />

          {/* Logout */}
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-red-400 hover:bg-slate-700 hover:text-red-300 transition"
          >
            <LogOut size={20} />
            <span className="font-medium">Logout</span>
          </button>
        </nav>
      </aside>

      {/* Content */}
      <main className="flex-1 p-8 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
}

function SidebarLink({ to, icon, label, end = false }) {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) =>
        `flex items-center gap-3 px-4 py-3 rounded-lg transition ${
          isActive
            ? "bg-blue-600 text-white"
            : "text-slate-300 hover:bg-slate-700"
        }`
      }
    >
      {icon}
      <span className="font-medium">{label}</span>
    </NavLink>
  );
}
