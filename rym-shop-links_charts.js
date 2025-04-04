// ==UserScript==
// @name         Shop Link Buttons for Release Pages and Charts Pages
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  Add buttons for shop links on release and charts pages with separate settings for format and Band/Release
// @author       You
// @match        *://*.rateyourmusic.com/release/*
// @match        *://*.rateyourmusic.com/charts/*
// @grant        GM_addStyle
// ==/UserScript==

(function() {
    // Function to save settings to cookies
    function saveSettings(format, releaseSetting) {
        const settings = { format, releaseSetting };
        const settingsString = JSON.stringify(settings);
        const expiryDate = new Date();
        expiryDate.setFullYear(expiryDate.getFullYear() + 1); // Expire in 1 year
        document.cookie = `shopSettings=${encodeURIComponent(settingsString)}; expires=${expiryDate.toUTCString()}; path=/`;
    }

    // Function to load settings from cookies
    function loadSettings() {
        const cookieName = "shopSettings=";
        const decodedCookie = decodeURIComponent(document.cookie);
        const cookieArray = decodedCookie.split(';');

        for (let i = 0; i < cookieArray.length; i++) {
            let cookie = cookieArray[i].trim();
            if (cookie.indexOf(cookieName) === 0) {
                const settingsString = cookie.substring(cookieName.length);
                return JSON.parse(settingsString);
            }
        }

        // Return default settings if no cookie is found
        return { format: "general", releaseSetting: "release" };
    }

    // Load settings from cookies on page load
    let { format, releaseSetting } = loadSettings();

    // Function to update the active setting button styles
    function updateButtonStyles() {
        // Reset all buttons' styles
        const allButtons = document.querySelectorAll('.settings-panel button');
        allButtons.forEach(button => {
            button.style.color = 'black';
            button.style.border = '1px solid var(--gen-blue-med)';
            button.style.backgroundColor = 'rgba(0, 0, 0, 0.1)';
            button.style.textDecoration = 'none';
            button.style.borderRadius = '3px';
            button.style.padding = '2px';
            button.style.marginLeft = '25px';
            button.style.maxWidth = '160px';
            button.style.fontSize = '0.8em';
        });

        // Highlight the active format button
        if (format === 'cd') {
            cdButton.style.backgroundColor = 'var(--gen-blue-med)';
        } else if (format === 'vinyl') {
            vinylButton.style.backgroundColor = 'var(--gen-blue-med)';
        } else if (format === 'cassette') {
            cassetteButton.style.backgroundColor = 'var(--gen-blue-med)';
        } else {
            generalButton.style.backgroundColor = 'var(--gen-blue-med)';
        }

        // Highlight the active release setting button
        if (releaseSetting === 'band') {
            bandButton.style.backgroundColor = 'var(--gen-blue-med)';
        } else {
            releaseButton.style.backgroundColor = 'var(--gen-blue-med)';
        }
    }

    // Create the fixed settings panel in the top-left corner
    const settingsPanel = document.createElement('div');
    settingsPanel.classList.add('settings-panel');
    settingsPanel.style.position = 'fixed';
    settingsPanel.style.top = '10px';
    settingsPanel.style.left = '10px';
    settingsPanel.style.zIndex = '1000';
    settingsPanel.style.backgroundColor = 'rgba(255, 255, 255, 0.8)';
    settingsPanel.style.border = '1px solid #ccc';
    settingsPanel.style.padding = '10px';
    settingsPanel.style.borderRadius = '5px';

    // Create buttons for format selection (CD, Vinyl, Cassette, General)
    const cdButton = document.createElement('button');
    cdButton.textContent = 'CD';
    cdButton.style.marginRight = '5px';
    cdButton.addEventListener('click', () => setFormat('cd'));

    const vinylButton = document.createElement('button');
    vinylButton.textContent = 'Vinyl';
    vinylButton.style.marginRight = '5px';
    vinylButton.addEventListener('click', () => setFormat('vinyl'));

    const generalButton = document.createElement('button');
    generalButton.textContent = 'General';
    generalButton.style.marginRight = '5px';
    generalButton.addEventListener('click', () => setFormat('general'));

    const cassetteButton = document.createElement('button');
    cassetteButton.textContent = "Cassette";
    cassetteButton.style.marginRight = '5px';
    cassetteButton.addEventListener('click', () => setFormat('cassette'));

    // Append to settingsPanel (first line)
    const settingLine1 = document.createElement('div');
    settingLine1.appendChild(cdButton);
    settingLine1.appendChild(vinylButton);
    settingLine1.appendChild(cassetteButton);
    settingLine1.appendChild(generalButton);

    // Create buttons for release setting selection (Band, Release)
    const bandButton = document.createElement('button');
    bandButton.textContent = 'Band';
    bandButton.style.marginRight = '5px';
    bandButton.addEventListener('click', () => setReleaseSetting('band'));

    const releaseButton = document.createElement('button');
    releaseButton.textContent = 'Release';
    releaseButton.style.marginRight = '5px';
    releaseButton.addEventListener('click', () => setReleaseSetting('release'));

    // Append to settingsPanel (second line)
    const settingLine2 = document.createElement('div');
    settingLine2.appendChild(bandButton);
    settingLine2.appendChild(releaseButton);

    // Add the settings panel to the page
    settingsPanel.appendChild(settingLine1);
    settingsPanel.appendChild(settingLine2);
    document.body.appendChild(settingsPanel);

    // Function to update the shop links based on the current settings
    function setFormat(setting) {
        format = setting;
        saveSettings(format, releaseSetting); // Save settings to cookies
        updateButtonStyles();
        updateShopLinks();
    }

    function setReleaseSetting(setting) {
        releaseSetting = setting;
        saveSettings(format, releaseSetting); // Save settings to cookies
        updateButtonStyles();
        updateShopLinks();
    }

    // Shop link builder functions (e.g., for Amazon, Booklooker, etc.)
    const shopLinks = {
        "Amazon": {
            linkBuilder: (releaseTitle, artistName, format, releaseSetting) => {
                const formattedReleaseTitle = releaseTitle.trim().toLowerCase();
                const formattedArtistName = artistName.trim().toLowerCase();

                let url = `https://www.amazon.de/s?k=${formattedArtistName}+${formattedReleaseTitle}&rh=n%3A255882`;

                if (format === "cd") {
                    url += `%2Cp_n_binding_browse-bin%3A379146011`;  // CD format
                } else if (format === "vinyl") {
                    url += `%2Cp_n_binding_browse-bin%3A379151011`;  // Vinyl format
                } else if (format === "cassette") {
                    url += `%2Cp_n_binding_browse-bin%3A379147011`;  // Cassette format
                }

                if (format !== "general") {
                    url += `&sprefix=${formattedReleaseTitle}`;
                }

                return url;
            }
        },
        "Booklooker": {
            linkBuilder: (releaseTitle, artistName, format, releaseSetting) => {
                let formatText = "";
                if (format !== "general") {
                    if (format === "cassette") {
                        formatText = "MC";  // Booklooker requires MC for cassette
                    } else if (format === "cd") {
                        formatText = "CD";  // Booklooker uses uppercase CD for CD format
                    } else {
                        formatText = capitalize(format);
                    }
                }

                const formattedReleaseTitle = releaseTitle.trim().toLowerCase();
                const formattedArtistName = artistName.trim().toLowerCase();

                let url = `https://www.booklooker.de/Musik/Angebote/artist=${formattedArtistName}&musicFormatCategory=${formatText}`;

                // Add title only if release setting is "release" (not "band")
                if (releaseSetting === "release") {
                    url += `&titel=${formattedReleaseTitle}`;
                }

                return url;
            }
        },
        // Additional shop link builders...
    };

    function capitalize(str) {
        if (typeof str !== "string") return str;
        return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
    }

    function updateShopLinks() {
        if (window.location.pathname.includes('/charts/')) {
            generateChartShopLinks(format, releaseSetting);
        } else {
            generateReleaseShopLinks(format, releaseSetting);
        }
    }

    // Generate shop links for /release/ pages
    function generateReleaseShopLinks(format, releaseSetting) {
        // Remove any existing shop buttons
        const existingButtons = document.querySelectorAll('.shop-button');
        existingButtons.forEach(button => button.remove());

        const releaseTitleElement = document.querySelector('.album_title');
        const artistNameElement = document.querySelector('.album_artist_small a');

        if (!releaseTitleElement || !artistNameElement) return;

        const releaseTitle = releaseTitleElement.textContent.trim();
        const artistName = artistNameElement.textContent.trim();

        const cleanReleaseTitle = releaseTitle.split('\n')[0].trim().toLowerCase();
        const cleanArtistName = artistName.toLowerCase();

        const buttonContainer = document.createElement('div');
        buttonContainer.classList.add('shop-buttons-container');
        buttonContainer.style.position = 'absolute';
        buttonContainer.style.top = '10px';
        buttonContainer.style.left = '10px';
        buttonContainer.style.zIndex = '999';
        buttonContainer.style.display = 'flex';
        buttonContainer.style.flexDirection = 'row';
        buttonContainer.style.flexWrap = 'wrap';

        for (const [shopName, shop] of Object.entries(shopLinks)) {
            const shopButton = document.createElement('button');
            shopButton.classList.add('shop-button'); // Assign a common class
            shopButton.style.marginRight = '5px';
            shopButton.style.color = 'black';
            shopButton.style.border = '1px solid var(--gen-blue-med)';
            shopButton.style.backgroundColor = '#d3d3d3';
            shopButton.style.textDecoration = 'none';
            shopButton.style.borderRadius = '3px';
            shopButton.style.padding = '2px';
            shopButton.style.marginLeft = '25px';
            shopButton.style.maxWidth = '160px';
            shopButton.style.fontSize = '0.8em';
            shopButton.textContent = shopName;

            const shopUrl = shop.linkBuilder(cleanReleaseTitle, cleanArtistName, format, releaseSetting);

            shopButton.addEventListener('click', () => {
                window.open(shopUrl, '_blank');
            });

            buttonContainer.appendChild(shopButton);
        }

        const mediaLinkContainer = document.querySelector('.section_main_info');
        mediaLinkContainer.appendChild(buttonContainer);
    }

    // Generate shop links for /charts/ pages
    function generateChartShopLinks(format, releaseSetting) {
        // Remove any existing shop buttons
        const existingButtons = document.querySelectorAll('.shop-button');
        existingButtons.forEach(button => button.remove());

        const chartEntries = document.querySelectorAll('.page_charts_section_charts_item');

        chartEntries.forEach(entry => {
            const releaseLink = entry.querySelector('.page_charts_section_charts_item_link.release');
            const artistLink = entry.querySelector('.page_charts_section_charts_item_credited_links_primary .artist');

            if (!releaseLink || !artistLink) return;

            const releaseTitle = releaseLink.textContent.trim();
            const artistName = artistLink.textContent.trim();

            const cleanReleaseTitle = releaseTitle.split('\n')[0].trim().toLowerCase();
            const cleanArtistName = artistName.toLowerCase();

            const buttonContainer = document.createElement('div');
            buttonContainer.classList.add('shop-buttons-container');
            buttonContainer.style.display = 'flex';
            buttonContainer.style.gap = '10px';

            for (const [shopName, shop] of Object.entries(shopLinks)) {
                const shopButton = document.createElement('button');
                shopButton.classList.add('shop-button'); // Assign a common class
                shopButton.textContent = shopName;
                shopButton.style.color = 'black';
                shopButton.style.border = '1px solid var(--gen-blue-med)';
                shopButton.style.backgroundColor = '#d3d3d3';
                shopButton.style.textDecoration = 'none';
                shopButton.style.borderRadius = '3px';
                shopButton.style.padding = '2px';
                shopButton.style.fontSize = '0.8em';

                const shopUrl = shop.linkBuilder(cleanReleaseTitle, cleanArtistName, format, releaseSetting);

                shopButton.addEventListener('click', () => {
                    window.open(shopUrl, '_blank');
                });

                buttonContainer.appendChild(shopButton);
            }

            const mediaLinkContainer = entry.querySelector('.page_charts_section_charts_item_stats_media');
            mediaLinkContainer.appendChild(buttonContainer);
        });
    }

    updateButtonStyles();
    updateShopLinks();

    function observePageChanges() {
        const paginationLinks = document.querySelectorAll('.ui_pagination_btn.ui_pagination_number');

        paginationLinks.forEach(link => {
            link.addEventListener('click', (event) => {
                event.preventDefault();  // Prevent the default link behavior (full reload)

                // Trigger page change (simulate click)
                const href = link.getAttribute('href');
                if (href) {
                    window.history.pushState({}, '', href);  // Update the URL without full reload
                    // Wait for the page to finish loading the new content
                    setTimeout(() => {
                        // Regenerate buttons on new page
                        updateShopLinks();
                    }, 2000);  // Wait 1 second for page content to be loaded (you can adjust the delay)
                }
            });
        });
    }

    // Initially, when the page is loaded, call observePageChanges to track pagination links
    observePageChanges();

    // Monitor page changes dynamically (in case of further page navigation within the same session)
    window.addEventListener('popstate', () => {
        setTimeout(() => {
            updateShopLinks();  // Regenerate shop links when navigating back/forward in history
        }, 1000);  // Wait a bit for content to load (adjust if needed)
    });
})();
