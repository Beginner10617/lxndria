function toggleAnswerType() {
    const answerType = document.getElementById("answer_Type").value.trim();
    document.getElementById("mcqOptions").style.display = answerType === "mcq" ? "block" : "none";
    document.getElementById("inputField").style.display = answerType === "input" ? "block" : "none";
}
document.addEventListener("DOMContentLoaded", function() {
    toggleAnswerType(); // Ensures correct fields are shown based on the selected option
});

function addOption() {
    const container = document.getElementById("optionsContainer");
    const index = container.children.length;
    const optionDiv = document.createElement("div");
    optionDiv.classList.add("option");
    optionDiv.innerHTML = `
    <div class="option-item">
        <input type="checkbox" onclick="toggleOptions()" class="correct-option" id="correct_option_"  value="${index}">
        <input type="text" name="options[]" placeholder="Option ${index + 1}">
    </div>
    `;
    container.appendChild(optionDiv);
}

function toggleOptions() {
    const options = document.getElementsByClassName("correct-option");
    for (let i = 0; i < options.length; i++) {
        if (options[i].checked) {
            options[i].checked = false;
        }
    }
    event.target.checked = true;
}

function removeOption() {
    const container = document.getElementById("optionsContainer");
    if (container.children.length > 2) {
        container.removeChild(container.lastChild);
    }
    else {
        alert("At least two options are required.");
    }
}