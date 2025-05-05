import React, { useState } from 'react';

const TrainForm = () => {
  const [ticker, setTicker] = useState("AAPL");
  const [period, setPeriod] = useState("6mo");
  const [epochs, setEpochs] = useState(10);
  const [response, setResponse] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();

    const payload = { ticker, period, epochs: parseInt(epochs) };

    try {
      const res = await fetch("/train", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const data = await res.json();
      setResponse(data);
    } catch (err) {
      console.error(err);
      setResponse({ error: "Request failed." });
    }
  };

  return (
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
        maxWidth: '400px',
        margin: '0 auto'
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
  );
};

export default TrainForm;
