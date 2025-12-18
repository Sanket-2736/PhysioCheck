import { Outlet, NavLink, useNavigate, Navigate } from "react-router-dom";
import {
  LayoutDashboard,
  Users,
  Bell,
  LogOut
} from "lucide-react";
import { useAuthPhysician } from "../context/AuthPhysicianContext";
import { usePhysicianNotifications } from "../context/PhysicianNotificationContext";

export default function PhysicianLayout() {
  const { physician, loading, logout } = useAuthPhysician();
  const { pendingCount } = usePhysicianNotifications();
  const navigate = useNavigate();

  // ⏳ WAIT until auth check finishes
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900 text-white">
        Checking session...
      </div>
    );
  }

  // 🚫 Redirect ONLY after loading
  if (!physician) {
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
          onClick={() => navigate("/physician")}
        >
          PhysioCheck
          <span className="block text-sm text-slate-400">
            Physician Panel
          </span>
        </h2>

        <nav className="flex-1 space-y-2">
          <SidebarLink
            to="."
            icon={<LayoutDashboard size={20} />}
            label="Dashboard"
            end
          />

          <SidebarLink
            to="patients"
            icon={<Users size={20} />}
            label="My Patients"
          />

          <SidebarLink
            to="requests"
            icon={<Bell size={20} />}
            label="Requests"
            badge={pendingCount}
          />
        </nav>

        <button
          onClick={handleLogout}
          className="flex items-center gap-3 text-red-400 hover:text-red-300 mt-10"
        >
          <LogOut size={20} />
          Logout
        </button>
      </aside>

      <main className="flex-1 p-8 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
}

/* -------------------- */
/* Sidebar Link         */
/* -------------------- */
function SidebarLink({ to, icon, label, end = false, badge }) {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) =>
        `relative flex items-center gap-3 px-4 py-3 rounded-lg transition ${
          isActive
            ? "bg-blue-600 text-white"
            : "text-slate-300 hover:bg-slate-700"
        }`
      }
    >
      {icon}
      <span className="font-medium">{label}</span>

      {badge > 0 && (
        <span className="absolute right-4 top-2 bg-red-600 text-white text-xs px-2 py-1 rounded-full">
          {badge}
        </span>
      )}
    </NavLink>
  );
}
