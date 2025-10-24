import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { CreateTripPage } from './pages/CreateTripPage';
import { TripDashboardPage } from './pages/TripDashboardPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import LandingPage from './pages/LandingPage';
import ProtectedRoute from './components/ProtectedRoute';

const App = () => {
  return (
    <>
      <div>
        <Toaster 
          position="top-center"
          reverseOrder={false}
          toastOptions={{
            style: {
              background: '#333',
              color: '#fff',
            },
          }}
        />
      </div>

      <Router>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <CreateTripPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/trip/:tripId"
            element={
              <ProtectedRoute>
                <TripDashboardPage />
              </ProtectedRoute>
            }
          />
        </Routes>
      </Router>
    </>
  );
};

export default App;

