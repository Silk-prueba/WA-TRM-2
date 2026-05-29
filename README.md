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
   yes
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

6. **Send today's exchange rate message manually**
   Generate today's exchange rate message and send it immediately to the `TEST_CHAT_ID`:
   ```bash
   docker-compose exec backend python backend/test_send_rate.py
   ```
   The script will print the message to the console before sending so you can verify the content. This is useful for testing the full flow without waiting for the scheduled time.

7. **Test Webhooks**
   Send a message to your connected WhatsApp number from another phone. You should see the webhook event logged in your backend container logs:
   ```bash
   docker-compose logs -f backend
   ```

## Daily Exchange Rate Automation

The backend includes an automated job that fetches the latest currency exchange rate and sends a WhatsApp message daily.

### Configuration

You can configure the behavior of the daily message using variables in your `.env` file:

- `SCHEDULE_TIME`: The time of day to send the message in 24-hour format (e.g., `08:00` for 8 AM).
- `TZ`: The timezone used for the schedule (e.g., `America/Bogota`).
- `TEST_CHAT_ID`: The WhatsApp ID (user or group) where the message will be sent.

By default, the automation fetches the exchange rate from **USD** to **COP**. To change these, you can modify `base_currency` and `target_currency` inside `backend/core/config.py`.

### Running the Automation

The automation is tied to the lifecycle of the FastAPI backend container and runs automatically when the container starts.

1. Configure your `.env` variables.
2. Restart the backend to apply changes:
   ```bash
   docker-compose up -d --build
   ```
3. Ensure the WAHA session is connected and active (status `WORKING`). The message will be automatically dispatched at the configured `SCHEDULE_TIME`.

## Project Structure

- `docker-compose.yml`: Container orchestration and environment mapping.
- `backend/main.py`: FastAPI entry point.
- `backend/api/routes.py`: Contains the webhook endpoint `POST /api/webhook`.
- `backend/services/waha.py`: Helper class to interact with WAHA via HTTP requests.
- `backend/core/config.py`: Environment variable configuration logic using Pydantic.
- `backend/test_connection.py`: Sends a plain test message to verify the WAHA connection.
- `backend/test_send_rate.py`: Generates today's exchange rate message and sends it to WhatsApp immediately.
- `backend/list_chats.py`, `backend/list_groups.py`: Utility scripts for retrieving chat and group IDs from WAHA.
