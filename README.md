# PJATK Notifier

**Gakko Reminder vol 2** is a lightweight app that helps students stay organized by:

- Authenticating with your educational platform (via ADFS)
- Scraping upcoming homework and assignments
- Parsing due dates directly from task detail pages
- Publishing them straight to Google Calendar or any preferred third-party calendar app
- Runs automatically on a scheduled cron job inside the container

### [To run the app:](#how-to-run-it-on-your-local-machine)
No need to clone the repository, just run the Docker container:

---

## How It Works

The app follows a clean, extensible command pipeline that processes steps in order:

1. Authorization – Logs in using an ADFS form
2. Scraping – Gathers tasks from the dashboard and extracts due dates directly from detail HTML
3. Publishing – Sends tasks to Google Calendar (or any compatible calendar)

---

## Architecture and Design Principles

**Gakko Reminder** is built with simplicity, extensibility, and testability in mind. It uses:

- Command Pattern – Each step in the flow is encapsulated in a dedicated command class implementing a common interface.
- Pipeline Execution – Commands are executed in sequence using a lightweight pipeline structure.
- Context Injection – Configuration, session, and shared state are passed through a centralized context object.
- Separation of Concerns – Responsibilities are clearly separated using abstract interfaces for commands and protocols for repositories and publishers.
- Pure Python – The application avoids heavy frameworks, relying instead on a minimal and composable set of libraries.

---

## Technology Stack

| Tool                        | Purpose                                |
|----------------------------|----------------------------------------|
| requests                   | HTTP communication with Gakko         |
| beautifulsoup4             | HTML parsing                           |
| pydantic                   | Data modeling and validation           |
| google-api-python-client   | Google Calendar integration            |
| pytest, factory_boy        | Unit testing & test factories          |
| jinja2                     | HTML templating for mock fixtures      |
| mypy, coverage, ruff       | Static typing, linting & coverage      |

---

## How to run it on your local machine?

To successfully run `gakko-reminder`, make sure you have the following:

### 1. `.env` file with your login credentials

```env
GAKKO_CLIENT_ID=your-adfs-client-id
GAKKO_USERNAME=your-username@pjwstk.edu.pl
GAKKO_PASSWORD=your-password
```

### 2. `token.json` – Google Calendar authorization token

You don’t need `credentials.json` in the container. You only need the `token.json` file which can be generated once using the following script:

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

Note: For production, it's recommended to host the app on Google Cloud (GCE/Cloud Run) to avoid token expiration issues.

---

### 3. Run the Docker container

```bash
docker run --rm \
  -v $PWD/.env:/app/.env \
  -v $PWD/token.json:/app/token.json \
  --platform linux/arm64 \
  kkaarroollm/gakko-reminder:v2.0.0  # or use `:latest`
```

> **Note:**
> This image is **multi-platform** (supports both `linux/amd64` and `linux/arm64`).  
> Use the `--platform` flag to ensure compatibility with your machine.

> **Tip:**
> For the cloud deployment use `--platform linux/amd64` to avoid issues with `arm64` images.


### 4. Run the script inside the container
```bash
docker exec -it <container_id> uv run python src/main.py
```

---

## Test Coverage

| File                                             | Stmts | Miss | Cover | Missing              |
|--------------------------------------------------|-------|------|--------|----------------------|
| src/auth/command.py                              | 23    | 0    | 100%   |                      |
| src/auth/models.py                               | 13    | 0    | 100%   |                      |
| src/core/command.py                              | 6     | 1    | 83%    | 9                    |
| src/core/command_context.py                      | 21    | 2    | 90%    | 20, 26               |
| src/core/config.py                               | 16    | 0    | 100%   |                      |
| src/core/exceptions.py                           | 4     | 0    | 100%   |                      |
| src/core/pipeline.py                             | 13    | 0    | 100%   |                      |
| src/core/protocols.py                            | 9     | 0    | 100%   |                      |
| src/integrations/google/calendar_repository.py   | 27    | 27   | 0%     | 1–48                 |
| src/integrations/google/mock_calendar.py         | 16    | 0    | 100%   |                      |
| src/integrations/google/models.py                | 59    | 7    | 88%    | 39–44, 83, 118       |
| src/integrations/google/publisher.py             | 18    | 0    | 100%   |                      |
| src/main.py                                      | 22    | 22   | 0%     | 1–46                 |
| src/tasks/commands.py                            | 16    | 0    | 100%   |                      |
| src/tasks/dashboard.py                           | 18    | 0    | 100%   |                      |
| src/tasks/details.py                             | 24    | 0    | 100%   |                      |
| src/tasks/models.py                              | 15    | 0    | 100%   |                      |
| **TOTAL**                                        | 320   | 59   | 82%    |                      |

---

## Project Structure

```
.
├── src/
│   ├── auth/              # Login & ADFS auth
│   ├── core/              # Pipeline logic, base classes, config
│   ├── tasks/             # Scraping tasks logic
│   └── integrations/      # Google Calendar API integration
├── tests/
│   ├── fixtures/          # Factories & HTML templates
│   ├── core/, tasks/, ... # Unit & integration tests
├── main.py                # App entrypoint
├── entrypoint.sh          # Cron-based entrypoint to start the app on schedule
├── Dockerfile             # Docker config
├── token.json             # GCP token
```

---
## Author

Made with beer **kkaarroollm**.  
GitHub: [https://github.com/kkaarroollm](https://github.com/kkaarroollm)

---

## License

MIT © 2024