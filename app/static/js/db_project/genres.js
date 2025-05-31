document.addEventListener("DOMContentLoaded", () => {
  // Add click listeners to all genre boxes
  document.querySelectorAll(".ms_genres_box").forEach(box => {
    box.addEventListener("click", () => {
      const genre = box.getAttribute("data-genre");
      if (genre) {
        localStorage.setItem("selectedGenre", genre);
        window.location.href = "/playlist";
      }
    });
  });
});
