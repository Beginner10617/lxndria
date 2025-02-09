document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("comment-form").addEventListener("submit", function(event) {
        event.preventDefault();  // Prevent page reload

        let form = new FormData(this);

        fetch(this.action, {
            method: "POST",
            body: form,
            headers: { "X-Requested-With": "XMLHttpRequest" }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadComments();  // Reload comments section after posting
            } else {
                alert("Error: " + JSON.stringify(data.errors));
            }
        });
    });

    function loadComments() {
        fetch(window.location.pathname, { headers: { "X-Requested-With": "XMLHttpRequest" } })
        .then(response => response.text())
        .then(html => {
            document.getElementById("comments-section").innerHTML = html;
        });
    }

    document.querySelectorAll(".reply-button").forEach(button => {
        button.addEventListener("click", function() {
            let replyUrl = this.getAttribute("data-reply-url");

            fetch(replyUrl, { headers: { "X-Requested-With": "XMLHttpRequest" } })
            .then(response => response.text())
            .then(html => {
                document.getElementById("reply-form-container").innerHTML = html;
            });
        });
    });
});