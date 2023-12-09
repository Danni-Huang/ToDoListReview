using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using ToDoList.Models;

namespace ToDoList.Controllers
{
    [ApiController()]
    public class TaskApiController : Controller
    {
        public TaskApiController(ToDoContext toDoContext) 
        { 
            _toDoContext = toDoContext;
        }

        [HttpGet("task-api")]
        public async Task<IActionResult> GetApiHomeResult()
        {
            TaskApiViewModel viewModel = new TaskApiViewModel()
            {
                Links = new Dictionary<string, Link>()
                {
                    {"self", new Link() {Rel = "self", Href = GenerateFullUrl("/task-api")} },
                    {"tasks", new Link() {Rel = "tasks", Href = GenerateFullUrl("/api/tasks")} },
                    {"categories", new Link() {Rel = "categories", Href = GenerateFullUrl("/api/categories") } }
                },
                Version = "1.0",
                Creator = "Danni Huang"
            };
            return Ok(viewModel);
        }

        [HttpGet("/api/categories")]
        public async Task<IActionResult> GetAllCategories()
        {
            List<string> categories = await _toDoContext.Categories
                .OrderBy(c => c.Name)
                .Select(c => c.Name)
                .ToListAsync();

            if (categories == null || categories.Count == 0)
            {
                return NotFound();
            }

            return Ok(categories);
        }

        [Authorize()]
        [HttpGet("/api/tasks")]
        public async Task<IActionResult> GetAllTasks()
        {
            var categories = await _toDoContext.Categories.Select(c => c.Name).ToListAsync();

            // use db context to query for all ToDo entities and transform them
            List<TaskInfo> tasks = await _toDoContext.ToDos
                .Include(t => t.Category)
                .Include(t => t.Status)
                .OrderByDescending(t => t.DueDate)
                .Select(t => new TaskInfo()
                {
                    Description = t.Description,
                    DueDate = t.DueDate,
                    Status = t.Status.Name,
                    Category = t.Category.Name,
                    TaskId = t.Id
                })
                .ToListAsync();

            DateTime? tasksLastModified = new DateTime(1970, 1, 1);

            if (tasks.Count > 0)
            {
                tasksLastModified = await _toDoContext.ToDos.MaxAsync(t => t.LastModified);
            }

            TasksViewModel viewModel = new TasksViewModel()
            {
                Tasks = tasks,
                TasksLastModified = tasksLastModified,
                TaskCategories = categories
            };

            Response.Headers.LastModified = tasksLastModified?.ToUniversalTime().ToString("R");    

            return Ok(viewModel);
        }

        [Authorize()]
        [HttpGet("/api/tasks/{id}")]
        public async Task<IActionResult> GetTaskById(int id)
        {
            TaskInfo? tasks = await _toDoContext.ToDos
                .Include(t => t.Category)
                .Include(t => t.Status)
                .OrderByDescending(t => t.DueDate)
                .Select(t => new TaskInfo()
                {
                    Description = t.Description,
                    DueDate = t.DueDate,
                    Status = t.Status.Name,
                    Category = t.Category.Name,
                    TaskId = t.Id
                })
                .Where(t => t.TaskId == id)
                .FirstOrDefaultAsync();

            if (tasks == null)
            {
                return NotFound();
            }

            return Ok(tasks);
        }

        [Authorize()]
        [HttpPost("/api/tasks")]
        public async Task<IActionResult> AddNewTask(NewTaskRequest newTaskRequest)
        {
            Category category = await _toDoContext.Categories.Where(c => c.Name == newTaskRequest.Category).FirstOrDefaultAsync();

            DateTime? dueDate = newTaskRequest.DueDate == null ? DateTime.Now : newTaskRequest.DueDate;

            ToDo newTodo = new ToDo()
            {
                Description = newTaskRequest.Description,
                DueDate = dueDate,
                CategoryId = category.CategoryId,
                StatusId = "open"
            };

            _toDoContext.ToDos.Add(newTodo);
            await _toDoContext.SaveChangesAsync();

            TaskInfo task = new TaskInfo()
            {
                TaskId = newTodo.Id,
                DueDate = newTodo.DueDate,
                Description = newTaskRequest.Description,
                Category = newTaskRequest.Category,
                Status = "Open"
            };

            return CreatedAtAction(nameof(GetTaskById), new {id = task.TaskId}, task);
        }

        private string GenerateFullUrl(string path)
        {
            return $"{Request.Scheme}://{Request.Host}{path}";
        }

        private ToDoContext _toDoContext;
    }

}
