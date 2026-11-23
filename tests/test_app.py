import unittest
from unittest.mock import Mock, patch

import requests

from app import app


class PokedexTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.payload = {
            "id": 25, "name": "pikachu", "height": 4, "weight": 60,
            "types": [{"type": {"name": "electric"}}],
            "sprites": {
                "front_default": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png"
            },
        }
        patcher = patch("app.requests.get")
        self.get = patcher.start()
        self.addCleanup(patcher.stop)
        self.get.return_value = Mock(status_code=200)
        self.get.return_value.json.return_value = self.payload

    def test_home_and_assets(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("寶可夢圖鑑 Pokédex", response.get_data(as_text=True))
        for path in ("/assets/pokedex.css", "/assets/pokedex.js"):
            with self.client.get(path) as asset:
                self.assertEqual(asset.status_code, 200)

    def test_health(self):
        self.assertEqual(self.client.get("/api/health").json, {"ok": True})
        self.get.assert_not_called()

    def test_name_and_number(self):
        for key, normalized in (("PIKACHU", "pikachu"), ("0025", "25")):
            with self.subTest(key=key):
                response = self.client.get(f"/api/pokemon/{key}")
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json, {
                    "id": 25, "name": "pikachu", "types": ["electric"],
                    "height_m": 0.4, "weight_kg": 6.0,
                    "image_url": self.payload["sprites"]["front_default"],
                })
                self.get.assert_called_with(
                    f"https://pokeapi.co/api/v2/pokemon/{normalized}/",
                    timeout=8, allow_redirects=False,
                )

    def test_invalid_inputs_never_reach_upstream(self):
        for key in ("0", "026_", "%20", "a" * 81):
            with self.subTest(key=key):
                self.assertEqual(self.client.get(f"/api/pokemon/{key}").status_code, 400)
        self.get.assert_not_called()

    def test_upstream_http_errors(self):
        for upstream, expected in ((404, 404), (429, 429), (500, 502), (302, 502)):
            with self.subTest(upstream=upstream):
                self.get.return_value.status_code = upstream
                response = self.client.get("/api/pokemon/25")
                self.assertEqual(response.status_code, expected)
                self.assertTrue(response.json["error"])
        self.get.return_value.json.assert_not_called()

    def test_timeout(self):
        self.get.side_effect = requests.exceptions.Timeout
        self.assertEqual(self.client.get("/api/pokemon/25").status_code, 504)

    def test_connection_error(self):
        self.get.side_effect = requests.exceptions.ConnectionError
        self.assertEqual(self.client.get("/api/pokemon/25").status_code, 502)

    def test_invalid_json(self):
        self.get.return_value.json.side_effect = ValueError
        response = self.client.get("/api/pokemon/25")
        self.assertEqual(response.status_code, 502)
        self.assertIn("JSON", response.json["error"])

    def test_missing_and_malformed_required_data(self):
        for value in (None, [], {}, dict(self.payload, types=[{"type": {}}]),
                      dict(self.payload, height=True)):
            with self.subTest(value=value):
                self.get.return_value.json.return_value = value
                self.assertEqual(self.client.get("/api/pokemon/25").status_code, 502)

    def test_unsafe_and_missing_images(self):
        for value in ("http://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png",
                      "https://raw.githubusercontent.com.evil.example/25.png",
                      "https://raw.githubusercontent.com/other/repo/25.png", None):
            with self.subTest(value=value):
                self.payload["sprites"] = {"front_default": value}
                response = self.client.get("/api/pokemon/25")
                self.assertEqual(response.status_code, 200)
                self.assertIsNone(response.json["image_url"])

    def test_official_artwork_and_fallback(self):
        artwork = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png"
        sprites = self.payload["sprites"]
        sprites["other"] = {"official-artwork": {"front_default": artwork}}
        self.assertEqual(self.client.get("/api/pokemon/25").json["image_url"], artwork)
        sprites["other"]["official-artwork"]["front_default"] = "https://example.org/25.png"
        self.assertEqual(
            self.client.get("/api/pokemon/25").json["image_url"], sprites["front_default"],
        )


if __name__ == "__main__":
    unittest.main()
