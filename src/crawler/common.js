const blockElements = ['div', 'section', 'article', 'aside', 'nav',
  'header', 'footer', 'main', 'form', 'fieldset', 'table'
];
const ignoredElements = ['script', 'style', 'noscript', 'br', 'hr'];

const winWidth = window.innerWidth;
const winHeight = window.innerHeight;
const winArea = winWidth * winHeight;

var getElementArea = function(element) {
  var rect = element.getBoundingClientRect();
  return rect.height * rect.width;
};

var getClientRect = function(element) {
  if (element.tagName.toLowerCase() === 'html') {
    var w = Math.max(document.documentElement.clientWidth, window.innerWidth || 0);
    var h = Math.max(document.documentElement.clientHeight, window.innerHeight || 0);

    return {
      top: 0,
      left: 0,
      bottom: h,
      right: w,
      width: w,
      height: h,
      x: 0,
      y: 0
    };
  }
  else {
    return element.getBoundingClientRect();
  }
};

var getBackgroundColor = function(element) {
  var style = window.getComputedStyle(element);
  var tagName = element.tagName.toLowerCase();

  if (style === null || style.backgroundColor === 'transparent') {
    var parent = element.parentElement;
    return (parent === null || tagName === 'body') ? 'rgb(255, 255, 255)' : getBackgroundColor(parent);
  }
  else {
    return style.backgroundColor;
  }
};

var getRandomSubarray = function(arr, size) {
  var shuffled = arr.slice(0),
    i = arr.length,
    temp, index;
  while (i--) {
    index = Math.floor((i + 1) * Math.random());
    temp = shuffled[index];
    shuffled[index] = shuffled[i];
    shuffled[i] = temp;
  }
  return shuffled.slice(0, size);
};

var elementCombinations = function(arguments) {
  var r = [],
    arg = arguments,
    max = arg.length - 1;

  function helper(arr, i) {
    for (var j = 0, l = arg[i].length; j < l; j++) {
      var a = arr.slice(0);
      a.push(arg[i][j])
      if (i === max) {
        r.push(a);
      } else
        helper(a, i + 1);
    }
  }
  helper([], 0);

  return r.length === 0 ? arguments : r;
};

var getVisibleChildren = function(element) {
  if (element) {
    var children = Array.from(element.children);
    return children.filter(child => isShown(child));
  } else {
    return [];
  }
};

var getParents = function(node) {
  const result = [];
  while (node = node.parentElement) {
    result.push(node);
  }
  return result;
};

var isShown = function(element) {
  var displayed = function(element, style) {
    if (!style) {
      style = window.getComputedStyle(element);
    }

    if (style.display === 'none') {
      return false;
    } else {
      var parent = element.parentNode;

      if (parent && (parent.nodeType === Node.DOCUMENT_NODE)) {
        return true;
      }

      return parent && displayed(parent, null);
    }
  };

  var getOpacity = function(element, style) {
    if (!style) {
      style = window.getComputedStyle(element);
    }

    if (style.position === 'relative') {
      return 1.0;
    } else {
      return parseFloat(style.opacity);
    }
  };

  var positiveSize = function(element, style) {
    if (!style) {
      style = window.getComputedStyle(element);
    }

    var tagName = element.tagName.toLowerCase();
    var rect = getClientRect(element);
    if (rect.height > 0 && rect.width > 0) {
      return true;
    }

    if (tagName == 'path' && (rect.height > 0 || rect.width > 0)) {
      var strokeWidth = element.strokeWidth;
      return !!strokeWidth && (parseInt(strokeWidth, 10) > 0);
    }

    return style.overflow !== 'hidden' && Array.from(element.childNodes).some(
      n => (n.nodeType === Node.TEXT_NODE && !!filterText(n.nodeValue)) ||
      (n.nodeType === Node.ELEMENT_NODE &&
        positiveSize(n) && window.getComputedStyle(n).display !== 'none')
    );
  };

  var getOverflowState = function(element) {
    var region = getClientRect(element);
    var htmlElem = document.documentElement;
    var bodyElem = document.body;
    var htmlOverflowStyle = window.getComputedStyle(htmlElem).overflow;
    var treatAsFixedPosition;

    function getOverflowParent(e) {
      var position = window.getComputedStyle(e).position;
      if (position === 'fixed') {
        treatAsFixedPosition = true;
        return e == htmlElem ? null : htmlElem;
      } else {
        var parent = e.parentElement;

        while (parent && !canBeOverflowed(parent)) {
          parent = parent.parentElement;
        }

        return parent;
      }

      function canBeOverflowed(container) {
        if (container == htmlElem) {
          return true;
        }

        var style = window.getComputedStyle(container);
        var containerDisplay = style.display;
        if (containerDisplay.startsWith('inline')) {
          return false;
        }

        if (position === 'absolute' && style.position === 'static') {
          return false;
        }

        return true;
      }
    }

    function getOverflowStyles(e) {
      var overflowElem = e;
      if (htmlOverflowStyle === 'visible') {
        if (e == htmlElem && bodyElem) {
          overflowElem = bodyElem;
        } else if (e == bodyElem) {
          return {
            x: 'visible',
            y: 'visible'
          };
        }
      }

      var ostyle = window.getComputedStyle(overflowElem);
      var overflow = {
        x: ostyle.overflowX,
        y: ostyle.overflowY
      };

      if (e == htmlElem) {
        overflow.x = overflow.x === 'visible' ? 'auto' : overflow.x;
        overflow.y = overflow.y === 'visible' ? 'auto' : overflow.y;
      }

      return overflow;
    }

    function getScroll(e) {
      if (e == htmlElem) {
        return {
          x: htmlElem.scrollLeft,
          y: htmlElem.scrollTop
        };
      } else {
        return {
          x: e.scrollLeft,
          y: e.scrollTop
        };
      }
    }

    for (var container = getOverflowParent(element); !!container; container =
      getOverflowParent(container)) {
      var containerOverflow = getOverflowStyles(container);

      if (containerOverflow.x === 'visible' && containerOverflow.y ===
        'visible') {
        continue;
      }

      var containerRect = getClientRect(container);

      if (containerRect.width == 0 || containerRect.height == 0) {
        return 'hidden';
      }

      var underflowsX = region.right < containerRect.left;
      var underflowsY = region.bottom < containerRect.top;

      if ((underflowsX && containerOverflow.x === 'hidden') || (underflowsY &&
          containerOverflow.y === 'hidden')) {
        return 'hidden';
      } else if ((underflowsX && containerOverflow.x !== 'visible') || (
          underflowsY && containerOverflow.y !== 'visible')) {
        var containerScroll = getScroll(container);
        var unscrollableX = region.right < containerRect.left -
          containerScroll.x;
        var unscrollableY = region.bottom < containerRect.top -
          containerScroll.y;
        if ((unscrollableX && containerOverflow.x !== 'visible') || (
            unscrollableY && containerOverflow.x !== 'visible')) {
          return 'hidden';
        }

        var containerState = getOverflowState(container);
        return containerState === 'hidden' ? 'hidden' : 'scroll';
      }

      var overflowsX = region.left >= containerRect.left + containerRect.width;
      var overflowsY = region.top >= containerRect.top + containerRect.height;

      if ((overflowsX && containerOverflow.x === 'hidden') || (overflowsY &&
          containerOverflow.y === 'hidden')) {
        return 'hidden';
      } else if ((overflowsX && containerOverflow.x !== 'visible') || (
          overflowsY && containerOverflow.y !== 'visible')) {
        if (treatAsFixedPosition) {
          var docScroll = getScroll(container);
          if ((region.left >= htmlElem.scrollWidth - docScroll.x) || (
              region.right >= htmlElem.scrollHeight - docScroll.y)) {
            return 'hidden';
          }
        }

        var containerState = getOverflowState(container);
        return containerState === 'hidden' ? 'hidden' : 'scroll';
      }
    }

    return 'none';
  };

  function hiddenByOverflow(element) {
    return getOverflowState(element) === 'hidden' && Array.from(element.childNodes)
      .every(n => n.nodeType !== Node.ELEMENT_NODE || hiddenByOverflow(n) ||
        !positiveSize(n));
  }

  var tagName = element.tagName.toLowerCase();

  if (tagName === 'body') {
    return true;
  }

  if (tagName === 'input' && element.type.toLowerCase() === 'hidden') {
    return false;
  }

  if (tagName === 'noscript' || tagName === 'script' || tagName === 'style') {
    return false;
  }

  var style = window.getComputedStyle(element);

  if (style == null) {
    return false;
  }

  if (style.visibility === 'hidden' || style.visibility === 'collapse') {
    return false;
  }

  if (!displayed(element, style)) {
    return false;
  }

  if (getOpacity(element, style) === 0.0) {
    return false;
  }

  if (!positiveSize(element, style)) {
    return false;
  }

  return !hiddenByOverflow(element);
};

var isInteractable = function(element) {
  function isEnabled(element) {
    var disabledSupportElements = ['button', 'input', 'optgroup', 'option', 'select', 'textarea'];
    var tagName = element.tagName.toLowerCase();

    if (!disabledSupportElements.includes(tagName)) {
      return true;
    }

    if (element.getAttribute('disabled')) {
      return false;
    }

    if (element.parentElement && tagName === 'optgroup' || tagName === 'option') {
      return isEnabled(element.parentElement);
    }

    return true;
  }

  function arePointerEventsDisabled(element) {
    var style = window.getComputedStyle(element);
    if (!style) {
      return false;
    }

    return style.pointerEvents === 'none';
  }

  return isShown(element) && isEnabled(element) && !arePointerEventsDisabled(element);
};

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

var filterText = function(text) {
  return text.replace(/(\r\n|\n|\r)/gm, '').trim();
};

var isPixel = function(element) {
  var rect = element.getBoundingClientRect();
  var height = rect.bottom - rect.top;
  var width = rect.right - rect.left;

  return (height === 1 && width === 1);
};

var containsBlockElements = function(element, visibility = true) {
  for (var be of blockElements) {
    var children = Array.from(element.getElementsByTagName(be));
    if (visibility) {
      for (child of children){
        if (isShown(child))
          return true;
      }
    }
    else {
      return children.length > 0 ? true : false;
    }
  }

  return false;
};

var removeElement = function(array, element) {
  var index = array.indexOf(element);
  if (index > -1) {
    array.splice(index, 1);
    return array;
  } else {
    return array;
  }
};

var findElementWithParent = function(elements) {
  for (var i = 0; i < elements.length; i++) {
    var element = elements[i];
    var arr = elements.slice(0, i).concat(elements.slice(i + 1, elements.length));

    for (var other of arr) {
      if (other.contains(element)) {
        return {
          'element': elements[i],
          'parent': other
        };
      }
    }
  }

  return null;
};

var parentRemoval = function(elements, base) {
  var result = Array.from(elements);

  while (true) {
    var ep = findElementWithParent(result);

    if (ep) {
      if (base && ep.parent.tagName.toLowerCase() === base && ep.element
        .tagName.toLowerCase() !== ep.parent.tagName.toLowerCase()
      ) {
        result = removeElement(result, ep.element);
      } else {
        result = removeElement(result, ep.parent);
      }
    } else {
      break;
    }
  }

  return result;
};

