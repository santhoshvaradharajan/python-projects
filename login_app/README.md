# Login & Registration System

A Flask + SQLite app demonstrating user registration, login, and session-based authentication.

## Features

- Register a new user
- Log in / log out
- Session-protected home page

## Built with

- Python, Flask, SQLite3

## Run locally

```
pip install flask
python app.py
```

Then open http://127.0.0.1:5000

## Known limitations (next improvements)

- Passwords are stored in plain text — a good next step is hashing them with `werkzeug.security` (`generate_password_hash` / `check_password_hash`).
- The secret key is hardcoded — should be moved to an environment variable before this goes anywhere real.
