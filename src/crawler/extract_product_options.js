const excludedWords = ['instagram', 'youtube', 'twitter', 'facebook', 'login',
  'log in', 'signup', 'sign up', 'signin', 'sign in',
  'share', 'account', 'add', 'review', 'submit', 'related',
  'show ', 'shop ', 'upload ', 'code ', 'view details',
  'choose options', 'cart', 'loading', 'cancel', 'view all',
  'description', 'additional information', 'ship ', '$',
  '%', 'save as', 'out ', 'wishlist', 'increment', 'buy',
  'availability', 'decrement', 'pick ', 'video', 'plus', 'minus', 'quantity',
  'slide', 'address', 'learn more', 'at ', 'reserve', 'save'
];

const winWidth = window.innerWidth;

var parseColor = function(color) {
  var m = color.match(/^rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)$/i);
  if (m) {
    return [m[1], m[2], m[3], '1'];
  }

  m = color.match(
    /^rgba\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*((0.)?\d+)\s*\)$/i);
  if (m) {
    return [m[1], m[2], m[3], m[4]];
  }
};

var hasBorder = function(element, recurseChildren = true) {

  var borderCheck = function(borderStyle, borderColor) {
    return borderStyle.toLowerCase() !== 'none' && parseFloat(parseColor(borderColor)[3]) > 0.0;
  };

  var elements = [element];

  if (recurseChildren) {
    elements = elements.concat(Array.from(element.querySelectorAll('*')));
  }

  for (var child of elements) {
    var style = window.getComputedStyle(child);
    if (borderCheck(style.borderLeftStyle, style.borderLeftColor) &&
      borderCheck(style.borderRightStyle, style.borderRightColor)
    ) {
      return true;
    } else {
      var bstyle = window.getComputedStyle(child, ':before');
      if (borderCheck(bstyle.borderLeftStyle, bstyle.borderLeftColor) &&
        borderCheck(bstyle.borderRightStyle, bstyle.borderRightColor)
      ) {
        return true;
      } else {
        var astyle = window.getComputedStyle(child, ':after');
        if (borderCheck(astyle.borderLeftStyle, astyle.borderLeftColor) &&
          borderCheck(astyle.borderRightStyle, astyle.borderRightColor)
        ) {
          return true;
        } else {
          if (style.boxShadow !== 'none') {
            return true;
          }
        }
      }
    }
  }

  return false;
};

var hasIgnoredText = function(text) {
  if (text) {
    text = text.toLowerCase();

    for (var ew of excludedWords) {
      if (text.includes(ew)) {
        return true;
      }
    }

    return false;
  } else {
    return false;
  }
};

var hasExcludedElements = function(element) {
  var elements = {
    'select': null,
    'form': null,
    'iframe': null,
    'style': null,
    'input': function(x) {
      return x.type.toLowerCase() !== 'radio' && x.type.toLowerCase() !==
        'checkbox'
    },
    'dl': null,
    'ol': null,
    'ul': null,
    'table': null
  };

  for (var e in elements) {
    if (elements.hasOwnProperty(e)) {
      var children = element.querySelectorAll(e);
      var f = elements[e];

      if (f) {
        children = Array.from(children).filter(n => f(n));
      }

      if (children.length > 0) {
        return true;
      }
    }
  }

  return false;
};

var hasRequiredDisplay = function(element) {
  if (element) {
    var style = window.getComputedStyle(element);

    if (style.display === 'inline-block' || style.float === 'left') {
      return true;
    } else {
      var pStyle = window.getComputedStyle(element.parentElement);

      if (pStyle.display === 'flex' || pStyle.float === 'left') {
        return true;
      } else {
        return false;
      }
    }

  } else {
    return false;
  }
};

var hasHeight = function(rect, lower, upper) {
  var height = rect.bottom - rect.top;
  return (height > lower && height < upper);
};

var hasWidth = function(rect, lower, upper) {
  var width = rect.right - rect.left;
  return (width > lower && width < upper);
};

var hasLocation = function(rect) {
  return (rect.left >= 0.3 * winWidth && rect.left <= winWidth && rect.bottom <=
    900 && rect.top >= 200);
};

var elementCombinations = function(arr) {
  if (arr.length == 1) {
    return arr[0];
  } else {
    var result = [];
    var allCasesOfRest = elementCombinations(arr.slice(1));
    for (var i = 0; i < allCasesOfRest.length; i++) {
      for (var j = 0; j < arr[0].length; j++) {
        result.push([arr[0][j], allCasesOfRest[i]]);
      }
    }
    return result;
  }
};

