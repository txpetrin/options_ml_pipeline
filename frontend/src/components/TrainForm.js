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
    <form onSubmit={handleSubmit}>
      <label>
        Ticker:
        <input value={ticker} onChange={(e) => setTicker(e.target.value)} />
      </label>
      <br />
      <label>
        Period:
        <select value={period} onChange={(e) => setPeriod(e.target.value)}>
          <option>1mo</option>
          <option>3mo</option>
          <option>6mo</option>
          <option>1y</option>
          <option>2y</option>
          <option>5y</option>
        </select>
      </label>
      <br />
      <label>
        Epochs:
        <input type="number" value={epochs} onChange={(e) => setEpochs(e.target.value)} />
      </label>
      <br />
      <button type="submit">Start Training</button>

      {response && (
        <div style={{ marginTop: "1rem" }}>
          <h3>Response:</h3>
          <pre>{JSON.stringify(response, null, 2)}</pre>
        </div>
      )}
    </form>
  );
};

export default TrainForm;
