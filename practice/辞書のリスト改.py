tasks = [
    {"name": "Python学習", "time": 3},
    {"name": "勉強", "time": 2},
    {"name": "家事", "time": 1},
    {"name": "不明なタスク", "time": -1} # テスト用の異常値
]

def check_schedule(datas):
    total_time = 0
    
    for data in datas:
        #【ガード節】マイナスの時間があれば即座にエラーXを返す
        if data["time"] < 0:
            return f"エラーX：不明なエラー（{data['name']} の時間が不正です）"
        
        total_time += data["time"]
    
    #合計が8時間を超えたらエラー
    if total_time > 8:
        return f"エラーⅠ：ブッキング過多（合計 {total_time}時間）"
    
    return f"本日の予定は計 {total_time}時間です。順調ですね！"

def main():
    result = check_schedule(datas=tasks)
    print(result)

if __name__ == "__main__":
    main()