function AboutPage() {
    return (
      <main className="about-page">
        <section className="about-hero">
          <p className="eyebrow">About NextHomeAI</p>
          <h1>Real estate search through natural conversation.</h1>
          <p>
            NextHomeAI helps users search for properties by describing what they are
            looking for in plain language. Instead of manually adjusting filters, users
            can tell the assistant their budget, location, property type, bedrooms,
            bathrooms, and preferences.
          </p>
        </section>
  
        <section className="about-card">
          <h2>What the app does</h2>
          <p>
            The assistant converts user messages into structured search filters, queries
            available property listings, and displays matching results. Users can continue
            refining their search naturally, and the results update based on the latest
            criteria.
          </p>
        </section>
  
        <section className="about-grid">
          <article className="about-card">
            <h2>Natural language search</h2>
            <p>
              Users can search with messages like “Find me a 3-bedroom home in Ottawa
              under $700,000” instead of filling out a traditional form.
            </p>
          </article>
  
          <article className="about-card">
            <h2>Listing results</h2>
            <p>
              Matching listings are shown as cards with key property details, including
              price, address, bedrooms, bathrooms, location, and property type.
            </p>
          </article>
  
          <article className="about-card">
            <h2>Tour booking support</h2>
            <p>
              Users can ask to book a showing for a listing. The assistant collects the
              required booking details, confirms the property, and prepares the request.
            </p>
          </article>
        </section>
  
        <section className="about-card">
          <h2>Project goal</h2>
          <p>
            The goal of NextHomeAI is to make property search faster and more intuitive by
            combining conversational AI, listing data, and booking assistance in one flow.
          </p>
        </section>
      </main>
    );
  }
  
  export default AboutPage;