
todo_list = []

"""
todo_list.append({"name": "掃除", "time": 1})
todo_list.append({"name": "Python学習", "time": 2})
todo_list.append({"name":"料理","time":1})
"""

todo_list.extend([
    {"name": "掃除", "time": 1},
    {"name": "Python学習", "time": 2},
    {"name":"料理","time":1}
])

print(todo_list)

