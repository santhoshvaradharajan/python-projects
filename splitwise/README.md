# Splitwise Clone

A Flask + SQLite expense-splitting app, inspired by Splitwise. Create a group, add members, log shared expenses, and see who owes who.

## Features

- User registration and login (passwords hashed with `werkzeug.security`)
- Create groups and add members to them
- Add expenses to a group — the cost is split evenly across all members
- Per-group balance view showing how much each member has overpaid or underpaid

## Built with

- Python, Flask, SQLite3

## Run locally

```
pip install flask werkzeug
python app.py
```

Then open http://127.0.0.1:5000, register an account, and create a group.

## How it works

- `users` — registered accounts
- `groups` / `group_members` — groups and who belongs to them
- `expenses` — each logged expense, who paid, and how much
- `expense_splits` — each member's share of an expense

Each member's balance is `total they paid - total they owe`, computed by summing `expenses` and `expense_splits` per group.

## Known limitations (next steps)

- The secret key is hardcoded — should move to an environment variable before this goes anywhere real
- Expenses are always split evenly — unequal splits would be a good next feature
- No "settle up" flow yet to clear a balance once someone pays another member back
