import logo from './logo.svg';
import './App.css';
import YouTubeLinkSender from './send.js';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <YouTubeLinkSender></YouTubeLinkSender>
        
      </header>
    </div>
    
  );
}

export default App;

