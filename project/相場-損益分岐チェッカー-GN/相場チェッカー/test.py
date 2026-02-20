import pandas as pd
import urllib.parse
import requests
from bs4 import BeautifulSoup
import time

# 設定：ここを実際のファイル名に合わせてください
CSV_FILE = 'C:/Users/tomit/python-practice/project/相場-損益分岐チェッカー-GN/相場チェッカー/list.csv'

def create_test_url(product_name):
    # 1. 記号のクレンジング
    clean_name = product_name.replace('/', ' ').replace('･', ' ').replace('　', ' ')
    
    # 2. パラメータ構築（ヤフオク詳細検索: closedsearch）
    params = {
        'va': clean_name,  # すべてのキーワードを含む
        'vo': '',          # いずれかのキーワード
        've': '',          # 除外キーワード
        'auccat': 0,       # カテゴリ
        'aucminprice': '',
        'aucmaxprice': '',
        'slider': 0,
        'ei': 'UTF-8',
        'f_adv': 1,        # 詳細検索モード
        'fr': 'auc_adv'
    }
    
    # 3. URL組み立て
    query_string = urllib.parse.urlencode(params)
    url = f"https://auctions.yahoo.co.jp/pastbidsearch/closedsearch?{query_string}"
    
    return url

def main():
    try:
        # CSV読み込み
        df = pd.read_csv(CSV_FILE, encoding='utf-8')
        
        print(f"--- URL生成テスト開始 ({len(df)}件) ---")
        
        for name in df['商品名']:
            # テスト用にURLだけを生成して表示
            target_url = create_test_url(name)
            
            print(f"\n【元の商品名】: {name}")
            print(f"【生成されたURL】: \n{target_url}")
            print("-" * 30)

    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()