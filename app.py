from flask import Flask, request, render_template, url_for, jsonify
import jwt
import os 
import json
import base64
from datetime import datetime
import urllib.parse

app = Flask(__name__)

# -------------------------------
# XSUAA Configuration
# -------------------------------
def get_xsuaa_config():
    """Get XSUAA configuration from VCAP_SERVICES"""
    vcap_services = os.environ.get('VCAP_SERVICES')
    if vcap_services:
        services = json.loads(vcap_services)
        xsuaa_service = services.get('xsuaa', [])
        if xsuaa_service:
            return xsuaa_service[0]['credentials']
    return None

# -------------------------------
# Comprehensive Token Debug Routes
# -------------------------------
@app.route('/capture-everything')
def capture_everything():
    """Capture ALL possible authentication data, tokens, headers, cookies"""
    auth_header = request.headers.get("Authorization")
    
    # Try to decode any JWT-like tokens found
    decoded_tokens = {}
    
    # Check Authorization header
    if auth_header:
        try:
            if auth_header.startswith("Bearer "):
                token = auth_header[7:]  # Remove "Bearer "
                decoded_tokens["authorization_header"] = {
                    "raw_token": token,
                    "decoded": jwt.decode(token, options={"verify_signature": False})
                }
        except Exception as e:
            decoded_tokens["authorization_header_error"] = str(e)
    
    # Check all cookies for JWT-like data
    for cookie_name, cookie_value in request.cookies.items():
        if len(cookie_value) > 50:  # JWT tokens are usually long
            try:
                # Try direct JWT decode
                decoded_tokens[f"cookie_{cookie_name}"] = {
                    "raw_value": cookie_value,
                    "decoded": jwt.decode(cookie_value, options={"verify_signature": False})
                }
            except:
                try:
                    # Try URL decode first
                    url_decoded = urllib.parse.unquote(cookie_value)
                    decoded_tokens[f"cookie_{cookie_name}_url_decoded"] = {
                        "raw_value": cookie_value,
                        "url_decoded": url_decoded,
                        "decoded": jwt.decode(url_decoded, options={"verify_signature": False})
                    }
                except:
                    try:
                        # Try base64 decode
                        base64_decoded = base64.b64decode(cookie_value + '==')
                        decoded_tokens[f"cookie_{cookie_name}_base64"] = {
                            "raw_value": cookie_value,
                            "base64_decoded": base64_decoded.decode('utf-8', errors='ignore')
                        }
                    except:
                        pass
    
    # Check all headers for JWT-like data
    for header_name, header_value in request.headers.items():
        if len(str(header_value)) > 50 and 'jwt' in header_name.lower():
            try:
                decoded_tokens[f"header_{header_name}"] = {
                    "raw_value": header_value,
                    "decoded": jwt.decode(header_value, options={"verify_signature": False})
                }
            except:
                pass
    
    # Check query parameters for OAuth codes/tokens
    oauth_data = {}
    for param in ['code', 'access_token', 'id_token', 'token']:
        if param in request.args:
            oauth_data[param] = request.args.get(param)
            if param != 'code':  # Don't try to decode authorization codes
                try:
                    decoded_tokens[f"query_{param}"] = {
                        "raw_value": request.args.get(param),
                        "decoded": jwt.decode(request.args.get(param), options={"verify_signature": False})
                    }
                except:
                    pass
    
    return jsonify({
        "timestamp": str(datetime.now()),
        "status": "COMPLETE AUTHENTICATION CAPTURE",
        
        # Raw data
        "authorization_header": auth_header,
        "all_headers": dict(request.headers),
        "all_cookies": dict(request.cookies),
        "query_params": dict(request.args),
        "form_data": dict(request.form) if request.form else None,
        
        # OAuth specific data
        "oauth_data": oauth_data,
        "oauth_errors": {
            "error": request.args.get("error"),
            "error_description": request.args.get("error_description"),
            "error_uri": request.args.get("error_uri")
        },
        
        # Token analysis
        "token_analysis": {
            "has_authorization_header": auth_header is not None,
            "authorization_starts_with_bearer": auth_header and auth_header.startswith("Bearer "),
            "has_oauth_code": "code" in request.args,
            "has_access_token": "access_token" in request.args,
            "cookies_with_long_values": [k for k, v in request.cookies.items() if len(str(v)) > 30],
            "headers_with_jwt": [k for k, v in request.headers.items() if 'jwt' in k.lower() or 'token' in k.lower()],
        },
        
        # Decoded tokens (this is what you want to see!)
        "decoded_tokens": decoded_tokens,
        
        # XSUAA headers
        "xsuaa_headers": {
            "x_user_token": request.headers.get("X-User-Token"),
            "x_forwarded_user": request.headers.get("X-Forwarded-User"),
            "x_remote_user": request.headers.get("X-Remote-User"),
            "x_user": request.headers.get("X-User"),
            "x_forwarded_access_token": request.headers.get("X-Forwarded-Access-Token"),
            "x_identity_zone_id": request.headers.get("X-Identity-Zone-Id"),
        }
    })

