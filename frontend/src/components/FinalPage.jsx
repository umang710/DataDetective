import React, { useState } from "react";

function FinalPage() {
  const team = sessionStorage.getItem("team");
  const [a1, setA1] = useState("");
  const [a2, setA2] = useState("");
  const [attempts, setAttempts] = useState(0);
  const [message, setMessage] = useState("");

  const correct1 = "protecting personal data";
  const correct2 = "protecting computer systems";

  const handleSubmit = async (e) => {
    e.preventDefault();
    setAttempts((prev) => prev + 1);

    const now = new Date();
    const offsetIST = 5.5 * 60 * 60 * 1000;
    const istTime = new Date(now.getTime() + offsetIST).toISOString();

    if (
      a1.trim().toLowerCase() === correct1 &&
      a2.trim().toLowerCase() === correct2
    ) {
      await fetch(`${import.meta.env.VITE_API_BASE}/submit-final`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          team,
          answer1: a1,
          answer2: a2,
          attempts: attempts + 1, // ✅ send total attempts for both final answers
          timestamp: istTime,
        }),
      });

      setMessage(
        "✅ Congratulations! You’ve completed all levels. Please inform the event coordinator."
      );
    } else {
      setMessage("❌ One or both answers are incorrect. Try again.");
    }
  };

  return (
    <div className="final-page" style={{ textAlign: "center", marginTop: "50px" }}>
      <h2>Final Challenge</h2>
      <form onSubmit={handleSubmit}>
        <label>
          1. What does data privacy focus on?
          <input
            type="text"
            value={a1}
            onChange={(e) => setA1(e.target.value)}
            style={{ display: "block", margin: "10px auto", width: "300px" }}
          />
        </label>
        <label>
          2. What is cybersecurity about?
          <input
            type="text"
            value={a2}
            onChange={(e) => setA2(e.target.value)}
            style={{ display: "block", margin: "10px auto", width: "300px" }}
          />
        </label>
        <button type="submit" style={{ padding: "8px 16px" }}>
          Submit Final Answers
        </button>
      </form>
      <p style={{ marginTop: "20px", fontWeight: "bold" }}>{message}</p>
    </div>
  );
}

export default FinalPage;
