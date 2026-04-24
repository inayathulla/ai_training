"""
Flask HTTP layer — exposes the document agent as a REST API.
"""

import os

from flask import Flask, jsonify, request

from agent_core import get_executor

app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health():
    """Liveness check. Used by Docker healthchecks and load balancers."""
    return jsonify({"status": "ok"})


@app.route("/chat", methods=["POST"])
def chat():
    """Accept a user message, run the agent, return the answer."""
    data = request.get_json(silent=True) or {}
    user_message = data.get("message")

    if not user_message:
        return jsonify({"error": "Missing 'message' field in request body."}), 400

    try:
        executor = get_executor()
        result = executor.invoke({"input": user_message})
        return jsonify({"response": result["output"]})
    except Exception as exc:
        # Never leak internal stack traces in production; training scope keeps it simple.
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    # host=0.0.0.0 is required so the process is reachable from outside the container.
    app.run(host="0.0.0.0", port=port, debug=False)
