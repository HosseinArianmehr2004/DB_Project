document.addEventListener("DOMContentLoaded", () => {
  const isLoggedIn = localStorage.getItem("loggedInUsername");

  const loggedInSection = document.querySelector(".ms_top_btn.logged-in");
  const loggedOutSection = document.querySelector(".ms_top_btn.logged-out");
  const displayNameSpan = document.querySelector(".user-display-name");

  if (isLoggedIn) {
    // Show logged-in header
    if (loggedInSection) loggedInSection.style.display = "flex";
    if (loggedOutSection) loggedOutSection.style.display = "none";

    // Set username
    if (displayNameSpan) {
      displayNameSpan.textContent = isLoggedIn.split("@")[0];
    }

    // Insert "Profile" link at top of .nav_downloads
    const navDownloads = document.querySelector(".nav_downloads");
    if (navDownloads) {
      const profileItem = document.createElement("li");
      profileItem.innerHTML = `
        <a href="/profile" title="Profile">
          <span class="nav_icon"><span class="icon icon_profile"></span></span>
          <span class="nav_text">profile</span>
        </a>
      `;
      navDownloads.insertBefore(profileItem, navDownloads.firstChild);
    }

  } else {
    // Show logged-out header
    if (loggedOutSection) loggedOutSection.style.display = "flex";
    if (loggedInSection) loggedInSection.style.display = "none";
  }

  // Handle logout
  const logoutLink = document.getElementById("logout-link");
  if (logoutLink) {
    logoutLink.addEventListener("click", () => {
      // localStorage.removeItem("loggedInEmail");
      localStorage.removeItem("loggedInUsername");
      location.reload();
    });
  }
});
