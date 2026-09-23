from flask import Flask, render_template, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import re
import os

app = Flask(__name__)

# کلیلی سڕی بۆ سێشنەکان (لە ژینگەی ڕاستەقینە لە .env دابنرێت)
app.secret_key = os.urandom(32)
app.permanent_session_lifetime = timedelta(days=7)

# بنکەدراوەی تاقیکاری بەکارهێنەران (وشەی نهێنی پارێزراو بە هاش)
USERS_DB = {
    "danyal": {
        "email": "danyal@app.io",
        "name": "Danyal Ismail",
        "password_hash": generate_password_hash("Admin@2026")
    }
}

EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({
            "status": "error",
            "message": "داواکارییەکی نادروستە (هیچ داتایەک نەدۆزرایەوە)"
        }), 400

    identifier = data.get("identifier", "").strip()
    password = data.get("password", "").strip()
    remember_me = data.get("remember_me", False)

    # پشکنینی سەرەتایی فۆرم
    if not identifier or not password:
        return jsonify({
            "status": "error",
            "message": "تکایە هەردوو خانەی ناسنامە و وشەی نهێنی پڕبکەرەوە"
        }), 422

    # گەڕان بەپێی ناوی بەکارهێنەر یان ئیمەیڵ
    user_found = None
    target_username = None

    for username, details in USERS_DB.items():
        if username.lower() == identifier.lower() or details["email"].lower() == identifier.lower():
            user_found = details
            target_username = username
            break

    # سەلماندنی ناسنامە
    if not user_found or not check_password_hash(user_found["password_hash"], password):
        return jsonify({
            "status": "error",
            "message": "ناوی بەکارهێنەر یان وشەی نهێنی هەڵەیە!"
        }), 401

    # سازدانی سێشن
    session.permanent = bool(remember_me)
    session["user"] = {
        "username": target_username,
        "name": user_found["name"],
        "email": user_found["email"]
    }

    return jsonify({
        "status": "success",
        "message": f"بەخێربێیتەوە {user_found['name']}!",
        "redirect_url": "/dashboard"
    }), 200


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return "تکایە سەرەتا بچۆ ژوورەوە", 403
    return f"<h1>داشبۆردی دانیال</h1><p>بەخێربێیت {session['user']['name']}</p>"


@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"status": "success", "message": "بە سەرکەوتوویی دەرچوویت"}), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
