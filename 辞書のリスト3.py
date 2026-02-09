def check_limit(data_list):
    total = sum(item["time"] for item in data_list)
    return total

def main():
    
    todo_list = []

    """
    todo_list.append({"name": "掃除", "time": 1})
    todo_list.append({"name": "Python学習", "time": 2})
    todo_list.append({"name":"料理","time":1})
    """
    # 初期値入力
    todo_list.extend([
        {"name": "掃除", "time": 1},
        {"name": "Python学習", "time": 2},
        {"name":"料理","time":1}
    ])


    # ユーザー入力
    print("--- タスク登録 （'None'と入力で終了）---")
    while True:
        new_task_name = input("タスク名を入力してください: ")

        if new_task_name == "None":
            break
        
        # 時間の入力
        new_task_time = int(input(f"「{new_task_name}」の時間を入力してください: "))
        
        # リストに追加
        todo_list.append({"name": new_task_name, "time": new_task_time})
    
    """
    new_task_name = "Javascript勉強"
    new_task_time = 3
    todo_list.append({"name": new_task_name, "time": new_task_time})
    """

    total = check_limit(todo_list)
    print(f"現在の合計時間は {total} 時間です。")
    # ルールとの照合（1日は24時間 - 睡眠7時間 = 活動可能17時間）
    limit_hours = 17 
    if total > limit_hours:
        print("⚠️ 警告：活動時間が17時間を超えています！7時間の睡眠が確保できません！")
    else:
        print("✅ 順調です。しっかり睡眠も確保できそうですね。")


if __name__ == "__main__":
    main()

"""
【本日の学習サマリー】
・辞書のリスト ＝ 構造化されたCSVのようなもの
・算術代入演算子（+= 等）の活用
・データとロジックの分離（引数の活用）
・リスト操作（append / extend）
・whileループとinputによる対話実装
・内包表記によるスマートな集計
"""