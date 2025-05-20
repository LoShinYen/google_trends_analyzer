import pandas as pd
from pytrends.request import TrendReq
from datetime import datetime, timedelta
import time, random

# --- 參數設定 ---
KEYWORDS = {"BTC": "btc_hourly_macro_trend.csv", "ETH": "eth_hourly_macro_trend.csv"}
START_DATE = datetime(2015, 1, 1)
END_DATE = datetime(2025, 1, 1)
STEP_YEARS = 5
OVERLAP_WEEKS = 26


def fetch_trend_segments(keyword, start_date, end_date, step_years, overlap_weeks):
    """
    分段抓取 Google Trends 資料，並自動處理重疊區間，使用隨機延遲以降低請求頻率。
    """
    pytrends = TrendReq(hl='en-US', 
                        tz=0 , 
                        requests_args={
                            'headers': {
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                                'Accept-Language': 'en-US,en;q=0.9',
                                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                                'Accept-Encoding': 'gzip, deflate, br',
                                'Connection': 'keep-alive',
                                'Upgrade-Insecure-Requests': '1',
                                'TE': 'Trailers'
                            }
                        })
    segments = []
    current_start = start_date
    while current_start < end_date:
        current_end = min(current_start + timedelta(days=step_years * 365), end_date)
        tf_str = f"{current_start.strftime('%Y-%m-%d')} {current_end.strftime('%Y-%m-%d')}"
        try:
            pytrends.build_payload([keyword], timeframe=tf_str)
            df = pytrends.interest_over_time()
            if df.empty:
                print(f"[警告] {tf_str} 無資料，略過。")
            else:
                segments.append(df)
                print(f"已抓取: {tf_str}，資料筆數: {len(df)}")
        except Exception as e:
            print(f"[錯誤] 抓取 {tf_str} 失敗: {e}")
        current_start = current_end - timedelta(weeks=overlap_weeks)
        time.sleep(random.uniform(1, 3))  # 使用隨機延遲，降低請求頻率，避免 429
    return segments


def merge_and_rescale_segments(segments, keyword, overlap_weeks):
    """
    合併分段資料並進行比例修正，確保趨勢連續。
    """
    if not segments:
        raise ValueError("無可用的 Google Trends 資料段。")
    adjusted = segments[0].copy()
    for i in range(1, len(segments)):
        prev = adjusted[-overlap_weeks:]
        curr = segments[i][:overlap_weeks]
        mean_prev = prev[keyword].mean()
        mean_curr = curr[keyword].mean()
        scaling_factor = mean_prev / mean_curr if mean_curr != 0 else 1
        scaled = segments[i].copy()
        scaled[keyword] *= scaling_factor
        adjusted = pd.concat([adjusted, scaled[scaled.index > prev.index.max()]])
    adjusted = adjusted.resample("D").ffill()
    adjusted["date"] = adjusted.index.date
    return adjusted


def expand_to_hourly(adjusted, keyword):
    """
    將日級資料展開為小時級資料，並平分每日熱度，同時計算小時熱度與最大小時熱度之比值。
    """
    hourly_range = pd.date_range(start=adjusted.index.min(), end=adjusted.index.max() + timedelta(days=1), freq='H')[:-1]
    hourly_df = pd.DataFrame({"timestamp": hourly_range})
    hourly_df["date"] = hourly_df["timestamp"].dt.date
    merged_df = hourly_df.merge(adjusted[["date", keyword]], on="date", how="left")
    merged_df["macro_trend_hour"] = merged_df[keyword] / 24
    merged_df["hour_ratio_to_max"] = merged_df["macro_trend_hour"] / merged_df["macro_trend_hour"].max()
    
    return merged_df


def main():
    for keyword, output_csv in KEYWORDS.items():
        print(f"[INFO] 開始抓取關鍵字「{keyword}」的 Google Trends 資料...")
        segments = fetch_trend_segments(keyword, START_DATE, END_DATE, STEP_YEARS, OVERLAP_WEEKS)
        if not segments:
            print(f"[ERROR] 無法取得關鍵字「{keyword}」的 Google Trends 資料，略過。")
            continue
        print(f"[INFO] 合併與比例修正關鍵字「{keyword}」...")
        adjusted = merge_and_rescale_segments(segments, keyword, OVERLAP_WEEKS)
        print(f"[INFO] 展開關鍵字「{keyword}」為小時級資料...")
        hourly_df = expand_to_hourly(adjusted, keyword)
        hourly_df.to_csv(output_csv, index=False)
        print(f"[INFO] 已輸出關鍵字「{keyword}」結果至 {output_csv}")
        print(hourly_df.head())


if __name__ == "__main__":
    main()