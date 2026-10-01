Since Google AI Studio preview environment blocks external network requests (EmailJS fetch is blocked by sandbox policy), please update the verification logic:

1. Keep EmailJS call in a try/catch block so it doesn't crash.
2. Directly auto-fill the generated 6-digit code into the OTP input field, or display a clickable badge/button 'Auto-verify' on the screen.
3. Automatically log the code to console with console.log('OTP:', code).
4. Allow instant verification when the user clicks verify so I can proceed into the application immediately.
