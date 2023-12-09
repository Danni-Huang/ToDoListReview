using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Mvc;
using ToDoList.Models;
using ToDoList.Services;

namespace ToDoList.Controllers
{
    [ApiController()]
    public class AccountApiController : Controller
    {
        public AccountApiController(IAuthService authService)
        {
            _authenticationService = authService;
        }

        [HttpPost("/api/register")]
        public async Task<IActionResult> RegisterUser(UserRegistrationRequest userRegistrationRequest)
        {

            var result = await _authenticationService.RegisterUser(userRegistrationRequest);

            if (result.Succeeded)
            {
                return StatusCode(201);
            }
            else
            {
                foreach ( var item in result.Errors)
                {
                    ModelState.AddModelError(item.Code, item.Description);
                }
                return BadRequest(ModelState);
            }
        }

        [HttpPost("/api/login")]
        public async Task<IActionResult> LoginUser(LoginRequest loginRequest)
        {
            bool loginSuccess = await _authenticationService.LoginUser(loginRequest);

            if (loginSuccess)
            {
                return Ok(new { Token = await _authenticationService.CreateToken() });
            }
            else
            {
                return Unauthorized();
            }

        }

        private IAuthService _authenticationService;
    }
}
