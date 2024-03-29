// ==UserScript==
// @name         RYM genre exporter
// @namespace    http://tampermonkey.net/
// @version      0.2
// @description  try to take over the world!
// @author       You
// @match        https://rateyourmusic.com/release/*
// @match        https://rateyourmusic.com/list/*
// @match        https://rateyourmusic.com/charts/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';
    var pri_genres, sec_genres, complete_string, area, releases;
    if (window.location.href.indexOf("/release/") > -1) {
        pri_genres = document.getElementsByClassName('release_pri_genres')[0];
        sec_genres = document.getElementsByClassName('release_sec_genres')[0];

        complete_string = createString(pri_genres, sec_genres);

        area = document.getElementsByClassName('release_pri_genres')[0].parentNode.parentNode;
        createButton(area, '', complete_string, 25);

    } else if (window.location.href.indexOf("/list/") > -1) {
        releases = document.getElementsByClassName('extra_metadata_genres');
        for (let index = 0; index < releases.length; index++) {
            pri_genres = releases[index];
            sec_genres = pri_genres.parentNode.children[1];

            complete_string = createString(pri_genres, sec_genres);
            createButton(pri_genres, index, complete_string, 25);
        }
    } else {
        releases = document.getElementsByClassName('page_charts_section_charts_item object_release');
        for (let index = 0; index < releases.length; index++) {
            const element = releases[index];
            pri_genres = element.getElementsByClassName("page_charts_section_charts_item_genres_primary")[0];
            sec_genres = element.getElementsByClassName("page_charts_section_charts_item_genres_secondary")[0];

            complete_string = createString(pri_genres, sec_genres);
            createButton(element.getElementsByClassName("page_charts_section_charts_item_media_links")[0], index, complete_string, 0);
        }
    }
})();

function copyStringToClipboard(str) {
    var el = document.createElement('textarea');
    el.value = str;
    el.setAttribute('readonly', '');
    el.style = {position: 'absolute', left: '-9999px'};
    document.body.appendChild(el);
    el.select();
    document.execCommand('copy');
    document.body.removeChild(el);
}

function createString(pri_genres, sec_genres) {
    var genres = [];

    if (pri_genres) {
      for (let index = 0; index < pri_genres.children.length; index++) {
          genres.push(getGenreStringFromElement(pri_genres.children[index]));
      }
    }

    if (sec_genres) {
      for (let index = 0; index < sec_genres.children.length; index++) {
          genres.push(getGenreStringFromElement(sec_genres.children[index]));
      }
    }

    return genres.join('; ');
}

function getGenreStringFromElement(element) {
    var result;
    if (element.innerHTML.startsWith("<a")) {
      result = element.innerText;
    } else {
      result = element.innerHTML;
    }
    return result.replace("&amp;", "&").replace(", ", "");
}

function createButton(area, number, complete_string, margin) {
    area.innerHTML += "<button class='copy_btn' id='pri_button" + number + "'>copy genres</button>";
    var pri_button = document.getElementById('pri_button' + number);
    pri_button.style.cssText = "color: black;border: 1px var(--gen-blue-med) solid;background-color: var(--gen-blue-med);text-decoration: none;border-radius: 3px;padding: 2px;margin-left: " + margin + "px;max-width: 140px;";
    pri_button.addEventListener('click', function() {
      copyStringToClipboard(complete_string);
      this.style.backgroundColor='green';
      this.style.border='1px green solid';
    });
}
