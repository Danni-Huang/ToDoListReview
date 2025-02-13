﻿using System.ComponentModel.DataAnnotations;

namespace ToDoList.Controllers
{
    public class LoginRequest
    {
        [Required(ErrorMessage = "User name is required")]
        public string? UserName { get; set; }


        [Required(ErrorMessage = "Password name is required")]
        public string? Password { get; set; }
    }
}
