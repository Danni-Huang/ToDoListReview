using Microsoft.AspNetCore.Identity;

namespace ToDoList.Models
{
    public class User : IdentityUser
    {
        public string? FirstName { get; set; }
        public string? LastName { get; set; }
    }
}
