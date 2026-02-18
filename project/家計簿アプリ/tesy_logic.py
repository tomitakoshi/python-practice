import function
import os

# 既存のテストデータを一旦リセット（もしあれば）
if os.path.exists('expenses.json'):
    os.remove('expenses.json')

print("--- テスト開始 ---")

# 保存関数のテスト
function.save_expense("2026-02-13", 1200, "食費")
function.save_expense("2026-02-13", 3000, "娯楽")
print("2件のデータを保存しました。")

# 読み込みと計算のテスト
total, remaining = function.get_summary()

print(f"期待される合計: 4200 / 実際の合計: {total}")
print(f"期待される残高: 45800 / 実際の残高: {remaining}")

if total == 4200:
    print("ロジックチェック：合格！")
else:
    print("ロジックに不備があります。")