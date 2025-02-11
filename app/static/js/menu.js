function toggleMenu() {
    document.getElementById("menuList").classList.toggle("show");
}

function toggleNotif(){
    document.getElementById("notifList").classList.toggle("show");
}

// Close menu if clicked outside
document.addEventListener("click", function(event) {
    const menuContainer = document.querySelector(".menu-container");
    if (!menuContainer.contains(event.target)) {
        document.getElementById("menuList").classList.remove("show");
    }
});
