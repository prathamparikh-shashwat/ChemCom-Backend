# ChemCom API Reference Guide

All endpoints in this reference are prefixed with `/api/v1`.

---

## 1. Global Setup

### Base URLs
* **Local Development**: `http://localhost:8000` (or `http://<your-local-ip-address>:8000` for physical devices/Android emulator testing)
* **Production**: `https://chemcom-backend.onrender.com`

### Request Headers
* JSON Requests: `Content-Type: application/json`
* File / Product Upload Requests: `Content-Type: multipart/form-data`
* Authenticated Requests: `Authorization: Bearer <jwt_access_token>`

---

## 2. Authentication API

### A. Login & Retrieve Token
Exchange credentials for an access token to access admin/protected paths.

* **Method**: `POST`
* **Path**: `/auth/login`
* **Content-Type**: `application/x-www-form-urlencoded`
* **Form Parameters**:
  * `username` (string, required): User email
  * `password` (string, required): User password
* **Success Response (`200 OK`)**:
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

## 3. Users API

### A. User Self-Registration (Sign up)
Create a normal user account.

* **Method**: `POST`
* **Path**: `/users/signup`
* **Body (JSON)**:
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

### B. Admin User Creation (CLI / Key Override)
Creates an administrator account. Allowed if the DB is empty, or if standard secret headers match.

* **Method**: `POST`
* **Path**: `/users/admin`
* **Headers**: `X-Admin-Creation-Key: <secret_key>`
* **Body (JSON)**: Same as signup.
* **Success Response (`200 OK`)**:
  ```json
  {
    "id": 1,
    "email": "admin@example.com",
    "is_active": true,
    "is_superuser": true,
    "full_name": "Admin User"
  }
  ```

### C. Get Current Profile
* **Method**: `GET`
* **Path**: `/users/me`
* **Headers**: `Authorization: Bearer <token>`
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

### D. Get User Orders
Retrieve all orders associated with a user. Accessible by the user or an admin.

* **Method**: `GET`
* **Path**: `/users/{user_id}/orders`
* **Headers**: `Authorization: Bearer <token>`
* **Success Response (`200 OK`)**:
  ```json
  [
    {
      "id": 1,
      "customer_name": "Jane Doe",
      "customer_email": "customer@example.com",
      "items": [
        {
          "product_id": 1,
          "name": "Protective Gloves",
          "quantity": 2,
          "price": 15.99
        }
      ],
      "total_amount": 31.98,
      "status": "Pending",
      "created_at": "2026-07-08T06:54:45Z"
    }
  ]
  ```

---

## 4. Products API

### A. Create Product (Admin Only)
Creates a product. Supports file uploads for storing images on Cloudinary.

* **Method**: `POST`
* **Path**: `/products/`
* **Headers**: `Authorization: Bearer <token>`, `Content-Type: multipart/form-data`
* **Request Form Parameters**:
  * `name` (string, required): Name of the product
  * `description` (string, optional): Detailed description
  * `price` (float, required): Product price
  * `is_active` (boolean, optional, default: true): Active status
  * `file` (binary, optional): Photo image file to upload
* **Success Response (`200 OK`)**:
  ```json
  {
    "id": 1,
    "name": "Protective Gloves",
    "description": "Heavy duty protective gloves.",
    "price": 15.99,
    "photo_url": "https://res.cloudinary.com/cloud-name/image/upload/v12345/products/glove.jpg",
    "is_active": true,
    "created_at": "2026-07-08T06:54:45.786373"
  }
  ```

### B. List Active Products (Public)
Retrieve all active products.

* **Method**: `GET`
* **Path**: `/products/`
* **Query Parameters**:
  * `skip` (int, default: 0)
  * `limit` (int, default: 100)
* **Success Response (`200 OK`)**:
  ```json
  [
    {
      "id": 1,
      "name": "Protective Gloves",
      "description": "Heavy duty protective gloves.",
      "price": 15.99,
      "photo_url": "https://res.cloudinary.com/cloud-name/image/upload/v12345/products/glove.jpg",
      "is_active": true,
      "created_at": "2026-07-08T06:54:45.786373"
    }
  ]
  ```

### C. List All Products (Admin Only)
Retrieve all products including inactive ones.

* **Method**: `GET`
* **Path**: `/products/all`
* **Headers**: `Authorization: Bearer <token>`
* **Success Response (`200 OK`)**: Similar list as above.

### D. Get Product by ID (Public)
* **Method**: `GET`
* **Path**: `/products/{product_id}`
* **Success Response (`200 OK`)**: Single product object.

### E. Update Product (Admin Only)
Updates product metadata and/or replaces the Cloudinary image.

* **Method**: `PUT`
* **Path**: `/products/{product_id}`
* **Headers**: `Authorization: Bearer <token>`, `Content-Type: multipart/form-data`
* **Request Form Parameters**:
  * `name` (string, optional)
  * `description` (string, optional)
  * `price` (float, optional)
  * `is_active` (boolean, optional)
  * `file` (binary, optional): New photo image file to upload
* **Success Response (`200 OK`)**: Updated product object.

### F. Deactivate Product (Admin Only)
Soft-deletes a product by changing `is_active` to `false`.

* **Method**: `DELETE`
* **Path**: `/products/{product_id}`
* **Headers**: `Authorization: Bearer <token>`
* **Success Response (`200 OK`)**: Deactivated product object.

---

## 5. Orders API

### A. Submit Customer Order (Public)
Places a new order. Quantities, item prices, names, and totals are computed and snapshotted on the backend from active product rows.

* **Method**: `POST`
* **Path**: `/orders/`
* **Body (JSON)**:
  ```json
  {
    "customer_name": "Jane Doe",
    "customer_email": "jane@example.com",
    "items": [
      {
        "product_id": 1,
        "quantity": 2
      },
      {
        "product_id": 2,
        "quantity": 1
      }
    ]
  }
  ```
* **Success Response (`200 OK`)**:
  ```json
  {
    "id": 1,
    "customer_name": "Jane Doe",
    "customer_email": "jane@example.com",
    "items": [
      {
        "product_id": 1,
        "name": "Protective Gloves",
        "quantity": 2,
        "price": 15.99
      },
      {
        "product_id": 2,
        "name": "Safety Goggles",
        "quantity": 1,
        "price": 9.5
      }
    ],
    "total_amount": 41.48,
    "status": "Pending",
    "created_at": "2026-07-08T06:54:45.786373"
  }
  ```
* **Error Response (`400 Bad Request`)**:
  ```json
  {
    "detail": "Product with ID 99 not found."
  }
  ```

### B. List Orders (Admin Only)
Retrieve all customer orders.

* **Method**: `GET`
* **Path**: `/orders/`
* **Headers**: `Authorization: Bearer <token>`
* **Success Response (`200 OK`)**: List of order response objects.

### C. Order Stats Dashboard (Admin Only)
Retrieve counts of orders grouped by status.

* **Method**: `GET`
* **Path**: `/orders/stats`
* **Headers**: `Authorization: Bearer <token>`
* **Success Response (`200 OK`)**:
  ```json
  {
    "total_orders": 25,
    "pending_orders": 10,
    "approved_orders": 5,
    "completed_orders": 8,
    "rejected_orders": 2
  }
  ```

### D. Update Order Status (Admin Only)
Change the state of a customer order.

* **Method**: `PUT`
* **Path**: `/orders/{order_id}/status`
* **Headers**: `Authorization: Bearer <token>`
* **Body (JSON)**:
  ```json
  {
    "status": "Approved"
  }
  ```
* **Success Response (`200 OK`)**: Updated order object.
