using ToDoList.Controllers;

namespace ToDoList.Models
{
    public class TasksViewModel
    {
        public List<TaskInfo>? Tasks { get; set; }
        public DateTime? TasksLastModified { get; set; }
        public List<string>? TaskCategories { get; set; }
    }
}
