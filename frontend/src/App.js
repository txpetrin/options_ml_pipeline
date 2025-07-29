import React, { useState } from 'react';

function App() {
  const [stock, setStock] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async () => {
    if (!stock.trim()) {
      setError('Please enter a stock symbol');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await fetch('http://localhost:4000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ stock: stock.trim().toUpperCase() }),
      });

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError(err.message || 'An error occurred');
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSubmit();
    }
  };

  const renderDataFrame = (data, title) => {
    if (!Array.isArray(data) || data.length === 0) return null;

    const columns = Object.keys(data[0]);

    return (
      <div style={{ marginTop: '20px' }}>
        <h3>{title}</h3>
        <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
          <table style={{ borderCollapse: 'collapse', width: '100%', border: '1px solid #ddd' }}>
            <thead>
              <tr style={{ backgroundColor: '#f5f5f5' }}>
                {columns.map((col) => (
                  <th key={col} style={{ border: '1px solid #ddd', padding: '8px', textAlign: 'left' }}>
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.map((row, idx) => (
                <tr key={idx}>
                  {columns.map((col) => (
                    <td key={col} style={{ border: '1px solid #ddd', padding: '8px' }}>
                      {typeof row[col] === 'number' ? row[col].toFixed(2) : row[col]}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  return (
    <div style={{ padding: '50px', maxWidth: '1000px', margin: '0 auto' }}>
      <h2>Stock Prediction</h2>

      <div style={{ marginBottom: '20px' }}>
        <input
          type="text"
          value={stock}
          onChange={(e) => setStock(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Enter stock symbol (e.g., AAPL, GOOGL)"
          style={{
            padding: '10px',
            fontSize: '16px',
            border: '1px solid #ddd',
            borderRadius: '4px',
            marginRight: '10px',
            width: '250px',
          }}
          disabled={loading}
        />

        <button
          onClick={handleSubmit}
          disabled={loading || !stock.trim()}
          style={{
            padding: '10px 20px',
            fontSize: '16px',
            backgroundColor: loading ? '#ccc' : '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: loading ? 'not-allowed' : 'pointer',
          }}
        >
          {loading ? 'Processing...' : 'Predict'}
        </button>
      </div>

      {error && (
        <div
          style={{
            color: 'red',
            backgroundColor: '#ffe6e6',
            padding: '10px',
            borderRadius: '4px',
            marginBottom: '20px',
          }}
        >
          Error: {error}
        </div>
      )}

      {loading && (
        <div
          style={{
            color: '#666',
            fontStyle: 'italic',
            marginBottom: '20px',
          }}
        >
          Processing your request... This may take a moment.
        </div>
      )}

      {result && (
        <div>
          <h3 style={{ color: '#28a745' }}>Results for {stock.toUpperCase()}</h3>
          {renderDataFrame(result.forecast, 'Forecast')}
          {renderDataFrame(result.stock_history, 'Stock History')}
        </div>
      )}
    </div>
  );
}

export default App;
