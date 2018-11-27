var doSegment = function(element) {
  if (element) {
    var segs = segment(element);

    if (segs.length === 1 && segs[0] == element) {
      return segs;
    } else {
      var result = [];

      for (var s of segs) {
        result = result.concat(doSegment(s));
      }

      return result;
    }
  } else {
    return [];
  }
};

var segment = function(element) {
  if (!isShown(element) || isPixel(element)) {
    return [];
  }

  var tag = element.tagName.toLowerCase();
  if (ignoredElements.includes(tag)) {
    return [];
  } else if (!blockElements.includes(tag)) {
    return [element];
  } else {
    var children = getVisibleChildren(element);
    children = children.filter(child => !isPixel(child));

    if (!containsBlockElements(children) || (containsTextNodes(element) && tag !== 'body')) {
      return [element];
    }

    if (children.length === 1) {
      return children;
    }

    var aSD = avgSeamDegree(children, element);
    var aCS = avgContentSimilarity(children, element);

    if (aSD <= 0.8 || aCS <= 0.8) {
      return children;
    }

    return [element];
  }
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
    } else {
      x1 = rect2.left;
    }

    if (rect1.right > rect2.right) {
      x2 = rect1.right;
    } else {
      x2 = rect2.right;
    }

    if (rect1.top < rect2.top) {
      y1 = rect1.bottom;
      y2 = rect2.top;
    } else {
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
    seamLength = getElementWidth(element2);
  } else if (rect1.right < rect2.right && rect1.left > rect2.left) {
    seamLength = getElementWidth(element1);
  } else if (rect1.right < rect2.right) {
    seamLength = Math.abs(rect1.right - rect2.left);
  } else {
    seamLength = Math.abs(rect2.right - rect1.left);
  }

  if (getElementWidth(element1) === 0 || getElementWidth(element2) === 0) {
    return 0;
  } else {
    return (seamLength * seamLength) / (getElementWidth(element1) * getElementWidth(element2));
  }
};

