// ==UserScript==
// @name         RYM genre exporter
// @namespace    http://tampermonkey.net/
// @version      0.2
// @description  try to take over the world!
// @author       You
// @match        https://rateyourmusic.com/release/*
// @match        https://rateyourmusic.com/customchart*
// @match        https://rateyourmusic.com/charts/*
// @grant        none
// @require      https://ajax.googleapis.com/ajax/libs/jquery/3.4.0/jquery.min.js
// ==/UserScript==

(function() {
    'use strict';
    var pri_genres, sec_genres, complete_string, area, releases;
    if(window.location.href.indexOf("/release/") > -1) {
        pri_genres = document.getElementsByClassName('release_pri_genres');
        sec_genres = document.getElementsByClassName('release_sec_genres');

        complete_string = createString(pri_genres, sec_genres);

        area = document.getElementsByClassName('release_pri_genres')[0].parentNode.parentNode;
        createButton(area, '', complete_string, 25);

    } else if (window.location.href.indexOf("rateyourmusic.com/list/") > -1) {
        for (let oddeven = 0; oddeven < 2; oddeven++) {
            if (!oddeven) {
                releases = document.getElementsByClassName('treven');
            } else {
                releases = document.getElementsByClassName('trodd');
            }
            for (let index = 0; index < releases.length; index++) {
                const element = releases[index];
                pri_genres = element.children[2].children[2].children[0];
                sec_genres = element.children[2].children[2].children[1];

                complete_string = createString(pri_genres, sec_genres);
                createButton(element, index, complete_string);
            }
        }
    } else {
        releases = document.getElementsByClassName('chart_item_release');
        for (let index = 0; index < releases.length; index++) {
            const element = releases[index];
            pri_genres = element.getElementsByClassName("topcharts_item_genres_container");
            sec_genres = element.getElementsByClassName("topcharts_item_secondarygenres_container");

            complete_string = createString(pri_genres, sec_genres);
            createButton(element.getElementsByClassName("topcharts_textbox_bottom")[0], index, complete_string, 0);
        }
    }

})();

function copyStringToClipboard (str) {
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
    if (pri_genres.length > 0) {
        pri_genres = pri_genres[0].children;
    }
    if (sec_genres.length > 0) {
        sec_genres = sec_genres[0].children;
    }
    var genres = [];

    for (let index = 0; index < pri_genres.length; index++) {
        genres.push(getGenreStringFromElement(pri_genres[index]));
    }

    for (let index = 0; index < sec_genres.length; index++) {
        genres.push(getGenreStringFromElement(sec_genres[index]));
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
    area.innerHTML += "<button class='copy_btn' id='pri_button" + number + "' onclick=\"this.style.backgroundColor='green';this.style.border='1px green';\">copy genres</button>";
    var pri_button = document.getElementById('pri_button' + number);
    pri_button.style.cssText = "color: black;border: 1px var(--gen-blue-med) solid;background-color: var(--gen-blue-med);text-decoration: none;border-radius: 3px;padding: 2px;margin-left: " + margin + "px;max-width: 140px;";
    pri_button.addEventListener('click', function() {
        copyStringToClipboard(complete_string);
    });
}
