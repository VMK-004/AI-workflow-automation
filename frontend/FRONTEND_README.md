# AI Workflow Builder - Frontend

React + TypeScript + Vite frontend for the AI Workflow Builder platform.

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **React Router v6** - Routing
- **Zustand** - State management
- **Tailwind CSS** - Styling
- **Headless UI** - Accessible components
- **Heroicons** - Icons
- **Axios** - HTTP client
- **React Hot Toast** - Notifications

## Project Structure

```
frontend/
├── src/
│   ├── api/                 # API client and endpoints
│   │   ├── client.ts        # Axios instance with interceptors
│   │   ├── auth.ts          # Authentication endpoints
│   │   ├── workflows.ts     # Workflow endpoints
│   │   ├── nodes.ts         # Node endpoints
│   │   ├── edges.ts         # Edge endpoints
│   │   └── vectors.ts       # Vector collection endpoints
│   │
│   ├── components/
│   │   ├── auth/           # Auth-related components
│   │   │   └── ProtectedRoute.tsx
│   │   ├── common/         # Reusable components
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Modal.tsx
│   │   │   └── Loader.tsx
│   │   ├── layout/         # Layout components
│   │   │   ├── Navbar.tsx
│   │   │   └── Sidebar.tsx
│   │   └── workflows/      # Workflow-specific (to be added)
│   │
│   ├── pages/              # Page components
│   │   ├── LoginPage.tsx
│   │   ├── RegisterPage.tsx
│   │   ├── DashboardPage.tsx
│   │   ├── WorkflowListPage.tsx
│   │   ├── WorkflowEditorPage.tsx (placeholder)
│   │   ├── VectorCollectionsPage.tsx
│   │   └── ExecutionHistoryPage.tsx (placeholder)
│   │
│   ├── store/              # Zustand stores
│   │   ├── authStore.ts    # Authentication state
│   │   ├── workflowStore.ts # Workflow state
│   │   ├── editorStore.ts  # Editor state
│   │   └── vectorStore.ts  # Vector collection state
│   │
│   ├── layouts/            # Layout wrappers
│   │   ├── RootLayout.tsx  # Main app layout
│   │   └── AuthLayout.tsx  # Auth pages layout
│   │
│   ├── router/             # Route configuration
│   │   └── index.tsx
│   │
│   ├── utils/              # Utility functions
│   │   ├── token.ts        # JWT token management
│   │   └── http.ts         # HTTP helpers
│   │
│   ├── App.tsx             # Main app component
│   └── main.tsx            # Entry point
│
├── public/                 # Static assets
├── .env                    # Environment variables
├── tailwind.config.js      # Tailwind configuration
└── vite.config.ts          # Vite configuration
```

## Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

Create a `.env` file:

```bash
VITE_API_URL=http://localhost:8000/api
```

### 3. Start Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

## Features

### ✅ Implemented

1. **Authentication**
   - Login page with JWT auth
   - Register page
   - Protected routes
   - Auto-redirect on auth state change
   - Token management (localStorage)

2. **Dashboard**
   - Overview of workflows and collections
   - Quick actions
   - Recent items

3. **Workflow Management**
   - List all workflows
   - Create new workflow
   - Delete workflow
   - Basic workflow editor (placeholder)

4. **Vector Collections**
   - List collections
   - View collection details
   - Delete collection
   - Search interface (placeholder)

5. **Execution History**
   - Placeholder page for run history

6. **UI Components**
   - Reusable Button, Input, Modal, Loader
   - Responsive Navbar and Sidebar
   - Toast notifications
   - Tailwind styling

### 🔄 To Be Implemented

1. **Visual Workflow Editor**
   - Canvas-based node editor
   - Drag-and-drop nodes
   - Visual edge connections
   - Node configuration panel
   - Real-time validation

2. **Vector Collection Features**
   - Create collection with documents
   - Add documents to collection
   - Search interface with filters
   - View search results

3. **Execution Features**
   - Workflow execution UI
   - Real-time execution status
   - View execution results
   - Execution history table

4. **Advanced Features**
   - Workflow templates
   - Duplicate workflow
   - Export/import workflows
   - Collaborative editing
   - Dark mode

## Routes

| Path | Component | Protected | Description |
|------|-----------|-----------|-------------|
| `/` | Redirect | No | Redirects to /dashboard |
| `/login` | LoginPage | No | User login |
| `/register` | RegisterPage | No | User registration |
| `/dashboard` | DashboardPage | Yes | Main dashboard |
| `/workflows` | WorkflowListPage | Yes | List workflows |
| `/workflows/:id` | WorkflowEditorPage | Yes | Edit workflow |
| `/vectors` | VectorCollectionsPage | Yes | Manage collections |
| `/runs` | ExecutionHistoryPage | Yes | View run history |

## State Management

### Auth Store (`authStore.ts`)
- User information
- Authentication status
- Login/logout/register methods
- Token management

### Workflow Store (`workflowStore.ts`)
- Workflows list
- Current workflow
- Nodes and edges
- CRUD operations

### Editor Store (`editorStore.ts`)
- Selected node
- Config modal state
- Editor-specific state

### Vector Store (`vectorStore.ts`)
- Collections list
- Search results
- Collection operations

## API Integration

All API calls go through the centralized client (`src/api/client.ts`) with:
- Automatic JWT token injection
- Response interceptor for 401 errors
- Error handling
- Base URL configuration

Example:
```typescript
import { workflowsApi } from '../api/workflows';

// List workflows
const workflows = await workflowsApi.list();

// Create workflow
const workflow = await workflowsApi.create({
  name: 'My Workflow',
  description: 'Description'
});
```

## Styling

The app uses Tailwind CSS with a custom theme:

- **Primary color**: Blue (#3b82f6)
- **Responsive**: Mobile-first design
- **Components**: Consistent spacing and sizing
- **Dark mode ready**: Classes prepared for dark mode

## Development

### Run Dev Server

```bash
npm run dev
```

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

### Lint Code

```bash
npm run lint
```

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers

## Next Steps

1. **Implement Visual Editor**
   - Use React Flow or custom canvas
   - Node dragging and positioning
   - Edge drawing and deletion
   - Node configuration forms

2. **Complete Vector UI**
   - Collection creation form
   - Document upload
   - Search interface
   - Results display

3. **Add Execution Monitoring**
   - Real-time status updates
   - Progress indicators
   - Result visualization

4. **Testing**
   - Unit tests (Vitest)
   - Component tests (Testing Library)
   - E2E tests (Playwright)

5. **Optimization**
   - Code splitting
   - Lazy loading routes
   - Image optimization
   - Bundle analysis

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API base URL | `http://localhost:8000/api` |

## Contributing

1. Follow the existing code structure
2. Use TypeScript strictly
3. Follow React best practices
4. Use Tailwind for styling
5. Test your changes

## Status

✅ **Setup Complete** - Basic structure and auth flow working  
🔄 **In Progress** - Visual editor and advanced features  
📋 **Planned** - Testing, optimization, deployment  

---

**Ready to develop!** Start the dev server and begin building features! 🚀





