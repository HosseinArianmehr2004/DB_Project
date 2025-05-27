document.addEventListener("DOMContentLoaded", async () => {
    const username = localStorage.getItem("loggedInUsername");
    if (!username) {
        alert("You must be logged in.");
        window.location.href = "/";
        return;
    }

    const userData = await fetchUserProfile(username);
    if (!userData) return;

    set_profile(username);

    const profileImgElement = document.getElementById("profileImage");

    // if (profileImgElement) {
    //     // const imagePath = userData.profile_image || "/static/images/profiles/default.jpg";
    //     const imagePath = `${username}.jpg` || "/static/images/profiles/default.jpg";
    //     profileImgElement.src = imagePath;
    // }

    if (profileImgElement) {
        const userImagePath = `/static/images/profiles/${username}.jpg`;
        const defaultImagePath = "/static/images/profiles/profile_default.jpg";

        const testImage = new Image();
        testImage.onload = function () {
            profileImgElement.src = userImagePath;
        };
        testImage.onerror = function () {
            profileImgElement.src = defaultImagePath;
        };
        testImage.src = userImagePath;
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

async function fetchUserProfile(username) {
    try {
        const res = await fetch(`/get-profile?username=${encodeURIComponent(username)}`);
        if (!res.ok) throw new Error("Failed to fetch user");
        return await res.json();
    } catch (err) {
        console.error(err);
        alert("Could not load profile.");
        return null;
    }
}

function set_profile(username) {
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
        formData.append("username", username);

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

function config_buttons() {
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

        // Add current username for identification
        data.current_username = localStorage.getItem("loggedInUsername");

        // console.log("FormData result before sending:", data);

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
                // If username was changed, update localStorage too!
                if (data.username && data.username !== data.current_username) {
                    localStorage.setItem("loggedInUsername", data.username);
                }

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
        localStorage.removeItem("loggedInUsername");
        window.location.href = "/";
    });
}