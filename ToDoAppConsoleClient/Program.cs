using System.Net.Http.Json;
using Newtonsoft.Json;

namespace ToDoAppConsoleClient
{
    public class Program
    {
        public static void Main(string[] args)
        {
            AddNewTask();
            GetAllTasks();
        }

        public static void GetAllTasks()
        {
            HttpClient client = new HttpClient();

            HttpResponseMessage resp = client.GetAsync("https://localhost:7187/tasks").Result;

            if (resp.StatusCode == System.Net.HttpStatusCode.OK)
            {
                List<TaskInfo> tasks = resp.Content.ReadFromJsonAsync<List<TaskInfo>>().Result;
                foreach(var task in tasks)
                {
                    Console.WriteLine($"Task ID: {task.TaskId};" +
                        $"description: {task.Description} ({task.Category}) " +
                        $"is due: {task.DueDate:d} and has status: {task.Status}");
                }
            }
            else
            {
                Console.WriteLine("there was a problem reading the tasks");
            }

        }

        public static void AddNewTask()
        {
            HttpClient client = new HttpClient();

            NewTaskRequest request = new NewTaskRequest()
            {
                Description = "Test C# Console client",
                Category = "Home",
                DueDate = DateTime.Now.AddDays(2)
            };

            StringContent taskContent = new StringContent(JsonConvert.SerializeObject(request), System.Text.Encoding.UTF8,
                "application/json");

            HttpResponseMessage resp = client.PostAsync("https://localhost:7187/tasks", taskContent).Result;

            if (resp.StatusCode == System.Net.HttpStatusCode.Created)
            {
                Console.WriteLine("created successfully.");
            }
            else
            {
                Console.WriteLine("there was problem adding new task");
            }
        }
    }
}