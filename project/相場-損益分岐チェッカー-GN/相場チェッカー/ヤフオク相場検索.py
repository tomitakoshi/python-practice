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
import customtkinter as ctk
from tkinter import filedialog
import os

# 設定：ここを実際のファイル名に合わせてください
CSV_FILE = 'C:/Users/tomit/python-practice/project/相場-損益分岐チェッカー-GN/相場チェッカー/list.csv'

def get_yahoo_average(driver, product_name):
    clean_name = product_name.replace('/', ' ').strip()
    params = {'va': clean_name, 'ei': 'UTF-8', 'f_adv': 1, 'fr': 'auc_adv'}
    query_string = urllib.parse.urlencode(params, quote_via=urllib.parse.quote_plus)
    url = f"https://auctions.yahoo.co.jp/pastbidsearch/closedsearch?{query_string}"

    try:
        driver.get(url)
        wait = WebDriverWait(driver, 5)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        page_text = driver.find_element(By.TAG_NAME, "body").text
        match = re.search(r"平均\s*([\d,]+)円", page_text)
        count_match = re.search(r"([\d,]+)件", page_text)

        if match:
            avg_price = int(match.group(1).replace(',', ''))
            count = int(count_match.group(1).replace(',', '')) if count_match else 1
            return avg_price, count
            
    except Exception as e:
        pass
    #ここで driver.quit() はしない 次に使う
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

def main(input_path, output_path, status_label, progress_bar, app):
    df = pd.read_csv(input_path, encoding='utf-8')

    if df is not None:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_argument('--blink-settings=imagesEnabled=false')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        try:
            total = len(df)
            app.after(0, lambda: progress_bar.set(0))
            avg_prices = []
            counts = []

            for i, name in enumerate(df['商品名'], 1):
                progress_value = i / total
                status_text = f"【進捗: {i}/{total}件】\n検索中: {name[:20]}..."
                app.after(0, lambda p=progress_value, t=status_text: (
                    progress_bar.set(p), 
                    status_label.configure(text=t, text_color="orange")
                ))
                avg_price, count = get_yahoo_average(driver, name)
                avg_prices.append(avg_price)
                counts.append(count)
                time.sleep(1.0)
            
            df['平均価格'] = avg_prices
            df['落札件数'] = counts
            
            # 🛡️ 指定された保存先に書き出し
            df.to_csv(output_path, index=False, encoding='utf-8-sig')

            final_text = f"✅ 完了！\n保存しました:\n{os.path.basename(output_path)}"
            app.after(0, lambda t=final_text: status_label.configure(text=t, text_color="lightgreen"))
        finally:
            driver.quit()
            
    else:
        app.after(0, lambda: status_label.configure(text="❌ ファイル読み込み失敗", text_color="red"))

def start_gui():
    ctk.set_appearance_mode("dark")
    app = ctk.CTk()
    app.title("ヤフオク相場チェッカー Pro")
    app.geometry("700x500")

    # パスを保持する変数
    input_file_path = ctk.StringVar(value="未選択")
    output_file_path = ctk.StringVar(value="未選択")

    # --- レイアウト ---
    label = ctk.CTkLabel(app, text="ヤフオク相場自動取得ツール", font=("Meiryo", 22, "bold"))
    label.pack(pady=20)

    # プログレスバーの設置
    progress_bar = ctk.CTkProgressBar(app, width=400)
    progress_bar.pack(pady=10)
    progress_bar.set(0)

    # 入力ファイル選択
    def select_input():
        path = filedialog.askopenfilename(filetypes=[("CSVファイル", "*.csv")])
        if path:
            input_file_path.set(path)
            # 自動で保存先も提案（同じフォルダに _result をつける）
            suggested_output = path.replace(".csv", "_result.csv")
            output_file_path.set(suggested_output)

    input_btn = ctk.CTkButton(app, text="① 読み込むCSVを選択", command=select_input)
    input_btn.pack(pady=5)
    ctk.CTkLabel(app, textvariable=input_file_path, font=("Meiryo", 10), text_color="gray").pack()

    # 保存先選択
    def select_output():
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSVファイル", "*.csv")])
        if path:
            output_file_path.set(path)

    output_btn = ctk.CTkButton(app, text="② 保存先を確認/変更", command=select_output, fg_color="transparent", border_width=1)
    output_btn.pack(pady=5)
    ctk.CTkLabel(app, textvariable=output_file_path, font=("Meiryo", 10), text_color="gray").pack()

    status_label = ctk.CTkLabel(app, text="待機中", font=("Meiryo", 14))
    status_label.pack(pady=20)

    def on_start():
        if input_file_path.get() == "未選択":
            status_label.configure(text="❌ ファイルを選択してください", text_color="red")
            return
        
        start_button.configure(state="disabled")
        thread = threading.Thread(target=main, args=(input_file_path.get(), output_file_path.get(), status_label, progress_bar, app))
        thread.daemon = True
        thread.start()

    start_button = ctk.CTkButton(app, text="相場取得スタート", command=on_start, fg_color="green", hover_color="darkgreen")
    start_button.pack(pady=20)

    app.mainloop()

if __name__ == "__main__":
    start_gui()