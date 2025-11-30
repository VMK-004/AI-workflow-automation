import { createBrowserRouter, Navigate } from 'react-router-dom';
import { LoginPage } from '../pages/LoginPage';
import { RegisterPage } from '../pages/RegisterPage';
import { DashboardPage } from '../pages/DashboardPage';
import { WorkflowListPage } from '../pages/WorkflowListPage';
import { WorkflowEditorPage } from '../pages/WorkflowEditorPage';
import { VectorCollectionsPage } from '../pages/VectorCollectionsPage';
import { ExecutionHistoryPage } from '../pages/ExecutionHistoryPage';
import { VectorCollectionDetailPage } from '../pages/VectorCollectionDetailPage';
import { RootLayout } from '../layouts/RootLayout';
import { AuthLayout } from '../layouts/AuthLayout';
import { ProtectedRoute } from '../components/auth/ProtectedRoute';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Navigate to="/login" replace />,
  },
  {
    path: '/',
    element: <AuthLayout />,
    children: [
      {
        path: 'login',
        element: <LoginPage />,
      },
      {
        path: 'register',
        element: <RegisterPage />,
      },
    ],
  },
  {
    path: '/',
    element: <ProtectedRoute><RootLayout /></ProtectedRoute>,
    children: [
      {
        path: 'dashboard',
        element: <DashboardPage />,
      },
      {
        path: 'workflows',
        element: <WorkflowListPage />,
      },
      {
        path: 'workflows/:id',
        element: <WorkflowEditorPage />,
      },
      {
        path: 'vectors',
        element: <VectorCollectionsPage />,
      },
      {
        path: 'vector-collections/:name',
        element: <VectorCollectionDetailPage />,
      },
      {
        path: 'runs',
        element: <ExecutionHistoryPage />,
      },
    ],
  },
]);