@app.route('/bearer-token-hunter')
def bearer_token_hunter():
    """Specifically hunt for Bearer tokens in all possible locations"""
    results = {
        "timestamp": str(datetime.now()),
        "status": "HUNTING FOR BEARER TOKENS",
        "bearer_tokens_found": [],
        "potential_tokens": [],
        "search_locations": []
    }
    
    # Search Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header:
        results["search_locations"].append("Authorization header")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            try:
                decoded = jwt.decode(token, options={"verify_signature": False})
                results["bearer_tokens_found"].append({
                    "location": "Authorization header",
                    "raw_token": token[:50] + "..." if len(token) > 50 else token,
                    "full_raw_token": token,
                    "decoded": decoded,
                    "user_info": {
                        "email": decoded.get("email"),
                        "user_name": decoded.get("user_name"),
                        "sub": decoded.get("sub"),
                        "client_id": decoded.get("client_id"),
                        "scopes": decoded.get("scope", []),
                        "authorities": decoded.get("authorities", [])
                    }
                })
            except Exception as e:
                results["potential_tokens"].append({
                    "location": "Authorization header",
                    "raw_token": token[:50] + "...",
                    "error": str(e)
                })
    
    # Search all headers for Bearer-like patterns
    for header_name, header_value in request.headers.items():
        if 'bearer' in str(header_value).lower():
            results["search_locations"].append(f"Header: {header_name}")
            # Extract token after "Bearer "
            parts = str(header_value).split("Bearer ")
            if len(parts) > 1:
                token = parts[1].strip()
                try:
                    decoded = jwt.decode(token, options={"verify_signature": False})
                    results["bearer_tokens_found"].append({
                        "location": f"Header: {header_name}",
                        "raw_token": token[:50] + "...",
                        "full_raw_token": token,
                        "decoded": decoded
                    })
                except:
                    results["potential_tokens"].append({
                        "location": f"Header: {header_name}",
                        "raw_token": token[:50] + "...",
                        "note": "Found 'Bearer' but couldn't decode as JWT"
                    })
    
    # Search cookies for JWT patterns
    for cookie_name, cookie_value in request.cookies.items():
        if len(cookie_value) > 100:  # JWTs are usually long
            results["search_locations"].append(f"Cookie: {cookie_name}")
            try:
                # Try different decoding methods
                for decode_method, decoded_value in [
                    ("direct", cookie_value),
                    ("url_decode", urllib.parse.unquote(cookie_value)),
                    ("base64_decode", base64.b64decode(cookie_value + '==').decode('utf-8', errors='ignore'))
                ]:
                    try:
                        jwt_decoded = jwt.decode(decoded_value, options={"verify_signature": False})
                        results["bearer_tokens_found"].append({
                            "location": f"Cookie: {cookie_name} ({decode_method})",
                            "raw_token": decoded_value[:50] + "...",
                            "full_raw_token": decoded_value,
                            "decoded": jwt_decoded
                        })
                        break
                    except:
                        continue
            except:
                pass
    
    return jsonify(results)

