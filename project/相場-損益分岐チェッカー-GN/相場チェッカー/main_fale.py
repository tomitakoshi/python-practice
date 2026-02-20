"""
この方法ではできなかったけど記録だけ残しておく
"""

import pandas as pd
import urllib.parse
import requests
from bs4 import BeautifulSoup
import time

# 設定：ここを実際のファイル名に合わせてください
CSV_FILE = 'C:/Users/tomit/python-practice/project/相場-損益分岐チェッカー-GN/相場チェッカー/list.csv'

def get_yahoo_average(product_name):
    clean_name = product_name.replace('/', ' ').strip()
    
    params = {
            'va': clean_name,   # 「すべてのキーワードを含む」に商品名を投入
            'vo': '',
            've': '',
            'auccat': 0,
            'aucminprice': '',
            'aucmaxprice': '',
            'slider': 0,
            'ei': 'UTF-8',
            'f_adv': 1,
            'fr': 'auc_adv'
        }
    query_string = urllib.parse.urlencode(params, quote_via=urllib.parse.quote_plus)
    url = f"https://auctions.yahoo.co.jp/pastbidsearch/closedsearch?{query_string}"
    # --- ここから下は通信と解析 ---
    print(f"生成URL: {url}") # デバッグ用に表示して確認できます

    query_string = urllib.parse.urlencode(params)
    url = f"https://auctions.yahoo.co.jp/pastbidsearch/closedsearch?{query_string}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
        "Referer": "https://auctions.yahoo.co.jp/"
    }

    try:
        time.sleep(1.0) 
        
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        price_elements = soup.select('.Price__value')
        
        prices = []
        for el in price_elements:
            price_text = "".join(filter(str.isdigit, el.get_text()))
            if price_text:
                prices.append(int(price_text))
        
        if prices:
            avg = sum(prices) / len(prices)
            return int(avg), len(prices)
        
        if prices:
            avg = sum(prices) / len(prices)
            return int(avg), len(prices)
    except Exception as e:
        print(f" 通信エラー: {e}")
        
    return 0, 0



def read_file():
    try:
        df = pd.read_csv(CSV_FILE, encoding='utf-8')
        
        print(f"--- {CSV_FILE} の読み込みに成功しました ---")
        """
        print("【データの中身（先頭5件）】")
        print(df.head())
        
        print("\n【見つかった列名】")
        print(df.columns.tolist())
        """
        return df

    except FileNotFoundError:
        print(f"エラー：{CSV_FILE} が見つかりません。")
        print("同じフォルダにファイルを作成してください。")
        return None
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")
        return None

def main():
    df = read_file()

    if df is not None:
        print("\n=== 相場取得を開始します ===")

        for name in df['商品名']:
            print(f"検索中: {name[:30]}...", end="", flush=True)
            avg_price, count = get_yahoo_average(name)

            if count > 0:
                print(f" 完了！ [平均: {avg_price:,}円 / {count}件]")
            else:
                print(" データが見当たらないか、取得に失敗しました。")
            time.sleep(1.5)
        
        print("\n=== すべての工程が終了しました ===")
    
    else:
        print("データ取得エラー")

if __name__ == "__main__":
    main()