var getToggleAttributes = function() {
  var liElements = Array.from(document.body.getElementsByTagName('li'));
  liElements = liElements.filter(element => element.getElementsByTagName('ul')
    .length === 0 && element.getElementsByTagName('ol').length === 0);

  var labelElements = Array.from(document.body.getElementsByTagName('label'));
  var aElements = Array.from(document.body.getElementsByTagName('a'));
  var spanElements = Array.from(document.body.getElementsByTagName('span'));
  var divElements = Array.from(document.body.getElementsByTagName('div'));

  var toggleElements = liElements.concat(labelElements).concat(aElements).concat(
    spanElements).concat(divElements);
  toggleElements = toggleElements.filter(element => isShown(element));

  toggleElements = toggleElements.filter(element => filterText(element.innerText) !== '1');

  toggleElements = toggleElements.filter(element => !hasIgnoredText(element.innerText +
    ' ' + element.getAttribute('class')));

  toggleElements = toggleElements.filter(element => hasRequiredDisplay(
    element));

  toggleElements = toggleElements.filter(element => !hasExcludedElements(
    element));

  toggleElements = toggleElements.filter(element => element.getElementsByTagName(
    'a').length <= 1);
  toggleElements = toggleElements.filter(element => element.getElementsByTagName(
    'button').length <= 1);

  toggleElements = toggleElements.filter(element => hasBorder(element));

  toggleElements = toggleElements.filter(element => {
    var rect = element.getBoundingClientRect();
    return hasHeight(rect, 21, 110) && hasWidth(rect, 5, 270) &&
      hasLocation(rect);
  });

  toggleElements = clusters(parentRemoval(toggleElements, 'li'), 4);

  for (var c of toggleElements) {
    if (c[0].tagName.toLowerCase() === 'li') {
      var parent = c[0].parentElement;
      var children = getVisibleChildren(parent);
      children = children.filter(child => !c.includes(child));

      if (children.length !== 0) {
        var index = toggleElements.indexOf(c);
        c = c.concat(children);
        if (index !== -1) {
          toggleElements[index] = c;
        }
      }
    }
  }

  return toggleElements;
};

var getSelectAttributes = function() {
  var selectElements = Array.from(document.body.getElementsByTagName('select'));
  selectElements = selectElements.filter(se => isShown(se));

  selectElements = selectElements.filter(se => filterText(se.innerText) !== '' && filterText(se.innerText) !== '1');

  selectElements = selectElements.filter(se => hasLocation(se));

  var result = [];
  for (var se of selectElements) {
    var res = [];
    var options = se.getElementsByTagName('option');

    for (var opt of options) {
      res.push([se, opt]);
    }

    result.push(res);
  }

  return selectElements;
};

var getNonStandardSelectAttributes = function(excludedElements) {
  var labelElements = Array.from(document.body.getElementsByTagName('label'));
  var aElements = Array.from(document.body.getElementsByTagName('a'));
  var spanElements = Array.from(document.body.getElementsByTagName('span'));
  var divElements = Array.from(document.body.getElementsByTagName('div'));
  var buttonElements = Array.from(document.body.getElementsByTagName('button'));

  var triggerElements = labelElements.concat(aElements).concat(spanElements).concat(
    divElements).concat(buttonElements);
  triggerElements = triggerElements.filter(te => isShown(te));

  triggerElements = triggerElements.filter(te => filterText(te.innerText) !==
    '' && filterText(te.innerText) !== '1' && !hasIgnoredText(te.innerText));

  triggerElements = triggerElements.filter(te => {
    var rect = te.getBoundingClientRect();
    return hasHeight(rect, 10, 100) && hasLocation(rect) && hasWidth(rect, 5, 600);
  });

  triggerElements = triggerElements.filter(te => hasBorder(te, false));

  triggerElements = triggerElements.filter(te => te.getElementsByTagName('a')
    .length <= 1);

  triggerElements = triggerElements.filter(te => !te.style.position !==
    'fixed');

  triggerElements = parentRemoval(triggerElements);

  triggerElements = triggerElements.filter(te => excludedElements.map(ee => !
    ee.contains(te) && !te.contains(ee)).every(val => val === true));


  var ulElements = Array.from(document.body.getElementsByTagName('ul'));
  var olElements = Array.from(document.body.getElementsByTagName('ol'));
  var dlElements = Array.from(document.body.getElementsByTagName('dl'));

  var optionLists = ulElements.concat(olElements).concat(dlElements);
  optionLists = optionLists.filter(element => !isShown(element) && element.children.length > 0);

  var result = [];

  for (var te of triggerElements) {
    for (var optList of optionLists) {
      if ([te].concat(getSiblings(te)).some(ele => ele.contains(optList))) {
        var res = [];

        for (var child of optList.children) {
          res.push([te, child]);
        }

        result.push(res);
      }
    }
  }

  return result;
};

var play = function() {
  var te = getToggleAttributes();
  var se = getSelectAttributes();

  if (se.length === 0) {
    se = getNonStandardSelectAttributes(flattenDeep(te));
  }

  console.log(te);
  console.log(se);
};
