document.addEventListener("DOMContentLoaded", () => {
    const storageKey = "gharsetu-theme";
    const root = document.documentElement;
    const toggleButton = document.getElementById("theme-toggle");
    const toggleIcon = document.getElementById("theme-toggle-icon");
    const toggleLabel = document.getElementById("theme-toggle-label");

    if (!toggleButton || !toggleIcon || !toggleLabel) {
        console.warn("Theme toggle elements not found in DOM");
        return;
    }

    // Get current theme from DOM attribute
    function currentTheme() {
        const theme = root.getAttribute("data-bs-theme");
        return theme === "dark" ? "dark" : "light";
    }

    // Apply theme to UI and DOM
    function applyTheme(theme) {
        const nextTheme = theme === "dark" ? "dark" : "light";
        const isDark = nextTheme === "dark";

        root.setAttribute("data-bs-theme", nextTheme);
        
        // Update button state
        toggleButton.setAttribute("aria-pressed", String(isDark));
        toggleButton.setAttribute(
            "aria-label",
            isDark ? "Switch to light mode" : "Switch to dark mode"
        );
        
        // Update icon
        toggleIcon.className = isDark ? "fas fa-sun" : "fas fa-moon";
        
        // Update label
        toggleLabel.textContent = isDark ? "Light" : "Dark";
        
        console.log("Theme applied:", nextTheme);
    }

    // Initialize theme on page load
    applyTheme(currentTheme());

    // Add click listener to toggle button
    toggleButton.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        
        const nextTheme = currentTheme() === "dark" ? "light" : "dark";
        applyTheme(nextTheme);

        // Save theme preference to localStorage
        try {
            localStorage.setItem(storageKey, nextTheme);
            console.log("Theme saved to localStorage:", nextTheme);
        } catch (error) {
            console.warn("Could not save theme to localStorage:", error);
        }
    });
});

