import { E as w, U as Mt, T as Be, a as $e, a2 as B, a3 as G, D as V, N as Ut, ac as Y, ad as ke, ae as Re, _ as E, af as re, ag as ye, w as $, s as M, M as U, Z as J, O as ie, ah as Gt, ai as A, k as j, c as je, H as W, a5 as be, R as we, F as Ke, b as Q, B as D, n as Me, y as se, aj as zt, ak as Te, K as xe, al as Z, q as ve, u as At, t as Wt, l as Ne, p as qe, a7 as Qe, aa as Je, m as Dt, o as Lt, a8 as It, a9 as Ot, ab as Et, am as Ht, an as Vt, e as P, ao as Yt } from "./Index-Ct_1BCRd.js";
import { S as ne, c as le, a as Xt, b as $t, B as Ze } from "./colorToUniform-zJcCVLeu.js";
import { C as K } from "./CanvasPool-CO7699qB.js";
class et {
  /**
   * Initialize the plugin with scope of application instance
   * @private
   * @param {object} [options] - See application options
   */
  static init(e) {
    Object.defineProperty(
      this,
      "resizeTo",
      {
        set(t) {
          globalThis.removeEventListener("resize", this.queueResize), this._resizeTo = t, t && (globalThis.addEventListener("resize", this.queueResize), this.resize());
        },
        get() {
          return this._resizeTo;
        }
      }
    ), this.queueResize = () => {
      this._resizeTo && (this._cancelResize(), this._resizeId = requestAnimationFrame(() => this.resize()));
    }, this._cancelResize = () => {
      this._resizeId && (cancelAnimationFrame(this._resizeId), this._resizeId = null);
    }, this.resize = () => {
      if (!this._resizeTo)
        return;
      this._cancelResize();
      let t, r;
      if (this._resizeTo === globalThis.window)
        t = globalThis.innerWidth, r = globalThis.innerHeight;
      else {
        const { clientWidth: i, clientHeight: s } = this._resizeTo;
        t = i, r = s;
      }
      this.renderer.resize(t, r), this.render();
    }, this._resizeId = null, this._resizeTo = null, this.resizeTo = e.resizeTo || null;
  }
  /**
   * Clean up the ticker, scoped to application
   * @private
   */
  static destroy() {
    globalThis.removeEventListener("resize", this.queueResize), this._cancelResize(), this._cancelResize = null, this.queueResize = null, this.resizeTo = null, this.resize = null;
  }
}
et.extension = w.Application;
class tt {
  /**
   * Initialize the plugin with scope of application instance
   * @private
   * @param {object} [options] - See application options
   */
  static init(e) {
    e = Object.assign({
      autoStart: !0,
      sharedTicker: !1
    }, e), Object.defineProperty(
      this,
      "ticker",
      {
        set(t) {
          this._ticker && this._ticker.remove(this.render, this), this._ticker = t, t && t.add(this.render, this, Mt.LOW);
        },
        get() {
          return this._ticker;
        }
      }
    ), this.stop = () => {
      this._ticker.stop();
    }, this.start = () => {
      this._ticker.start();
    }, this._ticker = null, this.ticker = e.sharedTicker ? Be.shared : new Be(), e.autoStart && this.start();
  }
  /**
   * Clean up the ticker, scoped to application.
   * @private
   */
  static destroy() {
    if (this._ticker) {
      const e = this._ticker;
      this.ticker = null, e.destroy();
    }
  }
}
tt.extension = w.Application;
class jt extends $e {
  constructor() {
    super(...arguments), this.chars = /* @__PURE__ */ Object.create(null), this.lineHeight = 0, this.fontFamily = "", this.fontMetrics = { fontSize: 0, ascent: 0, descent: 0 }, this.baseLineOffset = 0, this.distanceField = { type: "none", range: 0 }, this.pages = [], this.applyFillAsTint = !0, this.baseMeasurementFontSize = 100, this.baseRenderedFontSize = 100;
  }
  /**
   * The name of the font face.
   * @deprecated since 8.0.0 Use `fontFamily` instead.
   */
  get font() {
    return B(G, "BitmapFont.font is deprecated, please use BitmapFont.fontFamily instead."), this.fontFamily;
  }
  /**
   * The map of base page textures (i.e., sheets of glyphs).
   * @deprecated since 8.0.0 Use `pages` instead.
   */
  get pageTextures() {
    return B(G, "BitmapFont.pageTextures is deprecated, please use BitmapFont.pages instead."), this.pages;
  }
  /**
   * The size of the font face in pixels.
   * @deprecated since 8.0.0 Use `fontMetrics.fontSize` instead.
   */
  get size() {
    return B(G, "BitmapFont.size is deprecated, please use BitmapFont.fontMetrics.fontSize instead."), this.fontMetrics.fontSize;
  }
  /**
   * The kind of distance field for this font or "none".
   * @deprecated since 8.0.0 Use `distanceField.type` instead.
   */
  get distanceFieldRange() {
    return B(G, "BitmapFont.distanceFieldRange is deprecated, please use BitmapFont.distanceField.range instead."), this.distanceField.range;
  }
  /**
   * The range of the distance field in pixels.
   * @deprecated since 8.0.0 Use `distanceField.range` instead.
   */
  get distanceFieldType() {
    return B(G, "BitmapFont.distanceFieldType is deprecated, please use BitmapFont.distanceField.type instead."), this.distanceField.type;
  }
  destroy(e = !1) {
    var t;
    this.emit("destroy", this), this.removeAllListeners();
    for (const r in this.chars)
      (t = this.chars[r].texture) == null || t.destroy();
    this.chars = null, e && (this.pages.forEach((r) => r.texture.destroy(!0)), this.pages = null);
  }
}
/**
 * tiny-lru
 *
 * @copyright 2025 Jason Mulligan <jason.mulligan@avoidwork.com>
 * @license BSD-3-Clause
 * @version 11.4.5
 */
