import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../api/axios";

export default function PhysicianList() {
  const [physicians, setPhysicians] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchPhysicians = async () => {
      try {
        const res = await api.get("/physicians");
        setPhysicians(res.data.physicians);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchPhysicians();
  }, []);

  if (loading) return <div>Loading physicians...</div>;

  return (
    <div className="max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Available Physicians</h1>

      <div className="grid md:grid-cols-2 gap-6">
        {physicians.map((p) => (
          <div
            key={p.physician_id}
            className="bg-white rounded-lg shadow p-5 cursor-pointer hover:shadow-lg"
            onClick={() => navigate(`/patient/physicians/${p.physician_id}`)}
          >
            <div className="flex items-center gap-4">
              <img
                src={p.profile_photo || "/default-avatar.png"}
                alt="physician"
                className="w-16 h-16 rounded-full object-cover"
              />
              <div>
                <h2 className="font-semibold text-lg">{p.full_name}</h2>
                <p className="text-sm text-gray-500">
                  {p.specialization || "Physician"}
                </p>
              </div>
            </div>

            <p className="text-sm text-gray-600 mt-3">
              Experience: {p.years_experience || 0} years
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
