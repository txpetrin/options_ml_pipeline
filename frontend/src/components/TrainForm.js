import React, { useState } from 'react';

const TrainForm = () => {
  const [ticker, setTicker] = useState("AAPL");
  const [period, setPeriod] = useState("6mo");
  const [epochs, setEpochs] = useState(10);
  const [response, setResponse] = useState(null);
  const [progress, setProgress] = useState(0); // State for progress bar

  const handleSubmit = async (e) => {
    e.preventDefault();

    const payload = { ticker, period, epochs: parseInt(epochs) };

    try {
      setProgress(10); // Start progress
      const res = await fetch("/train", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      setProgress(50); // Midway progress

      const data = await res.json();
      setResponse(data);
      setProgress(100); // Complete progress
    } catch (err) {
      console.error(err);
      setResponse({ error: "Request failed." });
      setProgress(0); // Reset progress on error
    }
  };

  return (
    <div 
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'flex-start',
        gap: '2rem',
        padding: '2rem',
        maxWidth: '900px',
        margin: '0 auto'
      }}
    >
      {/* Form Section */}
      <form 
        onSubmit={handleSubmit} 
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '1rem',
          padding: '2rem',
          backgroundColor: '#f5f5f5',
          borderRadius: '8px',
          boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
          maxWidth: '600px',
          flex: '1'
        }}
      >
        <label style={{ display: 'flex', flexDirection: 'column', fontSize: '1rem', color: '#333' }}>
          Ticker:
          <input 
            value={ticker} 
            onChange={(e) => setTicker(e.target.value)} 
            style={{
              padding: '0.5rem',
              border: '1px solid #ccc',
              borderRadius: '4px',
              marginTop: '0.5rem'
            }}
          />
        </label>
        <label style={{ display: 'flex', flexDirection: 'column', fontSize: '1rem', color: '#333' }}>
          Period:
          <select 
            value={period} 
            onChange={(e) => setPeriod(e.target.value)} 
            style={{
              padding: '0.5rem',
              border: '1px solid #ccc',
              borderRadius: '4px',
              marginTop: '0.5rem'
            }}
          >
            <option>1mo</option>
            <option>3mo</option>
            <option>6mo</option>
            <option>1y</option>
            <option>2y</option>
            <option>5y</option>
          </select>
        </label>
        <label style={{ display: 'flex', flexDirection: 'column', fontSize: '1rem', color: '#333' }}>
          Epochs:
          <input 
            type="number" 
            value={epochs} 
            onChange={(e) => setEpochs(e.target.value)} 
            style={{
              padding: '0.5rem',
              border: '1px solid #ccc',
              borderRadius: '4px',
              marginTop: '0.5rem'
            }}
          />
        </label>
        <button 
          type="submit" 
          style={{
            padding: '0.75rem',
            backgroundColor: '#4CAF50',
            color: '#fff',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '1rem'
          }}
        >
          Start Training
        </button>

        {/* Progress Bar */}
        {progress > 0 && (
          <div 
            style={{
              marginTop: '1rem',
              width: '100%',
              height: '10px',
              backgroundColor: '#e0e0e0',
              borderRadius: '5px',
              overflow: 'hidden'
            }}
          >
            <div 
              style={{
                width: `${progress}%`,
                height: '100%',
                backgroundColor: '#4CAF50',
                transition: 'width 0.3s ease'
              }}
            ></div>
          </div>
        )}

        {response && (
          <div 
            style={{
              marginTop: '1rem',
              padding: '1rem',
              backgroundColor: '#e8f5e9',
              borderRadius: '8px',
              boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)'
            }}
          >
            <h3 style={{ color: '#4CAF50' }}>Response:</h3>
            <pre style={{ fontSize: '0.9rem', color: '#333' }}>
              {JSON.stringify(response, null, 2)}
            </pre>
          </div>
        )}
      </form>

      {/* Tips Section */}
      <aside 
        style={{
          flex: '1',
          padding: '1rem',
          backgroundColor: '#f0f4f8',
          borderRadius: '8px',
          boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
          fontSize: '0.9rem',
          color: '#555'
        }}
      >
        <h4 style={{ color: '#4CAF50', marginBottom: '0.5rem' }}>Tips for Using the Form:</h4>
        <ul style={{ paddingLeft: '1.5rem' }}>
          <li>Enter a valid stock ticker symbol (e.g., AAPL for Apple).</li>
          <li>Select a period to define the historical data range.</li>
          <li>Choose the number of epochs for training (higher values may take longer).</li>
        </ul>
      </aside>
    </div>
  );
};

export default TrainForm;
