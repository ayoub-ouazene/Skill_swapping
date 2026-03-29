document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector(".signup-form");
  const errEl = document.getElementById("signup-error");

  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (errEl) {
      errEl.textContent = "";
      errEl.setAttribute("hidden", "");
    }

    const email = document.getElementById("email").value.trim();
    const first_name = document.getElementById("firstName").value.trim();
    const last_name = document.getElementById("lastName").value.trim();
    const password = document.getElementById("password").value;
    const confirm = document.getElementById("confirmPassword").value;

    if (password !== confirm) {
      if (errEl) {
        errEl.textContent = "Passwords do not match.";
        errEl.removeAttribute("hidden");
      } else {
        alert("Passwords do not match.");
      }
      return;
    }

    if (password.length < 8) {
      if (errEl) {
        errEl.textContent = "Password must be at least 8 characters.";
        errEl.removeAttribute("hidden");
      } else {
        alert("Password must be at least 8 characters.");
      }
      return;
    }

    const base = window.SKILLSWAP_API_BASE || "http://127.0.0.1:8000";

    try {
      const res = await fetch(`${base}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email,
          password,
          first_name,
          last_name,
        }),
      });

      const data = await res.json().catch(() => ({}));

      if (!res.ok) {
        const msg =
          typeof data.detail === "string"
            ? data.detail
            : Array.isArray(data.detail)
              ? data.detail.map((d) => d.msg || d).join(" ")
              : "Registration failed.";
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
        window.location.href = "login.html";
      }
    } catch (err) {
      const msg =
        "Cannot reach API. Is the backend running on port 8000?";
      if (errEl) {
        errEl.textContent = msg;
        errEl.removeAttribute("hidden");
      } else {
        alert(msg);
      }
    }
  });
});
