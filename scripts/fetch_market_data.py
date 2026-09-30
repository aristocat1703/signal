#!/usr/bin/env python3
"""Fetch market data using yfinance and save to JSON"""

import yfinance as yf
import pandas as pd
import json
import os
from datetime import datetime
import pytz

def get_latest_price(ticker, max_retries=2):
    """Fetch latest price for a ticker"""
    for attempt in range(max_retries):
        try:
            data = yf.Ticker(ticker)
            hist = data.history(period='1d')
            if hist.empty:
                return None
            
            row = hist.iloc[-1]
            return {
                'price': float(row['Close']) if not pd.isna(row['Close']) else None,
                'high': float(row['High']) if not pd.isna(row['High']) else None,
                'open': float(row['Open']) if not pd.isna(row['Open']) else None,
                'date': hist.index[-1].strftime('%Y-%m-%d')
            }
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Error fetching {ticker}: {e}")
                return None
    return None

def main():
    # 수집할 종목 및 지표
    symbols = {
        'etf_us': ['QQQM', 'SCHD', 'QQQI', 'QLD', 'TQQQ', 'QQQ', 'SPY'],
        'etf_kr': ['069500'],  # KODEX 200
        'individual_watch': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', '005930.KS', '000660.KS'],  # M7 + 삼성, 하이닉스
        'individual_major': ['NVDA', 'AAPL', 'MSFT', 'MU', 'AMD', 'GOOGL', 'META', 'AMZN', 'QCOM', 'TXN', 'KO', 'PG', 'MRK', 'CVS'],  # QQQM·QQQI·SCHD 주요
        'sectors': ['XLK', 'XLF', 'XLE', 'XLV', 'XLI', 'XLY', 'XLP', 'XLB', 'XLU', 'XLRE', 'XLC'],  # 11개 섹터
        'indices': ['^KS11'],  # 코스피
        'indicators': ['^VIX', '^TNX', 'KRW=X', '^CRUDE']  # VIX, 미10년물, 원/달러, WTI
    }
    
    # 데이터 수집
    data = {
        'fetched_at': datetime.now(pytz.timezone('Asia/Seoul')).isoformat(),
        'market_data': {}
    }
    
    all_tickers = []
    for category in symbols.values():
        all_tickers.extend(category)
    
    print(f"Fetching {len(all_tickers)} tickers...")
    
    for ticker in all_tickers:
        print(f"  {ticker}...", end=' ', flush=True)
        result = get_latest_price(ticker)
        if result:
            data['market_data'][ticker] = result
            print("✓")
        else:
            print("✗")
    
    # 디렉토리 생성
    os.makedirs('data', exist_ok=True)
    
    # JSON 저장
    with open('data/market-data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\nSaved to data/market-data.json")
    print(f"Total tickers fetched: {len(data['market_data'])}/{len(all_tickers)}")

if __name__ == '__main__':
    main()
