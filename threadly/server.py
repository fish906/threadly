from flask import Flask, request, jsonify
from threadly.db import SessionLocal
from threadly import crud, utils, logger

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    # Validate payload structure
    if not data:
        logger.logger.warning("Received empty payload.")
        return jsonify({"error": "Invalid JSON payload"}), 400

    topic_name = data.get("topic")
    title = data.get("title")
    message = data.get("message")
    key = data.get("key")

    if not all([topic_name, title, message, key]):
        logger.logger.warning("Received incomplete payload for topic '%s'.", topic_name)
        return jsonify({"error": "Missing fields"}), 400

    # Sanitize inputs
    topic_name = utils.sanitize_input(topic_name)
    title = utils.sanitize_input(title)
    message = utils.sanitize_input(message)

    db = SessionLocal()
    try:
        topic = crud.get_topic_by_name(db, topic_name)
        if not topic:
            logger.logger.warning("Message rejected: Topic '%s' does not exist.", topic_name)
            return jsonify({"error": "Invalid topic"}), 403

        if not utils.verify_key(key, topic.key_hash):
            logger.logger.warning("Message rejected: Invalid key for topic '%s'.", topic_name)
            return jsonify({"error": "Invalid key"}), 403

        crud.add_message(db, topic.id, title, message)

        return jsonify({"status": "Message received"}), 200

    except Exception as e:
        logger.logger.error("Internal server error: %s", str(e))
        return jsonify({"error": "Internal server error"}), 500

    finally:
        db.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
