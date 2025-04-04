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

                let url = `https://www.booklooker.de/Musik/Angebote/artist=${formattedArtistName}&musicFormatCategory=${formatText}?sortOrder=preis_euro`;

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
            updateAllChartShopLinks();
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

            shopButton.addEventListener('mousedown', () => {
                e.preventDefault();
                window.open(shopUrl, '_blank');
            });

            buttonContainer.appendChild(shopButton);
        }

        const mediaLinkContainer = document.querySelector('.section_main_info');
        mediaLinkContainer.appendChild(buttonContainer);
    }

    // Function to generate shop links for chart items
   function generateChartShopLinks(item) {
       // Remove existing shop links first
       const existingButtons = item.querySelectorAll('.shop-button');
       existingButtons.forEach(button => button.remove());

       // Get the necessary elements with null checks
       const titleElement = item.querySelector('.page_charts_section_charts_item_link');
       const artistElement = item.querySelector('.page_charts_section_charts_item_credited_links_primary');
       const mediaLinksContainer = item.querySelector('.page_charts_section_charts_item_media_links');

       // Early return if required elements don't exist
       if (!titleElement || !artistElement || !mediaLinksContainer) {
           return;
       }

       const cleanReleaseTitle = titleElement.textContent.trim().toLowerCase();
       const cleanArtistName = artistElement.textContent
           .replace(/\s+/g, ' ')
           .replace(/\r?\n/g, '')
           .trim()
           .toLowerCase();

       // Create container for shop links
       const linksContainer = document.createElement('div');
       linksContainer.className = 'media_link_container';
       linksContainer.style.marginTop = '0.5em';
       linksContainer.style.display = 'flex';
       linksContainer.style.justifyContent = 'flex-end'; // Added to align content to the right

       // Add shop links based on title and artist
       const shopLinks = createShopLinks(cleanReleaseTitle, cleanArtistName);
       linksContainer.appendChild(shopLinks);

       // Insert links into the media links container
       mediaLinksContainer.appendChild(linksContainer);
   }

   function createShopLinks(title, artist) {
       const container = document.createElement('div');
       container.style.display = 'flex';
       container.style.flexDirection = 'row';
       container.style.gap = '5px';
       container.style.justifyContent = 'flex-end'; // Changed from flex-start to flex-end
       container.style.width = '100%'; // Added to ensure full width

       for (const [shopName, shop] of Object.entries(shopLinks)) {
           const shopButton = document.createElement('button');
           shopButton.classList.add('shop-button');
           shopButton.style.color = 'black';
           shopButton.style.border = '1px solid var(--gen-blue-med)';
           shopButton.style.backgroundColor = '#d3d3d3';
           shopButton.style.textDecoration = 'none';
           shopButton.style.borderRadius = '3px';
           shopButton.style.padding = '2px 6px';
           shopButton.style.fontSize = '0.8em';
           shopButton.style.whiteSpace = 'nowrap';
           shopButton.textContent = shopName;

           const shopUrl = shop.linkBuilder(title, artist, format, releaseSetting);

           shopButton.addEventListener('mousedown', (e) => {
               e.preventDefault();
               window.open(shopUrl, '_blank');
           });

           container.appendChild(shopButton);
       }

       return container;
   }

    function observePageChanges() {
        const chartsContainer = document.querySelector('#page_charts_section_charts');
        if (!chartsContainer) return;

        // Create and setup the observer here instead of globally
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.classList?.contains('page_charts_section_charts_item')) {
                        generateChartShopLinks(node);
                    }
                });
            });
        });

        // Start observing
        observer.observe(chartsContainer, {
            childList: true,
            subtree: false
        });

        // Setup the update observer
        const updateObserver = new MutationObserver((mutations) => {
            const shouldUpdate = mutations.some(mutation =>
                mutation.type === 'childList' &&
                (mutation.addedNodes.length > 0 || mutation.removedNodes.length > 0)
            );

            if (shouldUpdate) {
                debouncedUpdate();
            }
        });

        updateObserver.observe(chartsContainer, {
            childList: true,
            subtree: false
        });
    }

    // Add this near the top of your IIFE, after your initial variable declarations
    const DEBOUNCE_DELAY = 250; // milliseconds

    // Debounce helper function
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Function to update shop links for all chart items
    function updateAllChartShopLinks() {
        // Remove only shop buttons
        const existingButtons = document.querySelectorAll('.shop-button');
        existingButtons.forEach(button => button.remove());

        // Add new shop links
        const chartItems = document.querySelectorAll('.page_charts_section_charts_item');
        chartItems.forEach(item => generateChartShopLinks(item));
    }

    // Debounced version of the update function
    const debouncedUpdate = debounce(() => {
        if (window.location.pathname.includes('/charts/')) {
            updateAllChartShopLinks();
        } else if (window.location.pathname.includes('/release/')) {
            generateReleaseShopLinks(format, releaseSetting);
        }
    }, DEBOUNCE_DELAY);

    // Initialize
    updateButtonStyles();
    debouncedUpdate();
    observePageChanges();

    // Handle navigation
    window.addEventListener('popstate', () => {
        setTimeout(debouncedUpdate, 500);
    });
})();
