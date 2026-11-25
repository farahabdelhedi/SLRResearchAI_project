
// Adresse de notre backend FastAPI
const API_URL = "http://127.0.0.1:8000";

// Session courante de validation humaine
let currentSessionId = null;
let currentQuestions = [];

// Éléments HTML
const researchForm = document.getElementById("research-form");
const generateBtn = document.getElementById("generate-btn");
const editBtn = document.getElementById("edit-btn");
const approveBtn = document.getElementById("approve-btn");
const rejectBtn = document.getElementById("reject-btn");

const resultsSection = document.getElementById("results-section");
const questionsContainer = document.getElementById("questions-container");
const editedQuestions = document.getElementById("edited-questions");
const messageBox = document.getElementById("message");
const finalSection = document.getElementById("final-section");

// Afficher un message
function showMessage(message, type = "info") {
    messageBox.textContent = message;
    messageBox.className = `message ${type}`;
}

// Masquer le message
function hideMessage() {
    messageBox.className = "message hidden";
    messageBox.textContent = "";
}

// Activer ou désactiver les boutons
function setLoading(button, loading, loadingText = "Chargement...") {
    if (loading) {
        button.dataset.originalText = button.textContent.trim();
        button.textContent = loadingText;
        button.disabled = true;
    } else {
        button.textContent = button.dataset.originalText || button.textContent;
        button.disabled = false;
    }
}

// Vérifier que le serveur FastAPI fonctionne
async function checkApiStatus() {
    const indicator = document.getElementById("status-indicator");
    const statusText = document.getElementById("api-status-text");

    try {
        const response = await fetch(`${API_URL}/api/health`);

        if (!response.ok) {
            throw new Error("Serveur indisponible");
        }

        indicator.className = "status-dot online";
        statusText.textContent = "API connectée";
    } catch (error) {
        indicator.className = "status-dot offline";
        statusText.textContent = "API déconnectée";
    }
}

// Transformer les questions en texte éditable
function formatQuestions(questions) {
    return questions
        .map(item => `${item.identifier}. ${item.question}`)
        .join("\n");
}

// Afficher les questions sous forme de cartes
function displayQuestions(questions) {
    questionsContainer.innerHTML = "";

    questions.forEach(question => {
        const card = document.createElement("article");
        card.className = "question-card";

        const title = document.createElement("h4");
        title.textContent = question.identifier;

        const content = document.createElement("p");
        content.textContent = question.question;

        card.appendChild(title);
        card.appendChild(content);

        questionsContainer.appendChild(card);
    });

    currentQuestions = questions;
    editedQuestions.value = formatQuestions(questions);
}

// Afficher le résultat final
function showFinalResult(title, description, rejected = false) {
    resultsSection.classList.add("hidden");
    finalSection.classList.remove("hidden");

    document.getElementById("final-title").textContent = title;
    document.getElementById("final-description").textContent = description;

    const icon = document.getElementById("final-icon");

    if (rejected) {
        icon.textContent = "×";
        icon.style.background = "#fff0f0";
        icon.style.color = "#d64545";
    } else {
        icon.textContent = "✓";
        icon.style.background = "#eaf8f1";
        icon.style.color = "#16865b";
    }
}

