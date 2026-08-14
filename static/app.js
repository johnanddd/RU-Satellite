// =========================================================
// RU Satellite
// Front-end behavior
// =========================================================

const EMAIL_STORAGE_KEY = "ruSatelliteEmail";


document.addEventListener("DOMContentLoaded", () => {
    initializeRememberedEmail();
    initializeHomepage();
    initializeDashboard();
});


// ---------------------------------------------------------
// Remembered email
// ---------------------------------------------------------

function initializeRememberedEmail() {
    const dashboard =
        document.querySelector("[data-dashboard]");

    const changeEmailLink =
        document.getElementById("change-email");

    if (dashboard) {
        const email =
            dashboard.dataset.email?.trim();

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
}


// ---------------------------------------------------------
// Homepage
// ---------------------------------------------------------

function initializeHomepage() {
    const emailForm =
        document.getElementById("email-form");

    const emailInput =
        document.getElementById("email");

    if (!emailForm || !emailInput) {
        return;
    }

    const rememberedEmail =
        localStorage.getItem(
            EMAIL_STORAGE_KEY
        );

    if (
        rememberedEmail &&
        !emailInput.value.trim()
    ) {
        emailInput.value =
            rememberedEmail;
    }

    emailForm.addEventListener(
        "submit",
        () => {
            const email =
                emailInput.value
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
    const dashboard =
        document.querySelector(
            "[data-dashboard]"
        );

    if (!dashboard) {
        return;
    }

    const sectionInput =
        document.getElementById(
            "section-search-input"
        );

    const findButton =
        document.getElementById(
            "find-section-button"
        );

    const courseResult =
        document.getElementById(
            "course-result"
        );

    const watchlistItems =
        document.getElementById(
            "watchlist-items"
        );

    const watchCount =
        document.getElementById(
            "watch-count"
        );

    const sectionIndexesInput =
        document.getElementById(
            "section-indexes"
        );

    const saveButton =
        document.getElementById(
            "submit-watchlist"
        );

    const messageBox =
        document.getElementById(
            "message"
        );

    const watchlistForm =
        document.getElementById(
            "subscription-form"
        );


    if (
        !sectionInput ||
        !findButton ||
        !courseResult ||
        !watchlistItems ||
        !watchCount ||
        !sectionIndexesInput ||
        !saveButton ||
        !messageBox ||
        !watchlistForm
    ) {
        console.error(
            "RU Satellite dashboard could not initialize."
        );

        return;
    }


    const MAX_SECTIONS = 5;

    const email =
        dashboard.dataset.email || "";

    const watchlist = [];


    // -----------------------------------------------------
    // Load sections that already exist on the dashboard
    // -----------------------------------------------------

    const existingSections =
        document.querySelectorAll(
            "[data-existing-section]"
        );

    existingSections.forEach(
        element => {
            watchlist.push({
                registration_index:
                    element.dataset
                        .registrationIndex || "",

                course_code:
                    element.dataset
                        .courseCode || "",

                course_title:
                    element.dataset
                        .courseTitle ||
                    "Rutgers section",

                instructors:
                    element.dataset
                        .instructors ||
                    "Instructor not listed",

                notification_sent:
                    element.querySelector(
                        ".notified"
                    ) !== null
            });
        }
    );


    // -----------------------------------------------------
    // Messages
    // -----------------------------------------------------

    function showMessage(
        text,
        type = "success"
    ) {
        messageBox.textContent =
            text;

        if (type === "error") {
            messageBox.className =
                "message error-message";
        } else {
            messageBox.className =
                "message success-message";
        }
    }


    function clearMessage() {
        messageBox.textContent = "";

        messageBox.className =
            "message hidden";
    }


    // -----------------------------------------------------
    // Safe text
    // -----------------------------------------------------

    function escapeHtml(value) {
        const div =
            document.createElement("div");

        div.textContent =
            value ?? "";

        return div.innerHTML;
    }


    // -----------------------------------------------------
    // Render watchlist
    // -----------------------------------------------------

    function renderWatchlist() {
        watchlistItems.innerHTML = "";


        if (watchlist.length === 0) {
            const empty =
                document.createElement("p");

            empty.id =
                "empty-watchlist";

            empty.className =
                "empty-watchlist";

            empty.textContent =
                "You are not watching any sections yet.";

            watchlistItems.appendChild(
                empty
            );
        }


        for (const section of watchlist) {
            const item =
                document.createElement(
                    "div"
                );

            item.className =
                "watchlist-item";


            const statusText =
                section.notification_sent
                    ? "Alert already sent"
                    : "Monitoring";


            const statusClass =
                section.notification_sent
                    ? "notified"
                    : "monitoring";


            item.innerHTML = `
                <div class="course-title">
                    ${escapeHtml(
                        section.course_title
                    )}
                </div>

                ${
                    section.course_code
                        ? `
                        <div class="course-code">
                            ${escapeHtml(
                                section.course_code
                            )}
                        </div>
                        `
                        : ""
                }

                <div class="course-detail">
                    Section ${escapeHtml(
                        section.registration_index
                    )}
                </div>

                <div class="course-detail">
                    ${escapeHtml(
                        section.instructors
                    )}
                </div>

                <div class="section-status ${statusClass}">
                    ${statusText}
                </div>
            `;


            const removeButton =
                document.createElement(
                    "button"
                );

            removeButton.type =
                "button";

            removeButton.className =
                "remove-button";

            removeButton.textContent =
                "Remove";


            removeButton.addEventListener(
                "click",
                () => {
                    const index =
                        watchlist.findIndex(
                            item =>
                                item.registration_index ===
                                section.registration_index
                        );

                    if (index !== -1) {
                        watchlist.splice(
                            index,
                            1
                        );
                    }

                    clearMessage();

                    renderWatchlist();
                }
            );


            item.appendChild(
                removeButton
            );

            watchlistItems.appendChild(
                item
            );
        }


        watchCount.textContent =
            `${watchlist.length} / ${MAX_SECTIONS}`;


        sectionIndexesInput.value =
            watchlist
                .map(
                    section =>
                        section.registration_index
                )
                .join(",");


        saveButton.disabled =
            watchlist.length === 0;
    }


    // -----------------------------------------------------
    // Add section
    // -----------------------------------------------------

    function addSection(section) {
        clearMessage();


        if (
            watchlist.length >=
            MAX_SECTIONS
        ) {
            showMessage(
                "You can watch a maximum of 5 sections.",
                "error"
            );

            return;
        }


        const alreadyAdded =
            watchlist.some(
                item =>
                    item.registration_index ===
                    String(
                        section.registration_index
                    )
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
                String(
                    section.registration_index
                ),

            course_code:
                section.course_code || "",

            course_title:
                section.course_title ||
                "Rutgers section",

            instructors:
                section.instructors ||
                "Instructor not listed",

            notification_sent:
                false
        });


        renderWatchlist();


        courseResult.innerHTML = "";

        sectionInput.value = "";

        sectionInput.focus();


        showMessage(
            "Section added. Save your watchlist when you're done."
        );
    }


    // -----------------------------------------------------
    // Display search result
    // -----------------------------------------------------

    function displaySectionResult(
        section
    ) {
        courseResult.innerHTML = "";


        const card =
            document.createElement(
                "div"
            );

        card.className =
            "course-result";


        card.innerHTML = `
            <div class="course-title">
                ${escapeHtml(
                    section.course_title
                )}
            </div>

            ${
                section.course_code
                    ? `
                    <div class="course-code">
                        ${escapeHtml(
                            section.course_code
                        )}
                    </div>
                    `
                    : ""
            }

            <div class="course-detail">
                Section ${escapeHtml(
                    section.registration_index
                )}
            </div>

            <div class="course-detail">
                ${escapeHtml(
                    section.instructors
                )}
            </div>
        `;


        const addButton =
            document.createElement(
                "button"
            );

        addButton.type =
            "button";

        addButton.className =
            "primary-button";

        addButton.textContent =
            "Add to Watchlist";

        addButton.style.marginTop =
            "14px";


        addButton.addEventListener(
            "click",
            () => {
                addSection(section);
            }
        );


        card.appendChild(
            addButton
        );

        courseResult.appendChild(
            card
        );
    }


    // -----------------------------------------------------
    // Find section
    // -----------------------------------------------------

    async function findSection() {
        clearMessage();

        courseResult.innerHTML = "";


        const sectionIndex =
            sectionInput.value.trim();


        if (
            !/^\d{5}$/.test(
                sectionIndex
            )
        ) {
            showMessage(
                "Enter a valid five-digit section index.",
                "error"
            );

            sectionInput.focus();

            return;
        }


        const duplicate =
            watchlist.some(
                section =>
                    section.registration_index ===
                    sectionIndex
            );


        if (duplicate) {
            showMessage(
                "That section is already in your watchlist.",
                "error"
            );

            return;
        }


        findButton.disabled =
            true;

        findButton.textContent =
            "Searching...";


        try {
            const response =
                await fetch(
                    `/api/section/${encodeURIComponent(
                        sectionIndex
                    )}`
                );


            const data =
                await response.json();


            if (!response.ok) {
                showMessage(
                    data.error ||
                    "That section could not be found.",
                    "error"
                );

                return;
            }


            displaySectionResult(
                data
            );

        } catch (error) {
            console.error(
                "RU Satellite search failed:",
                error
            );


            showMessage(
                "Could not search for that section.",
                "error"
            );

        } finally {
            findButton.disabled =
                false;

            findButton.textContent =
                "Find Section";
        }
    }


    // -----------------------------------------------------
    // Button events
    // -----------------------------------------------------

    findButton.addEventListener(
        "click",
        findSection
    );


    sectionInput.addEventListener(
        "keydown",
        event => {
            if (
                event.key === "Enter"
            ) {
                event.preventDefault();

                findSection();
            }
        }
    );


    sectionInput.addEventListener(
        "input",
        () => {
            sectionInput.value =
                sectionInput.value
                    .replace(
                        /\D/g,
                        ""
                    )
                    .slice(
                        0,
                        5
                    );
        }
    );


    watchlistForm.addEventListener(
        "submit",
        event => {
            if (
                watchlist.length === 0
            ) {
                event.preventDefault();

                showMessage(
                    "Add at least one section before saving.",
                    "error"
                );

                return;
            }


            sectionIndexesInput.value =
                watchlist
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


            saveButton.disabled =
                true;

            saveButton.textContent =
                "Saving...";
        }
    );


    renderWatchlist();
}