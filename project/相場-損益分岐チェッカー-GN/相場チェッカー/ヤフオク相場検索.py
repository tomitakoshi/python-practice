import customtkinter as ctk
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
import threading

# 設定：ここを実際のファイル名に合わせてください
CSV_FILE = 'C:/Users/tomit/python-practice/project/相場-損益分岐チェッカー-GN/相場チェッカー/list.csv'

def get_yahoo_average(product_name):
    clean_name = product_name.replace('/', ' ').strip()
    params = {'va': clean_name, 'ei': 'UTF-8', 'f_adv': 1, 'fr': 'auc_adv'}
    query_string = urllib.parse.urlencode(params, quote_via=urllib.parse.quote_plus)
    url = f"https://auctions.yahoo.co.jp/pastbidsearch/closedsearch?{query_string}"

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(url)

        wait = WebDriverWait(driver, 5)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

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

def main(status_label, app): # appも受け取れるように変更
    df = read_file()
    if df is not None:
        total = len(df)
        avg_prices = []
        counts = []

        for i, name in enumerate(df['商品名'], 1):
            # 🛡️ 進捗をGUIに表示
            status_text = f"【進捗: {i}/{total}件】\n検索中: {name[:20]}..."
            app.after(0, lambda: status_label.configure(text=status_text, text_color="orange"))
            
            avg_price, count = get_yahoo_average(name)
            avg_prices.append(avg_price)
            counts.append(count)
            time.sleep(1.0)
        
        df['平均価格'] = avg_prices
        df['落札件数'] = counts
        output_file = CSV_FILE.replace('.csv', '_result.csv')
        df.to_csv(output_file, index=False, encoding='utf-8-sig')

        # 🛡️ 完了表示
        final_text = f"✅ 完了！ ({total}/{total}件)\n保存先: {output_file}"
        app.after(0, lambda: status_label.configure(text=final_text, text_color="lightgreen"))
    else:
        app.after(0, lambda: status_label.configure(text="❌ ファイル読み込み失敗", text_color="red"))

def start_gui():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("ヤフオク相場チェッカー Pro")
    app.geometry("600x400")

    label = ctk.CTkLabel(app, text="ヤフオク相場自動取得ツール", font=("Meiryo", 20))
    label.pack(pady=20)

    status_label = ctk.CTkLabel(app, text="待機中", font=("Meiryo", 14), justify="left")
    status_label.pack(pady=10)

    # 🛡️ ボタンが押された時の動作を「別動隊（スレッド）」で起動するように変更
    def on_click():
        button.configure(state="disabled") # 二重クリック防止
        # threadingを使ってmain関数を裏で動かす
        thread = threading.Thread(target=main, args=(status_label, app))
        thread.daemon = True # アプリを閉じたらスレッドも終了させる設定
        thread.start()

    button = ctk.CTkButton(app, text="相場取得スタート", command=on_click)
    button.pack(pady=20)

    app.mainloop()

if __name__ == "__main__":
    start_gui()