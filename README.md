# Villa Reservation System

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.68.0+-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue.svg)
![MinIO](https://img.shields.io/badge/MinIO-latest-orange.svg)
![Docker](https://img.shields.io/badge/Docker-20.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

Welcome to the **Villa Reservation System**, a modern, microservices-based platform for managing villa rentals. Built with **FastAPI**, **PostgreSQL**, **MinIO**, and **Docker**, this project offers a scalable and secure solution for users to browse, reserve, and manage villa bookings, with robust admin controls for overseeing operations.

## 🌟 Features

- **User Authentication**: Secure phone-based login with OTP verification.
- **Villa Management**: Create, update, and retrieve villas with image uploads (PNG, JPEG, GIF, WebP).
- **Reservation System**: Book villas with overlap prevention, capacity checks, and dynamic pricing.
- **Media Storage**: Store and serve villa images using MinIO object storage.
- **Admin Controls**: View all reservations, user-specific reservations, and delete bookings.
- **Public Villa Dates**: Retrieve reserved date ranges for any villa to plan bookings.
- **Swagger UI**: Interactive API documentation for all services with clear tags and descriptions.
- **Dockerized Deployment**: Run the entire system with a single `docker-compose up`.

## 🏗️ Architecture

The system is composed of five microservices, each handling a specific domain:

1. **User Service** (`user-service`, port `8001`):
   - Handles user authentication via phone number and OTP.
   - Endpoints: Login, OTP verification, user registration.
   - Swagger UI: `http://localhost:8001/docs`

2. **OTP Service** (`otp-service`, port `8005`):
   - Generates and verifies one-time passwords for authentication.
   - Stores OTPs in Redis for fast access.
   - Swagger UI: `http://localhost:8005/docs`

3. **Villa Service** (`villa-service`, port `8002`):
   - Manages villa creation, updates, and retrieval.
   - Supports image uploads via `media-service`.
   - Admin-only for create/update, public for retrieval.
   - Swagger UI: `http://localhost:8002/docs`

4. **Reservation Service** (`reservation-service`, port `8003`):
   - Handles villa reservations with overlap prevention and capacity validation.
   - User routes for creating and viewing bookings.
   - Admin routes for viewing all/user-specific reservations and deleting bookings.
   - Public route for villa reservation dates.
   - Swagger UI: `http://localhost:8003/docs`

5. **Media Service** (`media-service`, port `8004`):
   - Manages image uploads and retrieval using MinIO.
   - Supports multiple formats with UUID-based filenames.
   - Swagger UI: `http://localhost:8004/docs`

### Dependencies
- **PostgreSQL**: Stores users, villas, and reservations.
- **Redis**: Caches OTPs for `otp-service`.
- **MinIO**: Stores villa images for `media-service`.
- **Docker Compose**: Orchestrates all services and dependencies.

## 🚀 Getting Started

### Prerequisites
- **Docker** and **Docker Compose** installed.
- **Python 3.9+** (optional, for local development without Docker).
- A modern web browser to access Swagger UI.

### Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/ErfanZmp/villa-reservation.git
   cd villa-reservation
   ```

2. **Set Up Environment Variables**:
   Copy the example `.env` file and adjust if needed:
   ```bash
   cp .env.example .env
   ```
   Example `.env`:
   ```plaintext
   POSTGRES_USER=admin
   POSTGRES_PASSWORD=password
   POSTGRES_DB=villa_db
   MINIO_ROOT_USER=admin
   MINIO_ROOT_PASSWORD=password
   MINIO_HOST=minio:9000
   EXTERNAL_MINIO_HOST=localhost:9000
   USER_SERVICE_URL=http://user-service:8001
   VILLA_SERVICE_URL=http://villa-service:8002
   RESERVATION_SERVICE_URL=http://reservation-service:8003
   MEDIA_SERVICE_URL=http://media-service:8004
   MEDIA_SERVICE_HOST=localhost:8004
   OTP_SERVICE_URL=http://otp-service:8005
   JWT_SECRET=your-secret-key
   MINIO_BUCKET_NAME=villa-images
   ```

3. **Build and Run with Docker**:
   ```bash
   docker-compose up -d
   ```
   This starts all services, PostgreSQL, Redis, and MinIO.

4. **Verify Services**:
   - User Service: `http://localhost:8001/docs`
   - OTP Service: `http://localhost:8005/docs`
   - Villa Service: `http://localhost:8002/docs`
   - Reservation Service: `http://localhost:8003/docs`
   - Media Service: `http://localhost:8004/docs`
   - MinIO Console: `http://localhost:9001` (login: `admin`/`password`)

### Usage

#### 1. Authenticate as a User
- **Register/Login**:
  ```bash
  curl -X POST http://localhost:8001/auth/login -H "Content-Type: application/json" -d '{"phone_number": "+0000000002"}'
  ```
  Check OTP in `otp-service` logs:
  ```bash
  docker-compose logs otp-service
  ```
  Verify OTP:
  ```bash
  curl -X POST http://localhost:8001/auth/login/verify -H "Content-Type: application/json" -d '{"phone_number": "+0000000002", "otp": "<otp>"}'
  ```
  Save the `access_token`.

#### 2. Create a Villa (Admin)
- Authenticate as an admin (`+0000000001`).
- Create a villa:
  ```bash
  curl -X POST http://localhost:8002/api/v1/villas \
  -H "Authorization: Bearer <admin-jwt-token>" \
  -F "villa={\"title\":\"Seaside Villa\",\"city\":\"Mazandaran\",\"address\":\"123 Seaside Rd\",\"base_capacity\":5,\"maximum_capacity\":8,\"area\":400,\"bed_count\":5,\"has_pool\":false,\"has_cooling_system\":true,\"base_price_per_night\":2500,\"extra_person_price\":400,\"rating\":4.5}" \
  -F "image=@/path/to/image.png"
  ```

#### 3. Reserve a Villa
- Check available dates:
  ```bash
  curl http://localhost:8003/reservations/villa/1/dates
  ```
- Create a reservation:
  ```bash
  curl -X POST http://localhost:8003/reservations \
  -H "Authorization: Bearer <user-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{"villa_id":1,"check_in_date":"2025-06-01","check_out_date":"2025-06-05","people_count":5}'
  ```

#### 4. Admin Operations
- List all reservations:
  ```bash
  curl -X GET http://localhost:8003/reservations/admin/all \
  -H "Authorization: Bearer <admin-jwt-token>"
  ```
- List user reservations:
  ```bash
  curl -X GET http://localhost:8003/reservations/admin/user/1 \
  -H "Authorization: Bearer <admin-jwt-token>"
  ```
- Delete a reservation:
  ```bash
  curl -X DELETE http://localhost:8003/reservations/admin/1 \
  -H "Authorization: Bearer <admin-jwt-token>"
  ```

## 📚 API Documentation

Each service provides interactive Swagger UI:
- **User Service**: `http://localhost:8001/docs` (auth endpoints)
- **OTP Service**: `http://localhost:8005/docs` (OTP management)
- **Villa Service**: `http://localhost:8002/docs` (villa CRUD)
- **Reservation Service**: `http://localhost:8003/docs` (reservations, tagged as `user-reservations`, `villa-dates`, `admin-reservations`)
- **Media Service**: `http://localhost:8004/docs` (image upload/retrieval)

Endpoints are tagged and described for clarity, with examples and schemas.

## 🛠️ Development

### Local Development
1. Install dependencies for a service (e.g., `reservation-service`):
   ```bash
   cd reservation-service
   pip install -r requirements.txt
   ```
2. Run a service locally:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
   ```
   Ensure dependencies (PostgreSQL, Redis, MinIO) are running via Docker.

### Project Structure
```
villa-reservation-system/
├── user-service/
│   ├── app/
│   │   ├── main.py
│   │   ├── schemas/
│   │   ├── models/
│   │   ├── dependencies.py
├── otp-service/
│   ├── app/
│   │   ├── main.py
├── villa-service/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/v1/routers/villa.py
│   │   ├── schemas/villa.py
├── reservation-service/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/v1/routers/admin.py
│   │   ├── models/
│   │   ├── dependencies.py
├── media-service/
│   ├── app/
│   │   ├── main.py
├── .env
├── docker-compose.yml
```

### Extending the Project
- **Add Notifications**: Integrate email/SMS via `otp-service` for reservation confirmations.
- **Soft Delete**: Implement soft deletion for reservations with an `is_deleted` flag.
- **Pagination**: Add offset/limit to reservation list endpoints.
- **Frontend**: Build a React/Vue.js frontend to interact with the APIs.

## 🔍 Troubleshooting

- **Service Not Starting**:
  - Check logs: `docker-compose logs <service-name>`
  - Verify `.env` variables and Docker health checks.
- **Authentication Issues**:
  - Ensure `JWT_SECRET` is consistent across services.
  - Check OTP logs for verification failures.
- **Image Upload Failures**:
  - Confirm MinIO is running: `http://localhost:9001`
  - Verify `MINIO_BUCKET_NAME` and credentials.
- **Reservation Overlaps**:
  - Use `GET /reservations/villa/{villa_id}/dates` to check reserved dates.

## 📝 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🙌 Contributing

Contributions are welcome! Please:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/your-feature`).
3. Commit changes (`git commit -m 'Add your feature'`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a Pull Request.

## 📬 Contact

For questions or feedback, open an issue on GitHub or contact the maintainer at `your-email@example.com`.

---

Happy booking! 🏡