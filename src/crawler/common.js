const blockElements = ['div', 'body', 'section', 'article', 'aside', 'nav',
  'header', 'footer', 'main', 'form', 'fieldset'
];
const ignoredElements = ['script', 'style', 'noscript', 'br', 'hr'];

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

var getElementWidth = function(element) {
  var rect = element.getBoundingClientRect();
  return rect.right - rect.left;
};

var getElementHeight = function(element) {
  var rect = element.getBoundingClientRect();
  return rect.bottom - rect.top;
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

    var rect = element.getBoundingClientRect();
    if (rect.height > 0 && rect.width > 0) {
      return true;
    }

    return style.overflow !== 'hidden' && Array.from(element.childNodes).some(
      n => n.nodeType === Node.TEXT_NODE || (n.nodeType === Node.ELEMENT_NODE &&
        positiveSize(n)));
  };

  var getOverflowState = function(element) {
    var region = element.getBoundingClientRect();
    var htmlElem = document.documentElement;
    var bodyElem = document.body;
    var htmlOverflowStyle = window.getComputedStyle(htmlElem).overflow;
    var treatAsFixedPosition;

    var getOverflowParent = function(e) {
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
        var containerDisplay = (style.display);
        if (containerDisplay.startsWith('inline')) {
          return false;
        }

        if (position === 'absolute' && style.position === 'static') {
          return false;
        }

        return true;
      }
    };

    var getOverflowStyles = function(e) {
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

      var style = window.getComputedStyle(overflowElem);
      var overflow = {
        x: style.overflowX,
        y: style.overflowY
      };

      if (e == htmlElem) {
        overflow.x = overflow.x === 'visible' ? 'auto' : overflow.x;
        overflow.y = overflow.y === 'visible' ? 'auto' : overflow.y;
      }

      return overflow;
    };

    var getScroll = function(e) {
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
    };

    for (var container = getOverflowParent(element); !!container; container =
      getOverflowParent(container)) {
      var containerOverflow = getOverflowStyles(container);

      if (containerOverflow.x == 'visible' && containerOverflow.y ==
        'visible') {
        continue;
      }

      var containerRect = container.getBoundingClientRect();

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

  var hiddenByOverflow = function(element) {
    return getOverflowState(element) === 'hidden' && Array.from(element.childNodes)
      .every(n => n.nodeType !== Node.ELEMENT_NODE || !hiddenByOverflow(n) ||
        !positiveSize(n));
  };

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
  var style = window.getComputedStyle(element);

  var height = getElementHeight(element);
  var width = getElementWidth(element);

  return (height === 1 && width === 1);
};

var containsBlockElements = function(element) {
  for (var child of element.children) {
    if (blockElements.includes(child.tagName.toLowerCase())) {
      return true;
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

var getElementsByXPath = function(xpath, parent) {
  let results = [];
  let query = document.evaluate(xpath,
    parent || document,
    null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
  for (let i = 0, length = query.snapshotLength; i < length; ++i) {
    results.push(query.snapshotItem(i));
  }
  return results;
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

var min = function(iterable, by = identity) {
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
    return min(clustersAndDistances(), x => x.distance);
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
