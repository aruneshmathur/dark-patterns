// Possible tags for add-to-cart buttons
let possibleTags = ["button", "input", "a"];

// Toggles debug print statement
let debugFlag = false;

// Debug print statement
var debug = function(msg) {
    if (debugFlag) {
        console.log(msg);
    }
};

// Returns true if any attribute of elem matches the regex.
var anyAttributeMatches = function(elem, regex) {
    for (let i = 0; i < elem.attributes.length; i++) {
        if (elem.attributes[i].value.match(regex) != null) {
            return true;
        }
    }
};

// Runs various heuristics for identifying the add-to-cart button on the given
// element, and returns its individual score toward being the button. Min 0,
// which indicates that it's not an add-to-cart button, and higher score is
// better.
var computeIndividualScore = function(elem) {
    let tag = elem.tagName.toLowerCase();

    // Is one of the commonly used tags for add-to-cart buttons
    if (!possibleTags.includes(tag)) {
        debug("isAddToCart: returning 0: not one of the possible tags");
        return 0;
    }

    // "input" tag is of type "button"
    if (tag == "input" && elem.type != "button") {
        debug("isAddToCart: returning 0: input tag is not of type \"button\"");
        return 0;
    }

    // Hidden/disabled
    if (elem.disabled || elem.offsetParent == null) {
        debug("isAddToCart: returning 0: element is disabled");
        return 0;
    }

    let regex = "[Aa][Dd][Dd][ ]{0,1}[Tt][Oo].*"; // variants of "add to cart"
    let score = 0;

    // Text says a variant of "add to _"
    if (elem.textContent.match(regex) != null) {
        debug("isAddToCart: text matches regex");
        score += 1;
    }

    // Any attribute contains a variant of "add to _"
    if (anyAttributeMatches(elem, regex)) {
        debug("isAddToCart: attribute matches regex");
        score += 1;
    }

    // Parent div/elem has attribute that contains a variant of "add to _"
    if (anyAttributeMatches(elem.parentElement, regex)) {
        debug("isAddToCart: parent element attribute matches regex");
        score += 1;
    }

    // For images, check if src contains a variant of "add to _"
    imgSrc = "src";
    if (elem[imgSrc] != undefined) {
        if (elem[imgSrc].match(regex) != null) {
            debug("isAddToCart: img src matches regex");
            score += 1;
        }
    }

    return score;
};

// Attempts to find an add-to-cart button on the page. Returns a list of
// possible buttons, sorted with the most likely button first, or an empty list
// if no possible buttons are found.
var getPossibleAddToCartButtons = function() {
    let candidates = [];

    // Select elements that could be buttons, and compute their scores
    possibleTags.forEach(tag => {
        let matches = document.getElementsByTagName(tag);
        for (let i = 0; i < matches.length; i++) {
            let elem = matches[i];
            let score = computeIndividualScore(elem);
            if (score > 0) {
                candidates.push({
                    element: elem,
                    score: score
                });
            }
        }
    });

    // Sort by score
    // Return top element with a score above 0, if there is one
    candidates.sort(function(x, y) {
        if (x.score < y.score) return -1;
        if (x.score > y.score) return 1;
        return 0;
    });

    // Return elements
    let results = [];
    for (let i = 0; i < candidates.length; i++) {
        results.push(candidates[i].element);
    }
    return results;
};

// Returns the add-to-cart button on the page if one exists, or null if one
// doesn't.
var getAddToCartButton = function() {
    candidates = getPossibleAddToCartButtons();
    if (candidates.length == 0) {
        return null;
    }
    return candidates[0];
};
