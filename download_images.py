import requests

images = {
    "A.png": "https://img.freepik.com/free-psd/close-up-delicious-apple_23-2151868338.jpg",
    "B.png": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRZHqf21DZiCpdYl00cJWztmPzHQQwq8MXhDQ&s",
    "C.png": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQxMMWd08C5AE2EXAyUKJ_5SLvDntWHayN0uA&s",
    "D.png": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQrnZ54J4MeXVIDKWQcGt5dj_gXkOjJcOTM_w&s",
    "E.png": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSFnDnhqw5kPYKQ8g0lmNj6N-lpRTbyo_tJhw&s",
    "F.png": "https://upload.wikimedia.org/wikipedia/commons/1/1d/Football_Pallo_valmiina-cropped.jpg"
}

import os
os.makedirs("static/images", exist_ok=True)

for name, url in images.items():
    print(f"Downloading {name}...")
    img_data = requests.get(url).content
    with open(f"static/images/{name}", "wb") as f:
        f.write(img_data)

print("✅ All images saved successfully!")
