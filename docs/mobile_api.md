# Mobile API Integration Guide (React Native)

Welcome! This document outlines how to integrate the React Native mobile application with the FastAPI backend. 

---

## 1. Connection Guidelines

### Base URL
* **Local Development**: `http://<your-local-ip-address>:8000` 
  *(Note: Do **NOT** use `localhost` or `127.0.0.1` in React Native when testing on physical devices or Android Emulators; use your machine's local network IP address instead).*
* **Production / Render**: `https://chemcom-backend.onrender.com`

### Request Headers
* All JSON write requests (`POST`, `PUT`) must include:
  `Content-Type: application/json`
* Authenticated endpoints require the Bearer Token header:
  `Authorization: Bearer <your_access_token>`

---

## 2. Authentication Flow

```text
[Mobile Client]                               [FastAPI Backend]
       │                                              │
       ├───── 1. POST /users/signup ─────────────────>│  (Register User)
       │                                              │
       ├───── 2. POST /auth/login (Form Data) ────────>│  (Retrieve JWT Access Token)
       │                                              │
       │<──── 3. Response: {access_token: "..."} ─────┤  (Save token in AsyncStorage)
       │                                              │
       ├───── 4. GET /users/me (Bearer Token Header) ─>│  (Access Authenticated API)
```

---

## 3. API Endpoints Reference

All paths are relative to the Base URL, prefixed with `/api/v1`.

### A. Public Registration (Sign up)
Creates a new customer or user account.

* **Method**: `POST`
* **Path**: `/api/v1/users/signup`
* **Headers**: `Content-Type: application/json`
* **Request Body (JSON)**:
  ```json
  {
    "email": "customer@example.com",
    "password": "customerpassword123",
    "full_name": "Jane Doe"
  }
  ```
* **Success Response (`200 OK`)**:
  ```json
  {
    "id": 2,
    "email": "customer@example.com",
    "is_active": true,
    "is_superuser": false,
    "full_name": "Jane Doe"
  }
  ```
* **Error Response (`400 Bad Request`)**:
  ```json
  {
    "detail": "The user with this email already exists."
  }
  ```

---

### B. Access Token Login (Authenticate)
Exchanges user credentials for a JWT token to access private endpoints.

* **Method**: `POST`
* **Path**: `/api/v1/auth/login`
* **Headers**: `Content-Type: application/x-www-form-urlencoded`
* **Request Body (Form Data)**:
  * `username`: `customer@example.com`
  * `password`: `customerpassword123`
* **Success Response (`200 OK`)**:
  * *Store the `access_token` locally in the mobile app (e.g., using `AsyncStorage`, `SecureStore`, or `MMKV`).*
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
    "token_type": "bearer"
  }
  ```
* **Error Response (`400 Bad Request`)**:
  ```json
  {
    "detail": "Incorrect email or password"
  }
  ```

---

### C. Create Customer Order
Submits customer orders from the React Native cart checkout.

* **Method**: `POST`
* **Path**: `/api/v1/orders/`
* **Headers**: `Content-Type: application/json`
* **Request Body (JSON)**:
  ```json
  {
    "customer_name": "Jane Doe",
    "customer_email": "customer@example.com",
    "items": [
      {
        "name": "Heavy Duty ChemCom Glove",
        "quantity": 2,
        "price": 14.99
      },
      {
        "name": "Standard Protective Goggles",
        "quantity": 1,
        "price": 9.50
      }
    ],
    "total_amount": 39.48
  }
  ```
* **Success Response (`200 OK`)**:
  ```json
  {
    "id": 4,
    "customer_name": "Jane Doe",
    "customer_email": "customer@example.com",
    "items": [
      {
        "name": "Heavy Duty ChemCom Glove",
        "quantity": 2,
        "price": 14.99
      },
      {
        "name": "Standard Protective Goggles",
        "quantity": 1,
        "price": 9.50
      }
    ],
    "total_amount": 39.48,
    "status": "Pending",
    "created_at": "2026-07-03T10:00:00Z"
  }
  ```

---

### D. Get Current User Details (Profile)
Fetches logged-in user details to display on screen.

* **Method**: `GET`
* **Path**: `/api/v1/users/me`
* **Headers**: 
  * `Authorization: Bearer <your_access_token>`
* **Success Response (`200 OK`)**:
  ```json
  {
    "id": 2,
    "email": "customer@example.com",
    "is_active": true,
    "is_superuser": false,
    "full_name": "Jane Doe"
  }
  ```

---

### E. Update Current User Details
Updates logged-in user profile or password.

* **Method**: `PUT`
* **Path**: `/api/v1/users/me`
* **Headers**:
  * `Content-Type: application/json`
  * `Authorization: Bearer <your_access_token>`
* **Request Body (JSON)**:
  ```json
  {
    "full_name": "Jane Alice Doe",
    "password": "newsecurepassword456"
  }
  ```
* **Success Response (`200 OK`)**:
  ```json
  {
    "id": 2,
    "email": "customer@example.com",
    "is_active": true,
    "is_superuser": false,
    "full_name": "Jane Alice Doe"
  }
  ```

---

### F. Get User Orders
Fetches all orders associated with a specific user by their user ID.

* **Method**: `GET`
* **Path**: `/api/v1/users/{user_id}/orders`
* **Headers**:
  * `Authorization: Bearer <your_access_token>`
* **Success Response (`200 OK`)**:
  ```json
  [
    {
      "id": 4,
      "customer_name": "Jane Doe",
      "customer_email": "customer@example.com",
      "items": [
        {
          "name": "Heavy Duty ChemCom Glove",
          "quantity": 2,
          "price": 14.99
        }
      ],
      "total_amount": 29.98,
      "status": "Pending",
      "created_at": "2026-07-03T10:00:00Z"
    }
  ]
  ```
* **Error Response (`403 Forbidden`)**:
  ```json
  {
    "detail": "The user doesn't have enough privileges"
  }
  ```
* **Error Response (`404 Not Found`)**:
  ```json
  {
    "detail": "The user with this ID does not exist."
  }
  ```

---

## 4. React Native Integration Snippets

Here are examples using the built-in `fetch` API in JavaScript/TypeScript.

### 1. Registering a User (Sign up)
```javascript
const registerUser = async (email, password, fullName) => {
  try {
    const response = await fetch('http://192.168.1.100:8000/api/v1/users/signup', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: email,
        password: password,
        full_name: fullName,
      }),
    });

    const data = await response.json();
    if (response.ok) {
      console.log('Registration Success:', data);
    } else {
      console.error('Registration Failed:', data.detail);
    }
  } catch (error) {
    console.error('Network Error:', error);
  }
};
```

### 2. Logging In & Storing Token
```javascript
import AsyncStorage from '@react-native-async-storage/async-storage';

