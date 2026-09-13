<div align="center">

<img src="frontend/logo.png" alt="MuxFlow Logo" width="160" />

# MuxFlow
### Modern, Mobile-First MKV Batch Muxing Suite for Unraid & Docker

[![Docker Image](https://img.shields.io/badge/docker-junyou1998%2Fmuxflow-blue?logo=docker&logoColor=white)](https://hub.docker.com/r/junyou1998/muxflow)
[![Platform](https://img.shields.io/badge/platform-amd64%20%7C%20arm64-lightgrey)](https://hub.docker.com/r/junyou1998/muxflow/tags)
[![GitHub release](https://img.shields.io/github/v/release/junyou1998/muxflow?include_prereleases&color=emerald)](https://github.com/junyou1998/muxflow/releases)
[![License](https://img.shields.io/github/license/junyou1998/muxflow)](LICENSE)

*專為 **手機、平板與桌面** 打造的現代化 MKV 批次封裝工具，提供極速、純網頁的原生觸控體驗。*

[繁體中文說明](#繁體中文說明) • [English Guide](#english-guide) • [Docker Hub](https://hub.docker.com/r/junyou1998/muxflow) • [Unraid 安裝教學](#-unraid-安裝教學)

</div>

---

## 🌟 設計理念與特色 (Design & Highlights)

**MuxFlow** 是一套專為現代家庭伺服器、NAS 與 Unraid 使用者打造的輕量化批次封裝工作站：
- 🚀 **100% 原生純網頁架構 (Vue 3 + Tailwind CSS + FastAPI)**：響應式 RWD 設計，無論在手機、平板或桌機螢幕上皆能流暢操作。
- ⚡ **極致輕量與低資源消耗**：內建官方最新 `mkvtoolnix`，待機記憶體僅約 **35MB - 50MB**，無需多餘視窗層。
- 📱 **行動端優先體驗**：專屬伺服器檔案瀏覽器、觸控拖曳排序、一鍵「頂端/上移/下移」、自動集數智慧對齊。
- 🛡️ **標準 Unraid / LinuxServer 權限**：完整支援 `PUID` / `PGID` / `UMASK`，確保 NAS 影音庫檔案權限安全乾淨。
- ⚡ **秒級無損原地修改 (`mkvpropedit`)**：僅需調整軌道名稱、語言標籤或預設軌時，支援原地秒級修改，無需耗時重寫整部影片。

---

## 📖 核心功能 (Core Features)

1. **影片清單 (Videos)**
   - 伺服器目錄瀏覽器（預設直連 `/storage` 或自訂目錄）。
   - 副檔名篩選（.mkv, .mp4, .avi, .ts, .m2ts, .mov, .webm 等）。
   - MediaInfo 即時軌道解析（視訊規格、編碼器、音訊聲道、字幕語言）。
   - 預設 FPS 覆蓋（23.976p, 24p, 25p, 29.97p, 50p, 60p）。
   - **修改既有軌道 (Modify Old Tracks)**：批次重新命名現有音軌/字幕軌名稱、語言代碼、Default/Forced 旗標。
2. **多軌字幕與音訊 (Subtitles & Audios)**
   - 支援動態新增多組字幕/音訊分頁（Subtitle 1, Subtitle 2...）。
   - **自動集數智慧對齊**：檔名包含 `[01]`、`EP02`、`E03` 自動精準配對。
   - 觸控友善排序器（支援手勢拖曳與單擊上下移動按鈕）。
   - 延遲毫秒（Delay ms）、軌道名稱自訂、ISO-639-2 語言代碼、預設/強制軌道設定。
3. **章節與附件 (Chapters & Attachments)**
   - 批次掛載章節檔案（.xml, .txt），支援「捨棄既有舊章節 (`--no-chapters`)」。
   - 批次掛載字型（.ttf, .otf）或封面，支援「捨棄舊附件 (`--no-attachments`)」與「過濾重複附件」。
4. **封裝與輸出控制 (Mux Settings)**
   - 輸出目錄設定、支援安全原子覆蓋來源檔案。
   - **原地修改 (`mkvpropedit`)**：不重寫影片主體，原地秒級修改中繼資料。
   - **CRC32 自動校驗**：封裝完成自動計算 CRC 並追加到檔名 `[A1B2C3D4]`，亦支援清除舊 CRC。
   - **白名單過濾 (Only Keep...)**：一鍵只保留特定 ID、特定語言代碼或名稱的音軌與字幕。
   - **預設軌自動降級**：將特定語言或音軌設為預設時，自動清除其餘軌道的 default 旗標。
5. **任務隊列與即時日誌 (Queue & Progress)**
   - 批次佇列即時進度百分比、目前處理檔案、耗時預估。
   - 支援開始 (Start)、暫停 (Pause)、繼續 (Resume)、中止 (Stop)、清除任務。
   - WebSocket 終端機即時輸出與錯誤排查日誌。
6. **設定與預設集 (Settings & Presets)**
   - 預設目錄記憶、常用偏好設定儲存。
   - 預設集（Presets）一鍵切換，針對不同動畫組或壓制格式快速套用。

---

## 🚀 快速啟動 (Quick Start)

### 1. 使用 Docker Run
```bash
docker run -d \
  --name muxflow \
  --restart unless-stopped \
  -p 5800:5800 \
  -e PUID=99 \
  -e PGID=100 \
  -e UMASK=022 \
  -e TZ=Asia/Taipei \
  -v /mnt/user/:/storage \
  -v /mnt/user/appdata/muxflow:/config \
  junyou1998/muxflow:latest
```

### 2. 使用 Docker Compose
在你的專案目錄建立 `docker-compose.yml`：
```yaml
version: "3.8"

services:
  muxflow:
    image: junyou1998/muxflow:latest
    container_name: muxflow
    restart: unless-stopped
    ports:
      - "5800:5800"
    environment:
      - PUID=99          # Unraid 預設使用者 ID (可依系統修改)
      - PGID=100         # Unraid 預設群組 ID
      - UMASK=022        # 新建檔案預設權限
      - TZ=Asia/Taipei   # 時區
    volumes:
      - /mnt/user/:/storage                 # 你的影音檔案庫路徑
      - /mnt/user/appdata/muxflow:/config   # 設定檔與日誌保存目錄
```
執行啟動：
```bash
docker compose up -d
```
瀏覽器開啟：`http://<伺服器IP>:5800`

---

## 🖥️ Unraid 安裝教學

MuxFlow 原生適配 Unraid OS，提供專屬的 Community Applications (CA) 模板。

### 方法 A：透過 Unraid 模板庫安裝（最推薦）
1. 進入 Unraid 網頁控制台 ➔ 前往 **Docker** 分頁。
2. 滑動到頁面底部，找到 **Template repositories (範本存儲庫)**。
3. 加入 MuxFlow 的範本網址：
   ```text
   https://github.com/junyou1998/muxflow
   ```
4. 點擊 **Save (儲存)** 後，點擊 **Add Container (新增容器)**。
5. 在右上角的 **Template (範本)** 下拉選單中選擇 **MuxFlow**。
6. 檢查 `/storage`（預設為 `/mnt/user/`）與 `/config`（預設為 `/mnt/user/appdata/muxflow`）路徑，點擊 **Apply (套用)** 即可完成安裝！

### 方法 B：直接手動下載 XML 範本
1. 下載本專案中的 `unraid-template.xml`。
2. 放置於 Unraid 隨身碟的：
   ```text
   /boot/config/plugins/dockerMan/templates-user/my-muxflow.xml
   ```
3. 在 Unraid 的 Docker 頁面點擊 **Add Container**，在 Template 中直接選取 **my-muxflow** 即可。

---

## ⚙️ 環境變數與目錄映射 (Configuration)

| 變數 / 映射路徑 | 預設值 | 說明 |
| :--- | :--- | :--- |
| **`PORT`** | `5800` | Web 服務監聽連接埠 |
| **`PUID`** | `99` | 執行容器內進程的使用者 ID (Unraid 建議為 99: nobody) |
| **`PGID`** | `100` | 執行容器內進程的群組 ID (Unraid 建議為 100: users) |
| **`UMASK`** | `022` | 新建立檔案的權限掩碼 |
| **`TZ`** | `Asia/Taipei` | 系統時區 (例如 `Asia/Taipei`, `UTC`, `America/New_York`) |
| **`/storage`** | *(容器路徑)* | 掛載宿主機的影片庫目錄 (例如 `/mnt/user/` 或 `/data`) |
| **`/config`** | *(容器路徑)* | 保存自訂預設集 (presets) 與設定檔的目錄 |

---

## 📱 手機 PWA 級體驗小技巧
- 用 Safari (iOS) 或 Chrome (Android) 開啟 `http://<你的NAS_IP>:5800`。
- 點擊瀏覽器的「分享」或「選單」按鈕，選擇 **「加入主畫面 (Add to Home Screen)」**。
- MuxFlow 將以全螢幕模式啟動，自動隱藏瀏覽器網址列與上下工具欄，操作體驗如同原生 App！

---

## 🛠️ 本地開發 (Local Development)

本專案採用前後端分離架構，但無需複雜的 Node.js 編譯打包，前端為純原生 ES 模組，即開即用：

```bash
# 1. 複製專案
git clone https://github.com/junyou1998/muxflow.git
cd muxflow

# 2. 建立 Python 虛擬環境並安裝依賴
python3 -m venv backend/venv
source backend/venv/bin/activate
pip install -r backend/requirements.txt

# 3. 確保本機已安裝 MKVToolNix (mkvmerge, mkvpropedit)
# macOS: brew install mkvtoolnix
# Ubuntu/Debian: apt-get install mkvtoolnix

# 4. 啟動後端伺服器 (同時提供前端靜態檔案)
python backend/run.py
```
開啟瀏覽器訪問 `http://localhost:5800`。

---

## 🤝 開發與授權 (License)

- 本專案基於 [MIT License](LICENSE) 開源。
- 核心依賴開源套件：[MKVToolNix](https://mkvtoolnix.download/), [FastAPI](https://fastapi.tiangolo.com/), [Vue.js](https://vuejs.org/), [Tailwind CSS](https://tailwindcss.com/)。
