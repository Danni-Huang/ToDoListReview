namespace ToDoAppConsoleClient
{
    public class TaskInfo : NewTaskRequest
    {
        public int? TaskId { get; set; }
        public string? Status { get; set; } = "Open";
    }
}
