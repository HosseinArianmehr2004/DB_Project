const searchBox = document.getElementById("searchBox");
const resultsContainer = document.getElementById("searchResults");

searchBox.addEventListener("input", function () {
    const query = this.value.trim();
    if (query.length > 0) {
        fetch(`/api/search-songs?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                const results = data.results;
                resultsContainer.innerHTML = ""; // Clear old results

                if (results.length === 0) {
                    const li = document.createElement("li");
                    li.textContent = "No results found.";
                    li.style.padding = "10px";
                    li.style.color = "#888";
                    resultsContainer.appendChild(li);
                } else {
                    results.forEach(song => {
                        const li = document.createElement("li");
                        li.textContent = `${song.title} - ${song.artist}`;
                        li.style.padding = "10px";
                        li.style.cursor = "pointer";

                        li.addEventListener("click", () => {
                            if (!song.username) {
                                alert("Uploader username not found for this song.");
                                return;
                            }

                            const filePath = `/static/musics/${encodeURIComponent(song.username)}/${encodeURIComponent(song.title)}.mp3`;

                            // Play the song using jPlayer
                            $("#jquery_jplayer_1").jPlayer("setMedia", {
                                title: song.title,
                                mp3: filePath
                            }).jPlayer("play");

                            // Update track name and artist display
                            const playing_track_name = document.getElementById("playing_track_name");
                            const playing_track_artist = document.getElementById("playing_track_artist");

                            if (playing_track_name && playing_track_artist) {
                                playing_track_name.innerText = song.title;
                                playing_track_artist.innerText = song.artist;
                            }

                            resultsContainer.style.display = "none"; // hide list
                            searchBox.value = song.title; // fill input
                        });

                        resultsContainer.appendChild(li);
                    });
                }

                resultsContainer.style.display = "block"; // Show results
            })
            .catch(error => {
                console.error("Search error:", error);
                resultsContainer.innerHTML = "";
                const li = document.createElement("li");
                li.textContent = "Error occurred.";
                li.style.padding = "10px";
                li.style.color = "red";
                resultsContainer.appendChild(li);
                resultsContainer.style.display = "block";
            });
    } else {
        resultsContainer.innerHTML = "";
        resultsContainer.style.display = "none"; // hide if input is empty
    }
});

// Hide suggestions when clicking outside
document.addEventListener("click", function (e) {
    if (!searchBox.contains(e.target) && !resultsContainer.contains(e.target)) {
        resultsContainer.style.display = "none";
    }
});
