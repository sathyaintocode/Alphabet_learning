from flask import Flask, request, render_template, url_for
import jwt
import os 

app = Flask(__name__)

# -------------------------------
# XSUAA Token Validation
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
    return render_template('index.html', alphabets=list(alphabet_data.keys()))

@app.route('/alphabet/<letter>')
@login_required
def show_alphabet(letter):
    data = alphabet_data.get(letter.upper(), {'word': 'Not Found', 'image': 'notfound.png'})
    image_url = url_for('static', filename=f'images/{data["image"]}')
    return render_template('alphabet.html', letter=letter.upper(), data=data, image_url=image_url)

# -------------------------------
# Run (local only)
# -------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
