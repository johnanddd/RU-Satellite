// =========================================================
// RU Satellite
// Front-end behavior
// =========================================================

document.addEventListener("DOMContentLoaded", () => {
    initializeRememberedEmail();
    initializeHomepage();
    initializeDashboard();
});


// ---------------------------------------------------------
// Remembered email
// ---------------------------------------------------------

const EMAIL_STORAGE_KEY = "ruSatelliteEmail";


function initializeRememberedEmail() {
    const dashboard = document.querySelector("[data-dashboard]");
    const emailForm = document.getElementById("email-form");
    const changeEmailLink = document.getElementById("change-email");

    if (dashboard) {
        const email = dashboard.dataset.email?.trim();

        if (email) {
            localStorage.setItem(
                EMAIL_STORAGE_KEY,
                email
            );
        }
    }

    if (changeEmailLink) {
        changeEmailLink.addEventListener(
            "click",
            () => {
                localStorage.removeItem(
                    EMAIL_STORAGE_KEY
                );
            }
        );
    }

    if (emailForm && !dashboard) {
        const rememberedEmail = localStorage.getItem(
            EMAIL_STORAGE_KEY
        );

        if (rememberedEmail) {
            window.location.replace(
                `/dashboard?email=${encodeURIComponent(
                    rememberedEmail
                )}`
            );
        }
    }
}


// ---------------------------------------------------------
// Homepage
// ---------------------------------------------------------

function initializeHomepage() {
    const emailForm = document.getElementById("email-form");
    const emailInput = document.getElementById("email");

    if (!emailForm || !emailInput) {
        return;
    }

    emailForm.addEventListener(
        "submit",
        () => {
            const email = emailInput.value
                .trim()
                .toLowerCase();

            if (email) {
                localStorage.setItem(
                    EMAIL_STORAGE_KEY,
                    email
                );
            }
        }
    );
}


// ---------------------------------------------------------
// Dashboard
// ---------------------------------------------------------