const loginUser = async (email, password) => {
  try {
    // Note: OAuth2 expects Form URL Encoded format
    const details = {
      'username': email,
      'password': password,
    };

    const formBody = Object.keys(details)
      .map(key => encodeURIComponent(key) + '=' + encodeURIComponent(details[key]))
      .join('&');

    const response = await fetch('http://192.168.1.100:8000/api/v1/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
      },
      body: formBody,
    });

    const data = await response.json();
    if (response.ok) {
      // Save JWT access token in storage
      await AsyncStorage.setItem('userToken', data.access_token);
      console.log('Token successfully stored!');
    } else {
      console.error('Login failed:', data.detail);
    }
  } catch (error) {
    console.error('Network Error:', error);
  }
};
```

### 3. Posting an Order (Checkout)
```javascript
const submitOrder = async (customerName, email, cartItems, total) => {
  try {
    const response = await fetch('http://192.168.1.100:8000/api/v1/orders/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        customer_name: customerName,
        customer_email: email,
        items: cartItems.map(item => ({
          name: item.title,
          quantity: item.qty,
          price: item.price
        })),
        total_amount: total
      }),
    });

    const data = await response.json();
    if (response.ok) {
      console.log('Order Submitted Successfully. Order ID:', data.id);
    } else {
      console.error('Order Submission Failed:', data);
    }
  } catch (error) {
    console.error('Network Error:', error);
  }
};

### 4. Fetching User Orders
```javascript
const fetchUserOrders = async (userId, userToken) => {
  try {
    const response = await fetch(`http://192.168.1.100:8000/api/v1/users/${userId}/orders`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${userToken}`,
      },
    });

    const data = await response.json();
    if (response.ok) {
      console.log('User Orders:', data);
      return data;
    } else {
      console.error('Failed to fetch orders:', data.detail);
    }
  } catch (error) {
    console.error('Network Error:', error);
  }
};
```
```
