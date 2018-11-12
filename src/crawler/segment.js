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

var getVisibleChildren = function(element) {
  if (element) {
    var children = Array.from(element.children);
    return children.filter(child => !isVisuallyHidden(child));
  }
  else {
    return [];
  }
};

var containsBlockElements = function(elements) {
  for (var element of elements) {
    if (blockElements.includes(element.tagName.toLowerCase())) {
      return true;
    }
  }
  return false;
};

var filterText = function(text) {
  return text.replace(/(\r\n|\n|\r)/gm, '').trim();
};

var isPixel = function(element) {
  var style = window.getComputedStyle(element);

  var height = element.offsetHeight;
  var width = element.offsetWidth;

  return (height === 1 && width === 1);
};

var doSegment = function(element) {
  if (element) {
    var segs = segment(element);

    if (segs.length === 1 && segs[0] == element) {
      return segs;
    }
    else {
      var result = [];

      for (var s of segs) {
        result = result.concat(doSegment(s));
      }

      return result;
    }
  }
  else {
    return [];
  }
};

var segment = function(element) {
  if (isVisuallyHidden(element) || isPixel(element)) {
    return [];
  }

  var tag = element.tagName.toLowerCase();
  if (ignoredElements.includes(tag)) {
    return [];
  }

  if (!blockElements.includes(tag)) {
    return [element];
  }

  var children = getVisibleChildren(element);
  if (children.length === 0) {
    return [element];
  }

  if (!containsBlockElements(children)) {
    return [element];
  }

  if (children.length === 1) {
    return children;
  }

  var aSD = avgSeamDegree(children, element);
  var aCS = avgContentSimilarity(children, element);

  console.log(element);
  console.log(aSD);
  console.log(aCS);

  if (aSD < 0.9 || aCS < 0.8) {
    return children;
  }

  return [element];
};

var checkIntersect = function(rect1, rect2) {
  return !(rect1.right < rect2.left ||
            rect1.left > rect2.right ||
            rect1.bottom < rect2.top ||
            rect1.top > rect2.bottom)
};

var checkWidthAdj = function(element1, element2, parentEle) {
  var x1, x2, y1, y2;

  var rect1 = element1.getBoundingClientRect();
  var rect2 = element2.getBoundingClientRect();

  if (rect1.right > rect2.left && rect1.left < rect2.right) {
    if (rect1.left < rect2.left) {
      x1 = rect1.left;
    }
    else {
      x1 = rect2.left;
    }

    if (rect1.right > rect2.right) {
      x2 = rect1.right;
    }
    else {
      x2 = rect2.right;
    }

    if (rect1.top < rect2.top) {
      y1 = rect1.bottom;
      y2 = rect2.top;
    }
    else  {
      y1 = rect2.bottom;
      y2 = rect1.top;
    }

    var boundingRect = {};
    boundingRect['left'] = x1;
    boundingRect['right'] = x2;
    boundingRect['top'] = y1;
    boundingRect['bottom'] = y2;

    for (var child of getVisibleChildren(parentEle)) {
      if (child != element1 && child != element2) {
        if (checkIntersect(boundingRect, child.getBoundingClientRect())) {
          return false;
        }
      }
    }

    return true;
  }

  return false;
};

var seamDegreeW = function(element1, element2) {
  var seamLength = 0;

  var rect1 = element1.getBoundingClientRect();
  var rect2 = element2.getBoundingClientRect();


  if (rect1.right > rect2.right && rect1.left < rect2.left) {
    seamLength = element2.offsetWidth;
  }
  else if (rect1.right < rect2.right && rect1.left > rect2.left) {
    seamLength = element1.offsetWidth;
  }
  else if (rect1.right < rect2.right) {
    seamLength = Math.abs(rect1.right - rect2.left);
  }
  else {
    seamLength = Math.abs(rect2.right - rect1.left);
  }

  if (element1.offsetWidth === 0 || element2.offsetWidth === 0) {
    return 0;
  }
  else {
    return (seamLength * seamLength) / (element1.offsetWidth * element2.offsetWidth);
  }
};

