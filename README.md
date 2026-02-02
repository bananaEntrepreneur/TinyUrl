# TinyUrl Service

FastAPI-based high-performance URL shortening service.

## Quick Start

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd tiny_url
   ```

2. Copy the environment sample file:
   ```bash
   cp env-sample.txt .env
   ```
   
   Edit `.env` file with your desired configuration.

3. Start the services:
   ```bash
   docker-compose up -d
   ```

4. Access the application:
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health