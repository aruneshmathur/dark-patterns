var blockElements = ['div', 'body', 'section', 'aside', 'nav', 'header', 'footer', 'main', 'form', 'fieldset'];
var ignoredElements = ['script', 'style', 'noscript', 'br', 'hr'];

//opacity

var isHidden = function(element) {
  var style = window.getComputedStyle(element);
  if (style.display === 'none' || style.visibility === 'hidden') {
    return true;
  } else {
    var height = element.offsetHeight;
    var width = element.offsetwidth;

    if (height === 0 || width === 0) {
      if (element.children.length === 0) {
        return true;
      } else {
        for (var child of element.children) {
          if (!isHidden(child)) {
            return false;
          }
        }
        return true;
      }
    } else {
      return false;
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
        if (cnode.nodeType == Node.TEXT_NODE) {
          var text = filterText(cnode.nodeValue);
          if (text.length !== 0) {
            nodes.push(text);
          }
        }
      }

      if (nodes.length > 0) {
        return true;
      } else {
        return false;
      }
    } else {
      return false;
    }
  } else {
    return false;
  }
};

var notPixel = function(element) {
  var style = window.getComputedStyle(element);

  var height = element.offsetHeight;
  var width = element.offsetwidth;

  return height !== 1 && width !== 1;
}

var segments = function(element) {
  if (element && !isHidden(element) && notPixel(element)) {
    var tag = element.tagName.toLowerCase();
    if (blockElements.includes(tag)) {
      if (window.getComputedStyle(element).display != 'block') {
        return [element];
      } else if (!containsBlockElements(element)) {
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


segments(document.body);
//fathom.clusters(segments(document.body), 7);