var getElementsByXPath = function(xpath, parent, doc) {
  let results = [];
  let query = doc.evaluate(xpath,
    parent || doc,
    null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
  for (let i = 0, length = query.snapshotLength; i < length; ++i) {
    results.push(query.snapshotItem(i));
  }
  return results;
};

var getXPathTo = function(element) {
  if (element.tagName == 'HTML')
    return '/HTML[1]';
  if (element === document.body)
    return '/HTML[1]/BODY[1]';

  var ix = 0;
  var siblings = element.parentNode.childNodes;
  for (var i = 0; i < siblings.length; i++) {
    var sibling = siblings[i];
    if (sibling === element)
      return getXPathTo(element.parentNode) + '/' + element.tagName + '[' + (
        ix + 1) + ']';
    if (sibling.nodeType === 1 && sibling.tagName === element.tagName)
      ix++;
  }
};

var getChildren = function(n, skipMe) {
  var r = [];
  for (; n; n = n.nextSibling)
    if (n.nodeType === 1 && n != skipMe)
      r.push(n);
  return r;
};

var getSiblings = function(n) {
  return getChildren(n.parentNode.firstChild, n);
};


var best = function(iterable, by, isBetter) {
  let bestSoFar, bestKeySoFar;
  let isFirst = true;

  for (var item of iterable) {
    const key = by(item);
    if (isBetter(key, bestKeySoFar) || isFirst) {
      bestSoFar = item;
      bestKeySoFar = key;
      isFirst = false;
    }
  }

  if (isFirst) {
    throw new Error('Tried to call best() on empty iterable');
  }
  return bestSoFar;
};

var minC = function(iterable, by = identity) {
  return best(iterable, by, (a, b) => a < b);
};

var flattenDeep = function(arr1) {
  return arr1.reduce((acc, val) => Array.isArray(val) ? acc.concat(
    flattenDeep(val)) : acc.concat(val), []);
};

var isWhitespace = function(element) {
  return (element.nodeType === element.TEXT_NODE &&
    element.textContent.trim().length === 0);
};

/**
 * Return the number of stride nodes between 2 DOM nodes *at the same
 * level of the tree*, without going up or down the tree.
 *
 * ``left`` xor ``right`` may also be undefined.
 */
var numStrides = function(left, right) {
  let num = 0;

  // Walk right from left node until we hit the right node or run out:
  let sibling = left;
  let shouldContinue = sibling && sibling !== right;
  while (shouldContinue) {
    sibling = sibling.nextSibling;
    if ((shouldContinue = sibling && sibling !== right) &&
      !isWhitespace(sibling)) {
      num += 1;
    }
  }
  if (sibling !== right) { // Don't double-punish if left and right are siblings.
    // Walk left from right node:
    sibling = right;
    while (sibling) {
      sibling = sibling.previousSibling;
      if (sibling && !isWhitespace(sibling)) {
        num += 1;
      }
    }
  }
  return num;
};

/**
 * Return a topological distance between 2 DOM nodes or :term:`fnodes<fnode>`
 * weighted according to the similarity of their ancestry in the DOM. For
 * instance, if one node is situated inside ``<div><span><b><theNode>`` and the
 * other node is at ``<differentDiv><span><b><otherNode>``, they are considered
 * close to each other for clustering purposes. This is useful for picking out
 * nodes which have similar purposes.
 *
 * Return ``Number.MAX_VALUE`` if one of the nodes contains the other.
 *
 * This is largely an implementation detail of :func:`clusters`, but you can
 * call it yourself if you wish to implement your own clustering. Takes O(n log
 * n) time.
 *
 * Note that the default costs may change; pass them in explicitly if they are
 * important to you.
 *
 * @arg fnodeA {Node|Fnode}
 * @arg fnodeB {Node|Fnode}
 * @arg differentDepthCost {number} Cost for each level deeper one node is than
 *    the other below their common ancestor
 * @arg differentTagCost {number} Cost for a level below the common ancestor
 *    where tagNames differ
 * @arg sameTagCost {number} Cost for a level below the common ancestor where
 *    tagNames are the same
 * @arg strideCost {number} Cost for each stride node between A and B. Stride
 *     nodes are siblings or siblings-of-ancestors that lie between the 2
 *     nodes. These interposed nodes make it less likely that the 2 nodes
 *     should be together in a cluster.
 * @arg additionalCost {function} Return an additional cost, given 2 fnodes or
 *    nodes.
 *
 */
var distance = function(fnodeA,
  fnodeB, {
    differentDepthCost = 2,
    differentTagCost = 2,
    sameTagCost = 1,
    strideCost = 1,
    additionalCost = (fnodeA, fnodeB) => 0
  } = {}) {
  // I was thinking of something that adds little cost for siblings. Up
  // should probably be more expensive than down (see middle example in the
  // Nokia paper).

  // TODO: Test and tune default costs. They're off the cuff at the moment.

  if (fnodeA === fnodeB) {
    return 0;
  }

  const elementA = fnodeA;
  const elementB = fnodeB;

  // Stacks that go from the common ancestor all the way to A and B:
  const aAncestors = [elementA];
  const bAncestors = [elementB];

  let aAncestor = elementA;
  let bAncestor = elementB;

  // Ascend to common parent, stacking them up for later reference:
  while (!aAncestor.contains(elementB)) { // Note: an element does contain() itself.
    aAncestor = aAncestor.parentNode;
    aAncestors.push(aAncestor); //aAncestors = [a, b]. aAncestor = b // if a is outer: no loop here; aAncestors = [a]. aAncestor = a.
  }

  // In compareDocumentPosition()'s opinion, inside implies after. Basically,
  // before and after pertain to opening tags.
  const comparison = elementA.compareDocumentPosition(elementB);

  // If either contains the other, abort. We'd either return a misleading
  // number or else walk upward right out of the document while trying to
  // make the ancestor stack.
  if (comparison & (elementA.DOCUMENT_POSITION_CONTAINS | elementA.DOCUMENT_POSITION_CONTAINED_BY)) {
    return Number.MAX_VALUE;
  }
  // Make an ancestor stack for the right node too so we can walk
  // efficiently down to it:
  do {
    bAncestor = bAncestor.parentNode; // Assumes we've early-returned above if A === B. This walks upward from the outer node and up out of the tree. It STARTS OUT with aAncestor === bAncestor!
    bAncestors.push(bAncestor);
  } while (bAncestor !== aAncestor);

  // Figure out which node is left and which is right, so we can follow
  // sibling links in the appropriate directions when looking for stride
  // nodes:
  let left = aAncestors;
  let right = bAncestors;
  let cost = 0;
  if (comparison & elementA.DOCUMENT_POSITION_FOLLOWING) {
    // A is before, so it could contain the other node. What did I mean to do if one contained the other?
    left = aAncestors;
    right = bAncestors;
  } else if (comparison & elementA.DOCUMENT_POSITION_PRECEDING) {
    // A is after, so it might be contained by the other node.
    left = bAncestors;
    right = aAncestors;
  }

  // Descend to both nodes in parallel, discounting the traversal
  // cost iff the nodes we hit look similar, implying the nodes dwell
  // within similar structures.
  while (left.length || right.length) {
    const l = left.pop();
    const r = right.pop();
    if (l === undefined || r === undefined) {
      // Punishment for being at different depths: same as ordinary
      // dissimilarity punishment for now
      cost += differentDepthCost;
    } else {
      // TODO: Consider similarity of classList.
      cost += l.tagName === r.tagName ? sameTagCost : differentTagCost;
    }
    // Optimization: strides might be a good dimension to eliminate.
    if (strideCost !== 0) {
      cost += numStrides(l, r) * strideCost;
    }
  }

  return cost + additionalCost(fnodeA, fnodeB);
};

/**
 * Return the spatial distance between 2 fnodes, assuming a rendered page.
 *
 * Specifically, return the distance in pixels between the centers of
 * ``fnodeA.element.getBoundingClientRect()`` and
 * ``fnodeB.element.getBoundingClientRect()``.
 */
var euclidean = function(fnodeA, fnodeB) {
  /**
   * Return the horizontal distance from the left edge of the viewport to the
   * center of an element, given a DOMRect object for it. It doesn't matter
   * that the distance is affected by the page's scroll offset, since the 2
   * elements have the same offset.
   */
  function xCenter(domRect) {
    return domRect.left + domRect.width / 2;
  }

  function yCenter(domRect) {
    return domRect.top + domRect.height / 2;
  }

  const aRect = fnodeA.element.getBoundingClientRect();
  const bRect = fnodeB.element.getBoundingClientRect();
  return Math.sqrt((xCenter(aRect) - xCenter(bRect)) ** 2 +
    (yCenter(aRect) - yCenter(bRect)) ** 2);
};

/** A lower-triangular matrix of inter-cluster distances */
class DistanceMatrix {
  /**
   * @arg distance {function} Some notion of distance between 2 given nodes
   */
  constructor(elements, distance) {
    // A sparse adjacency matrix:
    // {A => {},
    //  B => {A => 4},
    //  C => {A => 4, B => 4},
    //  D => {A => 4, B => 4, C => 4}
    //  E => {A => 4, B => 4, C => 4, D => 4}}
    //
    // A, B, etc. are arrays of [arrays of arrays of...] nodes, each
    // array being a cluster. In this way, they not only accumulate a
    // cluster but retain the steps along the way.
    //
    // This is an efficient data structure in terms of CPU and memory, in
    // that we don't have to slide a lot of memory around when we delete a
    // row or column from the middle of the matrix while merging. Of
    // course, we lose some practical efficiency by using hash tables, and
    // maps in particular are slow in their early implementations.
    this._matrix = new Map();

    // Convert elements to clusters:
    const clusters = elements.map(el => [el]);

    // Init matrix:
    for (let outerCluster of clusters) {
      const innerMap = new Map();
      for (let innerCluster of this._matrix.keys()) {
        innerMap.set(innerCluster, distance(outerCluster[0],
          innerCluster[0]));
      }
      this._matrix.set(outerCluster, innerMap);
    }
    this._numClusters = clusters.length;
  }

  // Return (distance, a: clusterA, b: clusterB) of closest-together clusters.
  // Replace this to change linkage criterion.
  closest() {
    const self = this;

    if (this._numClusters < 2) {
      throw new Error(
        'There must be at least 2 clusters in order to return the closest() ones.'
      );
    }

    // Return the distances between every pair of clusters.
    function clustersAndDistances() {
      const ret = [];
      for (let [outerKey, row] of self._matrix.entries()) {
        for (let [innerKey, storedDistance] of row.entries()) {
          ret.push({
            a: outerKey,
            b: innerKey,
            distance: storedDistance
          });
        }
      }
      return ret;
    }
    // Optimizing this by inlining the loop and writing it less
    // functionally doesn't help:
    return minC(clustersAndDistances(), x => x.distance);
  }

  // Look up the distance between 2 clusters in me. Try the lookup in the
  // other direction if the first one falls in the nonexistent half of the
  // triangle.
  _cachedDistance(clusterA, clusterB) {
    let ret = this._matrix.get(clusterA).get(clusterB);
    if (ret === undefined) {
      ret = this._matrix.get(clusterB).get(clusterA);
    }
    return ret;
  }

  // Merge two clusters.
  merge(clusterA, clusterB) {
    // An example showing how rows merge:
    //  A: {}
    //  B: {A: 1}
    //  C: {A: 4, B: 4},
    //  D: {A: 4, B: 4, C: 4}
    //  E: {A: 4, B: 4, C: 2, D: 4}}
    //
    // Step 2:
    //  C: {}
    //  D: {C: 4}
    //  E: {C: 2, D: 4}}
    //  AB: {C: 4, D: 4, E: 4}
    //
    // Step 3:
    //  D:  {}
    //  AB: {D: 4}
    //  CE: {D: 4, AB: 4}

    // Construct new row, finding min distances from either subcluster of
    // the new cluster to old clusters.
    //
    // There will be no repetition in the matrix because, after all,
    // nothing pointed to this new cluster before it existed.
    const newRow = new Map();
    for (let outerKey of this._matrix.keys()) {
      if (outerKey !== clusterA && outerKey !== clusterB) {
        newRow.set(outerKey, Math.min(this._cachedDistance(clusterA, outerKey),
          this._cachedDistance(clusterB, outerKey)));
      }
    }

    // Delete the rows of the clusters we're merging.
    this._matrix.delete(clusterA);
    this._matrix.delete(clusterB);

    // Remove inner refs to the clusters we're merging.
    for (let inner of this._matrix.values()) {
      inner.delete(clusterA);
      inner.delete(clusterB);
    }

    // Attach new row.
    this._matrix.set([clusterA, clusterB], newRow);

    // There is a net decrease of 1 cluster:
    this._numClusters -= 1;
  }

  numClusters() {
    return this._numClusters;
  }

  // Return an Array of nodes for each cluster in me.
  clusters() {
    // TODO: Can't get wu.map to work here. Don't know why.
    var result = [];

    for (var k of this._matrix.keys()) {
      result.push(flattenDeep(k));
    }

    return result;
  }
};

/**
 * Partition the given nodes into one or more clusters by position in the DOM
 * tree.
 *
 * This implements an agglomerative clustering. It uses single linkage, since
 * we're talking about adjacency here more than Euclidean proximity: the
 * clusters we're talking about in the DOM will tend to be adjacent, not
 * overlapping. We haven't tried other linkage criteria yet.
 *
 * In a later release, we may consider score or notes.
 *
 * @arg {Fnode[]|Node[]} fnodes :term:`fnodes<fnode>` or DOM nodes to group
 *     into clusters
 * @arg {number} splittingDistance The closest-nodes :func:`distance` beyond
 *     which we will not attempt to unify 2 clusters. Make this larger to make
 *     larger clusters.
 * @arg getDistance {function} A function that returns some notion of numerical
 *    distance between 2 nodes. Default: :func:`distance`
 * @return {Array} An Array of Arrays, with each Array containing all the
 *     nodes in one cluster. Note that neither the clusters nor the nodes are
 *     in any particular order. You may find :func:`domSort` helpful to remedy
 *     the latter.
 */
var clusters = function(fnodes, splittingDistance, getDistance = distance) {
  const matrix = new DistanceMatrix(fnodes, getDistance);
  let closest;

  while (matrix.numClusters() > 1 && (closest = matrix.closest()).distance <
    splittingDistance) {
    matrix.merge(closest.a, closest.b);
  }

  return matrix.clusters();
};

/*! URI.js v1.19.1 http://medialize.github.io/URI.js/ */
/* build contains: SecondLevelDomains.js, URI.js, URITemplate.js */
/*
 URI.js - Mutating URLs
 Second Level Domain (SLD) Support

 Version: 1.19.1

 Author: Rodney Rehm
 Web: http://medialize.github.io/URI.js/

 Licensed under
   MIT License http://www.opensource.org/licenses/mit-license

 URI.js - Mutating URLs

 Version: 1.19.1

 Author: Rodney Rehm
 Web: http://medialize.github.io/URI.js/

 Licensed under
   MIT License http://www.opensource.org/licenses/mit-license

 URI.js - Mutating URLs
 URI Template Support - http://tools.ietf.org/html/rfc6570

 Version: 1.19.1

 Author: Rodney Rehm
 Web: http://medialize.github.io/URI.js/

 Licensed under
   MIT License http://www.opensource.org/licenses/mit-license

*/
(function(f, n) {
  "object" === typeof module && module.exports ? module.exports = n() :
    "function" === typeof define && define.amd ? define(n) : f
    .SecondLevelDomains = n(f)
})(this, function(f) {
  var n = f && f.SecondLevelDomains,
    k = {
      list: {
        ac: " com gov mil net org ",
        ae: " ac co gov mil name net org pro sch ",
        af: " com edu gov net org ",
        al: " com edu gov mil net org ",
        ao: " co ed gv it og pb ",
        ar: " com edu gob gov int mil net org tur ",
        at: " ac co gv or ",
        au: " asn com csiro edu gov id net org ",
        ba: " co com edu gov mil net org rs unbi unmo unsa untz unze ",
        bb: " biz co com edu gov info net org store tv ",
        bh: " biz cc com edu gov info net org ",
        bn: " com edu gov net org ",
        bo: " com edu gob gov int mil net org tv ",
        br: " adm adv agr am arq art ato b bio blog bmd cim cng cnt com coop ecn edu eng esp etc eti far flog fm fnd fot fst g12 ggf gov imb ind inf jor jus lel mat med mil mus net nom not ntr odo org ppg pro psc psi qsl rec slg srv tmp trd tur tv vet vlog wiki zlg ",
        bs: " com edu gov net org ",
        bz: " du et om ov rg ",
        ca: " ab bc mb nb nf nl ns nt nu on pe qc sk yk ",
        ck: " biz co edu gen gov info net org ",
        cn: " ac ah bj com cq edu fj gd gov gs gx gz ha hb he hi hl hn jl js jx ln mil net nm nx org qh sc sd sh sn sx tj tw xj xz yn zj ",
        co: " com edu gov mil net nom org ",
        cr: " ac c co ed fi go or sa ",
        cy: " ac biz com ekloges gov ltd name net org parliament press pro tm ",
        "do": " art com edu gob gov mil net org sld web ",
        dz: " art asso com edu gov net org pol ",
        ec: " com edu fin gov info med mil net org pro ",
        eg: " com edu eun gov mil name net org sci ",
        er: " com edu gov ind mil net org rochest w ",
        es: " com edu gob nom org ",
        et: " biz com edu gov info name net org ",
        fj: " ac biz com info mil name net org pro ",
        fk: " ac co gov net nom org ",
        fr: " asso com f gouv nom prd presse tm ",
        gg: " co net org ",
        gh: " com edu gov mil org ",
        gn: " ac com gov net org ",
        gr: " com edu gov mil net org ",
        gt: " com edu gob ind mil net org ",
        gu: " com edu gov net org ",
        hk: " com edu gov idv net org ",
        hu: " 2000 agrar bolt casino city co erotica erotika film forum games hotel info ingatlan jogasz konyvelo lakas media news org priv reklam sex shop sport suli szex tm tozsde utazas video ",
        id: " ac co go mil net or sch web ",
        il: " ac co gov idf k12 muni net org ",
        "in": " ac co edu ernet firm gen gov i ind mil net nic org res ",
        iq: " com edu gov i mil net org ",
        ir: " ac co dnssec gov i id net org sch ",
        it: " edu gov ",
        je: " co net org ",
        jo: " com edu gov mil name net org sch ",
        jp: " ac ad co ed go gr lg ne or ",
        ke: " ac co go info me mobi ne or sc ",
        kh: " com edu gov mil net org per ",
        ki: " biz com de edu gov info mob net org tel ",
        km: " asso com coop edu gouv k medecin mil nom notaires pharmaciens presse tm veterinaire ",
        kn: " edu gov net org ",
        kr: " ac busan chungbuk chungnam co daegu daejeon es gangwon go gwangju gyeongbuk gyeonggi gyeongnam hs incheon jeju jeonbuk jeonnam k kg mil ms ne or pe re sc seoul ulsan ",
        kw: " com edu gov net org ",
        ky: " com edu gov net org ",
        kz: " com edu gov mil net org ",
        lb: " com edu gov net org ",
        lk: " assn com edu gov grp hotel int ltd net ngo org sch soc web ",
        lr: " com edu gov net org ",
        lv: " asn com conf edu gov id mil net org ",
        ly: " com edu gov id med net org plc sch ",
        ma: " ac co gov m net org press ",
        mc: " asso tm ",
        me: " ac co edu gov its net org priv ",
        mg: " com edu gov mil nom org prd tm ",
        mk: " com edu gov inf name net org pro ",
        ml: " com edu gov net org presse ",
        mn: " edu gov org ",
        mo: " com edu gov net org ",
        mt: " com edu gov net org ",
        mv: " aero biz com coop edu gov info int mil museum name net org pro ",
        mw: " ac co com coop edu gov int museum net org ",
        mx: " com edu gob net org ",
        my: " com edu gov mil name net org sch ",
        nf: " arts com firm info net other per rec store web ",
        ng: " biz com edu gov mil mobi name net org sch ",
        ni: " ac co com edu gob mil net nom org ",
        np: " com edu gov mil net org ",
        nr: " biz com edu gov info net org ",
        om: " ac biz co com edu gov med mil museum net org pro sch ",
        pe: " com edu gob mil net nom org sld ",
        ph: " com edu gov i mil net ngo org ",
        pk: " biz com edu fam gob gok gon gop gos gov net org web ",
        pl: " art bialystok biz com edu gda gdansk gorzow gov info katowice krakow lodz lublin mil net ngo olsztyn org poznan pwr radom slupsk szczecin torun warszawa waw wroc wroclaw zgora ",
        pr: " ac biz com edu est gov info isla name net org pro prof ",
        ps: " com edu gov net org plo sec ",
        pw: " belau co ed go ne or ",
        ro: " arts com firm info nom nt org rec store tm www ",
        rs: " ac co edu gov in org ",
        sb: " com edu gov net org ",
        sc: " com edu gov net org ",
        sh: " co com edu gov net nom org ",
        sl: " com edu gov net org ",
        st: " co com consulado edu embaixada gov mil net org principe saotome store ",
        sv: " com edu gob org red ",
        sz: " ac co org ",
        tr: " av bbs bel biz com dr edu gen gov info k12 name net org pol tel tsk tv web ",
        tt: " aero biz cat co com coop edu gov info int jobs mil mobi museum name net org pro tel travel ",
        tw: " club com ebiz edu game gov idv mil net org ",
        mu: " ac co com gov net or org ",
        mz: " ac co edu gov org ",
        na: " co com ",
        nz: " ac co cri geek gen govt health iwi maori mil net org parliament school ",
        pa: " abo ac com edu gob ing med net nom org sld ",
        pt: " com edu gov int net nome org publ ",
        py: " com edu gov mil net org ",
        qa: " com edu gov mil net org ",
        re: " asso com nom ",
        ru: " ac adygeya altai amur arkhangelsk astrakhan bashkiria belgorod bir bryansk buryatia cbg chel chelyabinsk chita chukotka chuvashia com dagestan e-burg edu gov grozny int irkutsk ivanovo izhevsk jar joshkar-ola kalmykia kaluga kamchatka karelia kazan kchr kemerovo khabarovsk khakassia khv kirov koenig komi kostroma kranoyarsk kuban kurgan kursk lipetsk magadan mari mari-el marine mil mordovia mosreg msk murmansk nalchik net nnov nov novosibirsk nsk omsk orenburg org oryol penza perm pp pskov ptz rnd ryazan sakhalin samara saratov simbirsk smolensk spb stavropol stv surgut tambov tatarstan tom tomsk tsaritsyn tsk tula tuva tver tyumen udm udmurtia ulan-ude vladikavkaz vladimir vladivostok volgograd vologda voronezh vrn vyatka yakutia yamal yekaterinburg yuzhno-sakhalinsk ",
        rw: " ac co com edu gouv gov int mil net ",
        sa: " com edu gov med net org pub sch ",
        sd: " com edu gov info med net org tv ",
        se: " a ac b bd c d e f g h i k l m n o org p parti pp press r s t tm u w x y z ",
        sg: " com edu gov idn net org per ",
        sn: " art com edu gouv org perso univ ",
        sy: " com edu gov mil net news org ",
        th: " ac co go in mi net or ",
        tj: " ac biz co com edu go gov info int mil name net nic org test web ",
        tn: " agrinet com defense edunet ens fin gov ind info intl mincom nat net org perso rnrt rns rnu tourism ",
        tz: " ac co go ne or ",
        ua: " biz cherkassy chernigov chernovtsy ck cn co com crimea cv dn dnepropetrovsk donetsk dp edu gov if in ivano-frankivsk kh kharkov kherson khmelnitskiy kiev kirovograd km kr ks kv lg lugansk lutsk lviv me mk net nikolaev od odessa org pl poltava pp rovno rv sebastopol sumy te ternopil uzhgorod vinnica vn zaporizhzhe zhitomir zp zt ",
        ug: " ac co go ne or org sc ",
        uk: " ac bl british-library co cym gov govt icnet jet lea ltd me mil mod national-library-scotland nel net nhs nic nls org orgn parliament plc police sch scot soc ",
        us: " dni fed isa kids nsn ",
        uy: " com edu gub mil net org ",
        ve: " co com edu gob info mil net org web ",
        vi: " co com k12 net org ",
        vn: " ac biz com edu gov health info int name net org pro ",
        ye: " co com gov ltd me net org plc ",
        yu: " ac co edu gov org ",
        za: " ac agric alt bourse city co cybernet db edu gov grondar iaccess imt inca landesign law mil net ngo nis nom olivetti org pix school tm web ",
        zm: " ac co com edu gov net org sch ",
        com: "ar br cn de eu gb gr hu jpn kr no qc ru sa se uk us uy za ",
        net: "gb jp se uk ",
        org: "ae",
        de: "com "
      },
      has: function(f) {
        var c = f.lastIndexOf(".");
        if (0 >= c || c >= f.length - 1) return !1;
        var p = f.lastIndexOf(".", c - 1);
        if (0 >= p || p >= c - 1) return !1;
        var n = k.list[f.slice(c + 1)];
        return n ? 0 <= n.indexOf(" " + f.slice(p + 1, c) + " ") : !1
      },
      is: function(f) {
        var c = f.lastIndexOf(".");
        if (0 >= c || c >= f.length - 1 || 0 <= f.lastIndexOf(".", c - 1))
          return !1;
        var p = k.list[f.slice(c + 1)];
        return p ? 0 <= p.indexOf(" " + f.slice(0, c) + " ") : !1
      },
      get: function(f) {
        var c = f.lastIndexOf(".");
        if (0 >= c || c >= f.length - 1) return null;
        var n = f.lastIndexOf(".", c - 1);
        if (0 >= n || n >= c - 1) return null;
        var p = k.list[f.slice(c + 1)];
        return !p || 0 > p.indexOf(" " + f.slice(n + 1, c) + " ") ? null : f
          .slice(n + 1)
      },
      noConflict: function() {
        f.SecondLevelDomains === this && (f.SecondLevelDomains = n);
        return this
      }
    };
  return k
});
(function(f, n) {
  "object" === typeof module && module.exports ? module.exports = n(require(
      "./punycode"), require("./IPv6"), require("./SecondLevelDomains")) :
    "function" === typeof define && define.amd ? define(["./punycode",
      "./IPv6", "./SecondLevelDomains"
    ], n) : f.URI = n(f.punycode, f.IPv6, f.SecondLevelDomains, f)
})(this, function(f, n, k, p) {
  function c(a, b) {
    var d = 1 <= arguments.length,
      h = 2 <= arguments.length;
    if (!(this instanceof c)) return d ? h ? new c(a, b) : new c(a) : new c;
    if (void 0 === a) {
      if (d) throw new TypeError("undefined is not a valid argument for URI");
      a = "undefined" !== typeof location ? location.href + "" : ""
    }
    if (null === a && d) throw new TypeError(
      "null is not a valid argument for URI");
    this.href(a);
    return void 0 !== b ? this.absoluteTo(b) : this
  }

  function A(a) {
    return a.replace(/([.*+?^=!:${}()|[\]\/\\])/g, "\\$1")
  }

  function z(a) {
    return void 0 === a ? "Undefined" : String(Object.prototype.toString.call(
      a)).slice(8, -1)
  }

  function w(a) {
    return "Array" === z(a)
  }

  function g(a, b) {
    var d = {},
      c;
    if ("RegExp" === z(b)) d = null;
    else if (w(b)) {
      var l = 0;
      for (c = b.length; l < c; l++) d[b[l]] = !0
    } else d[b] = !0;
    l = 0;
    for (c = a.length; l < c; l++)
      if (d && void 0 !== d[a[l]] || !d && b.test(a[l])) a.splice(l, 1), c--,
        l--;
    return a
  }

  function q(a, b) {
    var d;
    if (w(b)) {
      var c = 0;
      for (d = b.length; c < d; c++)
        if (!q(a, b[c])) return !1;
      return !0
    }
    var l = z(b);
    c = 0;
    for (d = a.length; c < d; c++)
      if ("RegExp" === l) {
        if ("string" === typeof a[c] && a[c].match(b)) return !0
      } else if (a[c] === b) return !0;
    return !1
  }

  function x(a, b) {
    if (!w(a) || !w(b) || a.length !== b.length) return !1;
    a.sort();
    b.sort();
    for (var d = 0, c = a.length; d < c; d++)
      if (a[d] !== b[d]) return !1;
    return !0
  }

  function y(a) {
    return a.replace(/^\/+|\/+$/g,
      "")
  }

  function E(a) {
    return escape(a)
  }

  function C(a) {
    return encodeURIComponent(a).replace(/[!'()*]/g, E).replace(/\*/g, "%2A")
  }

  function m(a) {
    return function(b, d) {
      if (void 0 === b) return this._parts[a] || "";
      this._parts[a] = b || null;
      this.build(!d);
      return this
    }
  }

  function B(a, b) {
    return function(d, c) {
      if (void 0 === d) return this._parts[a] || "";
      null !== d && (d += "", d.charAt(0) === b && (d = d.substring(1)));
      this._parts[a] = d;
      this.build(!c);
      return this
    }
  }
  var t = p && p.URI;
  c.version = "1.19.1";
  var e = c.prototype,
    r = Object.prototype.hasOwnProperty;
  c._parts = function() {
    return {
      protocol: null,
      username: null,
      password: null,
      hostname: null,
      urn: null,
      port: null,
      path: null,
      query: null,
      fragment: null,
      preventInvalidHostname: c.preventInvalidHostname,
      duplicateQueryParameters: c.duplicateQueryParameters,
      escapeQuerySpace: c.escapeQuerySpace
    }
  };
  c.preventInvalidHostname = !1;
  c.duplicateQueryParameters = !1;
  c.escapeQuerySpace = !0;
  c.protocol_expression = /^[a-z][a-z0-9.+-]*$/i;
  c.idn_expression = /[^a-z0-9\._-]/i;
  c.punycode_expression = /(xn--)/i;
  c.ip4_expression = /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/;
  c.ip6_expression =
    /^\s*((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))(%.+)?\s*$/;
  c.find_uri_expression =
    /\b((?:[a-z][\w-]+:(?:\/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}\/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?\u00ab\u00bb\u201c\u201d\u2018\u2019]))/ig;
  c.findUri = {
    start: /\b(?:([a-z][a-z0-9.+-]*:\/\/)|www\.)/gi,
    end: /[\s\r\n]|$/,
    trim: /[`!()\[\]{};:'".,<>?\u00ab\u00bb\u201c\u201d\u201e\u2018\u2019]+$/,
    parens: /(\([^\)]*\)|\[[^\]]*\]|\{[^}]*\}|<[^>]*>)/g
  };
  c.defaultPorts = {
    http: "80",
    https: "443",
    ftp: "21",
    gopher: "70",
    ws: "80",
    wss: "443"
  };
  c.hostProtocols = ["http", "https"];
  c.invalid_hostname_characters = /[^a-zA-Z0-9\.\-:_]/;
  c.domAttributes = {
    a: "href",
    blockquote: "cite",
    link: "href",
    base: "href",
    script: "src",
    form: "action",
    img: "src",
    area: "href",
    iframe: "src",
    embed: "src",
    source: "src",
    track: "src",
    input: "src",
    audio: "src",
    video: "src"
  };
  c.getDomAttribute = function(a) {
    if (a && a.nodeName) {
      var b = a.nodeName.toLowerCase();
      if ("input" !== b || "image" === a.type) return c.domAttributes[b]
    }
  };
  c.encode = C;
  c.decode = decodeURIComponent;
  c.iso8859 =
    function() {
      c.encode = escape;
      c.decode = unescape
    };
  c.unicode = function() {
    c.encode = C;
    c.decode = decodeURIComponent
  };
  c.characters = {
    pathname: {
      encode: {
        expression: /%(24|26|2B|2C|3B|3D|3A|40)/ig,
        map: {
          "%24": "$",
          "%26": "&",
          "%2B": "+",
          "%2C": ",",
          "%3B": ";",
          "%3D": "=",
          "%3A": ":",
          "%40": "@"
        }
      },
      decode: {
        expression: /[\/\?#]/g,
        map: {
          "/": "%2F",
          "?": "%3F",
          "#": "%23"
        }
      }
    },
    reserved: {
      encode: {
        expression: /%(21|23|24|26|27|28|29|2A|2B|2C|2F|3A|3B|3D|3F|40|5B|5D)/ig,
        map: {
          "%3A": ":",
          "%2F": "/",
          "%3F": "?",
          "%23": "#",
          "%5B": "[",
          "%5D": "]",
          "%40": "@",
          "%21": "!",
          "%24": "$",
          "%26": "&",
          "%27": "'",
          "%28": "(",
          "%29": ")",
          "%2A": "*",
          "%2B": "+",
          "%2C": ",",
          "%3B": ";",
          "%3D": "="
        }
      }
    },
    urnpath: {
      encode: {
        expression: /%(21|24|27|28|29|2A|2B|2C|3B|3D|40)/ig,
        map: {
          "%21": "!",
          "%24": "$",
          "%27": "'",
          "%28": "(",
          "%29": ")",
          "%2A": "*",
          "%2B": "+",
          "%2C": ",",
          "%3B": ";",
          "%3D": "=",
          "%40": "@"
        }
      },
      decode: {
        expression: /[\/\?#:]/g,
        map: {
          "/": "%2F",
          "?": "%3F",
          "#": "%23",
          ":": "%3A"
        }
      }
    }
  };
  c.encodeQuery = function(a, b) {
    var d = c.encode(a + "");
    void 0 === b && (b = c.escapeQuerySpace);
    return b ? d.replace(/%20/g, "+") : d
  };
  c.decodeQuery =
    function(a, b) {
      a += "";
      void 0 === b && (b = c.escapeQuerySpace);
      try {
        return c.decode(b ? a.replace(/\+/g, "%20") : a)
      } catch (d) {
        return a
      }
    };
  var u = {
      encode: "encode",
      decode: "decode"
    },
    v, D = function(a, b) {
      return function(d) {
        try {
          return c[b](d + "").replace(c.characters[a][b].expression,
            function(d) {
              return c.characters[a][b].map[d]
            })
        } catch (h) {
          return d
        }
      }
    };
  for (v in u) c[v + "PathSegment"] = D("pathname", u[v]), c[v +
    "UrnPathSegment"] = D("urnpath", u[v]);
  u = function(a, b, d) {
    return function(h) {
      var l = d ? function(a) {
        return c[b](c[d](a))
      } : c[b];
      h = (h + "").split(a);
      for (var e = 0, g = h.length; e < g; e++) h[e] = l(h[e]);
      return h.join(a)
    }
  };
  c.decodePath = u("/", "decodePathSegment");
  c.decodeUrnPath = u(":", "decodeUrnPathSegment");
  c.recodePath = u("/", "encodePathSegment", "decode");
  c.recodeUrnPath = u(":", "encodeUrnPathSegment", "decode");
  c.encodeReserved = D("reserved", "encode");
  c.parse = function(a, b) {
    b || (b = {
      preventInvalidHostname: c.preventInvalidHostname
    });
    var d = a.indexOf("#"); - 1 < d && (b.fragment = a.substring(d + 1) ||
      null, a = a.substring(0, d));
    d = a.indexOf("?"); - 1 < d && (b.query =
      a.substring(d + 1) || null, a = a.substring(0, d));
    "//" === a.substring(0, 2) ? (b.protocol = null, a = a.substring(2), a =
      c.parseAuthority(a, b)) : (d = a.indexOf(":"), -1 < d && (b
      .protocol = a.substring(0, d) || null, b.protocol && !b.protocol
      .match(c.protocol_expression) ? b.protocol = void 0 : "//" === a
      .substring(d + 1, d + 3) ? (a = a.substring(d + 3), a = c
        .parseAuthority(a, b)) : (a = a.substring(d + 1), b.urn = !0)));
    b.path = a;
    return b
  };
  c.parseHost = function(a, b) {
    a || (a = "");
    a = a.replace(/\\/g, "/");
    var d = a.indexOf("/"); - 1 === d && (d = a.length);
    if ("[" === a.charAt(0)) {
      var h =
        a.indexOf("]");
      b.hostname = a.substring(1, h) || null;
      b.port = a.substring(h + 2, d) || null;
      "/" === b.port && (b.port = null)
    } else {
      var l = a.indexOf(":");
      h = a.indexOf("/");
      l = a.indexOf(":", l + 1); - 1 !== l && (-1 === h || l < h) ? (b
        .hostname = a.substring(0, d) || null, b.port = null) : (h = a
        .substring(0, d).split(":"), b.hostname = h[0] || null, b.port =
        h[1] || null)
    }
    b.hostname && "/" !== a.substring(d).charAt(0) && (d++, a = "/" + a);
    b.preventInvalidHostname && c.ensureValidHostname(b.hostname, b
      .protocol);
    b.port && c.ensureValidPort(b.port);
    return a.substring(d) ||
      "/"
  };
  c.parseAuthority = function(a, b) {
    a = c.parseUserinfo(a, b);
    return c.parseHost(a, b)
  };
  c.parseUserinfo = function(a, b) {
    var d = a.indexOf("/"),
      h = a.lastIndexOf("@", -1 < d ? d : a.length - 1); - 1 < h && (-1 ===
      d || h < d) ? (d = a.substring(0, h).split(":"), b.username = d[0] ?
      c.decode(d[0]) : null, d.shift(), b.password = d[0] ? c.decode(d
        .join(":")) : null, a = a.substring(h + 1)) : (b.username = null,
      b.password = null);
    return a
  };
  c.parseQuery = function(a, b) {
    if (!a) return {};
    a = a.replace(/&+/g, "&").replace(/^\?*&*|&+$/g, "");
    if (!a) return {};
    for (var d = {}, h = a.split("&"),
        l = h.length, e, g, f = 0; f < l; f++)
      if (e = h[f].split("="), g = c.decodeQuery(e.shift(), b), e = e
        .length ? c.decodeQuery(e.join("="), b) : null, r.call(d, g)) {
        if ("string" === typeof d[g] || null === d[g]) d[g] = [d[g]];
        d[g].push(e)
      } else d[g] = e;
    return d
  };
  c.build = function(a) {
    var b = "";
    a.protocol && (b += a.protocol + ":");
    a.urn || !b && !a.hostname || (b += "//");
    b += c.buildAuthority(a) || "";
    "string" === typeof a.path && ("/" !== a.path.charAt(0) && "string" ===
      typeof a.hostname && (b += "/"), b += a.path);
    "string" === typeof a.query && a.query && (b += "?" + a.query);
    "string" ===
    typeof a.fragment && a.fragment && (b += "#" + a.fragment);
    return b
  };
  c.buildHost = function(a) {
    var b = "";
    if (a.hostname) b = c.ip6_expression.test(a.hostname) ? b + ("[" + a
      .hostname + "]") : b + a.hostname;
    else return "";
    a.port && (b += ":" + a.port);
    return b
  };
  c.buildAuthority = function(a) {
    return c.buildUserinfo(a) + c.buildHost(a)
  };
  c.buildUserinfo = function(a) {
    var b = "";
    a.username && (b += c.encode(a.username));
    a.password && (b += ":" + c.encode(a.password));
    b && (b += "@");
    return b
  };
  c.buildQuery = function(a, b, d) {
    var h = "",
      l, e;
    for (l in a)
      if (r.call(a,
          l) && l)
        if (w(a[l])) {
          var g = {};
          var f = 0;
          for (e = a[l].length; f < e; f++) void 0 !== a[l][f] && void 0 ===
            g[a[l][f] + ""] && (h += "&" + c.buildQueryParameter(l, a[l][f],
              d), !0 !== b && (g[a[l][f] + ""] = !0))
        } else void 0 !== a[l] && (h += "&" + c.buildQueryParameter(l, a[l],
          d));
    return h.substring(1)
  };
  c.buildQueryParameter = function(a, b, d) {
    return c.encodeQuery(a, d) + (null !== b ? "=" + c.encodeQuery(b, d) :
      "")
  };
  c.addQuery = function(a, b, d) {
    if ("object" === typeof b)
      for (var h in b) r.call(b, h) && c.addQuery(a, h, b[h]);
    else if ("string" === typeof b) void 0 === a[b] ?
      a[b] = d : ("string" === typeof a[b] && (a[b] = [a[b]]), w(d) || (
        d = [d]), a[b] = (a[b] || []).concat(d));
    else throw new TypeError(
      "URI.addQuery() accepts an object, string as the name parameter");
  };
  c.setQuery = function(a, b, d) {
    if ("object" === typeof b)
      for (var h in b) r.call(b, h) && c.setQuery(a, h, b[h]);
    else if ("string" === typeof b) a[b] = void 0 === d ? null : d;
    else throw new TypeError(
      "URI.setQuery() accepts an object, string as the name parameter");
  };
  c.removeQuery = function(a, b, d) {
    var h;
    if (w(b))
      for (d = 0, h = b.length; d < h; d++) a[b[d]] =
        void 0;
    else if ("RegExp" === z(b))
      for (h in a) b.test(h) && (a[h] = void 0);
    else if ("object" === typeof b)
      for (h in b) r.call(b, h) && c.removeQuery(a, h, b[h]);
    else if ("string" === typeof b) void 0 !== d ? "RegExp" === z(d) ? !w(a[
        b]) && d.test(a[b]) ? a[b] = void 0 : a[b] = g(a[b], d) : a[b] !==
      String(d) || w(d) && 1 !== d.length ? w(a[b]) && (a[b] = g(a[b], d)) :
      a[b] = void 0 : a[b] = void 0;
    else throw new TypeError(
      "URI.removeQuery() accepts an object, string, RegExp as the first parameter"
      );
  };
  c.hasQuery = function(a, b, d, h) {
    switch (z(b)) {
      case "String":
        break;
      case "RegExp":
        for (var l in a)
          if (r.call(a, l) && b.test(l) && (void 0 === d || c.hasQuery(a, l,
              d))) return !0;
        return !1;
      case "Object":
        for (var e in b)
          if (r.call(b, e) && !c.hasQuery(a, e, b[e])) return !1;
        return !0;
      default:
        throw new TypeError(
          "URI.hasQuery() accepts a string, regular expression or object as the name parameter"
          );
    }
    switch (z(d)) {
      case "Undefined":
        return b in a;
      case "Boolean":
        return a = !(w(a[b]) ? !a[b].length : !a[b]), d === a;
      case "Function":
        return !!d(a[b], b, a);
      case "Array":
        return w(a[b]) ? (h ? q : x)(a[b], d) : !1;
      case "RegExp":
        return w(a[b]) ?
          h ? q(a[b], d) : !1 : !(!a[b] || !a[b].match(d));
      case "Number":
        d = String(d);
      case "String":
        return w(a[b]) ? h ? q(a[b], d) : !1 : a[b] === d;
      default:
        throw new TypeError(
          "URI.hasQuery() accepts undefined, boolean, string, number, RegExp, Function as the value parameter"
          );
    }
  };
  c.joinPaths = function() {
    for (var a = [], b = [], d = 0, h = 0; h < arguments.length; h++) {
      var l = new c(arguments[h]);
      a.push(l);
      l = l.segment();
      for (var e = 0; e < l.length; e++) "string" === typeof l[e] && b.push(
        l[e]), l[e] && d++
    }
    if (!b.length || !d) return new c("");
    b = (new c("")).segment(b);
    "" !== a[0].path() && "/" !== a[0].path().slice(0, 1) || b.path("/" + b
      .path());
    return b.normalize()
  };
  c.commonPath = function(a, b) {
    var d = Math.min(a.length, b.length),
      c;
    for (c = 0; c < d; c++)
      if (a.charAt(c) !== b.charAt(c)) {
        c--;
        break
      } if (1 > c) return a.charAt(0) === b.charAt(0) && "/" === a.charAt(
      0) ? "/" : "";
    if ("/" !== a.charAt(c) || "/" !== b.charAt(c)) c = a.substring(0, c)
      .lastIndexOf("/");
    return a.substring(0, c + 1)
  };
  c.withinString = function(a, b, d) {
    d || (d = {});
    var h = d.start || c.findUri.start,
      l = d.end || c.findUri.end,
      e = d.trim || c.findUri.trim,
      g =
      d.parens || c.findUri.parens,
      f = /[a-z0-9-]=["']?$/i;
    for (h.lastIndex = 0;;) {
      var q = h.exec(a);
      if (!q) break;
      var k = q.index;
      if (d.ignoreHtml) {
        var m = a.slice(Math.max(k - 3, 0), k);
        if (m && f.test(m)) continue
      }
      var y = k + a.slice(k).search(l);
      m = a.slice(k, y);
      for (y = -1;;) {
        var n = g.exec(m);
        if (!n) break;
        y = Math.max(y, n.index + n[0].length)
      }
      m = -1 < y ? m.slice(0, y) + m.slice(y).replace(e, "") : m.replace(e,
        "");
      m.length <= q[0].length || d.ignore && d.ignore.test(m) || (y = k + m
        .length, q = b(m, k, y, a), void 0 === q ? h.lastIndex = y : (q =
          String(q), a = a.slice(0, k) + q + a.slice(y),
          h.lastIndex = k + q.length))
    }
    h.lastIndex = 0;
    return a
  };
  c.ensureValidHostname = function(a, b) {
    var d = !!a,
      h = !1;
    b && (h = q(c.hostProtocols, b));
    if (h && !d) throw new TypeError(
      "Hostname cannot be empty, if protocol is " + b);
    if (a && a.match(c.invalid_hostname_characters)) {
      if (!f) throw new TypeError('Hostname "' + a +
        '" contains characters other than [A-Z0-9.-:_] and Punycode.js is not available'
        );
      if (f.toASCII(a).match(c.invalid_hostname_characters))
      throw new TypeError('Hostname "' + a +
          '" contains characters other than [A-Z0-9.-:_]');
    }
  };
  c.ensureValidPort = function(a) {
    if (a) {
      var b = Number(a);
      if (!(/^[0-9]+$/.test(b) && 0 < b && 65536 > b)) throw new TypeError(
        'Port "' + a + '" is not a valid port');
    }
  };
  c.noConflict = function(a) {
    if (a) return a = {
        URI: this.noConflict()
      }, p.URITemplate && "function" === typeof p.URITemplate
      .noConflict && (a.URITemplate = p.URITemplate.noConflict()), p
      .IPv6 && "function" === typeof p.IPv6.noConflict && (a.IPv6 = p.IPv6
        .noConflict()), p.SecondLevelDomains && "function" === typeof p
      .SecondLevelDomains.noConflict && (a.SecondLevelDomains = p
        .SecondLevelDomains.noConflict()),
      a;
    p.URI === this && (p.URI = t);
    return this
  };
  e.build = function(a) {
    if (!0 === a) this._deferred_build = !0;
    else if (void 0 === a || this._deferred_build) this._string = c.build(
      this._parts), this._deferred_build = !1;
    return this
  };
  e.clone = function() {
    return new c(this)
  };
  e.valueOf = e.toString = function() {
    return this.build(!1)._string
  };
  e.protocol = m("protocol");
  e.username = m("username");
  e.password = m("password");
  e.hostname = m("hostname");
  e.port = m("port");
  e.query = B("query", "?");
  e.fragment = B("fragment", "#");
  e.search = function(a, b) {
    var d =
      this.query(a, b);
    return "string" === typeof d && d.length ? "?" + d : d
  };
  e.hash = function(a, b) {
    var d = this.fragment(a, b);
    return "string" === typeof d && d.length ? "#" + d : d
  };
  e.pathname = function(a, b) {
    if (void 0 === a || !0 === a) {
      var d = this._parts.path || (this._parts.hostname ? "/" : "");
      return a ? (this._parts.urn ? c.decodeUrnPath : c.decodePath)(d) : d
    }
    this._parts.path = this._parts.urn ? a ? c.recodeUrnPath(a) : "" : a ? c
      .recodePath(a) : "/";
    this.build(!b);
    return this
  };
  e.path = e.pathname;
  e.href = function(a, b) {
    var d;
    if (void 0 === a) return this.toString();
    this._string = "";
    this._parts = c._parts();
    var h = a instanceof c,
      e = "object" === typeof a && (a.hostname || a.path || a.pathname);
    a.nodeName && (e = c.getDomAttribute(a), a = a[e] || "", e = !1);
    !h && e && void 0 !== a.pathname && (a = a.toString());
    if ("string" === typeof a || a instanceof String) this._parts = c.parse(
      String(a), this._parts);
    else if (h || e) {
      h = h ? a._parts : a;
      for (d in h) "query" !== d && r.call(this._parts, d) && (this._parts[
        d] = h[d]);
      h.query && this.query(h.query, !1)
    } else throw new TypeError("invalid input");
    this.build(!b);
    return this
  };
  e.is = function(a) {
    var b = !1,
      d = !1,
      h = !1,
      e = !1,
      g = !1,
      f = !1,
      q = !1,
      m = !this._parts.urn;
    this._parts.hostname && (m = !1, d = c.ip4_expression.test(this._parts
        .hostname), h = c.ip6_expression.test(this._parts.hostname), b =
      d || h, g = (e = !b) && k && k.has(this._parts.hostname), f = e && c
      .idn_expression.test(this._parts.hostname), q = e && c
      .punycode_expression.test(this._parts.hostname));
    switch (a.toLowerCase()) {
      case "relative":
        return m;
      case "absolute":
        return !m;
      case "domain":
      case "name":
        return e;
      case "sld":
        return g;
      case "ip":
        return b;
      case "ip4":
      case "ipv4":
      case "inet4":
        return d;
      case "ip6":
      case "ipv6":
      case "inet6":
        return h;
      case "idn":
        return f;
      case "url":
        return !this._parts.urn;
      case "urn":
        return !!this._parts.urn;
      case "punycode":
        return q
    }
    return null
  };
  var F = e.protocol,
    G = e.port,
    H = e.hostname;
  e.protocol = function(a, b) {
    if (a && (a = a.replace(/:(\/\/)?$/, ""), !a.match(c
        .protocol_expression))) throw new TypeError('Protocol "' + a +
      "\" contains characters other than [A-Z0-9.+-] or doesn't start with [A-Z]"
      );
    return F.call(this, a, b)
  };
  e.scheme = e.protocol;
  e.port = function(a, b) {
    if (this._parts.urn) return void 0 ===
      a ? "" : this;
    void 0 !== a && (0 === a && (a = null), a && (a += "", ":" === a.charAt(
      0) && (a = a.substring(1)), c.ensureValidPort(a)));
    return G.call(this, a, b)
  };
  e.hostname = function(a, b) {
    if (this._parts.urn) return void 0 === a ? "" : this;
    if (void 0 !== a) {
      var d = {
        preventInvalidHostname: this._parts.preventInvalidHostname
      };
      if ("/" !== c.parseHost(a, d)) throw new TypeError('Hostname "' + a +
        '" contains characters other than [A-Z0-9.-]');
      a = d.hostname;
      this._parts.preventInvalidHostname && c.ensureValidHostname(a, this
        ._parts.protocol)
    }
    return H.call(this,
      a, b)
  };
  e.origin = function(a, b) {
    if (this._parts.urn) return void 0 === a ? "" : this;
    if (void 0 === a) {
      var d = this.protocol();
      return this.authority() ? (d ? d + "://" : "") + this.authority() : ""
    }
    d = c(a);
    this.protocol(d.protocol()).authority(d.authority()).build(!b);
    return this
  };
  e.host = function(a, b) {
    if (this._parts.urn) return void 0 === a ? "" : this;
    if (void 0 === a) return this._parts.hostname ? c.buildHost(this
      ._parts) : "";
    if ("/" !== c.parseHost(a, this._parts)) throw new TypeError(
      'Hostname "' + a + '" contains characters other than [A-Z0-9.-]');
    this.build(!b);
    return this
  };
  e.authority = function(a, b) {
    if (this._parts.urn) return void 0 === a ? "" : this;
    if (void 0 === a) return this._parts.hostname ? c.buildAuthority(this
      ._parts) : "";
    if ("/" !== c.parseAuthority(a, this._parts)) throw new TypeError(
      'Hostname "' + a + '" contains characters other than [A-Z0-9.-]');
    this.build(!b);
    return this
  };
  e.userinfo = function(a, b) {
    if (this._parts.urn) return void 0 === a ? "" : this;
    if (void 0 === a) {
      var d = c.buildUserinfo(this._parts);
      return d ? d.substring(0, d.length - 1) : d
    }
    "@" !== a[a.length - 1] &&
      (a += "@");
    c.parseUserinfo(a, this._parts);
    this.build(!b);
    return this
  };
  e.resource = function(a, b) {
    if (void 0 === a) return this.path() + this.search() + this.hash();
    var d = c.parse(a);
    this._parts.path = d.path;
    this._parts.query = d.query;
    this._parts.fragment = d.fragment;
    this.build(!b);
    return this
  };
  e.subdomain = function(a, b) {
    if (this._parts.urn) return void 0 === a ? "" : this;
    if (void 0 === a) {
      if (!this._parts.hostname || this.is("IP")) return "";
      var d = this._parts.hostname.length - this.domain().length - 1;
      return this._parts.hostname.substring(0,
        d) || ""
    }
    d = this._parts.hostname.length - this.domain().length;
    d = this._parts.hostname.substring(0, d);
    d = new RegExp("^" + A(d));
    a && "." !== a.charAt(a.length - 1) && (a += ".");
    if (-1 !== a.indexOf(":")) throw new TypeError(
      "Domains cannot contain colons");
    a && c.ensureValidHostname(a, this._parts.protocol);
    this._parts.hostname = this._parts.hostname.replace(d, a);
    this.build(!b);
    return this
  };
  e.domain = function(a, b) {
    if (this._parts.urn) return void 0 === a ? "" : this;
    "boolean" === typeof a && (b = a, a = void 0);
    if (void 0 === a) {
      if (!this._parts.hostname ||
        this.is("IP")) return "";
      var d = this._parts.hostname.match(/\./g);
      if (d && 2 > d.length) return this._parts.hostname;
      d = this._parts.hostname.length - this.tld(b).length - 1;
      d = this._parts.hostname.lastIndexOf(".", d - 1) + 1;
      return this._parts.hostname.substring(d) || ""
    }
    if (!a) throw new TypeError("cannot set domain empty");
    if (-1 !== a.indexOf(":")) throw new TypeError(
      "Domains cannot contain colons");
    c.ensureValidHostname(a, this._parts.protocol);
    !this._parts.hostname || this.is("IP") ? this._parts.hostname = a : (d =
      new RegExp(A(this.domain()) +
        "$"), this._parts.hostname = this._parts.hostname.replace(d, a));
    this.build(!b);
    return this
  };
  e.tld = function(a, b) {
    if (this._parts.urn) return void 0 === a ? "" : this;
    "boolean" === typeof a && (b = a, a = void 0);
    if (void 0 === a) {
      if (!this._parts.hostname || this.is("IP")) return "";
      var d = this._parts.hostname.lastIndexOf(".");
      d = this._parts.hostname.substring(d + 1);
      return !0 !== b && k && k.list[d.toLowerCase()] ? k.get(this._parts
        .hostname) || d : d
    }
    if (a)
      if (a.match(/[^a-zA-Z0-9-]/))
        if (k && k.is(a)) d = new RegExp(A(this.tld()) + "$"), this._parts
          .hostname =
          this._parts.hostname.replace(d, a);
        else throw new TypeError('TLD "' + a +
          '" contains characters other than [A-Z0-9]');
    else {
      if (!this._parts.hostname || this.is("IP")) throw new ReferenceError(
        "cannot set TLD on non-domain host");
      d = new RegExp(A(this.tld()) + "$");
      this._parts.hostname = this._parts.hostname.replace(d, a)
    } else throw new TypeError("cannot set TLD empty");
    this.build(!b);
    return this
  };
  e.directory = function(a, b) {
    if (this._parts.urn) return void 0 === a ? "" : this;
    if (void 0 === a || !0 === a) {
      if (!this._parts.path &&
        !this._parts.hostname) return "";
      if ("/" === this._parts.path) return "/";
      var d = this._parts.path.length - this.filename().length - 1;
      d = this._parts.path.substring(0, d) || (this._parts.hostname ? "/" :
        "");
      return a ? c.decodePath(d) : d
    }
    d = this._parts.path.length - this.filename().length;
    d = this._parts.path.substring(0, d);
    d = new RegExp("^" + A(d));
    this.is("relative") || (a || (a = "/"), "/" !== a.charAt(0) && (a =
      "/" + a));
    a && "/" !== a.charAt(a.length - 1) && (a += "/");
    a = c.recodePath(a);
    this._parts.path = this._parts.path.replace(d, a);
    this.build(!b);
    return this
  };
  e.filename = function(a, b) {
    if (this._parts.urn) return void 0 === a ? "" : this;
    if ("string" !== typeof a) {
      if (!this._parts.path || "/" === this._parts.path) return "";
      var d = this._parts.path.lastIndexOf("/");
      d = this._parts.path.substring(d + 1);
      return a ? c.decodePathSegment(d) : d
    }
    d = !1;
    "/" === a.charAt(0) && (a = a.substring(1));
    a.match(/\.?\//) && (d = !0);
    var h = new RegExp(A(this.filename()) + "$");
    a = c.recodePath(a);
    this._parts.path = this._parts.path.replace(h, a);
    d ? this.normalizePath(b) : this.build(!b);
    return this
  };
  e.suffix =
    function(a, b) {
      if (this._parts.urn) return void 0 === a ? "" : this;
      if (void 0 === a || !0 === a) {
        if (!this._parts.path || "/" === this._parts.path) return "";
        var d = this.filename(),
          h = d.lastIndexOf(".");
        if (-1 === h) return "";
        d = d.substring(h + 1);
        d = /^[a-z0-9%]+$/i.test(d) ? d : "";
        return a ? c.decodePathSegment(d) : d
      }
      "." === a.charAt(0) && (a = a.substring(1));
      if (d = this.suffix()) h = a ? new RegExp(A(d) + "$") : new RegExp(A(
        "." + d) + "$");
      else {
        if (!a) return this;
        this._parts.path += "." + c.recodePath(a)
      }
      h && (a = c.recodePath(a), this._parts.path = this._parts.path.replace(
        h,
        a));
      this.build(!b);
      return this
    };
  e.segment = function(a, b, d) {
    var c = this._parts.urn ? ":" : "/",
      e = this.path(),
      g = "/" === e.substring(0, 1);
    e = e.split(c);
    void 0 !== a && "number" !== typeof a && (d = b, b = a, a = void 0);
    if (void 0 !== a && "number" !== typeof a) throw Error('Bad segment "' +
      a + '", must be 0-based integer');
    g && e.shift();
    0 > a && (a = Math.max(e.length + a, 0));
    if (void 0 === b) return void 0 === a ? e : e[a];
    if (null === a || void 0 === e[a])
      if (w(b)) {
        e = [];
        a = 0;
        for (var f = b.length; a < f; a++)
          if (b[a].length || e.length && e[e.length - 1].length) e.length &&
            !e[e.length -
              1].length && e.pop(), e.push(y(b[a]))
      } else {
        if (b || "string" === typeof b) b = y(b), "" === e[e.length - 1] ?
          e[e.length - 1] = b : e.push(b)
      }
    else b ? e[a] = y(b) : e.splice(a, 1);
    g && e.unshift("");
    return this.path(e.join(c), d)
  };
  e.segmentCoded = function(a, b, d) {
    var e;
    "number" !== typeof a && (d = b, b = a, a = void 0);
    if (void 0 === b) {
      a = this.segment(a, b, d);
      if (w(a)) {
        var g = 0;
        for (e = a.length; g < e; g++) a[g] = c.decode(a[g])
      } else a = void 0 !== a ? c.decode(a) : void 0;
      return a
    }
    if (w(b))
      for (g = 0, e = b.length; g < e; g++) b[g] = c.encode(b[g]);
    else b = "string" === typeof b || b instanceof
    String ? c.encode(b) : b;
    return this.segment(a, b, d)
  };
  var I = e.query;
  e.query = function(a, b) {
    if (!0 === a) return c.parseQuery(this._parts.query, this._parts
      .escapeQuerySpace);
    if ("function" === typeof a) {
      var d = c.parseQuery(this._parts.query, this._parts.escapeQuerySpace),
        e = a.call(this, d);
      this._parts.query = c.buildQuery(e || d, this._parts
        .duplicateQueryParameters, this._parts.escapeQuerySpace);
      this.build(!b);
      return this
    }
    return void 0 !== a && "string" !== typeof a ? (this._parts.query = c
      .buildQuery(a, this._parts.duplicateQueryParameters,
        this._parts.escapeQuerySpace), this.build(!b), this) : I.call(
      this, a, b)
  };
  e.setQuery = function(a, b, d) {
    var e = c.parseQuery(this._parts.query, this._parts.escapeQuerySpace);
    if ("string" === typeof a || a instanceof String) e[a] = void 0 !== b ?
      b : null;
    else if ("object" === typeof a)
      for (var g in a) r.call(a, g) && (e[g] = a[g]);
    else throw new TypeError(
      "URI.addQuery() accepts an object, string as the name parameter");
    this._parts.query = c.buildQuery(e, this._parts
      .duplicateQueryParameters, this._parts.escapeQuerySpace);
    "string" !== typeof a &&
      (d = b);
    this.build(!d);
    return this
  };
  e.addQuery = function(a, b, d) {
    var e = c.parseQuery(this._parts.query, this._parts.escapeQuerySpace);
    c.addQuery(e, a, void 0 === b ? null : b);
    this._parts.query = c.buildQuery(e, this._parts
      .duplicateQueryParameters, this._parts.escapeQuerySpace);
    "string" !== typeof a && (d = b);
    this.build(!d);
    return this
  };
  e.removeQuery = function(a, b, d) {
    var e = c.parseQuery(this._parts.query, this._parts.escapeQuerySpace);
    c.removeQuery(e, a, b);
    this._parts.query = c.buildQuery(e, this._parts
      .duplicateQueryParameters,
      this._parts.escapeQuerySpace);
    "string" !== typeof a && (d = b);
    this.build(!d);
    return this
  };
  e.hasQuery = function(a, b, d) {
    var e = c.parseQuery(this._parts.query, this._parts.escapeQuerySpace);
    return c.hasQuery(e, a, b, d)
  };
  e.setSearch = e.setQuery;
  e.addSearch = e.addQuery;
  e.removeSearch = e.removeQuery;
  e.hasSearch = e.hasQuery;
  e.normalize = function() {
    return this._parts.urn ? this.normalizeProtocol(!1).normalizePath(!1)
      .normalizeQuery(!1).normalizeFragment(!1).build() : this
      .normalizeProtocol(!1).normalizeHostname(!1).normalizePort(!1)
      .normalizePath(!1).normalizeQuery(!1).normalizeFragment(!1).build()
  };
  e.normalizeProtocol = function(a) {
    "string" === typeof this._parts.protocol && (this._parts.protocol = this
      ._parts.protocol.toLowerCase(), this.build(!a));
    return this
  };
  e.normalizeHostname = function(a) {
    this._parts.hostname && (this.is("IDN") && f ? this._parts.hostname = f
      .toASCII(this._parts.hostname) : this.is("IPv6") && n && (this
        ._parts.hostname = n.best(this._parts.hostname)), this._parts
      .hostname = this._parts.hostname.toLowerCase(), this.build(!a));
    return this
  };
  e.normalizePort = function(a) {
    "string" === typeof this._parts.protocol &&
      this._parts.port === c.defaultPorts[this._parts.protocol] && (this
        ._parts.port = null, this.build(!a));
    return this
  };
  e.normalizePath = function(a) {
    var b = this._parts.path;
    if (!b) return this;
    if (this._parts.urn) return this._parts.path = c.recodeUrnPath(this
      ._parts.path), this.build(!a), this;
    if ("/" === this._parts.path) return this;
    b = c.recodePath(b);
    var d = "";
    if ("/" !== b.charAt(0)) {
      var e = !0;
      b = "/" + b
    }
    if ("/.." === b.slice(-3) || "/." === b.slice(-2)) b += "/";
    b = b.replace(/(\/(\.\/)+)|(\/\.$)/g, "/").replace(/\/{2,}/g, "/");
    e && (d = b.substring(1).match(/^(\.\.\/)+/) ||
      "") && (d = d[0]);
    for (;;) {
      var g = b.search(/\/\.\.(\/|$)/);
      if (-1 === g) break;
      else if (0 === g) {
        b = b.substring(3);
        continue
      }
      var f = b.substring(0, g).lastIndexOf("/"); - 1 === f && (f = g);
      b = b.substring(0, f) + b.substring(g + 3)
    }
    e && this.is("relative") && (b = d + b.substring(1));
    this._parts.path = b;
    this.build(!a);
    return this
  };
  e.normalizePathname = e.normalizePath;
  e.normalizeQuery = function(a) {
    "string" === typeof this._parts.query && (this._parts.query.length ?
      this.query(c.parseQuery(this._parts.query, this._parts
        .escapeQuerySpace)) : this._parts.query =
      null, this.build(!a));
    return this
  };
  e.normalizeFragment = function(a) {
    this._parts.fragment || (this._parts.fragment = null, this.build(!a));
    return this
  };
  e.normalizeSearch = e.normalizeQuery;
  e.normalizeHash = e.normalizeFragment;
  e.iso8859 = function() {
    var a = c.encode,
      b = c.decode;
    c.encode = escape;
    c.decode = decodeURIComponent;
    try {
      this.normalize()
    } finally {
      c.encode = a, c.decode = b
    }
    return this
  };
  e.unicode = function() {
    var a = c.encode,
      b = c.decode;
    c.encode = C;
    c.decode = unescape;
    try {
      this.normalize()
    } finally {
      c.encode = a, c.decode = b
    }
    return this
  };
  e.readable = function() {
    var a = this.clone();
    a.username("").password("").normalize();
    var b = "";
    a._parts.protocol && (b += a._parts.protocol + "://");
    a._parts.hostname && (a.is("punycode") && f ? (b += f.toUnicode(a._parts
        .hostname), a._parts.port && (b += ":" + a._parts.port)) : b += a
      .host());
    a._parts.hostname && a._parts.path && "/" !== a._parts.path.charAt(0) &&
      (b += "/");
    b += a.path(!0);
    if (a._parts.query) {
      for (var d = "", e = 0, g = a._parts.query.split("&"), q = g
        .length; e < q; e++) {
        var m = (g[e] || "").split("=");
        d += "&" + c.decodeQuery(m[0], this._parts.escapeQuerySpace)
          .replace(/&/g,
            "%26");
        void 0 !== m[1] && (d += "=" + c.decodeQuery(m[1], this._parts
          .escapeQuerySpace).replace(/&/g, "%26"))
      }
      b += "?" + d.substring(1)
    }
    return b += c.decodeQuery(a.hash(), !0)
  };
  e.absoluteTo = function(a) {
    var b = this.clone(),
      d = ["protocol", "username", "password", "hostname", "port"],
      e, g;
    if (this._parts.urn) throw Error(
      "URNs do not have any generally defined hierarchical components");
    a instanceof c || (a = new c(a));
    if (b._parts.protocol) return b;
    b._parts.protocol = a._parts.protocol;
    if (this._parts.hostname) return b;
    for (e = 0; g = d[e]; e++) b._parts[g] =
      a._parts[g];
    b._parts.path ? (".." === b._parts.path.substring(-2) && (b._parts
      .path += "/"), "/" !== b.path().charAt(0) && (d = (d = a
        .directory()) ? d : 0 === a.path().indexOf("/") ? "/" : "", b
      ._parts.path = (d ? d + "/" : "") + b._parts.path, b
      .normalizePath())) : (b._parts.path = a._parts.path, b._parts
      .query || (b._parts.query = a._parts.query));
    b.build();
    return b
  };
  e.relativeTo = function(a) {
    var b = this.clone().normalize();
    if (b._parts.urn) throw Error(
      "URNs do not have any generally defined hierarchical components");
    a = (new c(a)).normalize();
    var d =
      b._parts;
    var e = a._parts;
    var g = b.path();
    a = a.path();
    if ("/" !== g.charAt(0)) throw Error("URI is already relative");
    if ("/" !== a.charAt(0)) throw Error(
      "Cannot calculate a URI relative to another relative URI");
    d.protocol === e.protocol && (d.protocol = null);
    if (d.username === e.username && d.password === e.password && null === d
      .protocol && null === d.username && null === d.password && d
      .hostname === e.hostname && d.port === e.port) d.hostname = null, d
      .port = null;
    else return b.build();
    if (g === a) return d.path = "", b.build();
    g = c.commonPath(g, a);
    if (!g) return b.build();
    e = e.path.substring(g.length).replace(/[^\/]*$/, "").replace(/.*?\//g,
      "../");
    d.path = e + d.path.substring(g.length) || "./";
    return b.build()
  };
  e.equals = function(a) {
    var b = this.clone(),
      d = new c(a);
    a = {};
    var e;
    b.normalize();
    d.normalize();
    if (b.toString() === d.toString()) return !0;
    var g = b.query();
    var f = d.query();
    b.query("");
    d.query("");
    if (b.toString() !== d.toString() || g.length !== f.length) return !1;
    b = c.parseQuery(g, this._parts.escapeQuerySpace);
    f = c.parseQuery(f, this._parts.escapeQuerySpace);
    for (e in b)
      if (r.call(b,
          e)) {
        if (!w(b[e])) {
          if (b[e] !== f[e]) return !1
        } else if (!x(b[e], f[e])) return !1;
        a[e] = !0
      } for (e in f)
      if (r.call(f, e) && !a[e]) return !1;
    return !0
  };
  e.preventInvalidHostname = function(a) {
    this._parts.preventInvalidHostname = !!a;
    return this
  };
  e.duplicateQueryParameters = function(a) {
    this._parts.duplicateQueryParameters = !!a;
    return this
  };
  e.escapeQuerySpace = function(a) {
    this._parts.escapeQuerySpace = !!a;
    return this
  };
  return c
});
(function(f, n) {
  "object" === typeof module && module.exports ? module.exports = n(require(
    "./URI")) : "function" === typeof define && define.amd ? define([
    "./URI"], n) : f.URITemplate = n(f.URI, f)
})(this, function(f, n) {
  function k(c) {
    if (k._cache[c]) return k._cache[c];
    if (!(this instanceof k)) return new k(c);
    this.expression = c;
    k._cache[c] = this;
    return this
  }

  function p(c) {
    this.data = c;
    this.cache = {}
  }
  var c = n && n.URITemplate,
    A = Object.prototype.hasOwnProperty,
    z = k.prototype,
    w = {
      "": {
        prefix: "",
        separator: ",",
        named: !1,
        empty_name_separator: !1,
        encode: "encode"
      },
      "+": {
        prefix: "",
        separator: ",",
        named: !1,
        empty_name_separator: !1,
        encode: "encodeReserved"
      },
      "#": {
        prefix: "#",
        separator: ",",
        named: !1,
        empty_name_separator: !1,
        encode: "encodeReserved"
      },
      ".": {
        prefix: ".",
        separator: ".",
        named: !1,
        empty_name_separator: !1,
        encode: "encode"
      },
      "/": {
        prefix: "/",
        separator: "/",
        named: !1,
        empty_name_separator: !1,
        encode: "encode"
      },
      ";": {
        prefix: ";",
        separator: ";",
        named: !0,
        empty_name_separator: !1,
        encode: "encode"
      },
      "?": {
        prefix: "?",
        separator: "&",
        named: !0,
        empty_name_separator: !0,
        encode: "encode"
      },
      "&": {
        prefix: "&",
        separator: "&",
        named: !0,
        empty_name_separator: !0,
        encode: "encode"
      }
    };
  k._cache = {};
  k.EXPRESSION_PATTERN = /\{([^a-zA-Z0-9%_]?)([^\}]+)(\}|$)/g;
  k.VARIABLE_PATTERN = /^([^*:.](?:\.?[^*:.])*)((\*)|:(\d+))?$/;
  k.VARIABLE_NAME_PATTERN = /[^a-zA-Z0-9%_.]/;
  k.LITERAL_PATTERN = /[<>{}"`^| \\]/;
  k.expand = function(c, f, n) {
    var g = w[c.operator],
      q = g.named ? "Named" : "Unnamed";
    c = c.variables;
    var p = [],
      m, x;
    for (x = 0; m = c[x]; x++) {
      var t = f.get(m.name);
      if (0 === t.type && n && n.strict) throw Error(
        'Missing expansion value for variable "' +
        m.name + '"');
      if (t.val.length) {
        if (1 < t.type && m.maxlength) throw Error(
          'Invalid expression: Prefix modifier not applicable to variable "' +
          m.name + '"');
        p.push(k["expand" + q](t, g, m.explode, m.explode && g.separator ||
          ",", m.maxlength, m.name))
      } else t.type && p.push("")
    }
    return p.length ? g.prefix + p.join(g.separator) : ""
  };
  k.expandNamed = function(c, q, k, y, n, p) {
    var g = "",
      x = q.encode;
    q = q.empty_name_separator;
    var t = !c[x].length,
      e = 2 === c.type ? "" : f[x](p),
      r;
    var u = 0;
    for (r = c.val.length; u < r; u++) {
      if (n) {
        var v = f[x](c.val[u][1].substring(0,
          n));
        2 === c.type && (e = f[x](c.val[u][0].substring(0, n)))
      } else t ? (v = f[x](c.val[u][1]), 2 === c.type ? (e = f[x](c.val[u][
        0]), c[x].push([e, v])) : c[x].push([void 0, v])) : (v = c[x][u][
        1], 2 === c.type && (e = c[x][u][0]));
      g && (g += y);
      k ? g += e + (q || v ? "=" : "") + v : (u || (g += f[x](p) + (q || v ?
        "=" : "")), 2 === c.type && (g += e + ","), g += v)
    }
    return g
  };
  k.expandUnnamed = function(c, q, k, n, p) {
    var g = "",
      m = q.encode;
    q = q.empty_name_separator;
    var y = !c[m].length,
      x;
    var e = 0;
    for (x = c.val.length; e < x; e++) {
      if (p) var r = f[m](c.val[e][1].substring(0, p));
      else y ? (r = f[m](c.val[e][1]),
          c[m].push([2 === c.type ? f[m](c.val[e][0]) : void 0, r])) : r =
        c[m][e][1];
      g && (g += n);
      if (2 === c.type) {
        var u = p ? f[m](c.val[e][0].substring(0, p)) : c[m][e][0];
        g += u;
        g = k ? g + (q || r ? "=" : "") : g + ","
      }
      g += r
    }
    return g
  };
  k.noConflict = function() {
    n.URITemplate === k && (n.URITemplate = c);
    return k
  };
  z.expand = function(c, f) {
    var g = "";
    this.parts && this.parts.length || this.parse();
    c instanceof p || (c = new p(c));
    for (var q = 0, n = this.parts.length; q < n; q++) g += "string" ===
      typeof this.parts[q] ? this.parts[q] : k.expand(this.parts[q], c, f);
    return g
  };
  z.parse = function() {
    var c =
      this.expression,
      f = k.EXPRESSION_PATTERN,
      n = k.VARIABLE_PATTERN,
      p = k.VARIABLE_NAME_PATTERN,
      A = k.LITERAL_PATTERN,
      z = [],
      m = 0,
      B = function(c) {
        if (c.match(A)) throw Error('Invalid Literal "' + c + '"');
        return c
      };
    for (f.lastIndex = 0;;) {
      var t = f.exec(c);
      if (null === t) {
        z.push(B(c.substring(m)));
        break
      } else z.push(B(c.substring(m, t.index))), m = t.index + t[0].length;
      if (!w[t[1]]) throw Error('Unknown Operator "' + t[1] + '" in "' + t[
        0] + '"');
      if (!t[3]) throw Error('Unclosed Expression "' + t[0] + '"');
      var e = t[2].split(",");
      for (var r = 0, u = e.length; r <
        u; r++) {
        var v = e[r].match(n);
        if (null === v) throw Error('Invalid Variable "' + e[r] + '" in "' +
          t[0] + '"');
        if (v[1].match(p)) throw Error('Invalid Variable Name "' + v[1] +
          '" in "' + t[0] + '"');
        e[r] = {
          name: v[1],
          explode: !!v[3],
          maxlength: v[4] && parseInt(v[4], 10)
        }
      }
      if (!e.length) throw Error('Expression Missing Variable(s) "' + t[0] +
        '"');
      z.push({
        expression: t[0],
        operator: t[1],
        variables: e
      })
    }
    z.length || z.push(B(c));
    this.parts = z;
    return this
  };
  p.prototype.get = function(c) {
    var f = this.data,
      g = {
        type: 0,
        val: [],
        encode: [],
        encodeReserved: []
      };
    if (void 0 !== this.cache[c]) return this.cache[c];
    this.cache[c] = g;
    f = "[object Function]" === String(Object.prototype.toString.call(f)) ?
      f(c) : "[object Function]" === String(Object.prototype.toString.call(
        f[c])) ? f[c](c) : f[c];
    if (void 0 !== f && null !== f)
      if ("[object Array]" === String(Object.prototype.toString.call(f))) {
        var k = 0;
        for (c = f.length; k < c; k++) void 0 !== f[k] && null !== f[k] && g
          .val.push([void 0, String(f[k])]);
        g.val.length && (g.type = 3)
      } else if ("[object Object]" === String(Object.prototype.toString
        .call(f))) {
      for (k in f) A.call(f,
        k) && void 0 !== f[k] && null !== f[k] && g.val.push([k, String(f[
        k])]);
      g.val.length && (g.type = 2)
    } else g.type = 1, g.val.push([void 0, String(f)]);
    return g
  };
  f.expand = function(c, n) {
    var g = (new k(c)).expand(n);
    return new f(g)
  };
  return k
});
