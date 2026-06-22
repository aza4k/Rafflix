import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import RaffleDetail from './pages/RaffleDetail';
import Wallet from './pages/Wallet';
import Referral from './pages/Referral';

function App() {
  return (
    <Router>
      <div className="bg-primary min-h-screen text-white flex flex-col max-w-lg mx-auto">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/raffle/:id" element={<RaffleDetail />} />
          <Route path="/wallet" element={<Wallet />} />
          <Route path="/referral" element={<Referral />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
