import requests
import random
from datetime import datetime, timedelta
import json

# Note: you can run suppressing warnings to avoid getting the self-signed cert warnings:
# >python -W "ignore" task-app.py

# Note: your port number might be different
task_api_url = 'https://localhost:7187/task-api'

# some helper fns to load the client with info from the API:
def get_api_info():
    resp = requests.get(task_api_url, verify=False)
    result = resp.json()
    
    tasks_url = result['links']['tasks']['href']
    categories_url = result['links']['categories']['href']

    return {'tasks_url': tasks_url, 'categories_url': categories_url}    


def get_categories(categories_url):
    resp = requests.get(categories_url, verify=False)
    return resp.json()


# a helper function that adds the task using the web API, and
# returns true if successful, false otherwise:
def add_new_task(tasks_url, task_description, task_category, due_date):
    headers = {
        'Content-Type': 'application/json'
    }

    new_task = {
      'description': task_description,
      'category': task_category,
      'dueDate': due_date.isoformat()
    }

    resp = requests.post(tasks_url, headers=headers, json=new_task, verify=False)

    # return resp.status_code == 201 and 'Location' in resp.headers
    result = {}
    if resp.status_code == 201 and 'Location' in resp.headers:
        result['success'] = True
        result['message'] = 'New task added successfully'
    elif resp.status_code == 401:
        result['success'] = False
        result['message'] = 'You are not authorized to do this - please log in first'
    else:
        result['success'] = False
        result['message'] = 'There was a problem adding the new task'

    return result


# Another helper fn to get all tasks:
def get_all_tasks(tasks_url):
    resp = requests.get(tasks_url, verify=False)
    result = resp.json()
    return result['tasks']


# Next are the 3 fns to handle user requests...
def handle_load_tasks(tasks_url):
    print('Loading tasks..')
    
    # TODO: error handling should be better:
    try:
        task_file = open('raw-task-data.txt', 'r')
        for line in task_file.readlines():
            task_components = [c.strip() for c in line.split('|')]

            due_date = datetime.strptime(task_components[2], '%Y-%m-%d')
            task_added_successfully = add_new_task(tasks_url, task_components[0], task_components[1], due_date)
        
        print('Tasks loaded successfully!\n')
    except:
        print('Sorry, there was a problem loading tasks :(\n')
        

def handle_random_task(tasks_url):
    all_tasks = get_all_tasks(tasks_url)
    random_task = random.choice(all_tasks)    
    print(f'The randomly selected task is...\nTask: {random_task["description"]}\nCategory: {random_task["category"]}')

def handle_new_task(tasks_url, task_categories):
    task_description = input('What is your task? ')
    num_days_due = int(input('In how many days is the task due? '))
    
    categories_str = '\n'.join([f'{i+1}). {task_categories[i]}' for i in range(len(task_categories))])
    print(f'Choose your category. The options are...\n{categories_str}\n')
    task_category_index = int(input('What category? '))

    due_date = datetime.now() + timedelta(days=num_days_due)

    #task_added_successfully = add_new_task(tasks_url, task_description, task_categories[task_category_index - 1], due_date)

    #if task_added_successfully:
        #print('The new task was added successfully!\n')
    #else:
        #print('Hmmm, sorry, there was a problem adding your new task.\n')

    result = add_new_task(tasks_url, task_description, task_categories[task_category_index - 1], due_date)

    if result['success']:
        print('The new task was added successfully!\n')
    else:
        print(result['message'])

    

# set up the app:
api_info = get_api_info()

tasks_url = api_info['tasks_url']
categories_url = api_info['categories_url']

task_categories = get_categories(categories_url)

# and then go into the main menu-driven app cycle:
done = False
main_title = '\n\nWhat do you want to do? '
main_options = ['Load tasks from file', 'Randomly select an open task', 'Add a new task', 'Quit']

while not done:
    print('\n' + '\n'.join([f'{i+1}). {main_options[i]}' for i in range(len(main_options))]))    
    main_index = int(input(main_title)) - 1
    
    if main_index == 0:
        handle_load_tasks(tasks_url)
    elif main_index == 1:
        handle_random_task(tasks_url)
    elif main_index == 2:
        handle_new_task(tasks_url, task_categories)
    else:
        print('\n\nGoodbye!\n')
        done = True

