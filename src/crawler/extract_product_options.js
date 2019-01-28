const excludedWords = ['instagram', 'youtube', 'twitter', 'facebook', 'login',
  'log in', 'signup', 'sign up', 'signin', 'sign in', 'pinterest', 'email',
  'share', 'account', 'add ', 'review', 'submit', 'related',
  'show ', 'shop ', 'upload ', 'code ', 'view details',
  'choose options', 'cart', 'loading', 'cancel', 'view all',
  'description', 'additional information', 'ship ', '$',
  '%', 'save as', 'out ', 'wishlist', 'increment', 'buy', 'shipping',
  'availability', 'decrement', 'pick ', 'video', 'plus', 'minus', 'quantity',
  'slide', 'address', 'learn more', 'at ', 'reserve', 'save', 'pickup', 'favorite',
  'gift', 'registry', 'larger ', 'guide', 'seeds', 'stars', 'compare', 'linkedin', 'chat',
  'notify ', 'order ', ' order', 'question', 'upsell', 'looking for ', 'get free demo',
  'wish list', 'more information', 'delivery', 'back', 'in-store', 'trustpilot', 'newsletter',
  'custom size'
];

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
    return borderStyle.toLowerCase() !== 'none';
    //&& parseFloat(parseColor(borderColor)[3]) > 0.0;
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
  return (rect.left >= 0.3 * winWidth && rect.left <= winWidth && rect.top <=
    900 && rect.top >= 200 && rect.right <= 0.9 * winWidth);
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

  toggleElements = toggleElements.filter(element => element.getElementsByTagName(
    'a').length <= 1);
  toggleElements = toggleElements.filter(element => element.getElementsByTagName(
    'button').length <= 1);

  toggleElements = toggleElements.filter(element => {
    var text = element.innerText;
    var eclass = element.getAttribute('class');
    var textCheck = text + ' ' + eclass;

    var a_child = element.getElementsByTagName('a');
    var button_child = element.getElementsByTagName('button');

    if (a_child.length === 1) {
      textCheck = textCheck + ' ' + (a_child[0].getAttribute('href') || '').replace(/%/, '');
      textCheck = textCheck + ' ' + (a_child[0].getAttribute('onclick') || '').replace(/%/, '');
      textCheck = textCheck + ' ' + (a_child[0].getAttribute('class') || '').replace(/%/, '');
    }

    if (button_child.length === 1) {
      textCheck = textCheck + ' ' + (button_child[0].getAttribute('href') || '').replace(/%/, '');
      textCheck = textCheck + ' ' + (button_child[0].getAttribute('onclick') || '').replace(/%/, '');
      textCheck = textCheck + ' ' + (button_child[0].getAttribute('class') || '').replace(/%/, '');
    }

    return !hasIgnoredText(textCheck) && text.replace(
      /[^\x00-\xFF]/g, '') !== '1';
  });

  toggleElements = toggleElements.filter(element => {
    var href = element.getAttribute('href');
    var src = element.getAttribute('src');
    var onclick = element.getAttribute('onclick');

    for (var ew of ['facebook', 'linkedin', 'twitter', 'blogger', 'instagram', 'youtube', 'email', 'tumblr', 'google', 'pinterest', 'wishlist', 'sendfriend', 'trustpilot', 'newsletter']) {
      if ((href + ' ' + src + ' ' + onclick).includes(ew)) {
        return false;
      }
    }

    return true;
  });

  toggleElements = toggleElements.filter(element => !hasExcludedElements(
    element));

  toggleElements = toggleElements.filter(element => {
    var rect = element.getBoundingClientRect();
    return hasHeight(rect, 19, 110) && hasWidth(rect, 5, 270) &&
      hasLocation(rect);
  });

  toggleElements = toggleElements.filter(element => hasRequiredDisplay(
    element));

  toggleElements = toggleElements.filter(element => hasBorder(element));

  toggleElements = toggleElements.filter(element => isShown(element));

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

  selectElements = selectElements.filter(se => filterText(se.innerText) !==
    '' && filterText(se.options[se.selectedIndex].innerText) !== '1');

  selectElements = selectElements.filter(se => {
    var rect = se.getBoundingClientRect();
    return hasLocation(rect) && hasHeight(rect, 5, winHeight) && hasWidth(rect, 5, winWidth);
  });

  var result = [];
  for (var se of selectElements) {
    var res = [];
    var options = se.getElementsByTagName('option');

    for (var opt of options) {
      if (opt.innerText.toUpperCase().includes('SELECT') || opt.innerText.toUpperCase().includes('CHOOSE')) {
        continue;
      }
      else {
        res.push([se, opt]);
      }
    }

    result.push(res);
  }

  return result;
};

