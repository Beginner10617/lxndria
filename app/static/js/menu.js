function toggleMenu() {
    document.getElementById("menuList").classList.toggle("show");
}

function toggleNotif() {
    const popup = document.getElementById("notificationPopup");
            if (popup.style.display === "none" || popup.style.display === "") {
                popup.style.display = "block";
                fetchNotifications();
            } else {
                popup.style.display = "none";
            }
}

async function fetchNotifications() {
    const popup = document.getElementById("notificationPopup");
    popup.innerHTML = "<p>Loading...</p>";

    try {
        const response = await fetch("/notifs");// fetch notifications for the current user (pop-up only)
        const notifications = await response.json();

        popup.innerHTML = "";
        notifications.forEach(notification => {
            const div = document.createElement("div");
            div.className = "notification-item";
            div.innerText = notification.message;
/*
            div.innerHTML = `<a href="${notification.discussion_url}#comment-${notification.comment_id}" class="notification-link">
                                ${notification.message}
                            </a>`;
*/
            popup.appendChild(div);
        });

        if (notifications.length === 0) {
            popup.innerHTML = "<p>No new notifications</p>";
        }

    } catch (error) {
        popup.innerHTML = "<p>Error loading notifications</p>";
    }
}

// Close menu if clicked outside
document.addEventListener("click", function(event) {
    const menuContainer = document.querySelector(".menu-container");
    if (!menuContainer.contains(event.target)) {
        document.getElementById("menuList").classList.remove("show");
        document.getElementById("notificationPopup").style.display = "none";
    }
});
