#Claude案

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

# =====================================
# 固定定数
# =====================================
SITE_FEE   = 0.10  # 各サイト販売手数料（固定10%）
FURYO_FEE  = 0.12  # 古物市場仕入れ手数料（固定12%）

# =====================================
# 計算ロジック
# =====================================
def calc_breakeven(avg_price: float) -> int:
    """損益分岐点 = x * 0.9 / 1.12"""
    if avg_price <= 0:
        return 0
    return int(avg_price * (1 - SITE_FEE) / (1 + FURYO_FEE))

def calc_target_price(avg_price: float, margin: float) -> int:
    """理想仕入れ価格 = x * 0.9 * (1 - a) / 1.12"""
    if avg_price <= 0:
        return 0
    return int(avg_price * (1 - SITE_FEE) * (1 - margin) / (1 + FURYO_FEE))

# =====================================
# スクレイピング
# =====================================
def build_chrome_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument('--blink-settings=imagesEnabled=false')
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def get_yahoo_average(driver, product_name: str) -> tuple[float, int]:
    clean_name = product_name.replace('/', ' ').strip()
    params = {'va': clean_name, 'ei': 'UTF-8', 'f_adv': 1, 'fr': 'auc_adv'}
    query_string = urllib.parse.urlencode(params, quote_via=urllib.parse.quote_plus)
    url = f"https://auctions.yahoo.co.jp/pastbidsearch/closedsearch?{query_string}"
    try:
        driver.get(url)
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        page_text = driver.find_element(By.TAG_NAME, "body").text
        match = re.search(r"平均\s*([\d,]+)円", page_text)
        count_match = re.search(r"([\d,]+)件", page_text)
        if match:
            avg_price = int(match.group(1).replace(',', ''))
            count = int(count_match.group(1).replace(',', '')) if count_match else 1
            return avg_price, count
    except:
        pass
    return 0, 0

def get_ebay_average(driver, product_name: str) -> tuple[float, int]:
    clean_name = urllib.parse.quote(product_name)
    url = f"https://www.ebay.com/sch/i.html?_nkw={clean_name}&LH_Sold=1&LH_Complete=1&LH_ItemCondition=3000&_ipg=24"
    try:
        driver.get(url)
        time.sleep(3)
        page_text = driver.find_element(By.TAG_NAME, "body").text
        pattern = r"(?:中古品|新品|今すぐ買う|[\d]+件の入札|オークション)\s+([\d,]+)\s*円"
        matches = re.findall(pattern, page_text)
        data_points = [float(m.replace(',', '')) for m in matches if 1000 < float(m.replace(',', '')) < 1000000]
        if data_points:
            return sum(data_points[:20]) / len(data_points[:20]), len(data_points[:20])
    except Exception as e:
        print(f"DEBUG eBay Error: {e}")
    return 0, 0

def get_mercari_average(driver, product_name: str) -> tuple[float, int]:
    clean_name = urllib.parse.quote(product_name)
    url = f"https://jp.mercari.com/search?keyword={clean_name}&status=sold_out"
    try:
        driver.get(url)
        time.sleep(3)
        page_text = driver.find_element(By.TAG_NAME, "body").text
        matches = re.findall(r"¥[\s\n]*([\d,]+)", page_text)
        data_points = [float(m.replace(',', '')) for m in matches if 1000 < float(m.replace(',', '')) < 1000000]
        if data_points:
            return sum(data_points[:20]) / len(data_points[:20]), len(data_points[:20])
    except Exception as e:
        print(f"DEBUG Mercari Error: {e}")
    return 0, 0

# =====================================
# メイン処理（単一サイト）
# =====================================
def main(input_path, output_path, status_label, progress_bar, app, mode, margin, start_button):
    df = pd.read_csv(input_path, encoding='utf-8')
    driver = build_chrome_driver()
    try:
        total = len(df)
        avg_prices, counts = [], []

        for i, name in enumerate(df['商品名'], 1):
            progress_value = i / total
            status_text = f"【{mode}モード: {i}/{total}件】\n検索中: {name[:20]}..."
            app.after(0, lambda p=progress_value, t=status_text: (
                progress_bar.set(p),
                status_label.configure(text=t, text_color="orange")
            ))

            if mode == "eBay":
                avg_p, c = get_ebay_average(driver, name)
            elif mode == "メルカリ":
                avg_p, c = get_mercari_average(driver, name)
            else:
                avg_p, c = get_yahoo_average(driver, name)

            avg_prices.append(avg_p)
            counts.append(c)
            time.sleep(1.2)

        df['平均価格']     = avg_prices
        df['落札件数']     = counts
        df['損益分岐点']   = df['平均価格'].apply(calc_breakeven)
        df['理想仕入れ価格'] = df['平均価格'].apply(lambda x: calc_target_price(x, margin))

        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        final_text = f"✅ {mode}完了！\n保存: {os.path.basename(output_path)}"
        app.after(0, lambda t=final_text: status_label.configure(text=t, text_color="lightgreen"))
    finally:
        driver.quit()
        app.after(0, lambda: start_button.configure(state="normal"))