function initializeDashboard() {
    const dashboard = document.querySelector("[data-dashboard]");

    if (!dashboard) {
        return;
    }

    const sectionInput = document.getElementById(
        "section-search-input"
    );

    const findButton = document.getElementById(
        "find-section-button"
    );

    const courseResult = document.getElementById(
        "course-result"
    );

    const watchlistItems = document.getElementById(
        "watchlist-items"
    );

    const watchCount = document.getElementById(
        "watch-count"
    );

    const sectionIndexesInput = document.getElementById(
        "section-indexes"
    );

    const saveButton = document.getElementById(
        "save-watchlist-button"
    );

    const clientMessage = document.getElementById(
        "client-message"
    );

    const watchlistForm = document.getElementById(
        "watchlist-form"
    );

    if (
        !sectionInput ||
        !findButton ||
        !courseResult ||
        !watchlistItems ||
        !watchCount ||
        !sectionIndexesInput ||
        !saveButton ||
        !clientMessage ||
        !watchlistForm
    ) {
        return;
    }

    const maxSections = Number(
        dashboard.dataset.maxSections || 5
    );

    const email = dashboard.dataset.email || "";

    const watchlist = loadInitialWatchlist(
        watchlistItems
    );


    function showMessage(text, type = "success") {
        clientMessage.textContent = text;
        clientMessage.className =
            `message ${type}-message`;
    }


    function clearMessage() {
        clientMessage.textContent = "";
        clientMessage.className = "message";
    }


    function updateWatchlist() {
        watchlistItems.replaceChildren();

        if (watchlist.length === 0) {
            watchlistItems.appendChild(
                buildEmptyWatchlist()
            );
        } else {
            for (const section of watchlist) {
                watchlistItems.appendChild(
                    buildWatchlistItem(
                        section,
                        removeSection
                    )
                );
            }
        }

        watchCount.textContent =
            `${watchlist.length} / ${maxSections}`;

        sectionIndexesInput.value = watchlist
            .map(
                section =>
                    section.registration_index
            )
            .join(",");

        saveButton.disabled =
            watchlist.length === 0;
    }


    function removeSection(sectionIndex) {
        const position = watchlist.findIndex(
            section =>
                section.registration_index
                === sectionIndex
        );

        if (position === -1) {
            return;
        }

        const removed = watchlist[position];

        watchlist.splice(
            position,
            1
        );

        updateWatchlist();

        showMessage(
            `${removed.course_title || "Section"} removed. `
            + "Save your watchlist to apply the change.",
            "success"
        );
    }


    function addSection(section) {
        clearMessage();

        if (watchlist.length >= maxSections) {
            showMessage(
                `You can watch a maximum of `
                + `${maxSections} sections.`,
                "error"
            );

            return;
        }

        const alreadyAdded = watchlist.some(
            item =>
                item.registration_index
                === section.registration_index
        );

        if (alreadyAdded) {
            showMessage(
                "That section is already in your watchlist.",
                "error"
            );

            return;
        }

        watchlist.push({
            registration_index:
                String(section.registration_index),
            course_code:
                section.course_code || "",
            course_title:
                section.course_title || "Rutgers section",
            instructors:
                section.instructors
                || "Instructor not listed",
            notification_sent:
                false,
        });

        updateWatchlist();

        courseResult.replaceChildren();
        sectionInput.value = "";
        sectionInput.focus();

        showMessage(
            "Section added. Save your watchlist "
            + "to start monitoring it.",
            "success"
        );
    }


    function displaySectionResult(section) {
        courseResult.replaceChildren();

        const card = document.createElement("article");
        card.className = "course-result";

        const code = document.createElement("p");
        code.className = "course-code";
        code.textContent =
            section.course_code || "Rutgers Course";

        const title = document.createElement("h3");
        title.className = "course-title";
        title.textContent =
            section.course_title || "Rutgers section";

        const meta = document.createElement("div");
        meta.className = "course-meta";

        const indexText = document.createElement("span");
        indexText.append("Index ");

        const indexStrong =
            document.createElement("strong");

        indexStrong.textContent =
            String(section.registration_index);

        indexText.appendChild(indexStrong);

        const instructorText =
            document.createElement("span");

        instructorText.append("Instructor ");

        const instructorStrong =
            document.createElement("strong");

        instructorStrong.textContent =
            section.instructors
            || "Instructor not listed";

        instructorText.appendChild(
            instructorStrong
        );

        meta.append(
            indexText,
            instructorText
        );

        const addButton =
            document.createElement("button");

        addButton.type = "button";
        addButton.className = "primary-button";
        addButton.textContent = "Add to Watchlist";

        addButton.addEventListener(
            "click",
            () => {
                addSection(section);
            }
        );

        card.append(
            code,
            title,
            meta,
            addButton
        );

        courseResult.appendChild(card);
    }


    async function findSection() {
        clearMessage();
        courseResult.replaceChildren();

        const sectionIndex =
            sectionInput.value.trim();

        if (!/^\d{5}$/.test(sectionIndex)) {
            showMessage(
                "Enter a valid five-digit section index.",
                "error"
            );

            sectionInput.focus();
            return;
        }

        const duplicate = watchlist.some(
            section =>
                section.registration_index
                === sectionIndex
        );

        if (duplicate) {
            showMessage(
                "That section is already in your watchlist.",
                "error"
            );

            return;
        }

        findButton.disabled = true;
        findButton.textContent = "Searching...";

        try {
            const response = await fetch(
                `/api/section/${encodeURIComponent(
                    sectionIndex
                )}`
            );

            const data = await response.json();

            if (!response.ok) {
                showMessage(
                    data.error
                    || "That section could not be found.",
                    "error"
                );

                return;
            }

            displaySectionResult(data);

        } catch (error) {
            console.error(
                "RU Satellite section search failed:",
                error
            );

            showMessage(
                "RU Satellite could not search right now. "
                + "Try again in a moment.",
                "error"
            );

        } finally {
            findButton.disabled = false;
            findButton.textContent = "Find Section";
        }
    }


    findButton.addEventListener(
        "click",
        findSection
    );


    sectionInput.addEventListener(
        "keydown",
        event => {
            if (event.key === "Enter") {
                event.preventDefault();
                findSection();
            }
        }
    );


    sectionInput.addEventListener(
        "input",
        () => {
            sectionInput.value = sectionInput.value
                .replace(/\D/g, "")
                .slice(0, 5);
        }
    );


    watchlistForm.addEventListener(
        "submit",
        event => {
            if (watchlist.length === 0) {
                event.preventDefault();

                showMessage(
                    "Add at least one section before saving.",
                    "error"
                );

                return;
            }

            sectionIndexesInput.value = watchlist
                .map(
                    section =>
                        section.registration_index
                )
                .join(",");

            if (email) {
                localStorage.setItem(
                    EMAIL_STORAGE_KEY,
                    email
                );
            }

            saveButton.disabled = true;
            saveButton.textContent = "Saving...";
        }
    );


    updateWatchlist();
}


