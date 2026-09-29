/* Shared helpers */
function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function showEl(el) { el.classList.remove("hidden"); }
function hideEl(el) { el.classList.add("hidden"); }

function showLoading(container) {
  showEl(container);
  container.innerHTML = '<div class="loading"><span class="spinner"></span> Thinking...</div>';
}

function showError(container, message) {
  showEl(container);
  container.innerHTML = `<div class="error-msg">${escapeHtml(message)}</div>`;
}

function renderList(title, items) {
  if (!items || !items.length) return "";
  const lis = items.map(i => `<li>${escapeHtml(String(i))}</li>`).join("");
  return `<h4>${escapeHtml(title)}</h4><ul>${lis}</ul>`;
}

async function apiPost(endpoint, body) {
  const res = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return res.json();
}

function initFeatureForm(formId, endpoint, renderFn, bodyFn) {
  const form = document.getElementById(formId);
  const resultEl = document.getElementById("result");
  if (!form || !resultEl) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const btn = form.querySelector("button[type=submit]");
    const fd = new FormData(form);

    showLoading(resultEl);
    btn.disabled = true;

    try {
      const json = await apiPost(endpoint, bodyFn(fd));
      if (!json.success) {
        showError(resultEl, json.error || "Something went wrong.");
        return;
      }
      showEl(resultEl);
      renderFn(json.data, resultEl);
    } catch {
      showError(resultEl, "Network error. Is the server running?");
    } finally {
      btn.disabled = false;
    }
  });
}

/* Sidebar toggle for mobile */
document.getElementById("menu-toggle")?.addEventListener("click", () => {
  document.getElementById("sidebar")?.classList.toggle("open");
  document.getElementById("sidebar-overlay")?.classList.toggle("show");
});

document.getElementById("sidebar-overlay")?.addEventListener("click", () => {
  document.getElementById("sidebar")?.classList.remove("open");
  document.getElementById("sidebar-overlay")?.classList.remove("show");
});
