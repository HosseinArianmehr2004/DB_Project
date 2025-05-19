document.addEventListener("DOMContentLoaded", async () => {
    const email = localStorage.getItem("loggedInEmail");
    if (!email) {
        alert("You must be logged in.");
        window.location.href = "/";
        return;
    }

    const userData = await fetchUserProfile(email);
    if (!userData) return;

    set_profile(email);

    const profileImgElement = document.getElementById("profileImage");
    if (profileImgElement) {
        const imagePath = userData.profile_image || "/static/images/profiles/default.jpg";
        profileImgElement.src = imagePath;
    }

    if (userData.is_premium) {
        document.getElementById("premiumBadge").classList.remove("d-none");
        document.getElementById("profileImageWrapper").classList.add("premium-border");
    }

    // Populate spans and inputs
    for (const key in userData) {
        const span = document.getElementById(`${key}-value`);
        const input = document.querySelector(`[name="${key}"]`);
        const value = userData[key] ?? "";

        if (span) span.textContent = value;
        if (input) {
            input.placeholder = value;
            input.value = value;
        }
    }

    config_buttons();
    logout();
});

async function fetchUserProfile(email) {
    try {
        const res = await fetch(`/get-profile?email=${encodeURIComponent(email)}`);
        if (!res.ok) throw new Error("Failed to fetch user");
        return await res.json();
    } catch (err) {
        console.error(err);
        alert("Could not load profile.");
        return null;
    }
}

function set_profile(email) {
    const profileImage = document.getElementById("profileImageWrapper");
    const imageInput = document.getElementById("profileImageInput");

    profileImage.addEventListener("click", () => {
        imageInput.click();
    });

    imageInput.addEventListener("change", async () => {
        const file = imageInput.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append("image", file);
        formData.append("email", email); // Or username if needed

        try {
            const res = await fetch("/upload-profile-image", {
                method: "POST",
                body: formData
            });

            const result = await res.json();
            if (res.ok) {
                profileImage.src = result.image_url + "?t=" + new Date().getTime(); // Prevent caching
                location.reload();
            } else {
                alert(result.detail || "Image upload failed.");
            }
        } catch (err) {
            console.error(err);
            alert("Upload error.");
        }
    });
}

function config_buttons(email) {
    const editBtn = document.getElementById("editProfileBtn");
    const saveBtn = document.getElementById("saveProfileBtn");
    const cancelBtn = document.getElementById("cancelProfileBtn");

    editBtn.addEventListener("click", () => {
        document.querySelectorAll(".profile-value").forEach(span => span.classList.add("d-none"));
        document.querySelectorAll("#profileForm .form-control").forEach(input => input.classList.remove("d-none"));

        editBtn.classList.add("d-none");
        saveBtn.classList.remove("d-none");
        cancelBtn.classList.remove("d-none");
    });


    saveBtn.addEventListener("click", async (e) => {
        e.preventDefault();

        const formData = new FormData(document.getElementById("profileForm"));
        const data = Object.fromEntries(formData.entries());
        data.email = localStorage.getItem("loggedInEmail"); // Ensure email is used to identify user
        console.log("Email in JS:", email); // Should not be null or empty
        console.log("FormData result before sending:", data);


        try {
            const res = await fetch("/update-profile", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            });

            const result = await res.json();
            if (res.ok) {
                // alert("Profile updated successfully.");
                location.reload();
            } else {
                alert(result.detail || "Update failed.");
            }
        } catch (err) {
            console.error(err);
            alert("Server error. Try again later.");
        }
    });

    cancelBtn.addEventListener("click", () => {
        document.querySelectorAll(".profile-value").forEach(span => span.classList.remove("d-none"));
        document.querySelectorAll("#profileForm .form-control").forEach(input => input.classList.add("d-none"));

        editBtn.classList.remove("d-none");
        saveBtn.classList.add("d-none");
        cancelBtn.classList.add("d-none");
    });
}

function logout() {
    document.getElementById('logout-link').addEventListener('click', (e) => {
        e.preventDefault();
        localStorage.removeItem("loggedInEmail");
        window.location.href = "/";
    });
}