class Kt {
  /**
   * Creates a new LRU cache instance.
   * Note: Constructor does not validate parameters. Use lru() factory function for parameter validation.
   *
   * @constructor
   * @param {number} [max=0] - Maximum number of items to store. 0 means unlimited.
   * @param {number} [ttl=0] - Time to live in milliseconds. 0 means no expiration.
   * @param {boolean} [resetTtl=false] - Whether to reset TTL when accessing existing items via get().
   * @example
   * const cache = new LRU(1000, 60000, true); // 1000 items, 1 minute TTL, reset on access
   * @see {@link lru} For parameter validation
   * @since 1.0.0
   */
  constructor(e = 0, t = 0, r = !1) {
    this.first = null, this.items = /* @__PURE__ */ Object.create(null), this.last = null, this.max = e, this.resetTtl = r, this.size = 0, this.ttl = t;
  }
  /**
   * Removes all items from the cache.
   *
   * @method clear
   * @memberof LRU
   * @returns {LRU} The LRU instance for method chaining.
   * @example
   * cache.clear();
   * console.log(cache.size); // 0
   * @since 1.0.0
   */
  clear() {
    return this.first = null, this.items = /* @__PURE__ */ Object.create(null), this.last = null, this.size = 0, this;
  }
  /**
   * Removes an item from the cache by key.
   *
   * @method delete
   * @memberof LRU
   * @param {string} key - The key of the item to delete.
   * @returns {LRU} The LRU instance for method chaining.
   * @example
   * cache.set('key1', 'value1');
   * cache.delete('key1');
   * console.log(cache.has('key1')); // false
   * @see {@link LRU#has}
   * @see {@link LRU#clear}
   * @since 1.0.0
   */
  delete(e) {
    if (this.has(e)) {
      const t = this.items[e];
      delete this.items[e], this.size--, t.prev !== null && (t.prev.next = t.next), t.next !== null && (t.next.prev = t.prev), this.first === t && (this.first = t.next), this.last === t && (this.last = t.prev);
    }
    return this;
  }
  /**
   * Returns an array of [key, value] pairs for the specified keys.
   * Order follows LRU order (least to most recently used).
   *
   * @method entries
   * @memberof LRU
   * @param {string[]} [keys=this.keys()] - Array of keys to get entries for. Defaults to all keys.
   * @returns {Array<Array<*>>} Array of [key, value] pairs in LRU order.
   * @example
   * cache.set('a', 1).set('b', 2);
   * console.log(cache.entries()); // [['a', 1], ['b', 2]]
   * console.log(cache.entries(['a'])); // [['a', 1]]
   * @see {@link LRU#keys}
   * @see {@link LRU#values}
   * @since 11.1.0
   */
  entries(e = this.keys()) {
    return e.map((t) => [t, this.get(t)]);
  }
  /**
   * Removes the least recently used item from the cache.
   *
   * @method evict
   * @memberof LRU
   * @param {boolean} [bypass=false] - Whether to force eviction even when cache is empty.
   * @returns {LRU} The LRU instance for method chaining.
   * @example
   * cache.set('old', 'value').set('new', 'value');
   * cache.evict(); // Removes 'old' item
   * @see {@link LRU#setWithEvicted}
   * @since 1.0.0
   */
  evict(e = !1) {
    if (e || this.size > 0) {
      const t = this.first;
      delete this.items[t.key], --this.size === 0 ? (this.first = null, this.last = null) : (this.first = t.next, this.first.prev = null);
    }
    return this;
  }
  /**
   * Returns the expiration timestamp for a given key.
   *
   * @method expiresAt
   * @memberof LRU
   * @param {string} key - The key to check expiration for.
   * @returns {number|undefined} The expiration timestamp in milliseconds, or undefined if key doesn't exist.
   * @example
   * const cache = new LRU(100, 5000); // 5 second TTL
   * cache.set('key1', 'value1');
   * console.log(cache.expiresAt('key1')); // timestamp 5 seconds from now
   * @see {@link LRU#get}
   * @see {@link LRU#has}
   * @since 1.0.0
   */
  expiresAt(e) {
    let t;
    return this.has(e) && (t = this.items[e].expiry), t;
  }
  /**
   * Retrieves a value from the cache by key. Updates the item's position to most recently used.
   *
   * @method get
   * @memberof LRU
   * @param {string} key - The key to retrieve.
   * @returns {*} The value associated with the key, or undefined if not found or expired.
   * @example
   * cache.set('key1', 'value1');
   * console.log(cache.get('key1')); // 'value1'
   * console.log(cache.get('nonexistent')); // undefined
   * @see {@link LRU#set}
   * @see {@link LRU#has}
   * @since 1.0.0
   */
  get(e) {
    const t = this.items[e];
    if (t !== void 0) {
      if (this.ttl > 0 && t.expiry <= Date.now()) {
        this.delete(e);
        return;
      }
      return this.moveToEnd(t), t.value;
    }
  }
  /**
   * Checks if a key exists in the cache.
   *
   * @method has
   * @memberof LRU
   * @param {string} key - The key to check for.
   * @returns {boolean} True if the key exists, false otherwise.
   * @example
   * cache.set('key1', 'value1');
   * console.log(cache.has('key1')); // true
   * console.log(cache.has('nonexistent')); // false
   * @see {@link LRU#get}
   * @see {@link LRU#delete}
   * @since 9.0.0
   */
  has(e) {
    return e in this.items;
  }
  /**
   * Efficiently moves an item to the end of the LRU list (most recently used position).
   * This is an internal optimization method that avoids the overhead of the full set() operation
   * when only LRU position needs to be updated.
   *
   * @method moveToEnd
   * @memberof LRU
   * @param {Object} item - The cache item with prev/next pointers to reposition.
   * @private
   * @since 11.3.5
   */
  moveToEnd(e) {
    this.last !== e && (e.prev !== null && (e.prev.next = e.next), e.next !== null && (e.next.prev = e.prev), this.first === e && (this.first = e.next), e.prev = this.last, e.next = null, this.last !== null && (this.last.next = e), this.last = e, this.first === null && (this.first = e));
  }
  /**
   * Returns an array of all keys in the cache, ordered from least to most recently used.
   *
   * @method keys
   * @memberof LRU
   * @returns {string[]} Array of keys in LRU order.
   * @example
   * cache.set('a', 1).set('b', 2);
   * cache.get('a'); // Move 'a' to most recent
   * console.log(cache.keys()); // ['b', 'a']
   * @see {@link LRU#values}
   * @see {@link LRU#entries}
   * @since 9.0.0
   */
  keys() {
    const e = [];
    let t = this.first;
    for (; t !== null; )
      e.push(t.key), t = t.next;
    return e;
  }
  /**
   * Sets a value in the cache and returns any evicted item.
   *
   * @method setWithEvicted
   * @memberof LRU
   * @param {string} key - The key to set.
   * @param {*} value - The value to store.
   * @param {boolean} [resetTtl=this.resetTtl] - Whether to reset the TTL for this operation.
   * @returns {Object|null} The evicted item (if any) with shape {key, value, expiry, prev, next}, or null.
   * @example
   * const cache = new LRU(2);
   * cache.set('a', 1).set('b', 2);
   * const evicted = cache.setWithEvicted('c', 3); // evicted = {key: 'a', value: 1, ...}
   * @see {@link LRU#set}
   * @see {@link LRU#evict}
   * @since 11.3.0
   */
  setWithEvicted(e, t, r = this.resetTtl) {
    let i = null;
    if (this.has(e))
      this.set(e, t, !0, r);
    else {
      this.max > 0 && this.size === this.max && (i = { ...this.first }, this.evict(!0));
      let s = this.items[e] = {
        expiry: this.ttl > 0 ? Date.now() + this.ttl : this.ttl,
        key: e,
        prev: this.last,
        next: null,
        value: t
      };
      ++this.size === 1 ? this.first = s : this.last.next = s, this.last = s;
    }
    return i;
  }
  /**
   * Sets a value in the cache. Updates the item's position to most recently used.
   *
   * @method set
   * @memberof LRU
   * @param {string} key - The key to set.
   * @param {*} value - The value to store.
   * @param {boolean} [bypass=false] - Internal parameter for setWithEvicted method.
   * @param {boolean} [resetTtl=this.resetTtl] - Whether to reset the TTL for this operation.
   * @returns {LRU} The LRU instance for method chaining.
   * @example
   * cache.set('key1', 'value1')
   *      .set('key2', 'value2')
   *      .set('key3', 'value3');
   * @see {@link LRU#get}
   * @see {@link LRU#setWithEvicted}
   * @since 1.0.0
   */
  set(e, t, r = !1, i = this.resetTtl) {
    let s = this.items[e];
    return r || s !== void 0 ? (s.value = t, r === !1 && i && (s.expiry = this.ttl > 0 ? Date.now() + this.ttl : this.ttl), this.moveToEnd(s)) : (this.max > 0 && this.size === this.max && this.evict(!0), s = this.items[e] = {
      expiry: this.ttl > 0 ? Date.now() + this.ttl : this.ttl,
      key: e,
      prev: this.last,
      next: null,
      value: t
    }, ++this.size === 1 ? this.first = s : this.last.next = s, this.last = s), this;
  }
  /**
   * Returns an array of all values in the cache for the specified keys.
   * Order follows LRU order (least to most recently used).
   *
   * @method values
   * @memberof LRU
   * @param {string[]} [keys=this.keys()] - Array of keys to get values for. Defaults to all keys.
   * @returns {Array<*>} Array of values corresponding to the keys in LRU order.
   * @example
   * cache.set('a', 1).set('b', 2);
   * console.log(cache.values()); // [1, 2]
   * console.log(cache.values(['a'])); // [1]
   * @see {@link LRU#keys}
   * @see {@link LRU#entries}
   * @since 11.1.0
   */
  values(e = this.keys()) {
    return e.map((t) => this.get(t));
  }
}
function rt(o = 1e3, e = 0, t = !1) {
  if (isNaN(o) || o < 0)
    throw new TypeError("Invalid max value");
  if (isNaN(e) || e < 0)
    throw new TypeError("Invalid ttl value");
  if (typeof t != "boolean")
    throw new TypeError("Invalid resetTtl value");
  return new Kt(o, e, t);
}
const Nt = [
  "serif",
  "sans-serif",
  "monospace",
  "cursive",
  "fantasy",
  "system-ui"
];
function ae(o) {
  const e = typeof o.fontSize == "number" ? `${o.fontSize}px` : o.fontSize;
  let t = o.fontFamily;
  Array.isArray(o.fontFamily) || (t = o.fontFamily.split(","));
  for (let r = t.length - 1; r >= 0; r--) {
    let i = t[r].trim();
    !/([\"\'])[^\'\"]+\1/.test(i) && !Nt.includes(i) && (i = `"${i}"`), t[r] = i;
  }
  return `${o.fontStyle} ${o.fontVariant} ${o.fontWeight} ${e} ${t.join(",")}`;
}
const ce = {
  // TextMetrics requires getImageData readback for measuring fonts.
  willReadFrequently: !0
}, z = class g {
  /**
   * Checking that we can use modern canvas 2D API.
   *
   * Note: This is an unstable API, Chrome < 94 use `textLetterSpacing`, later versions use `letterSpacing`.
   * @see TextMetrics.experimentalLetterSpacing
   * @see https://developer.mozilla.org/en-US/docs/Web/API/ICanvasRenderingContext2D/letterSpacing
   * @see https://developer.chrome.com/origintrials/#/view_trial/3585991203293757441
   */
  static get experimentalLetterSpacingSupported() {
    let e = g._experimentalLetterSpacingSupported;
    if (e === void 0) {
      const t = V.get().getCanvasRenderingContext2D().prototype;
      e = g._experimentalLetterSpacingSupported = "letterSpacing" in t || "textLetterSpacing" in t;
    }
    return e;
  }
  /**
   * @param text - the text that was measured
   * @param style - the style that was measured
   * @param width - the measured width of the text
   * @param height - the measured height of the text
   * @param lines - an array of the lines of text broken by new lines and wrapping if specified in style
   * @param lineWidths - an array of the line widths for each line matched to `lines`
   * @param lineHeight - the measured line height for this style
   * @param maxLineWidth - the maximum line width for all measured lines
   * @param {FontMetrics} fontProperties - the font properties object from TextMetrics.measureFont
   */
  constructor(e, t, r, i, s, n, a, l, u) {
    this.text = e, this.style = t, this.width = r, this.height = i, this.lines = s, this.lineWidths = n, this.lineHeight = a, this.maxLineWidth = l, this.fontProperties = u;
  }
  /**
   * Measures the supplied string of text and returns a Rectangle.
   * @param text - The text to measure.
   * @param style - The text style to use for measuring
   * @param canvas - optional specification of the canvas to use for measuring.
   * @param wordWrap
   * @returns Measured width and height of the text.
   */
  static measureText(e = " ", t, r = g._canvas, i = t.wordWrap) {
    var b;
    const s = `${e}-${t.styleKey}-wordWrap-${i}`;
    if (g._measurementCache.has(s))
      return g._measurementCache.get(s);
    const n = ae(t), a = g.measureFont(n);
    a.fontSize === 0 && (a.fontSize = t.fontSize, a.ascent = t.fontSize);
    const l = g.__context;
    l.font = n;
    const h = (i ? g._wordWrap(e, t, r) : e).split(/(?:\r\n|\r|\n)/), c = new Array(h.length);
    let d = 0;
    for (let y = 0; y < h.length; y++) {
      const T = g._measureText(h[y], t.letterSpacing, l);
      c[y] = T, d = Math.max(d, T);
    }
    const f = ((b = t._stroke) == null ? void 0 : b.width) || 0;
    let m = d + f;
    t.dropShadow && (m += t.dropShadow.distance);
    const x = t.lineHeight || a.fontSize;
    let _ = Math.max(x, a.fontSize + f) + (h.length - 1) * (x + t.leading);
    t.dropShadow && (_ += t.dropShadow.distance);
    const p = new g(
      e,
      t,
      m,
      _,
      h,
      c,
      x + t.leading,
      d,
      a
    );
    return g._measurementCache.set(s, p), p;
  }
  static _measureText(e, t, r) {
    let i = !1;
    g.experimentalLetterSpacingSupported && (g.experimentalLetterSpacing ? (r.letterSpacing = `${t}px`, r.textLetterSpacing = `${t}px`, i = !0) : (r.letterSpacing = "0px", r.textLetterSpacing = "0px"));
    const s = r.measureText(e);
    let n = s.width;
    const a = -s.actualBoundingBoxLeft;
    let u = s.actualBoundingBoxRight - a;
    if (n > 0)
      if (i)
        n -= t, u -= t;
      else {
        const h = (g.graphemeSegmenter(e).length - 1) * t;
        n += h, u += h;
      }
    return Math.max(n, u);
  }
  /**
   * Applies newlines to a string to have it optimally fit into the horizontal
   * bounds set by the Text object's wordWrapWidth property.
   * @param text - String to apply word wrapping to
   * @param style - the style to use when wrapping
   * @param canvas - optional specification of the canvas to use for measuring.
   * @returns New string with new lines applied where required
   */
  static _wordWrap(e, t, r = g._canvas) {
    const i = r.getContext("2d", ce);
    let s = 0, n = "", a = "";
    const l = /* @__PURE__ */ Object.create(null), { letterSpacing: u, whiteSpace: h } = t, c = g._collapseSpaces(h), d = g._collapseNewlines(h);
    let f = !c;
    const m = t.wordWrapWidth + u, x = g._tokenize(e);
    for (let _ = 0; _ < x.length; _++) {
      let p = x[_];
      if (g._isNewline(p)) {
        if (!d) {
          a += g._addLine(n), f = !c, n = "", s = 0;
          continue;
        }
        p = " ";
      }
      if (c) {
        const y = g.isBreakingSpace(p), T = g.isBreakingSpace(n[n.length - 1]);
        if (y && T)
          continue;
      }
      const b = g._getFromCache(p, u, l, i);
      if (b > m)
        if (n !== "" && (a += g._addLine(n), n = "", s = 0), g.canBreakWords(p, t.breakWords)) {
          const y = g.wordWrapSplit(p);
          for (let T = 0; T < y.length; T++) {
            let S = y[T], k = S, v = 1;
            for (; y[T + v]; ) {
              const R = y[T + v];
              if (!g.canBreakChars(k, R, p, T, t.breakWords))
                S += R;
              else
                break;
              k = R, v++;
            }
            T += v - 1;
            const F = g._getFromCache(S, u, l, i);
            F + s > m && (a += g._addLine(n), f = !1, n = "", s = 0), n += S, s += F;
          }
        } else {
          n.length > 0 && (a += g._addLine(n), n = "", s = 0);
          const y = _ === x.length - 1;
          a += g._addLine(p, !y), f = !1, n = "", s = 0;
        }
      else
        b + s > m && (f = !1, a += g._addLine(n), n = "", s = 0), (n.length > 0 || !g.isBreakingSpace(p) || f) && (n += p, s += b);
    }
    return a += g._addLine(n, !1), a;
  }
  /**
   * Convenience function for logging each line added during the wordWrap method.
   * @param line    - The line of text to add
   * @param newLine - Add new line character to end
   * @returns A formatted line
   */
  static _addLine(e, t = !0) {
    return e = g._trimRight(e), e = t ? `${e}
` : e, e;
  }
  /**
   * Gets & sets the widths of calculated characters in a cache object
   * @param key            - The key
   * @param letterSpacing  - The letter spacing
   * @param cache          - The cache
   * @param context        - The canvas context
   * @returns The from cache.
   */
  static _getFromCache(e, t, r, i) {
    let s = r[e];
    return typeof s != "number" && (s = g._measureText(e, t, i) + t, r[e] = s), s;
  }
  /**
   * Determines whether we should collapse breaking spaces.
   * @param whiteSpace - The TextStyle property whiteSpace
   * @returns Should collapse
   */
  static _collapseSpaces(e) {
    return e === "normal" || e === "pre-line";
  }
  /**
   * Determines whether we should collapse newLine chars.
   * @param whiteSpace - The white space
   * @returns should collapse
   */
  static _collapseNewlines(e) {
    return e === "normal";
  }
  /**
   * Trims breaking whitespaces from string.
   * @param text - The text
   * @returns Trimmed string
   */
  static _trimRight(e) {
    if (typeof e != "string")
      return "";
    for (let t = e.length - 1; t >= 0; t--) {
      const r = e[t];
      if (!g.isBreakingSpace(r))
        break;
      e = e.slice(0, -1);
    }
    return e;
  }
  /**
   * Determines if char is a newline.
   * @param char - The character
   * @returns True if newline, False otherwise.
   */
  static _isNewline(e) {
    return typeof e != "string" ? !1 : g._newlines.includes(e.charCodeAt(0));
  }
  /**
   * Determines if char is a breaking whitespace.
   *
   * It allows one to determine whether char should be a breaking whitespace
   * For example certain characters in CJK langs or numbers.
   * It must return a boolean.
   * @param char - The character
   * @param [_nextChar] - The next character
   * @returns True if whitespace, False otherwise.
   */
  static isBreakingSpace(e, t) {
    return typeof e != "string" ? !1 : g._breakingSpaces.includes(e.charCodeAt(0));
  }
  /**
   * Splits a string into words, breaking-spaces and newLine characters
   * @param text - The text
   * @returns A tokenized array
   */
  static _tokenize(e) {
    const t = [];
    let r = "";
    if (typeof e != "string")
      return t;
    for (let i = 0; i < e.length; i++) {
      const s = e[i], n = e[i + 1];
      if (g.isBreakingSpace(s, n) || g._isNewline(s)) {
        r !== "" && (t.push(r), r = ""), s === "\r" && n === `
` ? (t.push(`\r
`), i++) : t.push(s);
        continue;
      }
      r += s;
    }
    return r !== "" && t.push(r), t;
  }
  /**
   * Overridable helper method used internally by TextMetrics, exposed to allow customizing the class's behavior.
   *
   * It allows one to customise which words should break
   * Examples are if the token is CJK or numbers.
   * It must return a boolean.
   * @param _token - The token
   * @param breakWords - The style attr break words
   * @returns Whether to break word or not
   */
  static canBreakWords(e, t) {
    return t;
  }
  /**
   * Overridable helper method used internally by TextMetrics, exposed to allow customizing the class's behavior.
   *
   * It allows one to determine whether a pair of characters
   * should be broken by newlines
   * For example certain characters in CJK langs or numbers.
   * It must return a boolean.
   * @param _char - The character
   * @param _nextChar - The next character
   * @param _token - The token/word the characters are from
   * @param _index - The index in the token of the char
   * @param _breakWords - The style attr break words
   * @returns whether to break word or not
   */
  static canBreakChars(e, t, r, i, s) {
    return !0;
  }
  /**
   * Overridable helper method used internally by TextMetrics, exposed to allow customizing the class's behavior.
   *
   * It is called when a token (usually a word) has to be split into separate pieces
   * in order to determine the point to break a word.
   * It must return an array of characters.
   * @param token - The token to split
   * @returns The characters of the token
   * @see CanvasTextMetrics.graphemeSegmenter
   */
  static wordWrapSplit(e) {
    return g.graphemeSegmenter(e);
  }
  /**
   * Calculates the ascent, descent and fontSize of a given font-style
   * @param font - String representing the style of the font
   * @returns Font properties object
   */
  static measureFont(e) {
    if (g._fonts[e])
      return g._fonts[e];
    const t = g._context;
    t.font = e;
    const r = t.measureText(g.METRICS_STRING + g.BASELINE_SYMBOL), i = {
      ascent: r.actualBoundingBoxAscent,
      descent: r.actualBoundingBoxDescent,
      fontSize: r.actualBoundingBoxAscent + r.actualBoundingBoxDescent
    };
    return g._fonts[e] = i, i;
  }
  /**
   * Clear font metrics in metrics cache.
   * @param {string} [font] - font name. If font name not set then clear cache for all fonts.
   */
  static clearMetrics(e = "") {
    e ? delete g._fonts[e] : g._fonts = {};
  }
  /**
   * Cached canvas element for measuring text
   * TODO: this should be private, but isn't because of backward compat, will fix later.
   * @ignore
   */
  static get _canvas() {
    if (!g.__canvas) {
      let e;
      try {
        const t = new OffscreenCanvas(0, 0), r = t.getContext("2d", ce);
        if (r != null && r.measureText)
          return g.__canvas = t, t;
        e = V.get().createCanvas();
      } catch {
        e = V.get().createCanvas();
      }
      e.width = e.height = 10, g.__canvas = e;
    }
    return g.__canvas;
  }
  /**
   * TODO: this should be private, but isn't because of backward compat, will fix later.
   * @ignore
   */
  static get _context() {
    return g.__context || (g.__context = g._canvas.getContext("2d", ce)), g.__context;
  }
};
z.METRICS_STRING = "|ÉqÅ";
z.BASELINE_SYMBOL = "M";
z.BASELINE_MULTIPLIER = 1.4;
z.HEIGHT_MULTIPLIER = 2;
z.graphemeSegmenter = (() => {
  if (typeof (Intl == null ? void 0 : Intl.Segmenter) == "function") {
    const o = new Intl.Segmenter();
    return (e) => {
      const t = o.segment(e), r = [];
      let i = 0;
      for (const s of t)
        r[i++] = s.segment;
      return r;
    };
  }
  return (o) => [...o];
})();
z.experimentalLetterSpacing = !1;
z._fonts = {};
z._newlines = [
  10,
  // line feed
  13
  // carriage return
];
z._breakingSpaces = [
  9,
  // character tabulation
  32,
  // space
  8192,
  // en quad
  8193,
  // em quad
  8194,
  // en space
  8195,
  // em space
  8196,
  // three-per-em space
  8197,
  // four-per-em space
  8198,
  // six-per-em space
  8200,
  // punctuation space
  8201,
  // thin space
  8202,
  // hair space
  8287,
  // medium mathematical space
  12288
  // ideographic space
];
z._measurementCache = rt(1e3);
let L = z;
const Se = class X extends $e {
  constructor(e = {}) {
    super(), this.uid = Ut("textStyle"), this._tick = 0, qt(e);
    const t = { ...X.defaultTextStyle, ...e };
    for (const r in t) {
      const i = r;
      this[i] = t[r];
    }
    this.update(), this._tick = 0;
  }
  /**
   * Alignment for multiline text, does not affect single line text.
   * @type {'left'|'center'|'right'|'justify'}
   */
  get align() {
    return this._align;
  }
  set align(e) {
    this._align = e, this.update();
  }
  /** Indicates if lines can be wrapped within words, it needs wordWrap to be set to true. */
  get breakWords() {
    return this._breakWords;
  }
  set breakWords(e) {
    this._breakWords = e, this.update();
  }
  /** Set a drop shadow for the text. */
  get dropShadow() {
    return this._dropShadow;
  }
  set dropShadow(e) {
    e !== null && typeof e == "object" ? this._dropShadow = this._createProxy({ ...X.defaultDropShadow, ...e }) : this._dropShadow = e ? this._createProxy({ ...X.defaultDropShadow }) : null, this.update();
  }
  /** The font family, can be a single font name, or a list of names where the first is the preferred font. */
  get fontFamily() {
    return this._fontFamily;
  }
  set fontFamily(e) {
    this._fontFamily = e, this.update();
  }
  /** The font size (as a number it converts to px, but as a string, equivalents are '26px','20pt','160%' or '1.6em') */
  get fontSize() {
    return this._fontSize;
  }
  set fontSize(e) {
    typeof e == "string" ? this._fontSize = parseInt(e, 10) : this._fontSize = e, this.update();
  }
  /**
   * The font style.
   * @type {'normal'|'italic'|'oblique'}
   */
  get fontStyle() {
    return this._fontStyle;
  }
  set fontStyle(e) {
    this._fontStyle = e.toLowerCase(), this.update();
  }
  /**
   * The font variant.
   * @type {'normal'|'small-caps'}
   */
  get fontVariant() {
    return this._fontVariant;
  }
  set fontVariant(e) {
    this._fontVariant = e, this.update();
  }
  /**
   * The font weight.
   * @type {'normal'|'bold'|'bolder'|'lighter'|'100'|'200'|'300'|'400'|'500'|'600'|'700'|'800'|'900'}
   */
  get fontWeight() {
    return this._fontWeight;
  }
  set fontWeight(e) {
    this._fontWeight = e, this.update();
  }
  /** The space between lines. */
  get leading() {
    return this._leading;
  }
  set leading(e) {
    this._leading = e, this.update();
  }
  /** The amount of spacing between letters, default is 0. */
  get letterSpacing() {
    return this._letterSpacing;
  }
  set letterSpacing(e) {
    this._letterSpacing = e, this.update();
  }
  /** The line height, a number that represents the vertical space that a letter uses. */
  get lineHeight() {
    return this._lineHeight;
  }
  set lineHeight(e) {
    this._lineHeight = e, this.update();
  }
  /**
   * Occasionally some fonts are cropped. Adding some padding will prevent this from happening
   * by adding padding to all sides of the text.
   * > [!NOTE] This will NOT affect the positioning or bounds of the text.
   */
  get padding() {
    return this._padding;
  }
  set padding(e) {
    this._padding = e, this.update();
  }
  /**
   * An optional filter or array of filters to apply to the text, allowing for advanced visual effects.
   * These filters will be applied to the text as it is created, resulting in faster rendering for static text
   * compared to applying the filter directly to the text object (which would be applied at run time).
   * @default null
   */
  get filters() {
    return this._filters;
  }
  set filters(e) {
    this._filters = Object.freeze(e), this.update();
  }
  /**
   * Trim transparent borders from the text texture.
   * > [!IMPORTANT] PERFORMANCE WARNING:
   * > This is a costly operation as it requires scanning pixel alpha values.
   * > Avoid using `trim: true` for dynamic text, as it could significantly impact performance.
   */
  get trim() {
    return this._trim;
  }
  set trim(e) {
    this._trim = e, this.update();
  }
  /**
   * The baseline of the text that is rendered.
   * @type {'alphabetic'|'top'|'hanging'|'middle'|'ideographic'|'bottom'}
   */
  get textBaseline() {
    return this._textBaseline;
  }
  set textBaseline(e) {
    this._textBaseline = e, this.update();
  }
  /**
   * How newlines and spaces should be handled.
   * Default is 'pre' (preserve, preserve).
   *
   *  value       | New lines     |   Spaces
   *  ---         | ---           |   ---
   * 'normal'     | Collapse      |   Collapse
   * 'pre'        | Preserve      |   Preserve
   * 'pre-line'   | Preserve      |   Collapse
   * @type {'normal'|'pre'|'pre-line'}
   */
  get whiteSpace() {
    return this._whiteSpace;
  }
  set whiteSpace(e) {
    this._whiteSpace = e, this.update();
  }
  /** Indicates if word wrap should be used. */
  get wordWrap() {
    return this._wordWrap;
  }
  set wordWrap(e) {
    this._wordWrap = e, this.update();
  }
  /** The width at which text will wrap, it needs wordWrap to be set to true. */
  get wordWrapWidth() {
    return this._wordWrapWidth;
  }
  set wordWrapWidth(e) {
    this._wordWrapWidth = e, this.update();
  }
  /**
   * The fill style that will be used to color the text.
   * This can be:
   * - A color string like 'red', '#00FF00', or 'rgba(255,0,0,0.5)'
   * - A hex number like 0xff0000 for red
   * - A FillStyle object with properties like { color: 0xff0000, alpha: 0.5 }
   * - A FillGradient for gradient fills
   * - A FillPattern for pattern/texture fills
   *
   * When using a FillGradient, vertical gradients (angle of 90 degrees) are applied per line of text,
   * while gradients at any other angle are spread across the entire text body as a whole.
   * @example
   * // Vertical gradient applied per line
   * const verticalGradient = new FillGradient(0, 0, 0, 1)
   *     .addColorStop(0, 0xff0000)
   *     .addColorStop(1, 0x0000ff);
   *
   * const text = new Text({
   *     text: 'Line 1\nLine 2',
   *     style: { fill: verticalGradient }
   * });
   *
   * To manage the gradient in a global scope, set the textureSpace property of the FillGradient to 'global'.
   * @type {string|number|FillStyle|FillGradient|FillPattern}
   */
  get fill() {
    return this._originalFill;
  }
  set fill(e) {
    e !== this._originalFill && (this._originalFill = e, this._isFillStyle(e) && (this._originalFill = this._createProxy({ ...Y.defaultFillStyle, ...e }, () => {
      this._fill = ke(
        { ...this._originalFill },
        Y.defaultFillStyle
      );
    })), this._fill = ke(
      e === 0 ? "black" : e,
      Y.defaultFillStyle
    ), this.update());
  }
  /** A fillstyle that will be used on the text stroke, e.g., 'blue', '#FCFF00'. */
  get stroke() {
    return this._originalStroke;
  }
  set stroke(e) {
    e !== this._originalStroke && (this._originalStroke = e, this._isFillStyle(e) && (this._originalStroke = this._createProxy({ ...Y.defaultStrokeStyle, ...e }, () => {
      this._stroke = Re(
        { ...this._originalStroke },
        Y.defaultStrokeStyle
      );
    })), this._stroke = Re(e, Y.defaultStrokeStyle), this.update());
  }
  update() {
    this._tick++, this.emit("update", this);
  }
  /** Resets all properties to the default values */
  reset() {
    const e = X.defaultTextStyle;
    for (const t in e)
      this[t] = e[t];
  }
  /**
   * Returns a unique key for this instance.
   * This key is used for caching.
   * @returns {string} Unique key for the instance
   */
  get styleKey() {
    return `${this.uid}-${this._tick}`;
  }
  /**
   * Creates a new TextStyle object with the same values as this one.
   * @returns New cloned TextStyle object
   */
  clone() {
    return new X({
      align: this.align,
      breakWords: this.breakWords,
      dropShadow: this._dropShadow ? { ...this._dropShadow } : null,
      fill: this._fill,
      fontFamily: this.fontFamily,
      fontSize: this.fontSize,
      fontStyle: this.fontStyle,
      fontVariant: this.fontVariant,
      fontWeight: this.fontWeight,
      leading: this.leading,
      letterSpacing: this.letterSpacing,
      lineHeight: this.lineHeight,
      padding: this.padding,
      stroke: this._stroke,
      textBaseline: this.textBaseline,
      whiteSpace: this.whiteSpace,
      wordWrap: this.wordWrap,
      wordWrapWidth: this.wordWrapWidth,
      filters: this._filters ? [...this._filters] : void 0
    });
  }
  /**
   * Returns the final padding for the text style, taking into account any filters applied.
   * Used internally for correct measurements
   * @internal
   * @returns {number} The final padding for the text style.
   */
  _getFinalPadding() {
    let e = 0;
    if (this._filters)
      for (let t = 0; t < this._filters.length; t++)
        e += this._filters[t].padding;
    return Math.max(this._padding, e);
  }
  /**
   * Destroys this text style.
   * @param options - Options parameter. A boolean will act as if all options
   *  have been set to that value
   * @example
   * // Destroy the text style and its textures
   * textStyle.destroy({ texture: true, textureSource: true });
   * textStyle.destroy(true);
   */
  destroy(e = !1) {
    var r, i, s, n;
    if (this.removeAllListeners(), typeof e == "boolean" ? e : e == null ? void 0 : e.texture) {
      const a = typeof e == "boolean" ? e : e == null ? void 0 : e.textureSource;
      (r = this._fill) != null && r.texture && this._fill.texture.destroy(a), (i = this._originalFill) != null && i.texture && this._originalFill.texture.destroy(a), (s = this._stroke) != null && s.texture && this._stroke.texture.destroy(a), (n = this._originalStroke) != null && n.texture && this._originalStroke.texture.destroy(a);
    }
    this._fill = null, this._stroke = null, this.dropShadow = null, this._originalStroke = null, this._originalFill = null;
  }
  _createProxy(e, t) {
    return new Proxy(e, {
      set: (r, i, s) => (r[i] = s, t == null || t(i, s), this.update(), !0)
    });
  }
  _isFillStyle(e) {
    return (e ?? null) !== null && !(E.isColorLike(e) || e instanceof re || e instanceof ye);
  }
};
Se.defaultDropShadow = {
  alpha: 1,
  angle: Math.PI / 6,
  blur: 0,
  color: "black",
  distance: 5
};
Se.defaultTextStyle = {
  align: "left",
  breakWords: !1,
  dropShadow: null,
  fill: "black",
  fontFamily: "Arial",
  fontSize: 26,
  fontStyle: "normal",
  fontVariant: "normal",
  fontWeight: "normal",
  leading: 0,
  letterSpacing: 0,
  lineHeight: 0,
  padding: 0,
  stroke: null,
  textBaseline: "alphabetic",
  trim: !1,
  whiteSpace: "pre",
  wordWrap: !1,
  wordWrapWidth: 100
};
let N = Se;
function qt(o) {
  const e = o;
  if (typeof e.dropShadow == "boolean" && e.dropShadow) {
    const t = N.defaultDropShadow;
    o.dropShadow = {
      alpha: e.dropShadowAlpha ?? t.alpha,
      angle: e.dropShadowAngle ?? t.angle,
      blur: e.dropShadowBlur ?? t.blur,
      color: e.dropShadowColor ?? t.color,
      distance: e.dropShadowDistance ?? t.distance
    };
  }
  if (e.strokeThickness !== void 0) {
    B(G, "strokeThickness is now a part of stroke");
    const t = e.stroke;
    let r = {};
    if (E.isColorLike(t))
      r.color = t;
    else if (t instanceof re || t instanceof ye)
      r.fill = t;
    else if (Object.hasOwnProperty.call(t, "color") || Object.hasOwnProperty.call(t, "fill"))
      r = t;
    else
      throw new Error("Invalid stroke value.");
    o.stroke = {
      ...r,
      width: e.strokeThickness
    };
  }
  if (Array.isArray(e.fillGradientStops)) {
    if (B(G, "gradient fill is now a fill pattern: `new FillGradient(...)`"), !Array.isArray(e.fill) || e.fill.length === 0)
      throw new Error("Invalid fill value. Expected an array of colors for gradient fill.");
    e.fill.length !== e.fillGradientStops.length && $("The number of fill colors must match the number of fill gradient stops.");
    const t = new re({
      start: { x: 0, y: 0 },
      end: { x: 0, y: 1 },
      textureSpace: "local"
    }), r = e.fillGradientStops.slice(), i = e.fill.map((s) => E.shared.setValue(s).toNumber());
    r.forEach((s, n) => {
      t.addColorStop(s, i[n]);
    }), o.fill = {
      fill: t
    };
  }
}
const Ue = 1e5;
function oe(o, e, t, r = 0) {
  if (o.texture === M.WHITE && !o.fill)
    return E.shared.setValue(o.color).setAlpha(o.alpha ?? 1).toHexa();
  if (o.fill) {
    if (o.fill instanceof ye) {
      const i = o.fill, s = e.createPattern(i.texture.source.resource, "repeat"), n = i.transform.copyTo(U.shared);
      return n.scale(
        i.texture.frame.width,
        i.texture.frame.height
      ), s.setTransform(n), s;
    } else if (o.fill instanceof re) {
      const i = o.fill, s = i.type === "linear", n = i.textureSpace === "local";
      let a = 1, l = 1;
      n && t && (a = t.width + r, l = t.height + r);
      let u, h = !1;
      if (s) {
        const { start: c, end: d } = i;
        u = e.createLinearGradient(
          c.x * a,
          c.y * l,
          d.x * a,
          d.y * l
        ), h = Math.abs(d.x - c.x) < Math.abs((d.y - c.y) * 0.1);
      } else {
        const { center: c, innerRadius: d, outerCenter: f, outerRadius: m } = i;
        u = e.createRadialGradient(
          c.x * a,
          c.y * l,
          d * a,
          f.x * a,
          f.y * l,
          m * a
        );
      }
      if (h && n && t) {
        const c = t.lineHeight / l;
        for (let d = 0; d < t.lines.length; d++) {
          const f = (d * t.lineHeight + r / 2) / l;
          i.colorStops.forEach((m) => {
            const x = f + m.offset * c;
            u.addColorStop(
              // fix to 5 decimal places to avoid floating point precision issues
              Math.floor(x * Ue) / Ue,
              E.shared.setValue(m.color).toHex()
            );
          });
        }
      } else
        i.colorStops.forEach((c) => {
          u.addColorStop(c.offset, E.shared.setValue(c.color).toHex());
        });
      return u;
    }
  } else {
    const i = e.createPattern(o.texture.source.resource, "repeat"), s = o.matrix.copyTo(U.shared);
    return s.scale(o.texture.frame.width, o.texture.frame.height), i.setTransform(s), i;
  }
  return $("FillStyle not recognised", o), "red";
}
const it = class st extends jt {
  /**
   * @param options - The options for the dynamic bitmap font.
   */
  constructor(e) {
    super(), this.resolution = 1, this.pages = [], this._padding = 0, this._measureCache = /* @__PURE__ */ Object.create(null), this._currentChars = [], this._currentX = 0, this._currentY = 0, this._currentMaxCharHeight = 0, this._currentPageIndex = -1, this._skipKerning = !1;
    const t = { ...st.defaultOptions, ...e };
    this._textureSize = t.textureSize, this._mipmap = t.mipmap;
    const r = t.style.clone();
    t.overrideFill && (r._fill.color = 16777215, r._fill.alpha = 1, r._fill.texture = M.WHITE, r._fill.fill = null), this.applyFillAsTint = t.overrideFill;
    const i = r.fontSize;
    r.fontSize = this.baseMeasurementFontSize;
    const s = ae(r);
    t.overrideSize ? r._stroke && (r._stroke.width *= this.baseRenderedFontSize / i) : r.fontSize = this.baseRenderedFontSize = i, this._style = r, this._skipKerning = t.skipKerning ?? !1, this.resolution = t.resolution ?? 1, this._padding = t.padding ?? 4, t.textureStyle && (this._textureStyle = t.textureStyle instanceof J ? t.textureStyle : new J(t.textureStyle)), this.fontMetrics = L.measureFont(s), this.lineHeight = r.lineHeight || this.fontMetrics.fontSize || r.fontSize;
  }
  ensureCharacters(e) {
    var _, p;
    const t = L.graphemeSegmenter(e).filter((b) => !this._currentChars.includes(b)).filter((b, y, T) => T.indexOf(b) === y);
    if (!t.length)
      return;
    this._currentChars = [...this._currentChars, ...t];
    let r;
    this._currentPageIndex === -1 ? r = this._nextPage() : r = this.pages[this._currentPageIndex];
    let { canvas: i, context: s } = r.canvasAndContext, n = r.texture.source;
    const a = this._style;
    let l = this._currentX, u = this._currentY, h = this._currentMaxCharHeight;
    const c = this.baseRenderedFontSize / this.baseMeasurementFontSize, d = this._padding * c;
    let f = !1;
    const m = i.width / this.resolution, x = i.height / this.resolution;
    for (let b = 0; b < t.length; b++) {
      const y = t[b], T = L.measureText(y, a, i, !1);
      T.lineHeight = T.height;
      const S = T.width * c, k = Math.ceil((a.fontStyle === "italic" ? 2 : 1) * S), v = T.height * c, F = k + d * 2, R = v + d * 2;
      if (f = !1, y !== `
` && y !== "\r" && y !== "	" && y !== " " && (f = !0, h = Math.ceil(Math.max(R, h))), l + F > m && (u += h, h = R, l = 0, u + h > x)) {
        n.update();
        const I = this._nextPage();
        i = I.canvasAndContext.canvas, s = I.canvasAndContext.context, n = I.texture.source, l = 0, u = 0, h = 0;
      }
      const ue = S / c - (((_ = a.dropShadow) == null ? void 0 : _.distance) ?? 0) - (((p = a._stroke) == null ? void 0 : p.width) ?? 0);
      if (this.chars[y] = {
        id: y.codePointAt(0),
        xOffset: -this._padding,
        yOffset: -this._padding,
        xAdvance: ue,
        kerning: {}
      }, f) {
        this._drawGlyph(
          s,
          T,
          l + d,
          u + d,
          c,
          a
        );
        const I = n.width * c, q = n.height * c, C = new ie(
          l / I * n.width,
          u / q * n.height,
          F / I * n.width,
          R / q * n.height
        );
        this.chars[y].texture = new M({
          source: n,
          frame: C
        }), l += Math.ceil(F);
      }
    }
    n.update(), this._currentX = l, this._currentY = u, this._currentMaxCharHeight = h, this._skipKerning && this._applyKerning(t, s);
  }
  /**
   * @deprecated since 8.0.0
   * The map of base page textures (i.e., sheets of glyphs).
   */
  get pageTextures() {
    return B(G, "BitmapFont.pageTextures is deprecated, please use BitmapFont.pages instead."), this.pages;
  }
  _applyKerning(e, t) {
    const r = this._measureCache;
    for (let i = 0; i < e.length; i++) {
      const s = e[i];
      for (let n = 0; n < this._currentChars.length; n++) {
        const a = this._currentChars[n];
        let l = r[s];
        l || (l = r[s] = t.measureText(s).width);
        let u = r[a];
        u || (u = r[a] = t.measureText(a).width);
        let h = t.measureText(s + a).width, c = h - (l + u);
        c && (this.chars[s].kerning[a] = c), h = t.measureText(s + a).width, c = h - (l + u), c && (this.chars[a].kerning[s] = c);
      }
    }
  }
  _nextPage() {
    this._currentPageIndex++;
    const e = this.resolution, t = K.getOptimalCanvasAndContext(
      this._textureSize,
      this._textureSize,
      e
    );
    this._setupContext(t.context, this._style, e);
    const r = e * (this.baseRenderedFontSize / this.baseMeasurementFontSize), i = new M({
      source: new Gt({
        resource: t.canvas,
        resolution: r,
        alphaMode: "premultiply-alpha-on-upload",
        autoGenerateMipmaps: this._mipmap
      })
    });
    this._textureStyle && (i.source.style = this._textureStyle);
    const s = {
      canvasAndContext: t,
      texture: i
    };
    return this.pages[this._currentPageIndex] = s, s;
  }
  // canvas style!
  _setupContext(e, t, r) {
    t.fontSize = this.baseRenderedFontSize, e.scale(r, r), e.font = ae(t), t.fontSize = this.baseMeasurementFontSize, e.textBaseline = t.textBaseline;
    const i = t._stroke, s = (i == null ? void 0 : i.width) ?? 0;
    if (i && (e.lineWidth = s, e.lineJoin = i.join, e.miterLimit = i.miterLimit, e.strokeStyle = oe(i, e)), t._fill && (e.fillStyle = oe(t._fill, e)), t.dropShadow) {
      const n = t.dropShadow, a = E.shared.setValue(n.color).toArray(), l = n.blur * r, u = n.distance * r;
      e.shadowColor = `rgba(${a[0] * 255},${a[1] * 255},${a[2] * 255},${n.alpha})`, e.shadowBlur = l, e.shadowOffsetX = Math.cos(n.angle) * u, e.shadowOffsetY = Math.sin(n.angle) * u;
    } else
      e.shadowColor = "black", e.shadowBlur = 0, e.shadowOffsetX = 0, e.shadowOffsetY = 0;
  }
  _drawGlyph(e, t, r, i, s, n) {
    const a = t.text, l = t.fontProperties, u = n._stroke, h = ((u == null ? void 0 : u.width) ?? 0) * s, c = r + h / 2, d = i - h / 2, f = l.descent * s, m = t.lineHeight * s;
    let x = !1;
    n.stroke && h && (x = !0, e.strokeText(a, c, d + m - f));
    const { shadowBlur: _, shadowOffsetX: p, shadowOffsetY: b } = e;
    n._fill && (x && (e.shadowBlur = 0, e.shadowOffsetX = 0, e.shadowOffsetY = 0), e.fillText(a, c, d + m - f)), x && (e.shadowBlur = _, e.shadowOffsetX = p, e.shadowOffsetY = b);
  }
  destroy() {
    super.destroy();
    for (let e = 0; e < this.pages.length; e++) {
      const { canvasAndContext: t, texture: r } = this.pages[e];
      K.returnCanvasAndContext(t), r.destroy(!0);
    }
    this.pages = null;
  }
};
it.defaultOptions = {
  textureSize: 512,
  style: new N(),
  mipmap: !0
};
let Ge = it;
function nt(o, e, t, r) {
  const i = {
    width: 0,
    height: 0,
    offsetY: 0,
    scale: e.fontSize / t.baseMeasurementFontSize,
    lines: [{
      width: 0,
      charPositions: [],
      spaceWidth: 0,
      spacesIndex: [],
      chars: []
    }]
  };
  i.offsetY = t.baseLineOffset;
  let s = i.lines[0], n = null, a = !0;
  const l = {
    width: 0,
    start: 0,
    index: 0,
    // use index to not modify the array as we use it a lot!
    positions: [],
    chars: []
  }, u = t.baseMeasurementFontSize / e.fontSize, h = e.letterSpacing * u, c = e.wordWrapWidth * u, d = e.lineHeight ? e.lineHeight * u : t.lineHeight, f = e.wordWrap && e.breakWords, m = (p) => {
    const b = s.width;
    for (let y = 0; y < l.index; y++) {
      const T = p.positions[y];
      s.chars.push(p.chars[y]), s.charPositions.push(T + b);
    }
    s.width += p.width, a = !1, l.width = 0, l.index = 0, l.chars.length = 0;
  }, x = () => {
    let p = s.chars.length - 1;
    if (r) {
      let b = s.chars[p];
      for (; b === " "; )
        s.width -= t.chars[b].xAdvance, b = s.chars[--p];
    }
    i.width = Math.max(i.width, s.width), s = {
      width: 0,
      charPositions: [],
      chars: [],
      spaceWidth: 0,
      spacesIndex: []
    }, a = !0, i.lines.push(s), i.height += d;
  }, _ = (p) => p - h > c;
  for (let p = 0; p < o.length + 1; p++) {
    let b;
    const y = p === o.length;
    y || (b = o[p]);
    const T = t.chars[b] || t.chars[" "];
    if (/(?:\s)/.test(b) || b === "\r" || b === `
` || y) {
      if (!a && e.wordWrap && _(s.width + l.width) ? (x(), m(l), y || s.charPositions.push(0)) : (l.start = s.width, m(l), y || s.charPositions.push(0)), b === "\r" || b === `
`)
        x();
      else if (!y) {
        const F = T.xAdvance + (T.kerning[n] || 0) + h;
        s.width += F, s.spaceWidth = F, s.spacesIndex.push(s.charPositions.length), s.chars.push(b);
      }
    } else {
      const v = T.kerning[n] || 0, F = T.xAdvance + v + h;
      f && _(s.width + l.width + F) && (m(l), x()), l.positions[l.index++] = l.width + v, l.chars.push(b), l.width += F;
    }
    n = b;
  }
  return x(), e.align === "center" ? Qt(i) : e.align === "right" ? Jt(i) : e.align === "justify" && Zt(i), i;
}
function Qt(o) {
  for (let e = 0; e < o.lines.length; e++) {
    const t = o.lines[e], r = o.width / 2 - t.width / 2;
    for (let i = 0; i < t.charPositions.length; i++)
      t.charPositions[i] += r;
  }
}
function Jt(o) {
  for (let e = 0; e < o.lines.length; e++) {
    const t = o.lines[e], r = o.width - t.width;
    for (let i = 0; i < t.charPositions.length; i++)
      t.charPositions[i] += r;
  }
}
function Zt(o) {
  const e = o.width;
  for (let t = 0; t < o.lines.length; t++) {
    const r = o.lines[t];
    let i = 0, s = r.spacesIndex[i++], n = 0;
    const a = r.spacesIndex.length, u = (e - r.width) / a;
    for (let h = 0; h < r.charPositions.length; h++)
      h === s && (s = r.spacesIndex[i++], n += u), r.charPositions[h] += n;
  }
}
function er(o) {
  if (o === "")
    return [];
  typeof o == "string" && (o = [o]);
  const e = [];
  for (let t = 0, r = o.length; t < r; t++) {
    const i = o[t];
    if (Array.isArray(i)) {
      if (i.length !== 2)
        throw new Error(`[BitmapFont]: Invalid character range length, expecting 2 got ${i.length}.`);
      if (i[0].length === 0 || i[1].length === 0)
        throw new Error("[BitmapFont]: Invalid character delimiter.");
      const s = i[0].charCodeAt(0), n = i[1].charCodeAt(0);
      if (n < s)
        throw new Error("[BitmapFont]: Invalid character range.");
      for (let a = s, l = n; a <= l; a++)
        e.push(String.fromCharCode(a));
    } else
      e.push(...Array.from(i));
  }
  if (e.length === 0)
    throw new Error("[BitmapFont]: Empty set when resolving characters.");
  return e;
}
let ee = 0;
class tr {
  constructor() {
    this.ALPHA = [["a", "z"], ["A", "Z"], " "], this.NUMERIC = [["0", "9"]], this.ALPHANUMERIC = [["a", "z"], ["A", "Z"], ["0", "9"], " "], this.ASCII = [[" ", "~"]], this.defaultOptions = {
      chars: this.ALPHANUMERIC,
      resolution: 1,
      padding: 4,
      skipKerning: !1,
      textureStyle: null
    }, this.measureCache = rt(1e3);
  }
  /**
   * Get a font for the specified text and style.
   * @param text - The text to get the font for
   * @param style - The style to use
   */
  getFont(e, t) {
    var n;
    let r = `${t.fontFamily}-bitmap`, i = !0;
    if (t._fill.fill && !t._stroke ? (r += t._fill.fill.styleKey, i = !1) : (t._stroke || t.dropShadow) && (r = `${t.styleKey}-bitmap`, i = !1), !A.has(r)) {
      const a = Object.create(t);
      a.lineHeight = 0;
      const l = new Ge({
        style: a,
        overrideFill: i,
        overrideSize: !0,
        ...this.defaultOptions
      });
      ee++, ee > 50 && $("BitmapText", `You have dynamically created ${ee} bitmap fonts, this can be inefficient. Try pre installing your font styles using \`BitmapFont.install({name:"style1", style})\``), l.once("destroy", () => {
        ee--, A.remove(r);
      }), A.set(
        r,
        l
      );
    }
    const s = A.get(r);
    return (n = s.ensureCharacters) == null || n.call(s, e), s;
  }
  /**
   * Get the layout of a text for the specified style.
   * @param text - The text to get the layout for
   * @param style - The style to use
   * @param trimEnd - Whether to ignore whitespaces at the end of each line
   */
  getLayout(e, t, r = !0) {
    const i = this.getFont(e, t), s = `${e}-${t.styleKey}-${r}`;
    if (this.measureCache.has(s))
      return this.measureCache.get(s);
    const n = L.graphemeSegmenter(e), a = nt(n, t, i, r);
    return this.measureCache.set(s, a), a;
  }
  /**
   * Measure the text using the specified style.
   * @param text - The text to measure
   * @param style - The style to use
   * @param trimEnd - Whether to ignore whitespaces at the end of each line
   */
  measureText(e, t, r = !0) {
    return this.getLayout(e, t, r);
  }
  // eslint-disable-next-line max-len
  install(...e) {
    var u, h, c, d;
    let t = e[0];
    typeof t == "string" && (t = {
      name: t,
      style: e[1],
      chars: (u = e[2]) == null ? void 0 : u.chars,
      resolution: (h = e[2]) == null ? void 0 : h.resolution,
      padding: (c = e[2]) == null ? void 0 : c.padding,
      skipKerning: (d = e[2]) == null ? void 0 : d.skipKerning
    }, B(G, "BitmapFontManager.install(name, style, options) is deprecated, use BitmapFontManager.install({name, style, ...options})"));
    const r = t == null ? void 0 : t.name;
    if (!r)
      throw new Error("[BitmapFontManager] Property `name` is required.");
    t = { ...this.defaultOptions, ...t };
    const i = t.style, s = i instanceof N ? i : new N(i), n = t.dynamicFill ?? this._canUseTintForStyle(s), a = new Ge({
      style: s,
      overrideFill: n,
      skipKerning: t.skipKerning,
      padding: t.padding,
      resolution: t.resolution,
      overrideSize: !1,
      textureStyle: t.textureStyle
    }), l = er(t.chars);
    return a.ensureCharacters(l.join("")), A.set(`${r}-bitmap`, a), a.once("destroy", () => A.remove(`${r}-bitmap`)), a;
  }
  /**
   * Uninstalls a bitmap font from the cache.
   * @param {string} name - The name of the bitmap font to uninstall.
   */
  uninstall(e) {
    const t = `${e}-bitmap`, r = A.get(t);
    r && r.destroy();
  }
  /**
   * Determines if a style can use tinting instead of baking colors into the bitmap.
   * Tinting is more efficient as it allows reusing the same bitmap with different colors.
   * @param style - The text style to evaluate
   * @returns true if the style can use tinting, false if colors must be baked in
   * @private
   */
  _canUseTintForStyle(e) {
    return !e._stroke && (!e.dropShadow || e.dropShadow.color === 0) && !e._fill.fill && e._fill.color === 16777215;
  }
}
const rr = new tr();
class at {
  constructor(e) {
    this._renderer = e;
  }
  push(e, t, r) {
    this._renderer.renderPipes.batch.break(r), r.add({
      renderPipeId: "filter",
      canBundle: !1,
      action: "pushFilter",
      container: t,
      filterEffect: e
    });
  }
  pop(e, t, r) {
    this._renderer.renderPipes.batch.break(r), r.add({
      renderPipeId: "filter",
      action: "popFilter",
      canBundle: !1
    });
  }
  execute(e) {
    e.action === "pushFilter" ? this._renderer.filter.push(e) : e.action === "popFilter" && this._renderer.filter.pop();
  }
  destroy() {
    this._renderer = null;
  }
}
at.extension = {
  type: [
    w.WebGLPipes,
    w.WebGPUPipes,
    w.CanvasPipes
  ],
  name: "filter"
};
const ze = new U();
function ir(o, e) {
  e.clear();
  const t = e.matrix;
  for (let r = 0; r < o.length; r++) {
    const i = o[r];
    if (i.globalDisplayStatus < 7)
      continue;
    const s = i.renderGroup ?? i.parentRenderGroup;
    s != null && s.isCachedAsTexture ? e.matrix = ze.copyFrom(s.textureOffsetInverseTransform).append(i.worldTransform) : s != null && s._parentCacheAsTextureRenderGroup ? e.matrix = ze.copyFrom(s._parentCacheAsTextureRenderGroup.inverseWorldTransform).append(i.groupTransform) : e.matrix = i.worldTransform, e.addBounds(i.bounds);
  }
  return e.matrix = t, e;
}
const sr = new be({
  attributes: {
    aPosition: {
      buffer: new Float32Array([0, 0, 1, 0, 1, 1, 0, 1]),
      format: "float32x2",
      stride: 2 * 4,
      offset: 0
    }
  },
  indexBuffer: new Uint32Array([0, 1, 2, 0, 2, 3])
});
class nr {
  constructor() {
    this.skip = !1, this.inputTexture = null, this.backTexture = null, this.filters = null, this.bounds = new Ke(), this.container = null, this.blendRequired = !1, this.outputRenderSurface = null, this.globalFrame = { x: 0, y: 0, width: 0, height: 0 };
  }
}
class ot {
  constructor(e) {
    this._filterStackIndex = 0, this._filterStack = [], this._filterGlobalUniforms = new j({
      uInputSize: { value: new Float32Array(4), type: "vec4<f32>" },
      uInputPixel: { value: new Float32Array(4), type: "vec4<f32>" },
      uInputClamp: { value: new Float32Array(4), type: "vec4<f32>" },
      uOutputFrame: { value: new Float32Array(4), type: "vec4<f32>" },
      uGlobalFrame: { value: new Float32Array(4), type: "vec4<f32>" },
      uOutputTexture: { value: new Float32Array(4), type: "vec4<f32>" }
    }), this._globalFilterBindGroup = new je({}), this.renderer = e;
  }
  /**
   * The back texture of the currently active filter. Requires the filter to have `blendRequired` set to true.
   * @readonly
   */
  get activeBackTexture() {
    var e;
    return (e = this._activeFilterData) == null ? void 0 : e.backTexture;
  }
  /**
   * Pushes a filter instruction onto the filter stack.
   * @param instruction - The instruction containing the filter effect and container.
   * @internal
   */
  push(e) {
    const t = this.renderer, r = e.filterEffect.filters, i = this._pushFilterData();
    i.skip = !1, i.filters = r, i.container = e.container, i.outputRenderSurface = t.renderTarget.renderSurface;
    const s = t.renderTarget.renderTarget.colorTexture.source, n = s.resolution, a = s.antialias;
    if (r.length === 0) {
      i.skip = !0;
      return;
    }
    const l = i.bounds;
    if (this._calculateFilterArea(e, l), this._calculateFilterBounds(i, t.renderTarget.rootViewPort, a, n, 1), i.skip)
      return;
    const u = this._getPreviousFilterData(), h = this._findFilterResolution(n);
    let c = 0, d = 0;
    u && (c = u.bounds.minX, d = u.bounds.minY), this._calculateGlobalFrame(
      i,
      c,
      d,
      h,
      s.width,
      s.height
    ), this._setupFilterTextures(i, l, t, u);
  }
  /**
   * Applies filters to a texture.
   *
   * This method takes a texture and a list of filters, applies the filters to the texture,
   * and returns the resulting texture.
   * @param {object} params - The parameters for applying filters.
   * @param {Texture} params.texture - The texture to apply filters to.
   * @param {Filter[]} params.filters - The filters to apply.
   * @returns {Texture} The resulting texture after all filters have been applied.
   * @example
   *
   * ```ts
   * // Create a texture and a list of filters
   * const texture = new Texture(...);
   * const filters = [new BlurFilter(), new ColorMatrixFilter()];
   *
   * // Apply the filters to the texture
   * const resultTexture = filterSystem.applyToTexture({ texture, filters });
   *
   * // Use the resulting texture
   * sprite.texture = resultTexture;
   * ```
   *
   * Key Points:
   * 1. padding is not currently supported here - so clipping may occur with filters that use padding.
   * 2. If all filters are disabled or skipped, the original texture is returned.
   */
  generateFilteredTexture({ texture: e, filters: t }) {
    const r = this._pushFilterData();
    this._activeFilterData = r, r.skip = !1, r.filters = t;
    const i = e.source, s = i.resolution, n = i.antialias;
    if (t.length === 0)
      return r.skip = !0, e;
    const a = r.bounds;
    if (a.addRect(e.frame), this._calculateFilterBounds(r, a.rectangle, n, s, 0), r.skip)
      return e;
    const l = s;
    this._calculateGlobalFrame(
      r,
      0,
      0,
      l,
      i.width,
      i.height
    ), r.outputRenderSurface = W.getOptimalTexture(
      a.width,
      a.height,
      r.resolution,
      r.antialias
    ), r.backTexture = M.EMPTY, r.inputTexture = e, this.renderer.renderTarget.finishRenderPass(), this._applyFiltersToTexture(r, !0);
    const d = r.outputRenderSurface;
    return d.source.alphaMode = "premultiplied-alpha", d;
  }
  /** @internal */
  pop() {
    const e = this.renderer, t = this._popFilterData();
    t.skip || (e.globalUniforms.pop(), e.renderTarget.finishRenderPass(), this._activeFilterData = t, this._applyFiltersToTexture(t, !1), t.blendRequired && W.returnTexture(t.backTexture), W.returnTexture(t.inputTexture));
  }
  /**
   * Copies the last render surface to a texture.
   * @param lastRenderSurface - The last render surface to copy from.
   * @param bounds - The bounds of the area to copy.
   * @param previousBounds - The previous bounds to use for offsetting the copy.
   */
  getBackTexture(e, t, r) {
    const i = e.colorTexture.source._resolution, s = W.getOptimalTexture(
      t.width,
      t.height,
      i,
      !1
    );
    let n = t.minX, a = t.minY;
    r && (n -= r.minX, a -= r.minY), n = Math.floor(n * i), a = Math.floor(a * i);
    const l = Math.ceil(t.width * i), u = Math.ceil(t.height * i);
    return this.renderer.renderTarget.copyToTexture(
      e,
      s,
      { x: n, y: a },
      { width: l, height: u },
      { x: 0, y: 0 }
    ), s;
  }
  /**
   * Applies a filter to a texture.
   * @param filter - The filter to apply.
   * @param input - The input texture.
   * @param output - The output render surface.
   * @param clear - Whether to clear the output surface before applying the filter.
   */
  applyFilter(e, t, r, i) {
    const s = this.renderer, n = this._activeFilterData, l = n.outputRenderSurface === r, u = s.renderTarget.rootRenderTarget.colorTexture.source._resolution, h = this._findFilterResolution(u);
    let c = 0, d = 0;
    if (l) {
      const f = this._findPreviousFilterOffset();
      c = f.x, d = f.y;
    }
    this._updateFilterUniforms(t, r, n, c, d, h, l, i), this._setupBindGroupsAndRender(e, t, s);
  }
  /**
   * Multiply _input normalized coordinates_ to this matrix to get _sprite texture normalized coordinates_.
   *
   * Use `outputMatrix * vTextureCoord` in the shader.
   * @param outputMatrix - The matrix to output to.
   * @param {Sprite} sprite - The sprite to map to.
   * @returns The mapped matrix.
   */
  calculateSpriteMatrix(e, t) {
    const r = this._activeFilterData, i = e.set(
      r.inputTexture._source.width,
      0,
      0,
      r.inputTexture._source.height,
      r.bounds.minX,
      r.bounds.minY
    ), s = t.worldTransform.copyTo(U.shared), n = t.renderGroup || t.parentRenderGroup;
    return n && n.cacheToLocalTransform && s.prepend(n.cacheToLocalTransform), s.invert(), i.prepend(s), i.scale(
      1 / t.texture.orig.width,
      1 / t.texture.orig.height
    ), i.translate(t.anchor.x, t.anchor.y), i;
  }
  destroy() {
  }
  /**
   * Sets up the bind groups and renders the filter.
   * @param filter - The filter to apply
   * @param input - The input texture
   * @param renderer - The renderer instance
   */
  _setupBindGroupsAndRender(e, t, r) {
    if (r.renderPipes.uniformBatch) {
      const i = r.renderPipes.uniformBatch.getUboResource(this._filterGlobalUniforms);
      this._globalFilterBindGroup.setResource(i, 0);
    } else
      this._globalFilterBindGroup.setResource(this._filterGlobalUniforms, 0);
    this._globalFilterBindGroup.setResource(t.source, 1), this._globalFilterBindGroup.setResource(t.source.style, 2), e.groups[0] = this._globalFilterBindGroup, r.encoder.draw({
      geometry: sr,
      shader: e,
      state: e._state,
      topology: "triangle-list"
    }), r.type === we.WEBGL && r.renderTarget.finishRenderPass();
  }
  /**
   * Sets up the filter textures including input texture and back texture if needed.
   * @param filterData - The filter data to update
   * @param bounds - The bounds for the texture
   * @param renderer - The renderer instance
   * @param previousFilterData - The previous filter data for back texture calculation
   */
  _setupFilterTextures(e, t, r, i) {
    if (e.backTexture = M.EMPTY, e.inputTexture = W.getOptimalTexture(
      t.width,
      t.height,
      e.resolution,
      e.antialias
    ), e.blendRequired) {
      r.renderTarget.finishRenderPass();
      const s = r.renderTarget.getRenderTarget(e.outputRenderSurface);
      e.backTexture = this.getBackTexture(s, t, i == null ? void 0 : i.bounds);
    }
    r.renderTarget.bind(e.inputTexture, !0), r.globalUniforms.push({
      offset: t
    });
  }
  /**
   * Calculates and sets the global frame for the filter.
   * @param filterData - The filter data to update
   * @param offsetX - The X offset
   * @param offsetY - The Y offset
   * @param globalResolution - The global resolution
   * @param sourceWidth - The source texture width
   * @param sourceHeight - The source texture height
   */
  _calculateGlobalFrame(e, t, r, i, s, n) {
    const a = e.globalFrame;
    a.x = t * i, a.y = r * i, a.width = s * i, a.height = n * i;
  }
  /**
   * Updates the filter uniforms with the current filter state.
   * @param input - The input texture
   * @param output - The output render surface
   * @param filterData - The current filter data
   * @param offsetX - The X offset for positioning
   * @param offsetY - The Y offset for positioning
   * @param resolution - The current resolution
   * @param isFinalTarget - Whether this is the final render target
   * @param clear - Whether to clear the output surface
   */
  _updateFilterUniforms(e, t, r, i, s, n, a, l) {
    const u = this._filterGlobalUniforms.uniforms, h = u.uOutputFrame, c = u.uInputSize, d = u.uInputPixel, f = u.uInputClamp, m = u.uGlobalFrame, x = u.uOutputTexture;
    a ? (h[0] = r.bounds.minX - i, h[1] = r.bounds.minY - s) : (h[0] = 0, h[1] = 0), h[2] = e.frame.width, h[3] = e.frame.height, c[0] = e.source.width, c[1] = e.source.height, c[2] = 1 / c[0], c[3] = 1 / c[1], d[0] = e.source.pixelWidth, d[1] = e.source.pixelHeight, d[2] = 1 / d[0], d[3] = 1 / d[1], f[0] = 0.5 * d[2], f[1] = 0.5 * d[3], f[2] = e.frame.width * c[2] - 0.5 * d[2], f[3] = e.frame.height * c[3] - 0.5 * d[3];
    const _ = this.renderer.renderTarget.rootRenderTarget.colorTexture;
    m[0] = i * n, m[1] = s * n, m[2] = _.source.width * n, m[3] = _.source.height * n, t instanceof M && (t.source.resource = null);
    const p = this.renderer.renderTarget.getRenderTarget(t);
    this.renderer.renderTarget.bind(t, !!l), t instanceof M ? (x[0] = t.frame.width, x[1] = t.frame.height) : (x[0] = p.width, x[1] = p.height), x[2] = p.isRoot ? -1 : 1, this._filterGlobalUniforms.update();
  }
  /**
   * Finds the correct resolution by looking back through the filter stack.
   * @param rootResolution - The fallback root resolution to use
   * @returns The resolution from the previous filter or root resolution
   */
  _findFilterResolution(e) {
    let t = this._filterStackIndex - 1;
    for (; t > 0 && this._filterStack[t].skip; )
      --t;
    return t > 0 && this._filterStack[t].inputTexture ? this._filterStack[t].inputTexture.source._resolution : e;
  }
  /**
   * Finds the offset from the previous non-skipped filter in the stack.
   * @returns The offset coordinates from the previous filter
   */
  _findPreviousFilterOffset() {
    let e = 0, t = 0, r = this._filterStackIndex;
    for (; r > 0; ) {
      r--;
      const i = this._filterStack[r];
      if (!i.skip) {
        e = i.bounds.minX, t = i.bounds.minY;
        break;
      }
    }
    return { x: e, y: t };
  }
  /**
   * Calculates the filter area bounds based on the instruction type.
   * @param instruction - The filter instruction
   * @param bounds - The bounds object to populate
   */
  _calculateFilterArea(e, t) {
    if (e.renderables ? ir(e.renderables, t) : e.filterEffect.filterArea ? (t.clear(), t.addRect(e.filterEffect.filterArea), t.applyMatrix(e.container.worldTransform)) : e.container.getFastGlobalBounds(!0, t), e.container) {
      const i = (e.container.renderGroup || e.container.parentRenderGroup).cacheToLocalTransform;
      i && t.applyMatrix(i);
    }
  }
  _applyFiltersToTexture(e, t) {
    const r = e.inputTexture, i = e.bounds, s = e.filters;
    if (this._globalFilterBindGroup.setResource(r.source.style, 2), this._globalFilterBindGroup.setResource(e.backTexture.source, 3), s.length === 1)
      s[0].apply(this, r, e.outputRenderSurface, t);
    else {
      let n = e.inputTexture;
      const a = W.getOptimalTexture(
        i.width,
        i.height,
        n.source._resolution,
        !1
      );
      let l = a, u = 0;
      for (u = 0; u < s.length - 1; ++u) {
        s[u].apply(this, n, l, !0);
        const c = n;
        n = l, l = c;
      }
      s[u].apply(this, n, e.outputRenderSurface, t), W.returnTexture(a);
    }
  }
  _calculateFilterBounds(e, t, r, i, s) {
    var x;
    const n = this.renderer, a = e.bounds, l = e.filters;
    let u = 1 / 0, h = 0, c = !0, d = !1, f = !1, m = !0;
    for (let _ = 0; _ < l.length; _++) {
      const p = l[_];
      if (u = Math.min(u, p.resolution === "inherit" ? i : p.resolution), h += p.padding, p.antialias === "off" ? c = !1 : p.antialias === "inherit" && c && (c = r), p.clipToViewport || (m = !1), !!!(p.compatibleRenderers & n.type)) {
        f = !1;
        break;
      }
      if (p.blendRequired && !(((x = n.backBuffer) == null ? void 0 : x.useBackBuffer) ?? !0)) {
        $("Blend filter requires backBuffer on WebGL renderer to be enabled. Set `useBackBuffer: true` in the renderer options."), f = !1;
        break;
      }
      f = p.enabled || f, d || (d = p.blendRequired);
    }
    if (!f) {
      e.skip = !0;
      return;
    }
    if (m && a.fitBounds(0, t.width / i, 0, t.height / i), a.scale(u).ceil().scale(1 / u).pad((h | 0) * s), !a.isPositive) {
      e.skip = !0;
      return;
    }
    e.antialias = c, e.resolution = u, e.blendRequired = d;
  }
  _popFilterData() {
    return this._filterStackIndex--, this._filterStack[this._filterStackIndex];
  }
  _getPreviousFilterData() {
    let e, t = this._filterStackIndex - 1;
    for (; t > 0 && (t--, e = this._filterStack[t], !!e.skip); )
      ;
    return e;
  }
  _pushFilterData() {
    let e = this._filterStack[this._filterStackIndex];
    return e || (e = this._filterStack[this._filterStackIndex] = new nr()), this._filterStackIndex++, e;
  }
}
ot.extension = {
  type: [
    w.WebGLSystem,
    w.WebGPUSystem
  ],
  name: "filter"
};
const lt = class ut extends be {
  constructor(...e) {
    let t = e[0] ?? {};
    t instanceof Float32Array && (B(G, "use new MeshGeometry({ positions, uvs, indices }) instead"), t = {
      positions: t,
      uvs: e[1],
      indices: e[2]
    }), t = { ...ut.defaultOptions, ...t };
    const r = t.positions || new Float32Array([0, 0, 1, 0, 1, 1, 0, 1]);
    let i = t.uvs;
    i || (t.positions ? i = new Float32Array(r.length) : i = new Float32Array([0, 0, 1, 0, 1, 1, 0, 1]));
    const s = t.indices || new Uint32Array([0, 1, 2, 0, 2, 3]), n = t.shrinkBuffersToFit, a = new Q({
      data: r,
      label: "attribute-mesh-positions",
      shrinkToFit: n,
      usage: D.VERTEX | D.COPY_DST
    }), l = new Q({
      data: i,
      label: "attribute-mesh-uvs",
      shrinkToFit: n,
      usage: D.VERTEX | D.COPY_DST
    }), u = new Q({
      data: s,
      label: "index-mesh-buffer",
      shrinkToFit: n,
      usage: D.INDEX | D.COPY_DST
    });
    super({
      attributes: {
        aPosition: {
          buffer: a,
          format: "float32x2",
          stride: 2 * 4,
          offset: 0
        },
        aUV: {
          buffer: l,
          format: "float32x2",
          stride: 2 * 4,
          offset: 0
        }
      },
      indexBuffer: u,
      topology: t.topology
    }), this.batchMode = "auto";
  }
  /** The positions of the mesh. */
  get positions() {
    return this.attributes.aPosition.buffer.data;
  }
  /**
   * Set the positions of the mesh.
   * When setting the positions, its important that the uvs array is at least as long as the positions array.
   * otherwise the geometry will not be valid.
   * @param {Float32Array} value - The positions of the mesh.
   */
  set positions(e) {
    this.attributes.aPosition.buffer.data = e;
  }
  /** The UVs of the mesh. */
  get uvs() {
    return this.attributes.aUV.buffer.data;
  }
  /**
   * Set the UVs of the mesh.
   * Its important that the uvs array you set is at least as long as the positions array.
   * otherwise the geometry will not be valid.
   * @param {Float32Array} value - The UVs of the mesh.
   */
  set uvs(e) {
    this.attributes.aUV.buffer.data = e;
  }
  /** The indices of the mesh. */
  get indices() {
    return this.indexBuffer.data;
  }
  set indices(e) {
    this.indexBuffer.data = e;
  }
};
lt.defaultOptions = {
  topology: "triangle-list",
  shrinkBuffersToFit: !1
};
let Ce = lt, H = null, O = null;
function ar(o, e) {
  H || (H = V.get().createCanvas(256, 128), O = H.getContext("2d", { willReadFrequently: !0 }), O.globalCompositeOperation = "copy", O.globalAlpha = 1), (H.width < o || H.height < e) && (H.width = Me(o), H.height = Me(e));
}
function Ae(o, e, t) {
  for (let r = 0, i = 4 * t * e; r < e; ++r, i += 4)
    if (o[i + 3] !== 0)
      return !1;
  return !0;
}
function We(o, e, t, r, i) {
  const s = 4 * e;
  for (let n = r, a = r * s + 4 * t; n <= i; ++n, a += s)
    if (o[a + 3] !== 0)
      return !1;
  return !0;
}
function or(...o) {
  let e = o[0];
  e.canvas || (e = { canvas: o[0], resolution: o[1] });
  const { canvas: t } = e, r = Math.min(e.resolution ?? 1, 1), i = e.width ?? t.width, s = e.height ?? t.height;
  let n = e.output;
  if (ar(i, s), !O)
    throw new TypeError("Failed to get canvas 2D context");
  O.drawImage(
    t,
    0,
    0,
    i,
    s,
    0,
    0,
    i * r,
    s * r
  );
  const l = O.getImageData(0, 0, i, s).data;
  let u = 0, h = 0, c = i - 1, d = s - 1;
  for (; h < s && Ae(l, i, h); )
    ++h;
  if (h === s)
    return ie.EMPTY;
  for (; Ae(l, i, d); )
    --d;
  for (; We(l, i, u, h, d); )
    ++u;
  for (; We(l, i, c, h, d); )
    --c;
  return ++c, ++d, O.globalCompositeOperation = "source-over", O.strokeRect(u, h, c - u, d - h), O.globalCompositeOperation = "copy", n ?? (n = new ie()), n.set(u / r, h / r, (c - u) / r, (d - h) / r), n;
}
const De = new ie();
class lr {
  /**
   * Creates a canvas with the specified text rendered to it.
   *
   * Generates a canvas of appropriate size, renders the text with the provided style,
   * and returns both the canvas/context and a Rectangle representing the text bounds.
   *
   * When trim is enabled in the style, the frame will represent the bounds of the
   * non-transparent pixels, which can be smaller than the full canvas.
   * @param options - The options for generating the text canvas
   * @param options.text - The text to render
   * @param options.style - The style to apply to the text
   * @param options.resolution - The resolution of the canvas (defaults to 1)
   * @param options.padding
   * @returns An object containing the canvas/context and the frame (bounds) of the text
   */
  getCanvasAndContext(e) {
    const { text: t, style: r, resolution: i = 1 } = e, s = r._getFinalPadding(), n = L.measureText(t || " ", r), a = Math.ceil(Math.ceil(Math.max(1, n.width) + s * 2) * i), l = Math.ceil(Math.ceil(Math.max(1, n.height) + s * 2) * i), u = K.getOptimalCanvasAndContext(a, l);
    this._renderTextToCanvas(t, r, s, i, u);
    const h = r.trim ? or({ canvas: u.canvas, width: a, height: l, resolution: 1, output: De }) : De.set(0, 0, a, l);
    return {
      canvasAndContext: u,
      frame: h
    };
  }
  /**
   * Returns a canvas and context to the pool.
   *
   * This should be called when you're done with the canvas to allow reuse
   * and prevent memory leaks.
   * @param canvasAndContext - The canvas and context to return to the pool
   */
  returnCanvasAndContext(e) {
    K.returnCanvasAndContext(e);
  }
  /**
   * Renders text to its canvas, and updates its texture.
   * @param text - The text to render
   * @param style - The style of the text
   * @param padding - The padding of the text
   * @param resolution - The resolution of the text
   * @param canvasAndContext - The canvas and context to render the text to
   */
  _renderTextToCanvas(e, t, r, i, s) {
    var y, T, S, k;
    const { canvas: n, context: a } = s, l = ae(t), u = L.measureText(e || " ", t), h = u.lines, c = u.lineHeight, d = u.lineWidths, f = u.maxLineWidth, m = u.fontProperties, x = n.height;
    if (a.resetTransform(), a.scale(i, i), a.textBaseline = t.textBaseline, (y = t._stroke) != null && y.width) {
      const v = t._stroke;
      a.lineWidth = v.width, a.miterLimit = v.miterLimit, a.lineJoin = v.join, a.lineCap = v.cap;
    }
    a.font = l;
    let _, p;
    const b = t.dropShadow ? 2 : 1;
    for (let v = 0; v < b; ++v) {
      const F = t.dropShadow && v === 0, R = F ? Math.ceil(Math.max(1, x) + r * 2) : 0, ue = R * i;
      if (F) {
        a.fillStyle = "black", a.strokeStyle = "black";
        const C = t.dropShadow, Bt = C.color, kt = C.alpha;
        a.shadowColor = E.shared.setValue(Bt).setAlpha(kt).toRgbaString();
        const Rt = C.blur * i, Fe = C.distance * i;
        a.shadowBlur = Rt, a.shadowOffsetX = Math.cos(C.angle) * Fe, a.shadowOffsetY = Math.sin(C.angle) * Fe + ue;
      } else {
        if (a.fillStyle = t._fill ? oe(t._fill, a, u, r * 2) : null, (T = t._stroke) != null && T.width) {
          const C = t._stroke.width * 0.5 + r * 2;
          a.strokeStyle = oe(t._stroke, a, u, C);
        }
        a.shadowColor = "black";
      }
      let I = (c - m.fontSize) / 2;
      c - m.fontSize < 0 && (I = 0);
      const q = ((S = t._stroke) == null ? void 0 : S.width) ?? 0;
      for (let C = 0; C < h.length; C++)
        _ = q / 2, p = q / 2 + C * c + m.ascent + I, t.align === "right" ? _ += f - d[C] : t.align === "center" && (_ += (f - d[C]) / 2), (k = t._stroke) != null && k.width && this._drawLetterSpacing(
          h[C],
          t,
          s,
          _ + r,
          p + r - R,
          !0
        ), t._fill !== void 0 && this._drawLetterSpacing(
          h[C],
          t,
          s,
          _ + r,
          p + r - R
        );
    }
  }
  /**
   * Render the text with letter-spacing.
   *
   * This method handles rendering text with the correct letter spacing, using either:
   * 1. Native letter spacing if supported by the browser
   * 2. Manual letter spacing calculation if not natively supported
   *
   * For manual letter spacing, it calculates the position of each character
   * based on its width and the desired spacing.
   * @param text - The text to draw
   * @param style - The text style to apply
   * @param canvasAndContext - The canvas and context to draw to
   * @param x - Horizontal position to draw the text
   * @param y - Vertical position to draw the text
   * @param isStroke - Whether to render the stroke (true) or fill (false)
   * @private
   */
  _drawLetterSpacing(e, t, r, i, s, n = !1) {
    const { context: a } = r, l = t.letterSpacing;
    let u = !1;
    if (L.experimentalLetterSpacingSupported && (L.experimentalLetterSpacing ? (a.letterSpacing = `${l}px`, a.textLetterSpacing = `${l}px`, u = !0) : (a.letterSpacing = "0px", a.textLetterSpacing = "0px")), l === 0 || u) {
      n ? a.strokeText(e, i, s) : a.fillText(e, i, s);
      return;
    }
    let h = i;
    const c = L.graphemeSegmenter(e);
    let d = a.measureText(e).width, f = 0;
    for (let m = 0; m < c.length; ++m) {
      const x = c[m];
      n ? a.strokeText(x, h, s) : a.fillText(x, h, s);
      let _ = "";
      for (let p = m + 1; p < c.length; ++p)
        _ += c[p];
      f = a.measureText(_).width, h += d - f + l, d = f;
    }
  }
}
const he = new lr(), Le = "http://www.w3.org/2000/svg", Ie = "http://www.w3.org/1999/xhtml";
class ct {
  constructor() {
    this.svgRoot = document.createElementNS(Le, "svg"), this.foreignObject = document.createElementNS(Le, "foreignObject"), this.domElement = document.createElementNS(Ie, "div"), this.styleElement = document.createElementNS(Ie, "style");
    const { foreignObject: e, svgRoot: t, styleElement: r, domElement: i } = this;
    e.setAttribute("width", "10000"), e.setAttribute("height", "10000"), e.style.overflow = "hidden", t.appendChild(e), e.appendChild(r), e.appendChild(i), this.image = V.get().createImage();
  }
  destroy() {
    this.svgRoot.remove(), this.foreignObject.remove(), this.styleElement.remove(), this.domElement.remove(), this.image.src = "", this.image.remove(), this.svgRoot = null, this.foreignObject = null, this.styleElement = null, this.domElement = null, this.image = null, this.canvasAndContext = null;
  }
}
let Oe;
function ur(o, e, t, r) {
  r || (r = Oe || (Oe = new ct()));
  const { domElement: i, styleElement: s, svgRoot: n } = r;
  i.innerHTML = `<style>${e.cssStyle};</style><div style='padding:0'>${o}</div>`, i.setAttribute("style", "transform-origin: top left; display: inline-block"), t && (s.textContent = t), document.body.appendChild(n);
  const a = i.getBoundingClientRect();
  n.remove();
  const l = e.padding * 2;
  return {
    width: a.width - l,
    height: a.height - l
  };
}
class cr {
  constructor() {
    this.batches = [], this.batched = !1;
  }
  destroy() {
    this.batches.forEach((e) => {
      se.return(e);
    }), this.batches.length = 0;
  }
}
class ht {
  constructor(e, t) {
    this.state = ne.for2d(), this.renderer = e, this._adaptor = t, this.renderer.runners.contextChange.add(this);
  }
  contextChange() {
    this._adaptor.contextChange(this.renderer);
  }
  validateRenderable(e) {
    const t = e.context, r = !!e._gpuData, i = this.renderer.graphicsContext.updateGpuContext(t);
    return !!(i.isBatchable || r !== i.isBatchable);
  }
  addRenderable(e, t) {
    const r = this.renderer.graphicsContext.updateGpuContext(e.context);
    e.didViewUpdate && this._rebuild(e), r.isBatchable ? this._addToBatcher(e, t) : (this.renderer.renderPipes.batch.break(t), t.add(e));
  }
  updateRenderable(e) {
    const r = this._getGpuDataForRenderable(e).batches;
    for (let i = 0; i < r.length; i++) {
      const s = r[i];
      s._batcher.updateElement(s);
    }
  }
  execute(e) {
    if (!e.isRenderable)
      return;
    const t = this.renderer, r = e.context;
    if (!t.graphicsContext.getGpuContext(r).batches.length)
      return;
    const s = r.customShader || this._adaptor.shader;
    this.state.blendMode = e.groupBlendMode;
    const n = s.resources.localUniforms.uniforms;
    n.uTransformMatrix = e.groupTransform, n.uRound = t._roundPixels | e._roundPixels, le(
      e.groupColorAlpha,
      n.uColor,
      0
    ), this._adaptor.execute(this, e);
  }
  _rebuild(e) {
    const t = this._getGpuDataForRenderable(e), r = this.renderer.graphicsContext.updateGpuContext(e.context);
    t.destroy(), r.isBatchable && this._updateBatchesForRenderable(e, t);
  }
  _addToBatcher(e, t) {
    const r = this.renderer.renderPipes.batch, i = this._getGpuDataForRenderable(e).batches;
    for (let s = 0; s < i.length; s++) {
      const n = i[s];
      r.addToBatch(n, t);
    }
  }
  _getGpuDataForRenderable(e) {
    return e._gpuData[this.renderer.uid] || this._initGpuDataForRenderable(e);
  }
  _initGpuDataForRenderable(e) {
    const t = new cr();
    return e._gpuData[this.renderer.uid] = t, t;
  }
  _updateBatchesForRenderable(e, t) {
    const r = e.context, i = this.renderer.graphicsContext.getGpuContext(r), s = this.renderer._roundPixels | e._roundPixels;
    t.batches = i.batches.map((n) => {
      const a = se.get(zt);
      return n.copyTo(a), a.renderable = e, a.roundPixels = s, a;
    });
  }
  destroy() {
    this.renderer = null, this._adaptor.destroy(), this._adaptor = null, this.state = null;
  }
}
ht.extension = {
  type: [
    w.WebGLPipes,
    w.WebGPUPipes,
    w.CanvasPipes
  ],
  name: "graphics"
};
const dt = class ft extends Ce {
  constructor(...e) {
    super({});
    let t = e[0] ?? {};
    typeof t == "number" && (B(G, "PlaneGeometry constructor changed please use { width, height, verticesX, verticesY } instead"), t = {
      width: t,
      height: e[1],
      verticesX: e[2],
      verticesY: e[3]
    }), this.build(t);
  }
  /**
   * Refreshes plane coordinates
   * @param options - Options to be applied to plane geometry
   */
  build(e) {
    e = { ...ft.defaultOptions, ...e }, this.verticesX = this.verticesX ?? e.verticesX, this.verticesY = this.verticesY ?? e.verticesY, this.width = this.width ?? e.width, this.height = this.height ?? e.height;
    const t = this.verticesX * this.verticesY, r = [], i = [], s = [], n = this.verticesX - 1, a = this.verticesY - 1, l = this.width / n, u = this.height / a;
    for (let c = 0; c < t; c++) {
      const d = c % this.verticesX, f = c / this.verticesX | 0;
      r.push(d * l, f * u), i.push(d / n, f / a);
    }
    const h = n * a;
    for (let c = 0; c < h; c++) {
      const d = c % n, f = c / n | 0, m = f * this.verticesX + d, x = f * this.verticesX + d + 1, _ = (f + 1) * this.verticesX + d, p = (f + 1) * this.verticesX + d + 1;
      s.push(
        m,
        x,
        _,
        x,
        p,
        _
      );
    }
    this.buffers[0].data = new Float32Array(r), this.buffers[1].data = new Float32Array(i), this.indexBuffer.data = new Uint32Array(s), this.buffers[0].update(), this.buffers[1].update(), this.indexBuffer.update();
  }
};
dt.defaultOptions = {
  width: 100,
  height: 100,
  verticesX: 10,
  verticesY: 10
};
let hr = dt;
class Pe {
  constructor() {
    this.batcherName = "default", this.packAsQuad = !1, this.indexOffset = 0, this.attributeOffset = 0, this.roundPixels = 0, this._batcher = null, this._batch = null, this._textureMatrixUpdateId = -1, this._uvUpdateId = -1;
  }
  get blendMode() {
    return this.renderable.groupBlendMode;
  }
  get topology() {
    return this._topology || this.geometry.topology;
  }
  set topology(e) {
    this._topology = e;
  }
  reset() {
    this.renderable = null, this.texture = null, this._batcher = null, this._batch = null, this.geometry = null, this._uvUpdateId = -1, this._textureMatrixUpdateId = -1;
  }
  /**
   * Sets the texture for the batchable mesh.
   * As it does so, it resets the texture matrix update ID.
   * this is to ensure that the texture matrix is recalculated when the uvs are referenced
   * @param value - The texture to set.
   */
  setTexture(e) {
    this.texture !== e && (this.texture = e, this._textureMatrixUpdateId = -1);
  }
  get uvs() {
    const t = this.geometry.getBuffer("aUV"), r = t.data;
    let i = r;
    const s = this.texture.textureMatrix;
    return s.isSimple || (i = this._transformedUvs, (this._textureMatrixUpdateId !== s._updateID || this._uvUpdateId !== t._updateID) && ((!i || i.length < r.length) && (i = this._transformedUvs = new Float32Array(r.length)), this._textureMatrixUpdateId = s._updateID, this._uvUpdateId = t._updateID, s.multiplyUvs(r, i))), i;
  }
  get positions() {
    return this.geometry.positions;
  }
  get indices() {
    return this.geometry.indices;
  }
  get color() {
    return this.renderable.groupColorAlpha;
  }
  get groupTransform() {
    return this.renderable.groupTransform;
  }
  get attributeSize() {
    return this.geometry.positions.length / 2;
  }
  get indexSize() {
    return this.geometry.indices.length;
  }
}
class Ee {
  destroy() {
  }
}
class pt {
  constructor(e, t) {
    this.localUniforms = new j({
      uTransformMatrix: { value: new U(), type: "mat3x3<f32>" },
      uColor: { value: new Float32Array([1, 1, 1, 1]), type: "vec4<f32>" },
      uRound: { value: 0, type: "f32" }
    }), this.localUniformsBindGroup = new je({
      0: this.localUniforms
    }), this.renderer = e, this._adaptor = t, this._adaptor.init();
  }
  validateRenderable(e) {
    const t = this._getMeshData(e), r = t.batched, i = e.batched;
    if (t.batched = i, r !== i)
      return !0;
    if (i) {
      const s = e._geometry;
      if (s.indices.length !== t.indexSize || s.positions.length !== t.vertexSize)
        return t.indexSize = s.indices.length, t.vertexSize = s.positions.length, !0;
      const n = this._getBatchableMesh(e);
      return n.texture.uid !== e._texture.uid && (n._textureMatrixUpdateId = -1), !n._batcher.checkAndUpdateTexture(
        n,
        e._texture
      );
    }
    return !1;
  }
  addRenderable(e, t) {
    var s, n;
    const r = this.renderer.renderPipes.batch, i = this._getMeshData(e);
    if (e.didViewUpdate && (i.indexSize = (s = e._geometry.indices) == null ? void 0 : s.length, i.vertexSize = (n = e._geometry.positions) == null ? void 0 : n.length), i.batched) {
      const a = this._getBatchableMesh(e);
      a.setTexture(e._texture), a.geometry = e._geometry, r.addToBatch(a, t);
    } else
      r.break(t), t.add(e);
  }
  updateRenderable(e) {
    if (e.batched) {
      const t = this._getBatchableMesh(e);
      t.setTexture(e._texture), t.geometry = e._geometry, t._batcher.updateElement(t);
    }
  }
  execute(e) {
    if (!e.isRenderable)
      return;
    e.state.blendMode = Te(e.groupBlendMode, e.texture._source);
    const t = this.localUniforms;
    t.uniforms.uTransformMatrix = e.groupTransform, t.uniforms.uRound = this.renderer._roundPixels | e._roundPixels, t.update(), le(
      e.groupColorAlpha,
      t.uniforms.uColor,
      0
    ), this._adaptor.execute(this, e);
  }
  _getMeshData(e) {
    var t, r;
    return (t = e._gpuData)[r = this.renderer.uid] || (t[r] = new Ee()), e._gpuData[this.renderer.uid].meshData || this._initMeshData(e);
  }
  _initMeshData(e) {
    return e._gpuData[this.renderer.uid].meshData = {
      batched: e.batched,
      indexSize: 0,
      vertexSize: 0
    }, e._gpuData[this.renderer.uid].meshData;
  }
  _getBatchableMesh(e) {
    var t, r;
    return (t = e._gpuData)[r = this.renderer.uid] || (t[r] = new Ee()), e._gpuData[this.renderer.uid].batchableMesh || this._initBatchableMesh(e);
  }
  _initBatchableMesh(e) {
    const t = new Pe();
    return t.renderable = e, t.setTexture(e._texture), t.transform = e.groupTransform, t.roundPixels = this.renderer._roundPixels | e._roundPixels, e._gpuData[this.renderer.uid].batchableMesh = t, t;
  }
  destroy() {
    this.localUniforms = null, this.localUniformsBindGroup = null, this._adaptor.destroy(), this._adaptor = null, this.renderer = null;
  }
}
pt.extension = {
  type: [
    w.WebGLPipes,
    w.WebGPUPipes,
    w.CanvasPipes
  ],
  name: "mesh"
};
class dr {
  execute(e, t) {
    const r = e.state, i = e.renderer, s = t.shader || e.defaultShader;
    s.resources.uTexture = t.texture._source, s.resources.uniforms = e.localUniforms;
    const n = i.gl, a = e.getBuffers(t);
    i.shader.bind(s), i.state.set(r), i.geometry.bind(a.geometry, s.glProgram);
    const u = a.geometry.indexBuffer.data.BYTES_PER_ELEMENT === 2 ? n.UNSIGNED_SHORT : n.UNSIGNED_INT;
    n.drawElements(n.TRIANGLES, t.particleChildren.length * 6, u, 0);
  }
}
class fr {
  execute(e, t) {
    const r = e.renderer, i = t.shader || e.defaultShader;
    i.groups[0] = r.renderPipes.uniformBatch.getUniformBindGroup(e.localUniforms, !0), i.groups[1] = r.texture.getTextureBindGroup(t.texture);
    const s = e.state, n = e.getBuffers(t);
    r.encoder.draw({
      geometry: n.geometry,
      shader: t.shader || e.defaultShader,
      state: s,
      size: t.particleChildren.length * 6
    });
  }
}
function He(o, e = null) {
  const t = o * 6;
  if (t > 65535 ? e || (e = new Uint32Array(t)) : e || (e = new Uint16Array(t)), e.length !== t)
    throw new Error(`Out buffer length is incorrect, got ${e.length} and expected ${t}`);
  for (let r = 0, i = 0; r < t; r += 6, i += 4)
    e[r + 0] = i + 0, e[r + 1] = i + 1, e[r + 2] = i + 2, e[r + 3] = i + 0, e[r + 4] = i + 2, e[r + 5] = i + 3;
  return e;
}
function pr(o) {
  return {
    dynamicUpdate: Ve(o, !0),
    staticUpdate: Ve(o, !1)
  };
}
function Ve(o, e) {
  const t = [];
  t.push(`

        var index = 0;

        for (let i = 0; i < ps.length; ++i)
        {
            const p = ps[i];

            `);
  let r = 0;
  for (const s in o) {
    const n = o[s];
    if (e !== n.dynamic)
      continue;
    t.push(`offset = index + ${r}`), t.push(n.code);
    const a = xe(n.format);
    r += a.stride / 4;
  }
  t.push(`
            index += stride * 4;
        }
    `), t.unshift(`
        var stride = ${r};
    `);
  const i = t.join(`
`);
  return new Function("ps", "f32v", "u32v", i);
}
class gr {
  constructor(e) {
    this._size = 0, this._generateParticleUpdateCache = {};
    const t = this._size = e.size ?? 1e3, r = e.properties;
    let i = 0, s = 0;
    for (const h in r) {
      const c = r[h], d = xe(c.format);
      c.dynamic ? s += d.stride : i += d.stride;
    }
    this._dynamicStride = s / 4, this._staticStride = i / 4, this.staticAttributeBuffer = new Z(t * 4 * i), this.dynamicAttributeBuffer = new Z(t * 4 * s), this.indexBuffer = He(t);
    const n = new be();
    let a = 0, l = 0;
    this._staticBuffer = new Q({
      data: new Float32Array(1),
      label: "static-particle-buffer",
      shrinkToFit: !1,
      usage: D.VERTEX | D.COPY_DST
    }), this._dynamicBuffer = new Q({
      data: new Float32Array(1),
      label: "dynamic-particle-buffer",
      shrinkToFit: !1,
      usage: D.VERTEX | D.COPY_DST
    });
    for (const h in r) {
      const c = r[h], d = xe(c.format);
      c.dynamic ? (n.addAttribute(c.attributeName, {
        buffer: this._dynamicBuffer,
        stride: this._dynamicStride * 4,
        offset: a * 4,
        format: c.format
      }), a += d.size) : (n.addAttribute(c.attributeName, {
        buffer: this._staticBuffer,
        stride: this._staticStride * 4,
        offset: l * 4,
        format: c.format
      }), l += d.size);
    }
    n.addIndex(this.indexBuffer);
    const u = this.getParticleUpdate(r);
    this._dynamicUpload = u.dynamicUpdate, this._staticUpload = u.staticUpdate, this.geometry = n;
  }
  getParticleUpdate(e) {
    const t = mr(e);
    return this._generateParticleUpdateCache[t] ? this._generateParticleUpdateCache[t] : (this._generateParticleUpdateCache[t] = this.generateParticleUpdate(e), this._generateParticleUpdateCache[t]);
  }
  generateParticleUpdate(e) {
    return pr(e);
  }
  update(e, t) {
    e.length > this._size && (t = !0, this._size = Math.max(e.length, this._size * 1.5 | 0), this.staticAttributeBuffer = new Z(this._size * this._staticStride * 4 * 4), this.dynamicAttributeBuffer = new Z(this._size * this._dynamicStride * 4 * 4), this.indexBuffer = He(this._size), this.geometry.indexBuffer.setDataWithSize(
      this.indexBuffer,
      this.indexBuffer.byteLength,
      !0
    ));
    const r = this.dynamicAttributeBuffer;
    if (this._dynamicUpload(e, r.float32View, r.uint32View), this._dynamicBuffer.setDataWithSize(
      this.dynamicAttributeBuffer.float32View,
      e.length * this._dynamicStride * 4,
      !0
    ), t) {
      const i = this.staticAttributeBuffer;
      this._staticUpload(e, i.float32View, i.uint32View), this._staticBuffer.setDataWithSize(
        i.float32View,
        e.length * this._staticStride * 4,
        !0
      );
    }
  }
  destroy() {
    this._staticBuffer.destroy(), this._dynamicBuffer.destroy(), this.geometry.destroy();
  }
}
function mr(o) {
  const e = [];
  for (const t in o) {
    const r = o[t];
    e.push(t, r.code, r.dynamic ? "d" : "s");
  }
  return e.join("_");
}
var xr = `varying vec2 vUV;
varying vec4 vColor;

uniform sampler2D uTexture;

void main(void){
    vec4 color = texture2D(uTexture, vUV) * vColor;
    gl_FragColor = color;
}`, _r = `attribute vec2 aVertex;
attribute vec2 aUV;
attribute vec4 aColor;

attribute vec2 aPosition;
attribute float aRotation;

uniform mat3 uTranslationMatrix;
uniform float uRound;
uniform vec2 uResolution;
uniform vec4 uColor;

varying vec2 vUV;
varying vec4 vColor;

vec2 roundPixels(vec2 position, vec2 targetSize)
{       
    return (floor(((position * 0.5 + 0.5) * targetSize) + 0.5) / targetSize) * 2.0 - 1.0;
}

void main(void){
    float cosRotation = cos(aRotation);
    float sinRotation = sin(aRotation);
    float x = aVertex.x * cosRotation - aVertex.y * sinRotation;
    float y = aVertex.x * sinRotation + aVertex.y * cosRotation;

    vec2 v = vec2(x, y);
    v = v + aPosition;

    gl_Position = vec4((uTranslationMatrix * vec3(v, 1.0)).xy, 0.0, 1.0);

    if(uRound == 1.0)
    {
        gl_Position.xy = roundPixels(gl_Position.xy, uResolution);
    }

    vUV = aUV;
    vColor = vec4(aColor.rgb * aColor.a, aColor.a) * uColor;
}
`, Ye = `
struct ParticleUniforms {
  uTranslationMatrix:mat3x3<f32>,
  uColor:vec4<f32>,
  uRound:f32,
  uResolution:vec2<f32>,
};

fn roundPixels(position: vec2<f32>, targetSize: vec2<f32>) -> vec2<f32>
{
  return (floor(((position * 0.5 + 0.5) * targetSize) + 0.5) / targetSize) * 2.0 - 1.0;
}

@group(0) @binding(0) var<uniform> uniforms: ParticleUniforms;

@group(1) @binding(0) var uTexture: texture_2d<f32>;
@group(1) @binding(1) var uSampler : sampler;

struct VSOutput {
    @builtin(position) position: vec4<f32>,
    @location(0) uv : vec2<f32>,
    @location(1) color : vec4<f32>,
  };
@vertex
fn mainVertex(
  @location(0) aVertex: vec2<f32>,
  @location(1) aPosition: vec2<f32>,
  @location(2) aUV: vec2<f32>,
  @location(3) aColor: vec4<f32>,
  @location(4) aRotation: f32,
) -> VSOutput {
  
   let v = vec2(
       aVertex.x * cos(aRotation) - aVertex.y * sin(aRotation),
       aVertex.x * sin(aRotation) + aVertex.y * cos(aRotation)
   ) + aPosition;

   var position = vec4((uniforms.uTranslationMatrix * vec3(v, 1.0)).xy, 0.0, 1.0);

   if(uniforms.uRound == 1.0) {
       position = vec4(roundPixels(position.xy, uniforms.uResolution), position.zw);
   }

    let vColor = vec4(aColor.rgb * aColor.a, aColor.a) * uniforms.uColor;

  return VSOutput(
   position,
   aUV,
   vColor,
  );
}

@fragment
fn mainFragment(
  @location(0) uv: vec2<f32>,
  @location(1) color: vec4<f32>,
  @builtin(position) position: vec4<f32>,
) -> @location(0) vec4<f32> {

    var sample = textureSample(uTexture, uSampler, uv) * color;
   
    return sample;
}`;
class yr extends ve {
  constructor() {
    const e = At.from({
      vertex: _r,
      fragment: xr
    }), t = Wt.from({
      fragment: {
        source: Ye,
        entryPoint: "mainFragment"
      },
      vertex: {
        source: Ye,
        entryPoint: "mainVertex"
      }
    });
    super({
      glProgram: e,
      gpuProgram: t,
      resources: {
        // this will be replaced with the texture from the particle container
        uTexture: M.WHITE.source,
        // this will be replaced with the texture style from the particle container
        uSampler: new J({}),
        // this will be replaced with the local uniforms from the particle container
        uniforms: {
          uTranslationMatrix: { value: new U(), type: "mat3x3<f32>" },
          uColor: { value: new E(16777215), type: "vec4<f32>" },
          uRound: { value: 1, type: "f32" },
          uResolution: { value: [0, 0], type: "vec2<f32>" }
        }
      }
    });
  }
}
class gt {
  /**
   * @param renderer - The renderer this sprite batch works for.
   * @param adaptor
   */
  constructor(e, t) {
    this.state = ne.for2d(), this.localUniforms = new j({
      uTranslationMatrix: { value: new U(), type: "mat3x3<f32>" },
      uColor: { value: new Float32Array(4), type: "vec4<f32>" },
      uRound: { value: 1, type: "f32" },
      uResolution: { value: [0, 0], type: "vec2<f32>" }
    }), this.renderer = e, this.adaptor = t, this.defaultShader = new yr(), this.state = ne.for2d();
  }
  validateRenderable(e) {
    return !1;
  }
  addRenderable(e, t) {
    this.renderer.renderPipes.batch.break(t), t.add(e);
  }
  getBuffers(e) {
    return e._gpuData[this.renderer.uid] || this._initBuffer(e);
  }
  _initBuffer(e) {
    return e._gpuData[this.renderer.uid] = new gr({
      size: e.particleChildren.length,
      properties: e._properties
    }), e._gpuData[this.renderer.uid];
  }
  updateRenderable(e) {
  }
  execute(e) {
    const t = e.particleChildren;
    if (t.length === 0)
      return;
    const r = this.renderer, i = this.getBuffers(e);
    e.texture || (e.texture = t[0].texture);
    const s = this.state;
    i.update(t, e._childrenDirty), e._childrenDirty = !1, s.blendMode = Te(e.blendMode, e.texture._source);
    const n = this.localUniforms.uniforms, a = n.uTranslationMatrix;
    e.worldTransform.copyTo(a), a.prepend(r.globalUniforms.globalUniformData.projectionMatrix), n.uResolution = r.globalUniforms.globalUniformData.resolution, n.uRound = r._roundPixels | e._roundPixels, le(
      e.groupColorAlpha,
      n.uColor,
      0
    ), this.adaptor.execute(this, e);
  }
  /** Destroys the ParticleRenderer. */
  destroy() {
    this.renderer = null, this.defaultShader && (this.defaultShader.destroy(), this.defaultShader = null);
  }
}
class mt extends gt {
  constructor(e) {
    super(e, new dr());
  }
}
mt.extension = {
  type: [
    w.WebGLPipes
  ],
  name: "particle"
};
class xt extends gt {
  constructor(e) {
    super(e, new fr());
  }
}
xt.extension = {
  type: [
    w.WebGPUPipes
  ],
  name: "particle"
};
const _t = class yt extends hr {
  constructor(e = {}) {
    e = { ...yt.defaultOptions, ...e }, super({
      width: e.width,
      height: e.height,
      verticesX: 4,
      verticesY: 4
    }), this.update(e);
  }
  /**
   * Updates the NineSliceGeometry with the options.
   * @param options - The options of the NineSliceGeometry.
   */
  update(e) {
    var t, r;
    this.width = e.width ?? this.width, this.height = e.height ?? this.height, this._originalWidth = e.originalWidth ?? this._originalWidth, this._originalHeight = e.originalHeight ?? this._originalHeight, this._leftWidth = e.leftWidth ?? this._leftWidth, this._rightWidth = e.rightWidth ?? this._rightWidth, this._topHeight = e.topHeight ?? this._topHeight, this._bottomHeight = e.bottomHeight ?? this._bottomHeight, this._anchorX = (t = e.anchor) == null ? void 0 : t.x, this._anchorY = (r = e.anchor) == null ? void 0 : r.y, this.updateUvs(), this.updatePositions();
  }
  /** Updates the positions of the vertices. */
  updatePositions() {
    const e = this.positions, {
      width: t,
      height: r,
      _leftWidth: i,
      _rightWidth: s,
      _topHeight: n,
      _bottomHeight: a,
      _anchorX: l,
      _anchorY: u
    } = this, h = i + s, c = t > h ? 1 : t / h, d = n + a, f = r > d ? 1 : r / d, m = Math.min(c, f), x = l * t, _ = u * r;
    e[0] = e[8] = e[16] = e[24] = -x, e[2] = e[10] = e[18] = e[26] = i * m - x, e[4] = e[12] = e[20] = e[28] = t - s * m - x, e[6] = e[14] = e[22] = e[30] = t - x, e[1] = e[3] = e[5] = e[7] = -_, e[9] = e[11] = e[13] = e[15] = n * m - _, e[17] = e[19] = e[21] = e[23] = r - a * m - _, e[25] = e[27] = e[29] = e[31] = r - _, this.getBuffer("aPosition").update();
  }
  /** Updates the UVs of the vertices. */
  updateUvs() {
    const e = this.uvs;
    e[0] = e[8] = e[16] = e[24] = 0, e[1] = e[3] = e[5] = e[7] = 0, e[6] = e[14] = e[22] = e[30] = 1, e[25] = e[27] = e[29] = e[31] = 1;
    const t = 1 / this._originalWidth, r = 1 / this._originalHeight;
    e[2] = e[10] = e[18] = e[26] = t * this._leftWidth, e[9] = e[11] = e[13] = e[15] = r * this._topHeight, e[4] = e[12] = e[20] = e[28] = 1 - t * this._rightWidth, e[17] = e[19] = e[21] = e[23] = 1 - r * this._bottomHeight, this.getBuffer("aUV").update();
  }
};
_t.defaultOptions = {
  /** The width of the NineSlicePlane, setting this will actually modify the vertices and UV's of this plane. */
  width: 100,
  /** The height of the NineSlicePlane, setting this will actually modify the vertices and UV's of this plane. */
  height: 100,
  /** The width of the left column. */
  leftWidth: 10,
  /** The height of the top row. */
  topHeight: 10,
  /** The width of the right column. */
  rightWidth: 10,
  /** The height of the bottom row. */
  bottomHeight: 10,
  /** The original width of the texture */
  originalWidth: 100,
  /** The original height of the texture */
  originalHeight: 100
};
let br = _t;
class wr extends Pe {
  constructor() {
    super(), this.geometry = new br();
  }
  destroy() {
    this.geometry.destroy();
  }
}
class bt {
  constructor(e) {
    this._renderer = e;
  }
  addRenderable(e, t) {
    const r = this._getGpuSprite(e);
    e.didViewUpdate && this._updateBatchableSprite(e, r), this._renderer.renderPipes.batch.addToBatch(r, t);
  }
  updateRenderable(e) {
    const t = this._getGpuSprite(e);
    e.didViewUpdate && this._updateBatchableSprite(e, t), t._batcher.updateElement(t);
  }
  validateRenderable(e) {
    const t = this._getGpuSprite(e);
    return !t._batcher.checkAndUpdateTexture(
      t,
      e._texture
    );
  }
  _updateBatchableSprite(e, t) {
    t.geometry.update(e), t.setTexture(e._texture);
  }
  _getGpuSprite(e) {
    return e._gpuData[this._renderer.uid] || this._initGPUSprite(e);
  }
  _initGPUSprite(e) {
    const t = e._gpuData[this._renderer.uid] = new wr(), r = t;
    return r.renderable = e, r.transform = e.groupTransform, r.texture = e._texture, r.roundPixels = this._renderer._roundPixels | e._roundPixels, e.didViewUpdate || this._updateBatchableSprite(e, r), t;
  }
  destroy() {
    this._renderer = null;
  }
}
bt.extension = {
  type: [
    w.WebGLPipes,
    w.WebGPUPipes,
    w.CanvasPipes
  ],
  name: "nineSliceSprite"
};
const Tr = {
  name: "tiling-bit",
  vertex: {
    header: (
      /* wgsl */
      `
            struct TilingUniforms {
                uMapCoord:mat3x3<f32>,
                uClampFrame:vec4<f32>,
                uClampOffset:vec2<f32>,
                uTextureTransform:mat3x3<f32>,
                uSizeAnchor:vec4<f32>
            };

            @group(2) @binding(0) var<uniform> tilingUniforms: TilingUniforms;
            @group(2) @binding(1) var uTexture: texture_2d<f32>;
            @group(2) @binding(2) var uSampler: sampler;
        `
    ),
    main: (
      /* wgsl */
      `
            uv = (tilingUniforms.uTextureTransform * vec3(uv, 1.0)).xy;

            position = (position - tilingUniforms.uSizeAnchor.zw) * tilingUniforms.uSizeAnchor.xy;
        `
    )
  },
  fragment: {
    header: (
      /* wgsl */
      `
            struct TilingUniforms {
                uMapCoord:mat3x3<f32>,
                uClampFrame:vec4<f32>,
                uClampOffset:vec2<f32>,
                uTextureTransform:mat3x3<f32>,
                uSizeAnchor:vec4<f32>
            };

            @group(2) @binding(0) var<uniform> tilingUniforms: TilingUniforms;
            @group(2) @binding(1) var uTexture: texture_2d<f32>;
            @group(2) @binding(2) var uSampler: sampler;
        `
    ),
    main: (
      /* wgsl */
      `

            var coord = vUV + ceil(tilingUniforms.uClampOffset - vUV);
            coord = (tilingUniforms.uMapCoord * vec3(coord, 1.0)).xy;
            var unclamped = coord;
            coord = clamp(coord, tilingUniforms.uClampFrame.xy, tilingUniforms.uClampFrame.zw);

            var bias = 0.;

            if(unclamped.x == coord.x && unclamped.y == coord.y)
            {
                bias = -32.;
            }

            outColor = textureSampleBias(uTexture, uSampler, coord, bias);
        `
    )
  }
}, vr = {
  name: "tiling-bit",
  vertex: {
    header: (
      /* glsl */
      `
            uniform mat3 uTextureTransform;
            uniform vec4 uSizeAnchor;

        `
    ),
    main: (
      /* glsl */
      `
            uv = (uTextureTransform * vec3(aUV, 1.0)).xy;

            position = (position - uSizeAnchor.zw) * uSizeAnchor.xy;
        `
    )
  },
  fragment: {
    header: (
      /* glsl */
      `
            uniform sampler2D uTexture;
            uniform mat3 uMapCoord;
            uniform vec4 uClampFrame;
            uniform vec2 uClampOffset;
        `
    ),
    main: (
      /* glsl */
      `

        vec2 coord = vUV + ceil(uClampOffset - vUV);
        coord = (uMapCoord * vec3(coord, 1.0)).xy;
        vec2 unclamped = coord;
        coord = clamp(coord, uClampFrame.xy, uClampFrame.zw);

        outColor = texture(uTexture, coord, unclamped == coord ? 0.0 : -32.0);// lod-bias very negative to force lod 0

        `
    )
  }
};
let de, fe;
class Sr extends ve {
  constructor() {
    de ?? (de = Ne({
      name: "tiling-sprite-shader",
      bits: [
        Xt,
        Tr,
        qe
      ]
    })), fe ?? (fe = Qe({
      name: "tiling-sprite-shader",
      bits: [
        $t,
        vr,
        Je
      ]
    }));
    const e = new j({
      uMapCoord: { value: new U(), type: "mat3x3<f32>" },
      uClampFrame: { value: new Float32Array([0, 0, 1, 1]), type: "vec4<f32>" },
      uClampOffset: { value: new Float32Array([0, 0]), type: "vec2<f32>" },
      uTextureTransform: { value: new U(), type: "mat3x3<f32>" },
      uSizeAnchor: { value: new Float32Array([100, 100, 0.5, 0.5]), type: "vec4<f32>" }
    });
    super({
      glProgram: fe,
      gpuProgram: de,
      resources: {
        localUniforms: new j({
          uTransformMatrix: { value: new U(), type: "mat3x3<f32>" },
          uColor: { value: new Float32Array([1, 1, 1, 1]), type: "vec4<f32>" },
          uRound: { value: 0, type: "f32" }
        }),
        tilingUniforms: e,
        uTexture: M.EMPTY.source,
        uSampler: M.EMPTY.source.style
      }
    });
  }
  updateUniforms(e, t, r, i, s, n) {
    const a = this.resources.tilingUniforms, l = n.width, u = n.height, h = n.textureMatrix, c = a.uniforms.uTextureTransform;
    c.set(
      r.a * l / e,
      r.b * l / t,
      r.c * u / e,
      r.d * u / t,
      r.tx / e,
      r.ty / t
    ), c.invert(), a.uniforms.uMapCoord = h.mapCoord, a.uniforms.uClampFrame = h.uClampFrame, a.uniforms.uClampOffset = h.uClampOffset, a.uniforms.uTextureTransform = c, a.uniforms.uSizeAnchor[0] = e, a.uniforms.uSizeAnchor[1] = t, a.uniforms.uSizeAnchor[2] = i, a.uniforms.uSizeAnchor[3] = s, n && (this.resources.uTexture = n.source, this.resources.uSampler = n.source.style);
  }
}
class Cr extends Ce {
  constructor() {
    super({
      positions: new Float32Array([0, 0, 1, 0, 1, 1, 0, 1]),
      uvs: new Float32Array([0, 0, 1, 0, 1, 1, 0, 1]),
      indices: new Uint32Array([0, 1, 2, 0, 2, 3])
    });
  }
}
function Pr(o, e) {
  const t = o.anchor.x, r = o.anchor.y;
  e[0] = -t * o.width, e[1] = -r * o.height, e[2] = (1 - t) * o.width, e[3] = -r * o.height, e[4] = (1 - t) * o.width, e[5] = (1 - r) * o.height, e[6] = -t * o.width, e[7] = (1 - r) * o.height;
}
function Fr(o, e, t, r) {
  let i = 0;
  const s = o.length / e, n = r.a, a = r.b, l = r.c, u = r.d, h = r.tx, c = r.ty;
  for (t *= e; i < s; ) {
    const d = o[t], f = o[t + 1];
    o[t] = n * d + l * f + h, o[t + 1] = a * d + u * f + c, t += e, i++;
  }
}
function Br(o, e) {
  const t = o.texture, r = t.frame.width, i = t.frame.height;
  let s = 0, n = 0;
  o.applyAnchorToTexture && (s = o.anchor.x, n = o.anchor.y), e[0] = e[6] = -s, e[2] = e[4] = 1 - s, e[1] = e[3] = -n, e[5] = e[7] = 1 - n;
  const a = U.shared;
  a.copyFrom(o._tileTransform.matrix), a.tx /= o.width, a.ty /= o.height, a.invert(), a.scale(o.width / r, o.height / i), Fr(e, 2, 0, a);
}
const te = new Cr();
class kr {
  constructor() {
    this.canBatch = !0, this.geometry = new Ce({
      indices: te.indices.slice(),
      positions: te.positions.slice(),
      uvs: te.uvs.slice()
    });
  }
  destroy() {
    var e;
    this.geometry.destroy(), (e = this.shader) == null || e.destroy();
  }
}
class wt {
  constructor(e) {
    this._state = ne.default2d, this._renderer = e;
  }
  validateRenderable(e) {
    const t = this._getTilingSpriteData(e), r = t.canBatch;
    this._updateCanBatch(e);
    const i = t.canBatch;
    if (i && i === r) {
      const { batchableMesh: s } = t;
      return !s._batcher.checkAndUpdateTexture(
        s,
        e.texture
      );
    }
    return r !== i;
  }
  addRenderable(e, t) {
    const r = this._renderer.renderPipes.batch;
    this._updateCanBatch(e);
    const i = this._getTilingSpriteData(e), { geometry: s, canBatch: n } = i;
    if (n) {
      i.batchableMesh || (i.batchableMesh = new Pe());
      const a = i.batchableMesh;
      e.didViewUpdate && (this._updateBatchableMesh(e), a.geometry = s, a.renderable = e, a.transform = e.groupTransform, a.setTexture(e._texture)), a.roundPixels = this._renderer._roundPixels | e._roundPixels, r.addToBatch(a, t);
    } else
      r.break(t), i.shader || (i.shader = new Sr()), this.updateRenderable(e), t.add(e);
  }
  execute(e) {
    const { shader: t } = this._getTilingSpriteData(e);
    t.groups[0] = this._renderer.globalUniforms.bindGroup;
    const r = t.resources.localUniforms.uniforms;
    r.uTransformMatrix = e.groupTransform, r.uRound = this._renderer._roundPixels | e._roundPixels, le(
      e.groupColorAlpha,
      r.uColor,
      0
    ), this._state.blendMode = Te(e.groupBlendMode, e.texture._source), this._renderer.encoder.draw({
      geometry: te,
      shader: t,
      state: this._state
    });
  }
  updateRenderable(e) {
    const t = this._getTilingSpriteData(e), { canBatch: r } = t;
    if (r) {
      const { batchableMesh: i } = t;
      e.didViewUpdate && this._updateBatchableMesh(e), i._batcher.updateElement(i);
    } else if (e.didViewUpdate) {
      const { shader: i } = t;
      i.updateUniforms(
        e.width,
        e.height,
        e._tileTransform.matrix,
        e.anchor.x,
        e.anchor.y,
        e.texture
      );
    }
  }
  _getTilingSpriteData(e) {
    return e._gpuData[this._renderer.uid] || this._initTilingSpriteData(e);
  }
  _initTilingSpriteData(e) {
    const t = new kr();
    return t.renderable = e, e._gpuData[this._renderer.uid] = t, t;
  }
  _updateBatchableMesh(e) {
    const t = this._getTilingSpriteData(e), { geometry: r } = t, i = e.texture.source.style;
    i.addressMode !== "repeat" && (i.addressMode = "repeat", i.update()), Br(e, r.uvs), Pr(e, r.positions);
  }
  destroy() {
    this._renderer = null;
  }
  _updateCanBatch(e) {
    const t = this._getTilingSpriteData(e), r = e.texture;
    let i = !0;
    return this._renderer.type === we.WEBGL && (i = this._renderer.context.supports.nonPowOf2wrapping), t.canBatch = r.textureMatrix.isSimple && (i || r.source.isPowerOfTwo), t.canBatch;
  }
}
wt.extension = {
  type: [
    w.WebGLPipes,
    w.WebGPUPipes,
    w.CanvasPipes
  ],
  name: "tilingSprite"
};
const Rr = {
  name: "local-uniform-msdf-bit",
  vertex: {
    header: (
      /* wgsl */
      `
            struct LocalUniforms {
                uColor:vec4<f32>,
                uTransformMatrix:mat3x3<f32>,
                uDistance: f32,
                uRound:f32,
            }

            @group(2) @binding(0) var<uniform> localUniforms : LocalUniforms;
        `
    ),
    main: (
      /* wgsl */
      `
            vColor *= localUniforms.uColor;
            modelMatrix *= localUniforms.uTransformMatrix;
        `
    ),
    end: (
      /* wgsl */
      `
            if(localUniforms.uRound == 1)
            {
                vPosition = vec4(roundPixels(vPosition.xy, globalUniforms.uResolution), vPosition.zw);
            }
        `
    )
  },
  fragment: {
    header: (
      /* wgsl */
      `
            struct LocalUniforms {
                uColor:vec4<f32>,
                uTransformMatrix:mat3x3<f32>,
                uDistance: f32
            }

            @group(2) @binding(0) var<uniform> localUniforms : LocalUniforms;
         `
    ),
    main: (
      /* wgsl */
      `
            outColor = vec4<f32>(calculateMSDFAlpha(outColor, localUniforms.uColor, localUniforms.uDistance));
        `
    )
  }
}, Mr = {
  name: "local-uniform-msdf-bit",
  vertex: {
    header: (
      /* glsl */
      `
            uniform mat3 uTransformMatrix;
            uniform vec4 uColor;
            uniform float uRound;
        `
    ),
    main: (
      /* glsl */
      `
            vColor *= uColor;
            modelMatrix *= uTransformMatrix;
        `
    ),
    end: (
      /* glsl */
      `
            if(uRound == 1.)
            {
                gl_Position.xy = roundPixels(gl_Position.xy, uResolution);
            }
        `
    )
  },
  fragment: {
    header: (
      /* glsl */
      `
            uniform float uDistance;
         `
    ),
    main: (
      /* glsl */
      `
            outColor = vec4(calculateMSDFAlpha(outColor, vColor, uDistance));
        `
    )
  }
}, Ur = {
  name: "msdf-bit",
  fragment: {
    header: (
      /* wgsl */
      `
            fn calculateMSDFAlpha(msdfColor:vec4<f32>, shapeColor:vec4<f32>, distance:f32) -> f32 {

                // MSDF
                var median = msdfColor.r + msdfColor.g + msdfColor.b -
                    min(msdfColor.r, min(msdfColor.g, msdfColor.b)) -
                    max(msdfColor.r, max(msdfColor.g, msdfColor.b));

                // SDF
                median = min(median, msdfColor.a);

                var screenPxDistance = distance * (median - 0.5);
                var alpha = clamp(screenPxDistance + 0.5, 0.0, 1.0);
                if (median < 0.01) {
                    alpha = 0.0;
                } else if (median > 0.99) {
                    alpha = 1.0;
                }

                // Gamma correction for coverage-like alpha
                var luma: f32 = dot(shapeColor.rgb, vec3<f32>(0.299, 0.587, 0.114));
                var gamma: f32 = mix(1.0, 1.0 / 2.2, luma);
                var coverage: f32 = pow(shapeColor.a * alpha, gamma);

                return coverage;

            }
        `
    )
  }
}, Gr = {
  name: "msdf-bit",
  fragment: {
    header: (
      /* glsl */
      `
            float calculateMSDFAlpha(vec4 msdfColor, vec4 shapeColor, float distance) {

                // MSDF
                float median = msdfColor.r + msdfColor.g + msdfColor.b -
                                min(msdfColor.r, min(msdfColor.g, msdfColor.b)) -
                                max(msdfColor.r, max(msdfColor.g, msdfColor.b));

                // SDF
                median = min(median, msdfColor.a);

                float screenPxDistance = distance * (median - 0.5);
                float alpha = clamp(screenPxDistance + 0.5, 0.0, 1.0);

                if (median < 0.01) {
                    alpha = 0.0;
                } else if (median > 0.99) {
                    alpha = 1.0;
                }

                // Gamma correction for coverage-like alpha
                float luma = dot(shapeColor.rgb, vec3(0.299, 0.587, 0.114));
                float gamma = mix(1.0, 1.0 / 2.2, luma);
                float coverage = pow(shapeColor.a * alpha, gamma);

                return coverage;
            }
        `
    )
  }
};
let pe, ge;
class zr extends ve {
  constructor(e) {
    const t = new j({
      uColor: { value: new Float32Array([1, 1, 1, 1]), type: "vec4<f32>" },
      uTransformMatrix: { value: new U(), type: "mat3x3<f32>" },
      uDistance: { value: 4, type: "f32" },
      uRound: { value: 0, type: "f32" }
    });
    pe ?? (pe = Ne({
      name: "sdf-shader",
      bits: [
        Dt,
        Lt(e),
        Rr,
        Ur,
        qe
      ]
    })), ge ?? (ge = Qe({
      name: "sdf-shader",
      bits: [
        It,
        Ot(e),
        Mr,
        Gr,
        Je
      ]
    })), super({
      glProgram: ge,
      gpuProgram: pe,
      resources: {
        localUniforms: t,
        batchSamplers: Et(e)
      }
    });
  }
}
class Ar extends Ht {
  destroy() {
    this.context.customShader && this.context.customShader.destroy(), super.destroy();
  }
}
class Tt {
  constructor(e) {
    this._renderer = e;
  }
  validateRenderable(e) {
    const t = this._getGpuBitmapText(e);
    return this._renderer.renderPipes.graphics.validateRenderable(t);
  }
  addRenderable(e, t) {
    const r = this._getGpuBitmapText(e);
    Xe(e, r), e._didTextUpdate && (e._didTextUpdate = !1, this._updateContext(e, r)), this._renderer.renderPipes.graphics.addRenderable(r, t), r.context.customShader && this._updateDistanceField(e);
  }
  updateRenderable(e) {
    const t = this._getGpuBitmapText(e);
    Xe(e, t), this._renderer.renderPipes.graphics.updateRenderable(t), t.context.customShader && this._updateDistanceField(e);
  }
  _updateContext(e, t) {
    const { context: r } = t, i = rr.getFont(e.text, e._style);
    r.clear(), i.distanceField.type !== "none" && (r.customShader || (r.customShader = new zr(this._renderer.limits.maxBatchableTextures)));
    const s = L.graphemeSegmenter(e.text), n = e._style;
    let a = i.baseLineOffset;
    const l = nt(s, n, i, !0), u = n.padding, h = l.scale;
    let c = l.width, d = l.height + l.offsetY;
    n._stroke && (c += n._stroke.width / h, d += n._stroke.width / h), r.translate(-e._anchor._x * c - u, -e._anchor._y * d - u).scale(h, h);
    const f = i.applyFillAsTint ? n._fill.color : 16777215;
    let m = i.fontMetrics.fontSize, x = i.lineHeight;
    n.lineHeight && (m = n.fontSize / h, x = n.lineHeight / h);
    let _ = (x - m) / 2;
    _ - i.baseLineOffset < 0 && (_ = 0);
    for (let p = 0; p < l.lines.length; p++) {
      const b = l.lines[p];
      for (let y = 0; y < b.charPositions.length; y++) {
        const T = b.chars[y], S = i.chars[T];
        if (S != null && S.texture) {
          const k = S.texture;
          r.texture(
            k,
            f || "black",
            Math.round(b.charPositions[y] + S.xOffset),
            Math.round(a + S.yOffset + _),
            k.orig.width,
            k.orig.height
          );
        }
      }
      a += x;
    }
  }
  _getGpuBitmapText(e) {
    return e._gpuData[this._renderer.uid] || this.initGpuText(e);
  }
  initGpuText(e) {
    const t = new Ar();
    return e._gpuData[this._renderer.uid] = t, this._updateContext(e, t), t;
  }
  _updateDistanceField(e) {
    const t = this._getGpuBitmapText(e).context, r = e._style.fontFamily, i = A.get(`${r}-bitmap`), { a: s, b: n, c: a, d: l } = e.groupTransform, u = Math.sqrt(s * s + n * n), h = Math.sqrt(a * a + l * l), c = (Math.abs(u) + Math.abs(h)) / 2, d = i.baseRenderedFontSize / e._style.fontSize, f = c * i.distanceField.range * (1 / d);
    t.customShader.resources.localUniforms.uniforms.uDistance = f;
  }
  destroy() {
    this._renderer = null;
  }
}
Tt.extension = {
  type: [
    w.WebGLPipes,
    w.WebGPUPipes,
    w.CanvasPipes
  ],
  name: "bitmapText"
};
function Xe(o, e) {
  e.groupTransform = o.groupTransform, e.groupColorAlpha = o.groupColorAlpha, e.groupColor = o.groupColor, e.groupBlendMode = o.groupBlendMode, e.globalDisplayStatus = o.globalDisplayStatus, e.groupTransform = o.groupTransform, e.localDisplayStatus = o.localDisplayStatus, e.groupAlpha = o.groupAlpha, e._roundPixels = o._roundPixels;
}
class Wr extends Ze {
  /**
   * Creates an instance of BatchableHTMLText.
   * @param renderer - The renderer instance to be used.
   */
  constructor(e) {
    super(), this.generatingTexture = !1, this.currentKey = "--", this._renderer = e, e.runners.resolutionChange.add(this);
  }
  /** Handles resolution changes for the HTML text. If the text has auto resolution enabled, it triggers a view update. */
  resolutionChange() {
    const e = this.renderable;
    e._autoResolution && e.onViewUpdate();
  }
  /** Destroys the BatchableHTMLText instance. Returns the texture promise to the renderer and cleans up references. */
  destroy() {
    const { htmlText: e } = this._renderer;
    e.getReferenceCount(this.currentKey) === null ? e.returnTexturePromise(this.texturePromise) : e.decreaseReferenceCount(this.currentKey), this._renderer.runners.resolutionChange.remove(this), this.texturePromise = null, this._renderer = null;
  }
}
function _e(o, e) {
  const { texture: t, bounds: r } = o, i = e._style._getFinalPadding();
  Vt(r, e._anchor, t);
  const s = e._anchor._x * i * 2, n = e._anchor._y * i * 2;
  r.minX -= i - s, r.minY -= i - n, r.maxX -= i - s, r.maxY -= i - n;
}
class vt {
  constructor(e) {
    this._renderer = e;
  }
  validateRenderable(e) {
    const t = this._getGpuText(e), r = e.styleKey;
    return t.currentKey !== r;
  }
  addRenderable(e, t) {
    const r = this._getGpuText(e);
    if (e._didTextUpdate) {
      const i = e._autoResolution ? this._renderer.resolution : e.resolution;
      (r.currentKey !== e.styleKey || e.resolution !== i) && this._updateGpuText(e).catch((s) => {
        console.error(s);
      }), e._didTextUpdate = !1, _e(r, e);
    }
    this._renderer.renderPipes.batch.addToBatch(r, t);
  }
  updateRenderable(e) {
    const t = this._getGpuText(e);
    t._batcher.updateElement(t);
  }
  async _updateGpuText(e) {
    e._didTextUpdate = !1;
    const t = this._getGpuText(e);
    if (t.generatingTexture)
      return;
    const r = t.texturePromise;
    t.texturePromise = null, t.generatingTexture = !0, e._resolution = e._autoResolution ? this._renderer.resolution : e.resolution;
    let i = this._renderer.htmlText.getTexturePromise(e);
    r && (i = i.finally(() => {
      this._renderer.htmlText.decreaseReferenceCount(t.currentKey), this._renderer.htmlText.returnTexturePromise(r);
    })), t.texturePromise = i, t.currentKey = e.styleKey, t.texture = await i;
    const s = e.renderGroup || e.parentRenderGroup;
    s && (s.structureDidChange = !0), t.generatingTexture = !1, _e(t, e);
  }
  _getGpuText(e) {
    return e._gpuData[this._renderer.uid] || this.initGpuText(e);
  }
  initGpuText(e) {
    const t = new Wr(this._renderer);
    return t.renderable = e, t.transform = e.groupTransform, t.texture = M.EMPTY, t.bounds = { minX: 0, maxX: 1, minY: 0, maxY: 0 }, t.roundPixels = this._renderer._roundPixels | e._roundPixels, e._resolution = e._autoResolution ? this._renderer.resolution : e.resolution, e._gpuData[this._renderer.uid] = t, t;
  }
  destroy() {
    this._renderer = null;
  }
}
vt.extension = {
  type: [
    w.WebGLPipes,
    w.WebGPUPipes,
    w.CanvasPipes
  ],
  name: "htmlText"
};
function Dr() {
  const { userAgent: o } = V.get().getNavigator();
  return /^((?!chrome|android).)*safari/i.test(o);
}
const Lr = new Ke();
function St(o, e, t, r) {
  const i = Lr;
  i.minX = 0, i.minY = 0, i.maxX = o.width / r | 0, i.maxY = o.height / r | 0;
  const s = W.getOptimalTexture(
    i.width,
    i.height,
    r,
    !1
  );
  return s.source.uploadMethodId = "image", s.source.resource = o, s.source.alphaMode = "premultiply-alpha-on-upload", s.frame.width = e / r, s.frame.height = t / r, s.source.emit("update", s.source), s.updateUvs(), s;
}
function Ir(o, e) {
  const t = e.fontFamily, r = [], i = {}, s = /font-family:([^;"\s]+)/g, n = o.match(s);
  function a(l) {
    i[l] || (r.push(l), i[l] = !0);
  }
  if (Array.isArray(t))
    for (let l = 0; l < t.length; l++)
      a(t[l]);
  else
    a(t);
  n && n.forEach((l) => {
    const u = l.split(":")[1].trim();
    a(u);
  });
  for (const l in e.tagStyles) {
    const u = e.tagStyles[l].fontFamily;
    a(u);
  }
  return r;
}
async function Or(o) {
  const t = await (await V.get().fetch(o)).blob(), r = new FileReader();
  return await new Promise((s, n) => {
    r.onloadend = () => s(r.result), r.onerror = n, r.readAsDataURL(t);
  });
}
async function Er(o, e) {
  const t = await Or(e);
  return `@font-face {
        font-family: "${o.fontFamily}";
        font-weight: ${o.fontWeight};
        font-style: ${o.fontStyle};
        src: url('${t}');
    }`;
}
const me = /* @__PURE__ */ new Map();
async function Hr(o) {
  const e = o.filter((t) => A.has(`${t}-and-url`)).map((t) => {
    if (!me.has(t)) {
      const { entries: r } = A.get(`${t}-and-url`), i = [];
      r.forEach((s) => {
        const n = s.url, l = s.faces.map((u) => ({ weight: u.weight, style: u.style }));
        i.push(
          ...l.map(
            (u) => Er(
              {
                fontWeight: u.weight,
                fontStyle: u.style,
                fontFamily: t
              },
              n
            )
          )
        );
      }), me.set(
        t,
        Promise.all(i).then((s) => s.join(`
`))
      );
    }
    return me.get(t);
  });
  return (await Promise.all(e)).join(`
`);
}
function Vr(o, e, t, r, i) {
  const { domElement: s, styleElement: n, svgRoot: a } = i;
  s.innerHTML = `<style>${e.cssStyle}</style><div style='padding:0;'>${o}</div>`, s.setAttribute("style", `transform: scale(${t});transform-origin: top left; display: inline-block`), n.textContent = r;
  const { width: l, height: u } = i.image;
  return a.setAttribute("width", l.toString()), a.setAttribute("height", u.toString()), new XMLSerializer().serializeToString(a);
}
function Yr(o, e) {
  const t = K.getOptimalCanvasAndContext(
    o.width,
    o.height,
    e
  ), { context: r } = t;
  return r.clearRect(0, 0, o.width, o.height), r.drawImage(o, 0, 0), t;
}
function Xr(o, e, t) {
  return new Promise(async (r) => {
    t && await new Promise((i) => setTimeout(i, 100)), o.onload = () => {
      r();
    }, o.src = `data:image/svg+xml;charset=utf8,${encodeURIComponent(e)}`, o.crossOrigin = "anonymous";
  });
}
class Ct {
  constructor(e) {
    this._activeTextures = {}, this._renderer = e, this._createCanvas = e.type === we.WEBGPU;
  }
  /**
   * @param options
   * @deprecated Use getTexturePromise instead
   */
  getTexture(e) {
    return this.getTexturePromise(e);
  }
  /**
   * Increases the reference count for a texture.
   * @param text - The HTMLText instance associated with the texture.
   */
  getManagedTexture(e) {
    const t = e.styleKey;
    if (this._activeTextures[t])
      return this._increaseReferenceCount(t), this._activeTextures[t].promise;
    const r = this._buildTexturePromise(e).then((i) => (this._activeTextures[t].texture = i, i));
    return this._activeTextures[t] = {
      texture: null,
      promise: r,
      usageCount: 1
    }, r;
  }
  /**
   * Gets the current reference count for a texture associated with a text key.
   * @param textKey - The unique key identifying the text style configuration
   * @returns The number of Text instances currently using this texture
   */
  getReferenceCount(e) {
    var t;
    return ((t = this._activeTextures[e]) == null ? void 0 : t.usageCount) ?? null;
  }
  _increaseReferenceCount(e) {
    this._activeTextures[e].usageCount++;
  }
  /**
   * Decreases the reference count for a texture.
   * If the count reaches zero, the texture is cleaned up.
   * @param textKey - The key associated with the HTMLText instance.
   */
  decreaseReferenceCount(e) {
    const t = this._activeTextures[e];
    t && (t.usageCount--, t.usageCount === 0 && (t.texture ? this._cleanUp(t.texture) : t.promise.then((r) => {
      t.texture = r, this._cleanUp(t.texture);
    }).catch(() => {
      $("HTMLTextSystem: Failed to clean texture");
    }), this._activeTextures[e] = null));
  }
  /**
   * Returns a promise that resolves to a texture for the given HTMLText options.
   * @param options - The options for the HTMLText.
   * @returns A promise that resolves to a Texture.
   */
  getTexturePromise(e) {
    return this._buildTexturePromise(e);
  }
  async _buildTexturePromise(e) {
    const { text: t, style: r, resolution: i, textureStyle: s } = e, n = se.get(ct), a = Ir(t, r), l = await Hr(a), u = ur(t, r, l, n), h = Math.ceil(Math.ceil(Math.max(1, u.width) + r.padding * 2) * i), c = Math.ceil(Math.ceil(Math.max(1, u.height) + r.padding * 2) * i), d = n.image, f = 2;
    d.width = (h | 0) + f, d.height = (c | 0) + f;
    const m = Vr(t, r, i, l, n);
    await Xr(d, m, Dr() && a.length > 0);
    const x = d;
    let _;
    this._createCanvas && (_ = Yr(d, i));
    const p = St(
      _ ? _.canvas : x,
      d.width - f,
      d.height - f,
      i
    );
    return s && (p.source.style = s), this._createCanvas && (this._renderer.texture.initSource(p.source), K.returnCanvasAndContext(_)), se.return(n), p;
  }
  returnTexturePromise(e) {
    e.then((t) => {
      this._cleanUp(t);
    }).catch(() => {
      $("HTMLTextSystem: Failed to clean texture");
    });
  }
  _cleanUp(e) {
    W.returnTexture(e, !0), e.source.resource = null, e.source.uploadMethodId = "unknown";
  }
  destroy() {
    this._renderer = null;
    for (const e in this._activeTextures)
      this._activeTextures[e] && this.returnTexturePromise(this._activeTextures[e].promise);
    this._activeTextures = null;
  }
}
Ct.extension = {
  type: [
    w.WebGLSystem,
    w.WebGPUSystem,
    w.CanvasSystem
  ],
  name: "htmlText"
};
class $r extends Ze {
  constructor(e) {
    super(), this._renderer = e, e.runners.resolutionChange.add(this);
  }
  resolutionChange() {
    const e = this.renderable;
    e._autoResolution && e.onViewUpdate();
  }
  destroy() {
    const { canvasText: e } = this._renderer;
    e.getReferenceCount(this.currentKey) > 0 ? e.decreaseReferenceCount(this.currentKey) : this.texture && e.returnTexture(this.texture), this._renderer.runners.resolutionChange.remove(this), this._renderer = null;
  }
}
class Pt {
  constructor(e) {
    this._renderer = e;
  }
  validateRenderable(e) {
    const t = this._getGpuText(e), r = e.styleKey;
    return t.currentKey !== r ? !0 : e._didTextUpdate;
  }
  addRenderable(e, t) {
    const r = this._getGpuText(e);
    if (e._didTextUpdate) {
      const i = e._autoResolution ? this._renderer.resolution : e.resolution;
      (r.currentKey !== e.styleKey || e.resolution !== i) && this._updateGpuText(e), e._didTextUpdate = !1;
    }
    this._renderer.renderPipes.batch.addToBatch(r, t);
  }
  updateRenderable(e) {
    const t = this._getGpuText(e);
    t._batcher.updateElement(t);
  }
  _updateGpuText(e) {
    const t = this._getGpuText(e);
    t.texture && this._renderer.canvasText.decreaseReferenceCount(t.currentKey), e._resolution = e._autoResolution ? this._renderer.resolution : e.resolution, t.texture = this._renderer.canvasText.getManagedTexture(e), t.currentKey = e.styleKey, _e(t, e);
  }
  _getGpuText(e) {
    return e._gpuData[this._renderer.uid] || this.initGpuText(e);
  }
  initGpuText(e) {
    const t = new $r(this._renderer);
    return t.currentKey = "--", t.renderable = e, t.transform = e.groupTransform, t.bounds = { minX: 0, maxX: 1, minY: 0, maxY: 0 }, t.roundPixels = this._renderer._roundPixels | e._roundPixels, e._gpuData[this._renderer.uid] = t, t;
  }
  destroy() {
    this._renderer = null;
  }
}
Pt.extension = {
  type: [
    w.WebGLPipes,
    w.WebGPUPipes,
    w.CanvasPipes
  ],
  name: "text"
};
class Ft {
  constructor(e) {
    this._activeTextures = {}, this._renderer = e;
  }
  getTexture(e, t, r, i) {
    typeof e == "string" && (B("8.0.0", "CanvasTextSystem.getTexture: Use object TextOptions instead of separate arguments"), e = {
      text: e,
      style: r,
      resolution: t
    }), e.style instanceof N || (e.style = new N(e.style)), e.textureStyle instanceof J || (e.textureStyle = new J(e.textureStyle)), typeof e.text != "string" && (e.text = e.text.toString());
    const { text: s, style: n, textureStyle: a } = e, l = e.resolution ?? this._renderer.resolution, { frame: u, canvasAndContext: h } = he.getCanvasAndContext({
      text: s,
      style: n,
      resolution: l
    }), c = St(h.canvas, u.width, u.height, l);
    if (a && (c.source.style = a), n.trim && (u.pad(n.padding), c.frame.copyFrom(u), c.frame.scale(1 / l), c.updateUvs()), n.filters) {
      const d = this._applyFilters(c, n.filters);
      return this.returnTexture(c), he.returnCanvasAndContext(h), d;
    }
    return this._renderer.texture.initSource(c._source), he.returnCanvasAndContext(h), c;
  }
  /**
   * Returns a texture that was created wit the above `getTexture` function.
   * Handy if you are done with a texture and want to return it to the pool.
   * @param texture - The texture to be returned.
   */
  returnTexture(e) {
    const t = e.source;
    t.resource = null, t.uploadMethodId = "unknown", t.alphaMode = "no-premultiply-alpha", W.returnTexture(e, !0);
  }
  /**
   * Renders text to its canvas, and updates its texture.
   * @deprecated since 8.10.0
   */
  renderTextToCanvas() {
    B(
      "8.10.0",
      "CanvasTextSystem.renderTextToCanvas: no longer supported, use CanvasTextSystem.getTexture instead"
    );
  }
  /**
   * Gets or creates a managed texture for a Text object. This method handles texture reuse and reference counting.
   * @param text - The Text object that needs a texture
   * @returns A Texture instance that represents the rendered text
   * @remarks
   * This method performs the following:
   * 1. Sets the appropriate resolution based on auto-resolution settings
   * 2. Checks if a texture already exists for the text's style
   * 3. Creates a new texture if needed or returns an existing one
   * 4. Manages reference counting for texture reuse
   */
  getManagedTexture(e) {
    e._resolution = e._autoResolution ? this._renderer.resolution : e.resolution;
    const t = e.styleKey;
    if (this._activeTextures[t])
      return this._increaseReferenceCount(t), this._activeTextures[t].texture;
    const r = this.getTexture({
      text: e.text,
      style: e.style,
      resolution: e._resolution,
      textureStyle: e.textureStyle
    });
    return this._activeTextures[t] = {
      texture: r,
      usageCount: 1
    }, r;
  }
  /**
   * Decreases the reference count for a texture associated with a text key.
   * When the reference count reaches zero, the texture is returned to the pool.
   * @param textKey - The unique key identifying the text style configuration
   * @remarks
   * This method is crucial for memory management, ensuring textures are properly
   * cleaned up when they are no longer needed by any Text instances.
   */
  decreaseReferenceCount(e) {
    const t = this._activeTextures[e];
    t.usageCount--, t.usageCount === 0 && (this.returnTexture(t.texture), this._activeTextures[e] = null);
  }
  /**
   * Gets the current reference count for a texture associated with a text key.
   * @param textKey - The unique key identifying the text style configuration
   * @returns The number of Text instances currently using this texture
   */
  getReferenceCount(e) {
    var t;
    return ((t = this._activeTextures[e]) == null ? void 0 : t.usageCount) ?? 0;
  }
  _increaseReferenceCount(e) {
    this._activeTextures[e].usageCount++;
  }
  /**
   * Applies the specified filters to the given texture.
   *
   * This method takes a texture and a list of filters, applies the filters to the texture,
   * and returns the resulting texture. It also ensures that the alpha mode of the resulting
   * texture is set to 'premultiplied-alpha'.
   * @param {Texture} texture - The texture to which the filters will be applied.
   * @param {Filter[]} filters - The filters to apply to the texture.
   * @returns {Texture} The resulting texture after all filters have been applied.
   */
  _applyFilters(e, t) {
    const r = this._renderer.renderTarget.renderTarget, i = this._renderer.filter.generateFilteredTexture({
      texture: e,
      filters: t
    });
    return this._renderer.renderTarget.bind(r, !1), i;
  }
  destroy() {
    this._renderer = null;
    for (const e in this._activeTextures)
      this._activeTextures[e] && this.returnTexture(this._activeTextures[e].texture);
    this._activeTextures = null;
  }
}
Ft.extension = {
  type: [
    w.WebGLSystem,
    w.WebGPUSystem,
    w.CanvasSystem
  ],
  name: "canvasText"
};
P.add(et);
P.add(tt);
P.add(ht);
P.add(Yt);
P.add(pt);
P.add(mt);
P.add(xt);
P.add(Ft);
P.add(Pt);
P.add(Tt);
P.add(Ct);
P.add(vt);
P.add(wt);
P.add(bt);
P.add(ot);
P.add(at);
