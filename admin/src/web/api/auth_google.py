from flask import Blueprint, request, jsonify, redirect, current_app, session
from flask_jwt_extended import create_access_token, set_access_cookies,unset_jwt_cookies
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import requests as req
import secrets
from urllib.parse import quote, unquote

from core.auth import repository as user_repo

auth_google_bp = Blueprint("auth_google_bp", __name__, url_prefix="/api/auth/google")


@auth_google_bp.get("/login")
def google_login():
    """
    Redirige al usuario a Google.
    """
    google_client_id = current_app.config["GOOGLE_CLIENT_ID"]
    redirect_uri = current_app.config["GOOGLE_REDIRECT_URI"]

    if not google_client_id or not redirect_uri:
        return jsonify({"error":"server_misconfigured","detail":"GOOGLE_CLIENT_ID or GOOGLE_REDIRECT_URI missing"}), 500
    raw_next = request.args.get("next") or "/"
    try:
        next_path = unquote(raw_next)
    except Exception:
        next_path = "/"
    session["oauth_next"] = next_path

    state = secrets.token_urlsafe(16)
    session["oauth_state"] = state

    auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={google_client_id}"
        f"&redirect_uri={redirect_uri}"
        "&response_type=code"
        "&scope=openid%20email%20profile"
        "&access_type=online"
        f"&state={state}"
    )
    current_app.logger.debug("Google login URL: %s", auth_url)
    return redirect(auth_url)

@auth_google_bp.get("/callback")
def google_callback():
    code = request.args.get("code")
    state = request.args.get("state")

    if not code:
        return jsonify({"error": "authorization_failed", "detail": "missing code"}), 400

    expected_state = session.pop("oauth_state", None)
    if expected_state is None or state != expected_state:
        return jsonify({"error": "invalid_state"}), 400

    google_client_id = current_app.config.get("GOOGLE_CLIENT_ID")
    google_client_secret = current_app.config.get("GOOGLE_CLIENT_SECRET")
    redirect_uri = current_app.config.get("GOOGLE_REDIRECT_URI")

    if not (google_client_id and google_client_secret and redirect_uri):
        return jsonify({"error": "server_misconfigured", "detail": "missing GOOGLE_CLIENT_ID/SECRET/REDIRECT_URI"}), 500

    token_resp = req.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": google_client_id,
            "client_secret": google_client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        },
        timeout=10,
    )

    try:
        token_res = token_resp.json()
    except Exception:
        return jsonify({"error": "token_exchange_failed", "detail": "invalid token response"}), 400

    if token_res.get("error"):
        return jsonify({"error": "token_exchange_failed", "detail": token_res.get("error_description") or token_res.get("error")}), 400

    id_token_str = token_res.get("id_token")
    if not id_token_str:
        return jsonify({"error": "token_exchange_failed", "detail": "no id_token returned"}), 400

    try:
        info = id_token.verify_oauth2_token(
            id_token_str,
            google_requests.Request(),
            google_client_id,  
        )
    except Exception as e:
        return jsonify({"error": "invalid_google_token", "detail": str(e)}), 401

    email = info.get("email")
    name = info.get("name") or ""
    picture = info.get("picture")
    sub = info.get("sub")  

    if not email:
        return jsonify({"error": "no_email", "detail": "Google profile did not return email"}), 400

    
    try:
        user = user_repo.upsert_user_from_google(email, name, picture)
    except Exception as e:
        current_app.logger.exception("user upsert failed")
        return jsonify({"error": "user_upsert_failed", "detail": str(e)}), 500

    try:
        access_token = create_access_token(identity=str(user.id))

        next_path = session.pop("oauth_next", "/") or "/"
        frontend = current_app.config.get("FRONTEND_ORIGIN", "http://127.0.0.1:5173")
        redirect_url = f"{frontend}/auth/callback?next={quote(next_path)}"

        resp = redirect(redirect_url)
        set_access_cookies(resp, access_token)
        return resp
    except Exception as e:
        return jsonify({"msg": str(e)}), 500