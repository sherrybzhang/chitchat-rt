const socketio = io();

const messages = document.getElementById("messages");
const messageInput = document.getElementById("message");
const messageStatus = document.getElementById("message-status");
const sendButton = document.getElementById("send-btn");
const openRoomModalButton = document.getElementById("open-room-modal");
const closeRoomModalButton = document.getElementById("close-room-modal");
const roomModal = document.getElementById("room-modal");
const roomShell = document.querySelector(".room-shell");
const roomCodeInput = document.getElementById("modal-room-code");
const roomModalForm = document.getElementById("room-modal-form");
const roomModalError = document.getElementById("room-modal-error");
const presenceIndicator = document.getElementById("presence-indicator");
const channelPills = new Map(
  Array.from(document.querySelectorAll("[data-room-code]")).map((pill) => [pill.dataset.roomCode, pill]),
);
let shouldAnnounceRoomJoin = roomShell?.dataset.announceRoomJoin === "true";
let previousFocusedElement = null;
const focusableSelector =
  'a[href], button:not([disabled]), input:not([disabled]):not([type="hidden"]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';
const unreadStorageKey = "chitchat-last-seen-counts";

function formatTimestamp(date) {
  return date.toLocaleString([], {
    hour: "2-digit",
    minute: "2-digit",
    month: "short",
    day: "numeric",
  });
}

function announceStatus(message) {
  if (!messageStatus) {
    return;
  }

  messageStatus.textContent = "";
  window.requestAnimationFrame(() => {
    messageStatus.textContent = message;
  });
}

function updatePresenceIndicator(count) {
  if (!presenceIndicator || !Number.isFinite(count)) {
    return;
  }

  presenceIndicator.dataset.memberCount = String(count);
  presenceIndicator.textContent = `${count} ${count === 1 ? "member" : "members"} active`;
}

