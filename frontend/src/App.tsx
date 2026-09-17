import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { AuthProvider } from "@/features/auth/AuthContext";
import { RequireAuth } from "@/features/auth/RequireAuth";
import { AppLayout } from "@/components/layout/AppLayout";
import { CaseDetail } from "@/pages/CaseDetail";
import { Dashboard } from "@/pages/Dashboard";
import { Login } from "@/pages/Login";
import { PatientDetail } from "@/pages/PatientDetail";
import { PatientsList } from "@/pages/PatientsList";
import { Schedule } from "@/pages/Schedule";
import { WaitingList } from "@/pages/WaitingList";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route element={<RequireAuth />}>
              <Route element={<AppLayout />}>
                <Route path="/" element={<Dashboard />} />
                <Route path="/patients" element={<PatientsList />} />
                <Route path="/patients/:id" element={<PatientDetail />} />
                <Route path="/schedule" element={<Schedule />} />
                <Route path="/schedule" element={<Schedule />} />
                <Route path="/waiting-list" element={<WaitingList />} />
                <Route path="/cases/:id" element={<CaseDetail />} />
              </Route>
            </Route>
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
