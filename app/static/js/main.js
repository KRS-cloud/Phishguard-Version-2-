// Mobile navigation menu toggle
const menuButton = document.getElementById("menuButton");
const navigation = document.getElementById("navigation");

if (menuButton && navigation) {
    menuButton.addEventListener("click", () => {
        const isOpen = navigation.classList.toggle("is-open");

        menuButton.setAttribute(
            "aria-expanded",
            String(isOpen)
        );
    });

    navigation.querySelectorAll("a").forEach((link) => {
        link.addEventListener("click", () => {
            navigation.classList.remove("is-open");

            menuButton.setAttribute(
                "aria-expanded",
                "false"
            );
        });
    });
}

// Password visibility toggle
document
    .querySelectorAll("[data-password-target]")
    .forEach((button) => {
        button.addEventListener("click", () => {
            const targetId = button.dataset.passwordTarget;
            const passwordInput = document.getElementById(targetId);

            if (!passwordInput) {
                return;
            }

            const isHidden = passwordInput.type === "password";

            passwordInput.type = isHidden
                ? "text"
                : "password";

            button.textContent = isHidden
                ? "Hide"
                : "Show";
        });
    });

// Flash message dismissals
document
    .querySelectorAll(".flash-close")
    .forEach((button) => {
        button.addEventListener("click", () => {
            const message = button.closest(".flash-message");

            if (message) {
                message.remove();
            }
        });
    });

// QR Code file input display
const qrImageInput = document.getElementById("qr_image");
const selectedFileName = document.getElementById("selected-file-name");

if (qrImageInput && selectedFileName) {
    qrImageInput.addEventListener("change", () => {
        const selectedFile = qrImageInput.files[0];

        selectedFileName.textContent = selectedFile
            ? selectedFile.name
            : "No image selected";
    });
}

// Copy to clipboard buttons
document
    .querySelectorAll("[data-copy-text]")
    .forEach((button) => {
        button.addEventListener("click", async () => {
            const text = button.dataset.copyText;

            try {
                await navigator.clipboard.writeText(text);

                button.textContent = "Copied";

                window.setTimeout(() => {
                    button.textContent = "Copy";
                }, 1500);
            } catch (error) {
                button.textContent = "Copy failed";
            }
        });
    });

