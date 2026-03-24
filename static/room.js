var socketio = io();

const messages = document.getElementById("messages");
const messageInput = document.getElementById("message");
const sendButton = document.getElementById("send-btn");
const openRoomModalButton = document.getElementById("open-room-modal");
const closeRoomModalButton = document.getElementById("close-room-modal");
const roomModal = document.getElementById("room-modal");
const roomCodeInput = document.getElementById("modal-room-code");
const roomModalForm = document.getElementById("room-modal-form");
const roomModalError = document.getElementById("room-modal-error");

if (roomModal && !roomModal.hidden) {
  document.body.classList.add("modal-open");
}

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

  const isJoinMessage = msg === "has entered the room" || msg === "has left the room";

  const row = document.createElement("div");
  row.className = "message-row";
  if (isJoinMessage) {
    row.classList.add("is-join");
  }

  const content = document.createElement("span");
  content.className = "message-content";

  if (isJoinMessage) {
    const joinedText = document.createElement("strong");
    joinedText.textContent = `${name} ${msg}`;
    content.appendChild(joinedText);
  } else {
    const author = document.createElement("strong");
    author.textContent = name;

    content.appendChild(author);
    content.appendChild(document.createTextNode(`: ${msg}`));
  }

  const meta = document.createElement("div");
  meta.className = "message-meta";

  const timestamp = document.createElement("span");
  timestamp.className = "muted";
  timestamp.textContent = formatTimestamp();

  meta.appendChild(timestamp);

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

function toggleRoomModal(isOpen) {
  if (!roomModal) {
    return;
  }

  roomModal.hidden = !isOpen;
  document.body.classList.toggle("modal-open", isOpen);

  if (isOpen && roomCodeInput) {
    roomCodeInput.focus();
  }
}

function setRoomModalError(message) {
  if (!roomModalError) {
    return;
  }

  roomModalError.textContent = message || "";
  roomModalError.hidden = !message;
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

if (openRoomModalButton) {
  openRoomModalButton.addEventListener("click", () => {
    setRoomModalError("");
    toggleRoomModal(true);
  });
}

if (closeRoomModalButton) {
  closeRoomModalButton.addEventListener("click", () => toggleRoomModal(false));
}

if (roomModal) {
  roomModal.addEventListener("click", (event) => {
    if (event.target === roomModal) {
      toggleRoomModal(false);
    }
  });
}

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && roomModal && !roomModal.hidden) {
    toggleRoomModal(false);
  }
});

if (roomModalForm) {
  roomModalForm.addEventListener("submit", async (event) => {
    const asyncEndpoint = roomModalForm.dataset.asyncEndpoint || roomModalForm.action;
    if (!asyncEndpoint) {
      return;
    }

    event.preventDefault();
    setRoomModalError("");

    const formData = new FormData(roomModalForm);

    try {
      const response = await fetch(asyncEndpoint, {
        method: "POST",
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
        body: formData,
      });
      const payload = await response.json();
      if (!response.ok || !payload.ok || !payload.room) {
        setRoomModalError(payload.error || "Unable to enter that channel.");
        return;
      }

      window.location.href = payload.redirect_url || "/room";
    } catch (_error) {
      setRoomModalError("Unable to enter that channel.");
    }
  });
}
