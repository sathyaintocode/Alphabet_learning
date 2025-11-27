from flask import Flask, request, render_template, url_for, jsonify
import jwt
import os 
import json

app = Flask(__name__)

# -------------------------------
# STEP 1 DEBUG: Basic Connectivity Test (WORKING)
# -------------------------------
@app.route('/debug-step1')
def debug_step1():
    """Step 1: Check if Flask app receives requests through approuter"""
    return jsonify({
        "step": 1,
        "status": "Flask app is reachable",
        "message": "If you see this, approuter can reach Flask app",
        "headers_received": dict(request.headers),
        "authorization_header_present": "Authorization" in request.headers,
        "authorization_header_value": request.headers.get("Authorization"),
        "cookies_received": dict(request.cookies)
    })

# -------------------------------
# STEP 2 DEBUG: Check What Happens During Authentication 
# -------------------------------
@app.route('/debug-step2')
def debug_step2():
    """Step 2: See what authentication data is passed (if any)"""
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        return jsonify({
            "step": 2,
            "status": "NO AUTHORIZATION HEADER",
            "message": "No JWT token is being passed from approuter to Flask",
            "all_headers": dict(request.headers),
            "all_cookies": dict(request.cookies)
        })
    
    # If we have an auth header, try to decode it
    try:
        token = auth_header.replace("Bearer ", "")
        # Use PyJWT syntax
        decoded = jwt.decode(token, options={"verify_signature": False})
        
        return jsonify({
            "step": 2,
            "status": "JWT TOKEN FOUND AND DECODED!",
            "message": "Authentication is working perfectly!",
            "token_preview": token[:50] + "...",
            "user_email": decoded.get("email"),
            "user_name": decoded.get("user_name"),
            "given_name": decoded.get("given_name"),
            "family_name": decoded.get("family_name"),
            "scopes": decoded.get("scope", []),
            "issuer": decoded.get("iss"),
            "tenant": decoded.get("zid"),
            "expires": decoded.get("exp"),
            "success": "✅ Your SAP BTP authentication is working!"
        })
        
    except Exception as e:
        return jsonify({
            "step": 2,
            "status": "TOKEN FOUND BUT DECODE FAILED",
            "message": "Token exists but JWT library issue",
            "raw_auth_header": auth_header[:100] + "...",
            "error": str(e),
            "solution": "Update requirements.txt to use PyJWT==2.8.0 instead of python-jose"
        })

# -------------------------------
# Original Code (Your App Logic) - FIXED
# -------------------------------
def get_logged_in_user():
    print(request.headers)
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None

    try:
        token = auth_header.replace("Bearer ", "")
        decoded = jwt.decode(token, options={"verify_signature": False})
        return decoded.get("email")
    except Exception as e:
        print(f"Token decode error: {e}")
        return None
        

def login_required(f):
    def wrapper(*args, **kwargs):
        user = get_logged_in_user()
        if not user:
            return jsonify({
                "error": "Authentication required",
                "message": "Please log in to access this feature",
                "debug_info": {
                    "auth_header_present": bool(request.headers.get("Authorization")),
                    "suggestion": "Try /debug-step2 to see authentication details"
                }
            }), 401
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# -------------------------------
# Alphabet Data
# -------------------------------
alphabet_data = {
    'A': {'word': 'Apple', 'image': 'A.png'},
    'B': {'word': 'Ball', 'image': 'B.png'},
    'C': {'word': 'Cat', 'image': 'C.png'},
    'D': {'word': 'Deer', 'image': 'D.png'},
    'E': {'word': 'Elephant', 'image': 'E.png'},
}

# -------------------------------
# Protected Routes
# -------------------------------
@app.route('/')
@login_required
def index():
    return render_template('index.html', alphabets=list(alphabet_data.keys()))

@app.route('/alphabet/<letter>')
@login_required
def show_alphabet(letter):
    data = alphabet_data.get(letter.upper(), {'word': 'Not Found', 'image': 'notfound.png'})
    image_url = url_for('static', filename=f'images/{data["image"]}')
    return render_template('alphabet.html', letter=letter.upper(), data=data, image_url=image_url)


# -------------------------------
# Run
# -------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)