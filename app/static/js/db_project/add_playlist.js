document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("playlistForm");
    const modal = document.getElementById("playlistModal");
    const openModal = document.getElementById("openModal");
    const closeModal = document.querySelector(".apl-close");
    const cancelBtn = document.getElementById("cancelBtn");
    const playlistRow = document.getElementById("playlistsContainer");
    const DEFAULT_IMAGE_URL = "/static/images/playlists/playlist_default.jpg";

    // Message container setup
    let msgContainer = document.getElementById("messageContainer");
    if (!msgContainer) {
        msgContainer = document.createElement("div");
        msgContainer.id = "messageContainer";
        msgContainer.style.margin = "10px 0";
        form.parentNode.insertBefore(msgContainer, form);
    }

    function showMessage(msg, isError = true) {
        msgContainer.textContent = msg;
        msgContainer.style.color = isError ? "red" : "green";
        setTimeout(() => {
            msgContainer.textContent = "";
        }, 4000);
    }

    // Show modal
    openModal.addEventListener("click", () => {
        modal.style.display = "block";
    });

    // Hide modal
    const closeModalFunc = () => {
        modal.style.display = "none";
    };
    closeModal.addEventListener("click", closeModalFunc);
    cancelBtn.addEventListener("click", closeModalFunc);

    function createPlaylistCard(pl) {
        const col = document.createElement("div");
        col.className = "col-lg-2 col-md-6";

        col.innerHTML = `
            <a href="/playlist?name=${encodeURIComponent(pl.name)}&user=${encodeURIComponent(pl.username)}" class="playlist-link">
                <div class="ms_rcnt_box marger_bottom25">
                    <div class="ms_rcnt_box_img">
                        <img 
                            src="/static/images/playlists/${pl.username + "_" + pl.name}.jpg"
                            alt="${pl.name}" class="img-fluid"
                            onerror="this.onerror=null; this.src='/static/images/playlists/playlist_default.jpg';" 
                        />
                        <div class="ms_main_overlay">
                            <div class="ms_box_overlay"></div>
                            <div class="ms_play_icon">
                                <img src="/static/images/svg/play.svg" alt="Play Icon" />
                            </div>
                        </div>
                    </div>
                    <div class="ms_rcnt_box_text">
                        <h3>${pl.name}</h3>
                        <p>${pl.items?.length || 0} Items</p>
                    </div>
                </div>
            </a>
        `;

        // Attach click listener to store playlist info
        const link = col.querySelector("a.playlist-link");
        link.addEventListener("click", () => {
            localStorage.setItem("selectedPlaylistName", pl.name);
            localStorage.setItem("selectedPlaylistUser", pl.username);
        });

        return col;
    }


    // Load playlists from server and render them
    async function loadPlaylists() {
        const username = localStorage.getItem("loggedInUsername");
        if (!username) {
            showMessage("You must be logged in to view playlists.");
            return;
        }

        try {
            const res = await fetch(`/api/user_playlists?username=${encodeURIComponent(username)}`); // this is insecure***********************
            if (!res.ok) throw new Error("Failed to fetch playlists");
            const playlists = await res.json();

            // Remove existing playlist cards except the "Create New Playlist" card
            playlistRow.querySelectorAll(".playlist-card").forEach(el => el.remove());

            const createCard = document.getElementById("openModal").closest(".col-lg-2");

            playlists.forEach(pl => {
                const card = createPlaylistCard(pl);
                playlistRow.insertBefore(card, createCard);
            });
        } catch (error) {
            showMessage("Error loading playlists.");
            console.error(error);
        }
    }

    form.addEventListener("submit", async e => {
        e.preventDefault();

        const username = localStorage.getItem("loggedInUsername");
        if (!username) {
            showMessage("You must be logged in to create a playlist.");
            return;
        }

        const name = document.getElementById("playlistName").value.trim();
        const description = document.getElementById("playlistDescription").value.trim();
        // const type = document.querySelector("input[name='type']:checked")?.value;
        const imageInput = document.getElementById("playlistImage");
        const imageFile = imageInput.files[0];

        if (!name) {
            showMessage("Playlist name is required.");
            return;
        }
        // if (!type) {
        //     showMessage("Playlist type must be selected.");
        //     return;
        // }

        // Prepare form data
        const formData = new FormData();
        formData.append("username", username);
        formData.append("name", name);
        formData.append("description", description);
        // formData.append("type", type);
        formData.append("items", JSON.stringify([])); // empty list for new playlist
        if (imageFile) {
            formData.append("image", imageFile);
        }

        try {
            const res = await fetch("/api/create_playlist", {
                method: "POST",
                body: formData,
            });
            const result = await res.json();

            if (res.ok) {
                showMessage("Playlist created successfully!", false);
                closeModalFunc();
                form.reset();

                const playlistData = {
                    username,
                    name,
                    description,
                    // type,
                    items: []
                };

                const createCard = document.getElementById("openModal").closest(".col-lg-2");
                const card = createPlaylistCard(playlistData);
                playlistRow.insertBefore(card, createCard);
            } else {
                showMessage(result.detail || "Error creating playlist.");
            }
        } catch (error) {
            showMessage("An error occurred: " + error.message);
        }
    });


    loadPlaylists();
});
