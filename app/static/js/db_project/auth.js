document.addEventListener('DOMContentLoaded', () => {
    register();
    login();
});

function register() {
    const registerBtn = document.getElementById('register-btn');
    const usernameInput = document.getElementById('username');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm-password');

    const messageContainer = document.createElement('div');
    messageContainer.style.marginTop = "10px";
    const form = document.querySelector('.ms_register_form');
    form.appendChild(messageContainer);

    function showMessage(msg, color = "red") {
        messageContainer.textContent = msg;
        messageContainer.style.color = color;
    }

    registerBtn.addEventListener('click', async (event) => {
        event.preventDefault();

        const username = usernameInput.value.trim();
        const email = emailInput.value.trim();
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;

        if (!username || !email || !password || !confirmPassword) {
            showMessage("All fields are required.");
            return;
        }

        // Simple username validation example: min 6 chars, alphanumeric
        if (!/^[a-zA-Z0-9_]{6,}$/.test(username)) {
            showMessage("Username must be at least 6 characters and contain only letters, numbers, or underscores.");
            return;
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            showMessage("Invalid email format.");
            return;
        }

        if (password.length < 6) {
            showMessage("Password must be at least 6 characters.");
            return;
        }

        if (password !== confirmPassword) {
            showMessage("Passwords do not match.");
            return;
        }

        try {
            const response = await fetch('/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    username: username,   // new
                    email: email,
                    password: password,
                })
            });

            if (response.ok) {
                showMessage("Registration successful!", "green");
                setTimeout(() => {
                    document.querySelector('.close').click(); // close modal
                }, 1500);
            } else {
                const data = await response.json();
                showMessage(data.detail || "Registration failed.");
            }
        } catch (err) {
            showMessage("Server error. Please try again.");
            console.error(err);
        }
    });
}

function login() {
    const loginBtn = document.getElementById('login-btn');
    const emailInput = document.querySelector('#myModal1 input[placeholder="Enter Your Email"]');
    const passwordInput = document.querySelector('#myModal1 input[placeholder="Enter Password"]');

    const messageContainer = document.createElement('div');
    messageContainer.style.marginTop = "10px";
    const form = document.querySelector('#myModal1 .ms_register_form');
    form.appendChild(messageContainer);

    function showMessage(msg, color = "red") {
        messageContainer.textContent = msg;
        messageContainer.style.color = color;
    }

    loginBtn.addEventListener('click', async (event) => {
        event.preventDefault();

        const email = emailInput.value.trim();
        const password = passwordInput.value;

        if (!email || !password) {
            showMessage("Both fields are required.");
            return;
        }

        try {
            const response = await fetch('/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });


            const data = await response.json();

            if (response.ok) {
                showMessage("Login successful!", "green");

                // Fetch username from the server
                try {
                    const usernameRes = await fetch(`/get_username?email=${encodeURIComponent(email)}`);
                    if (usernameRes.ok) {
                        const { username } = await usernameRes.json();
                        localStorage.setItem("loggedInUsername", username);
                    }
                } catch (fetchErr) {
                    console.warn("Could not fetch username:", fetchErr);
                }

                setTimeout(() => {
                    window.location.href = "/profile";
                }, 1000);
            }
            else {
                showMessage(data.detail || "Invalid credentials.");
            }
        } catch (error) {
            console.error(error);
            showMessage("Server error. Please try again.");
        }
    });
}
