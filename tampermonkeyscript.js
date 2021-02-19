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

//     GM_addStyle ( `
//     .copy_btn {display: inline-block;color: #55c;border: 1px #ddd solid;background: #f4f4f4;text-decoration: none;border-radius: 3px;padding: 2px;width: 80%;max-width: 140px; float: right;  opacity: 0;transition: opacity 100ms;}
// ` );

    // document.head.innerHTML += "<style type ='text/css'> .copy_btn {display: inline-block;color: #55c;border: 1px #ddd solid;background: #f4f4f4;text-decoration: none;border-radius: 3px;padding: 2px;width: 80%;max-width: 140px; float: right;  opacity: 0;transition: opacity 100ms;}</style>";
    var pri_genres, sec_genres, complete_string, area, releases;
    if(window.location.href.indexOf("/release/") > -1) {
        pri_genres = document.getElementsByClassName('release_pri_genres');
        sec_genres = document.getElementsByClassName('release_sec_genres');
    
        complete_string = createString(pri_genres, sec_genres);
    
        area = document.getElementsByClassName('release_pri_genres')[0].parentNode.parentNode;
        createButton(area, '', complete_string);
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
            createButton(element.getElementsByClassName("topcharts_textbox_bottom")[0], index, complete_string);
        }
    }

})();

function copyStringToClipboard (str) {
    // Create new element
    var el = document.createElement('textarea');
    // Set value (string to be copied)
    el.value = str;
    // Set non-editable to avoid focus and move outside of view
    el.setAttribute('readonly', '');
    el.style = {position: 'absolute', left: '-9999px'};
    document.body.appendChild(el);
    // Select text inside element
    el.select();
    // Copy text to clipboard
    document.execCommand('copy');
    // Remove temporary element
    document.body.removeChild(el);
 }

function createString(pri_genres, sec_genres) {
    if (pri_genres.length == 0) {
        pri_genres = '';
    } else {
        pri_genres = pri_genres[0].children;
    }
    if (sec_genres.length == 0) {
        sec_genres = '';
    } else {
            sec_genres = sec_genres[0].children;
    }
    var pri_string = '', sec_string = '';

    for (let index = 0; index < pri_genres.length; index++) {
        if (pri_string != '') {
            pri_string += '; ';
        }
        pri_string += getGenreStringFromElement(pri_genres[index]);
    }

    for (let index = 0; index < sec_genres.length; index++) {
        if (sec_string != '') {
            sec_string += '; ';
        }
        sec_string += getGenreStringFromElement(sec_genres[index]);
    }

    var complete_string = '' + pri_string;
    if (pri_string != '' && sec_string != '') {
        complete_string += '; ';
    }
    complete_string += sec_string;

    return complete_string;
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

function createButton(area, number, complete_string) {
    area.innerHTML += "<button class='copy_btn' id='pri_button" + number + "'>copy genres</button>";
    var pri_button = document.getElementById('pri_button' + number);
    pri_button.style.cssText = "color: #55c;border: 1px #ddd solid;background: #f4f4f4;text-decoration: none;border-radius: 3px;padding: 2px;width: 80%;max-width: 140px;";
    pri_button.addEventListener('click', function() {
        copyStringToClipboard(complete_string);
    });

}
