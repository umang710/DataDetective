import { Routes, Route } from "react-router-dom";
import StartPage from "./components/StartPage";
import LevelPage from "./components/LevelPage";
import FinalPage from "./components/FinalPage";
import ResultsPage from "./components/ResultsPage";
import AdminLogin from "./components/AdminLogin";

function App() {
  return (
    <Routes>
      <Route path="/" element={<StartPage />} />
      <Route path="/level1" element={<LevelPage level={1} />} />
      <Route path="/level2" element={<LevelPage level={2} />} />
      <Route path="/level3" element={<LevelPage level={3} />} />
      <Route path="/final" element={<FinalPage />} />
      <Route path="/results" element={<ResultsPage />} />
      <Route path="/admin" element={<AdminLogin />} />
    </Routes>
  );
}

export default App;
