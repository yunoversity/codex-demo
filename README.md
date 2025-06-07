# Customer Ticketing System

This repository contains a simple HTTP server that stores customer ticket submissions in a JSON file. Incoming tickets are automatically classified using basic keyword rules, and a canned response is saved with each ticket.

## Usage

Run the server:

```bash
python3 ticket_server.py
```

Open `http://localhost:8000/` in a browser to access the web UI.

Submit a ticket with `curl`:

```bash
curl -X POST http://localhost:8000/tickets \
    -H 'Content-Type: application/json' \
    -d '{"user": "alice", "description": "I found a bug in your app"}'
```

List tickets:

```bash
curl http://localhost:8000/tickets
```

Retrieve a specific ticket:

```bash
curl http://localhost:8000/tickets/1
```

## ChatGPT Classification

Actual calls to OpenAI APIs are not performed because the environment blocks outbound network requests. Instead, the server uses simple keyword heuristics to classify tickets as a **bug report**, **feature request**, or **support** issue and generates a canned response based on that classification.