// AI Assistant, Scan Handler, and Password Tools
document.addEventListener("DOMContentLoaded", function () {
    const assistantForm = document.getElementById("assistantForm");
    const assistantInput = document.getElementById("assistantInput");
    const assistantChat = document.getElementById("assistantChat");
    const assistantSendButton = document.getElementById("assistantSendButton");

    function addChatMessage(message, sender) {
        if (!assistantChat) {
            return;
        }

        const messageElement = document.createElement("div");
        messageElement.classList.add("chat-message");

        if (sender === "user") {
            messageElement.classList.add("user-message");
        } else {
            messageElement.classList.add("assistant-message");
        }

        const avatar = document.createElement("div");
        avatar.classList.add("message-avatar");
        avatar.textContent = sender === "user" ? "You" : "AI";

        const content = document.createElement("div");
        content.classList.add("message-content");

        const paragraph = document.createElement("p");
        paragraph.textContent = message;

        content.appendChild(paragraph);

        messageElement.appendChild(avatar);
        messageElement.appendChild(content);

        assistantChat.appendChild(messageElement);
        assistantChat.scrollTop = assistantChat.scrollHeight;
    }

    async function sendAssistantMessage(message) {
        if (!message) {
            return;
        }

        addChatMessage(message, "user");

        if (assistantSendButton) {
            assistantSendButton.disabled = true;
            assistantSendButton.textContent = "Thinking...";
        }

        try {
            const response = await fetch("/assistant/message", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ message: message })
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error("Assistant server error:", errorText);
                throw new Error("Server returned " + response.status);
            }

            const data = await response.json();

            if (!data.reply) {
                throw new Error("No reply received.");
            }

            addChatMessage(data.reply, "assistant");
        } catch (error) {
            console.error("Assistant error:", error);
            addChatMessage(
                "The assistant could not process your request. Please check the server and try again.",
                "assistant"
            );
        } finally {
            if (assistantSendButton) {
                assistantSendButton.disabled = false;
                assistantSendButton.textContent = "Send";
            }
        }
    }

    if (assistantForm && assistantInput) {
        assistantForm.addEventListener("submit", function (event) {
            event.preventDefault();

            const message = assistantInput.value.trim();

            if (!message) {
                return;
            }

            assistantInput.value = "";
            sendAssistantMessage(message);
        });
    }

    const suggestionButtons = document.querySelectorAll(".suggestion-button");

    suggestionButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            const question = button.getAttribute("data-question");

            if (!question) {
                return;
            }

            sendAssistantMessage(question);
        });
    });

    // Explain Scan Result Handler
    const explainScanButton = document.getElementById("explainScanButton");
    const scanResultData = document.getElementById("scanResultData");

    if (explainScanButton && scanResultData) {
        explainScanButton.addEventListener("click", async function () {
            let scanResult;

            try {
                scanResult = JSON.parse(scanResultData.textContent);
            } catch (error) {
                console.error("Could not read scan result:", error);
                return;
            }

            explainScanButton.disabled = true;
            explainScanButton.textContent = "Opening Assistant...";

            try {
                const response = await fetch("/assistant/explain-scan", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ scan_result: scanResult })
                });

                if (!response.ok) {
                    throw new Error("Could not explain scan.");
                }

                const data = await response.json();

                sessionStorage.setItem("phishguard_scan_explanation", data.reply);
                window.location.href = "/assistant";
            } catch (error) {
                console.error(error);
                explainScanButton.disabled = false;
                explainScanButton.textContent = "Explain with AI";
            }
        });
    }

    // Password Security & Generator Handlers
    const generatePasswordButton = document.getElementById("generatePasswordButton");
    const generatedPassword = document.getElementById("generatedPassword");
    const copyPasswordButton = document.getElementById("copyPasswordButton");
    const passwordLength = document.getElementById("passwordLength");
    const passwordLengthValue = document.getElementById("passwordLengthValue");

    if (passwordLength && passwordLengthValue) {
        passwordLength.addEventListener("input", function () {
            passwordLengthValue.textContent = passwordLength.value;
        });
    }

    if (generatePasswordButton) {
        generatePasswordButton.addEventListener("click", async function () {
            const errorElement = document.getElementById("generatorError");
            if (errorElement) {
                errorElement.textContent = "";
            }

            const options = {
                length: passwordLength ? passwordLength.value : 16,
                uppercase: document.getElementById("useUppercase")?.checked ?? true,
                lowercase: document.getElementById("useLowercase")?.checked ?? true,
                numbers: document.getElementById("useNumbers")?.checked ?? true,
                symbols: document.getElementById("useSymbols")?.checked ?? true,
                exclude_ambiguous: document.getElementById("excludeAmbiguous")?.checked ?? false
            };

            try {
                const response = await fetch(
                    generatePasswordButton.dataset.generateUrl,
                    {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify(options)
                    }
                );

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(
                        data.error || "Could not generate password."
                    );
                }

                if (generatedPassword) {
                    generatedPassword.value = data.password;
                }
            } catch (error) {
                if (errorElement) {
                    errorElement.textContent = error.message;
                }
            }
        });
    }

    if (copyPasswordButton && generatedPassword) {
        copyPasswordButton.addEventListener("click", async function () {
            if (!generatedPassword.value) {
                return;
            }

            await navigator.clipboard.writeText(generatedPassword.value);

            copyPasswordButton.textContent = "Copied";

            setTimeout(function () {
                copyPasswordButton.textContent = "Copy";
            }, 1200);
        });
    }

    const togglePasswordButton = document.getElementById("togglePasswordButton");
    const passwordToCheck = document.getElementById("passwordToCheck");

    if (togglePasswordButton && passwordToCheck) {
        togglePasswordButton.addEventListener("click", function () {
            const hidden = passwordToCheck.type === "password";

            passwordToCheck.type = hidden ? "text" : "password";
            togglePasswordButton.textContent = hidden ? "Hide" : "Show";
        });
    }

    const checkPasswordButton = document.getElementById("checkPasswordButton");

    if (checkPasswordButton && passwordToCheck) {
        checkPasswordButton.addEventListener("click", async function () {
            const password = passwordToCheck.value;

            if (!password) {
                return;
            }

            try {
                const response = await fetch(
                    checkPasswordButton.dataset.checkUrl,
                    {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({
                            password: password
                        })
                    }
                );

                const data = await response.json();

                const result = document.getElementById("passwordResult");
                if (result) {
                    result.classList.remove("hidden");
                }

                const strengthLabel = document.getElementById("strengthLabel");
                if (strengthLabel) {
                    strengthLabel.textContent = data.strength;
                }

                const strengthScore = document.getElementById("strengthScore");
                if (strengthScore) {
                    strengthScore.textContent = data.score + "/100";
                }

                const strengthMeterFill = document.getElementById("strengthMeterFill");
                if (strengthMeterFill) {
                    strengthMeterFill.style.width = data.score + "%";
                }

                const entropyValue = document.getElementById("entropyValue");
                if (entropyValue) {
                    entropyValue.textContent = data.entropy + " bits";
                }

                const crackTimeValue = document.getElementById("crackTimeValue");
                if (crackTimeValue) {
                    crackTimeValue.textContent = data.crack_time;
                }

                const warnings = document.getElementById("passwordWarnings");
                const suggestions = document.getElementById("passwordSuggestions");

                if (warnings) {
                    warnings.innerHTML = "";
                    if (!data.warnings || data.warnings.length === 0) {
                        const item = document.createElement("li");
                        item.textContent = "No major weaknesses detected.";
                        warnings.appendChild(item);
                    } else {
                        data.warnings.forEach(function (warning) {
                            const item = document.createElement("li");
                            item.textContent = warning;
                            warnings.appendChild(item);
                        });
                    }
                }

                if (suggestions) {
                    suggestions.innerHTML = "";
                    if (!data.suggestions || data.suggestions.length === 0) {
                        const item = document.createElement("li");
                        item.textContent = "Password meets the main strength checks.";
                        suggestions.appendChild(item);
                    } else {
                        data.suggestions.forEach(function (suggestion) {
                            const item = document.createElement("li");
                            item.textContent = suggestion;
                            suggestions.appendChild(item);
                        });
                    }
                }
            } catch (error) {
                console.error("Error checking password strength:", error);
            }
        });
    }
});