function getLastSeenCounts() {
  try {
    const stored = window.localStorage.getItem(unreadStorageKey);
    if (!stored) {
      return {};
    }

    const parsed = JSON.parse(stored);
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch (_error) {
    return {};
  }
}

function setLastSeenCounts(lastSeenCounts) {
  try {
    window.localStorage.setItem(unreadStorageKey, JSON.stringify(lastSeenCounts));
  } catch (_error) {
    // Ignore storage failures and continue without persisted unread state.
  }
}

function getCurrentRoomCode() {
  return roomShell?.dataset.currentRoom || "";
}

function getRoomMessageCount(roomCode) {
  const pill = channelPills.get(roomCode);
  if (!pill) {
    return 0;
  }

  const count = Number.parseInt(pill.dataset.messageCount || "0", 10);
  return Number.isNaN(count) ? 0 : count;
}

function setRoomMessageCount(roomCode, count) {
  const pill = channelPills.get(roomCode);
  if (!pill || !Number.isFinite(count)) {
    return;
  }

  pill.dataset.messageCount = String(count);
  if (roomShell && roomShell.dataset.currentRoom === roomCode) {
    roomShell.dataset.currentRoomMessageCount = String(count);
  }
}

function updateUnreadBadge(roomCode) {
  const pill = channelPills.get(roomCode);
  if (!pill) {
    return;
  }

  const badge = pill.querySelector("[data-room-badge]");
  if (!badge) {
    return;
  }

  const currentRoomCode = getCurrentRoomCode();
  const lastSeenCounts = getLastSeenCounts();
  const unreadCount =
    roomCode === currentRoomCode ? 0 : Math.max(getRoomMessageCount(roomCode) - (lastSeenCounts[roomCode] || 0), 0);

  badge.textContent = unreadCount > 99 ? "99+" : String(unreadCount);
  badge.hidden = unreadCount <= 0;
}

function markRoomAsSeen(roomCode) {
  if (!roomCode) {
    return;
  }

  const lastSeenCounts = getLastSeenCounts();
  lastSeenCounts[roomCode] = getRoomMessageCount(roomCode);
  setLastSeenCounts(lastSeenCounts);
  updateUnreadBadge(roomCode);
}

function incrementUnreadRoomCount(roomCode, increment) {
  if (!Number.isFinite(increment) || increment <= 0) {
    return;
  }

  setRoomMessageCount(roomCode, getRoomMessageCount(roomCode) + increment);
  updateUnreadBadge(roomCode);
}

function initializeUnreadBadges() {
  const currentRoomCode = getCurrentRoomCode();
  if (currentRoomCode) {
    markRoomAsSeen(currentRoomCode);
  }

  channelPills.forEach((_pill, roomCode) => {
    updateUnreadBadge(roomCode);
  });
}

function getModalFocusableElements() {
  if (!roomModal) {
    return [];
  }

  return Array.from(roomModal.querySelectorAll(focusableSelector)).filter(
    (element) => !element.hasAttribute("hidden") && !element.closest("[hidden]"),
  );
}

function createMessage(name, msg, options = {}) {
  if (!messages) {
    return;
  }

  const { announce = true } = options;
  const isJoinMessage = msg === "has entered the room" || msg === "has left the room";
  const createdAt = new Date();
  const timestampLabel = formatTimestamp(createdAt);

  const row = document.createElement("article");
  row.className = "message-row";
  if (isJoinMessage) {
    row.classList.add("is-join");
  }

  const content = document.createElement("p");
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

  const timestamp = document.createElement("time");
  timestamp.className = "muted";
  timestamp.dateTime = createdAt.toISOString();
  timestamp.textContent = timestampLabel;

  meta.appendChild(timestamp);

  row.appendChild(content);
  row.appendChild(meta);

  messages.appendChild(row);
  messages.scrollTop = messages.scrollHeight;

  if (announce) {
    announceStatus(isJoinMessage ? `${name} ${msg}` : `${name} says ${msg}`);
  }
}

function isRoomStatusMessage(message) {
  return message === "has entered the room" || message === "has left the room";
}

socketio.on("message", (data) => {
  createMessage(data.name, data.message);
  if (!isRoomStatusMessage(data.message)) {
    incrementUnreadRoomCount(getCurrentRoomCode(), 1);
    markRoomAsSeen(getCurrentRoomCode());
  }
});

socketio.on("connect", () => {
  if (!shouldAnnounceRoomJoin) {
    return;
  }

  shouldAnnounceRoomJoin = false;
  socketio.emit("announce_join");
});

socketio.on("presence", (data) => {
  if (!data || typeof data.count !== "number") {
    return;
  }

  updatePresenceIndicator(data.count);
});

socketio.on("unread_update", (data) => {
  if (!data || typeof data.room !== "string" || typeof data.increment !== "number") {
    return;
  }

  incrementUnreadRoomCount(data.room, data.increment);
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

  if (isOpen) {
    previousFocusedElement = document.activeElement instanceof HTMLElement ? document.activeElement : null;
  }

  roomModal.hidden = !isOpen;
  document.body.classList.toggle("modal-open", isOpen);
  if (openRoomModalButton) {
    openRoomModalButton.setAttribute("aria-expanded", String(isOpen));
  }
  if (roomShell) {
    if (isOpen) {
      roomShell.setAttribute("aria-hidden", "true");
      roomShell.setAttribute("inert", "");
    } else {
      roomShell.removeAttribute("aria-hidden");
      roomShell.removeAttribute("inert");
    }
  }

  if (isOpen) {
    const focusableElements = getModalFocusableElements();
    const nextFocusTarget = focusableElements[0] || roomCodeInput || closeRoomModalButton;
    if (nextFocusTarget) {
      nextFocusTarget.focus();
    }
  } else if (previousFocusedElement && typeof previousFocusedElement.focus === "function") {
    previousFocusedElement.focus();
  }
}

function setRoomModalError(message) {
  if (!roomModalError) {
    return;
  }

  roomModalError.textContent = message || "";
  roomModalError.hidden = !message;
  if (roomCodeInput) {
    if (message) {
      roomCodeInput.setAttribute("aria-invalid", "true");
      roomCodeInput.setAttribute("aria-describedby", "room-modal-error");
    } else {
      roomCodeInput.removeAttribute("aria-invalid");
      roomCodeInput.removeAttribute("aria-describedby");
    }
  }
}

function handleModalKeydown(event) {
  if (!roomModal || roomModal.hidden) {
    return;
  }

  if (event.key === "Escape") {
    event.preventDefault();
    toggleRoomModal(false);
    return;
  }

  if (event.key !== "Tab") {
    return;
  }

  const focusableElements = getModalFocusableElements();
  if (!focusableElements.length) {
    return;
  }

  const firstElement = focusableElements[0];
  const lastElement = focusableElements[focusableElements.length - 1];

  if (!roomModal.contains(document.activeElement)) {
    event.preventDefault();
    firstElement.focus();
    return;
  }

  if (event.shiftKey && document.activeElement === firstElement) {
    event.preventDefault();
    lastElement.focus();
  } else if (!event.shiftKey && document.activeElement === lastElement) {
    event.preventDefault();
    firstElement.focus();
  }
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

document.addEventListener("keydown", handleModalKeydown);

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
        if (roomCodeInput) {
          roomCodeInput.focus();
        }
        return;
      }

      window.location.href = payload.redirect_url || "/room";
    } catch (_error) {
      setRoomModalError("Unable to enter that channel.");
      if (roomCodeInput) {
        roomCodeInput.focus();
      }
    }
  });
}

if (roomModal && !roomModal.hidden) {
  toggleRoomModal(true);
}

if (presenceIndicator) {
  const initialCount = Number.parseInt(presenceIndicator.dataset.memberCount || "0", 10);
  updatePresenceIndicator(Number.isNaN(initialCount) ? 0 : initialCount);
}

initializeUnreadBadges();
