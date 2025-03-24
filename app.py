from flask import Flask, redirect, request, session, jsonify
import requests
import os

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

FB_APP_ID = os.getenv("FB_APP_ID")
FB_APP_SECRET = os.getenv("FB_APP_SECRET")
REDIRECT_URI = "https://luvoclone-auth-1.onrender.com/auth/callback"  # <- Update to match your Render URL

# Root route (Render will check this to verify the app is running)
@app.route('/')
def home():
    return "Hello Supreme Ruler! LuvoClone Auth is live!"

# Facebook Login
@app.route('/login')
def login():
    return redirect(
        f"https://www.facebook.com/v17.0/dialog/oauth?client_id={FB_APP_ID}&redirect_uri={REDIRECT_URI}&scope=pages_show_list,pages_messaging,pages_manage_metadata"
    )

# Facebook OAuth Callback
@app.route('/auth/callback')
def callback():
    code = request.args.get('code')
    token_url = f"https://graph.facebook.com/v17.0/oauth/access_token?client_id={FB_APP_ID}&client_secret={FB_APP_SECRET}&redirect_uri={REDIRECT_URI}&code={code}"
    token_response = requests.get(token_url).json()
    access_token = token_response.get('access_token')

    session['user_token'] = access_token
    return redirect('/select-page')

# Select a Page from Facebook
@app.route('/select-page')
def select_page():
    access_token = session.get('user_token')
    if not access_token:
        return redirect('/login')

    url = f"https://graph.facebook.com/v17.0/me/accounts?access_token={access_token}"
    pages = requests.get(url).json()
    return jsonify(pages)

# Save the selected Page
@app.route('/save-page', methods=['POST'])
def save_page():
    data = request.json
    page_id = data.get('page_id')
    page_access_token = data.get('page_access_token')

    print("Saving Page Info:")
    print(f"Page ID: {page_id}")
    print(f"Access Token: {page_access_token}")

    return jsonify({"status": "success", "message": "Page connected successfully!"})

# Run app locally (not used in Render)
if __name__ == '__main__':
    app.run(debug=True)
