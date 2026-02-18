import json

class TodoApp:
    def __init__(self):
        self.file_name = "tasks.json"
        self.tasks = self.load_tasks()
        print("Todoアプリ起動完了")

    def add_task(self, task_name):
        # 「自分の持ち物（self.tasks）」にデータを追加する
        self.tasks.append(task_name)
        self.save_tasks()
        print(f"タスク『{task_name}』を追加しました！")

    def show_tasks(self):
        if not self.tasks:
            print("タスクはまだありません。")
        else:
            print(f"現在のタスク一覧: {self.tasks}")

    def load_tasks(self):
        try:
            with open(self.file_name, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return [] # ファイルがない、または壊れている時は空リストを返す

    def save_tasks(self):
        with open(self.file_name, "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=4)

    def remove_task(self, task_name):
        if task_name in self.tasks:
            self.tasks.remove(task_name)
            self.save_tasks() # 消した後も忘れずに保存！
            print(f"タスク『{task_name}』を削除しました。")
        else:
            print(f"『{task_name}』は見つかりませんでした。")

def main():
    app = TodoApp()
    app.show_tasks()
    
    while True:
        t_f = input("タスクを追加する場合はt/削除する場合はf")
        if t_f == "t":
            new_task = input("追加するタスクを入力してください: ")
            app.add_task(new_task)
            break

        elif t_f == "f":
            del_task = input("削除するタスク名を入力してください")
            app.remove_task(del_task)
            break

        else:
            print("もう一度入力してください")

if __name__ == "__main__":
    main()


    
