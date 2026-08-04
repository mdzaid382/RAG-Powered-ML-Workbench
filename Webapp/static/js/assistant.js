// ==========================================================
// AI Assistant
// ==========================================================

const chatContainer = document.getElementById("chatMessages");
const welcomeScreen = document.getElementById("welcomeScreen");
const chatMessages = document.getElementById("chatMessagesList");
const questionInput = document.getElementById("questionInput");
const sendButton = document.getElementById("sendButton");

let sessionId = null;
let waiting = false;

// ==========================================================
// Initialize Chat
// ==========================================================

window.addEventListener("load", initializeChat);

async function initializeChat() {

    try {

        const response = await fetch("/chat/new-session", {
            method: "POST"
        });

        if (!response.ok) {
            throw new Error("Unable to create chat session.");
        }

        const data = await response.json();
        sessionId = data.session_id;

    }
    catch (error) {
        // Session failed to initialize — surface it once the user tries to chat.
        console.error(error);
    }

}

// ==========================================================
// Capability shortcuts (welcome screen cards)
// ==========================================================

document.querySelectorAll(".capability-card").forEach(function (card) {

    card.addEventListener("click", function () {
        const prompt = card.dataset.prompt;
        if (!prompt) return;
        questionInput.value = prompt;
        sendMessage();
    });

});

// ==========================================================
// Events
// ==========================================================

sendButton.addEventListener("click", sendMessage);

questionInput.addEventListener("keydown", function (e) {

    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }

});

// Auto Resize

questionInput.addEventListener("input", autoResize);

function autoResize() {
    this.style.height = "52px";
    this.style.height = this.scrollHeight + "px";
}

// ==========================================================
// Send Message
// ==========================================================

async function sendMessage() {

    if (waiting) return;

    const question = questionInput.value.trim();
    if (question === "") return;

    if (!sessionId) {
        addBotMessage("Your chat session hasn't started yet — give it a second and try again.");
        return;
    }

    revealChat();

    addUserMessage(question);
    questionInput.value = "";
    questionInput.style.height = "52px";

    showTyping();
    waiting = true;
    sendButton.disabled = true;
    questionInput.disabled = true;

    try {

        const response = await fetch("/chat/ask", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                session_id: sessionId,
                question: question
            })
        });

        removeTyping();

        if (!response.ok) {
            throw new Error("Unable to get AI response.");
        }

        const data = await response.json();
        addBotMessage(data.answer);

    }
    catch (error) {
        removeTyping();
        addBotMessage(error.message);
    }
    finally {
        waiting = false;
        sendButton.disabled = false;
        questionInput.disabled = false;
        questionInput.focus();
    }

}

// ==========================================================
// Welcome screen <-> conversation
// ==========================================================

function revealChat() {
    if (!welcomeScreen.classList.contains("hidden")) {
        welcomeScreen.classList.add("hidden");
        chatMessages.classList.remove("hidden");
    }
}

// ==========================================================
// User Message
// ==========================================================

function addUserMessage(message) {

    const messageDiv = document.createElement("div");
    messageDiv.className = "message user";
    messageDiv.innerHTML = `
        <div class="bubble">${escapeHTML(message)}</div>
        <div class="avatar">YOU</div>
    `;

    chatMessages.appendChild(messageDiv);
    scrollBottom();

}

// ==========================================================
// AI Message
// ==========================================================

function addBotMessage(message) {

    revealChat();

    const messageDiv = document.createElement("div");
    messageDiv.className = "message ai";
    messageDiv.innerHTML = `
        <div class="avatar">AI</div>
        <div class="bubble">${formatMessage(message)}</div>
    `;

    chatMessages.appendChild(messageDiv);
    scrollBottom();

}

// ==========================================================
// Typing Indicator
// ==========================================================

function showTyping() {

    removeTyping();

    const typing = document.createElement("div");
    typing.className = "message ai";
    typing.id = "typingIndicator";
    typing.innerHTML = `
        <div class="avatar">AI</div>
        <div class="bubble">
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;

    chatMessages.appendChild(typing);
    scrollBottom();

}

function removeTyping() {
    const typing = document.getElementById("typingIndicator");
    if (typing) {
        typing.remove();
    }
}

// ==========================================================
// Message Formatter
// Escapes HTML first (safety), then renders a small safe
// subset of markdown: **bold**, `code`, and "* "/"- " bullet
// lists, since AI responses commonly use these.
// ==========================================================

function formatMessage(message) {

    const escaped = escapeHTML(message);
    const lines = escaped.split("\n");

    let html = "";
    let inList = false;

    lines.forEach(function (rawLine) {

        const line = rawLine.trim();
        const isBullet = /^([*-])\s+/.test(line);

        if (isBullet) {
            if (!inList) {
                html += "<ul>";
                inList = true;
            }
            html += `<li>${inlineFormat(line.replace(/^([*-])\s+/, ""))}</li>`;
            return;
        }

        if (inList) {
            html += "</ul>";
            inList = false;
        }

        if (line === "") {
            html += "<br>";
        } else {
            html += `<p>${inlineFormat(line)}</p>`;
        }

    });

    if (inList) {
        html += "</ul>";
    }

    return html;

}

function inlineFormat(text) {
    return text
        .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
        .replace(/`(.+?)`/g, "<code>$1</code>");
}

// ==========================================================
// Escape HTML
// ==========================================================

function escapeHTML(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

// ==========================================================
// Auto Scroll
// ==========================================================

function scrollBottom() {
    chatContainer.scrollTo({
        top: chatContainer.scrollHeight,
        behavior: "smooth"
    });
}
