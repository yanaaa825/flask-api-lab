# PokéAPI v2 規格卡｜寶可夢圖鑑

## A. 官方文件說明

PokéAPI 資源支援 HTTP GET，無需驗證。寶可夢詳情端點為 `GET /api/v2/pokemon/{id or name}/`。 [PokéAPI 官方文件](https://pokeapi.co/docs/v2#pokemon)

| 欄位 | 文件型別 | 用途 |
| --- | --- | --- |
| `id` | 整數 | 寶可夢資源識別碼 |
| `name` | 字串 | 寶可夢資源名稱 |
| `height` | 整數 | 身高，單位為分米（dm）。除以 10 可換算為公尺 |
| `weight` | 整數 | 體重，單位為百克（hg）。除以 10 可換算為公斤 |
| `types` | `PokemonType` 清單 | 從各項的 `type.name` 取得屬性名稱 |
| `sprites` | `PokemonSprites` 物件 | `front_default` 為預設正面圖的網址欄位 |

## B. 實際測試觀察

對 ID 25 送出一次 GET，未帶查詢參數、請求內容或憑證。curl 的整次傳輸 timeout 設為 8 秒，未啟用重試或跟隨轉址。

```bash
curl -q --request GET --max-time 8 --silent --show-error --include https://pokeapi.co/api/v2/pokemon/25/
```

- HTTP 狀態碼為 `200`（OK）。
- `Content-Type` 為 `application/json; charset=utf-8`。
- 回應內容成功由 Python 的 `json.loads` 解析，最外層為 JSON 物件。

| 欄位 | JSON 型別 | Python 型別 | 實測值或結構 |
| --- | --- | --- | --- |
| `id` | 整數 | `int` | `25` |
| `name` | 字串 | `str` | `"pikachu"` |
| `height` | 整數 | `int` | `4` dm，即 0.4 m |
| `weight` | 整數 | `int` | `60` hg，即 6 kg |
| `types` | 陣列 | `list` | 一筆，`types[0].type.name` 為 `"electric"`（電屬性） |
| `sprites` | 物件 | `dict` | 包含 `front_default` 字串 |

`sprites.front_default` 是一個含主機名稱、路徑以 `.png` 結尾的 HTTPS 圖片網址。 [回應中的預設正面圖網址](https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png)

## C. 尚未確認事項

- 本次只檢查圖片網址格式。圖片本身的 HTTP 狀態、媒體類型及能否顯示尚未測試。
- 本次僅測試 ID 25。其他寶可夢的欄位值、圖片欄位是否可能為空，以及無效 ID 的回應尚未實測。
