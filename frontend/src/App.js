import React, { useState } from 'react';

function App() {
  const [number, setNumber] = useState('');
  const [result, setResult] = useState(null);
  const [irisData, setIrisData] = useState(null);
  const [irisDf, setIrisDf] = useState(null); 

  const handleSubmit = async () => {
    const res = await fetch('http://localhost:4000/square', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ number: parseInt(number) }),
    });

    const data = await res.json();

    console.log('Received predictions:', data.predictions);
    console.log('Type of predictions:', typeof data.predictions);
    console.log('Received DataFrame:', data.dataframe);
    console.log('Type of dataframe:', typeof data.dataframe);

    setResult(data.squared);
    setIrisData(data.predictions);
    setIrisDf(data.dataframe);
  };

  const renderTable = () => {
    if (!irisDf || !Array.isArray(irisDf) || irisDf.length === 0) return null;

    const columns = Object.keys(irisDf[0]);

    return (
      <table border="1" cellPadding="5" style={{ marginTop: '20px', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col}>{col}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {irisDf.map((row, idx) => (
            <tr key={idx}>
              {columns.map((col) => (
                <td key={col}>{row[col]}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    );
  };

  return (
    <div style={{ padding: '50px' }}>
      <h2>Square a Number</h2>
      <input
        type="number"
        value={number}
        onChange={(e) => setNumber(e.target.value)}
        placeholder="Enter a number"
      />
      <button onClick={handleSubmit}>Square</button>

      {result !== null && (
        <div>
          <p>Result: {result}</p>
        </div>
      )}

      {irisData && Array.isArray(irisData) && (
        <div>
          <h3>Iris Predictions</h3>
          <ul>
            {irisData.map((val, idx) => (
              <li key={idx}>Sample {idx + 1}: Class {val}</li>
            ))}
          </ul>
        </div>
      )}

      {renderTable()}
    </div>
  );
}

export default App;
