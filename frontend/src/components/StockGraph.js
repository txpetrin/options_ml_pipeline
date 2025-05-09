import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';

function StockGraph() {
  const [chartData, setChartData] = useState(null);
  const [ticker, setTicker] = useState('AAPL'); // Default ticker
  const [period, setPeriod] = useState('1mo'); // Default period

  useEffect(() => {
    // Fetch stock data (replace with your backend API endpoint)
    fetch(`http://127.0.0.1:5000/api/stock-data?ticker=${ticker}&period=${period}`)
    .then((response) => response.json())
    .then((data) => {
      const labels = data.dates; // Array of dates
      const prices = data.prices; // Array of prices

      setChartData({
        labels,
        datasets: [
          {
            label: `${ticker} Stock Prices`,
            data: prices,
            borderColor: 'rgba(75, 192, 192, 1)',
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            fill: true,
          },
        ],
      });
    })
    .catch((error) => {
      console.error('Error fetching stock data:', error);
      alert('Failed to fetch stock data. Please try again later. Error: ${error.message}');
    });
  }, [ticker, period]);

  return (
    <div style={{ width: '80%', margin: '0 auto', textAlign: 'center' }}>
      <h2>Explore Stock Graphs</h2>
      <div style={{ marginBottom: '1rem' }}>
        <label>
          Ticker:
          <input
            type="text"
            value={ticker}
            onChange={(e) => setTicker(e.target.value)}
            style={{ marginLeft: '0.5rem', padding: '0.5rem', borderRadius: '4px', border: '1px solid #ccc' }}
          />
        </label>
        <label style={{ marginLeft: '1rem' }}>
          Period:
          <select
            value={period}
            onChange={(e) => setPeriod(e.target.value)}
            style={{ marginLeft: '0.5rem', padding: '0.5rem', borderRadius: '4px', border: '1px solid #ccc' }}
          >
            <option value="1mo">1 Month</option>
            <option value="3mo">3 Months</option>
            <option value="6mo">6 Months</option>
            <option value="1y">1 Year</option>
          </select>
        </label>
      </div>
      {chartData ? <Line data={chartData} /> : <p>Loading chart...</p>}
    </div>
  );
}

export default StockGraph;