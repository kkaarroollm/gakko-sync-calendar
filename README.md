# PJATK Notifier

**Gakko Reminder vol 2** is a lightweight app that helps students stay organized by:

- Authenticating with your educational platform (via ADFS + Selenium)
- Scraping upcoming homework and assignments from the dashboard
- Parsing due dates directly from task detail pages
- Publishing them straight to Google Calendar or any preferred third-party calendar app
- Runs automatically on a scheduled cron job inside a Docker container

### [To run the app:](#how-to-run-it-on-your-local-machine)
No need to clone the repository, just run the Docker container.

---

## How It Works

The app follows a clean, extensible command pipeline that processes steps in order:

1. **Authorization** -- Opens a headless browser, navigates to ADFS and submits credentials via Selenium
2. **Scraping** -- Gathers tasks from the dashboard and extracts due dates from detail pages using JavaScript execution with regex fallback
3. **Publishing** -- Sends tasks to Google Calendar (or any compatible calendar)

---

## Architecture and Design Principles

**Gakko Reminder** is built with simplicity, extensibility, and testability in mind. It uses:

- **Command Pattern** -- Each step in the flow is encapsulated in a dedicated command class implementing a common interface.
- **Pipeline Execution** -- Commands are executed in sequence using a lightweight pipeline structure.
- **Context Injection** -- Configuration, the Selenium WebDriver, and shared state are passed through a centralized context object.
- **Separation of Concerns** -- Responsibilities are clearly separated using abstract interfaces for commands and protocols for repositories and publishers.
- **Pure Python** -- The application avoids heavy frameworks, relying instead on a minimal and composable set of libraries.

---

## Technology Stack

| Tool                        | Purpose                                |
|-----------------------------|----------------------------------------|
| selenium                    | Browser automation & HTML scraping     |
| pydantic                    | Data modeling and validation           |
| google-api-python-client    | Google Calendar integration            |
| pytest, factory_boy         | Unit testing & test factories          |
| jinja2                      | HTML templating for mock fixtures      |
| mypy, coverage, ruff        | Static typing, linting & coverage      |

---

## How to run it on your local machine?

To successfully run `gakko-reminder`, make sure you have the following:

### 1. `.env` file with your login credentials

```env
GAKKO_CLIENT_ID=your-adfs-client-id
GAKKO_USERNAME=your-username@pjwstk.edu.pl
GAKKO_PASSWORD=your-password
```

### 2. `token.json` -- Google Calendar authorization token

You don't need `credentials.json` in the container. You only need the `token.json` file which can be generated once using the following script:

```python
from google_auth_oauthlib.flow import InstalledAppFlow

flow = InstalledAppFlow.from_client_secrets_file(
    "credentials.json",
    scopes=["https://www.googleapis.com/auth/calendar"]
)
creds = flow.run_local_server(port=0)

with open("token.json", "w") as token_file:
    token_file.write(creds.to_json())
```

> 1. Download `credentials.json` from the [Google Calendar API Quickstart](https://developers.google.com/calendar/quickstart/python)
> 2. Run the script once locally to generate `token.json`
> 3. Copy `token.json` into the container `/app/` directory

Note: It’s recommended to use a token in production mode, so the TTL never expires.

---

### 3. Run the Docker container

```bash
docker run --rm \
  -v $PWD/.env:/app/.env \
  -v $PWD/token.json:/app/token.json \
  kkaarroollm/gakko-reminder:latest
```

### 4. Run the script inside the container
```bash
docker exec -it <container_id> uv run python src/main.py
```

---

## CI/CD

A Docker image is automatically built and pushed to **Docker Hub** whenever a new GitHub release is published.

| Image | Tags |
|-------|------|
| `kkaarroollm/gakko-reminder` | `latest`, release version (e.g. `v2.1.0`) |

Required repository secrets: `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`.

---

## Project Structure

```
.
├── src/
│   ├── auth/              # Login & ADFS auth (Selenium)
│   ├── core/              # Pipeline logic, base classes, config
│   ├── tasks/             # Dashboard & detail page scraping
│   └── integrations/      # Google Calendar API integration
├── tests/
│   ├── fixtures/          # Factories & HTML templates
│   ├── core/, tasks/, ... # Unit & integration tests
├── src/main.py            # App entrypoint
├── entrypoint.sh          # Cron-based entrypoint
├── Dockerfile             # Docker config (headless Chrome)
```

---
## Author

Made with beer **kkaarroollm**.
GitHub: [https://github.com/kkaarroollm](https://github.com/kkaarroollm)

---

## License

MIT © 2024
