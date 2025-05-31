document.addEventListener("DOMContentLoaded", () => {
    loadFavoriteSongs();
    lyrics_panel();
    remove_from_favorite();
});

async function loadFavoriteSongs() {
    const username = localStorage.getItem("loggedInUsername");
    if (!username) {
        console.error("No logged in username found");
        return;
    }

    try {
        const response = await fetch(`/api/favorites/${username}`); // ✅ Corrected URL
        if (!response.ok) throw new Error("Failed to fetch favorites");

        const songs = await response.json(); // ✅ Already an array

        const container = document.getElementById("favorite-songs-list");
        container.innerHTML = `
            <ul class="album_list_name">
                <li>#</li>
                <li>Title</li>
                <li>Artist</li>
                <li class="text-center">Genre</li>
                <li class="text-center">Duration</li>
                <li class="text-center">Lyrics</li>
                <li class="text-center">More</li>
                <li class="text-center">remove</li>
            </ul>
        `;

        songs.forEach((song, index) => {
            const ul = document.createElement("ul");
            ul.classList.add("favorite-song");

            // Add data attributes so you can use them later when clicked
            ul.dataset.title = song.title || "Unknown Title";
            ul.dataset.artist = song.artist || "Unknown Artist";
            ul.dataset.genre = song.genre || "Unknown Genre";
            ul.dataset.duration = song.duration || "0";
            ul.dataset.file = `/static/musics/${localStorage.getItem("loggedInUsername")}/${encodeURIComponent(song.title)}.mp3`;

            ul.innerHTML = `
                <li><a href="#"><span class="play_no">${String(index + 1).padStart(2, "0")}</span><span class="play_hover"></span></a></li>
                <li><a href="#">${song.title || "Unknown Title"}</a></li>
                <li><a href="#">${song.artist || "Unknown Artist"}</a></li>
                <li class="text-center"><a href="#">${song.genre || "Unknown Genre"}</a></li>
                <li class="text-center"><a href="#">${formatDuration(song.duration)}</a></li>
                <li class="text-center">
                    <a href="#" class="lyrics-link" data-lyrics="${encodeURIComponent(song.lyrics || "No Lyrics available.")}">View Lyrics</a>
                </li>
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
                <li class="text-center">
                    <a href="#" class="remove-favorite" data-title="${encodeURIComponent(song.title)}" title="Remove from Favorites">
                        <span class="ms_close"><img src="/static/images/svg/close.svg" alt="Remove" /></span>
                    </a>
                </li>
            `;

            container.appendChild(ul);
        });

        setupFavoriteSongsClick();

    } catch (error) {
        console.error("Error loading favorites:", error);
    }
}

function setupFavoriteSongsClick() {
    document.querySelectorAll(".favorite-song").forEach((element) => {
        element.addEventListener("click", (event) => {
            // Prevent clicks on links inside the song item from triggering this (like remove, lyrics)
            if (event.target.closest("a.remove-favorite") || event.target.closest(".lyrics-link") || event.target.closest(".ms_more_icon")) {
                return; // Don't play on those clicks
            }

            event.preventDefault();
            event.stopPropagation();

            // Remove "play_active_song" from all favorite songs first
            document.querySelectorAll(".favorite-song.play_active_song").forEach((el) => {
                el.classList.remove("play_active_song");
            });

            // Add "play_active_song" to the clicked one
            element.classList.add("play_active_song");

            const title = element.dataset.title;
            const artist = element.dataset.artist;
            const file = element.dataset.file;

            $("#jquery_jplayer_1").jPlayer("setMedia", {
                title: title,
                mp3: file
            }).jPlayer("play");

            const playing_track_name = document.getElementById("playing_track_name");
            const playing_track_artist = document.getElementById("playing_track_artist");

            if (playing_track_name && playing_track_artist) {
                playing_track_name.innerText = title;
                playing_track_artist.innerText = artist;
            }
        });
    });
}

function formatDuration(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60).toString().padStart(2, "0");
    return `${mins}:${secs}`;
}

function lyrics_panel() {
    // Event delegation to listen for any click on a lyrics link
    document.body.addEventListener("click", (e) => {
        if (e.target.classList.contains("lyrics-link")) {
            e.preventDefault();

            // Decode lyrics and show panel
            const lyrics = decodeURIComponent(e.target.dataset.lyrics);
            const panel = document.getElementById("lyrics-panel");
            const content = document.getElementById("lyrics-content");

            content.textContent = lyrics;
            panel.style.transform = "translateX(0)";  // Slide panel into view
        }
    });

    // Close button listener
    document.getElementById("close-lyrics-panel").addEventListener("click", () => {
        const panel = document.getElementById("lyrics-panel");
        panel.style.transform = "translateX(100%)"; // Hide panel
    });
}

function remove_from_favorite() {
    document.body.addEventListener("click", async (e) => {
        if (e.target.closest('a.remove-favorite')) {
            e.preventDefault();

            const link = e.target.closest('a.remove-favorite');
            const title = decodeURIComponent(link.dataset.title);
            const username = localStorage.getItem("loggedInUsername");

            try {
                const response = await fetch(`/api/favorites/${username}/${encodeURIComponent(title)}`, {
                    method: "DELETE",
                });

                if (response.ok) {
                    remove_from_favorite_message(`${title} removed from favorites!`);
                } else {
                    remove_from_favorite_message("Failed to remove!", true);
                }
                // Refresh the favorite songs list
                loadFavoriteSongs();
            } catch (error) {
                console.error("Error removing favorite:", error);
            }
        }
    });
}

function remove_from_favorite_message(message, isError = false) {
    const box = document.getElementById("message-box");
    box.textContent = message;
    box.style.backgroundColor = isError ? "#f44336" : "#4caf50";

    box.classList.add("show");

    // Hide after 3 seconds with slide out
    setTimeout(() => {
        box.classList.remove("show");
    }, 3000);
}
