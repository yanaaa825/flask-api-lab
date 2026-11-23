import re
from pathlib import Path

import requests
from flask import Flask, jsonify, render_template, send_from_directory

app = Flask(__name__, static_folder=None)
PUBLIC_ASSETS = Path(__file__).resolve().parent / "public" / "assets"
POKEAPI = "https://pokeapi.co/api/v2/pokemon"
REQUEST_TIMEOUT = 8
LAST_NATIONAL_ID = 1025
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*", re.ASCII)
SPRITE_URL = re.compile(
    r"https://raw\.githubusercontent\.com/PokeAPI/sprites/master/"
    r"sprites/pokemon/(?:other/official-artwork/)?[0-9]+\.png"
)


def error(message, status):
    return jsonify(error=message), status


def normalize(data):
    pokemon_id = data["id"]
    name = data["name"]
    height = data["height"]
    weight = data["weight"]
    types = data["types"]
    if (
        type(pokemon_id) is not int or pokemon_id < 1
        or not isinstance(name, str) or not SLUG.fullmatch(name)
        or type(height) is not int or height < 0
        or type(weight) is not int or weight < 0
        or not isinstance(types, list) or not types
    ):
        raise ValueError("Invalid Pokémon fields")

    type_names = [item["type"]["name"] for item in types]
    if not all(isinstance(value, str) and SLUG.fullmatch(value) for value in type_names):
        raise ValueError("Invalid type names")

    sprites = data.get("sprites")
    sprites = sprites if isinstance(sprites, dict) else {}
    other = sprites.get("other")
    artwork = other.get("official-artwork") if isinstance(other, dict) else None
    official_url = artwork.get("front_default") if isinstance(artwork, dict) else None
    image_url = next(
        (url for url in (official_url, sprites.get("front_default"))
         if isinstance(url, str) and SPRITE_URL.fullmatch(url)),
        None,
    )
    return {
        "id": pokemon_id,
        "name": name,
        "types": type_names,
        "height_m": height / 10,
        "weight_kg": weight / 10,
        "image_url": image_url,
    }


@app.get("/")
def home():
    return render_template("index.html", last_national_id=LAST_NATIONAL_ID)


@app.get("/assets/<path:filename>")
def local_assets(filename):
    return send_from_directory(PUBLIC_ASSETS, filename)


@app.get("/api/health")
def health():
    return jsonify(ok=True)


@app.get("/api/pokemon/<name_or_id>")
def pokemon(name_or_id):
    key = name_or_id.strip().lower()
    if len(key) > 80 or not SLUG.fullmatch(key):
        return error("請輸入英文名稱或正整數圖鑑編號。", 400)
    if key.isascii() and key.isdecimal():
        key = key.lstrip("0")
        if not key:
            return error("圖鑑編號必須大於 0。", 400)

    try:
        upstream = requests.get(
            f"{POKEAPI}/{key}/",
            timeout=REQUEST_TIMEOUT,
            allow_redirects=False,
        )
    except requests.Timeout:
        return error("圖鑑服務回應逾時，請稍後重試。", 504)
    except requests.RequestException:
        return error("目前無法連線到圖鑑服務，請稍後重試。", 502)

    if upstream.status_code == 404:
        return error("找不到這隻寶可夢，請確認英文名稱或編號。", 404)
    if upstream.status_code == 429:
        return error("查詢次數過多，請稍等一下再試。", 429)
    if upstream.status_code != 200:
        return error("圖鑑服務暫時無法提供資料，請稍後重試。", 502)

    try:
        data = upstream.json()
    except ValueError:
        return error("圖鑑服務回傳的 JSON 無法讀取。", 502)
    try:
        return jsonify(normalize(data))
    except (AttributeError, KeyError, TypeError, ValueError):
        return error("圖鑑服務回傳的資料不完整或格式有誤。", 502)


if __name__ == "__main__":
    app.run()