# =====================================
# メイン処理（全サイト）
# =====================================
def main_all_sites(input_path, output_path, status_label, progress_bar, app, margin, start_button):
    df = pd.read_csv(input_path, encoding='utf-8')
    driver = build_chrome_driver()
    try:
        total = len(df)
        y_prices, e_prices, m_prices = [], [], []
        y_urls, e_urls, m_urls = [], [], []

        for i, name in enumerate(df['商品名'], 1):
            status_text = f"【全サイト調査: {i}/{total}件】\n解析中: {name[:15]}..."
            app.after(0, lambda p=i/total, t=status_text: (
                progress_bar.set(p),
                status_label.configure(text=t, text_color="cyan")
            ))

            y_url = f"https://auctions.yahoo.co.jp/pastbidsearch/closedsearch?va={urllib.parse.quote(name.replace('/', ' '))}"
            e_url = f"https://www.ebay.com/sch/i.html?_nkw={urllib.parse.quote(name)}&LH_Sold=1&LH_Complete=1&LH_ItemCondition=3000"
            m_url = f"https://jp.mercari.com/search?keyword={urllib.parse.quote(name)}&status=sold_out"

            yp, yc = get_yahoo_average(driver, name)
            ep, ec = get_ebay_average(driver, name)
            mp, mc = get_mercari_average(driver, name)

            y_prices.append(yp)
            e_prices.append(ep)
            m_prices.append(mp)
            y_urls.append(y_url)
            e_urls.append(e_url)
            m_urls.append(m_url)

            time.sleep(2.0)

        df['ヤフオク相場'] = y_prices
        df['ヤフオクURL']  = y_urls
        df['eBay相場']     = e_prices
        df['eBayURL']      = e_urls
        df['メルカリ相場'] = m_prices
        df['メルカリURL']  = m_urls

        df['最高値サイト'] = df[['ヤフオク相場', 'eBay相場', 'メルカリ相場']].idxmax(axis=1)
        df['最高価格']     = df[['ヤフオク相場', 'eBay相場', 'メルカリ相場']].max(axis=1)

        df['損益分岐点']   = df['最高価格'].apply(calc_breakeven)
        df['理想仕入れ価格'] = df['最高価格'].apply(lambda x: calc_target_price(x, margin))

        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        app.after(0, lambda: status_label.configure(text="✅ 全サイト統合調査完了！", text_color="lightgreen"))
    finally:
        driver.quit()
        app.after(0, lambda: start_button.configure(state="normal"))

# =====================================
# GUI
# =====================================
def start_gui():
    ctk.set_appearance_mode("dark")
    app = ctk.CTk()
    app.title("相場チェッカー ver5.0")
    app.geometry("700x700")

    input_file_path = ctk.StringVar(value="未選択")
    output_file_path = ctk.StringVar(value="未選択")

    ctk.CTkLabel(app, text="相場チェッカー", font=("Meiryo", 22, "bold")).pack(pady=20)
    progress_bar = ctk.CTkProgressBar(app, width=400)
    progress_bar.pack(pady=10)
    progress_bar.set(0)

    # 設定フレーム（利益率のみ）
    setting_frame = ctk.CTkFrame(app)
    setting_frame.pack(pady=10, padx=40, fill="x")

    ctk.CTkLabel(setting_frame, text="目標利益率 (%)").grid(row=0, column=0, padx=10, pady=10)
    margin_entry = ctk.CTkEntry(setting_frame, width=70)
    margin_entry.insert(0, "10")
    margin_entry.grid(row=0, column=1, pady=10)

    ctk.CTkLabel(setting_frame, text="※手数料はヤフオク/eBay/メルカリ=10%、古物市場=12%で固定", 
                 font=("Meiryo", 10), text_color="gray").grid(row=1, column=0, columnspan=3, padx=10, pady=2)

    # モード切替
    mode_var = ctk.StringVar(value="全サイト")
    ctk.CTkSegmentedButton(app, values=["ヤフオク", "eBay", "メルカリ", "全サイト"], variable=mode_var).pack(pady=20)

    def select_input():
        path = filedialog.askopenfilename(filetypes=[("CSVファイル", "*.csv")])
        if path:
            input_file_path.set(path)
            output_file_path.set(path.replace(".csv", "_result.csv"))

    ctk.CTkButton(app, text="① CSVを選択", command=select_input).pack(pady=5)
    ctk.CTkLabel(app, textvariable=input_file_path, font=("Meiryo", 10), text_color="gray").pack()

    def select_output():
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSVファイル", "*.csv")])
        if path:
            output_file_path.set(path)

    ctk.CTkButton(app, text="② 保存先を確認/変更", command=select_output, fg_color="transparent", border_width=1).pack(pady=5)
    ctk.CTkLabel(app, textvariable=output_file_path, font=("Meiryo", 10), text_color="gray").pack()

    status_label = ctk.CTkLabel(app, text="待機中", font=("Meiryo", 14))
    status_label.pack(pady=20)

    def on_start():
        if input_file_path.get() == "未選択":
            status_label.configure(text="❌ ファイルを選択してください", text_color="red")
            return
        try:
            margin = float(margin_entry.get()) / 100
        except ValueError:
            status_label.configure(text="❌ 利益率を正しく入力してください", text_color="red")
            return

        start_button.configure(state="disabled")
        mode = mode_var.get()

        if mode == "全サイト":
            args = (input_file_path.get(), output_file_path.get(), status_label,
                    progress_bar, app, margin, start_button)
            target_func = main_all_sites
        else:
            args = (input_file_path.get(), output_file_path.get(), status_label,
                    progress_bar, app, mode, margin, start_button)
            target_func = main

        threading.Thread(target=target_func, args=args, daemon=True).start()

    start_button = ctk.CTkButton(app, text="相場取得スタート", command=on_start,
                                  fg_color="green", hover_color="darkgreen")
    start_button.pack(pady=20)
    app.mainloop()

if __name__ == "__main__":
    start_gui()