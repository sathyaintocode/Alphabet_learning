from flask import Flask, render_template, url_for

app = Flask(__name__)

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

@app.route('/')
def index():
    return render_template('index.html', alphabets=list(alphabet_data.keys()))

@app.route('/alphabet/<letter>')
def show_alphabet(letter):
    data = alphabet_data.get(letter.upper())
    if not data:
        data = {'word': 'Not Found', 'image': 'notfound.png'}
    # Use url_for to point to the static folder
    image_url = url_for('static', filename=f'images/{data["image"]}')
    return render_template('alphabet.html', letter=letter.upper(), data=data, image_url=image_url)

if __name__ == '__main__':
    app.run(debug=True)
