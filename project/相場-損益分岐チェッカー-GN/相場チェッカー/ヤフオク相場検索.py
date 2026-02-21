import pandas as pd
import urllib.parse
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import re

# 設定：ここを実際のファイル名に合わせてください
CSV_FILE = 'C:/Users/tomit/python-practice/project/相場-損益分岐チェッカー-GN/相場チェッカー/list.csv'

def get_yahoo_average(product_name):
    clean_name = product_name.replace('/', ' ').strip()
    params = {'va': clean_name, 'ei': 'UTF-8', 'f_adv': 1, 'fr': 'auc_adv'}
    query_string = urllib.parse.urlencode(params, quote_via=urllib.parse.quote_plus)
    url = f"https://auctions.yahoo.co.jp/pastbidsearch/closedsearch?{query_string}"

    options = Options()
    # options.add_argument('--headless')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(url)
        time.sleep(4) # 🛡️ 画面が完全に出るまで長めに待つ

        # 🛡️ ページ全体のテキストを「力技」で取得
        page_text = driver.find_element(By.TAG_NAME, "body").text
        
        # 🛡️ 「平均」の後に続く数字を正規表現で引っこ抜く
        # 例: "平均\n4,686円" や "平均 4,686円" に対応
        match = re.search(r"平均\s*([\d,]+)円", page_text)
        
        # 🛡️ 件数も同様に取得
        count_match = re.search(r"([\d,]+)件", page_text)

        if match:
            avg_price = int(match.group(1).replace(',', ''))
            count = int(count_match.group(1).replace(',', '')) if count_match else 1
            return avg_price, count
            
    except Exception as e:
        pass
    finally:
        driver.quit()
        
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

        avg_prices = []
        counts = []

        for name in df['商品名']:
            print(f"検索中: {name[:30]}...", end="", flush=True)
            avg_price, count = get_yahoo_average(name)

            if count > 0:
                print(f" 完了！ [平均: {avg_price:,}円 / {count}件]")
            else:
                print(" データが見当たらないか、取得に失敗しました。")

            avg_prices.append(avg_price)
            counts.append(count)
            time.sleep(1.5)
        
        df['平均価格'] = avg_prices
        df['落札件数'] = counts

        output_file = CSV_FILE.replace('.csv', '_result.csv')
        df.to_csv(output_file, index=False, encoding='utf-8-sig')


        print("\n=== すべての工程が終了しました ===")
        print(f"結果を保存しました: {output_file}")
    
    else:
        print("データ取得エラー")

if __name__ == "__main__":
    main()
