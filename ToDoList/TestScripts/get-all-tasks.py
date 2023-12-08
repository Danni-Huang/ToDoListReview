import requests
import json


def get_all_tasks():
	url = "https://localhost:7187/tasks"

	headers = {
		'Content-Type' : "apllication/json"
	}

	resp = requests.get(url, headers=headers, verify=False)

	return resp.json()


def write_tasks_to_file(task_data):
	for t in task_data:
		curr_task_id = t['taskId']
		task_file = open(f'data/{curr_task_id}.json', 'w')

		task_file.write(json.dumps(t, indent=4))

		task_file.close()


tasks = get_all_tasks()
write_tasks_to_file(tasks)