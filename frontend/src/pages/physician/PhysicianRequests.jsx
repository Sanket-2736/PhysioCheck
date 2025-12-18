import React, { useEffect, useState } from "react";
import api from "../../api/axios";

export default function PhysicianRequests() {
  const [requests, setRequests] = useState([]);

  const fetchRequests = async () => {
    const res = await api.get("/subscription/physician/requests");
    setRequests(res.data.requests);
  };

  useEffect(() => {
    fetchRequests();
  }, []);

  const handleAction = async (id, action) => {
    await api.post(`/subscription/physician/requests/${id}/${action}`);
    fetchRequests(); // refresh
  };

  return (
    <div>
      <h1 className="text-xl font-bold mb-4">
        Subscription Requests
      </h1>

      {requests.length === 0 && (
        <p className="text-gray-400">No pending requests</p>
      )}

      <div className="space-y-4">
        {requests.map((r) => (
          <div
            key={r.request_id}
            className="bg-white text-black p-4 rounded flex justify-between items-center"
          >
            <span>Patient ID: {r.patient_id}</span>

            <div className="flex gap-2">
              <button
                onClick={() => handleAction(r.request_id, "accept")}
                className="px-4 py-2 bg-green-600 text-white rounded"
              >
                Accept
              </button>
              <button
                onClick={() => handleAction(r.request_id, "reject")}
                className="px-4 py-2 bg-red-600 text-white rounded"
              >
                Reject
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
