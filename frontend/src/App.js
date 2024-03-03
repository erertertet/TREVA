import React from 'react';
import logo from './logo_light.svg'; // Make sure the path to your logo is correct
import './App.css';
import YouTubeLinkSender from './send.js';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        {/* Logo container */}
        <div className="Logo-container">
          <img src={logo} className="App-logo" alt="logo" />
        </div>
        <YouTubeLinkSender></YouTubeLinkSender>
      </header>
    </div>
  );
}

export default App;
