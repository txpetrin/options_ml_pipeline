import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import TrainForm from './components/TrainForm';
import StockGraph from './components/StockGraph';

function App() {
  return (
    <Router>
      <div style={{ padding: '2rem', fontFamily: 'Arial, sans-serif', lineHeight: '1.6', backgroundColor: '#f9f9f9' }}>
        <header style={{ marginBottom: '2rem', textAlign: 'center', padding: '1rem', backgroundColor: '#e8f5e9', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)' }}>
          <h1 style={{ color: '#4CAF50', marginBottom: '0.5rem' }}>ML Model Training Dashboard f</h1>
          <nav>
            <Link to="/" style={{ marginRight: '1rem', color: '#4CAF50', textDecoration: 'none' }}>Home</Link>
            <Link to="/stock-graph" style={{ color: '#4CAF50', textDecoration: 'none' }}>Explore Stock Graphs</Link>
          </nav>
        </header>
        <main style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '50vh', padding: '1rem', backgroundColor: '#ffffff', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)' }}>
          <Routes>
            <Route path="/" element={<TrainForm />} />
            <Route path="/stock-graph" element={<StockGraph />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;