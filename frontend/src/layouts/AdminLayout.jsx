import { Outlet, NavLink, useNavigate } from "react-router-dom";
import {
  LayoutDashboard,
  Users,
  UserCheck,
  ScrollText,
  LogOut
} from "lucide-react";
import { useAuthAdmin } from "../context/AuthAdminContext";

export default function AdminLayout() {
  const { logout } = useAuthAdmin();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();               // clear context + storage
    navigate("/admin/login"); // redirect to admin login
  };

  return (
    <div className="min-h-screen flex bg-slate-900 text-white">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-800 p-6 flex flex-col">
        {/* Branding */}
        <h2
          className="text-2xl font-bold mb-10 cursor-pointer"
          onClick={() => navigate("/admin")}
        >
          PhysioCheck
          <span className="block text-sm text-slate-400">
            Admin Panel
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
            to="physicians"
            icon={<UserCheck size={20} />}
            label="Physicians"
          />

          <SidebarLink
            to="users"
            icon={<Users size={20} />}
            label="Users"
          />

          <SidebarLink
            to="audit-logs"
            icon={<ScrollText size={20} />}
            label="Audit Logs"
          />
        </nav>

        {/* Logout */}
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 text-red-400 hover:text-red-300 mt-10"
        >
          <LogOut size={20} />
          Logout
        </button>
      </aside>

      {/* Page Content */}
      <main className="flex-1 p-8 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
}

/* -------------------- */
/* Sidebar Link         */
/* -------------------- */
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
