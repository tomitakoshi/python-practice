import json
import os

DATA_FILE = 'expenses.json'
BUDGET = 40000  # 月間予算　あとで変更可能にする

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_expense(date, amount, category):
    data = load_data()
    new_entry = {
        "date": date,
        "amount": int(amount),
        "category": category
    }
    data.append(new_entry)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_summary():
    data = load_data()
    total = sum(item['amount'] for item in data)
    remaining = BUDGET - total
    return total, remaining