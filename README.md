# Airport Management & Ticketing System

REST API for managing airports, flights, airlines, aircraft, countries, users, and airline tickets.

The project also includes ticket booking, Stripe payments, asynchronous PDF ticket generation, AWS S3 storage, email notifications, and background tasks with Celery.

## Features

- User registration and authentication
- JWT authentication
- Email verification
- User roles (`admin` / `user`)
- User profiles
- Airport management
- Country management
- Airline management
- Aircraft management
- Flight management
- Ticket booking
- Seat availability validation
- Ticket status management
- Filtering and pagination
- Stripe Checkout integration
- Stripe Webhooks
- Asynchronous email notifications
- PDF boarding pass generation
- QR code generation
- AWS S3 file storage
- Background tasks with Celery
- Periodic tasks with Celery Beat
- Swagger / OpenAPI documentation

---

## Tech Stack

### Backend

- Python 3.13
- Django
- Django REST Framework
- PostgreSQL
- JWT
- Django Filters

### Background Processing

- Celery
- Redis
- Celery Beat

### Payments

- Stripe Checkout
- Stripe Webhooks

### PDF Service

- FastAPI
- ReportLab
- QR Code

### Storage

- AWS S3

### DevOps

- Docker
- Docker Compose

### Documentation

- Swagger
- OpenAPI
- drf-spectacular

---

## Architecture

The project consists of the main Django REST API and a separate FastAPI microservice responsible for PDF ticket generation.
