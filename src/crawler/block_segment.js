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
      var children = [];
      for (var be of blockElements) {
        children = Array.from(element.getElementsByTagName(be));
        children = children.filter(child => !isVisuallyHidden(child));

        if (children.length > 0) {
          break;
        }
      }

      if (children.length > 0) {
        var result = [];

        for (var child of element.children) {
          result = result.concat(segments(child));
        }

        return result;
      }
      else {
        return [element];
      }
    }
  } else {
    return [];
  }
};

var segs = segments(document.body);
console.log(segs);

for (var seg of segs) {
  seg.style.border = '0.1em solid red';
  var fontSize = parseInt(window.getComputedStyle(seg).fontSize);

  if (fontSize === 0) {
    seg.style.fontSize = "10px";
  }
}
