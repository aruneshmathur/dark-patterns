// Possible tags for add-to-cart buttons
let possibleTags = ["button", "input", "a", "add-to-cart-button"];

// Toggles debug print statement
let debugFlag = false;

// Debug print statement
let debug = function(msg) {
    if (debugFlag) {
        console.log(msg);
    }
};

// Gets an element given its string xpath
let getElementByXpath = function(path) {
    return document.evaluate(path, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
};

// Return the min of an array of numbers.
let min = function(a) {
    if (a.length == 0) {
        console.error("Array has no elements");
    }

    let m = a[0];
    for (let i = 0; i < a.length; i++) {
        if (a[i] < m) {
            m = a[i];
        }
    }
    return m;
};

// Return the max of an array of numbers.
let max = function(a) {
    if (a.length == 0) {
        console.error("Array has no elements");
    } else if (a.length == 1) {
        return 0;
    }

    let m = a[0];
    for (let i = 0; i < a.length; i++) {
        if (a[i] > m) {
            m = a[i];
        }
    }
    return m;
};

// Returns an array of the three rgb color values, given a string of the form
// "rgb(#, #, #)" or "rgba(#, #, #, #)".
let extractRgb = function(str) {
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
let anyAttributeMatches = function(elem, regex) {
    for (let i = 0; i < elem.attributes.length; i++) {
        if (elem.attributes[i].value.match(regex) != null) {
            return true;
        }
    }

    return false;
};

// Returns the absolute difference between this element's color and the page's
// background color.
let computeColorDist = function(elem) {
    let elemRgbStr = getBackgroundColor(elem);
    let body = document.getElementsByTagName("body");
    if (body.length == 0) {
        debug("No body tag, unable to determine background color");
        return 0;
    }
    body = body[0];
    let bodyRgbStr = getBackgroundColor(body);

    let elemRgb = extractRgb(elemRgbStr);
    let bodyRgb = extractRgb(bodyRgbStr);
    let dist = 0;
    for (let i = 0; i < 3; i++) {
        dist += (elemRgb[i] - bodyRgb[i]) * (elemRgb[i] - bodyRgb[i]);
    }
    dist = Math.sqrt(dist);
    return dist;
};

// Returns a value between 0 and 1 indicating how strongly the element matches
// the given regular expression.
let computeRegexScore = function(elem, regex) {
    let score = 0;
    if (elem.innerText.match(regex) != null){
        score += 5;
    }
    if (elem.href != undefined && elem.href.match(regex) != null) {
        score += 5;
    }
    if (elem.src != undefined && elem.src.match(regex) != null) {
        score += 5;
    }
    if (anyAttributeMatches(elem, regex)) {
        score += 4;
    }
    if (anyAttributeMatches(elem.parentElement, regex)) {
        score += 4;
    }
    let maxScore = 23;
    return score / maxScore;
};

// Weighs the features using the provided weights to produce a score for each
// candidate, and returns a new array of the candidates sorted by score (with
// highest score first): {element: <HTML element>, score: <number>}[]
//
// candidates should be an array of HTML elements; features should be a map
// from string feature names to {values: <array-of-numbers>, weight: <number>},
// so feature i of candidates[j] is in features[i].values[j]. thresh specifies
// the min score required for a candidate to be considered in the final output.
let weightCandidates = function(candidates, features, thresh) {
    // Normalize all features so min is 0 and max is 1
    Object.keys(features).forEach((i, _) => {
        let m = min(features[i].values);
        for (let j = 0; j < features[i].values.length; j++) {
            features[i].values[j] -= m;
        }
        let M = max(features[i].values);
        if (M != 0) {
            for (let j = 0; j < features[i].values.length; j++) {
                features[i].values[j] /= M;
            }
        }
    });

    // Compute weighted score for each candidate
    let scores = [];
    for (let j = 0; j < candidates.length; j++) {
        scores.push(0);
        Object.keys(features).forEach((i, _) => {
            scores[j] += features[i].weight * features[i].values[j];
        });
    }

    // Threshold scores
    let candidatesWithScores = [];
    for (let j = 0; j < candidates.length; j++) {
        if (scores[j] > thresh) {
            candidatesWithScores.push({element: candidates[j], score: scores[j]});
        }
    }

    // Sort by score, with highest score first
    candidatesWithScores.sort(function(x, y) {
        if (x.score > y.score) return -1;
        if (x.score < y.score) return 1;
        return 0;
    });

    return candidatesWithScores;
};

// Attempts to find an add-to-cart button on the page. Returns a list of
// possible buttons, sorted with the most likely button first, along with their
// scores (measure of likelihood). Or if no possible buttons are found, returns
// an empty list. Array returned is in the same format as the one returned by
// weightCandidates.
let getPossibleAddToCartButtons = function() {
    // candidates and fts are defined in the format accepted by weightCandidates.
    // Feature values are between 0 and 1 (higher is better), and weights sum to
    // 1, so resulting weighted scores are between 0 and 1.
    let regex = /(add[ -_]?\w*[ -_]?to[ -_]?(bag|cart|tote|basket|shop|trolley))|(buy[ -_]?(it)?[ -_]?now)|(shippingATCButton)/i; // variants of "add to cart"
    let candidates = [];
    let fts = {
        colorDists: {values: [], weight: 0.1}, // "distance" between this element's color and the background color
        regex: {values: [], weight: 0.6}, // indicator of whether text/attributes match the regex
        size: {values: [], weight: 0.3} // size of the element
    };

    // Select elements that could be buttons, and compute their raw scores
    for (let i = 0; i < possibleTags.length; i++) {
        let matches = Array.from(document.getElementsByTagName(possibleTags[i]));
        for (let j = 0; j < matches.length; j++) {
            let elem = matches[j];

            // Reject if doesn't meet the following conditions
            if (possibleTags[i] == "input" && (elem.type != "button" && elem.type != "submit" && elem.type != "image")) {
                continue;
            }

            if (elem.offsetParent == null) {
                continue;
            }

            candidates.push(elem);

            // Compute scores for each feature
            fts.colorDists.values.push(computeColorDist(elem));
            fts.regex.values.push(computeRegexScore(elem, regex));
            fts.size.values.push(elem.offsetWidth * elem.offsetHeight);
        }
    }

    if (candidates.length == 0) {
        return [];
    }

    let thresh = 0.5;
    return weightCandidates(candidates, fts, thresh);
};

// Returns the add-to-cart button on the page if one exists, or null if one
// doesn't.
let getAddToCartButton = function() {
    let candidates = getPossibleAddToCartButtons();
    if (candidates.length == 0) {
        return null;
    }
    return candidates[0].element;
};

let isProductPage = function() {
    let buttons = getPossibleAddToCartButtons();

    if (buttons.length === 0) {
        return false;
    } else if (buttons.length == 1) {
        return true;
    } else {
        if (buttons[0].element.innerText != buttons[1].element.innerText) {
            return true;
        } else if (buttons[0].score != buttons[1].score) {
            return true;
        } else {
            return false;
        }
    }
};

// Attempts to find a cart button on the page. Returns a list of possible
// buttons, sorted with the most likely button first, along with their scores
// (measure of likelihood). Or if no possible buttons are found, returns
// an empty list. Array returned is in the same format as the one returned by
// weightCandidates.
let getPossibleCartButtons = function() {
    // Returns boolean indicating whether elem is in the navbar/header bar.
    let isInNavbar = function(elem) {
        let regex = /header/i;
        let body = document.body;
        let e = elem.parentElement;
        while (e != body && e != null) {
            if (anyAttributeMatches(e, regex)) {
                return true;
            }
            e = e.parentElement;
        }
        return false;
    };

    // candidates and fts are defined in the format accepted by weightCandidates.
    // Feature values are between 0 and 1 (higher is better), and weights sum to
    // 1, so resulting weighted scores are between 0 and 1.
    let regex1 = /bag|cart|checkout|tote|basket|trolley/i;
    let regex2 = /(edit|view|shopping|addedto|my|go|mini)[ -_]?(\w[ -_]?)*(bag|cart|checkout|tote|basket|trolley)/i;
    let regex3 = /items[ -_]?(\w[ -_]?)*(in)?[ -_]?(\w[ -_]?)*(your)?(bag|cart|checkout|tote|basket|trolley)/i;
    let candidates = [];
    let fts = {
        negSize: {values: [], weight: 0.08}, // negative of size of the element
        inNavbar: {values: [], weight: 0.12}, // indicator of whether element is in navbar
        regex1: {values: [], weight: 0.12}, // indicators of whether text/attributes contain the regexs
        regex2: {values: [], weight: 0.17},
        regex3: {values: [], weight: 0.17},
        x: {values: [], weight: 0.17}, // x coordinate
        negY: {values: [], weight: 0.17} // negative of y coordinate
    };

    // Select elements that could be buttons, and compute their raw scores
    for (let i = 0; i < possibleTags.length; i++) {
        let matches = Array.from(document.getElementsByTagName(possibleTags[i]));
        for (let j = 0; j < matches.length; j++) {
            let elem = matches[j];

            if (possibleTags[i] == "input" && (elem.type != "button" && elem.type != "submit" && elem.type != "image")) {
                continue;
            }

            // Add candidate
            let rect = elem.getBoundingClientRect();
            candidates.push(elem);
            fts.negSize.values.push(-elem.offsetWidth * elem.offsetHeight);
            fts.inNavbar.values.push((isInNavbar(elem))? 1 : 0);
            fts.regex1.values.push(computeRegexScore(elem, regex1));
            fts.regex2.values.push(computeRegexScore(elem, regex2));
            fts.regex3.values.push(computeRegexScore(elem, regex3));
            fts.x.values.push(rect.x);
            fts.negY.values.push(-rect.y);
        }
    }

    if (candidates.length == 0) {
        return [];
    }

    // Weight/sort candidates
    let thresh = 0.5;
    return weightCandidates(candidates, fts, thresh);
};

// Returns the cart button if there is one, otherwise returns null.
let getCartButton = function() {
    let candidates = getPossibleCartButtons();
    if (candidates.length == 0) {
        return null;
    }
    return candidates[0].element;
};

// Attempts to find a checkout button on the page. Returns a list of possible
// buttons, sorted with the most likely button first, along with their scores
// (measure of likelihood). Or if no possible buttons are found, returns
// an empty list. Array returned is in the same format as the one returned by
// weightCandidates.
let getPossibleCheckoutButtons = function() {
    // candidates and fts are defined in the format accepted by weightCandidates.
    // Feature values are between 0 and 1 (higher is better), and weights sum to
    // 1, so resulting weighted scores are between 0 and 1.
    let regex = /(proceed|continue)[ -_]?(to)?[ -_]?(check[ -_]?out|pay)|check[ -_]?out/i;
    let candidates = [];
    let fts = {
        colorDists: {values: [], weight: 0.1}, // "distance" between this element's color and the background color
        regex: {values: [], weight: 0.7}, // indicator of whether text/attributes match the regex
        size: {values: [], weight: 0.2} // size of the element
    };

    // Select elements that could be buttons, and compute their raw scores
    for (let i = 0; i < possibleTags.length; i++) {
        let matches = Array.from(document.getElementsByTagName(possibleTags[i]));
        for (let j = 0; j < matches.length; j++) {
            let elem = matches[j];

            // Reject if doesn't meet the following conditions
            if (possibleTags[i] == "input" && (elem.type != "button" && elem.type != "submit" && elem.type != "image")) {
                continue;
            }

            if (elem.offsetParent == null) {
                continue;
            }

            candidates.push(elem);

            // Compute scores for each feature
            fts.colorDists.values.push(computeColorDist(elem));
            fts.regex.values.push(computeRegexScore(elem, regex));
            fts.size.values.push(elem.offsetWidth * elem.offsetHeight);
        }
    }

    if (candidates.length == 0) {
        return [];
    }

    let thresh = 0.5;
    return weightCandidates(candidates, fts, thresh);
};

// Returns the checkout button if one exists, or null if it doesn't.
let getCheckoutButton = function() {
    let candidates = getPossibleCheckoutButtons();
    if (candidates.length == 0) {
        return null;
    }
    return candidates[0].element;
};
