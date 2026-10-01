# Voice Order

A Flask + SQLite order-taking app for a restaurant. A customer speaks an order, Claude works out which menu items and quantities they asked for, the customer confirms, and the order is saved with a total price.

Right now it runs through a browser microphone. Taking orders over a phone call (with Twilio) is the next step.

## Features

- Speak an order in the browser and see it as text
- Claude matches what was said to the live menu, even when the speech-to-text mishears a word
- A confirmation step shows what was understood before anything is saved
- Orders are saved to SQLite with their items, and an order total is calculated from menu prices
- Unknown menu items and empty requests return clear errors, and a failed order never leaves a half-saved order behind

## Built with

- Python, Flask, SQLite3
- Anthropic API (Claude Haiku 4.5) to turn spoken text into structured items
- Browser speech recognition (Chrome or Edge) for speech-to-text

## Run locally

```
pip install -r requirements.txt
```

Create a `.env` file in this folder with your Anthropic API key:

```
ANTHROPIC_API_KEY=your-key-here
```

Then start the app:

```
python app.py
```

Open http://127.0.0.1:5000/talk in Chrome, click the button, allow the microphone, and say an order such as "two chicken tikka masala and one sheek kebab starter".

## How it works

1. The page turns your speech into text and sends it to `POST /parse`.
2. `parse_order.py` sends that text and the current menu to Claude, which returns a JSON list of `{name, quantity}`.
3. The page shows the items and asks "Is this right?".
4. On Confirm, the page sends the items to `POST /order`, which saves the order and returns the order id and total.

### Routes

- `GET /` health check
- `GET /talk` the voice ordering page
- `POST /parse` reads an order from text and returns the items, without saving
- `POST /order` saves an order, from either `{"text": "..."}` or `{"items": [...]}`

### Database

- `menu_items` the menu and prices
- `orders` one row per order, with a timestamp
- `order_items` the items in each order and their quantities

The menu is seeded on first run. The order total is `sum(price * quantity)` across an order's items.

## Known limitations (next steps)

- Phone calls are not supported yet. The plan is Twilio, with the app reading the order back and listening for a spoken yes or no
- Browser speech recognition only works in Chrome and Edge, and can mishear words
- Needs hosting on an always-on server with a production web server before real use
- No staff login, rate limiting or kitchen display yet
- No way to edit the menu except in the database
