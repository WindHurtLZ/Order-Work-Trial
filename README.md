# Order Platform (FastAPI + Docker + AWS EC2)

This project is a simple real-time trading service showcasing:

- REST API for creating and listing orders.
- WebSocket for live status updates to all clients.
- Docker-based containerization and deployment to AWS EC2.
- CI/CD pipeline on GitHub Actions for testing and deploying.

> For demonstration purposes, newly created orders are automatically updated from `pending` to `executed` after 3 seconds. You could feel how WebSocket act its role here

## Features

1. **Post Order**
   - **Endpoint**: `POST /api/orders`
   - **Data**: `symbol`, `price`, `quantity`, `order_type`
2. **Get Order List**
   - **Endpoint**: `GET /api/orders`
   - **Returns**: A JSON array of all matching orders, ordered by most recent.
3. **Auto-Execution**
   - After you create a new order, the system schedules a background task.
   - In **3 seconds**, that task changes the order’s status from `pending` to `executed`.
4. **WebSocket Real-time Updates**
   - **Endpoint**: `GET /ws/orders`
   - Any time an order is created or updated, the server broadcasts the full list of orders
5. **Database**
   - Uses PostgreSQL or SQLite based on environment:
     - `TESTING` = `True`  for SQLite for local testing.
     - Otherwise, `DB_URL` should point to PostgreSQL.
6. **Docker Containerization**
   - A `Dockerfile` builds the FastAPI.
   - A `docker-compose.yml` for both the API and PostgreSQL container.
7. **CI/CD**
   - GitHub Actions automatically runs tests on every PR
   - On push to `main`  or MR, it SSHs to AWS EC2 instance, pulls the code, and rebuild and restart the containers.

## Getting Started Quickly

1. **Clone the Repository**

   ```bash
   git clone https://github.com/your-username/trading-platform.git
   cd trading-platform
   ```

2. **Install Dependencies**

   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Launch FastAPI Server**

   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

   - `http://localhost:8000/docs` to see the API Documentation
   - `http://localhost:8000` to see the homepage

4. **Testing**

   ```bash
   export TESTING=True
   # Run tests
   pytest -v app/tests/
   ```

## Docker & AWS EC2 Deployment

### 1. Launch EC2 Instance

1. Log in to AWS Console → EC2 → Launch Instance
2. Choose `Ubuntu 22.04 LTS`
3. Select free trail instance is enough
4. Configure Security Group :
   - SSH (22): Your IP (for secure access)
   - HTTP (80): `0.0.0.0/0` (public web access)
   - Custom TCP (8000): `0.0.0.0/0` (API access)
5. Choose/Create a Key Pair: Download the `.pem` file (needed for SSH access).

#### Assign an Elastic IP

- Go to **EC2 → Elastic IPs → Allocate New IP**.
- **Associate** the IP with your instance

------

### 2. Connect to EC2 via SSH

Run the following:

```bash
chmod 400 your-key.pem  
ssh -i key.pem ubuntu@ec2-ip
```

------

### 3. Install Required Software

```bash
sudo apt update && sudo apt upgrade -y
```

#### Install Docker

```bash
sudo apt install -y docker.io
sudo systemctl enable docker
sudo usermod -aG docker ubuntu
```

#### Install Docker Compose

```bash
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version
```

------

### 4. Deploy the Application

#### Clone the Project

```bash
git clone https://github.com/WindHurtLZ/Order-Work-Trial.git
cd Order-Work-Trial
```

#### Start Services

```bash
docker-compose up -d --build
```

- `-d`: Run in the background
- `--build`: Rebuild the application

#### Check Running Containers

```bash
docker-compose ps
```

### 6. Server Management

```bash
docker-compose restart
```

```bash
docker-compose down -v
```

## CI/CD

- Test Stage
  1. Installs dependencies
  2. Runs `pytest` to validate code
- Deploy Stage
  1. If tests pass and branch is `main`, it SSHs into EC2.
  2. Pulls latest code
  3. Run `docker-compose up -d --build` to rebuild and redeploy