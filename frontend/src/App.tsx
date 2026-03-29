import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes, Navigate } from "react-router-dom";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AuthProvider } from "@/context/AuthContext";
import { RequireAuth, RequireRole } from "@/components/guards/RequireAuth";
import LoginPage from "./pages/LoginPage";
import ConsentPage from "./pages/ConsentPage";
import ProfileSetupPage from "./pages/ProfileSetupPage";
import QuestionnairePage from "./pages/QuestionnairePage";
import PatientHomePage from "./pages/PatientHomePage";
import JournalPage from "./pages/JournalPage";
import ChatPage from "./pages/ChatPage";
import PatientsListPage from "./pages/PatientsListPage";
import PatientDetailPage from "./pages/PatientDetailPage";
import PatientProfilePage from "./pages/PatientProfilePage";
import ClinicianProfilePage from "./pages/ClinicianProfilePage";
import ReportsPage from "./pages/ReportsPage";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            <Route path="/" element={<Navigate to="/login" replace />} />
            <Route path="/login" element={<LoginPage />} />

            {/* Patient routes */}
            <Route path="/patient/consent" element={<RequireAuth><RequireRole role="patient"><ConsentPage /></RequireRole></RequireAuth>} />
            <Route path="/patient/profile-setup" element={<RequireAuth><RequireRole role="patient"><ProfileSetupPage /></RequireRole></RequireAuth>} />
            <Route path="/patient/questionnaire" element={<RequireAuth><RequireRole role="patient"><QuestionnairePage /></RequireRole></RequireAuth>} />
            <Route path="/patient/home" element={<RequireAuth><RequireRole role="patient"><PatientHomePage /></RequireRole></RequireAuth>} />
            <Route path="/patient/journal" element={<RequireAuth><RequireRole role="patient"><JournalPage /></RequireRole></RequireAuth>} />
            <Route path="/patient/chat" element={<RequireAuth><RequireRole role="patient"><ChatPage /></RequireRole></RequireAuth>} />
            <Route path="/patient/profile" element={<RequireAuth><RequireRole role="patient"><PatientProfilePage /></RequireRole></RequireAuth>} />

            {/* Clinician routes */}
            <Route path="/clinician/patients" element={<RequireAuth><RequireRole role="clinician"><PatientsListPage /></RequireRole></RequireAuth>} />
            <Route path="/clinician/patients/:patient_id" element={<RequireAuth><RequireRole role="clinician"><PatientDetailPage /></RequireRole></RequireAuth>} />
            <Route path="/clinician/profile" element={<RequireAuth><RequireRole role="clinician"><ClinicianProfilePage /></RequireRole></RequireAuth>} />

            {/* Shared */}
            <Route path="/reports" element={<RequireAuth><ReportsPage /></RequireAuth>} />

            <Route path="*" element={<NotFound />} />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
