// =============================
// 🔐 CONFIG (DARWIN SAFE)
// =============================

// 👉 Empty = same origin
// Works in:
// - localhost
// - Darwin proxy (/user/.../proxy/5004)
// - future deployments
const BASE_URL = "";

// =============================
// 🔍 PREVIEW API
// =============================
export async function previewQuestion(payload) {
  try {
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