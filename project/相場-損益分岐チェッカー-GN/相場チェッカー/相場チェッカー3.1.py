import customtkinter as ctk
import pandas as pd
import urllib.parse
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
from tkinter import filedialog
import os

# 設定
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
    except: pass
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
        data_points = [float(m.replace(',', '')) for m in matches if 1000 < float(m.replace(',', '')) < 1000000]
        if data_points:
            return sum(data_points[:20]) / len(data_points[:20]), len(data_points[:20])
    except Exception as e: print(f"DEBUG eBay Error: {e}")
    return 0, 0

def get_mercari_average(driver, product_name):
    clean_name = urllib.parse.quote(product_name)
    url = f"https://jp.mercari.com/search?keyword={clean_name}&status=sold_out"
    try:
        driver.get(url)
        time.sleep(3) 
        page_text = driver.find_element(By.TAG_NAME, "body").text
        # メルカリ特有の「¥ (改行) 数字」に対応
        matches = re.findall(r"¥[\s\n]*([\d,]+)", page_text)
        data_points = [float(m.replace(',', '')) for m in matches if 1000 < float(m.replace(',', '')) < 1000000]
        if data_points:
            return sum(data_points[:20]) / len(data_points[:20]), len(data_points[:20])
    except Exception as e: print(f"DEBUG Mercari Error: {e}")
    return 0, 0

def main(input_path, output_path, status_label, progress_bar, app, mode, fee, ship, margin, rate, start_button):
    df = pd.read_csv(input_path, encoding='utf-8')
    if df is not None:
        options = Options()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_argument('--blink-settings=imagesEnabled=false')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        try:
            total = len(df)
            avg_prices, counts = [], []
            for i, name in enumerate(df['商品名'], 1):
                progress_value = i / total
                status_text = f"【{mode}モード: {i}/{total}件】\n検索中: {name[:20]}..."
                app.after(0, lambda p=progress_value, t=status_text: (progress_bar.set(p), status_label.configure(text=t, text_color="orange")))
                
                # モード分岐
                if mode == "eBay":
                    avg_p, c = get_ebay_average(driver, name)
                elif mode == "メルカリ":
                    avg_p, c = get_mercari_average(driver, name)
                else:
                    avg_p, c = get_yahoo_average(driver, name)
                
                avg_prices.append(avg_p)
                counts.append(c)
                time.sleep(1.2) # BAN防止
            
            df['平均価格'] = avg_prices
            df['落札件数'] = counts
            df['損益分岐点'] = df['平均価格'].apply(lambda x: int(x * (1 - fee) - ship) if x > 0 else 0)
            df['目標仕入れ値'] = df['平均価格'].apply(lambda x: int(x * (1 - fee - margin) - ship) if x > 0 else 0)
            
            df.loc[df['損益分岐点'] < 0, '損益分岐点'] = 0
            df.loc[df['目標仕入れ値'] < 0, '目標仕入れ値'] = 0
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            final_text = f"✅ {mode}完了！\n保存: {os.path.basename(output_path)}"
            app.after(0, lambda t=final_text: status_label.configure(text=t, text_color="lightgreen"))
        finally:
            driver.quit()
            app.after(0, lambda: start_button.configure(state="normal"))

def start_gui():
    ctk.set_appearance_mode("dark")
    app = ctk.CTk()
    app.title("相場チェッカー 三種の神器Edition")
    app.geometry("700x750")

    input_file_path = ctk.StringVar(value="未選択")
    output_file_path = ctk.StringVar(value="未選択")

    ctk.CTkLabel(app, text="相場チェッカー", font=("Meiryo", 22, "bold")).pack(pady=20)
    progress_bar = ctk.CTkProgressBar(app, width=400)
    progress_bar.pack(pady=10); progress_bar.set(0)

    setting_frame = ctk.CTkFrame(app)
    setting_frame.pack(pady=10, padx=40, fill="x")
    
    # 入力フィールド
    ctk.CTkLabel(setting_frame, text="販売手数料 (%)").grid(row=1, column=0, padx=10, pady=5)
    fee_entry = ctk.CTkEntry(setting_frame, width=70); fee_entry.insert(0, "10"); fee_entry.grid(row=1, column=1)
    ctk.CTkLabel(setting_frame, text="想定送料 (円)").grid(row=1, column=2, padx=10, pady=5)
    ship_entry = ctk.CTkEntry(setting_frame, width=90); ship_entry.insert(0, "800"); ship_entry.grid(row=1, column=3)
    ctk.CTkLabel(setting_frame, text="目標利益率 (%)").grid(row=2, column=0, padx=10, pady=5)
    margin_entry = ctk.CTkEntry(setting_frame, width=70); margin_entry.insert(0, "10"); margin_entry.grid(row=2, column=1)

    # モード切替（メルカリ追加！）
    mode_var = ctk.StringVar(value="ヤフオク")
    mode_switch = ctk.CTkSegmentedButton(app, values=["ヤフオク", "eBay", "メルカリ"], variable=mode_var)
    mode_switch.pack(pady=20)

    def select_input():
        path = filedialog.askopenfilename(filetypes=[("CSVファイル", "*.csv")])
        if path:
            input_file_path.set(path)
            output_file_path.set(path.replace(".csv", "_result.csv"))

    ctk.CTkButton(app, text="① CSVを選択", command=select_input).pack(pady=5)
    ctk.CTkLabel(app, textvariable=input_file_path, font=("Meiryo", 10), text_color="gray").pack()
    
    status_label = ctk.CTkLabel(app, text="待機中", font=("Meiryo", 14))
    status_label.pack(pady=20)

    def on_start():
        if input_file_path.get() == "未選択": return
        start_button.configure(state="disabled")
        threading.Thread(target=main, args=(
            input_file_path.get(), output_file_path.get(), status_label, progress_bar, app, 
            mode_var.get(), float(fee_entry.get())/100, int(ship_entry.get()), float(margin_entry.get())/100, 1.0, start_button
        ), daemon=True).start()

    start_button = ctk.CTkButton(app, text="相場取得スタート", command=on_start, fg_color="green", hover_color="darkgreen")
    start_button.pack(pady=20)
    app.mainloop()

if __name__ == "__main__":
    start_gui()