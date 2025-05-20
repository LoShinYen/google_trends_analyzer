# Google Trends Analyzer

本專案用於自動化抓取 Google Trends 關鍵字（例如 BTC、ETH 等）的長期趨勢資料，並將其轉換為小時級別的趨勢數據，方便後續分析與研究。

## 功能說明
- 支援多關鍵字（透過 dict 設定）分段抓取 Google Trends 資料，解決單次查詢時間範圍限制。
- 自動重疊半年資料以進行比例修正，拼接長期趨勢。
- 將日級資料補齊為每日，並細分為每小時資料，同時計算小時熱度與最大小時熱度之比值。
- 依關鍵字分別輸出小時級別的趨勢 CSV 檔案。

## 依賴安裝
請先安裝 Python 3.9.12 版本，並安裝必要套件：

```bash
pip install -r requirements.txt
```

## 使用方式
1. 編輯 `main.py`，可自訂關鍵字與對應輸出檔案（例如 KEYWORDS = {"BTC": "btc_hourly_macro_trend.csv", "ETH": "eth_hourly_macro_trend.csv"}），以及起始與結束日期、分段年數、重疊週數等參數。
2. 執行主程式：

```bash
python main.py
```

3. 執行後，系統會依 KEYWORDS 分別產生對應的 CSV 檔案。

## 輸出說明
- 每個關鍵字對應的 CSV 檔案（例如 btc_hourly_macro_trend.csv）內容包含：
  - `timestamp`：每小時的時間戳記
  - `date`：對應的日期
  - `關鍵字`（例如 BTC）：該日的 Google Trends 熱度值
  - `macro_trend_hour`：將每日熱度平均分配到每小時的值
  - `hour_ratio_to_max`：小時熱度與最大小時熱度之比值

## 注意事項
- Google Trends API 有查詢頻率限制，本專案已加入隨機延遲（random.uniform(1, 3)）以降低 429 錯誤風險，請勿頻繁重複執行。
- 若關鍵字查無資料，請確認拼寫或更換關鍵字。
- 本專案僅供學習與研究，不擔保資料正確性，且使用者須自行承擔因使用本專案所產生之風險。

## 免責聲明
本專案僅供學習與研究，不擔保資料正確性，且使用者須自行承擔因使用本專案所產生之風險。本專案之作者與維護者不對任何因使用本專案而導致的損失或損害負責。

## 聯絡方式
如有問題，歡迎提出 issue 或聯絡專案維護者。 