// 1. Génération des Research Questions
researchForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    hideMessage();

    const topic = document.getElementById("topic").value.trim();
    const objective = document.getElementById("objective").value.trim();
    const context = document.getElementById("context").value.trim();

    if (!topic || !objective) {
        showMessage("Le sujet et l'objectif sont obligatoires.", "error");
        return;
    }

    setLoading(generateBtn, true, "Génération en cours...");

    try {
        const response = await fetch(
            `${API_URL}/api/research-questions/generate`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                body: JSON.stringify({
                    topic,
                    objective,
                    context
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Erreur lors de la génération.");
        }

        if (!data.session_id || !data.questions || data.questions.length !== 3) {
            throw new Error(
                data.error ||
                "La génération n'a pas produit trois questions validées. Vérifiez les informations et réessayez."
            );
        }

        currentSessionId = data.session_id;

        displayQuestions(data.questions);

        document.getElementById("session-label").textContent =
            `Session : ${currentSessionId}`;

        document.getElementById("generation-status").textContent =
            data.status === "repaired"
                ? "Questions réparées automatiquement"
                : "En attente de validation humaine";

        finalSection.classList.add("hidden");
        resultsSection.classList.remove("hidden");

        showMessage(
            "Les trois questions ont été générées et validées. Vous pouvez maintenant les examiner.",
            "success"
        );

        resultsSection.scrollIntoView({ behavior: "smooth" });

    } catch (error) {
        showMessage(error.message, "error");
    } finally {
        setLoading(generateBtn, false);
    }
});

// 2. Modification des Research Questions
editBtn.addEventListener("click", async () => {
    hideMessage();

    if (!currentSessionId) {
        showMessage("Aucune session active.", "error");
        return;
    }

    const questionsText = editedQuestions.value.trim();

    if (!questionsText) {
        showMessage("Veuillez saisir les questions à modifier.", "error");
        return;
    }

    setLoading(editBtn, true, "Validation et réparation éventuelle...");

    try {
        const response = await fetch(
            `${API_URL}/api/research-questions/edit`,
            {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                body: JSON.stringify({
                    session_id: currentSessionId,
                    questions_text: questionsText
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Erreur lors de la modification.");
        }

        displayQuestions(data.questions);

        document.getElementById("generation-status").textContent =
            "Modifications validées — en attente de votre décision";

        showMessage(
            "Les modifications ont été enregistrées et validées. Vérifiez les questions proposées avant de les approuver.",
            "success"
        );

    } catch (error) {
        showMessage(error.message, "error");
    } finally {
        setLoading(editBtn, false);
    }
});

// 3. Approbation humaine
approveBtn.addEventListener("click", async () => {
    hideMessage();

    if (!currentSessionId) {
        showMessage("Aucune session active.", "error");
        return;
    }

    const confirmed = window.confirm(
        "Voulez-vous vraiment approuver ces trois questions ?"
    );

    if (!confirmed) return;

    setLoading(approveBtn, true, "Approbation...");

    try {
        const response = await fetch(
            `${API_URL}/api/research-questions/approve`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                body: JSON.stringify({
                    session_id: currentSessionId
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Erreur lors de l'approbation.");
        }

        showFinalResult(
            "Questions approuvées !",
            "Les trois questions de recherche ont été validées par le chercheur. Elles pourront être utilisées par les prochaines étapes du workflow SLRResearchAI."
        );

        currentSessionId = null;

    } catch (error) {
        showMessage(error.message, "error");
    } finally {
        setLoading(approveBtn, false);
    }
});

// 4. Rejet humain
rejectBtn.addEventListener("click", async () => {
    hideMessage();

    if (!currentSessionId) {
        showMessage("Aucune session active.", "error");
        return;
    }

    const confirmed = window.confirm(
        "Voulez-vous vraiment rejeter ces questions ?"
    );

    if (!confirmed) return;

    const reason = document.getElementById("rejection-reason").value.trim();

    setLoading(rejectBtn, true, "Rejet en cours...");

    try {
        const response = await fetch(
            `${API_URL}/api/research-questions/reject`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                body: JSON.stringify({
                    session_id: currentSessionId,
                    reason
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Erreur lors du rejet.");
        }

        showFinalResult(
            "Questions rejetées",
            data.rejection_reason
                ? `Votre décision a été enregistrée. Motif : ${data.rejection_reason}`
                : "Votre décision de rejet a été enregistrée.",
            true
        );

        currentSessionId = null;

    } catch (error) {
        showMessage(error.message, "error");
    } finally {
        setLoading(rejectBtn, false);
    }
});

// Vérification du backend au chargement
checkApiStatus();
