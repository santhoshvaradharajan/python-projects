from flask import Flask, request, render_template, session
import random

app = Flask(__name__)
app.secret_key = "your_secret_key"


@app.route("/")
def index():
    otp = random.randint(10000, 99999)
    session["otp"] = otp
    print("Generated otp:", otp)
    return render_template("index.html")

@app.route("/verify", methods = ["GET", "POST"])
def verify():
    entered = request.form.get("code")
    try:
        entered = int(entered)
    except:
       return "invalid input"    
    if entered == session.get("otp"):
       return "verified✌️"
    else:
        return "wrong code!! try again"

if __name__ == "__main__":
    app.run(debug = True)

    