@app.route('/oauth-callback-capture')
def oauth_callback_capture():
    """Capture OAuth callback with any tokens or codes"""
    return jsonify({
        "timestamp": str(datetime.now()),
        "status": "OAUTH CALLBACK CAPTURE",
        "url": request.url,
        "query_params": dict(request.args),
        "headers": dict(request.headers),
        "cookies": dict(request.cookies),
        
        "oauth_analysis": {
            "has_authorization_code": "code" in request.args,
            "authorization_code": request.args.get("code"),
            "has_error": "error" in request.args,
            "error": request.args.get("error"),
            "error_description": request.args.get("error_description"),
            "state": request.args.get("state"),
            "scope": request.args.get("scope")
        },
        
        "token_search": {
            "access_token": request.args.get("access_token"),
            "id_token": request.args.get("id_token"),
            "token_type": request.args.get("token_type")
        }
    })

@app.route('/login/callback')
def login_callback():
    """OAuth login callback - capture everything"""
    return oauth_callback_capture()

# -------------------------------
# Authentication Functions
# -------------------------------
def get_logged_in_user():
    """Extract user identifier from token - comprehensive version"""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None

    try:
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
        else:
            token = auth_header
            
        decoded = jwt.decode(token, options={"verify_signature": False}, algorithms=["RS256"])
        
        scopes = decoded.get("scope", [])
        authorities = decoded.get("authorities", [])
        xsappname = decoded.get('xsappname', 'alphabet-flask-security')
        
        has_user_scope = (
            f"{xsappname}.uaa.User" in scopes or 
            "uaa.user" in scopes or
            "uaa.resource" in authorities or
            "uaa.resource" in scopes or
            any("user" in scope.lower() for scope in scopes) or
            any("resource" in auth.lower() for auth in authorities)
        )
        
        if not has_user_scope:
            print(f"User doesn't have required scope/authority.")
            print(f"Available scopes: {scopes}")
            print(f"Available authorities: {authorities}")
            return None
        
        user_id = (
            decoded.get("email") or
            decoded.get("user_name") or
            decoded.get("user_id") or
            decoded.get("sub") or
            decoded.get("client_id")
        )
        
        print(f"User authenticated: {user_id}")
        return user_id
        
    except Exception as e:
        print(f"Token decode error: {e}")
        return None

def login_required(f):
    def wrapper(*args, **kwargs):
        # Skip authentication in development mode
        if os.environ.get('SKIP_AUTH') == 'true':
            return f(*args, **kwargs)
            
        user = get_logged_in_user()
        if not user:
            return jsonify({
                "error": "Unauthorized", 
                "message": "Valid token with user scope required",
                "debug": "Check /capture-everything endpoint to see authentication data"
            }), 401
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# -------------------------------
# Original Debug Routes
# -------------------------------
@app.route('/debug')
def debug_info():
    """Debug information about the environment"""
    return jsonify({
        "status": "Debug endpoint working",
        "vcap_services_available": os.environ.get('VCAP_SERVICES') is not None,
        "xsuaa_config_available": get_xsuaa_config() is not None,
        "headers_received": dict(request.headers),
        "authorization_header_present": "Authorization" in request.headers,
        "skip_auth_enabled": os.environ.get('SKIP_AUTH') == 'true',
        "environment_vars": {
            k: v for k, v in os.environ.items() 
            if k.startswith(('VCAP_', 'CF_', 'PORT', 'SKIP_'))
        }
    })

@app.route('/login-debug')
def login_debug():
    """Debug the login process"""
    return jsonify({
        "message": "Login debug endpoint - no auth required",
        "all_headers": dict(request.headers),
        "cookies": dict(request.cookies),
        "authorization_header_present": "Authorization" in request.headers
    })

