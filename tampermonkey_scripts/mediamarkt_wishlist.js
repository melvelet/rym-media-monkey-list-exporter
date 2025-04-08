// ==UserScript==
// @name         MediaMarkt Wishlist Shop Links
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  Improve the wishlist page for MediaMarkt
// @author       You
// @match        *://*.mediamarkt.de/de/myaccount/wishlist
// @match        *://*.saturn.de/de/myaccount/wishlist
// @grant        GM_addStyle
// ==/UserScript==

(function() {
    'use strict';

    // Add this at the beginning of your script
    GM_addStyle(`
        input[type="checkbox"] {
            all: revert !important;
            width: 16px !important;
            height: 16px !important;
            margin: 0 !important;
        }

        input[type="checkbox"] + label {
            all: revert !important;
            color: rgb(58, 58, 58) !important;
            font-size: 1rem !important;
            line-height: calc(1.5) !important;
            font-family: NotoSansDisplay, NotoSansDisplay-fallback, Arial, sans-serif !important;
            font-weight: 400 !important;
            margin: 0 !important;
            cursor: pointer !important;
        }
    `);

    // Add common text styles
    const commonStyles = {
        color: 'rgb(58, 58, 58)',
        fontSize: '1rem',
        lineHeight: 'calc(1.5)',
        fontFamily: 'NotoSansDisplay, NotoSansDisplay-fallback, Arial, sans-serif',
        fontWeight: '400'
    };

    // Settings state with filter functions
    const settings = {
        lieferung: {
            value: false,
            filterFn: item => !item.textContent.includes('Leider keine Lieferung möglich')
        },
        abholung: {
            value: false,
            filterFn: item => !item.textContent.includes('Leider keine Marktabholung möglich')
        },
        saturn: {
            value: false,
            filterFn: item => item.textContent.includes('Aktuell nur bei SATURN verfügbar')
        },
        sortPrice: {
            value: true  // Default enabled
        }
    };

    function parsePrice(priceText) {
        console.log(parseFloat(priceText.replace('€', '').replace(',', '.').trim()))
        return parseFloat(priceText.replace('€', '').replace(',', '.').trim());
    }

    function updateVisibility() {
        const firstItem = document.querySelector('[data-test="wishlist-item"]');
        if (!firstItem) return;

        const itemsContainer = firstItem.parentElement;
        const items = Array.from(document.querySelectorAll('[data-test="wishlist-item"]'));
        const saturnEnabled = settings.saturn.value;

        const lieferungCheckbox = document.getElementById('lieferung');
        const abholungCheckbox = document.getElementById('abholung');
        lieferungCheckbox.disabled = saturnEnabled;
        abholungCheckbox.disabled = saturnEnabled;

        let visibleCount = 0;
        let visibleItems = [];

        items.forEach(item => {
            let visible = true;
            if (saturnEnabled) {
                visible = settings.saturn.filterFn(item);
            } else {
                if (settings.lieferung.value) {
                    visible = visible && settings.lieferung.filterFn(item);
                }
                if (settings.abholung.value) {
                    visible = visible && settings.abholung.filterFn(item);
                }
            }

            item.style.display = visible ? '' : 'none';
            if (visible) {
                visibleCount++;
                visibleItems.push(item);
            }
        });

        // Sort visible items by price if enabled
        if (settings.sortPrice.value && visibleItems.length > 0) {
            visibleItems.sort((a, b) => {
                const priceA = parsePrice(a.querySelector('[data-test="cofr-price product-price"]').textContent);
                const priceB = parsePrice(b.querySelector('[data-test="cofr-price product-price"]').textContent);
                return priceA - priceB;
            });

            // Reorder DOM elements
            visibleItems.forEach(item => itemsContainer.appendChild(item));
        }

        // Update status text
        const status = document.querySelector('.loading-status');
        if (status) {
            const totalLoaded = getCurrentItems();
            status.textContent = `${totalLoaded} geladen/${visibleCount} gefiltert`;
        }
    }

    function createSettingsContainer() {
        const wishlistCount = document.querySelector('[data-test="wishlist-count"]');
        const container = document.createElement('div');
        Object.assign(container.style, {
            marginTop: '10px',
            display: 'flex',
            flexDirection: 'column',
            gap: '5px',
            ...commonStyles
        });

        const checkboxes = [
            { id: 'sortPrice', label: 'Nach Preis sortieren' },
            { id: 'lieferung', label: 'Lieferung möglich' },
            { id: 'abholung', label: 'Abholung möglich' },
            { id: 'saturn', label: 'Aktuell nur bei SATURN verfügbar' }
        ];

        checkboxes.forEach(({ id, label }) => {
            const wrapper = document.createElement('div');
            wrapper.style.display = 'flex';
            wrapper.style.alignItems = 'center';
            wrapper.style.gap = '8px';

            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.id = id;
            checkbox.checked = settings[id].value;
            checkbox.addEventListener('change', (e) => {
                settings[id].value = e.target.checked;
                updateVisibility();
            });

            const labelElement = document.createElement('label');
            labelElement.htmlFor = id;
            labelElement.textContent = label;
            Object.assign(labelElement.style, commonStyles);

            wrapper.appendChild(checkbox);
            wrapper.appendChild(labelElement);
            container.appendChild(wrapper);
        });

        wishlistCount.parentNode.insertBefore(container, wishlistCount.nextSibling);
    }

    // Modified waitForElements function
    function waitForElements() {
        return new Promise((resolve) => {
            const checkInterval = setInterval(() => {
                const wishlistCount = document.querySelector('[data-test="wishlist-count"]');
                if (wishlistCount) {
                    clearInterval(checkInterval);
                    createSettingsContainer();
                    resolve();
                }
            }, 500);
        });
    }

    // Rest of your existing functions...
    function getTotalItems() {
        const wishlistCount = document.querySelector('[data-test="wishlist-count"]');
        const match = wishlistCount.textContent.match(/(\d+)/);
        return match ? parseInt(match[1]) : 0;
    }

    function getCurrentItems() {
        return document.querySelectorAll('[data-test="wishlist-item"]').length;
    }

    function createStatusDisplay() {
        const wishlistCount = document.querySelector('[data-test="wishlist-count"]');
        const status = document.createElement('p');
        status.classList.add('loading-status');
        Object.assign(status.style, {
            margin: '0 10px 0 0',
            display: 'inline-block',
            ...commonStyles
        });
        wishlistCount.parentNode.insertBefore(status, wishlistCount);
        return status;
    }

    async function clickLoadMore() {
        const loadMoreButton = document.querySelector('[data-test="wishlist-loadMore"]');
        if (!loadMoreButton) return false;

        const currentCount = getCurrentItems();
        loadMoreButton.click();

        return new Promise((resolve) => {
            const checkInterval = setInterval(() => {
                const validationMessage = document.querySelector('[data-test="validationMessage"]');
                if (validationMessage) {
                    loadMoreButton.click();
                } else if (getCurrentItems() > currentCount) {
                    clearInterval(checkInterval);
                    resolve(true);
                }
            }, 500);
        });
    }

    async function loadAllItems() {
        const totalItems = getTotalItems();
        const status = createStatusDisplay();
        let isComplete = false;

        while (!isComplete) {
            const currentItems = getCurrentItems();
            const isLoading = currentItems < totalItems - 100;
            const loadingText = isLoading ? ' (weitere Artikel werden geladen)' : '';
            const visibleCount = document.querySelectorAll('[data-test="wishlist-item"]:not([style*="display: none"])').length;
            status.textContent = `${currentItems} geladen/${visibleCount} gefiltert${loadingText}`;

            if (currentItems >= totalItems - 100) {
                isComplete = true;
                continue;
            }

            const hasMore = await clickLoadMore();
            if (!hasMore) {
                isComplete = true;
            }

            await new Promise(resolve => setTimeout(resolve, 1000));
        }

        updateVisibility();
        console.log('All wishlist items loaded');
    }

    waitForElements().then(() => {
        loadAllItems();
    });
})();