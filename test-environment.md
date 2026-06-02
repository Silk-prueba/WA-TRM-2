# WA-TRM-2 — Development Guide & Environment Setup

## Environment Overview

| Environment | Branch | Server | Backend | WAHA |
|-------------|--------|--------|---------|------|
| **Local** | any `feature/xxx` | Your machine | `localhost:8000` | `localhost:3000` |
| **Staging** | `develop` | Hostinger `/opt/wa-trm-dev` | `2.25.145.47:8001` | `2.25.145.47:3001` |
| **Production** | `master` | Hostinger `/opt/wa-trm` | `2.25.145.47:8000` | `2.25.145.47:3000` |

---

## Git Workflow

```
feature/xxx  →  develop  →  master
   (local)      (staging)   (production)
```

1. Always branch off `develop` when starting new work
2. Open PRs targeting `develop` (default branch on GitHub)
3. Test on staging before promoting to `master`
4. To release to production: open a PR from `develop` → `master`

---

## Local Environment

### Configuration file
Use `.env.local` at the project root.

```env
WAHA_API_URL=http://localhost:3000
WAHA_API_KEY=123
WAHA_SESSION=default
TEST_CHAT_ID=573214837559@c.us   # your personal number for testing
SCHEDULE_TIME=08:00
TZ=America/Bogota
BACKEND_PORT=8000
WAHA_PORT=3000
```

### Start locally

```bash
# 1. Create your feature branch
git checkout develop
git checkout -b feature/your-change-name

# 2. Start containers with local env
docker compose --env-file .env.local up -d

# 3. Verify it's running
curl http://localhost:8000/
```

### Trigger a manual send

```bash
curl -X POST "http://localhost:8000/api/trigger"
```

### Update scheduler time on the fly

```bash
curl -X POST "http://localhost:8000/api/config?hour=9&minute=30"
```

### View local logs

```bash
docker compose logs backend -f
```

### When you're done with your changes

```bash
git add .
git commit -m "feat: describe your change"
git push origin feature/your-change-name
# Then open a PR on GitHub targeting develop
```

---

## Staging Environment (Develop on Hostinger)

### Configuration file
Use `.env.dev` at `/opt/wa-trm-dev/` on the server.

```env
WAHA_API_URL=http://waha-dev:3000
WAHA_API_KEY=123
WAHA_SESSION=default
TEST_CHAT_ID=TEST_GROUP_ID@g.us   # test group only — never production
SCHEDULE_TIME=08:00
TZ=America/Bogota
BACKEND_PORT=8001
WAHA_PORT=3001
```

### Start staging for the first time

```bash
# On the server via Hostinger terminal
cd /opt/wa-trm-dev
docker compose -f docker-compose.dev.yml --env-file .env.dev up -d
```

### Deploy changes to staging

```bash
cd /opt/wa-trm-dev
git pull origin develop
docker compose -f docker-compose.dev.yml restart backend-dev
```

### Test on staging

```bash
# Manual trigger
curl -X POST "http://localhost:8001/api/trigger"

# Update schedule time
curl -X POST "http://localhost:8001/api/config?hour=9&minute=30"

# View logs
docker compose -f docker-compose.dev.yml logs backend-dev --tail 30
```

### WAHA Dashboard (staging)
Open in your browser:
```
http://2.25.145.47:3001/dashboard
```
> ⚠️ Scan the QR code with a **test WhatsApp number only** — never with the production number.

---

## Production Environment (Master on Hostinger)

### Deploy to production

```bash
# 1. On GitHub: merge PR develop → master
# 2. On the server:
cd /opt/wa-trm
git pull origin master
docker compose restart backend
```

> ⚠️ **Never run `docker compose down` in production** — it disconnects the WhatsApp session.
> Always use `docker compose restart backend` instead.

### Update chat ID or schedule time without restarting

```bash
# Update schedule time
curl -X POST "http://localhost:8000/api/config?hour=7&minute=0"

# Update chat ID and schedule time
curl -X POST "http://localhost:8000/api/config?chat_id=NEW_ID@g.us&hour=7&minute=0"
```

### View production logs

```bash
cd /opt/wa-trm
docker compose logs backend --tail 30
```

---

## Port Reference

| Service | Production | Staging |
|---------|------------|---------|
| Backend API | `:8000` | `:8001` |
| WAHA Dashboard | `:3000` | `:3001` |

---

## Golden Rules

1. **Never** commit directly to `master`
2. **Never** run `docker compose down` in production
3. **Always** test on staging before promoting to production
4. **Never** commit `.env`, `.env.local`, or `.env.dev` to GitHub
5. The `TEST_CHAT_ID` in staging must be a test group — never the real production group