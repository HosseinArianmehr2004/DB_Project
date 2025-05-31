document.addEventListener("DOMContentLoaded", () => {
    const playlist_name = localStorage.getItem("selectedPlaylistName");
    const username = localStorage.getItem("selectedPlaylistUser");

    if (!playlist_name || !username) {
        alert("Missing playlist playlist_name or username in localStorage");
        return;
    }

    fetch_playlist_info(playlist_name, username);
    add_song();
});

function parseDuration(str) {
    try {
        // If it's already a number, assume it's seconds
        if (typeof str === "number") {
            return Math.floor(str); // Ensure it's an integer
        }

        if (typeof str !== "string") {
            console.warn("parseDuration: unexpected input type", typeof str, str);
            return 0;
        }

        // Handle MM:SS format
        const parts = str.split(":");
        if (parts.length === 2) {
            const minutes = parseInt(parts[0], 10);
            const seconds = parseInt(parts[1], 10);
            if (isNaN(minutes) || isNaN(seconds)) {
                console.warn("parseDuration: Invalid number in duration string", parts);
                return 0;
            }
            return minutes * 60 + seconds;
        }

        // Handle if it's a string representation of seconds
        const numericValue = parseFloat(str);
        if (!isNaN(numericValue)) {
            return Math.floor(numericValue);
        }

        console.warn("parseDuration: Unexpected format", str);
        return 0;
    } catch (err) {
        console.error("parseDuration: Error parsing duration", err);
        return 0;
    }
}

function formatDuration(seconds) {
    if (typeof seconds !== "number" || isNaN(seconds) || seconds < 0) {
        return "0:00";
    }

    // Ensure we're working with integers
    seconds = Math.floor(seconds);

    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
}

