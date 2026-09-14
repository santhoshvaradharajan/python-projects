# OTP Verification Demo

A small Flask app demonstrating one-time-password (OTP) generation and verification using sessions.

## How it works

- Visiting the homepage generates a random 5-digit OTP (currently printed to the console instead of sent via SMS/email, for demo purposes)
- Enter the code on the verify page to confirm it matches

## Built with

- Python, Flask

## Run locally

```
pip install flask
python app.py
```

Then open http://127.0.0.1:5000 and check your terminal for the generated OTP.
