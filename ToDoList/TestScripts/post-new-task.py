import requests
from datetime import datetime, timedelta
import json


headers = {
    'Content-Type': 'application/json'
}

# Note: your port number might be different
url = 'https://localhost:7187/tasks'

task_categories = ['Home', 'Work', 'Shopping']

task_desc = input('what is the descr of your task?')
task_category_index = int(input('what is the task category: 1) Home, 2) for work, 3): for shopping'))
num_days_due = int(input('how many days is the task due: '))

due_date = datetime.now() + timedelta(days=num_days_due)

new_task = {
    'description' : task_desc,
    'category' : task_categories[task_category_index - 1],
    'duedate' : due_date.isoformat()
}

resp = requests.post(url, json=new_task, verify=False)

if 'Location' in resp.headers:
    print(f'New task is at: {resp.headers["Location"]}')
else:
    print('hmm, there was a problem adding the task')
