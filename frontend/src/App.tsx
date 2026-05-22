import { Navigate, Route, Routes } from "react-router-dom";
import ProtectedRoute from "@/components/ProtectedRoute";
import DashboardLayout from "@/layouts/DashboardLayout";
import Landing from "@/pages/Landing";
import Pricing from "@/pages/Pricing";
import Login from "@/pages/Login";
import Register from "@/pages/Register";
import Dashboard from "@/pages/Dashboard";
import Numbers from "@/pages/Numbers";
import Templates from "@/pages/Templates";
import SendMessage from "@/pages/SendMessage";
import Conversations from "@/pages/Conversations";
import Settings from "@/pages/Settings";
import Subscription from "@/pages/Subscription";

export default function App() {
  return (
    <Routes>
      {/* Public */}
      <Route path="/" element={<Landing />} />
      <Route path="/pricing" element={<Pricing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* Authenticated dashboard */}
      <Route
        path="/app"
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="numbers" element={<Numbers />} />
        <Route path="templates" element={<Templates />} />
        <Route path="send" element={<SendMessage />} />
        <Route path="conversations" element={<Conversations />} />
        <Route path="settings" element={<Settings />} />
        <Route path="subscription" element={<Subscription />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