function fetch_playlist_info(playlistName, username) {
    fetch(`/api/playlist?name=${encodeURIComponent(playlistName)}&user=${encodeURIComponent(username)}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const playlist_img = document.getElementById("playlist_img");
            const playlist_name = document.getElementById("playlist_name");
            const playlist_owner = document.getElementById("playlist_owner");
            const playlist_description = document.getElementById("playlist_description");
            const playlist_summary = document.getElementById("playlist_summary");
            const playlist_release = document.getElementById("playlist_release");

            playlist_img.src = data.image_url;
            playlist_name.innerText = data.name;
            playlist_owner.innerText = "Owner: " + data.username;
            playlist_description.innerText = "Description: " + data.description;

            duration = fetch_playlist_songs(playlistName, username, data);

            playlist_summary.innerText = `${data.items.length} songs | ${duration}`;
            playlist_release.innerText = data.release;
        })
        .catch(err => {
            console.error("Failed to load playlist:", err);
            alert("Failed to load playlist. Check console for details.");
        });
}

function fetch_playlist_songs(playlistName, username, data) {
    const songsContainer = document.getElementById("album_list_wrapper2");

    songsContainer.innerHTML = `
        <ul class="album_list_name">
            <li>#</li>
            <li>Song Title</li>
            <li>Genre</li>
            <li class="text-center">Duration</li>
            <li class="text-center">Add To Favourites</li>
            <li class="text-center">More</li>
        </ul>
    `;

    const songItems = data.items || [];
    if (!songItems.length) {
        songsContainer.innerHTML = "<p>No songs found in this playlist.</p>";
        return;
    }

    let totalSeconds = 0;

    songItems.forEach((song, index) => {
        // Parse duration and handle various formats
        const duration = parseDuration(song.duration || "0:00");
        totalSeconds += duration;

        const songFilePath = `/static/musics/${username}/${encodeURIComponent(song.title)}.mp3`;
        const songHTML = `
            <ul class="playlist-song" data-title="${song.title}" data-artist="${song.artist}" data-file="${songFilePath}">
                <li><a href="#"><span class="play_no">${String(index + 1).padStart(2, "0")}</span><span class="play_hover"></span></a></li>
                <li><a href="#">${song.title || "Unknown Title"}</a></li>
                <li><a href="#">${song.genre || "Unknown Genre"}</a></li>
                <li class="text-center"><a href="#">${formatDuration(duration)}</a></li>
                <li class="text-center"><a href="#"><span class="ms_icon1 ms_fav_icon"></span></a></li>
                <li class="text-center ms_more_icon">
                    <a href="javascript:;"><span class="ms_icon1 ms_active_icon"></span></a>
                    <ul class="more_option">
                        <li><a href="#"><span class="opt_icon"><span class="icon icon_fav"></span></span>Add To Favourites</a></li>
                        <li><a href="#"><span class="opt_icon"><span class="icon icon_queue"></span></span>Add To Queue</a></li>
                        <li><a href="#"><span class="opt_icon"><span class="icon icon_dwn"></span></span>Download Now</a></li>
                        <li><a href="#"><span class="opt_icon"><span class="icon icon_playlst"></span></span>Add To Playlist</a></li>
                        <li><a href="#"><span class="opt_icon"><span class="icon icon_share"></span></span>Share</a></li>
                    </ul>
                </li>
            </ul>
        `;

        songsContainer.insertAdjacentHTML("beforeend", songHTML);
    });

    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    const summaryElement = document.getElementById("playlist-summary");
    if (summaryElement) {
        summaryElement.textContent =
            `${songItems.length} song${songItems.length > 1 ? "s" : ""} | ${minutes}:${seconds.toString().padStart(2, "0")}`;
    }

    // Initialize jPlayer if not already done
    $("#jquery_jplayer_1").jPlayer({
        ready: function () {
            console.log("jPlayer is ready");
        },
        swfPath: "/js", // Or wherever your jPlayer .swf is (if needed)
        supplied: "mp3",
        wmode: "window",
        useStateClassSkin: true,
        autoBlur: false,
        smoothPlayBar: true,
        keyEnabled: true
    });

    document.querySelectorAll(".playlist-song").forEach((element) => {
        element.addEventListener("click", (event) => {
            event.preventDefault();
            event.stopPropagation();

            const title = element.dataset.title;
            const artist = element.dataset.artist;
            const file = element.dataset.file;

            $("#jquery_jplayer_1").jPlayer("setMedia", {
                title: title,
                mp3: file
            }).jPlayer("play");

            // Add this inside the click handler:
            const playing_track_name = document.getElementById("playing_track_name");
            const playing_track_artist = document.getElementById("playing_track_artist");

            console.log(`playing_track_name.innerText: ${playing_track_name.innerText}`);
            console.log(`playing_track_artist.innerText: ${playing_track_artist.innerText}`);

            if (playing_track_name && playing_track_artist) {
                playing_track_name.innerText = title;
                playing_track_artist.innerText = artist;
            }
        });
    });

    document.querySelectorAll(".ms_fav_icon").forEach((icon) => {
        icon.addEventListener("click", async (event) => {
            event.preventDefault();
            event.stopPropagation();

            const songElement = icon.closest(".playlist-song");
            const username = localStorage.getItem("selectedPlaylistUser");
            const title = songElement.dataset.title;

            const response = await fetch(`/api/favorite`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ username, title }),
            });

            if (response.ok) {
                add_to_favorite_message(`${title} added to favorites!`);
            } else {
                add_to_favorite_message("Failed to add to favorites.", true);
            }
        });
    });

    return formatDuration(totalSeconds);
}

function add_song() {
    const playlistName = localStorage.getItem("selectedPlaylistName");
    const username = localStorage.getItem("selectedPlaylistUser");

    if (!playlistName || !username) {
        showMessage("Missing playlist info in localStorage.");
        return;
    }

    // Open popup when clicking the upload button
    const uploadBtn = document.getElementById("upload-song-btn");
    if (uploadBtn) {
        uploadBtn.addEventListener("click", () => {
            const popup = document.getElementById("upload-song-popup");
            if (popup) popup.style.display = "flex";
        });
    }

    // Close popup when clicking cancel
    const cancelBtn = document.getElementById("cancel-upload-btn");
    if (cancelBtn) {
        cancelBtn.addEventListener("click", () => {
            const popup = document.getElementById("upload-song-popup");
            if (popup) popup.style.display = "none";
        });
    }

    // Handle form submit
    const uploadForm = document.getElementById("upload-song-form");
    if (uploadForm) {
        uploadForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const form = e.target;
            const formData = new FormData(form);

            // Basic validation
            if (!formData.get("name").trim()) {
                showMessage("Please enter the track name.");
                return;
            }
            if (!formData.get("song_file") || formData.get("song_file").size === 0) {
                showMessage("Please upload a song file.");
                return;
            }

            try {
                const response = await fetch(
                    `/api/playlist/${encodeURIComponent(username)}/${encodeURIComponent(playlistName)}/add-song`,
                    {
                        method: "POST",
                        body: formData,
                    }
                );

                if (!response.ok) {
                    const errText = await response.text();
                    throw new Error(errText || "Failed to upload song.");
                }

                showMessage("Song uploaded successfully!");
                form.reset();
                const popup = document.getElementById("upload-song-popup");
                if (popup) popup.style.display = "none";

                // Optionally: refresh playlist info
                fetch_playlist_info(playlistName, username);

            } catch (err) {
                showMessage("Error: " + err.message);
                console.error(err);
            }
        });
    }
}

function showMessage(type, text) {
    const msgBox = document.getElementById("upload-message");
    if (!msgBox) return;

    msgBox.className = "message-box " + type;
    msgBox.textContent = text;
    msgBox.style.display = "block";

    setTimeout(() => {
        msgBox.style.display = "none";
    }, 4000); // Hide after 4 seconds
}

function add_to_favorite_message(message, isError = false) {
    const box = document.getElementById("message-box");
    box.textContent = message;
    box.style.backgroundColor = isError ? "#f44336" : "#4caf50";

    box.classList.add("show");

    // Hide after 3 seconds with slide out
    setTimeout(() => {
        box.classList.remove("show");
    }, 3000);
}
