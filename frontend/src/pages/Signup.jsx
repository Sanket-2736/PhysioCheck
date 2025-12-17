import { useState } from "react";
import api from "../api/axios";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { useNavigate } from "react-router-dom";

export default function Signup() {
  const [role, setRole] = useState("patient");
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  const [form, setForm] = useState({});
  const [profilePhoto, setProfilePhoto] = useState(null);
  const [credentialPhoto, setCredentialPhoto] = useState(null);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

const handleSubmit = async (e) => {
  e.preventDefault();

  try {
    setLoading(true);

    const fd = new FormData();

    // COMMON FIELDS
    fd.append("full_name", form.full_name);
    fd.append("email", form.email);
    fd.append("password", form.password);

    if (role === "patient") {
      // PATIENT REQUIRED
      fd.append("age", form.age);
      fd.append("gender", form.gender);

      // PATIENT OPTIONAL
      if (form.height_cm) fd.append("height_cm", form.height_cm);
      if (form.weight_kg) fd.append("weight_kg", form.weight_kg);
      if (form.address) fd.append("address", form.address);
      if (form.injury_description)
        fd.append("injury_description", form.injury_description);
      if (form.goals) fd.append("goals", form.goals);

      if (profilePhoto) fd.append("profile_photo", profilePhoto);

      const res = await api.post("/auth/register", fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      localStorage.setItem("token", res.data.access_token);
      localStorage.setItem("user_id", res.data.user_id);
      localStorage.setItem("role", "patient");

      toast.success("Patient registered successfully!");

      setTimeout(() => {
        navigate('/patient')
      }, 800);
    }

    if (role === "physician") {
      fd.append("specialization", form.specialization);
      fd.append("license_id", form.license_id);
      fd.append("years_experience", form.years_experience);

      if (profilePhoto) fd.append("profile_photo", profilePhoto);
      if (credentialPhoto)
        fd.append("credential_photo", credentialPhoto);

      await api.post("/auth/register-physician", fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      toast.success(
        "Physician registered successfully. Pending admin approval."
      );

      setTimeout(() => {
        navigate('/')
      }, 1200);
    }

  } catch (err) {
    toast.error(
      err.response?.data?.detail ||
        err.response?.data?.message ||
        "Signup failed"
    );
  } finally {
    setLoading(false);
  }
};



  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900">
      <ToastContainer position="top-right" />

      <form
        onSubmit={handleSubmit}
        className="w-full max-w-2xl bg-slate-800 p-8 rounded-2xl shadow-xl space-y-6"
      >
        <h2 className="text-2xl font-bold text-white text-center">
          {role === "patient" ? "Patient Signup" : "Physician Signup"}
        </h2>

        {/* ROLE SWITCH */}
        <div className="flex gap-2">
          {["patient", "physician"].map((r) => (
            <button
              type="button"
              key={r}
              onClick={() => setRole(r)}
              className={`w-1/2 py-2 rounded-lg font-semibold transition ${
                role === r
                  ? "bg-blue-600 text-white"
                  : "bg-slate-700 text-slate-300"
              }`}
            >
              {r.toUpperCase()}
            </button>
          ))}
        </div>

        {/* COMMON FIELDS */}
        <Field label="Full Name *">
          <input
            name="full_name"
            onChange={handleChange}
            required
            className="input"
          />
        </Field>

        <Field label="Email *">
          <input
            type="email"
            name="email"
            onChange={handleChange}
            required
            className="input"
          />
        </Field>

        <Field label="Password *">
          <input
            type="password"
            name="password"
            onChange={handleChange}
            required
            className="input"
          />
        </Field>

        {/* PATIENT FIELDS */}
        {role === "patient" && (
          <>
            <Field label="Age *">
              <input
                type="number"
                name="age"
                onChange={handleChange}
                required
                className="input"
              />
            </Field>

            <Field label="Gender *">
              <select
                name="gender"
                onChange={handleChange}
                required
                className="input"
              >
                <option value="">Select gender</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>
            </Field>

            <Field label="Height (cm)">
              <input
                name="height_cm"
                onChange={handleChange}
                className="input"
              />
            </Field>

            <Field label="Weight (kg)">
              <input
                name="weight_kg"
                onChange={handleChange}
                className="input"
              />
            </Field>

            <Field label="Address">
              <input
                name="address"
                onChange={handleChange}
                className="input"
              />
            </Field>

            <Field label="Injury Description">
              <textarea
                name="injury_description"
                onChange={handleChange}
                className="input h-20"
              />
            </Field>

            {/* ✅ GOALS — TEXT INPUT (as requested) */}
            <Field label="Rehabilitation Goals">
              <input
                name="goals"
                onChange={handleChange}
                className="input"
                placeholder="e.g. Improve shoulder mobility, reduce pain"
              />
            </Field>
          </>
        )}

        {/* PHYSICIAN FIELDS */}
        {role === "physician" && (
          <>
            <Field label="Specialization *">
              <input
                name="specialization"
                onChange={handleChange}
                required
                className="input"
              />
            </Field>

            <Field label="License ID *">
              <input
                name="license_id"
                onChange={handleChange}
                required
                className="input"
              />
            </Field>

            <Field label="Years of Experience *">
              <input
                type="number"
                name="years_experience"
                onChange={handleChange}
                required
                className="input"
              />
            </Field>
          </>
        )}

        {/* FILE UPLOADS */}
        <Field label="Profile Photo">
          <input
            type="file"
            onChange={(e) => setProfilePhoto(e.target.files[0])}
            className="text-slate-300"
          />
        </Field>

        {role === "physician" && (
          <Field label="Credential Proof">
            <input
              type="file"
              onChange={(e) => setCredentialPhoto(e.target.files[0])}
              className="text-slate-300"
            />
          </Field>
        )}

        <button
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 py-2 rounded-lg text-white font-semibold transition disabled:opacity-50"
        >
          {loading ? "Submitting..." : "Sign Up"}
        </button>
      </form>
    </div>
  );
}

/* ------------------ */
/* Helper Components  */
/* ------------------ */

function Field({ label, children }) {
  return (
    <div className="space-y-1">
      <label className="text-sm font-semibold text-slate-300">
        {label}
      </label>
      {children}
    </div>
  );
}
