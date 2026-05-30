(function () {
  var storageKey = "site-theme";
  var root = document.documentElement;
  var toggle;

  function systemPrefersDark() {
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  }

  function getSavedTheme() {
    try {
      return localStorage.getItem(storageKey);
    } catch (error) {
      return null;
    }
  }

  function saveTheme(theme) {
    try {
      localStorage.setItem(storageKey, theme);
    } catch (error) {
      return;
    }
  }

  function setTheme(theme) {
    root.setAttribute("data-theme", theme);

    if (!toggle) {
      return;
    }

    var isDark = theme === "dark";
    var icon = toggle.querySelector(".theme-toggle__icon");
    var text = toggle.querySelector(".theme-toggle__text");

    toggle.setAttribute("aria-pressed", String(isDark));
    toggle.setAttribute("aria-label", isDark ? "Switch to light mode" : "Switch to dark mode");

    if (icon) {
      icon.textContent = isDark ? "☀" : "☾";
    }

    if (text) {
      text.textContent = isDark ? "Light" : "Dark";
    }
  }

  function initialTheme() {
    var savedTheme = getSavedTheme();

    if (savedTheme === "light" || savedTheme === "dark") {
      return savedTheme;
    }

    return systemPrefersDark() ? "dark" : "light";
  }

  setTheme(initialTheme());

  document.addEventListener("DOMContentLoaded", function () {
    toggle = document.querySelector(".theme-toggle");
    setTheme(root.getAttribute("data-theme") || initialTheme());

    if (!toggle) {
      return;
    }

    toggle.addEventListener("click", function () {
      var nextTheme = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
      setTheme(nextTheme);
      saveTheme(nextTheme);
    });
  });
})();