var checkHeightAdj = function(element1, element2, parentEle) {
  var x1, x2, y1, y2;

  var rect1 = element1.getBoundingClientRect();
  var rect2 = element2.getBoundingClientRect();

  if (rect1.bottom > rect2.top && rect1.top < rect2.bottom) {
    if (rect1.top < rect2.top) {
      y1 = rect1.top;
    } else {
      y1 = rect2.top;
    }

    if (rect1.bottom > rect2.bottom) {
      y2 = rect1.bottom;
    } else {
      y2 = rect2.bottom;
    }

    if (rect1.left < rect2.left) {
      x1 = rect1.right;
      x2 = rect2.left;
    } else {
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
    seamLength = getElementHeight(element2);
  } else if (rect1.bottom < rect2.bottom && rect1.top > rect2.top) {
    seamLength = getElementHeight(element1);
  } else if (rect1.bottom < rect2.bottom) {
    seamLength = Math.abs(rect1.bottom - rect2.top);
  } else {
    seamLength = Math.abs(rect2.bottom - rect1.top);
  }

  if (getElementHeight(element1) === 0 || getElementHeight(element2) === 0) {
    return 0;
  } else {
    return (seamLength * seamLength) / (getElementHeight(element1) * getElementHeight(element2));
  }
};

var avgSeamDegree = function(elements, parentEle) {
  var count = 0;
  var avgSD = 0;

  for (var i = 0; i < elements.length; i++) {
    for (var j = i + 1; j < elements.length; j++) {
      if (checkWidthAdj(elements[i], elements[j], parentEle)) {
        avgSD += seamDegreeW(elements[i], elements[j]);
        count = count + 1;
      } else if (checkHeightAdj(elements[i], elements[j], parentEle)) {
        avgSD += seamDegreeH(elements[i], elements[j]);
        count = count + 1;
      }
    }
  }

  if (count !== 0) {
    avgSD = avgSD / count;
    return Number((avgSD).toFixed(1));
  } else {
    return 0.0;
  }
};

var getTextNodes = function(element) {
  if (element && isShown(element)) {
    var style = window.getComputedStyle(element);
    var textNodes = [];

    for (var child of element.childNodes) {
      var cNodeName = child.nodeName.toLowerCase();
      if (child.nodeType === Node.TEXT_NODE) {
        var text = filterText(child.nodeValue);
        if (text.length !== 0) {
          textNodes.push([text.length, parseInt(style.fontSize)]);
        }
      } else if (child.nodeType === Node.ELEMENT_NODE && cNodeName !== 'a' && cNodeName !== 'img' &&
        cNodeName !== 'input' && cNodeName !== 'button' && cNodeName !== 'select') {
        var result = getTextNodes(child);

        if (result.length !== 0) {
          textNodes = textNodes.concat(result);
        }
      }
    }

    return textNodes;
  } else {
    return [];
  }
};

var getVectors = function(element) {
  var res = {};
  var tv = [];
  var av = [];
  var imgv = [];
  var inputv = [];

  var a_children = Array.from(element.querySelectorAll('a'));
  a_children = a_children.concat(Array.from(element.querySelectorAll('input:not([type=submit])')));
  a_children = a_children.concat(Array.from(element.querySelectorAll('button')));
  for (var a of a_children) {
    if (isShown(a)) {
      var aText = filterText(a.innerText);
      var aStyle = window.getComputedStyle(a, ':after');
      var fontSize = parseInt(aStyle.fontSize);
      if (aText.length !== 0 && fontSize !== 0) {
        av.push(fontSize * fontSize * aText.length);
      }
    }
  }

  var img_children = Array.from(element.querySelectorAll('img'));
  img_children = img_children.concat(Array.from(element.querySelectorAll('svg')));
  for (var img of img_children) {
    if (isShown(img)) {
      imgv.push(getElementHeight(img) * getElementWidth(img));
    }
  }

  var input_children = Array.from(element.querySelectorAll('input'));
  input_children = input_children.concat(Array.from(element.querySelectorAll('select')));
  for (var input of input_children) {
    if (isShown(input)) {
      inputv.push(getElementHeight(input) * getElementWidth(input));
    }
  }

  for (var ele of getTextNodes(element)) {
    tv.push(ele[0] * ele[1] * ele[1]);
  }

  av.sort(function(a, b) {
    return b - a
  });
  imgv.sort(function(a, b) {
    return b - a
  });
  inputv.sort(function(a, b) {
    return b - a
  });
  tv.sort(function(a, b) {
    return b - a
  });

  res['linkVector'] = av;
  res['imgVector'] = imgv;
  res['inputVector'] = inputv;
  res['textVector'] = tv;

  return res;
};

var weight = function(vec1, vec2, element1, element2) {
  var ui = 0;
  var vi = 0;

  var area1 = getElementHeight(element1) * getElementWidth(element1);
  var area2 = getElementHeight(element2) * getElementWidth(element2);

  for (var ele of vec1) {
    ui += ele;
  }

  for (var ele of vec2) {
    vi += ele;
  }

  if (area1 === 0 || area2 === 0) {
    return 0;
  } else {
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
  } else if (vec1.length < vec2.length) {
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
  } else {
    cs = top / (botUi * botVi);
  }

  return cs;
};

var contentSimilarity = function(element1, element2) {
  var cs = 0.0;
  var total = 0;

  var vectors1 = getVectors(element1);
  var vectors2 = getVectors(element2);

  var tv1 = vectors1.textVector;
  var tv2 = vectors2.textVector;

  var av1 = vectors1.linkVector;
  var av2 = vectors2.linkVector;

  var imgv1 = vectors1.imgVector;
  var imgv2 = vectors2.imgVector;

  var inputv1 = vectors1.inputVector;
  var inputv2 = vectors2.inputVector;

  cs += cosineSimilarity(tv1, tv2);
  if (tv1.length !== 0) {
    total = total + 1;
  }

  cs += cosineSimilarity(av1, av2);
  if (av1.length !== 0) {
    total = total + 1;
  }

  cs += cosineSimilarity(imgv1, imgv2);
  if (imgv1.length !== 0) {
    total = total + 1;
  }

  cs += cosineSimilarity(inputv1, inputv2);
  if (inputv1.length !== 0) {
    total = total + 1;
  }

  if (total === 0) {
    return cs;
  } else {
    return cs / total;
  }
};

var avgContentSimilarity = function(elements, parentEle) {
  var count = 0;
  var avgCS = 0;

  for (var i = 0; i < elements.length; i++) {
    for (var j = i + 1; j < elements.length; j++) {
      if (checkWidthAdj(elements[i], elements[j], parentEle) || checkHeightAdj(elements[i], elements[j], parentEle)) {
        avgCS += contentSimilarity(elements[i], elements[j]);
        count = count + 1;
      }
    }
  }

  if (count != 0) {
    avgCS = avgCS / count;
  }

  return Number((avgCS).toFixed(1));
};

var segs = doSegment(document.body);
console.log(segs);

for (var seg of segs) {
  seg.style.border = '0.1em solid red';
  var fontSize = parseInt(window.getComputedStyle(seg).fontSize);

  if (fontSize === 0) {
    seg.style.fontSize = "10px";
  }
}
