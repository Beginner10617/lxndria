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
    const badge = document.getElementById("notificationBadge");

    popup.innerHTML = `
    <h2>Notifications</h2>
    <p>Loading...</p>
    `;

    try {
        const response = await fetch("/notifs");// fetch notifications for the current user (pop-up only)
        const notifications = await response.json();
        const unreadCount = notifications.length; // Count unread notifications

        popup.innerHTML = "<h2>Notifications</h2>";
        notifications.forEach(notification => {
            const div = document.createElement("div");
            div.className = "notification-item";

            div.innerHTML = `<a href="${notification.url}" class="notification-link" >
                                ${notification.message}
                            </a>`;

            popup.appendChild(div);
        });


        if (unreadCount === 0) {
            popup.innerHTML = `<h2>Notifications</h2>
            <div class="notification-item">
            No new notifications
            </div>
            <div class="notification-footer">
            <button onclick="window.location.href='/notifications'">View all</button>
            </div>
            `;
            badge.style.display = "none"; // Hide badge if no unread notifs
        } else {
            const div = document.createElement("div");
            div.className = "notification-footer";
            div.innerHTML = `<button onclick="readAll()">Mark all as read</button>
                            <button onclick="window.location.href='/notifications'">View all</button>
            `;
            popup.appendChild(div);
            badge.style.display = "flex"; // Show badge with count
            badge.innerText = unreadCount;
        }

    } catch (error) {
        popup.innerHTML = "<p>Error loading notifications</p>";
    }
}

function readAll()
{
    fetch("/markread?all=true")
        .then(response => response.json())
        .then(data => {
            console.log("Server response:", data);
            fetchNotifications();
        })
        .catch(error => console.error("Error:", error));
}

// Close menu if clicked outside
document.addEventListener("click", function(event) {
    const menuContainer = document.querySelector(".menu-container");
    if (!menuContainer.contains(event.target)) {
        document.getElementById("menuList").classList.remove("show");
        document.getElementById("notificationPopup").style.display = "none";
    }
});

document.addEventListener("DOMContentLoaded", function() {
    const urlParams = new URL(window.location.href);
    const commentId = urlParams.hash.replace("#comment-", ""); // Extract comment ID
    const solutionId = urlParams.hash.replace("#solution-", ""); // Extract solution ID
    if (commentId) {
        const commentElement = document.getElementById(`comment-${commentId}`);
        if (commentElement) {
            commentElement.scrollIntoView({ behavior: "smooth", block: "center" });
            
            // Highlight effect (fade in and out)
            commentElement.style.transition = "background-color 0.5s ease-in-out";
            commentElement.style.backgroundColor = "#999"; 
            setTimeout(() => {
                commentElement.style.backgroundColor = "transparent";
            }, 2000);
        }
    }
    if (solutionId) {
    
        const solutionElement = document.getElementById(`solution-${solutionId}`);
        if (solutionElement) {
            solutionElement.scrollIntoView({ behavior: "smooth", block: "center" });
            console.log(solutionElement);
            // Highlight effect (fade in and out)
            solutionElement.style.transition = "background-color 0.5s ease-in-out";
            solutionElement.style.backgroundColor = "#999"; 
            setTimeout(() => {
                solutionElement.style.backgroundColor = "transparent";
            }, 2000);
        }
    }
});



// Extract hash and send it to Flask
window.onload = function () {
    const hash = window.location.hash.substring(1); // Remove "#"
    if (hash) {
        fetch(`/markread?hash=${encodeURIComponent(hash)}`)
            .then(response => response.json())
            .then(data => console.log("Server response:", data))
            .catch(error => console.error("Error:", error));
    }
    fetchNotifications();
};
