# Implementing Admin-Only Web Interface Authorization (React / Web)

This guide explains how to implement admin-only views, navigation guards, token storage, and API integration for the **Admin Web Interface** interacting with the FastAPI backend.

---

## 1. Backend Role & Verification

The backend identifies administrator accounts using the `is_superuser` boolean flag.
When the admin logs in via `POST /api/v1/auth/login` and retrieves their profile via `GET /api/v1/users/me`, the backend returning payload looks like this:

```json
{
  "id": 1,
  "email": "admin@chemcom.com",
  "is_active": true,
  "is_superuser": true,
  "full_name": "Admin User"
}
```

If `is_superuser` is `false`, the user does not have permission to access admin-only endpoints, and the backend will reject requests with a `403 Forbidden` or `400 Bad Request` status.

---

## 2. Managing Auth State & Storage on the Web

In a web application (e.g., built with React + Vite, Next.js, or Vue), you should store the JWT access token securely in either `localStorage`, `sessionStorage`, or a secure cookie.

### Example: Web Auth Provider (`AuthContext.jsx`)

Below is a standard React Context to manage authentication and ensure the user has admin rights.

```javascript
import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(localStorage.getItem('adminToken'));
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      if (token) {
        await fetchProfile(token);
      } else {
        setLoading(false);
      }
    };
    initAuth();
  }, [token]);

  const fetchProfile = async (authToken) => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/users/me', {
        headers: {
          'Authorization': `Bearer ${authToken}`,
        },
      });

      if (response.ok) {
        const userData = await response.json();
        if (userData.is_superuser) {
          setUser(userData);
        } else {
          // If a non-admin signs in to the web panel, reject them
          logout();
          alert('Access Denied: Admin privileges required.');
        }
      } else {
        logout();
      }
    } catch (error) {
      console.error('Error fetching profile:', error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = (jwtToken) => {
    localStorage.setItem('adminToken', jwtToken);
    setToken(jwtToken);
  };

  const logout = () => {
    localStorage.removeItem('adminToken');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ token, user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
```

---

## 3. Protecting Admin Routes in Web Routers

To prevent unauthorized users from typing in admin URLs directly (e.g., `/dashboard`), you must wrap your routes with a protection component.

### Option A: Using React Router DOM (V6)

Create a `<ProtectedRoute>` component that wraps admin-only routes:

```javascript
import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from './context/AuthContext';

const ProtectedAdminRoute = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return <div>Loading admin portal...</div>;
  }

  // Redirect to login if user is not authenticated or not a superuser
  if (!user || !user.is_superuser) {
    return <Navigate to="/login" replace />;
  }

  // Render the child components/routes
  return <Outlet />;
};

export default ProtectedAdminRoute;
```

#### Routing Setup (`App.jsx`)
```javascript
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import OrderDetails from './pages/OrderDetails';
import ProtectedAdminRoute from './components/ProtectedAdminRoute';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<Login />} />

        {/* Protected Admin Routes */}
        <Route element={<ProtectedAdminRoute />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/orders/:id" element={<OrderDetails />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
```

---

### Option B: Using Next.js (App Router middleware.js)

If using Next.js for the Admin Portal, use a root `middleware.js` to block non-admin requests before pages are rendered.

```javascript
import { NextResponse } from 'next/server';

export function middleware(request) {
  const token = request.cookies.get('adminToken')?.value;
  const url = request.nextUrl.clone();

  // If trying to access protected paths and no token exists, redirect to login
  if (!token && url.pathname !== '/login') {
    url.pathname = '/login';
    return NextResponse.redirect(url);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*', '/orders/:path*', '/'],
};
```

---

## 4. Admin Navigation & UI Guards

Hide navigation items or admin panels dynamically so standard visitors or logged-out users cannot see them.

```javascript
import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Sidebar() {
  const { user, logout } = useAuth();

  return (
    <aside className="sidebar">
      <h2>ChemCom Admin</h2>
      <nav>
        <Link to="/">Dashboard</Link>
        <Link to="/orders">Manage Orders</Link>
        
        {/* Display special controls only to superusers */}
        {user?.is_superuser && (
          <>
            <hr />
            <span className="admin-tag">Developer Controls</span>
            <Link to="/users">Manage Admin Accounts</Link>
            <Link to="/system-settings">System Settings</Link>
          </>
        )}
      </nav>
      <button onClick={logout}>Sign Out</button>
    </aside>
  );
}
```

---

## 5. Integrating Admin-Only Web APIs

Ensure that all API requests contain the `Authorization` header with the Bearer token.

### A. Fetch Dashboard Statistics (`GET /orders/stats`)
```javascript
const fetchAdminStats = async (token) => {
  try {
    const response = await fetch('http://localhost:8000/api/v1/orders/stats', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (response.status === 403) {
      throw new Error('Access Denied: You do not have permission.');
    }

    const data = await response.json();
    return data; // Returns { total_orders, pending_orders, etc. }
  } catch (error) {
    console.error('API Error:', error.message);
  }
};
```

### B. Update Order Status (`PUT /orders/{id}/status`)
Used to change an order to `Approved`, `Completed`, or `Rejected`.
```javascript
const updateOrderStatus = async (token, orderId, newStatus) => {
  try {
    const response = await fetch(`http://localhost:8000/api/v1/orders/${orderId}/status`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        status: newStatus,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to update order status');
    }

    const updatedOrder = await response.json();
    return updatedOrder;
  } catch (error) {
    alert(error.message);
  }
};
```
