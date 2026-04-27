function SettingsPage() {
    return (
      <main className="settings-page">
        <div className="settings-card">
          <p className="eyebrow">Preferences</p>
          <h1>Settings</h1>
  
          <div className="setting-row">
            <div>
              <h3>EXAMPLE</h3>
              <p>example text</p>
            </div>
            <select defaultValue="CAD">
              <option value="CAD">CAD</option>
              <option value="USD">USD</option>
            </select>
          </div>
        </div>
      </main>
    );
  }
  
  export default SettingsPage;