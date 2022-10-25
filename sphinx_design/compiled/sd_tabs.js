var sd_labels_by_text = {};

const storageKey = '&{storage_key}';
// The default value for paramKey is the string 'None'. That value indicates
// not to set a URL search parameter.
const paramKey = '&{param_key}';

function ready() {
  const tabParam = new URLSearchParams(window.location.search).get(paramKey);
  if (tabParam) {
    window.localStorage.setItem(storageKey, tabParam)
  }

  const li = document.getElementsByClassName("sd-tab-label");
  const previousChoice = window.localStorage.getItem(storageKey)

  for (const label of li) {
    syncId = label.getAttribute("data-sync-id");
    if (syncId) {
      label.onclick = onLabelClick;
      if (!sd_labels_by_text[syncId]) {
        sd_labels_by_text[syncId] = [];
      }
      sd_labels_by_text[syncId].push(label);
      if (previousChoice === syncId) {
        label.previousElementSibling.checked = true;
        updateSearchParams(syncId)
      }
    }
  }
}

function onLabelClick() {
  // Activate other inputs with the same sync id.
  syncId = this.getAttribute("data-sync-id");
  for (label of sd_labels_by_text[syncId]) {
    if (label === this) continue;
    label.previousElementSibling.checked = true;
  }
  window.localStorage.setItem(storageKey, syncId);
  updateSearchParams(syncId)
}

/**
 * @param {string} syncId
 */
function updateSearchParams(syncId) {
  if (paramKey == 'None') {
    return;
  }
  const params = new URLSearchParams(window.location.search);
  if (params.get(paramKey) === syncId) {
    return;
  }
  params.set(paramKey, syncId);
  window.history.replaceState({}, '', `${window.location.pathname}?${params}`)
}

document.addEventListener("DOMContentLoaded", ready, false);
