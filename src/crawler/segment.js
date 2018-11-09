var blockElements = ['div', 'body', 'section', 'article', 'aside', 'nav', 'header', 'footer', 'main', 'form', 'fieldset'];
var ignoredElements = ['script', 'style', 'noscript', 'br', 'hr'];

var isVisuallyHidden = function(element) {
  var style = window.getComputedStyle(element);
  if (style.display === 'none' || style.visibility === 'hidden') {
    return true;
  } else if(parseFloat(style.opacity) === 0.0) {
    return true;
  } else {
    var height = element.offsetHeight;
    var width = element.offsetWidth;

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
        }
        else {
          return false;
        }
      }
      else {
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
  var width = element.offsetWidth;

  return (height !== 1 && width !== 1);
};

var segments = function(element) {
  if (element && !isVisuallyHidden(element) && notPixel(element)) {
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

var getChildren = function(n, skipMe) {
  var r = [];
  for (; n; n = n.nextSibling)
    if (n.nodeType == 1 && n != skipMe)
      r.push(n);
  return r;
};

var getSiblings = function(n) {
  return getChildren(n.parentNode.firstChild, n);
};

var resolveSegment = function(segment) {
  if (segment && blockElements.includes(segment.tagName.toLowerCase())) {
    var element = segment;
    while (true && element.tagName.toLowerCase() !== 'body') {
      var siblings = getSiblings(element).filter(sib => !isVisuallyHidden(sib));

      if (siblings.length === 0 && blockElements.includes(element.parentElement.tagName.toLowerCase())) {
        element = element.parentElement;
      } else {
        break;
      }
    }

    return element;
  } else {
    return segment;
  }
};

var segs = segments(document.body);
console.log(segs);
var rsegs = segs.map(s => resolveSegment(s));
console.log(rsegs);
fathom.clusters(rsegs, 6);
