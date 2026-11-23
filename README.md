# 寶可夢圖鑑 Pokédex

使用 Python 3.12、Flask、requests、HTML、CSS、JavaScript 與 PokéAPI。首頁預設顯示皮卡丘，可以用英文名稱或編號搜尋。隨機與前後導覽涵蓋全國圖鑑編號 1 至 1025。其他型態仍可依 PokéAPI 名稱或資源 ID 搜尋。

## 在 Windows PowerShell 啟動

將 ZIP 內的檔案解壓縮到 `C:\code\pokemon-pokedex`，讓 `app.py` 位於該資料夾。安裝 Python 3.12 後執行下列指令。若專案已有 Python 3.12 的 `.venv`，可以沿用並略過建立虛擬環境的指令。

```powershell
Set-Location C:\code\pokemon-pokedex
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m flask --app app run
```

瀏覽 [http://127.0.0.1:5000/](http://127.0.0.1:5000/)。按 Ctrl+C 停止伺服器。

## 執行測試

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

測試使用模擬的上游回應驗證 Flask 路由、資料轉換和錯誤處理，執行測試時不需要連線到 PokéAPI。

## 後端介面

| 方法與路徑 | 回應 |
| --- | --- |
| `GET /` | 圖鑑首頁 |
| `GET /api/health` | `{"ok": true}` |
| `GET /api/pokemon/<name_or_id>` | `id`、`name`、`types`、`height_m`、`weight_kg`、`image_url` |

錯誤回應使用 `{"error": "繁體中文訊息"}`。輸入錯誤回傳 400，查無資料回傳 404，上游限流回傳 429，逾時回傳 504，其餘上游失敗或必要欄位格式錯誤回傳 502。缺少可用圖片時，`image_url` 為 `null`。圖片限定 PokéAPI 官方 sprites 儲存庫的 HTTPS PNG 路徑，優先選用官方插畫並可退回預設正面圖。發往 PokéAPI 的 requests 呼叫設定 8 秒 timeout。

原始端點和欄位調查見 `api-spec.md`。 [PokéAPI 官方文件](https://pokeapi.co/docs/v2#pokemon)

## Vercel 專案結構

根目錄的 `app.py` 匯出 Flask 的 `app`，`requirements.txt` 宣告依賴，`.python-version` 指定 Python 3.12。CSS 與 JavaScript 放在 `public/assets/`，Vercel 會以 `/assets/` 提供靜態資源。使用 Flask 本機伺服器時，相同 URL 由 Flask 路由提供。目前尚未部署或驗證 Vercel 建置。 [Vercel Flask 部署文件](https://vercel.com/docs/frameworks/backend/flask) · [Vercel Python Runtime](https://vercel.com/docs/functions/runtimes/python)
