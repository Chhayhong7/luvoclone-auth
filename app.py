from flask import Flask, redirect, request, session, jsonify
import requests
import os

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

FB_APP_ID = os.getenv("FB_APP_ID")
FB_APP_SECRET = os.getenv("FB_APP_SECRET")
FB_VERIFY_TOKEN = os.getenv("FB_VERIFY_TOKEN")
REDIRECT_URI = "https://luvoclone-auth-1.onrender.com/auth/callback"  # Must match your Facebook app settings

# 1. Root route to confirm the server is live
@app.route('/')
def home():
    return "Hello Supreme Ruler! LuvoClone Auth is live!"

# 2. Facebook login redirect
@app.route('/login')
def login():
    return redirect(
        f"https://www.facebook.com/v17.0/dialog/oauth?client_id={FB_APP_ID}&redirect_uri={REDIRECT_URI}&scope=pages_show_list,pages_messaging,pages_manage_metadata"
    )

# 3. Facebook OAuth callback
@app.route('/auth/callback')
def callback():
    code = request.args.get('code')
    token_url = f"https://graph.facebook.com/v17.0/oauth/access_token?client_id={FB_APP_ID}&client_secret={FB_APP_SECRET}&redirect_uri={REDIRECT_URI}&code={code}"
    token_response = requests.get(token_url).json()
    access_token = token_response.get('access_token')

    session['user_token'] = access_token
    return redirect('/select-page')

# 4. Select a Page
@app.route('/select-page')
def select_page():
    access_token = session.get('user_token')
    if not access_token:
        return redirect('/login')

    url = f"https://graph.facebook.com/v17.0/me/accounts?access_token={access_token}"
    pages = requests.get(url).json()
    return jsonify(pages)

# 5. Save selected page info (not storing yet)
@app.route('/save-page', methods=['POST'])
def save_page():
    data = request.json
    page_id = data.get('page_id')
    page_access_token = data.get('page_access_token')

    print("Saving Page Info:")
    print(f"Page ID: {page_id}")
    print(f"Access Token: {page_access_token}")

    return jsonify({"status": "success", "message": "Page connected successfully!"})

# 6. Facebook Webhook (GET for verification, POST for message handling)
@app.route('/webhook/messenger', methods=['GET', 'POST'])
def messenger_webhook():
    if request.method == 'GET':
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == FB_VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Verification failed", 403

    if request.method == 'POST':
        data = request.get_json()

        sender_id = data['entry'][0]['messaging'][0]['sender']['id']
        message_text = data['entry'][0]['messaging'][0]['message']['text']
        page_id = data['entry'][0]['id']

        MAKE_AI_HUB_WEBHOOK = "https://hook.us2.make.com/8il24edxdmn27rytoac5plup9shqh4k1"
        payload = {
            "sender_id": sender_id,
            "message": message_text,
            "page_id": page_id
        }

        response = requests.post(MAKE_AI_HUB_WEBHOOK, json=payload)
        print("Sent to Make:", response.status_code)

        return "OK", 200
