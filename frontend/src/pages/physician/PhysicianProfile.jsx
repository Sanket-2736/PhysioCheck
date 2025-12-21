import React, { useEffect, useState } from "react";
import api from "../../api/axios";

export default function PhysicianProfile() {
  const [physician, setPhysician] = useState(null);
  const [form, setForm] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [editMode, setEditMode] = useState(false);

  /* ================= FETCH PROFILE ================= */
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await api.get("/physician/me");
        setPhysician(res.data.physician);
        setForm(res.data.physician);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);

  /* ================= HANDLERS ================= */
  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  /* ---------- SAVE TEXT FIELDS ---------- */
const handleSave = async () => {
  try {
    setSaving(true);

    const payload = {};

    if (form.full_name?.trim())
      payload.full_name = form.full_name;

    if (form.phone?.trim())
      payload.phone = form.phone;

    if (form.specialization?.trim())
      payload.specialization = form.specialization;

    if (form.license_id?.trim())
      payload.license_id = form.license_id;

    if (
      form.years_experience !== "" &&
      form.years_experience !== undefined &&
      !isNaN(form.years_experience)
    ) {
      payload.years_experience = Number(form.years_experience);
    }

    await api.put("/physician/me", payload);

    setPhysician({ ...physician, ...payload });
    setEditMode(false);
  } catch (err) {
    console.error("UPDATE ERROR:", err.response?.data || err);
    alert("Failed to update profile");
  } finally {
    setSaving(false);
  }
};



  /* ---------- PROFILE PHOTO UPLOAD ---------- */
  const handleProfilePhotoUpload = async (file) => {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await api.put(
        "/physician/me/profile-photo",
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );

      setForm((f) => ({ ...f, profile_photo: res.data.profile_photo }));
      setPhysician((p) => ({ ...p, profile_photo: res.data.profile_photo }));
    } catch (err) {
      console.error(err);
      alert("Failed to upload profile photo");
    }
  };

  /* ---------- CREDENTIAL UPLOAD ---------- */
  const handleCredentialUpload = async (file) => {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await api.put(
        "/physician/me/credential-photo",
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );

      setForm((f) => ({ ...f, credential_photo: res.data.credential_photo }));
      setPhysician((p) => ({ ...p, credential_photo: res.data.credential_photo }));
    } catch (err) {
      console.error(err);
      alert("Failed to upload credential");
    }
  };

  /* ================= STATES ================= */
  if (loading) {
    return <div className="text-slate-300">Loading profile...</div>;
  }

  if (!physician) {
    return <div className="text-red-400">Profile not found</div>;
  }

  return (
    <div className="max-w-4xl mx-auto text-white">
      <div className="bg-slate-800 rounded-lg p-6 space-y-6">

        {/* ================= HEADER ================= */}
        <div className="flex items-center gap-5">
          <img
            src={form.profile_photo || "/default-avatar.png"}
            alt="physician"
            className="w-24 h-24 rounded-full object-cover"
          />

          <div className="flex-1">
            {editMode ? (
              <>
                <input
                  name="full_name"
                  value={form.full_name || ""}
                  onChange={handleChange}
                  className="w-full mb-2 px-3 py-2 rounded bg-slate-700"
                  placeholder="Full Name"
                />
                <input
                  name="phone"
                  value={form.phone || ""}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded bg-slate-700"
                  placeholder="Phone"
                />
              </>
            ) : (
              <>
                <h1 className="text-2xl font-bold">{physician.full_name}</h1>
                <p className="text-slate-400">{physician.email}</p>
                <p className="text-slate-400 text-sm">
                  {physician.phone || "—"}
                </p>
              </>
            )}

            {physician.is_verified && (
              <span className="inline-block mt-2 text-xs px-2 py-1 bg-green-600 rounded">
                Verified Physician
              </span>
            )}
          </div>

          {!editMode ? (
            <button
              onClick={() => setEditMode(true)}
              className="px-4 py-2 bg-blue-600 rounded"
            >
              Edit
            </button>
          ) : (
            <div className="flex gap-2">
              <button
                onClick={handleSave}
                disabled={saving}
                className="px-4 py-2 bg-green-600 rounded"
              >
                {saving ? "Saving..." : "Save"}
              </button>
              <button
                onClick={() => {
                  setForm(physician);
                  setEditMode(false);
                }}
                className="px-4 py-2 bg-slate-600 rounded"
              >
                Cancel
              </button>
            </div>
          )}
        </div>

        {/* ================= PHOTO UPLOADS ================= */}
        {editMode && (
          <div className="grid sm:grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-slate-400 mb-1">Profile Photo</p>
              <input
                type="file"
                accept="image/*"
                onChange={(e) => handleProfilePhotoUpload(e.target.files[0])}
              />
            </div>

            <div>
              <p className="text-sm text-slate-400 mb-1">Credential</p>
              <input
                type="file"
                accept="image/*,.pdf"
                onChange={(e) => handleCredentialUpload(e.target.files[0])}
              />
            </div>
          </div>
        )}

        {/* ================= DETAILS ================= */}
        <div className="grid sm:grid-cols-2 gap-4">
          <EditableField
            label="Specialization"
            name="specialization"
            value={form.specialization}
            editMode={editMode}
            onChange={handleChange}
          />
          <EditableField
            label="Years of Experience"
            name="years_experience"
            value={form.years_experience}
            editMode={editMode}
            onChange={handleChange}
            type="number"
          />
          <EditableField
            label="License ID"
            name="license_id"
            value={form.license_id}
            editMode={editMode}
            onChange={handleChange}
          />
        </div>

        {/* ================= CREDENTIAL VIEW ================= */}
        {!editMode && (
          <div>
            <p className="text-sm text-slate-400 mb-2">Credential</p>
            {physician.credential_photo ? (
              physician.credential_photo.match(/\.(jpg|jpeg|png|webp)$/i) ? (
                <img
                  src={physician.credential_photo}
                  alt="credential"
                  className="max-w-xs rounded-lg border border-slate-700"
                />
              ) : (
                <a
                  href={physician.credential_photo}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-400 underline"
                >
                  View Credential Document
                </a>
              )
            ) : (
              <p className="text-slate-500 text-sm">
                No credential uploaded
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

/* ================= REUSABLE FIELD ================= */
function EditableField({
  label,
  name,
  value,
  editMode,
  onChange,
  type = "text",
}) {
  return (
    <div>
      <p className="text-sm text-slate-400">{label}</p>
      {editMode ? (
        <input
          type={type}
          name={name}
          value={value || ""}
          onChange={onChange}
          className="w-full px-3 py-2 rounded bg-slate-700"
        />
      ) : (
        <p className="font-medium">{value || "—"}</p>
      )}
    </div>
  );
}
