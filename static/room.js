var socketio = io();

const messages = document.getElementById("messages");

const createMessage = (name, msg) => {

    const content = `
    <div class="text">
        <span>
            <strong>${name}</strong>: ${msg}
        </span>
        <span class="muted">
            ${new Date().toLocaleString()}
        </span>
        <i onclick="toggleThumb(this)" class="fa fa-thumbs-up"></i>
    </div>
    `;
    messages.innerHTML += content;
};

socketio.on("message", (data) => {
    createMessage(data.name, data.message);
});

function sendMessage() {
    const message = document.getElementById("message");
    if (message.value == "") return;
    socketio.emit("message", { data: message.value });
    message.value = "";
}

function toggleThumb(x) {
    x.classList.toggle("fa-thumbs-down");
};
