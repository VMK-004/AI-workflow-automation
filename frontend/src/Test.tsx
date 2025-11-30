// Simple test component
export function Test() {
  return (
    <div style={{ 
      padding: '20px', 
      fontSize: '24px', 
      color: 'black',
      backgroundColor: 'yellow' 
    }}>
      <h1>✅ React is Working!</h1>
      <p>If you see this, React is rendering correctly.</p>
      <p>Backend API: {import.meta.env.VITE_API_URL || 'Not set'}</p>
    </div>
  );
}

