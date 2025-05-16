// document.getElementById("register-form").addEventListener("submit", async (e) => {
//     e.preventDefault();

//     const userData = {
//         username: document.getElementById("username").value,
//         email: document.getElementById("email").value,
//         password: document.getElementById("password").value
//     };

//     const response = await fetch("/register", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify(userData)
//     });

//     const result = await response.json();
//     document.getElementById("message").textContent = result.message || result.detail;
// });


async function loadUsers() {
    const res = await fetch("/users");
    const users = await res.json();

    const list = document.getElementById("user-list");
    list.innerHTML = ""; // Clear previous items

    users.forEach(user => {
        const li = document.createElement("li");
        li.textContent = `Username: ${user.username}, Email: ${user.email}`;
        list.appendChild(li);
    });
}

// Form submit handler
document.getElementById("register-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const userData = {
        username: document.getElementById("username").value,
        email: document.getElementById("email").value,
        password: document.getElementById("password").value
    };

    const response = await fetch("/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(userData)
    });

    const result = await response.json();
    document.getElementById("message").textContent = result.message || result.detail;

    await loadUsers(); // Reload user list after registration
});

// Load users when page loads
window.onload = loadUsers;
