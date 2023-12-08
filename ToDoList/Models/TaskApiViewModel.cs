namespace ToDoList.Models
{
    public class TaskApiViewModel
    {
        public IDictionary<string, Link> Links { get; set; }
        public string? Version { get; set; }
        public string? Creator { get; set; }
    }
}
