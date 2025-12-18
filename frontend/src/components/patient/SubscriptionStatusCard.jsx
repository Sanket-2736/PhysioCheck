import React, { useEffect, useState } from "react";
import api from "../../api/axios";

export default function SubscriptionStatusCard({ patient }) {
  const [status, setStatus] = useState("NONE");
  const [physician, setPhysician] = useState(null);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        // 1️⃣ If already assigned
        if (patient.physician_id) {
          const res = await api.get("/physicians");
          const doc = res.data.physicians.find(
            (p) => p.physician_id === patient.physician_id
          );
          setPhysician(doc);
          setStatus("APPROVED");
          return;
        }

        // 2️⃣ Else check pending requests
        const res = await api.get("/subscription/patient/requests");
        if (res.data.requests.length > 0) {
          setStatus("PENDING");
        }
      } catch (err) {
        console.error(err);
      }
    };

    fetchStatus();
  }, [patient]);

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h2 className="text-lg font-semibold mb-4">
        Subscription Status
      </h2>

      {status === "NONE" && (
        <p className="text-gray-600">
          You are not subscribed to any physician.
        </p>
      )}

      {status === "PENDING" && (
        <p className="text-yellow-600 font-medium">
          ⏳ Subscription request pending approval
        </p>
      )}

      {status === "APPROVED" && physician && (
        <div className="flex items-center gap-4">
          <img
            src={physician.profile_photo || "/default-avatar.png"}
            className="w-14 h-14 rounded-full"
            alt="physician"
          />
          <div>
            <p className="font-semibold">{physician.full_name}</p>
            <p className="text-sm text-gray-500">
              {physician.specialization}
            </p>
            <p className="text-green-600 text-sm mt-1">
              ✅ Subscription approved
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
