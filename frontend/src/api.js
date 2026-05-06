// =============================
// 🔐 CONFIG
// =============================

// DEV → localhost
// DARWIN → same origin (no CORS)
const BASE_URL = import.meta.env.DEV
  ? "http://localhost:5004"
  : window.location.origin + window.location.pathname.replace(/\/$/, "");


// =============================
// 🔍 PREVIEW API
// =============================
export async function previewQuestion(payload) {
  try {
    if (import.meta.env.DEV) {
      console.log("🔍 PREVIEW PAYLOAD:", payload);
    }

    const res = await fetch(`${BASE_URL}/preview`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        text:
          typeof payload === "string"
            ? payload
            : JSON.stringify(payload, null, 2),
      }),
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data?.error || "Preview API failed");
    }

    return data;

  } catch (err) {
    console.error("❌ Preview request failed:", err);
    return { questions: [] };
  }
}


// =============================
// ⚙️ GENERATE XML API
// =============================
export async function generateXML(payload) {
  try {
    if (import.meta.env.DEV) {
      console.log("🚀 GENERATE PAYLOAD:", payload);
    }

    const res = await fetch(`${BASE_URL}/generate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data?.error || "Generate API failed");
    }

    return data;

  } catch (err) {
    console.error("❌ Generate request failed:", err);
    return { xml: "" };
  }
}