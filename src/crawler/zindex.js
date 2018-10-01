/* This file is used to locate the div element of a web page that might contain
close buttons to dismiss a modal dialog */

// Given a list of elements, find one that has the largest z-index
var maxZindex = function(element_list) {
    var max = -99999999;
    var element;

    for (var i = 0; i < element_list.length; i++) {
        var zindex = window.getComputedStyle(element_list[i]).getPropertyValue('z-index');
        if (+zindex > +max) {
            max = zindex;
            element = element_list[i];
        }
    }

    return element;
}


// Given an element and a parent element (not necessarily immediate parent),
// this function returns true if none of the elements between itself and this
// parent have z-index values set to a value other than 'auto'
var domZindexCheck = function(element, parent_element) {
    if (element == parent_element) {
        return true;
    } else {
        var parent = element.parentElement;

        while (parent != parent_element) {
            if (window.getComputedStyle(parent).getPropertyValue('z-index') != 'auto') {
                return false;
            }

            parent = parent.parentElement;
        }

        return true;
    }
}


// Calls the above function on a list of elements and a given parent element
var getElementsForCheck = function(element_list, parent_element) {
    var result = [];

    for (var i = 0; i < element_list.length; i++) {
        if (domZindexCheck(element_list[i], parent_element)) {
            result.push(element_list[i]);
        }
    }

    return result;
}


// Returns a list of divs on the web page that are visible, have a non-static
// 'position' and a z-index set to not 'auto'
// Note that z-index values lose their meaning when position is set to static
// Only considers those divs with position z-index values
var getDivs = function() {
    var result = [];
    element_list = document.querySelectorAll('div');

    for (var i = 0; i < element_list.length; i++) {
        var element = element_list[i];
        var style = window.getComputedStyle(element);
        var display = style.getPropertyValue('display') != 'none';
        var position = style.getPropertyValue('position') != 'static';
        var zindex = style.getPropertyValue('z-index')

        if (display && position && zindex != 'auto' && +zindex > 0) {
            result.push(element);
        }
    }

    return result;
}

// Repeatedly filter the list of divs as extracted above until we know it is
// the element on 'top'
return (function() {
    var divs = getDivs();
    var parent = document.body;
    var element;

    while (divs.length != 0) {
        var elements = getElementsForCheck(divs, parent);
        element = maxZindex(elements);

        divs = divs.filter(x => x != element && element.contains(x))
        parent = element;
    }

    return element;
})();