@app.route('/check-roles', methods=['GET'])
def check_roles():
    """Check user roles"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"error": "Missing Authorization header"}), 200
    
    try:
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
        else:
            token = auth_header
            
        decoded = jwt.decode(token, options={"verify_signature": False}, algorithms=["RS256"])
        
        scopes = decoded.get('scope', [])
        authorities = decoded.get('authorities', [])
        xsappname = decoded.get('xsappname', 'alphabet-flask-security')
        
        has_user_role = (
            f"{xsappname}.uaa.User" in scopes or 
            "uaa.user" in scopes or
            "uaa.resource" in authorities or
            "uaa.resource" in scopes
        )
        
        return jsonify({
            "status": "Token decoded successfully",
            "user_info": {
                "email": decoded.get("email"),
                "user_name": decoded.get("user_name"),
                "sub": decoded.get("sub"),
                "client_id": decoded.get("client_id")
            },
            "access_check": {
                "has_access": has_user_role,
                "access_via": "uaa.resource in authorities" if "uaa.resource" in authorities else "other"
            },
            "token_details": {
                "scopes": scopes,
                "authorities": authorities,
                "grant_type": decoded.get('grant_type'),
                "xsappname": xsappname,
                "full_token": decoded
            }
        })
        
    except Exception as e:
        return jsonify({"error": f"Token decode failed: {str(e)}"}), 200

@app.route('/what-do-i-have')
def what_do_i_have():
    """Show what's in the token"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"error": "No Authorization header"}), 200
    
    try:
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
        else:
            token = auth_header
            
        decoded = jwt.decode(token, options={"verify_signature": False})
        
        return jsonify({
            "status": "Here's what you have in your token:",
            "scopes": decoded.get('scope', []),
            "authorities": decoded.get('authorities', []),
            "client_id": decoded.get('client_id'),
            "sub": decoded.get('sub'),
            "grant_type": decoded.get('grant_type'),
            "full_token": decoded,
            "analysis": {
                "has_uaa_user_scope": "uaa.user" in decoded.get('scope', []),
                "has_uaa_resource_authority": "uaa.resource" in decoded.get('authorities', []),
                "has_uaa_resource_scope": "uaa.resource" in decoded.get('scope', [])
            }
        })
        
    except Exception as e:
        return jsonify({"error": f"Token decode failed: {str(e)}"}), 200

# -------------------------------
# Alphabet Data
# -------------------------------
alphabet_data = {
    'A': {'word': 'Apple', 'image': 'A.png'},
    'B': {'word': 'Ball', 'image': 'B.png'},
    'C': {'word': 'Cat', 'image': 'C.png'},
    'D': {'word': 'Deer', 'image': 'D.png'},
    'E': {'word': 'Elephant', 'image': 'E.png'},
    'F': {'word': 'Foot', 'image': 'F.png'},
    'G': {'word': 'Giraffe', 'image': 'G.png'},
    'H': {'word': 'Hat', 'image': 'H.png'},
    'I': {'word': 'Ice cream', 'image': 'I.png'},
    'J': {'word': 'Jellyfish', 'image': 'J.png'},
    'K': {'word': 'Kite', 'image': 'K.png'},
    'L': {'word': 'Lion', 'image': 'L.png'},
    'M': {'word': 'Mango', 'image': 'M.png'},
    'N': {'word': 'Nose', 'image': 'N.png'},
    'O': {'word': 'Onion', 'image': 'O.png'},
    'P': {'word': 'Potato', 'image': 'P.png'},
    'Q': {'word': 'Queen', 'image': 'Q.png'},
    'R': {'word': 'Rabbit', 'image': 'R.png'},
    'S': {'word': 'Spider', 'image': 'S.png'},
    'T': {'word': 'Tiger', 'image': 'T.png'},
    'U': {'word': 'Umbrella', 'image': 'U.png'},
    'V': {'word': 'Violin', 'image': 'V.png'},
    'W': {'word': 'Watch', 'image': 'W.png'},
    'X': {'word': 'X-ray', 'image': 'X.png'},
    'Y': {'word': 'Yak', 'image': 'Y.png'},
    'Z': {'word': 'Zebra', 'image': 'Z.png'}
}

# -------------------------------
# Protected Routes
# -------------------------------
@app.route('/')
@login_required
def index():
    user = get_logged_in_user()
    return render_template('index.html', 
                         alphabets=list(alphabet_data.keys()),
                         current_user=user)

@app.route('/alphabet/<letter>')
@login_required
def show_alphabet(letter):
    data = alphabet_data.get(letter.upper(), {'word': 'Not Found', 'image': 'notfound.png'})
    image_url = url_for('static', filename=f'images/{data["image"]}')
    return render_template('alphabet.html', 
                         letter=letter.upper(), 
                         data=data, 
                         image_url=image_url)

# -------------------------------
# Run
# -------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)