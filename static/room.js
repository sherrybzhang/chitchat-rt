var socketio = io();

const messages = document.getElementById("messages");
const messageInput = document.getElementById("message");
const sendButton = document.getElementById("send-btn");

function formatTimestamp() {
  return new Date().toLocaleString([], {
    hour: "2-digit",
    minute: "2-digit",
    month: "short",
    day: "numeric",
  });
}

function createMessage(name, msg) {
  if (!messages) {
    return;
  }

  const row = document.createElement("div");
  row.className = "message-row";

  const content = document.createElement("span");
  content.className = "message-content";

  const author = document.createElement("strong");
  author.textContent = name;

  content.appendChild(author);
  content.appendChild(document.createTextNode(`: ${msg}`));

  const meta = document.createElement("div");
  meta.className = "message-meta";

  const timestamp = document.createElement("span");
  timestamp.className = "muted";
  timestamp.textContent = formatTimestamp();

  const reaction = document.createElement("button");
  reaction.type = "button";
  reaction.className = "reaction-btn";
  reaction.setAttribute("aria-label", "Toggle like");

  const icon = document.createElement("i");
  icon.className = "fa fa-thumbs-up";
  reaction.appendChild(icon);

  reaction.addEventListener("click", function () {
    reaction.classList.toggle("is-active");
  });

  meta.appendChild(timestamp);
  meta.appendChild(reaction);

  row.appendChild(content);
  row.appendChild(meta);

  messages.appendChild(row);
  messages.scrollTop = messages.scrollHeight;
}

socketio.on("message", (data) => {
  createMessage(data.name, data.message);
});

function sendMessage() {
  if (!messageInput) {
    return;
  }

  const messageValue = messageInput.value.trim();
  if (!messageValue) {
    return;
  }

  socketio.emit("message", { data: messageValue });
  messageInput.value = "";
  messageInput.focus();
}

if (messageInput) {
  messageInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      sendMessage();
    }
  });
}

if (sendButton) {
  sendButton.addEventListener("click", sendMessage);
}
