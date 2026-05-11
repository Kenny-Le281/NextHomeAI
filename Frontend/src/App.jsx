import { useEffect } from "react";
import { Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import HomePage from "./pages/HomePage";
import ListingDetailsPage from "./pages/ListingDetailsPage";
import SettingsPage from "./pages/SettingsPage";
import AboutPage from "./pages/AboutPage";

const DEFAULT_ACCESSIBILITY_SETTINGS = {
  fontSize: "normal",
  fontStyle: "default",
  reducedMotion: false,
  highContrast: false,
};

function applySavedAccessibilitySettings() {
  try {
    const saved = localStorage.getItem("accessibilitySettings");
    const settings = saved
      ? { ...DEFAULT_ACCESSIBILITY_SETTINGS, ...JSON.parse(saved) }
      : DEFAULT_ACCESSIBILITY_SETTINGS;

    const root = document.documentElement;

    root.setAttribute("data-font-size", settings.fontSize);
    root.setAttribute("data-font-style", settings.fontStyle);
    root.setAttribute("data-reduced-motion", settings.reducedMotion ? "true" : "false");
    root.setAttribute("data-high-contrast", settings.highContrast ? "true" : "false");
  } catch {
    const root = document.documentElement;

    root.setAttribute("data-font-size", "normal");
    root.setAttribute("data-font-style", "default");
    root.setAttribute("data-reduced-motion", "false");
    root.setAttribute("data-high-contrast", "false");
  }
}

function App() {
  useEffect(() => {
    applySavedAccessibilitySettings();
  }, []);

  return (
    <div className="app-shell">
      <Navbar />

      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/listing/:listingId" element={<ListingDetailsPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/about" element={<AboutPage />} />
      </Routes>
    </div>
  );
}

export default App;