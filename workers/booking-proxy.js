/**
 * Cloudflare Worker: proxies booking POSTs from the static listing site to Airtable.
 * Secrets: wrangler secret put AIRTABLE_TOKEN
 * Vars: AIRTABLE_BASE_ID, AIRTABLE_TABLE_ID (see wrangler.toml)
 */

const SHOWING_TIME_PLACEHOLDER = "Coordinate time with listing agent";

function corsHeaders(request) {
  const origin = request.headers.get("Origin") || "*";
  return {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "86400",
  };
}

export default {
  async fetch(request, env) {
    const headersBase = corsHeaders(request);

    if (request.method === "OPTIONS") {
      return new Response(null, { headers: headersBase });
    }

    if (request.method !== "POST") {
      return new Response(JSON.stringify({ error: "Method not allowed" }), {
        status: 405,
        headers: { ...headersBase, "Content-Type": "application/json" },
      });
    }

    let body;
    try {
      body = await request.json();
    } catch {
      return new Response(JSON.stringify({ error: "Invalid JSON" }), {
        status: 400,
        headers: { ...headersBase, "Content-Type": "application/json" },
      });
    }

    const name = String(body.name || "").trim();
    const email = String(body.email || "").trim();
    const phone = String(body.phone || "").trim();
    const showingDate = String(body.showingDate || "").trim();
    const moveInPreference = String(body.moveInPreference || "").trim();
    const showingTimeRaw = String(body.showingTime || "").trim();
    const showingTime = showingTimeRaw || SHOWING_TIME_PLACEHOLDER;

    if (!name || !showingDate || !moveInPreference) {
      return new Response(JSON.stringify({ error: "Missing required fields" }), {
        status: 400,
        headers: { ...headersBase, "Content-Type": "application/json" },
      });
    }

    function isValidEmail(s) {
      const t = String(s || "").trim();
      if (!t) {
        return false;
      }
      return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(t);
    }

    function isValidPhone(s) {
      return String(s || "").replace(/\D/g, "").length >= 10;
    }

    let contactErr = null;
    if (!isValidEmail(email)) {
      contactErr = "A valid email is required.";
    } else if (!isValidPhone(phone)) {
      contactErr = "A valid phone number (at least 10 digits) is required.";
    }

    if (contactErr) {
      return new Response(JSON.stringify({ error: contactErr }), {
        status: 400,
        headers: { ...headersBase, "Content-Type": "application/json" },
      });
    }

    const token = env.AIRTABLE_TOKEN;
    const baseId = env.AIRTABLE_BASE_ID;
    const tableId = env.AIRTABLE_TABLE_ID;

    if (!token || !baseId || !tableId) {
      return new Response(JSON.stringify({ error: "Server misconfigured" }), {
        status: 500,
        headers: { ...headersBase, "Content-Type": "application/json" },
      });
    }

    const url = `https://api.airtable.com/v0/${baseId}/${encodeURIComponent(tableId)}`;

    const airtableResponse = await fetch(url, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        records: [
          {
            fields: {
              Name: name,
              Email: email,
              Phone: phone,
              "Showing Date": showingDate,
              "Showing Time": showingTime,
              "Move-In Date Preference": moveInPreference,
              Status: "New",
            },
          },
        ],
      }),
    });

    const text = await airtableResponse.text();

    return new Response(text, {
      status: airtableResponse.status,
      headers: { ...headersBase, "Content-Type": "application/json" },
    });
  },
};
