# WhatsApp Automation Prototype

This project is a dockerized WhatsApp automation prototype using Python (FastAPI) and WAHA (WhatsApp HTTP API).

## Prerequisites

- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/)
- Python 3.11+ (optional, for running scripts outside of Docker)

## Setup and Usage

1. **Environment Setup**
   A `.env` file is included with sensible defaults. You can modify ports or the `TEST_CHAT_ID` as needed. The `TEST_CHAT_ID` defines where your test messages will be sent.

2. **Start the containers**
   ```bash
   docker-compose up -d --build
   ```
   This will start both the FastAPI backend (`http://localhost:8000`) and the WAHA server (`http://localhost:3000`).

3. **Configure the Dashboard & Authenticate**
   - Open your browser and go to the WAHA Dashboard: [http://localhost:3000/dashboard](http://localhost:3000/dashboard)
   - Click the gear icon (Settings) in the top right. Enter `123` in the **API Key** field and save.
   - The `default` session should be visible and in the `SCAN_QR_CODE` status.
   - Click the camera icon on the session to start it and scan the QR code with your WhatsApp app (Linked Devices).

4. **Finding Chat IDs**
   Once your session status changes to `WORKING`, you can list your recent chats or groups to find the ID of the person/group you want to interact with:
   
   To list recent chats:
   ```bash
   docker-compose exec backend python backend/list_chats.py
   ```
   
   To list all your groups:
   ```bash
   docker-compose exec backend python backend/list_groups.py
   ```
   
   Copy the desired ID and update the `TEST_CHAT_ID` variable in your `.env` file. (Remember to restart the backend container if you change the `.env` file: `docker-compose up -d`)

5. **Verify the connection**
   Run the test script to send a message to the `TEST_CHAT_ID`:
   ```bash
   docker-compose exec backend python backend/test_connection.py
   ```

6. **Test Webhooks**
   Send a message to your connected WhatsApp number from another phone. You should see the webhook event logged in your backend container logs:
   ```bash
   docker-compose logs -f backend
   ```

## Project Structure

- `docker-compose.yml`: Container orchestration and environment mapping.
- `backend/main.py`: FastAPI entry point.
- `backend/api/routes.py`: Contains the webhook endpoint `POST /api/webhook`.
- `backend/services/waha.py`: Helper class to interact with WAHA via HTTP requests.
- `backend/core/config.py`: Environment variable configuration logic using Pydantic.
- `backend/test_connection.py`, `list_chats.py`, `list_groups.py`: Utility scripts for testing and retrieving WAHA data.