// ---------------------------------------------------------
// Initial dashboard data
// ---------------------------------------------------------

function loadInitialWatchlist(container) {
    const elements = container.querySelectorAll(
        "[data-section-index]"
    );

    return Array.from(elements).map(
        element => {
            const statusBadge =
                element.querySelector(
                    ".status-badge"
                );

            return {
                registration_index:
                    element.dataset.sectionIndex || "",
                course_code:
                    element.dataset.courseCode || "",
                course_title:
                    element.dataset.courseTitle
                    || "Rutgers section",
                instructors:
                    element.dataset.instructors
                    || "Instructor not listed",
                notification_sent:
                    statusBadge?.classList.contains(
                        "notified"
                    ) || false,
            };
        }
    );
}


// ---------------------------------------------------------
// UI builders
// ---------------------------------------------------------

function buildWatchlistItem(
    section,
    onRemove
) {
    const article =
        document.createElement("article");

    article.className = "watchlist-item";
    article.dataset.sectionIndex =
        section.registration_index;

    article.dataset.courseCode =
        section.course_code || "";

    article.dataset.courseTitle =
        section.course_title || "";

    article.dataset.instructors =
        section.instructors || "";

    const top =
        document.createElement("div");

    top.className = "watchlist-item-top";

    const titleArea =
        document.createElement("div");

    const code =
        document.createElement("p");

    code.className = "course-code";
    code.textContent =
        section.course_code || "Rutgers Course";

    const title =
        document.createElement("h3");

    title.className = "course-title";
    title.textContent =
        section.course_title || "Rutgers section";

    titleArea.append(
        code,
        title
    );

    const badge =
        document.createElement("span");

    badge.className =
        section.notification_sent
            ? "status-badge notified"
            : "status-badge monitoring";

    badge.textContent =
        section.notification_sent
            ? "Alert sent"
            : "Monitoring";

    top.append(
        titleArea,
        badge
    );

    const meta =
        document.createElement("div");

    meta.className = "course-meta";

    const index =
        document.createElement("span");

    index.append("Index ");

    const indexStrong =
        document.createElement("strong");

    indexStrong.textContent =
        section.registration_index;

    index.appendChild(
        indexStrong
    );

    const instructor =
        document.createElement("span");

    instructor.append("Instructor ");

    const instructorStrong =
        document.createElement("strong");

    instructorStrong.textContent =
        section.instructors
        || "Instructor not listed";

    instructor.appendChild(
        instructorStrong
    );

    meta.append(
        index,
        instructor
    );

    const removeButton =
        document.createElement("button");

    removeButton.type = "button";
    removeButton.className = "remove-button";
    removeButton.dataset.removeSection =
        section.registration_index;

    removeButton.textContent = "Remove";

    removeButton.addEventListener(
        "click",
        () => {
            onRemove(
                section.registration_index
            );
        }
    );

    article.append(
        top,
        meta,
        removeButton
    );

    return article;
}


function buildEmptyWatchlist() {
    const empty =
        document.createElement("div");

    empty.id = "empty-watchlist";
    empty.className = "empty-watchlist";

    const icon =
        document.createElement("div");

    icon.className = "empty-icon";
    icon.textContent = "📡";

    const heading =
        document.createElement("h3");

    heading.textContent =
        "Nothing on radar yet";

    const text =
        document.createElement("p");

    text.textContent =
        "Search for a Rutgers section and add it "
        + "to begin monitoring.";

    empty.append(
        icon,
        heading,
        text
    );

    return empty;
}