var getNonStandardSelectAttributes = function(excludedElements) {
  var labelElements = Array.from(document.body.getElementsByTagName('label'));
  var aElements = Array.from(document.body.getElementsByTagName('a'));
  var spanElements = Array.from(document.body.getElementsByTagName('span'));
  var divElements = Array.from(document.body.getElementsByTagName('div'));
  var buttonElements = Array.from(document.body.getElementsByTagName('button'));

  var triggerElements = labelElements.concat(aElements).concat(spanElements).concat(
    divElements).concat(buttonElements);

  triggerElements = triggerElements.filter(te => te.getElementsByTagName('a')
    .length <= 1);

  triggerElements = triggerElements.filter(te => {
    var text = filterText(te.innerText);
    return text !== '' && text.replace(/[^\x00-\xFF]/g, '') !== '1' && !hasIgnoredText(text);
  });

  triggerElements = triggerElements.filter(te => {
    var rect = te.getBoundingClientRect();
    return hasHeight(rect, 10, 100) && hasLocation(rect) && hasWidth(rect,
      5, 600);
  });

  triggerElements = triggerElements.filter(te => hasBorder(te, false));

  triggerElements = triggerElements.filter(te => {
    var style = window.getComputedStyle(te);

    return style ? (style.position === 'fixed' ? false : true) : false;
  });

  triggerElements = triggerElements.filter(te => isShown(te));

  triggerElements = parentRemoval(triggerElements);

  triggerElements = triggerElements.filter(te => excludedElements.map(ee => !
    ee.contains(te) && !te.contains(ee)).every(val => val === true));


  var ulElements = Array.from(document.body.getElementsByTagName('ul'));
  var olElements = Array.from(document.body.getElementsByTagName('ol'));
  var dlElements = Array.from(document.body.getElementsByTagName('dl'));

  var optionLists = ulElements.concat(olElements).concat(dlElements);
  optionLists = optionLists.filter(element => !isShown(element) && element.children
    .length > 0);

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

var mapXPath = function(list) {
  return list.map(element => (element instanceof Array) ? mapXPath(element) :
    getXPathTo(element));
};

var playAttributes = function(signalWhenFinished=true) {

  var te = getToggleAttributes();
  var se = getSelectAttributes();

  if (se.length === 0) {
    se = getNonStandardSelectAttributes(flattenDeep(te));
  }

  var attributes = te.concat(se);
  attributes.sort(function(x, y) {
      var xy;
      var yy;

      if (x[0] instanceof Array) {
        xy = x[0][0].getBoundingClientRect().y;
      }
      else {
        xy = x[0].getBoundingClientRect().y;
      }

      if (y[0] instanceof Array) {
        yy = y[0][0].getBoundingClientRect().y;
      }
      else {
        yy = y[0].getBoundingClientRect().y;
      }

      return xy - yy;
  });

  attributes = mapXPath(attributes);

  if (attributes.length === 0) {
    return [];
  }

  var combinations = elementCombinations(attributes);
  return getRandomSubarray(combinations, 5);

  /*function clickHandler(element) {
    if (element) {
      var as = element.getElementsByTagName('a');
      if (as.length !== 0) {
        as[0].click();
        return;
      }

      var buttons = element.getElementsByTagName(
        'button');
      if (buttons.length !== 0) {
        buttons[0].click();
        return;
      }

      if (element.children.length > 0) {
        element.children[0].click()
      } else {
        element.click();
      }
    }

    return;
  }

  var waitTime = 3000;
  console.log(randomCombinations.length);
  randomCombinations.forEach(function(rc, ind) {

    setTimeout(function() {
      console.log(rc);
      try {
        rc.forEach(function(el, index) {

          setTimeout(function() {
            console.log(el);
            try {
              if (el instanceof Array) {
                var selectEl = getElementsByXPath(el[0],
                  document.documentElement, document)[0];
                var optionEl = getElementsByXPath(el[1],
                  document.documentElement, document)[0];
                if (selectEl.tagName.toLowerCase() ==
                  "select") {
                  selectEl.value = optionEl.value;
                  var event = new Event("change", {"bubbles":true, "cancelable":false});
                  selectEl.dispatchEvent(event);
                } else {
                  clickHandler(selectEl);
                  clickHandler(optionEl);
                }
              } else {
                var element = getElementsByXPath(el, document
                  .documentElement, document)[
                  0];
                if (element) {
                  console.log(element);
                  clickHandler(element);
                }
              }
            } catch (err) {
              console.log(err);
            }
            console.log("ind", ind);
            if (ind == randomCombinations.length -1) {
              if (signalWhenFinished){
                console.log("Finished product attribute interaction")
                // selenium will check this localStorate item to detect the end of product interaction
                localStorage['openwpm-playAttributesDone'] = true;
              }
             }
          }, index * waitTime);

        });
      } catch (err1) {
        console.log(err1);
      }
    }, ind * (randomCombinations.length) * (waitTime + 2000));
  });*/
};

//playAttributes();
