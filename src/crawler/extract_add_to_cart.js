// Possible tags for add-to-cart buttons
const possibleTags = ["button", "input", "a"];

// Returns true if any attribute of elem matches the regex.
var anyAttributeMatches = function(elem, regex) {
    for (let i = 0; i < elem.attributes.length; i++) {
        if (elem.attributes[i].value.match(regex) != null) {
            return true;
        }
    }
};

// Returns true if an element is likely to be an add-to-cart button.
var isAddToCartButton = function(elem) {
    // Try various heuristics for identifying the add-to-cart button

    // Is one of the commonly used tags for add-to-cart buttons
    if (!possibleTags.includes(elem.tagName.toLowerCase())) {
        return false;
    }

    // Hidden/disabled
    if (elem.disabled || elem.offsetParent == null) {
        return false;
    }

    let regex = "[Aa][Dd][Dd].*[Tt][Oo].*"; // variants of "add to cart"

    // Text says a variant of "add to _"
    if (elem.textContent.match(regex) != null) {
        return true;
    }

    // Any attribute contains a variant of "add to _"
    if (anyAttributeMatches(elem, regex)) {
        return true;
    }

    // Parent div/elem has attribute that contains a variant of "add to _"
    if (anyAttributeMatches(elem.parentElement, regex)) {
        return true;
    }

    // For images, check if src contains a variant of "add to _"
    imgSrc = "src";
    if (elem[imgSrc] != undefined) {
        if (elem[imgSrc].match(regex) != null) {
            return true;
        }
    }
};

// Attempts to find an add-to-cart button on the page. Returns an array of
// these buttons if it finds any, or an empty array if it doesn't.
var getAddToCartButton = function() {
    let candidates = [];

    // Filter elements that could be buttons
    possibleTags.forEach(tag => {
        matches = document.getElementsByTagName(tag);
        for (let i = 0; i < matches.length; i++) {
            candidates.push(matches[i]);
        }
    });

    let results = [];
    candidates.forEach(elem => {
        if (isAddToCartButton(elem)) {
            results.push(elem);
        }
    });

    return results;
};
