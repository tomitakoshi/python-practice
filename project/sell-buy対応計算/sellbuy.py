import customtkinter as ctk

class ProfitCalculator:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        self.app = ctk.CTk()
        self.app.title("GN利益戦略シミュレーター")
        self.app.geometry("450x550")
        self.app.attributes("-topmost", True)

        # --- 定数---
        self.FEE_SELLING = 0.12  # 販売手数料 12% ヤフオク
        self.FEE_BUYING  = 0.10  # 古物市場手数料 10%

        self.create_widgets()

    def create_widgets(self):
        # タイトル
        ctk.CTkLabel(self.app, text="利益シミュレーター", font=("Meiryo", 24, "bold"), text_color="#3b8ed0").pack(pady=20)

        # 入力エリア
        input_frame = ctk.CTkFrame(self.app, fg_color="transparent")
        input_frame.pack(pady=20)

        # 想定売価
        ctk.CTkLabel(input_frame, text="1. 想定売価 (円)", font=("Meiryo", 14)).grid(row=0, column=0, padx=10, pady=5)
        self.price_entry = ctk.CTkEntry(input_frame, placeholder_text="100,000", width=150, font=("Meiryo", 16))
        self.price_entry.grid(row=1, column=0, padx=10, pady=5)
        self.price_entry.bind("<KeyRelease>", self.calculate)

        # ほしい利益率
        ctk.CTkLabel(input_frame, text="2. 目標利益率 (%)", font=("Meiryo", 14)).grid(row=0, column=1, padx=10, pady=5)
        self.margin_entry = ctk.CTkEntry(input_frame, width=150, font=("Meiryo", 16))
        self.margin_entry.insert(0, "10") # デフォルト10%
        self.margin_entry.grid(row=1, column=1, padx=10, pady=5)
        self.margin_entry.bind("<KeyRelease>", self.calculate)

        # --- 結果表示エリア ---
        result_frame = ctk.CTkFrame(self.app, fg_color="#2b2b2b", corner_radius=15)
        result_frame.pack(pady=20, padx=30, fill="both")

        # 損益分岐点
        ctk.CTkLabel(result_frame, text="損益分岐点（赤字回避）", font=("Meiryo", 12), text_color="gray").pack(pady=(15,0))
        self.breakeven_lbl = ctk.CTkLabel(result_frame, text="¥0", font=("Meiryo", 32, "bold"), text_color="#FF4444")
        self.breakeven_lbl.pack()

        # 仕入限界
        ctk.CTkLabel(result_frame, text="目標仕入額（利益確保）", font=("Meiryo", 14), text_color="#FFCC00").pack(pady=(15,0))
        self.target_lbl = ctk.CTkLabel(result_frame, text="¥0", font=("Meiryo", 48, "bold"), text_color="#FFCC00")
        self.target_lbl.pack(pady=(0, 20))

        # 構成の内訳
        self.detail_lbl = ctk.CTkLabel(self.app, text="内訳: 販売手数料10% + 仕入経費10% を自動控除", font=("Meiryo", 11), text_color="gray")
        self.detail_lbl.pack(side="bottom", pady=20)

    def calculate(self, event=None):
        try:
            # 入力値の取得
            price = float(self.price_entry.get().replace(',', ''))
            margin = float(self.margin_entry.get()) / 100

            # 計算実行
            # 損益分岐
            breakeven = int(price * (1 - self.FEE_SELLING - self.FEE_BUYING))
            # 仕入限界
            target = int(price * (1 - self.FEE_SELLING - self.FEE_BUYING - margin))

            # 表示更新（マイナスになる場合は0表示）
            self.breakeven_lbl.configure(text=f"¥{max(0, breakeven):,}")
            self.target_lbl.configure(text=f"¥{max(0, target):,}")

        except ValueError:
            self.breakeven_lbl.configure(text="¥0")
            self.target_lbl.configure(text="¥0")

    def run(self):
        self.app.mainloop()

if __name__ == "__main__":
    app = ProfitCalculator()
    app.run()