import { useEffect, useState } from "react";

const DEFAULT_SETTINGS = {
  fontSize: "normal",
  fontStyle: "default",
  reducedMotion: false,
  highContrast: false,
};

function loadAccessibilitySettings() {
  try {
    const saved = localStorage.getItem("accessibilitySettings");
    return saved ? { ...DEFAULT_SETTINGS, ...JSON.parse(saved) } : DEFAULT_SETTINGS;
  } catch {
    return DEFAULT_SETTINGS;
  }
}

function applyAccessibilitySettings(settings) {
  const root = document.documentElement;

  root.setAttribute("data-font-size", settings.fontSize);
  root.setAttribute("data-font-style", settings.fontStyle);
  root.setAttribute("data-reduced-motion", settings.reducedMotion ? "true" : "false");
  root.setAttribute("data-high-contrast", settings.highContrast ? "true" : "false");

  localStorage.setItem("accessibilitySettings", JSON.stringify(settings));
}

function SettingsPage() {
  const [settings, setSettings] = useState(loadAccessibilitySettings);

  useEffect(() => {
    applyAccessibilitySettings(settings);
  }, [settings]);

  function updateSetting(name, value) {
    setSettings((currentSettings) => ({
      ...currentSettings,
      [name]: value,
    }));
  }

  function resetSettings() {
    setSettings(DEFAULT_SETTINGS);
  }

  return (
    <main className="settings-page">
      <div className="settings-card">
        <p className="eyebrow">Accessibility</p>
        <h1>Accessibility settings</h1>

        <div className="setting-row">
          <div>
            <h3>Font size</h3>
            <p>Increase text size across the app.</p>
          </div>

          <select
            value={settings.fontSize}
            onChange={(event) => updateSetting("fontSize", event.target.value)}
          >
            <option value="normal">Normal</option>
            <option value="large">Large</option>
            <option value="extra-large">Extra large</option>
          </select>
        </div>

        <div className="setting-row">
          <div>
            <h3>Font style</h3>
            <p>Use a simpler, more readable font style.</p>
          </div>

          <select
            value={settings.fontStyle}
            onChange={(event) => updateSetting("fontStyle", event.target.value)}
          >
            <option value="default">Default</option>
            <option value="readable">Readable</option>
            <option value="dyslexia-friendly">Dyslexia-friendly</option>
          </select>
        </div>

        <div className="setting-row">
          <div>
            <h3>High contrast</h3>
            <p>Increase contrast between text, backgrounds, and borders.</p>
          </div>

          <label className="switch-row">
            <input
              type="checkbox"
              checked={settings.highContrast}
              onChange={(event) => updateSetting("highContrast", event.target.checked)}
            />
            <span>{settings.highContrast ? "On" : "Off"}</span>
          </label>
        </div>

        <div className="setting-row">
          <div>
            <h3>Reduced motion</h3>
            <p>Reduce animations and movement effects.</p>
          </div>

          <label className="switch-row">
            <input
              type="checkbox"
              checked={settings.reducedMotion}
              onChange={(event) => updateSetting("reducedMotion", event.target.checked)}
            />
            <span>{settings.reducedMotion ? "On" : "Off"}</span>
          </label>
        </div>

        <button type="button" className="reset-accessibility-button" onClick={resetSettings}>
          Reset accessibility settings
        </button>
      </div>
    </main>
  );
}

export default SettingsPage;