const cord = document.getElementById('pullCord');
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');
let isLightOn = false;

// کاریگەری ڕاکێشانی پەتەکە
cord.addEventListener('click', () => {
  cord.classList.add('pulled');
  
  setTimeout(() => {
    cord.classList.remove('pulled');
    
    isLightOn = !isLightOn;
    if(isLightOn) {
      document.body.classList.add('light-on');
    } else {
      document.body.classList.remove('light-on');
    }
  }, 200);
});

// گۆڕینی نێوان چوونەژوورەوە و دروستکردنی هەژمار
function toggleForm() {
  if (loginForm.classList.contains('hidden')) {
    // نیشاندانی Login
    registerForm.classList.add('hidden');
    loginForm.classList.remove('hidden');
  } else {
    // نیشاندانی Register
    loginForm.classList.add('hidden');
    registerForm.classList.remove('hidden');
  }
}