var checkHeightAdj = function(element1, element2, parentEle) {
  var x1, x2, y1, y2;

  var rect1 = element1.getBoundingClientRect();
  var rect2 = element2.getBoundingClientRect();

  if (rect1.bottom > rect2.top && rect1.top < rect2.bottom) {
    if (rect1.top < rect2.top) {
      y1 = rect1.top;
    }
    else {
      y1 = rect2.top;
    }

    if (rect1.bottom > rect2.bottom) {
      y2 = rect1.bottom;
    }
    else {
      y2 = rect2.bottom;
    }

    if (rect1.left < rect2.left) {
      x1 = rect1.right;
      x2 = rect2.left;
    }
    else  {
      x1 = rect2.right;
      x2 = rect1.left;
    }

    var boundingRect = {};
    boundingRect['left'] = x1;
    boundingRect['right'] = x2;
    boundingRect['top'] = y1;
    boundingRect['bottom'] = y2;

    for (var child of getVisibleChildren(parentEle)) {
      if (child != element1 && child != element2) {
        if (checkIntersect(boundingRect, child.getBoundingClientRect())) {
          return false;
        }
      }
    }

    return true;
  }

  return false;
};

var seamDegreeH = function(element1, element2) {
  var seamLength = 0;

  var rect1 = element1.getBoundingClientRect();
  var rect2 = element2.getBoundingClientRect();

  if (rect1.bottom > rect2.bottom && rect1.top < rect2.top) {
    seamLength = element2.offsetHeight;
  }
  else if (rect1.bottom < rect2.bottom && rect1.top > rect2.top) {
    seamLength = element1.offsetHeight;
  }
  else if (rect1.bottom < rect2.bottom) {
    seamLength = Math.abs(rect1.bottom - rect2.top);
  }
  else {
    seamLength = Math.abs(rect2.bottom - rect1.top);
  }

  if (element1.offsetHeight === 0 || element2.offsetHeight === 0) {
    return 0;
  }
  else {
    return (seamLength * seamLength) / (element1.offsetHeight * element2.offsetHeight);
  }
};

var avgSeamDegree = function(elements, parentEle) {
  var count = 0;
  var avgSD = 0;

  for (var i=0; i < elements.length; i++) {
    for (var j=i+1; j < elements.length; j++) {
      if (checkWidthAdj(elements[i], elements[j], parentEle)) {
        avgSD += seamDegreeW(elements[i], elements[j]);
        count = count + 1;
      }
      else if (checkHeightAdj(elements[i], elements[j], parentEle)) {
        avgSD += seamDegreeH(elements[i], elements[j]);
        count = count + 1;
      }
    }
  }

  if (count != 0) {
    avgSD = avgSD / count;
    return avgSD;
  }
  else {
    return 0.0;
  }
};

var getVectors = function(element) {
  var res = {};
  var tv = [];
  var av = [];
  var cv = [];

  var style = window.getComputedStyle(element);

  for (var child of element.childNodes) {
    if (child.nodeType === Node.TEXT_NODE && filterText(child.nodeValue).length !== 0) {
      var text = filterText(child.nodeValue);
      tv.push(parseInt(style.fontSize) * parseInt(style.fontSize) * text.length);
    }
    else if (child.nodeType === Node.ELEMENT_NODE && !isVisuallyHidden(child)) {
      if (child.nodeName.toLowerCase() === 'a' && filterText(child.textContent).length !== 0) {
        var cText = filterText(child.textContent);
        var cStyle = window.getComputedStyle(child);
        av.push(parseInt(cStyle.fontSize) * parseInt(cStyle.fontSize) * cText.length);
      }
      else {
        cv.push(child.offsetWidth * child.offsetHeight);
      }
    }
  }

  if (element.children.length === 0) {
    cv.push(element.offsetWidth * element.offsetHeight);
  }

  tv.sort(); tv.reverse();
  av.sort(); av.reverse();
  cv.sort(); cv.reverse();

  res['textVector'] = tv;
  res['linkVector'] = av;
  res['contentVector'] = cv;

  return res;
};

