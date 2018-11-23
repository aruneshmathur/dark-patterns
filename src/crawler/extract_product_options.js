const excludedWords = ['instagram', 'youtube', 'twitter', 'facebook', 'login',
  'log in', 'signup', 'sign up', 'signin', 'sign in',
  'share', 'account', 'add ', 'review', 'submit', 'related',
  'show ', 'shop ', 'upload ', 'code ', 'view details',
  'choose options', 'cart', 'loading', 'cancel', 'view all',
  'description', 'additional information', 'ship ', '$',
  '%', 'save as', 'out ', 'wishlist', 'increment', 'buy',
  'availability', 'decrement', 'pick ', 'video', 'plus', 'minus', 'quantity',
  'slide', 'address', 'learn more', 'select', 'at '
];

const winWidth = window.innerWidth;

var hasBorder = function(element) {
  var elements = Array.from(element.querySelectorAll('*'));
  elements.push(element);

  for (var child of elements) {
    var style = window.getComputedStyle(child);
    if (style.borderLeftStyle.toLowerCase() !== 'none' && style.borderRightStyle
      .toLowerCase() !== 'none') {
      return true;
    } else {
      var bstyle = window.getComputedStyle(child, ':before');
      if (bstyle.borderLeftStyle.toLowerCase() !== 'none' && bstyle.borderRightStyle
        .toLowerCase() !== 'none') {
        return true;
      } else {
        var astyle = window.getComputedStyle(child, ':after');
        if (astyle.borderLeftStyle.toLowerCase() !== 'none' && astyle.borderRightStyle
          .toLowerCase() !== 'none') {
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

var isInRightHalfOfPage = function(element) {
  var rect = element.getBoundingClientRect();
  var winWidth = window.innerWidth;
  return (rect.left >= 0.3 * winWidth && rect.left <= winWidth && rect.bottom <=
    1000 && rect.top >= 200);
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

var hasDimensionsAndLocation = function(element) {
  var rect = element.getBoundingClientRect();
  var height = rect.bottom - rect.top;
  var width = rect.right - rect.left;

  return (height > 21 && height < 110 && width > 5 && width < 270) && (rect.left >=
    0.3 * winWidth && rect.left <= winWidth && rect.bottom <=
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

  var allElements = liElements.concat(labelElements).concat(aElements).concat(
    spanElements).concat(divElements);
  allElements = allElements.filter(element => !isVisuallyHidden(element));

  allElements = allElements.filter(element => !hasIgnoredText(element.textContent +
    ' ' + element.getAttribute('class')));

  allElements = allElements.filter(element => hasRequiredDisplay(element));

  allElements = allElements.filter(element => !hasExcludedElements(element));

  allElements = allElements.filter(element => element.getElementsByTagName(
    'a').length <= 1);
  allElements = allElements.filter(element => element.getElementsByTagName(
    'button').length <= 1);

  allElements = allElements.filter(element => hasBorder(element));

  allElements = allElements.filter(element => hasDimensionsAndLocation(
    element));

  allElements = clusters(parentRemoval(allElements, 'li'), 4);

  for (var c of allElements) {
    if (c[0].tagName === 'li') {
      var parent = c[0].parentElement;
      var children = getVisibleChildren(parent);
      children = children.filter(child => !c.includes(child));

      if (children.length !== 0) {
        c = c.concat(children);
      }
    }
  }

  return allElements;
};

var s = getToggleAttributes();
var combinations = elementCombinations(s);

for (var comb of combinations) {
  for (var c of comb) {
    c.click();  }
}
