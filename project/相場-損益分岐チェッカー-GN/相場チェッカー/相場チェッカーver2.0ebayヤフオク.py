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

def get_ebay_average(driver, product_name):
    clean_name = urllib.parse.quote(product_name)
    url = f"https://www.ebay.com/sch/i.html?_nkw={clean_name}&LH_Sold=1&LH_Complete=1&LH_ItemCondition=3000&_ipg=24"
    
    try:
        driver.get(url)
        time.sleep(3) 
        
        page_text = driver.find_element(By.TAG_NAME, "body").text
        
        target_pattern = r"(?:中古品|新品|今すぐ買う|[\d]+件の入札|オークション)\s+([\d,]+)\s*円"
        matches = re.findall(target_pattern, page_text)
        
        data_points = []
        for m in matches:
            clean_num = m.replace(',', '')
            try:
                val = float(clean_num)
                # 🛡️ 異常値フィルター（1000円以下の小物や、100万円超えの誤検知を除外）
                if 1000 < val < 1000000:
                    data_points.append(val)
            except:
                continue
            
            if len(data_points) >= 20: break

        if data_points:
            avg_price = sum(data_points) / len(data_points)
            count = len(data_points)
            return avg_price, count
            
    except Exception as e:
        print(f"DEBUG Error: {e}")
        
    return 0, 0

def read_file():
    try:
        df = pd.read_csv(CSV_FILE, encoding='utf-8')
        
        print(f"--- {CSV_FILE} の読み込みに成功しました ---")
        return df

    except FileNotFoundError:
        print(f"エラー：{CSV_FILE} が見つかりません。")
        print("同じフォルダにファイルを作成してください。")
        return None
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")
        return None

def main(input_path, output_path, status_label, progress_bar, app, mode, fee, ship, margin, rate,start_button):
    df = pd.read_csv(input_path, encoding='utf-8')

    if df is not None:
        options = Options()
        #options.add_argument('--headless')
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
                status_text = f"【{mode}モード進捗: {i}/{total}件】\n検索中: {name[:20]}..."
                app.after(0, lambda p=progress_value, t=status_text: (
                    progress_bar.set(p), 
                    status_label.configure(text=t, text_color="orange")
                ))

                # 🛡️ 分岐点1：モードによって呼び出す関数を変える
                if mode == "eBay":
                    avg_price, count = get_ebay_average(driver, name)
                else:
                    avg_price, count = get_yahoo_average(driver, name)
                
                avg_prices.append(avg_price)
                counts.append(count)
                time.sleep(1.0) # eBayは特にBAN防止でこれが必要
            
            df['平均価格'] = avg_prices
            df['落札件数'] = counts
            
            # 🛡️ 分岐点2：計算ロジックの統合
            if mode == "eBay":
                df['平均価格(円)'] = df['平均価格'].astype(int)
                df['損益分岐点'] = df['平均価格'].apply(
                    lambda x: int(x * (1 - fee) - ship) if x > 0 else 0
                )
                df['目標仕入れ値'] = df['平均価格'].apply(
                    lambda x: int(x * (1 - fee - margin) - ship) if x > 0 else 0
                )
            else:
                # ヤフオクの場合
                df['損益分岐点'] = df['平均価格'].apply(
                    lambda x: int(x * (1 - fee) - ship) if x > 0 else 0
                )
                df['目標仕入れ値'] = df['平均価格'].apply(
                    lambda x: int(x * (1 - fee - margin) - ship) if x > 0 else 0
                )

            # マイナス値の補正
            df.loc[df['損益分岐点'] < 0, '損益分岐点'] = 0
            df.loc[df['目標仕入れ値'] < 0, '目標仕入れ値'] = 0
            
            df.to_csv(output_path, index=False, encoding='utf-8-sig')

            final_text = f"✅ {mode}完了！\n保存しました:\n{os.path.basename(output_path)}"
            app.after(0, lambda t=final_text: status_label.configure(text=t, text_color="lightgreen"))
        finally:
            driver.quit()
            app.after(0, lambda: start_button.configure(state="normal")) # ボタンを復帰させる
            
    else:
        app.after(0, lambda: status_label.configure(text="❌ ファイル読み込み失敗", text_color="red"))