var weight = function(vec1, vec2, element1, element2) {
  var ui = 0;
  var vi = 0;

  var area1 = element1.offsetWidth * element1.offsetHeight;
  var area2 = element2.offsetWidth * element2.offsetHeight;

  for (var ele of vec1) {
    ui += ele;
  }

  for (var ele of vec2) {
    vi += ele;
  }

  if (area1 === 0 || area2 === 0) {
    return 0;
  }
  else {
    return (ui + vi) / (area1 + area2);
  }
};

var cosineSimilarity = function(vec1, vec2) {
  var cs = 0.0;
  var top = 0.0;
  var botUi = 0;
  var botVi = 0;

  if (vec1.length > vec2.length) {
    var pom = vec1.length - vec2.length;
    for (var i = 0; i < pom; i++) {
      vec2.push(0.0);
    }
  }
  else if (vec1.length < vec2.length){
    var pom = vec2.length - vec1.length;
    for (var i = 0; i < pom; i++) {
      vec1.push(0.0);
    }
  }

  var n = vec1.length;

  for (var i = 0; i < n; i++) {
    top += (vec1[i] * vec2[i]);
    botUi += (vec1[i] * vec1[i]);
    botVi += (vec2[i] * vec2[i]);
  }

  botUi = Math.sqrt(botUi);
  botVi = Math.sqrt(botVi);

  if (botUi === 0 || botVi === 0) {
    cs = 0;
  }
  else {
    cs = top / (botUi * botVi);
  }

  return cs;
};

var contentSimilarity = function(element1, element2) {
  var cs = 0.0;

  var vectors1 = getVectors(element1);
  console.log('Vector for ');
  console.log(element1);
  console.log(vectors1);
  var vectors2 = getVectors(element2);
  console.log('Vector for ');
  console.log(element2);
  console.log(vectors2);

  var tv1 = vectors1.textVector;
  var tv2 = vectors2.textVector;

  var av1 = vectors1.linkVector;
  var av2 = vectors2.linkVector;

  var cv1 = vectors1.contentVector;
  var cv2 = vectors2.contentVector;

  cs += weight(tv1, tv2, element1, element2) * cosineSimilarity(tv1, tv2);
  cs += weight(av1, av2, element1, element2) * cosineSimilarity(av1, av2);
  cs += weight(cv1, cv2, element1, element2) * cosineSimilarity(cv1, cv2);

  return cs;
};

var avgContentSimilarity = function(elements, parentEle) {
  var count = 0;
  var avgCS = 0;

  for (var i=0; i < elements.length; i++) {
    for (var j=i+1; j < elements.length; j++) {
      if (checkWidthAdj(elements[i], elements[j], parentEle) || checkHeightAdj(elements[i], elements[j], parentEle)) {
        avgCS += contentSimilarity(elements[i], elements[j]);
        count = count + 1;
      }
    }
  }

  if (count != 0) {
    avgCS = avgCS / count;
  }

  return avgCS;
};

var getVisibleSiblings = function(element) {
  if (element) {
    var parent = element.parentElement;
    var children = getVisibleChildren(parent);

    return children.filter(child => child != element);
  }
  else {
    return [];
  }
};

var resolveSegment = function(segment) {
  if (segment && blockElements.includes(segment.tagName.toLowerCase())) {
    var element = segment;
    while (true && element.tagName.toLowerCase() !== 'body') {
      var siblings = getVisibleSiblings(element);

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

var segs = doSegment(document.body);
console.log(segs);
