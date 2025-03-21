from flask import Flask, request, jsonify, Response
import sqlite3
import json
import time

app = Flask(__name__)

# Initialize the database
def init_db():
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS chat_history 
                 (chat_id TEXT, sender TEXT, message TEXT, timestamp REAL)''')
    conn.commit()
    conn.close()

init_db()

# Function to store messages in the database
def save_message(chat_id, sender, message):
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute("INSERT INTO chat_history VALUES (?, ?, ?, ?)", (chat_id, sender, message, time.time()))
    conn.commit()
    conn.close()

# Function to retrieve chat history
def get_chat_history(chat_id):
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute("SELECT sender, message FROM chat_history WHERE chat_id=? ORDER BY timestamp", (chat_id,))
    history = c.fetchall()
    conn.close()
    return [{"sender": row[0], "message": row[1]} for row in history]

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    chat_id = data.get("chat_id", "default")
    prompt = data.get("prompt", "")

    save_message(chat_id, "user", prompt)

    # Simulated streaming response
    def generate():
        response_text = f"I'm a bot! You said: {prompt}"  
        save_message(chat_id, "bot", response_text)
        for word in response_text.split():
            yield word + " "
            time.sleep(0.1)

    return Response(generate(), content_type="text/plain")

@app.route("/get_memory", methods=["POST"])
def get_memory():
    data = request.get_json()
    chat_id = data.get("chat_id", "default")
    return jsonify({"chat_history": get_chat_history(chat_id)})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
