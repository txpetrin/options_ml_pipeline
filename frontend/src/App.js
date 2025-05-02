import React from 'react';
import TrainForm from './components/TrainForm';

function App() {
  return (
    <div style={{ padding: '2rem', fontFamily: 'Arial, sans-serif', lineHeight: '1.6' }}>
      <header style={{ marginBottom: '2rem', textAlign: 'center' }}>
        <h1 style={{ color: '#4CAF50' }}>ML Model Training Dashboard</h1>
        <p style={{ fontSize: '1.2rem', color: '#555' }}>
          Welcome to the ML Model Training Dashboard! This web app allows you to configure and train machine learning models with ease. These models are trained using options data. 
        </p>
        <p style={{ fontSize: '1.2rem', color: '#555' }}>
          You can specify the ticker symbol, training period, and number of epochs for your model. The app will handle the rest, providing you with real-time feedback on the training process.
        </p>
        <p style={{ fontSize: '1.2rem', color: '#555' }}>
          Fill out the form below to get started.
        </p>
      </header>
      <main style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '50vh' }}>
        <TrainForm />
      </main>
    </div>
  );
}

export default App;
