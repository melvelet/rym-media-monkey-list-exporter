// ==UserScript==
// @name         RYM genre + descriptor exporter (all pages)
// @namespace    http://tampermonkey.net/
// @version      0.3
// @description  Export genres, scenes, and descriptors from RYM (release, list, charts pages)
// @author       You
// @match        https://rateyourmusic.com/release/*
// @match        https://rateyourmusic.com/list/*
// @match        https://rateyourmusic.com/charts/*
// @grant        none
// ==/UserScript==

(function () {
    'use strict';

    // -------- RELEASE PAGE --------
    if (window.location.href.includes("/release/")) {
        const primaryGenres = document.querySelector('.release_pri_genres');
        const secondaryGenres = document.querySelector('.release_sec_genres');
        const sceneSpan = findSceneSpan();
        const descriptorSpan = document.querySelector('.release_pri_descriptors');

        const genreSceneString = createString(primaryGenres, secondaryGenres, sceneSpan);
        const descriptorString = createDescriptorString(descriptorSpan);

        if (primaryGenres) {
            const genreArea = primaryGenres.closest('td');
            createButton(genreArea, 'genre_btn', genreSceneString, 25, 'copy genres + scenes');
        }

        if (descriptorSpan) {
            const descriptorArea = descriptorSpan.closest('td');
            createButton(descriptorArea, 'desc_btn', descriptorString, 25, 'copy descriptors');
        }

    // -------- LIST PAGE --------
    } else if (window.location.href.includes("/list/")) {
        const listEntries = document.querySelectorAll('.main_entry');
        listEntries.forEach((entry, index) => {
            const genres = entry.querySelector('.extra_metadata_genres');
            const secondaryGenres = entry.querySelector('.extra_metadata_sec_genres');
            const descriptors = entry.querySelector('.extra_metadata_descriptors');

            const genreString = createString(genres, secondaryGenres, null);
            const descriptorString = descriptors ? descriptors.textContent.trim() : '';

            const buttonContainer = document.createElement('div');
            buttonContainer.style.display = 'flex';
            buttonContainer.style.gap = '10px';
            buttonContainer.style.marginTop = '10px';

            if (genreString.length > 0) {
                createButton(buttonContainer, `list_genres_btn_${index}`, genreString, 0, 'copy genres');
            }

            if (descriptorString.length > 0) {
                createButton(buttonContainer, `list_desc_btn_${index}`, descriptorString, 0, 'copy descriptors');
            }

            entry.appendChild(buttonContainer);
        });

    // -------- CHARTS PAGE --------
    } else if (window.location.href.includes("/charts/")) {
        const chartReleases = document.querySelectorAll('.page_charts_section_charts_item_info');
        chartReleases.forEach((release, index) => {
            const primaryGenres = release.querySelector('.page_charts_section_charts_item_genres_primary');
            const secondaryGenres = release.querySelector('.page_charts_section_charts_item_genres_secondary');
            const descriptors = release.querySelector('.page_charts_section_charts_item_genre_descriptors');
            const target = release.querySelector('.page_charts_section_charts_item_media_links');

            const genreString = createString(primaryGenres, secondaryGenres, null);
            const descriptorString = descriptors ? Array.from(descriptors.children).map(e => e.textContent.trim()).join('; ') : '';

            if (target) {
                const buttonContainer = document.createElement('div');
                buttonContainer.style.display = 'flex';
                buttonContainer.style.gap = '10px';

                if (genreString.length > 0) {
                    createButton(buttonContainer, `chart_genres_btn_${index}`, genreString, 0, 'copy genres');
                }

                if (descriptorString.length > 0) {
                    createButton(buttonContainer, `chart_desc_btn_${index}`, descriptorString, 0, 'copy descriptors');
                }

                target.appendChild(buttonContainer);
            }
        });
    }




    // -------- HELPERS --------
    function createString(pri, sec, scenes) {
        const all = [];
        [pri, sec, scenes].forEach(group => {
            if (group) {
                for (let i = 0; i < group.children.length; i++) {
                    all.push(cleanText(group.children[i]));
                }
            }
        });
        return all.join('; ');
    }

    function createDescriptorString(descSpan) {
        const descriptors = [];
        if (descSpan) {
            descSpan.innerText.split(',').forEach(d => {
                const trimmed = d.trim();
                if (trimmed.length > 0) descriptors.push(trimmed);
            });
        }
        return descriptors.join('; ');
    }

    function cleanText(el) {
        return el.innerText.replace("&amp;", "&").replace(", ", "");
    }

    function createButton(area, id, text, margin, label) {
        const button = document.createElement('button');
        button.className = 'copy_btn';
        button.id = id;
        button.textContent = label;
        button.style.cssText = `color: black;border: 1px var(--gen-blue-med) solid;background-color: var(--gen-blue-med);text-decoration: none;border-radius: 3px;padding: 2px;margin-left: ${margin}px;max-width: 160px;font-size: 0.8em;`;
        button.addEventListener('click', function () {
            copyToClipboard(text);
            this.style.backgroundColor = 'green';
            this.style.border = '1px solid green';
        });
        area.appendChild(button);
    }

    function copyToClipboard(str) {
        const el = document.createElement('textarea');
        el.value = str;
        el.setAttribute('readonly', '');
        el.style.position = 'absolute';
        el.style.left = '-9999px';
        document.body.appendChild(el);
        el.select();
        document.execCommand('copy');
        document.body.removeChild(el);
    }

    function findSceneSpan() {
        const genreRows = document.querySelectorAll('tr.release_genres');
        for (let row of genreRows) {
            const th = row.querySelector('th');
            if (th && th.textContent.trim().toLowerCase() === 'scenes') {
                return row.querySelector('.release_pri_genres');
            }
        }
        return null;
    }
})();
