from flask import Flask, jsonify, render_template, request
from backend.knowledge_manager import initialize_knowledge_db, add_knowledge, get_all_knowledge, delete_knowledge
from backend.chatbot import generate_response
from backend.threat_detection import analyze_message

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024
initialize_knowledge_db()

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "app": "ZILDA AI"})

@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()
    if not message:
        return jsonify({"error": "Please enter a security question."}), 400
    if len(message) > 3000:
        return jsonify({"error": "Message is too long. Use fewer than 3000 characters."}), 400
    try:
        return jsonify({"assistant": "ZILDA AI", **generate_response(message)})
    except Exception:
        app.logger.exception("Chat request failed")
        return jsonify({"error": "ZILDA could not process this question. Please try again."}), 500

@app.post("/api/analyze")
def analyze():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()
    if not message:
        return jsonify({"error": "Paste a message to analyze."}), 400
    if len(message) > 10000:
        return jsonify({"error": "Message is too long."}), 400
    return jsonify(analyze_message(message))

@app.get("/api/knowledge")
def view_knowledge():
    return jsonify(get_all_knowledge())

@app.post("/api/knowledge")
def create_knowledge():
    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "")).strip()
    category = str(data.get("category", "")).strip()
    content = str(data.get("content", "")).strip()
    if not title or not category or not content:
        return jsonify({"error": "Title, category and content are required."}), 400
    if len(title) > 150 or len(category) > 80 or len(content) > 5000:
        return jsonify({"error": "One or more fields exceed the allowed length."}), 400
    item_id = add_knowledge(title, category, content)
    return jsonify({"success": True, "id": item_id, "message": "Information saved successfully."}), 201

@app.delete("/api/knowledge/<int:item_id>")
def remove_knowledge(item_id):
    if not delete_knowledge(item_id):
        return jsonify({"error": "Article not found."}), 404
    return jsonify({"success": True, "message": "Article deleted."})

@app.errorhandler(413)
def too_large(_error):
    return jsonify({"error": "Request is too large."}), 413

if __name__ == "__main__":
    print("Starting ZILDA AI...")
    app.run(host="127.0.0.1", port=5000, debug=False)
