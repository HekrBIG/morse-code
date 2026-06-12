import random
import os
from flask import Flask, render_template_string, request, session

app = Flask(__name__)
app.secret_key = "morse_secret_key"

MORSE = {
    "A": ".-", "B": "-...", "C": "-.-.", "D": "-..",
    "E": ".", "F": "..-.", "G": "--.", "H": "....",
    "I": "..", "J": ".---", "K": "-.-", "L": ".-..",
    "M": "--", "N": "-.", "O": "---", "P": ".--.",
    "Q": "--.-", "R": ".-.", "S": "...", "T": "-",
    "U": "..-", "V": "...-", "W": ".--", "X": "-..-",
    "Y": "-.--", "Z": "--..",
    "0": "-----", "1": ".----", "2": "..---",
    "3": "...--", "4": "....-", "5": ".....",
    "6": "-....", "7": "--...", "8": "---..",
    "9": "----."
}

LETTERS = list(MORSE.keys())

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Morse Trainer</title>
    <style>
        body {
            background: #111;
            color: white;
            font-family: Arial;
            text-align: center;
            padding-top: 40px;
        }

        .box {
            background: #222;
            padding: 30px;
            border-radius: 15px;
            width: 400px;
            margin: auto;
        }

        input {
            padding: 10px;
            font-size: 20px;
            width: 80%;
            margin-top: 20px;
        }

        button {
            padding: 10px 20px;
            font-size: 18px;
            margin-top: 20px;
            cursor: pointer;
        }

        .morse {
            font-size: 48px;
            margin-top: 20px;
            letter-spacing: 10px;
        }

        .stats {
            margin-top: 20px;
        }

        .correct {
            color: lime;
        }

        .wrong {
            color: red;
        }

        .guide {
            margin-top: 20px;
            color: #aaa;
        }
    </style>
</head>
<body>

<div class="box">
    <h1>🧠 Morse Code Trainer</h1>

    <div class="morse">{{ question }}</div>

    <form method="POST">
        <input autofocus autocomplete="off" name="answer" placeholder="Type answer">
        <br>
        <button type="submit">Submit</button>
    </form>

    {% if result %}
        <h2 class="{{ result_class }}">{{ result }}</h2>
    {% endif %}

    <div class="stats">
        <p>Score: {{ score }}</p>
        <p>Lives: {{ lives }}</p>
    </div>

    <div class="guide">
        <p><b>.</b> = short beep</p>
        <p><b>-</b> = long beep</p>
    </div>

    <button onclick="playMorse('{{ morse_audio }}')">
        🔊 Play Morse
    </button>
</div>

<script>
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function playMorse(code) {
    const context = new (window.AudioContext || window.webkitAudioContext)();

    for (let char of code) {

        let duration = 100;

        if (char === ".") duration = 120;
        if (char === "-") duration = 350;

        const oscillator = context.createOscillator();
        const gain = context.createGain();

        oscillator.connect(gain);
        gain.connect(context.destination);

        oscillator.frequency.value = 650;
        oscillator.type = "sine";

        oscillator.start();

        await sleep(duration);

        oscillator.stop();

        await sleep(100);
    }
}
</script>

</body>
</html>


def new_question():
    letter = random.choice(LETTERS)
    return letter, MORSE[letter]

@app.route("/", methods=["GET", "POST"])
def home():

    if "score" not in session:
        session["score"] = 0
        session["lives"] = 3

    result = ""
    result_class = ""

    if "current_letter" not in session:
        letter, morse = new_question()
        session["current_letter"] = letter
        session["current_morse"] = morse

    if request.method == "POST":

        answer = request.form.get("answer", "").strip().upper()
        correct = session["current_letter"]

        if answer == correct:
            session["score"] += 1
            result = "✅ Correct!"
            result_class = "correct"
        else:
            session["lives"] -= 1
            result = f"❌ Wrong! Correct answer was {correct}"
            result_class = "wrong"

        if session["lives"] <= 0:
            final_score = session["score"]
            session.clear()

            return f"""
            <body style='background:#111;color:white;font-family:Arial;text-align:center;padding-top:100px;'>
                <h1>💀 Game Over</h1>
                <h2>Final Score: {final_score}</h2>
                <a href="/" style='color:cyan;font-size:24px;'>Play Again</a>
            </body>
            """

        letter, morse = new_question()
        session["current_letter"] = letter
        session["current_morse"] = morse

    return render_template_string(
        HTML,
        question=session["current_morse"],
        morse_audio=session["current_morse"],
        score=session["score"],
        lives=session["lives"],
        result=result,
        result_class=result_class
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
