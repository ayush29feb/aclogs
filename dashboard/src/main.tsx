import { StrictMode, Suspense } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { RelayEnvironmentProvider } from 'react-relay';
import environment from './RelayEnvironment.js';
import App from './App.js';
import './index.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <RelayEnvironmentProvider environment={environment}>
      <BrowserRouter>
        <Suspense fallback={<p style={{ textAlign: 'center', marginTop: 48, color: 'var(--text-3)' }}>Loading…</p>}>
          <App />
        </Suspense>
      </BrowserRouter>
    </RelayEnvironmentProvider>
  </StrictMode>
);
