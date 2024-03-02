import logo from './logo.svg';
import './App.css';
import SendButton from './send.js';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <SendButton></SendButton>
      </header>
    </div>
  );
}

export default App;

