# AutoCourseGen 🎬

> AI-Powered Course Video Generator - 全自動課程影片生成系統

AutoCourseGen 是一個基於 AI 的全自動課程影片生成系統。只需輸入「學習需求」與「學生背景」，系統即可自動產出完整的教學影片，包含研究報告、課程大綱、投影片、配音與影片合成。

## ✨ 特色功能

- 🔬 **深度研究**: 自動分析學習需求，找出知識斷層與常見誤區
- 📚 **智慧課程規劃**: 使用幽默比喻設計循序漸進的課程大綱
- 🎨 **投影片自動生成**: 使用 python-pptx 生成可編輯的 PPTX 檔案
- 🎯 **Vision-based 座標提取**: 透過 Gemini Vision 分析投影片，自動產生滑鼠指向座標
- 🎤 **台灣腔甜美配音**: 使用 edge-tts 的 `zh-TW-HsiaoChenNeural` 語音模型
- 🖱️ **貝茲曲線滑鼠動畫**: 模擬真人滑鼠移動軌跡
- 💾 **斷點續做**: 所有中間產物都保存在 workspace，支援手動修改後繼續

## 🏗️ 系統架構

```
AutoCourseGen
├── 1. Deep Research Module      → workspace/1_research.md
├── 2. Curriculum Planner        → workspace/2_syllabus.json
├── 3. Slide Generator           → workspace/3_slides.pptx
├── 4. Visual Anchor & Script    → workspace/4_script_with_coords.json
└── 5. Composer                  → final_course_video.mp4
```

## 🚀 快速開始

### 1. 安裝依賴

```bash
cd autocourse_gen
pip install -r requirements.txt
```

### 2. 設定 API Key

複製 `.env.example` 為 `.env` 並填入您的 Gemini API Key：

```bash
cp .env.example .env
# 編輯 .env 檔案
GEMINI_API_KEY=your_api_key_here
```

### 3. 執行

**互動模式** (推薦初次使用):
```bash
python main.py -i
```

**命令列模式**:
```bash
python main.py \
  --requirement "學習 Python 基礎語法，包含變數、迴圈、函數" \
  --background "高中生，有基本數學概念，沒有程式經驗"
```

**單步執行** (開發/除錯用):
```bash
# 只執行研究步驟
python main.py --step research -r "..." -b "..."

# 只執行課程規劃
python main.py --step curriculum

# 只生成投影片
python main.py --step slides

# 只生成腳本和座標
python main.py --step anchor

# 只合成影片
python main.py --step compose
```

**斷點續做**:
```bash
python main.py --resume
```

## 📁 專案結構

```
autocourse_gen/
├── main.py                     # CLI 入口點
├── config.yaml                 # 設定檔
├── requirements.txt            # Python 依賴
├── .env.example               # 環境變數範本
├── setup.py                   # 安裝腳本
│
├── autocourse_gen/            # 主要程式碼
│   ├── __init__.py
│   │
│   ├── providers/             # LLM Provider (Adapter Pattern)
│   │   ├── base.py           # 抽象基底類別
│   │   └── gemini_provider.py # Gemini 實作
│   │
│   ├── modules/               # 核心模組
│   │   ├── deep_research.py   # 深度研究
│   │   ├── curriculum_planner.py # 課程規劃
│   │   ├── slide_generator.py # 投影片生成
│   │   ├── visual_anchor.py   # 視覺座標提取
│   │   └── composer.py        # 影音合成
│   │
│   └── utils/                 # 工具函數
│       ├── config_loader.py   # 設定載入
│       ├── resumable.py       # 斷點續做邏輯
│       ├── cursor_generator.py # 游標圖片生成
│       └── bezier.py          # 貝茲曲線計算
│
└── workspace/                 # 執行時產生的中間檔案
    ├── 1_research.md
    ├── 2_syllabus.json
    ├── 3_slides.pptx
    ├── 4_script_with_coords.json
    ├── slides_png/
    ├── audio/
    └── final_course_video.mp4
```

## ⚙️ 設定說明

編輯 `config.yaml` 可自訂以下項目：

### LLM 設定
```yaml
llm:
  default_provider: gemini
  gemini:
    text_model: gemini-1.5-pro
    vision_model: gemini-1.5-pro
    temperature: 0.7
```

### TTS 設定
```yaml
tts:
  voice: zh-TW-HsiaoChenNeural  # 台灣女聲
  rate: "+0%"                   # 語速調整
```

### 影片設定
```yaml
video:
  width: 1920
  height: 1080
  fps: 30
```

## 🔧 系統需求

- Python 3.9+
- LibreOffice (用於 PPTX 轉圖片)
- ffmpeg (用於影片合成)

### Ubuntu/Debian
```bash
sudo apt-get install libreoffice ffmpeg poppler-utils
```

### macOS
```bash
brew install libreoffice ffmpeg poppler
```

## 🤖 支援的 LLM Provider

目前支援：
- ✅ Google Gemini (預設)

計畫支援：
- ⏳ OpenAI GPT-4
- ⏳ Anthropic Claude

切換 Provider 只需修改 `config.yaml` 中的 `default_provider` 並實作對應的 Provider 類別。

## 📝 工作流程詳解

### Step 1: Deep Research
- 輸入：學習需求、學生背景
- 輸出：`1_research.md` (研究報告)
- 功能：分析知識斷層、找出常見誤區、搜尋最新文獻

### Step 2: Curriculum Planning
- 輸入：研究報告
- 輸出：`2_syllabus.json` (課程大綱)
- 功能：規劃課程結構、設計生動比喻、撰寫講解重點

### Step 3: Slide Generation
- 輸入：課程大綱
- 輸出：`3_slides.pptx` (PowerPoint 檔)
- 功能：自動排版投影片，可手動編輯調整

### Step 4: Visual Anchor & Script
- 輸入：投影片
- 輸出：`4_script_with_coords.json` (腳本+座標)
- 功能：
  - 將 PPTX 轉為圖片
  - 使用 Gemini Vision 生成逐字稿
  - 提取滑鼠應指向的座標

### Step 5: Composer
- 輸入：圖片、腳本、座標
- 輸出：`final_course_video.mp4`
- 功能：
  - TTS 語音合成 (台灣腔)
  - 貝茲曲線滑鼠動畫
  - 影片合成輸出

## 🐛 疑難排解

### LibreOffice 轉換失敗
如果 PPTX 無法正常轉為圖片，請確保 LibreOffice 已正確安裝：
```bash
libreoffice --version
```

### edge-tts 連線問題
edge-tts 需要網路連線。如遇連線問題，請檢查網路設定。

### moviepy 錯誤
確保已安裝 ImageMagick：
```bash
sudo apt-get install imagemagick
```

## 📄 授權

MIT License

## 🙏 致謝

- [Google Gemini](https://deepmind.google/technologies/gemini/) - AI 模型
- [edge-tts](https://github.com/rany2/edge-tts) - 語音合成
- [python-pptx](https://python-pptx.readthedocs.io/) - PowerPoint 生成
- [moviepy](https://zulko.github.io/moviepy/) - 影片處理
