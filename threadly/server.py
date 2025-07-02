from flask import Flask, request, jsonify
from threadly.db import SessionLocal
from threadly import crud, utils, logger
from threadly.tools import rate_limiter
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)

def get_real_ip():
    x_forwarded_for = request.headers.get('X-Forwarded-For', '')
    if x_forwarded_for:
        # The first IP in the list is the client's IP
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.remote_addr
    return ip


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

        if not topic.key_hash:
            logger.logger.error(f"Topic '{topic_name}' has no key hash set.")
            return jsonify({"error": "Topic key not set"}), 500
        
        try:
            if not utils.verify_key(key, topic.key_hash):
                logger.logger.warning("Message rejected: Invalid key for topic '%s'.", topic_name)
                return jsonify({"error": "Invalid key"}), 403
            
        except Exception as e:
            logger.logger.error(f"Key verification failed for topic '{topic_name}': {e}")
            return jsonify({"error": "Invalid key"}), 403

        user_ip = get_real_ip()

        if rate_limiter.is_rate_limited(db, user_ip, limit=5, window_minutes=1):
            logger.logger.warning(f"Rate limit exceeded for IP: {user_ip}")
            return jsonify({"error": "Too many requests"}), 429
        
        created_message = crud.add_message(db, topic.id, title, message)

        try:
            crud.log_ip_for_message(db, created_message.id, user_ip)
        except Exception as e:
            logger.logger.error(f"Failed to log IP: {e}")


        return jsonify({"status": "Message received"}), 200

    except Exception as e:
        logger.logger.error("Internal server error: %s", str(e))
        return jsonify({"error": "Internal server error"}), 500

    finally:
        db.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
