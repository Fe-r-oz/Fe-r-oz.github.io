(function () {
  var storageKey = "site-theme";
  var root = document.documentElement;
  var toggles = [];

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

    if (!toggles.length) {
      return;
    }

    var isDark = theme === "dark";
    toggles.forEach(function (toggle) {
      var text = toggle.querySelector(".theme-toggle__text");

      toggle.setAttribute("aria-pressed", String(isDark));
      toggle.setAttribute("aria-label", isDark ? "Switch to light mode" : "Switch to dark mode");

      if (text) {
        text.textContent = isDark ? "Light mode" : "Dark mode";
      }
    });
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
    toggles = Array.prototype.slice.call(document.querySelectorAll(".theme-toggle"));
    setTheme(root.getAttribute("data-theme") || initialTheme());

    toggles.forEach(function (toggle) {
      toggle.addEventListener("click", function () {
        var nextTheme = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
        setTheme(nextTheme);
        saveTheme(nextTheme);
      });
    });
  });
})();
