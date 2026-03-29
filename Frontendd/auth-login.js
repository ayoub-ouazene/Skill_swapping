document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector(".login-form");
  const errEl = document.getElementById("login-error");
  const back = document.querySelector(".back-arrow");

  if (back) {
    back.style.cursor = "pointer";
    back.addEventListener("click", () => {
      window.location.href = "index.html";
    });
  }

  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (errEl) {
      errEl.textContent = "";
      errEl.setAttribute("hidden", "");
    }

    const email = document.getElementById("login-email").value.trim();
    const password = document.getElementById("login-password").value;

    const base = window.SKILLSWAP_API_BASE || "http://127.0.0.1:8000";

    try {
      const res = await fetch(`${base}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json().catch(() => ({}));

      if (!res.ok) {
        const msg =
          typeof data.detail === "string"
            ? data.detail
            : Array.isArray(data.detail)
              ? data.detail.map((d) => d.msg || d).join(" ")
              : "Login failed. Check email and password.";
        if (errEl) {
          errEl.textContent = msg;
          errEl.removeAttribute("hidden");
        } else {
          alert(msg);
        }
        return;
      }

      if (data.access_token) {
        localStorage.setItem(
          window.SKILLSWAP_TOKEN_KEY || "skillswap_access_token",
          data.access_token
        );
        window.location.href = "home.html";
      } else {
        alert("Unexpected response from server.");
      }
    } catch (err) {
      const msg =
        "Cannot reach API. Is the backend running (uvicorn on port 8000) and CORS enabled?";
      if (errEl) {
        errEl.textContent = msg;
        errEl.removeAttribute("hidden");
      } else {
        alert(msg);
      }
    }
  });
});
