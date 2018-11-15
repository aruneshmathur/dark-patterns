var blockElements = ['div', 'body', 'section', 'article', 'aside', 'nav', 'header', 'footer', 'main', 'form', 'fieldset'];
var ignoredElements = ['script', 'style', 'noscript', 'br', 'hr'];

var getElementWidth = function(element) {
  var rect = element.getBoundingClientRect();
  return rect.right - rect.left;
};

var getElementHeight = function(element) {
  var rect = element.getBoundingClientRect();
  return rect.bottom - rect.top;
};

var isVisuallyHidden = function(element) {
  var style = window.getComputedStyle(element);
  if (style.display === 'none' || style.visibility === 'hidden') {
    return true;
  } else if (parseFloat(style.opacity) === 0.0) {
    return true;
  } else {
    var height = getElementHeight(element);
    var width = getElementWidth(element);

    if (height === 0 || width === 0) {

      var overflowX = style.getPropertyValue('overflow-x');
      var overflowY = style.getPropertyValue('overflow-y');

      if (overflowX !== 'visible' || overflowY !== 'visible') {
        return true;
      }

      if (element.children.length === 0) {
        return true;
      } else {
        for (var child of element.children) {
          if (!isVisuallyHidden(child)) {
            return false;
          }
        }
        return true;
      }
    } else {
      if (style.position === 'absolute') {
        var t = parseFloat(style.top);
        var l = parseFloat(style.left);

        if (t + height < 0 || l + width < 0) {
          return true;
        } else {
          return false;
        }
      } else if (height === 1 || width === 1) {
        // Likely a separator
        if (element.children.length === 0) {
          return true;
        }
      } else {
        return false;
      }
    }
  }
};

var allIgnoreChildren = function(element) {
  if (element.children.length === 0) {
    return false;
  } else {
    for (var child of element.children) {
      if (ignoredElements.includes(child.tagName.toLowerCase())) {
        continue;
      } else {
        return false;
      }
    }
    return true;
  }
};

var containsBlockElements = function(element) {
  for (var child of element.children) {
    if (blockElements.includes(child.tagName.toLowerCase())) {
      return true;
    }
  }

  return false;
}

var filterText = function(text) {
  return text.replace(/(\r\n|\n|\r)/gm, '').trim();
}

var containsTextNodes = function(element) {
  if (element) {
    if (element.hasChildNodes()) {

      var nodes = [];
      for (var cnode of element.childNodes) {
        if (cnode.nodeType === Node.TEXT_NODE) {
          var text = filterText(cnode.nodeValue);
          if (text.length !== 0) {
            nodes.push(text);
          }
        }
      }

      return (nodes.length > 0 ? true : false);
    } else {
      return false;
    }
  } else {
    return false;
  }
};

var isPixel = function(element) {
  var style = window.getComputedStyle(element);

  var height = getElementHeight(element);
  var width = getElementWidth(element);

  return (height === 1 && width === 1);
};


var segments = function(element) {
  if (element && !isVisuallyHidden(element) && !isPixel(element)) {
    var tag = element.tagName.toLowerCase();
    if (blockElements.includes(tag)) {
      if (!containsBlockElements(element)) {
        if (allIgnoreChildren(element)) {
          return [];
        } else {
          return [element];
        }
      } else if (containsTextNodes(element)) {
        return [element];
      } else {

        var result = [];

        for (var child of element.children) {
          result = result.concat(segments(child));
        }

        return result;
      }
    } else if (ignoredElements.includes(tag)) {
      return [];
    } else {
      return [element];
    }
  } else {
    return [];
  }
};

var segs = segments(document.body);
console.log(segs);
