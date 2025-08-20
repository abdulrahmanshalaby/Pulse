# Pulse – Twitter-Like Backend

![Python](https://img.shields.io/badge/python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100.0-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)
![Docker](https://img.shields.io/badge/Docker-informational)
![AWS S3](https://img.shields.io/badge/AWS_S3-orange)

Pulse is a **Twitter-like backend API** built with FastAPI, SQLAlchemy, and PostgreSQL.  
It demonstrates modern backend practices including **event-driven architecture, real-time updates, and cloud media storage**, all fully containerized for easy local setup.

---

## Features

- Twitter-like backend with JWT authentication  
- Real-time updates via **WebSockets**  
- Media storage on **AWS S3**  
- Dockerized for local development and testing  

---

## Tech Stack

- **Python 3.11**  
- **FastAPI** – web framework  
- **SQLAlchemy** – ORM for PostgreSQL  
- **PostgreSQL** – relational database  
- **Redis** – optional caching layer  
- **AWS S3** – media storage  
- **Docker** – containers for DB and services  
---

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/your-username/twclone.git
cd backend/src
```
### 2. Create a virtual environment & activate it
```bash
# Linux / macOS
python -m venv venv
source venv/bin/activate
```
```bash
# Windows (PowerShell)
python -m venv venv
venv\Scripts\Activate.ps1
````
### 3. Install dependencies
````bash

# Install dependencies
pip install -r requirements.txt
````
### 4. Start services with Docker
```bash
docker-compose up -d
```
## API Examples
## login
````
curl -X POST http://127.0.0.1:8000/auth/login \
-H "Content-Type: application/x-www-form-urlencoded" \
-d "username=alice&password=pass123"
````
### Create a Tweet
````
curl -X POST http://127.0.0.1:8080/api/tweet/ \
-H "Authorization: Bearer <TOKEN>" \
-H "Content-Type: application/json" \
-d '{"content": "Hello world!"}'
````
