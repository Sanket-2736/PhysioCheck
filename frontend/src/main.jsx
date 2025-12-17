import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './app.css'
import App from './App.jsx'
import { BrowserRouter } from 'react-router-dom'
import { AppProvider } from './context/AppContext.jsx'
import { ToastContainer } from 'react-toastify'

createRoot(document.getElementById('root')).render(
  <BrowserRouter>
  <ToastContainer position="top-right" />
    <AppProvider>
      <StrictMode>
        <App />
      </StrictMode>
    </AppProvider>  
  </BrowserRouter>,
)
