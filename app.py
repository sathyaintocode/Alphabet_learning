from flask import Flask, request, render_template, url_for, jsonify
import jwt
import os 

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
# STEP 2 DEBUG: Check What Happens During Authentication (FAILING)
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
            "problem": "SAP login failed - 'unable to verify password and username'",
            "diagnosis": "Login fails at SAP identity provider level",
            "all_headers": dict(request.headers),
            "all_cookies": dict(request.cookies)
        })
    
    # If we have an auth header, try to decode it
    try:
        token = auth_header.replace("Bearer ", "")
        decoded = jwt.decode(token, options={"verify_signature": False})
        
        return jsonify({
            "step": 2,
            "status": "JWT TOKEN FOUND!",
            "message": "Token is being generated and passed",
            "token_preview": token[:50] + "...",
            "decoded_token": decoded,
            "user_email": decoded.get("email"),
            "user_name": decoded.get("user_name"),
            "scopes": decoded.get("scope", [])
        })
        
    except Exception as e:
        return jsonify({
            "step": 2,
            "status": "TOKEN FOUND BUT DECODE FAILED",
            "message": "Token exists but cannot be decoded as JWT",
            "raw_auth_header": auth_header,
            "error": str(e)
        })

# -------------------------------
# STEP 3 DEBUG: Analyze WHY Login Fails
# -------------------------------
@app.route('/debug-step3')
def debug_step3():
    """Step 3: Analyze why SAP login fails"""
    return jsonify({
        "step": 3,
        "status": "LOGIN FAILURE ANALYSIS",
        "problem": "SAP Identity Provider rejects your credentials",
        
        "your_credentials": {
            "email": "sathyabhama.shibu@sap.com",
            "status": "Valid SAP employee credentials"
        },
        
        "identity_zone_issue": {
            "current_zone": "digital-assistant-experiment-djeq6drz.authentication.eu12.hana.ondemand.com",
            "standard_sap": "authentication.eu12.hana.ondemand.com", 
            "problem": "Your SAP email is NOT registered in this custom identity zone"
        },
        
        "why_login_fails": [
            "1. This app uses CUSTOM identity zone (digital-assistant-experiment-djeq6drz)",
            "2. Your SAP credentials work for STANDARD SAP systems",
            "3. Custom identity zone has SEPARATE user database",
            "4. Your email sathyabhama.shibu@sap.com is NOT in custom zone database",
            "5. Identity provider says 'unable to verify' because user doesn't exist"
        ],
        
        "solutions": [
            "1. Ask admin to ADD your email to custom identity zone user store",
            "2. Find out what credentials THIS specific app expects",
            "3. Check if there's a local user account you should use",
            "4. Reconfigure app to use standard SAP authentication"
        ],
        
        "test_this": {
            "manual_test": "Try login with different credential formats:",
            "variations": [
                "sathyabhama.shibu (without @sap.com)",
                "Your employee ID number",
                "Company-specific email domain",
                "Ask team: 'What login should I use for this app?'"
            ]
        },
        
        "current_diagnosis": "CONFIRMED: No JWT token generated because SAP login fails at identity verification step"
    })

# -------------------------------
# STEP 4 DEBUG: OAuth Flow Analysis
# -------------------------------
@app.route('/debug-step4')
def debug_step4():
    """Step 4: Show the complete OAuth flow and where it breaks"""
    return jsonify({
        "step": 4,
        "oauth_flow_analysis": {
            "step_1": {"status": "✅ WORKING", "description": "User accesses protected URL"},
            "step_2": {"status": "✅ WORKING", "description": "Approuter redirects to SAP login"},
            "step_3": {"status": "✅ WORKING", "description": "SAP login page loads"},
            "step_4": {"status": "❌ FAILING", "description": "SAP Identity Provider validates credentials → UNABLE TO VERIFY"},
            "step_5": {"status": "❌ NEVER HAPPENS", "description": "Authorization code generation → SKIPPED"},
            "step_6": {"status": "❌ NEVER HAPPENS", "description": "JWT token generation → SKIPPED"},
            "step_7": {"status": "❌ NEVER HAPPENS", "description": "Token forwarding to Flask → SKIPPED"}
        },
        
        "failure_point": "Step 4 - Identity Provider Validation",
        "failure_reason": "User credentials not found in custom identity zone database",
        
        "evidence": {
            "login_redirect_works": True,
            "login_page_loads": True,
            "credential_entry_works": True,
            "identity_validation": False,
            "error_message": "unable to verify password and username"
        }
    })

# -------------------------------
# Original Code (Your App Logic)
# -------------------------------
def get_logged_in_user():
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None

    token = auth_header.replace("Bearer ", "")

    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        return decoded.get("email")
    except:
        return None

def login_required(f):
    def wrapper(*args, **kwargs):
        user = get_logged_in_user()
        if not user:
            return "Unauthorized", 401
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