import customtkinter as ctk
import pandas as pd
from tkinter import filedialog

class AuctionBattleViewer:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        self.app = ctk.CTk()
        self.app.title("せりナビ")
        self.app.geometry("600x650")
        self.app.attributes("-topmost", True)

        self.df = None
        self.idx = 0

        self.create_widgets()
        self.app.bind("<Right>", self.next_item)
        self.app.bind("<Left>", self.prev_item)

    def create_widgets(self):
        # 1. ファイル読み込み（現場では最初に1回やるだけ）
        self.load_btn = ctk.CTkButton(self.app, text="CSVを読み込む", command=self.load_csv)
        self.load_btn.pack(pady=10)

        # 2. 箱番・商品No（小さく表示）
        self.meta_lbl = ctk.CTkLabel(self.app, text="箱番: -- / No: --", font=("Meiryo", 16))
        self.meta_lbl.pack(pady=5)

        # 3. 商品名
        self.name_lbl = ctk.CTkLabel(self.app, text="商品を選択してください", font=("Meiryo", 20, "bold"), wraplength=500)
        self.name_lbl.pack(pady=15)

        # --- ここからメインの情報エリア ---
        
        # 4. 損益分岐点（赤色・巨大）
        ctk.CTkLabel(self.app, text="▼ 損益分岐点（赤字ライン）", font=("Meiryo", 14), text_color="gray").pack()
        self.breakeven_lbl = ctk.CTkLabel(self.app, text="¥0", font=("Meiryo", 72, "bold"), text_color="#FF4444")
        self.breakeven_lbl.pack(pady=10)

        # スペーサー
        ctk.CTkLabel(self.app, text="").pack(pady=5)

        # 5. 目標仕入れ値（黄色・超巨大）
        ctk.CTkLabel(self.app, text="▼ 目標仕入れ値（利益確保）", font=("Meiryo", 14), text_color="gray").pack()
        self.target_lbl = ctk.CTkLabel(self.app, text="¥0", font=("Meiryo", 96, "bold"), text_color="#FFCC00")
        self.target_lbl.pack(pady=10)

        # 6. 操作ガイド
        ctk.CTkLabel(self.app, text="[←] 前へ / [→] 次へ", font=("Meiryo", 14), text_color="gray").pack(side="bottom", pady=20)

    def load_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSVファイル", "*.csv")])
        if path:
            self.df = pd.read_csv(path)
            self.idx = 0
            self.update_display()
            self.load_btn.pack_forget() # 読み込んだらボタンは消して画面を広く使う

    def update_display(self):
        if self.df is None or len(self.df) == 0: return
        row = self.df.iloc[self.idx]
        
        # 各種データの抽出
        box_no = row.get('箱番', '--')
        item_no = row.get('商品No', '--')
        name = row.get('商品名', '不明')
        breakeven = row.get('損益分岐点', 0)
        target = row.get('目標仕入れ値', 0)

        # 表示更新
        self.meta_lbl.configure(text=f"箱番: {box_no}  /  商品No: {item_no}")
        self.name_lbl.configure(text=name)
        self.breakeven_lbl.configure(text=f"¥{int(breakeven):,}")
        self.target_lbl.configure(text=f"¥{int(target):,}")

    def next_item(self, event=None):
        if self.df is not None and self.idx < len(self.df) - 1:
            self.idx += 1
            self.update_display()

    def prev_item(self, event=None):
        if self.df is not None and self.idx > 0:
            self.idx -= 1
            self.update_display()

if __name__ == "__main__":
    viewer = AuctionBattleViewer()
    viewer.app.mainloop()