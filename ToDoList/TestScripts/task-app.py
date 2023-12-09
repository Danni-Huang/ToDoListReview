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
	login_url = result['links']['login']['href']
	register_url = result['links']['register']['href']

	return {'tasks_url': tasks_url, 
			'categories_url': categories_url, 
			'login_url': login_url,
			'register_url': register_url}    


def get_categories(categories_url):
	resp = requests.get(categories_url, verify=False)
	return resp.json()


# a helper function that adds the task using the web API, and
# returns true if successful, false otherwise:
def add_new_task(tasks_url, access_token, task_description, task_category, due_date):
	headers = {
		'Content-Type': 'application/json',
		'Authorization': f'Bearer {access_token}',
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
def get_all_tasks(tasks_url, access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    
    resp = requests.get(tasks_url, headers=headers, verify=False)
    
    result = {}
    if resp.status_code == 200:
        result['success'] = True
        
        task_result = resp.json()
        tasks = task_result['tasks']
        num_tasks = len(tasks)
        
        result['tasks'] = tasks
        
        if num_tasks == 0:
            result['message'] = 'Currently no tasks'
        else:
            result['message'] = f'Successfully retrieved {num_tasks} tasks'           
    elif resp.status_code == 401:
        result['success'] = False
        result['tasks'] = []
        result['message'] = 'You are not authorized to do this - please log in first'
    else:
        result['success'] = False
        result['tasks'] = []
        result['message'] = 'There was a problem adding the new task'

    return result  


# Next are the 3 fns to handle user requests...
def handle_load_tasks(tasks_url, access_token):
    print('Loading tasks..')
    
    # TODO: error handling should be better:
    try:
        task_file = open('raw-task-data.txt', 'r')
        success = True
        for line in task_file.readlines():
            task_components = [c.strip() for c in line.split('|')]

            due_date = datetime.strptime(task_components[2], '%Y-%m-%d')
            result = add_new_task(tasks_url, access_token, task_components[0], task_components[1], due_date)
            
            if not result['success']:
                print(result['message'])
                success = False
                break

        if success:
            print('Tasks loaded successfully!\n')
    except:
        print('Sorry, there was a problem loading tasks :(\n')
		

def get_task_summary(task):
	return f'Task: \"{task["description"]}\" (Category: {task["category"]}) is due {task["dueDate"]} and is in {task["status"]} status'

def handle_random_task(tasks_url, access_token):
	result = get_all_tasks(tasks_url, access_token)
	if result['success']:
		all_tasks = result['tasks']
		
		if len(all_tasks) > 0: 
			random_task = random.choice(all_tasks)
			print(f'The randomly selected task is...\n{get_task_summary(random_task)}')
		else:
			print('Currently no tasks to randomly select - add some and try again!')
	else:
		print(result['message'])

def handle_new_task(tasks_url, task_categories, access_token):
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

	result = add_new_task(tasks_url, access_token, task_description, task_categories[task_category_index - 1], due_date)

	if result['success']:
		print('The new task was added successfully!\n')
	else:
		print(result['message'])

def handle_register_user(register_url):
	first_name = input('First name? ')
	last_name = input('Last name? ')
	username = input('Username? ')
	password = input('Password? ')
	email = input('Email? ')
	phone_number = input('Phone number? ')
	
	result = register_user(register_url, first_name, last_name, username, password, email, phone_number)
	print(result['message'] + '\n')


def register_user(register_url, first_name, last_name, username, password, email, phone_number):
	headers = {
		'Content-Type': 'application/json'
	}

	# hard-code the presence of the QuoteManager role
	register_request = {
		'firstName': first_name,
		'lastName': last_name,
		'userName': username,
		'password': password,
		'email': email,
		'phoneNumber': phone_number,
		'roles': ['TASK_MANAGER']
	}

	resp = requests.post(register_url, headers=headers, json=register_request, verify=False)

	result = {}
	if resp.status_code == 201:
		result['success'] = True        
		result['message'] = 'User registered successfully'
	else:
		result['success'] = False
		if resp.status_code == 400:
			result['message'] = 'The email or user name is already taken.'
		else:
			result['message'] = 'There was a problem registering this new user'

	return result

def handle_login(login_url):
	username = input('Username? ')
	password = input('Password? ')
	
	result = login_user(login_url, username, password)
	print(result['message'] + '\n')

	return result['token']

def login_user(login_url, username, password):
	headers = {
		'Content-Type': 'application/json'
	}

	login_request = {
	  'userName': username,
	  'password': password
	}

	resp = requests.post(login_url, headers=headers, json=login_request, verify=False)

	result = {}
	if resp.status_code == 200:
		result['success'] = True        
		login_result = resp.json()
		result['token'] = login_result['token']
		result['message'] = 'Logged in successfully'
	else:
		result['success'] = False
		result['token'] = ''
		result['message'] = 'There was a problem logging in'

	return result
	

# set up the app:
api_info = get_api_info()

tasks_url = api_info['tasks_url']
categories_url = api_info['categories_url']
register_url = api_info['register_url']
login_url = api_info['login_url']

task_categories = get_categories(categories_url)

# and then go into the main menu-driven app cycle:
done = False
main_title = '\n\nWhat do you want to do? '
main_options = ['Register a user', 'Log in','Load tasks from file', 'Randomly select an open task', 'Add a new task', 'Quit']

access_token = ''

while not done:
	print('\n' + '\n'.join([f'{i+1}). {main_options[i]}' for i in range(len(main_options))]))    
	main_index = int(input(main_title)) - 1
  
	if main_index == 0:
		handle_register_user(register_url)
	elif main_index == 1:
		access_token = handle_login(login_url)
	elif main_index == 2:
		handle_load_tasks(tasks_url, access_token)
	elif main_index == 3:
		handle_random_task(tasks_url, access_token)
	elif main_index == 4:
		handle_new_task(tasks_url, task_categories, access_token)
	else:
		print('\n\nGoodbye!\n')
		done = True

