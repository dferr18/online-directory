/**
 * Online Directory Project — Client-side Search
 *
 * On the landing page: searches across all suburbs/categories/businesses
 * On suburb pages: filters businesses within the current suburb
 */

(function () {
    "use strict";

    const searchInput = document.getElementById("search-input");
    if (!searchInput) return;

    const isSuburbPage = searchInput.hasAttribute("data-suburb");
    let directoryData = null;

    // Determine JSON path based on page location
    const jsonPath = isSuburbPage ? "../data/directory.json" : "data/directory.json";

    // Load the directory data
    fetch(jsonPath)
        .then((res) => res.json())
        .then((data) => {
            directoryData = data;
        })
        .catch((err) => {
            console.warn("Could not load directory data for search:", err);
        });

    if (isSuburbPage) {
        setupSuburbSearch();
    } else {
        setupGlobalSearch();
    }

    // ============================================================
    // Global search (landing page) — dropdown results
    // ============================================================
    function setupGlobalSearch() {
        const resultsContainer = document.getElementById("search-results");
        if (!resultsContainer) return;

        let debounceTimer;

        searchInput.addEventListener("input", function () {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                const query = searchInput.value.trim().toLowerCase();
                if (query.length < 2 || !directoryData) {
                    resultsContainer.hidden = true;
                    return;
                }
                const results = searchGlobal(query);
                renderGlobalResults(results, resultsContainer);
            }, 200);
        });

        // Close results when clicking outside
        document.addEventListener("click", function (e) {
            if (!e.target.closest("#global-search")) {
                resultsContainer.hidden = true;
            }
        });

        // Re-show results on focus if there's a query
        searchInput.addEventListener("focus", function () {
            if (searchInput.value.trim().length >= 2 && resultsContainer.children.length > 0) {
                resultsContainer.hidden = false;
            }
        });
    }

    function searchGlobal(query) {
        const results = [];
        if (!directoryData || !directoryData.suburbs) return results;

        for (const suburb of directoryData.suburbs) {
            // Match suburb name
            if (suburb.name.toLowerCase().includes(query)) {
                results.push({
                    type: "suburb",
                    name: suburb.name,
                    state: suburb.state,
                    slug: suburb.slug,
                    url: `suburb/${suburb.slug}.html`,
                });
            }

            for (const [category, businesses] of Object.entries(suburb.categories || {})) {
                // Match category name
                if (category.toLowerCase().includes(query)) {
                    results.push({
                        type: "category",
                        name: category,
                        suburb: suburb.name,
                        slug: suburb.slug,
                        url: `suburb/${suburb.slug}.html`,
                    });
                }

                // Match business names
                for (const biz of businesses) {
                    if (biz.name.toLowerCase().includes(query)) {
                        results.push({
                            type: "business",
                            name: biz.name,
                            category: category,
                            suburb: suburb.name,
                            slug: suburb.slug,
                            url: `suburb/${suburb.slug}.html`,
                        });
                    }
                }
            }
        }

        // Deduplicate and limit
        return results.slice(0, 20);
    }

    function renderGlobalResults(results, container) {
        container.innerHTML = "";

        if (results.length === 0) {
            container.innerHTML = '<div class="search-result-item"><span class="result-name">No results found</span></div>';
            container.hidden = false;
            return;
        }

        for (const result of results) {
            const item = document.createElement("a");
            item.className = "search-result-item";
            item.href = result.url;

            let meta = "";
            if (result.type === "suburb") {
                meta = `Suburb · ${result.state}`;
            } else if (result.type === "category") {
                meta = `Category · ${result.suburb}`;
            } else {
                meta = `${result.category} · ${result.suburb}`;
            }

            item.innerHTML = `
                <div class="result-name">${escapeHtml(result.name)}</div>
                <div class="result-meta">${escapeHtml(meta)}</div>
            `;
            container.appendChild(item);
        }

        container.hidden = false;
    }

    // ============================================================
    // Suburb search — filter businesses on the page
    // ============================================================
    function setupSuburbSearch() {
        let debounceTimer;

        searchInput.addEventListener("input", function () {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                const query = searchInput.value.trim().toLowerCase();
                filterSuburbBusinesses(query);
            }, 150);
        });
    }

    function filterSuburbBusinesses(query) {
        const sections = document.querySelectorAll(".category-section");

        if (!query) {
            // Show everything
            sections.forEach((section) => {
                section.classList.remove("hidden");
                section.querySelectorAll(".business-card").forEach((card) => {
                    card.classList.remove("hidden");
                });
            });
            return;
        }

        sections.forEach((section) => {
            const categoryName = section.querySelector("h2")?.textContent?.toLowerCase() || "";
            const cards = section.querySelectorAll(".business-card");
            let visibleCount = 0;

            cards.forEach((card) => {
                const name = card.getAttribute("data-name") || "";
                const cat = card.getAttribute("data-category") || "";
                const address = card.querySelector(".detail span:last-child")?.textContent?.toLowerCase() || "";

                const matches =
                    name.includes(query) ||
                    cat.includes(query) ||
                    categoryName.includes(query) ||
                    address.includes(query);

                card.classList.toggle("hidden", !matches);
                if (matches) visibleCount++;
            });

            // Hide entire category section if no matches
            section.classList.toggle("hidden", visibleCount === 0);
        });
    }

    // ============================================================
    // Utilities
    // ============================================================
    function escapeHtml(str) {
        const div = document.createElement("div");
        div.textContent = str;
        return div.innerHTML;
    }
})();
