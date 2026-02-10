def check_limit(data_list):
    total = sum(item["time"] for item in data_list)
    return total

def check_hw(data_list):
    total_hw = sum(item["time"] for item in data_list if item["is_hw"] == True)
    return total_hw

def make_task():
    
    new_task_name = input("タスク名を入力してください（'None'と入力で終了）: ")

    if new_task_name == "None":
        return None
    
    else:
        new_task_time = float(input(f"「{new_task_name}」の時間を入力してください: "))
        is_hw_qs = input("これは家事ですか？y/n")
        is_hw_an = True if is_hw_qs.lower() == 'y' else False
        return {"name": new_task_name, "time": new_task_time, "is_hw":is_hw_an}


def main():
    
    todo_list = []

    # 初期値入力
    todo_list.extend([
        {"name": "掃除", "time": 1,"is_hw":True},
        {"name": "Python学習", "time": 2,"is_hw":False},
        {"name":"料理","time":1,"is_hw":True}
    ])


    # ユーザー入力
    print("--- タスク登録開始---")
    while True:
        new_task = make_task()
        if new_task is None:
            break
        todo_list.append(new_task)
        """
        # リストに追加
        todo_list.append({"name": new_task_name, "time": new_task_time, "is_hw":is_hw_an})
        """





    total = check_limit(todo_list)
    total_hw = check_hw(todo_list)
    print(f"現在の合計時間は {total} 時間です。")
    print(f"家事の合計時間は{total_hw}時間です")
    # ルールとの照合（1日は24時間 - 睡眠7時間 = 活動可能17時間）
    limit_hours = 17 
    if total > limit_hours:
        print("⚠️ 警告：活動時間が17時間を超えています！7時間の睡眠が確保できません！")
    else:
        print("✅ 順調です。しっかり睡眠も確保できそうですね。")


if __name__ == "__main__":
    main()

