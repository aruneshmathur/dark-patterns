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

// Gets an element given its string xpath
var getElementByXpath = function(path) {
    return document.evaluate(path, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
};

// Returns an array of the three rgb color values, given a string of the form
// "rgb(#, #, #)" or "rgba(#, #, #, #)".
var extractRgb = function(str) {
    let matchesRgb = str.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);
    let matchesRgba = str.match(/^rgba\((\d+),\s*(\d+),\s*(\d+),\s*([0-9.]+)\)$/);
    let rgb;
    if (matchesRgb != null) {
        rgb = [parseInt(matchesRgb[1]), parseInt(matchesRgb[2]), parseInt(matchesRgb[3])];
    } else if (matchesRgba != null) {
        rgb = [parseInt(matchesRgba[1]), parseInt(matchesRgba[2]), parseInt(matchesRgba[3])];
    } else {
        console.error("Invalid rgb string: " + rgb);
    }
    return rgb;
};

// Returns true if any attribute of elem matches the regex.
var anyAttributeMatches = function(elem, regex) {
    for (let i = 0; i < elem.attributes.length; i++) {
        if (elem.attributes[i].value.match(regex) != null) {
            return true;
        }
    }
};

// Returns the absolute difference between this element's color and the page's
// background color (normalized so max distance is 1).
var computeBackgroundColorDistance = function(elem) {
    let elemRgbStr = window.getComputedStyle(elem).backgroundColor;
    let body = document.getElementsByTagName("body");
    if (body.length == 0) {
        debug("No body tag, unable to determine background color");
        return 0;
    }
    body = body[0];
    let bodyRgbStr = window.getComputedStyle(body).backgroundColor;

    let elemRgb = extractRgb(elemRgbStr);
    let bodyRgb = extractRgb(bodyRgbStr);
    let dist = 0;
    for (let i = 0; i < 3; i++) {
        dist += (elemRgb[i] - bodyRgb[i]) * (elemRgb[i] - bodyRgb[i]);
    }
    dist = Math.sqrt(dist) / Math.sqrt(3*255*255); // normalize so max is 1
    return dist;
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

    // Scores for each feature. The "score" field is out of 1, and the weight
    // is a multiplier for the score.
    let scores = {
        regex: {score: 0, weight: 3},
        colorDist: {score: 0, weight: 1}
    };

    // Text or any attribute contains a variant of "add to _"
    let regex = "[Aa][Dd][Dd][ ]{0,1}[Tt][Oo].*"; // variants of "add to cart"
    if (elem.textContent.match(regex) != null) {
        debug("isAddToCart: text matches regex");
        scores.regex.score = 1;
    } else if (anyAttributeMatches(elem, regex)) {
        debug("isAddToCart: attribute matches regex");
        scores.regex.score = 1;
    } else if (anyAttributeMatches(elem.parentElement, regex)) {
        debug("isAddToCart: parent element attribute matches regex");
        scores.regex.score = 1;
    } else if (elem["src"] != undefined && elem["src"].match(regex) != null) {
        debug("isAddToCart: img src matches regex");
        scores.regex.score = 1;
    }

    // Add the "distance" between this element's color and its surrounding
    // background color - the more different the colors, the higher the score
    scores.colorDist.score = computeBackgroundColorDistance(elem);

    // Compute total score
    let score = 0;
    Object.keys(scores).forEach((ft, _) => {
        score += scores[ft].weight * scores[ft].score;
    });
    return score;
};

// Attempts to find an add-to-cart button on the page. Returns a list of
// possible buttons, sorted with the most likely button first, or an empty list
// if no possible buttons are found.
var getPossibleAddToCartButtons = function() {
    let candidates = [];
    let scoreThresh = 1;

    // Select elements that could be buttons, and compute their scores
    possibleTags.forEach(tag => {
        let matches = document.getElementsByTagName(tag);
        for (let i = 0; i < matches.length; i++) {
            let elem = matches[i];
            let score = computeIndividualScore(elem);
            if (score > scoreThresh) {
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
        if (x.score < y.score) return 1;
        if (x.score > y.score) return -1;
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