def start_gui():
    ctk.set_appearance_mode("dark")
    app = ctk.CTk()
    app.title("相場チェッカー")
    app.geometry("700x700")
    app.resizable(True, True)


    # パスを保持する変数
    input_file_path = ctk.StringVar(value="未選択")
    output_file_path = ctk.StringVar(value="未選択")

    # --- レイアウト ---
    label = ctk.CTkLabel(app, text="相場チェッカー", font=("Meiryo", 22, "bold"))
    label.pack(pady=20)

    # プログレスバーの設置
    progress_bar = ctk.CTkProgressBar(app, width=400)
    progress_bar.pack(pady=10)
    progress_bar.set(0)

    
    # 送料手数料入力
    setting_frame = ctk.CTkFrame(app)
    setting_frame.pack(pady=20, padx=40, fill="x")

    ctk.CTkLabel(setting_frame, text="【利益計算設定】", font=("Meiryo", 14, "bold")).grid(row=0, column=0, columnspan=4, pady=10)

    ## 1行目：手数料と送料
    ctk.CTkLabel(setting_frame, text="販売手数料 (%) :").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    fee_entry = ctk.CTkEntry(setting_frame, width=70)
    fee_entry.insert(0, "10")
    fee_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

    ctk.CTkLabel(setting_frame, text="想定送料 (円) :").grid(row=1, column=2, padx=10, pady=5, sticky="e")
    shipping_entry = ctk.CTkEntry(setting_frame, width=90)
    shipping_entry.insert(0, "800")
    shipping_entry.grid(row=1, column=3, padx=5, pady=5, sticky="w")

    ## 2行目：利益率
    ctk.CTkLabel(setting_frame, text="確保したい利益 (%) :").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    margin_entry = ctk.CTkEntry(setting_frame, width=70)
    margin_entry.insert(0, "10")
    margin_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

    ## 3行目ebayモードでの為替レート
    """
    ctk.CTkLabel(setting_frame, text="為替 (1USD=円) :").grid(row=2, column=2, padx=10, pady=5, sticky="e")
    rate_entry = ctk.CTkEntry(setting_frame, width=90)
    rate_entry.insert(0, "150") # デフォルト150円
    rate_entry.grid(row=2, column=3, padx=5, pady=5, sticky="w")
    """

    #ebayモードスイッチ
    mode_var = ctk.StringVar(value="ヤフオク")
    mode_switch = ctk.CTkSegmentedButton(app, values=["ヤフオク", "eBay"], variable=mode_var)
    mode_switch.pack(pady=10)

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
    
        try:
            # GUIからの入力を数値に変換
            fee = float(fee_entry.get()) / 100
            ship = int(shipping_entry.get())
            margin = float(margin_entry.get()) / 100
            #rate = float(rate_entry.get())  # 為替レートを取得
            mode = mode_var.get()           
        except ValueError:
            status_label.configure(text="❌ 数値を正しく入力してください", text_color="red")
            return
        
        start_button.configure(state="disabled")

        # main関数にすべての引数を渡す
        thread = threading.Thread(target=main, args=(
            input_file_path.get(), 
            output_file_path.get(), 
            status_label, 
            progress_bar, 
            app,
            mode,
            fee, 
            ship, 
            margin,
            1.0,
            start_button
        ))
        thread.daemon = True
        thread.start()

    start_button = ctk.CTkButton(app, text="相場取得スタート", command=on_start, fg_color="green", hover_color="darkgreen")
    start_button.pack(pady=20)

    app.mainloop()

if __name__ == "__main__":
    start_gui()