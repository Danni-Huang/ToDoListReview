$(document).ready(function () {
    let _todoItemsMsg = $('#todoItemsMsg');
    let _todoItemsList = $('#todoItemsList');
    let _newTodoMsg = $('#newTodoMsg');
    let _taskCategory = $('#taskCategory');

    let _tasksLastModified = new Date(1970, 0, 1);

    let _taskApiHome = 'https://localhost:7187/task-api'
    let _tasksUrl = null;

    $('input[type=datetime]').datepicker({
        changeMonth: true,
        changeYear: true
    });

    let getDateString = function (d) {
        return `${d.getFullYear()}-${d.getMonth() + 1}-${d.getDate()}`;
    };

    let loadInitialData = async function () {
        let resp = await fetch(_taskApiHome, {
            mode: 'cors',
            headers: {
                'Accept': 'application/json'
            }
        });

        if (resp.status === 200) {
            let apiHomeResult = await resp.json();
            let links = apiHomeResult.links;
            _taskUrl = links["tasks"].href;

            let catogriesResp = await fetch(links['categories'].href, {
                mode: 'cors',
                headers: {
                    'Accept': 'application/json'
                }
            });

            if (catogriesResp.status === 200) {
                let categories = await catogriesResp.json();
                for (let i = 0; i < categories.length; i++) {
                    _taskCategory.append(`<option value=\"${categories[i]}\">${categories[i]}</option>`);
                }
            }
        } else {
            _todoItemsMsg.text('hmmmm, there was a problem accessing the tasks Api');
            _todoItemsMsg.attr('class', 'text-danger');
            _todoItemsMsg.fadeOut(10000);
        }
    };

    let loadToDos = async function () {
        let resp = await fetch(_taskUrl, {
            mode: 'cors',
            headers: {
                'Accept': 'application/json'
            }
        });

        if (resp.status === 200) {
            let tasksResult = await resp.json();
            let tasks = tasksResult.tasks;

            if (tasks.length === 0) {
                _todoItemsMsg.text('no tasks to display');
            } else {
                let latestLastModified = new Date(tasksResult.tasksLastModified);
                if (latestLastModified.getTime() > _tasksLastModified.getTime()) {
                    _tasksLastModified = latestLastModified;

                    _todoItemsList.empty();

                    for (let i = 0; i < tasks.length; i++) {
                        _todoItemsList.append('<li>\"' + tasks[i].description + '\" (ID: ' +
                            tasks[i].taskId + ') is in ' + tasks[i].status + ' status and category: ' +
                            tasks[i].category + ' and is due: ' + getDateString(new Date(tasks[i].dueDate)) + '</li > ');
                    }
                }         
            }
        } else {
            _todoItemsMsg.text('hmmmm, there was a problem loading the tasks');
            _todoItemsMsg.attr('class', 'text-danger');
            _todoItemsMsg.fadeOut(10000);
        }
        
        _todoItemsMsg.text('# task is: ' + tasks.length);
    };

    $('#addTaskBtn').click(async function () {
        let dueDate = new Date($('#taskDueDate').val());

        let newTask = {
            description: $('#taskDescription').val(),
            dueDate: dueDate.toISOString(),
            category: $('#taskCategory').val()
        };

        let resp = await fetch(_tasksUrl, {
            mode: 'cors',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(newTask)
        });

        if (resp.status === 201) {
            _newTodoMsg.text('adding the task successfully');
            _newTodoMsg.attr('class', 'text-success');
            $('#taskDescription').val('');
        } else {
            _newTodoMsg.text('hmmmm, there was a problem adding the tasks');
            _newTodoMsg.attr('class', 'text-danger');
        }
        _newTodoMsg.fadeOut(10000);
    });

    loadInitialData();

    loadToDos();

    setInterval(loadToDos, 1000);
});