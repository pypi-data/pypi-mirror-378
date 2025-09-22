import { E as g, U as ot, T as de, a as ut, a2 as w, a3 as U, s as C, ac as he, Z as W, ad as D, O as lt, l as Y, ae as ct, af as fe, _ as Ce, ag as I, ah as dt, ai as P, w as X, M as R, k as z, c as Se, F, a5 as se, R as ie, z as Pe, b as O, B, D as ne, x as K, aj as ht, ak as ae, J as te, al as L, q as oe, t as ft, G as pt, m as Fe, p as Be, a7 as Re, aa as Me, n as gt, o as mt, a8 as xt, a9 as _t, ab as yt, am as bt, an as vt, ao as N, e as T, ap as Tt } from "./Index-jQCzN2ap.js";
import { S as j, c as $, a as wt, b as Ct, B as Ue } from "./colorToUniform-zJcCVLeu.js";
class Ge {
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
        const { clientWidth: s, clientHeight: i } = this._resizeTo;
        t = s, r = i;
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
Ge.extension = g.Application;
class Ae {
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
          this._ticker && this._ticker.remove(this.render, this), this._ticker = t, t && t.add(this.render, this, ot.LOW);
        },
        get() {
          return this._ticker;
        }
      }
    ), this.stop = () => {
      this._ticker.stop();
    }, this.start = () => {
      this._ticker.start();
    }, this._ticker = null, this.ticker = e.sharedTicker ? de.shared : new de(), e.autoStart && this.start();
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
Ae.extension = g.Application;
class St extends ut {
  constructor() {
    super(...arguments), this.chars = /* @__PURE__ */ Object.create(null), this.lineHeight = 0, this.fontFamily = "", this.fontMetrics = { fontSize: 0, ascent: 0, descent: 0 }, this.baseLineOffset = 0, this.distanceField = { type: "none", range: 0 }, this.pages = [], this.applyFillAsTint = !0, this.baseMeasurementFontSize = 100, this.baseRenderedFontSize = 100;
  }
  /**
   * The name of the font face.
   * @deprecated since 8.0.0 Use `fontFamily` instead.
   */
  get font() {
    return w(U, "BitmapFont.font is deprecated, please use BitmapFont.fontFamily instead."), this.fontFamily;
  }
  /**
   * The map of base page textures (i.e., sheets of glyphs).
   * @deprecated since 8.0.0 Use `pages` instead.
   */
  get pageTextures() {
    return w(U, "BitmapFont.pageTextures is deprecated, please use BitmapFont.pages instead."), this.pages;
  }
  /**
   * The size of the font face in pixels.
   * @deprecated since 8.0.0 Use `fontMetrics.fontSize` instead.
   */
  get size() {
    return w(U, "BitmapFont.size is deprecated, please use BitmapFont.fontMetrics.fontSize instead."), this.fontMetrics.fontSize;
  }
  /**
   * The kind of distance field for this font or "none".
   * @deprecated since 8.0.0 Use `distanceField.type` instead.
   */
  get distanceFieldRange() {
    return w(U, "BitmapFont.distanceFieldRange is deprecated, please use BitmapFont.distanceField.range instead."), this.distanceField.range;
  }
  /**
   * The range of the distance field in pixels.
   * @deprecated since 8.0.0 Use `distanceField.range` instead.
   */
  get distanceFieldType() {
    return w(U, "BitmapFont.distanceFieldType is deprecated, please use BitmapFont.distanceField.type instead."), this.distanceField.type;
  }
  destroy(e = !1) {
    var t;
    this.emit("destroy", this), this.removeAllListeners();
    for (const r in this.chars)
      (t = this.chars[r].texture) == null || t.destroy();
    this.chars = null, e && (this.pages.forEach((r) => r.texture.destroy(!0)), this.pages = null);
  }
}
const ze = class ke extends St {
  /**
   * @param options - The options for the dynamic bitmap font.
   */
  constructor(e) {
    super(), this.resolution = 1, this.pages = [], this._padding = 0, this._measureCache = /* @__PURE__ */ Object.create(null), this._currentChars = [], this._currentX = 0, this._currentY = 0, this._currentMaxCharHeight = 0, this._currentPageIndex = -1, this._skipKerning = !1;
    const t = { ...ke.defaultOptions, ...e };
    this._textureSize = t.textureSize, this._mipmap = t.mipmap;
    const r = t.style.clone();
    t.overrideFill && (r._fill.color = 16777215, r._fill.alpha = 1, r._fill.texture = C.WHITE, r._fill.fill = null), this.applyFillAsTint = t.overrideFill;
    const s = r.fontSize;
    r.fontSize = this.baseMeasurementFontSize;
    const i = he(r);
    t.overrideSize ? r._stroke && (r._stroke.width *= this.baseRenderedFontSize / s) : r.fontSize = this.baseRenderedFontSize = s, this._style = r, this._skipKerning = t.skipKerning ?? !1, this.resolution = t.resolution ?? 1, this._padding = t.padding ?? 4, t.textureStyle && (this._textureStyle = t.textureStyle instanceof W ? t.textureStyle : new W(t.textureStyle)), this.fontMetrics = D.measureFont(i), this.lineHeight = r.lineHeight || this.fontMetrics.fontSize || r.fontSize;
  }
  ensureCharacters(e) {
    var x, p;
    const t = D.graphemeSegmenter(e).filter((_) => !this._currentChars.includes(_)).filter((_, b, v) => v.indexOf(_) === b);
    if (!t.length)
      return;
    this._currentChars = [...this._currentChars, ...t];
    let r;
    this._currentPageIndex === -1 ? r = this._nextPage() : r = this.pages[this._currentPageIndex];
    let { canvas: s, context: i } = r.canvasAndContext, n = r.texture.source;
    const a = this._style;
    let u = this._currentX, l = this._currentY, d = this._currentMaxCharHeight;
    const c = this.baseRenderedFontSize / this.baseMeasurementFontSize, h = this._padding * c;
    let f = !1;
    const y = s.width / this.resolution, m = s.height / this.resolution;
    for (let _ = 0; _ < t.length; _++) {
      const b = t[_], v = D.measureText(b, a, s, !1);
      v.lineHeight = v.height;
      const S = v.width * c, G = Math.ceil((a.fontStyle === "italic" ? 2 : 1) * S), k = v.height * c, M = G + h * 2, E = k + h * 2;
      if (f = !1, b !== `
` && b !== "\r" && b !== "	" && b !== " " && (f = !0, d = Math.ceil(Math.max(E, d))), u + M > y && (l += d, d = E, u = 0, l + d > m)) {
        n.update();
        const A = this._nextPage();
        s = A.canvasAndContext.canvas, i = A.canvasAndContext.context, n = A.texture.source, u = 0, l = 0, d = 0;
      }
      const nt = S / c - (((x = a.dropShadow) == null ? void 0 : x.distance) ?? 0) - (((p = a._stroke) == null ? void 0 : p.width) ?? 0);
      if (this.chars[b] = {
        id: b.codePointAt(0),
        xOffset: -this._padding,
        yOffset: -this._padding,
        xAdvance: nt,
        kerning: {}
      }, f) {
        this._drawGlyph(
          i,
          v,
          u + h,
          l + h,
          c,
          a
        );
        const A = n.width * c, ce = n.height * c, at = new lt(
          u / A * n.width,
          l / ce * n.height,
          M / A * n.width,
          E / ce * n.height
        );
        this.chars[b].texture = new C({
          source: n,
          frame: at
        }), u += Math.ceil(M);
      }
    }
    n.update(), this._currentX = u, this._currentY = l, this._currentMaxCharHeight = d, this._skipKerning && this._applyKerning(t, i);
  }
  /**
   * @deprecated since 8.0.0
   * The map of base page textures (i.e., sheets of glyphs).
   */
  get pageTextures() {
    return w(U, "BitmapFont.pageTextures is deprecated, please use BitmapFont.pages instead."), this.pages;
  }
  _applyKerning(e, t) {
    const r = this._measureCache;
    for (let s = 0; s < e.length; s++) {
      const i = e[s];
      for (let n = 0; n < this._currentChars.length; n++) {
        const a = this._currentChars[n];
        let u = r[i];
        u || (u = r[i] = t.measureText(i).width);
        let l = r[a];
        l || (l = r[a] = t.measureText(a).width);
        let d = t.measureText(i + a).width, c = d - (u + l);
        c && (this.chars[i].kerning[a] = c), d = t.measureText(i + a).width, c = d - (u + l), c && (this.chars[a].kerning[i] = c);
      }
    }
  }
  _nextPage() {
    this._currentPageIndex++;
    const e = this.resolution, t = Y.getOptimalCanvasAndContext(
      this._textureSize,
      this._textureSize,
      e
    );
    this._setupContext(t.context, this._style, e);
    const r = e * (this.baseRenderedFontSize / this.baseMeasurementFontSize), s = new C({
      source: new ct({
        resource: t.canvas,
        resolution: r,
        alphaMode: "premultiply-alpha-on-upload",
        autoGenerateMipmaps: this._mipmap
      })
    });
    this._textureStyle && (s.source.style = this._textureStyle);
    const i = {
      canvasAndContext: t,
      texture: s
    };
    return this.pages[this._currentPageIndex] = i, i;
  }
  // canvas style!
  _setupContext(e, t, r) {
    t.fontSize = this.baseRenderedFontSize, e.scale(r, r), e.font = he(t), t.fontSize = this.baseMeasurementFontSize, e.textBaseline = t.textBaseline;
    const s = t._stroke, i = (s == null ? void 0 : s.width) ?? 0;
    if (s && (e.lineWidth = i, e.lineJoin = s.join, e.miterLimit = s.miterLimit, e.strokeStyle = fe(s, e)), t._fill && (e.fillStyle = fe(t._fill, e)), t.dropShadow) {
      const n = t.dropShadow, a = Ce.shared.setValue(n.color).toArray(), u = n.blur * r, l = n.distance * r;
      e.shadowColor = `rgba(${a[0] * 255},${a[1] * 255},${a[2] * 255},${n.alpha})`, e.shadowBlur = u, e.shadowOffsetX = Math.cos(n.angle) * l, e.shadowOffsetY = Math.sin(n.angle) * l;
    } else
      e.shadowColor = "black", e.shadowBlur = 0, e.shadowOffsetX = 0, e.shadowOffsetY = 0;
  }
  _drawGlyph(e, t, r, s, i, n) {
    const a = t.text, u = t.fontProperties, l = n._stroke, d = ((l == null ? void 0 : l.width) ?? 0) * i, c = r + d / 2, h = s - d / 2, f = u.descent * i, y = t.lineHeight * i;
    let m = !1;
    n.stroke && d && (m = !0, e.strokeText(a, c, h + y - f));
    const { shadowBlur: x, shadowOffsetX: p, shadowOffsetY: _ } = e;
    n._fill && (m && (e.shadowBlur = 0, e.shadowOffsetX = 0, e.shadowOffsetY = 0), e.fillText(a, c, h + y - f)), m && (e.shadowBlur = x, e.shadowOffsetX = p, e.shadowOffsetY = _);
  }
  destroy() {
    super.destroy();
    for (let e = 0; e < this.pages.length; e++) {
      const { canvasAndContext: t, texture: r } = this.pages[e];
      Y.returnCanvasAndContext(t), r.destroy(!0);
    }
    this.pages = null;
  }
};
ze.defaultOptions = {
  textureSize: 512,
  style: new I(),
  mipmap: !0
};
let pe = ze;
function De(o, e, t, r) {
  const s = {
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
  s.offsetY = t.baseLineOffset;
  let i = s.lines[0], n = null, a = !0;
  const u = {
    width: 0,
    start: 0,
    index: 0,
    // use index to not modify the array as we use it a lot!
    positions: [],
    chars: []
  }, l = t.baseMeasurementFontSize / e.fontSize, d = e.letterSpacing * l, c = e.wordWrapWidth * l, h = e.lineHeight ? e.lineHeight * l : t.lineHeight, f = e.wordWrap && e.breakWords, y = (p) => {
    const _ = i.width;
    for (let b = 0; b < u.index; b++) {
      const v = p.positions[b];
      i.chars.push(p.chars[b]), i.charPositions.push(v + _);
    }
    i.width += p.width, a = !1, u.width = 0, u.index = 0, u.chars.length = 0;
  }, m = () => {
    let p = i.chars.length - 1;
    if (r) {
      let _ = i.chars[p];
      for (; _ === " "; )
        i.width -= t.chars[_].xAdvance, _ = i.chars[--p];
    }
    s.width = Math.max(s.width, i.width), i = {
      width: 0,
      charPositions: [],
      chars: [],
      spaceWidth: 0,
      spacesIndex: []
    }, a = !0, s.lines.push(i), s.height += h;
  }, x = (p) => p - d > c;
  for (let p = 0; p < o.length + 1; p++) {
    let _;
    const b = p === o.length;
    b || (_ = o[p]);
    const v = t.chars[_] || t.chars[" "];
    if (/(?:\s)/.test(_) || _ === "\r" || _ === `
` || b) {
      if (!a && e.wordWrap && x(i.width + u.width) ? (m(), y(u), b || i.charPositions.push(0)) : (u.start = i.width, y(u), b || i.charPositions.push(0)), _ === "\r" || _ === `
`)
        m();
      else if (!b) {
        const M = v.xAdvance + (v.kerning[n] || 0) + d;
        i.width += M, i.spaceWidth = M, i.spacesIndex.push(i.charPositions.length), i.chars.push(_);
      }
    } else {
      const k = v.kerning[n] || 0, M = v.xAdvance + k + d;
      f && x(i.width + u.width + M) && (y(u), m()), u.positions[u.index++] = u.width + k, u.chars.push(_), u.width += M;
    }
    n = _;
  }
  return m(), e.align === "center" ? Pt(s) : e.align === "right" ? Ft(s) : e.align === "justify" && Bt(s), s;
}
function Pt(o) {
  for (let e = 0; e < o.lines.length; e++) {
    const t = o.lines[e], r = o.width / 2 - t.width / 2;
    for (let s = 0; s < t.charPositions.length; s++)
      t.charPositions[s] += r;
  }
}
function Ft(o) {
  for (let e = 0; e < o.lines.length; e++) {
    const t = o.lines[e], r = o.width - t.width;
    for (let s = 0; s < t.charPositions.length; s++)
      t.charPositions[s] += r;
  }
}
function Bt(o) {
  const e = o.width;
  for (let t = 0; t < o.lines.length; t++) {
    const r = o.lines[t];
    let s = 0, i = r.spacesIndex[s++], n = 0;
    const a = r.spacesIndex.length, l = (e - r.width) / a;
    for (let d = 0; d < r.charPositions.length; d++)
      d === i && (i = r.spacesIndex[s++], n += l), r.charPositions[d] += n;
  }
}
function Rt(o) {
  if (o === "")
    return [];
  typeof o == "string" && (o = [o]);
  const e = [];
  for (let t = 0, r = o.length; t < r; t++) {
    const s = o[t];
    if (Array.isArray(s)) {
      if (s.length !== 2)
        throw new Error(`[BitmapFont]: Invalid character range length, expecting 2 got ${s.length}.`);
      if (s[0].length === 0 || s[1].length === 0)
        throw new Error("[BitmapFont]: Invalid character delimiter.");
      const i = s[0].charCodeAt(0), n = s[1].charCodeAt(0);
      if (n < i)
        throw new Error("[BitmapFont]: Invalid character range.");
      for (let a = i, u = n; a <= u; a++)
        e.push(String.fromCharCode(a));
    } else
      e.push(...Array.from(s));
  }
  if (e.length === 0)
    throw new Error("[BitmapFont]: Empty set when resolving characters.");
  return e;
}
let H = 0;
class Mt {
  constructor() {
    this.ALPHA = [["a", "z"], ["A", "Z"], " "], this.NUMERIC = [["0", "9"]], this.ALPHANUMERIC = [["a", "z"], ["A", "Z"], ["0", "9"], " "], this.ASCII = [[" ", "~"]], this.defaultOptions = {
      chars: this.ALPHANUMERIC,
      resolution: 1,
      padding: 4,
      skipKerning: !1,
      textureStyle: null
    }, this.measureCache = dt(1e3);
  }
  /**
   * Get a font for the specified text and style.
   * @param text - The text to get the font for
   * @param style - The style to use
   */
  getFont(e, t) {
    var n;
    let r = `${t.fontFamily}-bitmap`, s = !0;
    if (t._fill.fill && !t._stroke ? (r += t._fill.fill.styleKey, s = !1) : (t._stroke || t.dropShadow) && (r = `${t.styleKey}-bitmap`, s = !1), !P.has(r)) {
      const a = Object.create(t);
      a.lineHeight = 0;
      const u = new pe({
        style: a,
        overrideFill: s,
        overrideSize: !0,
        ...this.defaultOptions
      });
      H++, H > 50 && X("BitmapText", `You have dynamically created ${H} bitmap fonts, this can be inefficient. Try pre installing your font styles using \`BitmapFont.install({name:"style1", style})\``), u.once("destroy", () => {
        H--, P.remove(r);
      }), P.set(
        r,
        u
      );
    }
    const i = P.get(r);
    return (n = i.ensureCharacters) == null || n.call(i, e), i;
  }
  /**
   * Get the layout of a text for the specified style.
   * @param text - The text to get the layout for
   * @param style - The style to use
   * @param trimEnd - Whether to ignore whitespaces at the end of each line
   */
  getLayout(e, t, r = !0) {
    const s = this.getFont(e, t), i = `${e}-${t.styleKey}-${r}`;
    if (this.measureCache.has(i))
      return this.measureCache.get(i);
    const n = D.graphemeSegmenter(e), a = De(n, t, s, r);
    return this.measureCache.set(i, a), a;
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
    var l, d, c, h;
    let t = e[0];
    typeof t == "string" && (t = {
      name: t,
      style: e[1],
      chars: (l = e[2]) == null ? void 0 : l.chars,
      resolution: (d = e[2]) == null ? void 0 : d.resolution,
      padding: (c = e[2]) == null ? void 0 : c.padding,
      skipKerning: (h = e[2]) == null ? void 0 : h.skipKerning
    }, w(U, "BitmapFontManager.install(name, style, options) is deprecated, use BitmapFontManager.install({name, style, ...options})"));
    const r = t == null ? void 0 : t.name;
    if (!r)
      throw new Error("[BitmapFontManager] Property `name` is required.");
    t = { ...this.defaultOptions, ...t };
    const s = t.style, i = s instanceof I ? s : new I(s), n = t.dynamicFill ?? this._canUseTintForStyle(i), a = new pe({
      style: i,
      overrideFill: n,
      skipKerning: t.skipKerning,
      padding: t.padding,
      resolution: t.resolution,
      overrideSize: !1,
      textureStyle: t.textureStyle
    }), u = Rt(t.chars);
    return a.ensureCharacters(u.join("")), P.set(`${r}-bitmap`, a), a.once("destroy", () => P.remove(`${r}-bitmap`)), a;
  }
  /**
   * Uninstalls a bitmap font from the cache.
   * @param {string} name - The name of the bitmap font to uninstall.
   */
  uninstall(e) {
    const t = `${e}-bitmap`, r = P.get(t);
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
const Ut = new Mt();
class Oe {
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
Oe.extension = {
  type: [
    g.WebGLPipes,
    g.WebGPUPipes,
    g.CanvasPipes
  ],
  name: "filter"
};
const ge = new R();
function Gt(o, e) {
  e.clear();
  const t = e.matrix;
  for (let r = 0; r < o.length; r++) {
    const s = o[r];
    if (s.globalDisplayStatus < 7)
      continue;
    const i = s.renderGroup ?? s.parentRenderGroup;
    i != null && i.isCachedAsTexture ? e.matrix = ge.copyFrom(i.textureOffsetInverseTransform).append(s.worldTransform) : i != null && i._parentCacheAsTextureRenderGroup ? e.matrix = ge.copyFrom(i._parentCacheAsTextureRenderGroup.inverseWorldTransform).append(s.groupTransform) : e.matrix = s.worldTransform, e.addBounds(s.bounds);
  }
  return e.matrix = t, e;
}
const At = new se({
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
class zt {
  constructor() {
    this.skip = !1, this.inputTexture = null, this.backTexture = null, this.filters = null, this.bounds = new Pe(), this.container = null, this.blendRequired = !1, this.outputRenderSurface = null, this.globalFrame = { x: 0, y: 0, width: 0, height: 0 };
  }
}
class We {
  constructor(e) {
    this._filterStackIndex = 0, this._filterStack = [], this._filterGlobalUniforms = new z({
      uInputSize: { value: new Float32Array(4), type: "vec4<f32>" },
      uInputPixel: { value: new Float32Array(4), type: "vec4<f32>" },
      uInputClamp: { value: new Float32Array(4), type: "vec4<f32>" },
      uOutputFrame: { value: new Float32Array(4), type: "vec4<f32>" },
      uGlobalFrame: { value: new Float32Array(4), type: "vec4<f32>" },
      uOutputTexture: { value: new Float32Array(4), type: "vec4<f32>" }
    }), this._globalFilterBindGroup = new Se({}), this.renderer = e;
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
    const t = this.renderer, r = e.filterEffect.filters, s = this._pushFilterData();
    s.skip = !1, s.filters = r, s.container = e.container, s.outputRenderSurface = t.renderTarget.renderSurface;
    const i = t.renderTarget.renderTarget.colorTexture.source, n = i.resolution, a = i.antialias;
    if (r.length === 0) {
      s.skip = !0;
      return;
    }
    const u = s.bounds;
    if (this._calculateFilterArea(e, u), this._calculateFilterBounds(s, t.renderTarget.rootViewPort, a, n, 1), s.skip)
      return;
    const l = this._getPreviousFilterData(), d = this._findFilterResolution(n);
    let c = 0, h = 0;
    l && (c = l.bounds.minX, h = l.bounds.minY), this._calculateGlobalFrame(
      s,
      c,
      h,
      d,
      i.width,
      i.height
    ), this._setupFilterTextures(s, u, t, l);
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
    const s = e.source, i = s.resolution, n = s.antialias;
    if (t.length === 0)
      return r.skip = !0, e;
    const a = r.bounds;
    if (a.addRect(e.frame), this._calculateFilterBounds(r, a.rectangle, n, i, 0), r.skip)
      return e;
    const u = i;
    this._calculateGlobalFrame(
      r,
      0,
      0,
      u,
      s.width,
      s.height
    ), r.outputRenderSurface = F.getOptimalTexture(
      a.width,
      a.height,
      r.resolution,
      r.antialias
    ), r.backTexture = C.EMPTY, r.inputTexture = e, this.renderer.renderTarget.finishRenderPass(), this._applyFiltersToTexture(r, !0);
    const h = r.outputRenderSurface;
    return h.source.alphaMode = "premultiplied-alpha", h;
  }
  /** @internal */
  pop() {
    const e = this.renderer, t = this._popFilterData();
    t.skip || (e.globalUniforms.pop(), e.renderTarget.finishRenderPass(), this._activeFilterData = t, this._applyFiltersToTexture(t, !1), t.blendRequired && F.returnTexture(t.backTexture), F.returnTexture(t.inputTexture));
  }
  /**
   * Copies the last render surface to a texture.
   * @param lastRenderSurface - The last render surface to copy from.
   * @param bounds - The bounds of the area to copy.
   * @param previousBounds - The previous bounds to use for offsetting the copy.
   */
  getBackTexture(e, t, r) {
    const s = e.colorTexture.source._resolution, i = F.getOptimalTexture(
      t.width,
      t.height,
      s,
      !1
    );
    let n = t.minX, a = t.minY;
    r && (n -= r.minX, a -= r.minY), n = Math.floor(n * s), a = Math.floor(a * s);
    const u = Math.ceil(t.width * s), l = Math.ceil(t.height * s);
    return this.renderer.renderTarget.copyToTexture(
      e,
      i,
      { x: n, y: a },
      { width: u, height: l },
      { x: 0, y: 0 }
    ), i;
  }
  /**
   * Applies a filter to a texture.
   * @param filter - The filter to apply.
   * @param input - The input texture.
   * @param output - The output render surface.
   * @param clear - Whether to clear the output surface before applying the filter.
   */
  applyFilter(e, t, r, s) {
    const i = this.renderer, n = this._activeFilterData, u = n.outputRenderSurface === r, l = i.renderTarget.rootRenderTarget.colorTexture.source._resolution, d = this._findFilterResolution(l);
    let c = 0, h = 0;
    if (u) {
      const f = this._findPreviousFilterOffset();
      c = f.x, h = f.y;
    }
    this._updateFilterUniforms(t, r, n, c, h, d, u, s), this._setupBindGroupsAndRender(e, t, i);
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
    const r = this._activeFilterData, s = e.set(
      r.inputTexture._source.width,
      0,
      0,
      r.inputTexture._source.height,
      r.bounds.minX,
      r.bounds.minY
    ), i = t.worldTransform.copyTo(R.shared), n = t.renderGroup || t.parentRenderGroup;
    return n && n.cacheToLocalTransform && i.prepend(n.cacheToLocalTransform), i.invert(), s.prepend(i), s.scale(
      1 / t.texture.orig.width,
      1 / t.texture.orig.height
    ), s.translate(t.anchor.x, t.anchor.y), s;
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
      const s = r.renderPipes.uniformBatch.getUboResource(this._filterGlobalUniforms);
      this._globalFilterBindGroup.setResource(s, 0);
    } else
      this._globalFilterBindGroup.setResource(this._filterGlobalUniforms, 0);
    this._globalFilterBindGroup.setResource(t.source, 1), this._globalFilterBindGroup.setResource(t.source.style, 2), e.groups[0] = this._globalFilterBindGroup, r.encoder.draw({
      geometry: At,
      shader: e,
      state: e._state,
      topology: "triangle-list"
    }), r.type === ie.WEBGL && r.renderTarget.finishRenderPass();
  }
  /**
   * Sets up the filter textures including input texture and back texture if needed.
   * @param filterData - The filter data to update
   * @param bounds - The bounds for the texture
   * @param renderer - The renderer instance
   * @param previousFilterData - The previous filter data for back texture calculation
   */
  _setupFilterTextures(e, t, r, s) {
    if (e.backTexture = C.EMPTY, e.inputTexture = F.getOptimalTexture(
      t.width,
      t.height,
      e.resolution,
      e.antialias
    ), e.blendRequired) {
      r.renderTarget.finishRenderPass();
      const i = r.renderTarget.getRenderTarget(e.outputRenderSurface);
      e.backTexture = this.getBackTexture(i, t, s == null ? void 0 : s.bounds);
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
  _calculateGlobalFrame(e, t, r, s, i, n) {
    const a = e.globalFrame;
    a.x = t * s, a.y = r * s, a.width = i * s, a.height = n * s;
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
  _updateFilterUniforms(e, t, r, s, i, n, a, u) {
    const l = this._filterGlobalUniforms.uniforms, d = l.uOutputFrame, c = l.uInputSize, h = l.uInputPixel, f = l.uInputClamp, y = l.uGlobalFrame, m = l.uOutputTexture;
    a ? (d[0] = r.bounds.minX - s, d[1] = r.bounds.minY - i) : (d[0] = 0, d[1] = 0), d[2] = e.frame.width, d[3] = e.frame.height, c[0] = e.source.width, c[1] = e.source.height, c[2] = 1 / c[0], c[3] = 1 / c[1], h[0] = e.source.pixelWidth, h[1] = e.source.pixelHeight, h[2] = 1 / h[0], h[3] = 1 / h[1], f[0] = 0.5 * h[2], f[1] = 0.5 * h[3], f[2] = e.frame.width * c[2] - 0.5 * h[2], f[3] = e.frame.height * c[3] - 0.5 * h[3];
    const x = this.renderer.renderTarget.rootRenderTarget.colorTexture;
    y[0] = s * n, y[1] = i * n, y[2] = x.source.width * n, y[3] = x.source.height * n, t instanceof C && (t.source.resource = null);
    const p = this.renderer.renderTarget.getRenderTarget(t);
    this.renderer.renderTarget.bind(t, !!u), t instanceof C ? (m[0] = t.frame.width, m[1] = t.frame.height) : (m[0] = p.width, m[1] = p.height), m[2] = p.isRoot ? -1 : 1, this._filterGlobalUniforms.update();
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
      const s = this._filterStack[r];
      if (!s.skip) {
        e = s.bounds.minX, t = s.bounds.minY;
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
    if (e.renderables ? Gt(e.renderables, t) : e.filterEffect.filterArea ? (t.clear(), t.addRect(e.filterEffect.filterArea), t.applyMatrix(e.container.worldTransform)) : e.container.getFastGlobalBounds(!0, t), e.container) {
      const s = (e.container.renderGroup || e.container.parentRenderGroup).cacheToLocalTransform;
      s && t.applyMatrix(s);
    }
  }
  _applyFiltersToTexture(e, t) {
    const r = e.inputTexture, s = e.bounds, i = e.filters;
    if (this._globalFilterBindGroup.setResource(r.source.style, 2), this._globalFilterBindGroup.setResource(e.backTexture.source, 3), i.length === 1)
      i[0].apply(this, r, e.outputRenderSurface, t);
    else {
      let n = e.inputTexture;
      const a = F.getOptimalTexture(
        s.width,
        s.height,
        n.source._resolution,
        !1
      );
      let u = a, l = 0;
      for (l = 0; l < i.length - 1; ++l) {
        i[l].apply(this, n, u, !0);
        const c = n;
        n = u, u = c;
      }
      i[l].apply(this, n, e.outputRenderSurface, t), F.returnTexture(a);
    }
  }
  _calculateFilterBounds(e, t, r, s, i) {
    var m;
    const n = this.renderer, a = e.bounds, u = e.filters;
    let l = 1 / 0, d = 0, c = !0, h = !1, f = !1, y = !0;
    for (let x = 0; x < u.length; x++) {
      const p = u[x];
      if (l = Math.min(l, p.resolution === "inherit" ? s : p.resolution), d += p.padding, p.antialias === "off" ? c = !1 : p.antialias === "inherit" && c && (c = r), p.clipToViewport || (y = !1), !!!(p.compatibleRenderers & n.type)) {
        f = !1;
        break;
      }
      if (p.blendRequired && !(((m = n.backBuffer) == null ? void 0 : m.useBackBuffer) ?? !0)) {
        X("Blend filter requires backBuffer on WebGL renderer to be enabled. Set `useBackBuffer: true` in the renderer options."), f = !1;
        break;
      }
      f = p.enabled || f, h || (h = p.blendRequired);
    }
    if (!f) {
      e.skip = !0;
      return;
    }
    if (y && a.fitBounds(0, t.width / s, 0, t.height / s), a.scale(l).ceil().scale(1 / l).pad((d | 0) * i), !a.isPositive) {
      e.skip = !0;
      return;
    }
    e.antialias = c, e.resolution = l, e.blendRequired = h;
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
    return e || (e = this._filterStack[this._filterStackIndex] = new zt()), this._filterStackIndex++, e;
  }
}
We.extension = {
  type: [
    g.WebGLSystem,
    g.WebGPUSystem
  ],
  name: "filter"
};
const Ie = class Ee extends se {
  constructor(...e) {
    let t = e[0] ?? {};
    t instanceof Float32Array && (w(U, "use new MeshGeometry({ positions, uvs, indices }) instead"), t = {
      positions: t,
      uvs: e[1],
      indices: e[2]
    }), t = { ...Ee.defaultOptions, ...t };
    const r = t.positions || new Float32Array([0, 0, 1, 0, 1, 1, 0, 1]);
    let s = t.uvs;
    s || (t.positions ? s = new Float32Array(r.length) : s = new Float32Array([0, 0, 1, 0, 1, 1, 0, 1]));
    const i = t.indices || new Uint32Array([0, 1, 2, 0, 2, 3]), n = t.shrinkBuffersToFit, a = new O({
      data: r,
      label: "attribute-mesh-positions",
      shrinkToFit: n,
      usage: B.VERTEX | B.COPY_DST
    }), u = new O({
      data: s,
      label: "attribute-mesh-uvs",
      shrinkToFit: n,
      usage: B.VERTEX | B.COPY_DST
    }), l = new O({
      data: i,
      label: "index-mesh-buffer",
      shrinkToFit: n,
      usage: B.INDEX | B.COPY_DST
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
          buffer: u,
          format: "float32x2",
          stride: 2 * 4,
          offset: 0
        }
      },
      indexBuffer: l,
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
Ie.defaultOptions = {
  topology: "triangle-list",
  shrinkBuffersToFit: !1
};
let ue = Ie;
const me = "http://www.w3.org/2000/svg", xe = "http://www.w3.org/1999/xhtml";
class Le {
  constructor() {
    this.svgRoot = document.createElementNS(me, "svg"), this.foreignObject = document.createElementNS(me, "foreignObject"), this.domElement = document.createElementNS(xe, "div"), this.styleElement = document.createElementNS(xe, "style");
    const { foreignObject: e, svgRoot: t, styleElement: r, domElement: s } = this;
    e.setAttribute("width", "10000"), e.setAttribute("height", "10000"), e.style.overflow = "hidden", t.appendChild(e), e.appendChild(r), e.appendChild(s), this.image = ne.get().createImage();
  }
  destroy() {
    this.svgRoot.remove(), this.foreignObject.remove(), this.styleElement.remove(), this.domElement.remove(), this.image.src = "", this.image.remove(), this.svgRoot = null, this.foreignObject = null, this.styleElement = null, this.domElement = null, this.image = null, this.canvasAndContext = null;
  }
}
let _e;
function kt(o, e, t, r) {
  r || (r = _e || (_e = new Le()));
  const { domElement: s, styleElement: i, svgRoot: n } = r;
  s.innerHTML = `<style>${e.cssStyle};</style><div style='padding:0'>${o}</div>`, s.setAttribute("style", "transform-origin: top left; display: inline-block"), t && (i.textContent = t), document.body.appendChild(n);
  const a = s.getBoundingClientRect();
  n.remove();
  const u = e.padding * 2;
  return {
    width: a.width - u,
    height: a.height - u
  };
}
class Dt {
  constructor() {
    this.batches = [], this.batched = !1;
  }
  destroy() {
    this.batches.forEach((e) => {
      K.return(e);
    }), this.batches.length = 0;
  }
}
class He {
  constructor(e, t) {
    this.state = j.for2d(), this.renderer = e, this._adaptor = t, this.renderer.runners.contextChange.add(this);
  }
  contextChange() {
    this._adaptor.contextChange(this.renderer);
  }
  validateRenderable(e) {
    const t = e.context, r = !!e._gpuData, s = this.renderer.graphicsContext.updateGpuContext(t);
    return !!(s.isBatchable || r !== s.isBatchable);
  }
  addRenderable(e, t) {
    const r = this.renderer.graphicsContext.updateGpuContext(e.context);
    e.didViewUpdate && this._rebuild(e), r.isBatchable ? this._addToBatcher(e, t) : (this.renderer.renderPipes.batch.break(t), t.add(e));
  }
  updateRenderable(e) {
    const r = this._getGpuDataForRenderable(e).batches;
    for (let s = 0; s < r.length; s++) {
      const i = r[s];
      i._batcher.updateElement(i);
    }
  }
  execute(e) {
    if (!e.isRenderable)
      return;
    const t = this.renderer, r = e.context;
    if (!t.graphicsContext.getGpuContext(r).batches.length)
      return;
    const i = r.customShader || this._adaptor.shader;
    this.state.blendMode = e.groupBlendMode;
    const n = i.resources.localUniforms.uniforms;
    n.uTransformMatrix = e.groupTransform, n.uRound = t._roundPixels | e._roundPixels, $(
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
    const r = this.renderer.renderPipes.batch, s = this._getGpuDataForRenderable(e).batches;
    for (let i = 0; i < s.length; i++) {
      const n = s[i];
      r.addToBatch(n, t);
    }
  }
  _getGpuDataForRenderable(e) {
    return e._gpuData[this.renderer.uid] || this._initGpuDataForRenderable(e);
  }
  _initGpuDataForRenderable(e) {
    const t = new Dt();
    return e._gpuData[this.renderer.uid] = t, t;
  }
  _updateBatchesForRenderable(e, t) {
    const r = e.context, s = this.renderer.graphicsContext.getGpuContext(r), i = this.renderer._roundPixels | e._roundPixels;
    t.batches = s.batches.map((n) => {
      const a = K.get(ht);
      return n.copyTo(a), a.renderable = e, a.roundPixels = i, a;
    });
  }
  destroy() {
    this.renderer = null, this._adaptor.destroy(), this._adaptor = null, this.state = null;
  }
}
He.extension = {
  type: [
    g.WebGLPipes,
    g.WebGPUPipes,
    g.CanvasPipes
  ],
  name: "graphics"
};
const Ve = class Ye extends ue {
  constructor(...e) {
    super({});
    let t = e[0] ?? {};
    typeof t == "number" && (w(U, "PlaneGeometry constructor changed please use { width, height, verticesX, verticesY } instead"), t = {
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
    e = { ...Ye.defaultOptions, ...e }, this.verticesX = this.verticesX ?? e.verticesX, this.verticesY = this.verticesY ?? e.verticesY, this.width = this.width ?? e.width, this.height = this.height ?? e.height;
    const t = this.verticesX * this.verticesY, r = [], s = [], i = [], n = this.verticesX - 1, a = this.verticesY - 1, u = this.width / n, l = this.height / a;
    for (let c = 0; c < t; c++) {
      const h = c % this.verticesX, f = c / this.verticesX | 0;
      r.push(h * u, f * l), s.push(h / n, f / a);
    }
    const d = n * a;
    for (let c = 0; c < d; c++) {
      const h = c % n, f = c / n | 0, y = f * this.verticesX + h, m = f * this.verticesX + h + 1, x = (f + 1) * this.verticesX + h, p = (f + 1) * this.verticesX + h + 1;
      i.push(
        y,
        m,
        x,
        m,
        p,
        x
      );
    }
    this.buffers[0].data = new Float32Array(r), this.buffers[1].data = new Float32Array(s), this.indexBuffer.data = new Uint32Array(i), this.buffers[0].update(), this.buffers[1].update(), this.indexBuffer.update();
  }
};
Ve.defaultOptions = {
  width: 100,
  height: 100,
  verticesX: 10,
  verticesY: 10
};
let Ot = Ve;
class le {
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
    let s = r;
    const i = this.texture.textureMatrix;
    return i.isSimple || (s = this._transformedUvs, (this._textureMatrixUpdateId !== i._updateID || this._uvUpdateId !== t._updateID) && ((!s || s.length < r.length) && (s = this._transformedUvs = new Float32Array(r.length)), this._textureMatrixUpdateId = i._updateID, this._uvUpdateId = t._updateID, i.multiplyUvs(r, s))), s;
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
class ye {
  destroy() {
  }
}
class Xe {
  constructor(e, t) {
    this.localUniforms = new z({
      uTransformMatrix: { value: new R(), type: "mat3x3<f32>" },
      uColor: { value: new Float32Array([1, 1, 1, 1]), type: "vec4<f32>" },
      uRound: { value: 0, type: "f32" }
    }), this.localUniformsBindGroup = new Se({
      0: this.localUniforms
    }), this.renderer = e, this._adaptor = t, this._adaptor.init();
  }
  validateRenderable(e) {
    const t = this._getMeshData(e), r = t.batched, s = e.batched;
    if (t.batched = s, r !== s)
      return !0;
    if (s) {
      const i = e._geometry;
      if (i.indices.length !== t.indexSize || i.positions.length !== t.vertexSize)
        return t.indexSize = i.indices.length, t.vertexSize = i.positions.length, !0;
      const n = this._getBatchableMesh(e);
      return n.texture.uid !== e._texture.uid && (n._textureMatrixUpdateId = -1), !n._batcher.checkAndUpdateTexture(
        n,
        e._texture
      );
    }
    return !1;
  }
  addRenderable(e, t) {
    var i, n;
    const r = this.renderer.renderPipes.batch, s = this._getMeshData(e);
    if (e.didViewUpdate && (s.indexSize = (i = e._geometry.indices) == null ? void 0 : i.length, s.vertexSize = (n = e._geometry.positions) == null ? void 0 : n.length), s.batched) {
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
    e.state.blendMode = ae(e.groupBlendMode, e.texture._source);
    const t = this.localUniforms;
    t.uniforms.uTransformMatrix = e.groupTransform, t.uniforms.uRound = this.renderer._roundPixels | e._roundPixels, t.update(), $(
      e.groupColorAlpha,
      t.uniforms.uColor,
      0
    ), this._adaptor.execute(this, e);
  }
  _getMeshData(e) {
    var t, r;
    return (t = e._gpuData)[r = this.renderer.uid] || (t[r] = new ye()), e._gpuData[this.renderer.uid].meshData || this._initMeshData(e);
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
    return (t = e._gpuData)[r = this.renderer.uid] || (t[r] = new ye()), e._gpuData[this.renderer.uid].batchableMesh || this._initBatchableMesh(e);
  }
  _initBatchableMesh(e) {
    const t = new le();
    return t.renderable = e, t.setTexture(e._texture), t.transform = e.groupTransform, t.roundPixels = this.renderer._roundPixels | e._roundPixels, e._gpuData[this.renderer.uid].batchableMesh = t, t;
  }
  destroy() {
    this.localUniforms = null, this.localUniformsBindGroup = null, this._adaptor.destroy(), this._adaptor = null, this.renderer = null;
  }
}
Xe.extension = {
  type: [
    g.WebGLPipes,
    g.WebGPUPipes,
    g.CanvasPipes
  ],
  name: "mesh"
};
class Wt {
  execute(e, t) {
    const r = e.state, s = e.renderer, i = t.shader || e.defaultShader;
    i.resources.uTexture = t.texture._source, i.resources.uniforms = e.localUniforms;
    const n = s.gl, a = e.getBuffers(t);
    s.shader.bind(i), s.state.set(r), s.geometry.bind(a.geometry, i.glProgram);
    const l = a.geometry.indexBuffer.data.BYTES_PER_ELEMENT === 2 ? n.UNSIGNED_SHORT : n.UNSIGNED_INT;
    n.drawElements(n.TRIANGLES, t.particleChildren.length * 6, l, 0);
  }
}
class It {
  execute(e, t) {
    const r = e.renderer, s = t.shader || e.defaultShader;
    s.groups[0] = r.renderPipes.uniformBatch.getUniformBindGroup(e.localUniforms, !0), s.groups[1] = r.texture.getTextureBindGroup(t.texture);
    const i = e.state, n = e.getBuffers(t);
    r.encoder.draw({
      geometry: n.geometry,
      shader: t.shader || e.defaultShader,
      state: i,
      size: t.particleChildren.length * 6
    });
  }
}
function be(o, e = null) {
  const t = o * 6;
  if (t > 65535 ? e || (e = new Uint32Array(t)) : e || (e = new Uint16Array(t)), e.length !== t)
    throw new Error(`Out buffer length is incorrect, got ${e.length} and expected ${t}`);
  for (let r = 0, s = 0; r < t; r += 6, s += 4)
    e[r + 0] = s + 0, e[r + 1] = s + 1, e[r + 2] = s + 2, e[r + 3] = s + 0, e[r + 4] = s + 2, e[r + 5] = s + 3;
  return e;
}
function Et(o) {
  return {
    dynamicUpdate: ve(o, !0),
    staticUpdate: ve(o, !1)
  };
}
function ve(o, e) {
  const t = [];
  t.push(`

        var index = 0;

        for (let i = 0; i < ps.length; ++i)
        {
            const p = ps[i];

            `);
  let r = 0;
  for (const i in o) {
    const n = o[i];
    if (e !== n.dynamic)
      continue;
    t.push(`offset = index + ${r}`), t.push(n.code);
    const a = te(n.format);
    r += a.stride / 4;
  }
  t.push(`
            index += stride * 4;
        }
    `), t.unshift(`
        var stride = ${r};
    `);
  const s = t.join(`
`);
  return new Function("ps", "f32v", "u32v", s);
}
class Lt {
  constructor(e) {
    this._size = 0, this._generateParticleUpdateCache = {};
    const t = this._size = e.size ?? 1e3, r = e.properties;
    let s = 0, i = 0;
    for (const d in r) {
      const c = r[d], h = te(c.format);
      c.dynamic ? i += h.stride : s += h.stride;
    }
    this._dynamicStride = i / 4, this._staticStride = s / 4, this.staticAttributeBuffer = new L(t * 4 * s), this.dynamicAttributeBuffer = new L(t * 4 * i), this.indexBuffer = be(t);
    const n = new se();
    let a = 0, u = 0;
    this._staticBuffer = new O({
      data: new Float32Array(1),
      label: "static-particle-buffer",
      shrinkToFit: !1,
      usage: B.VERTEX | B.COPY_DST
    }), this._dynamicBuffer = new O({
      data: new Float32Array(1),
      label: "dynamic-particle-buffer",
      shrinkToFit: !1,
      usage: B.VERTEX | B.COPY_DST
    });
    for (const d in r) {
      const c = r[d], h = te(c.format);
      c.dynamic ? (n.addAttribute(c.attributeName, {
        buffer: this._dynamicBuffer,
        stride: this._dynamicStride * 4,
        offset: a * 4,
        format: c.format
      }), a += h.size) : (n.addAttribute(c.attributeName, {
        buffer: this._staticBuffer,
        stride: this._staticStride * 4,
        offset: u * 4,
        format: c.format
      }), u += h.size);
    }
    n.addIndex(this.indexBuffer);
    const l = this.getParticleUpdate(r);
    this._dynamicUpload = l.dynamicUpdate, this._staticUpload = l.staticUpdate, this.geometry = n;
  }
  getParticleUpdate(e) {
    const t = Ht(e);
    return this._generateParticleUpdateCache[t] ? this._generateParticleUpdateCache[t] : (this._generateParticleUpdateCache[t] = this.generateParticleUpdate(e), this._generateParticleUpdateCache[t]);
  }
  generateParticleUpdate(e) {
    return Et(e);
  }
  update(e, t) {
    e.length > this._size && (t = !0, this._size = Math.max(e.length, this._size * 1.5 | 0), this.staticAttributeBuffer = new L(this._size * this._staticStride * 4 * 4), this.dynamicAttributeBuffer = new L(this._size * this._dynamicStride * 4 * 4), this.indexBuffer = be(this._size), this.geometry.indexBuffer.setDataWithSize(
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
      const s = this.staticAttributeBuffer;
      this._staticUpload(e, s.float32View, s.uint32View), this._staticBuffer.setDataWithSize(
        s.float32View,
        e.length * this._staticStride * 4,
        !0
      );
    }
  }
  destroy() {
    this._staticBuffer.destroy(), this._dynamicBuffer.destroy(), this.geometry.destroy();
  }
}
function Ht(o) {
  const e = [];
  for (const t in o) {
    const r = o[t];
    e.push(t, r.code, r.dynamic ? "d" : "s");
  }
  return e.join("_");
}
var Vt = `varying vec2 vUV;
varying vec4 vColor;

uniform sampler2D uTexture;

void main(void){
    vec4 color = texture2D(uTexture, vUV) * vColor;
    gl_FragColor = color;
}`, Yt = `attribute vec2 aVertex;
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
`, Te = `
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
class Xt extends oe {
  constructor() {
    const e = ft.from({
      vertex: Yt,
      fragment: Vt
    }), t = pt.from({
      fragment: {
        source: Te,
        entryPoint: "mainFragment"
      },
      vertex: {
        source: Te,
        entryPoint: "mainVertex"
      }
    });
    super({
      glProgram: e,
      gpuProgram: t,
      resources: {
        // this will be replaced with the texture from the particle container
        uTexture: C.WHITE.source,
        // this will be replaced with the texture style from the particle container
        uSampler: new W({}),
        // this will be replaced with the local uniforms from the particle container
        uniforms: {
          uTranslationMatrix: { value: new R(), type: "mat3x3<f32>" },
          uColor: { value: new Ce(16777215), type: "vec4<f32>" },
          uRound: { value: 1, type: "f32" },
          uResolution: { value: [0, 0], type: "vec2<f32>" }
        }
      }
    });
  }
}
class Ke {
  /**
   * @param renderer - The renderer this sprite batch works for.
   * @param adaptor
   */
  constructor(e, t) {
    this.state = j.for2d(), this.localUniforms = new z({
      uTranslationMatrix: { value: new R(), type: "mat3x3<f32>" },
      uColor: { value: new Float32Array(4), type: "vec4<f32>" },
      uRound: { value: 1, type: "f32" },
      uResolution: { value: [0, 0], type: "vec2<f32>" }
    }), this.renderer = e, this.adaptor = t, this.defaultShader = new Xt(), this.state = j.for2d();
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
    return e._gpuData[this.renderer.uid] = new Lt({
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
    const r = this.renderer, s = this.getBuffers(e);
    e.texture || (e.texture = t[0].texture);
    const i = this.state;
    s.update(t, e._childrenDirty), e._childrenDirty = !1, i.blendMode = ae(e.blendMode, e.texture._source);
    const n = this.localUniforms.uniforms, a = n.uTranslationMatrix;
    e.worldTransform.copyTo(a), a.prepend(r.globalUniforms.globalUniformData.projectionMatrix), n.uResolution = r.globalUniforms.globalUniformData.resolution, n.uRound = r._roundPixels | e._roundPixels, $(
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
class je extends Ke {
  constructor(e) {
    super(e, new Wt());
  }
}
je.extension = {
  type: [
    g.WebGLPipes
  ],
  name: "particle"
};
class $e extends Ke {
  constructor(e) {
    super(e, new It());
  }
}
$e.extension = {
  type: [
    g.WebGPUPipes
  ],
  name: "particle"
};
const Ne = class qe extends Ot {
  constructor(e = {}) {
    e = { ...qe.defaultOptions, ...e }, super({
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
      _leftWidth: s,
      _rightWidth: i,
      _topHeight: n,
      _bottomHeight: a,
      _anchorX: u,
      _anchorY: l
    } = this, d = s + i, c = t > d ? 1 : t / d, h = n + a, f = r > h ? 1 : r / h, y = Math.min(c, f), m = u * t, x = l * r;
    e[0] = e[8] = e[16] = e[24] = -m, e[2] = e[10] = e[18] = e[26] = s * y - m, e[4] = e[12] = e[20] = e[28] = t - i * y - m, e[6] = e[14] = e[22] = e[30] = t - m, e[1] = e[3] = e[5] = e[7] = -x, e[9] = e[11] = e[13] = e[15] = n * y - x, e[17] = e[19] = e[21] = e[23] = r - a * y - x, e[25] = e[27] = e[29] = e[31] = r - x, this.getBuffer("aPosition").update();
  }
  /** Updates the UVs of the vertices. */
  updateUvs() {
    const e = this.uvs;
    e[0] = e[8] = e[16] = e[24] = 0, e[1] = e[3] = e[5] = e[7] = 0, e[6] = e[14] = e[22] = e[30] = 1, e[25] = e[27] = e[29] = e[31] = 1;
    const t = 1 / this._originalWidth, r = 1 / this._originalHeight;
    e[2] = e[10] = e[18] = e[26] = t * this._leftWidth, e[9] = e[11] = e[13] = e[15] = r * this._topHeight, e[4] = e[12] = e[20] = e[28] = 1 - t * this._rightWidth, e[17] = e[19] = e[21] = e[23] = 1 - r * this._bottomHeight, this.getBuffer("aUV").update();
  }
};
Ne.defaultOptions = {
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
let Kt = Ne;
class jt extends le {
  constructor() {
    super(), this.geometry = new Kt();
  }
  destroy() {
    this.geometry.destroy();
  }
}
class Qe {
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
    const t = e._gpuData[this._renderer.uid] = new jt(), r = t;
    return r.renderable = e, r.transform = e.groupTransform, r.texture = e._texture, r.roundPixels = this._renderer._roundPixels | e._roundPixels, e.didViewUpdate || this._updateBatchableSprite(e, r), t;
  }
  destroy() {
    this._renderer = null;
  }
}
Qe.extension = {
  type: [
    g.WebGLPipes,
    g.WebGPUPipes,
    g.CanvasPipes
  ],
  name: "nineSliceSprite"
};
const $t = {
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
}, Nt = {
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
let q, Q;
class qt extends oe {
  constructor() {
    q ?? (q = Fe({
      name: "tiling-sprite-shader",
      bits: [
        wt,
        $t,
        Be
      ]
    })), Q ?? (Q = Re({
      name: "tiling-sprite-shader",
      bits: [
        Ct,
        Nt,
        Me
      ]
    }));
    const e = new z({
      uMapCoord: { value: new R(), type: "mat3x3<f32>" },
      uClampFrame: { value: new Float32Array([0, 0, 1, 1]), type: "vec4<f32>" },
      uClampOffset: { value: new Float32Array([0, 0]), type: "vec2<f32>" },
      uTextureTransform: { value: new R(), type: "mat3x3<f32>" },
      uSizeAnchor: { value: new Float32Array([100, 100, 0.5, 0.5]), type: "vec4<f32>" }
    });
    super({
      glProgram: Q,
      gpuProgram: q,
      resources: {
        localUniforms: new z({
          uTransformMatrix: { value: new R(), type: "mat3x3<f32>" },
          uColor: { value: new Float32Array([1, 1, 1, 1]), type: "vec4<f32>" },
          uRound: { value: 0, type: "f32" }
        }),
        tilingUniforms: e,
        uTexture: C.EMPTY.source,
        uSampler: C.EMPTY.source.style
      }
    });
  }
  updateUniforms(e, t, r, s, i, n) {
    const a = this.resources.tilingUniforms, u = n.width, l = n.height, d = n.textureMatrix, c = a.uniforms.uTextureTransform;
    c.set(
      r.a * u / e,
      r.b * u / t,
      r.c * l / e,
      r.d * l / t,
      r.tx / e,
      r.ty / t
    ), c.invert(), a.uniforms.uMapCoord = d.mapCoord, a.uniforms.uClampFrame = d.uClampFrame, a.uniforms.uClampOffset = d.uClampOffset, a.uniforms.uTextureTransform = c, a.uniforms.uSizeAnchor[0] = e, a.uniforms.uSizeAnchor[1] = t, a.uniforms.uSizeAnchor[2] = s, a.uniforms.uSizeAnchor[3] = i, n && (this.resources.uTexture = n.source, this.resources.uSampler = n.source.style);
  }
}
class Qt extends ue {
  constructor() {
    super({
      positions: new Float32Array([0, 0, 1, 0, 1, 1, 0, 1]),
      uvs: new Float32Array([0, 0, 1, 0, 1, 1, 0, 1]),
      indices: new Uint32Array([0, 1, 2, 0, 2, 3])
    });
  }
}
function Jt(o, e) {
  const t = o.anchor.x, r = o.anchor.y;
  e[0] = -t * o.width, e[1] = -r * o.height, e[2] = (1 - t) * o.width, e[3] = -r * o.height, e[4] = (1 - t) * o.width, e[5] = (1 - r) * o.height, e[6] = -t * o.width, e[7] = (1 - r) * o.height;
}
function Zt(o, e, t, r) {
  let s = 0;
  const i = o.length / e, n = r.a, a = r.b, u = r.c, l = r.d, d = r.tx, c = r.ty;
  for (t *= e; s < i; ) {
    const h = o[t], f = o[t + 1];
    o[t] = n * h + u * f + d, o[t + 1] = a * h + l * f + c, t += e, s++;
  }
}
function er(o, e) {
  const t = o.texture, r = t.frame.width, s = t.frame.height;
  let i = 0, n = 0;
  o.applyAnchorToTexture && (i = o.anchor.x, n = o.anchor.y), e[0] = e[6] = -i, e[2] = e[4] = 1 - i, e[1] = e[3] = -n, e[5] = e[7] = 1 - n;
  const a = R.shared;
  a.copyFrom(o._tileTransform.matrix), a.tx /= o.width, a.ty /= o.height, a.invert(), a.scale(o.width / r, o.height / s), Zt(e, 2, 0, a);
}
const V = new Qt();
class tr {
  constructor() {
    this.canBatch = !0, this.geometry = new ue({
      indices: V.indices.slice(),
      positions: V.positions.slice(),
      uvs: V.uvs.slice()
    });
  }
  destroy() {
    var e;
    this.geometry.destroy(), (e = this.shader) == null || e.destroy();
  }
}
class Je {
  constructor(e) {
    this._state = j.default2d, this._renderer = e;
  }
  validateRenderable(e) {
    const t = this._getTilingSpriteData(e), r = t.canBatch;
    this._updateCanBatch(e);
    const s = t.canBatch;
    if (s && s === r) {
      const { batchableMesh: i } = t;
      return !i._batcher.checkAndUpdateTexture(
        i,
        e.texture
      );
    }
    return r !== s;
  }
  addRenderable(e, t) {
    const r = this._renderer.renderPipes.batch;
    this._updateCanBatch(e);
    const s = this._getTilingSpriteData(e), { geometry: i, canBatch: n } = s;
    if (n) {
      s.batchableMesh || (s.batchableMesh = new le());
      const a = s.batchableMesh;
      e.didViewUpdate && (this._updateBatchableMesh(e), a.geometry = i, a.renderable = e, a.transform = e.groupTransform, a.setTexture(e._texture)), a.roundPixels = this._renderer._roundPixels | e._roundPixels, r.addToBatch(a, t);
    } else
      r.break(t), s.shader || (s.shader = new qt()), this.updateRenderable(e), t.add(e);
  }
  execute(e) {
    const { shader: t } = this._getTilingSpriteData(e);
    t.groups[0] = this._renderer.globalUniforms.bindGroup;
    const r = t.resources.localUniforms.uniforms;
    r.uTransformMatrix = e.groupTransform, r.uRound = this._renderer._roundPixels | e._roundPixels, $(
      e.groupColorAlpha,
      r.uColor,
      0
    ), this._state.blendMode = ae(e.groupBlendMode, e.texture._source), this._renderer.encoder.draw({
      geometry: V,
      shader: t,
      state: this._state
    });
  }
  updateRenderable(e) {
    const t = this._getTilingSpriteData(e), { canBatch: r } = t;
    if (r) {
      const { batchableMesh: s } = t;
      e.didViewUpdate && this._updateBatchableMesh(e), s._batcher.updateElement(s);
    } else if (e.didViewUpdate) {
      const { shader: s } = t;
      s.updateUniforms(
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
    const t = new tr();
    return t.renderable = e, e._gpuData[this._renderer.uid] = t, t;
  }
  _updateBatchableMesh(e) {
    const t = this._getTilingSpriteData(e), { geometry: r } = t, s = e.texture.source.style;
    s.addressMode !== "repeat" && (s.addressMode = "repeat", s.update()), er(e, r.uvs), Jt(e, r.positions);
  }
  destroy() {
    this._renderer = null;
  }
  _updateCanBatch(e) {
    const t = this._getTilingSpriteData(e), r = e.texture;
    let s = !0;
    return this._renderer.type === ie.WEBGL && (s = this._renderer.context.supports.nonPowOf2wrapping), t.canBatch = r.textureMatrix.isSimple && (s || r.source.isPowerOfTwo), t.canBatch;
  }
}
Je.extension = {
  type: [
    g.WebGLPipes,
    g.WebGPUPipes,
    g.CanvasPipes
  ],
  name: "tilingSprite"
};
const rr = {
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
}, sr = {
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
}, ir = {
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
}, nr = {
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
let J, Z;
class ar extends oe {
  constructor(e) {
    const t = new z({
      uColor: { value: new Float32Array([1, 1, 1, 1]), type: "vec4<f32>" },
      uTransformMatrix: { value: new R(), type: "mat3x3<f32>" },
      uDistance: { value: 4, type: "f32" },
      uRound: { value: 0, type: "f32" }
    });
    J ?? (J = Fe({
      name: "sdf-shader",
      bits: [
        gt,
        mt(e),
        rr,
        ir,
        Be
      ]
    })), Z ?? (Z = Re({
      name: "sdf-shader",
      bits: [
        xt,
        _t(e),
        sr,
        nr,
        Me
      ]
    })), super({
      glProgram: Z,
      gpuProgram: J,
      resources: {
        localUniforms: t,
        batchSamplers: yt(e)
      }
    });
  }
}
class or extends bt {
  destroy() {
    this.context.customShader && this.context.customShader.destroy(), super.destroy();
  }
}
class Ze {
  constructor(e) {
    this._renderer = e;
  }
  validateRenderable(e) {
    const t = this._getGpuBitmapText(e);
    return this._renderer.renderPipes.graphics.validateRenderable(t);
  }
  addRenderable(e, t) {
    const r = this._getGpuBitmapText(e);
    we(e, r), e._didTextUpdate && (e._didTextUpdate = !1, this._updateContext(e, r)), this._renderer.renderPipes.graphics.addRenderable(r, t), r.context.customShader && this._updateDistanceField(e);
  }
  updateRenderable(e) {
    const t = this._getGpuBitmapText(e);
    we(e, t), this._renderer.renderPipes.graphics.updateRenderable(t), t.context.customShader && this._updateDistanceField(e);
  }
  _updateContext(e, t) {
    const { context: r } = t, s = Ut.getFont(e.text, e._style);
    r.clear(), s.distanceField.type !== "none" && (r.customShader || (r.customShader = new ar(this._renderer.limits.maxBatchableTextures)));
    const i = D.graphemeSegmenter(e.text), n = e._style;
    let a = s.baseLineOffset;
    const u = De(i, n, s, !0), l = n.padding, d = u.scale;
    let c = u.width, h = u.height + u.offsetY;
    n._stroke && (c += n._stroke.width / d, h += n._stroke.width / d), r.translate(-e._anchor._x * c - l, -e._anchor._y * h - l).scale(d, d);
    const f = s.applyFillAsTint ? n._fill.color : 16777215;
    let y = s.fontMetrics.fontSize, m = s.lineHeight;
    n.lineHeight && (y = n.fontSize / d, m = n.lineHeight / d);
    let x = (m - y) / 2;
    x - s.baseLineOffset < 0 && (x = 0);
    for (let p = 0; p < u.lines.length; p++) {
      const _ = u.lines[p];
      for (let b = 0; b < _.charPositions.length; b++) {
        const v = _.chars[b], S = s.chars[v];
        if (S != null && S.texture) {
          const G = S.texture;
          r.texture(
            G,
            f || "black",
            Math.round(_.charPositions[b] + S.xOffset),
            Math.round(a + S.yOffset + x),
            G.orig.width,
            G.orig.height
          );
        }
      }
      a += m;
    }
  }
  _getGpuBitmapText(e) {
    return e._gpuData[this._renderer.uid] || this.initGpuText(e);
  }
  initGpuText(e) {
    const t = new or();
    return e._gpuData[this._renderer.uid] = t, this._updateContext(e, t), t;
  }
  _updateDistanceField(e) {
    const t = this._getGpuBitmapText(e).context, r = e._style.fontFamily, s = P.get(`${r}-bitmap`), { a: i, b: n, c: a, d: u } = e.groupTransform, l = Math.sqrt(i * i + n * n), d = Math.sqrt(a * a + u * u), c = (Math.abs(l) + Math.abs(d)) / 2, h = s.baseRenderedFontSize / e._style.fontSize, f = c * s.distanceField.range * (1 / h);
    t.customShader.resources.localUniforms.uniforms.uDistance = f;
  }
  destroy() {
    this._renderer = null;
  }
}
Ze.extension = {
  type: [
    g.WebGLPipes,
    g.WebGPUPipes,
    g.CanvasPipes
  ],
  name: "bitmapText"
};
function we(o, e) {
  e.groupTransform = o.groupTransform, e.groupColorAlpha = o.groupColorAlpha, e.groupColor = o.groupColor, e.groupBlendMode = o.groupBlendMode, e.globalDisplayStatus = o.globalDisplayStatus, e.groupTransform = o.groupTransform, e.localDisplayStatus = o.localDisplayStatus, e.groupAlpha = o.groupAlpha, e._roundPixels = o._roundPixels;
}
class ur extends Ue {
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
function re(o, e) {
  const { texture: t, bounds: r } = o, s = e._style._getFinalPadding();
  vt(r, e._anchor, t);
  const i = e._anchor._x * s * 2, n = e._anchor._y * s * 2;
  r.minX -= s - i, r.minY -= s - n, r.maxX -= s - i, r.maxY -= s - n;
}
class et {
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
      const s = e._autoResolution ? this._renderer.resolution : e.resolution;
      (r.currentKey !== e.styleKey || e.resolution !== s) && this._updateGpuText(e).catch((i) => {
        console.error(i);
      }), e._didTextUpdate = !1, re(r, e);
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
    let s = this._renderer.htmlText.getTexturePromise(e);
    r && (s = s.finally(() => {
      this._renderer.htmlText.decreaseReferenceCount(t.currentKey), this._renderer.htmlText.returnTexturePromise(r);
    })), t.texturePromise = s, t.currentKey = e.styleKey, t.texture = await s;
    const i = e.renderGroup || e.parentRenderGroup;
    i && (i.structureDidChange = !0), t.generatingTexture = !1, re(t, e);
  }
  _getGpuText(e) {
    return e._gpuData[this._renderer.uid] || this.initGpuText(e);
  }
  initGpuText(e) {
    const t = new ur(this._renderer);
    return t.renderable = e, t.transform = e.groupTransform, t.texture = C.EMPTY, t.bounds = { minX: 0, maxX: 1, minY: 0, maxY: 0 }, t.roundPixels = this._renderer._roundPixels | e._roundPixels, e._resolution = e._autoResolution ? this._renderer.resolution : e.resolution, e._gpuData[this._renderer.uid] = t, t;
  }
  destroy() {
    this._renderer = null;
  }
}
et.extension = {
  type: [
    g.WebGLPipes,
    g.WebGPUPipes,
    g.CanvasPipes
  ],
  name: "htmlText"
};
function lr() {
  const { userAgent: o } = ne.get().getNavigator();
  return /^((?!chrome|android).)*safari/i.test(o);
}
const cr = new Pe();
function tt(o, e, t, r) {
  const s = cr;
  s.minX = 0, s.minY = 0, s.maxX = o.width / r | 0, s.maxY = o.height / r | 0;
  const i = F.getOptimalTexture(
    s.width,
    s.height,
    r,
    !1
  );
  return i.source.uploadMethodId = "image", i.source.resource = o, i.source.alphaMode = "premultiply-alpha-on-upload", i.frame.width = e / r, i.frame.height = t / r, i.source.emit("update", i.source), i.updateUvs(), i;
}
function dr(o, e) {
  const t = e.fontFamily, r = [], s = {}, i = /font-family:([^;"\s]+)/g, n = o.match(i);
  function a(u) {
    s[u] || (r.push(u), s[u] = !0);
  }
  if (Array.isArray(t))
    for (let u = 0; u < t.length; u++)
      a(t[u]);
  else
    a(t);
  n && n.forEach((u) => {
    const l = u.split(":")[1].trim();
    a(l);
  });
  for (const u in e.tagStyles) {
    const l = e.tagStyles[u].fontFamily;
    a(l);
  }
  return r;
}
async function hr(o) {
  const t = await (await ne.get().fetch(o)).blob(), r = new FileReader();
  return await new Promise((i, n) => {
    r.onloadend = () => i(r.result), r.onerror = n, r.readAsDataURL(t);
  });
}
async function fr(o, e) {
  const t = await hr(e);
  return `@font-face {
        font-family: "${o.fontFamily}";
        font-weight: ${o.fontWeight};
        font-style: ${o.fontStyle};
        src: url('${t}');
    }`;
}
const ee = /* @__PURE__ */ new Map();
async function pr(o) {
  const e = o.filter((t) => P.has(`${t}-and-url`)).map((t) => {
    if (!ee.has(t)) {
      const { entries: r } = P.get(`${t}-and-url`), s = [];
      r.forEach((i) => {
        const n = i.url, u = i.faces.map((l) => ({ weight: l.weight, style: l.style }));
        s.push(
          ...u.map(
            (l) => fr(
              {
                fontWeight: l.weight,
                fontStyle: l.style,
                fontFamily: t
              },
              n
            )
          )
        );
      }), ee.set(
        t,
        Promise.all(s).then((i) => i.join(`
`))
      );
    }
    return ee.get(t);
  });
  return (await Promise.all(e)).join(`
`);
}
function gr(o, e, t, r, s) {
  const { domElement: i, styleElement: n, svgRoot: a } = s;
  i.innerHTML = `<style>${e.cssStyle}</style><div style='padding:0;'>${o}</div>`, i.setAttribute("style", `transform: scale(${t});transform-origin: top left; display: inline-block`), n.textContent = r;
  const { width: u, height: l } = s.image;
  return a.setAttribute("width", u.toString()), a.setAttribute("height", l.toString()), new XMLSerializer().serializeToString(a);
}
function mr(o, e) {
  const t = Y.getOptimalCanvasAndContext(
    o.width,
    o.height,
    e
  ), { context: r } = t;
  return r.clearRect(0, 0, o.width, o.height), r.drawImage(o, 0, 0), t;
}
function xr(o, e, t) {
  return new Promise(async (r) => {
    t && await new Promise((s) => setTimeout(s, 100)), o.onload = () => {
      r();
    }, o.src = `data:image/svg+xml;charset=utf8,${encodeURIComponent(e)}`, o.crossOrigin = "anonymous";
  });
}
class rt {
  constructor(e) {
    this._activeTextures = {}, this._renderer = e, this._createCanvas = e.type === ie.WEBGPU;
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
    const r = this._buildTexturePromise(e).then((s) => (this._activeTextures[t].texture = s, s));
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
      X("HTMLTextSystem: Failed to clean texture");
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
    const { text: t, style: r, resolution: s, textureStyle: i } = e, n = K.get(Le), a = dr(t, r), u = await pr(a), l = kt(t, r, u, n), d = Math.ceil(Math.ceil(Math.max(1, l.width) + r.padding * 2) * s), c = Math.ceil(Math.ceil(Math.max(1, l.height) + r.padding * 2) * s), h = n.image, f = 2;
    h.width = (d | 0) + f, h.height = (c | 0) + f;
    const y = gr(t, r, s, u, n);
    await xr(h, y, lr() && a.length > 0);
    const m = h;
    let x;
    this._createCanvas && (x = mr(h, s));
    const p = tt(
      x ? x.canvas : m,
      h.width - f,
      h.height - f,
      s
    );
    return i && (p.source.style = i), this._createCanvas && (this._renderer.texture.initSource(p.source), Y.returnCanvasAndContext(x)), K.return(n), p;
  }
  returnTexturePromise(e) {
    e.then((t) => {
      this._cleanUp(t);
    }).catch(() => {
      X("HTMLTextSystem: Failed to clean texture");
    });
  }
  _cleanUp(e) {
    F.returnTexture(e, !0), e.source.resource = null, e.source.uploadMethodId = "unknown";
  }
  destroy() {
    this._renderer = null;
    for (const e in this._activeTextures)
      this._activeTextures[e] && this.returnTexturePromise(this._activeTextures[e].promise);
    this._activeTextures = null;
  }
}
rt.extension = {
  type: [
    g.WebGLSystem,
    g.WebGPUSystem,
    g.CanvasSystem
  ],
  name: "htmlText"
};
class _r extends Ue {
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
class st {
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
      const s = e._autoResolution ? this._renderer.resolution : e.resolution;
      (r.currentKey !== e.styleKey || e.resolution !== s) && this._updateGpuText(e), e._didTextUpdate = !1;
    }
    this._renderer.renderPipes.batch.addToBatch(r, t);
  }
  updateRenderable(e) {
    const t = this._getGpuText(e);
    t._batcher.updateElement(t);
  }
  _updateGpuText(e) {
    const t = this._getGpuText(e);
    t.texture && this._renderer.canvasText.decreaseReferenceCount(t.currentKey), e._resolution = e._autoResolution ? this._renderer.resolution : e.resolution, t.texture = this._renderer.canvasText.getManagedTexture(e), t.currentKey = e.styleKey, re(t, e);
  }
  _getGpuText(e) {
    return e._gpuData[this._renderer.uid] || this.initGpuText(e);
  }
  initGpuText(e) {
    const t = new _r(this._renderer);
    return t.currentKey = "--", t.renderable = e, t.transform = e.groupTransform, t.bounds = { minX: 0, maxX: 1, minY: 0, maxY: 0 }, t.roundPixels = this._renderer._roundPixels | e._roundPixels, e._gpuData[this._renderer.uid] = t, t;
  }
  destroy() {
    this._renderer = null;
  }
}
st.extension = {
  type: [
    g.WebGLPipes,
    g.WebGPUPipes,
    g.CanvasPipes
  ],
  name: "text"
};
class it {
  constructor(e) {
    this._activeTextures = {}, this._renderer = e;
  }
  getTexture(e, t, r, s) {
    typeof e == "string" && (w("8.0.0", "CanvasTextSystem.getTexture: Use object TextOptions instead of separate arguments"), e = {
      text: e,
      style: r,
      resolution: t
    }), e.style instanceof I || (e.style = new I(e.style)), e.textureStyle instanceof W || (e.textureStyle = new W(e.textureStyle)), typeof e.text != "string" && (e.text = e.text.toString());
    const { text: i, style: n, textureStyle: a } = e, u = e.resolution ?? this._renderer.resolution, { frame: l, canvasAndContext: d } = N.getCanvasAndContext({
      text: i,
      style: n,
      resolution: u
    }), c = tt(d.canvas, l.width, l.height, u);
    if (a && (c.source.style = a), n.trim && (l.pad(n.padding), c.frame.copyFrom(l), c.frame.scale(1 / u), c.updateUvs()), n.filters) {
      const h = this._applyFilters(c, n.filters);
      return this.returnTexture(c), N.returnCanvasAndContext(d), h;
    }
    return this._renderer.texture.initSource(c._source), N.returnCanvasAndContext(d), c;
  }
  /**
   * Returns a texture that was created wit the above `getTexture` function.
   * Handy if you are done with a texture and want to return it to the pool.
   * @param texture - The texture to be returned.
   */
  returnTexture(e) {
    const t = e.source;
    t.resource = null, t.uploadMethodId = "unknown", t.alphaMode = "no-premultiply-alpha", F.returnTexture(e, !0);
  }
  /**
   * Renders text to its canvas, and updates its texture.
   * @deprecated since 8.10.0
   */
  renderTextToCanvas() {
    w(
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
    const r = this._renderer.renderTarget.renderTarget, s = this._renderer.filter.generateFilteredTexture({
      texture: e,
      filters: t
    });
    return this._renderer.renderTarget.bind(r, !1), s;
  }
  destroy() {
    this._renderer = null;
    for (const e in this._activeTextures)
      this._activeTextures[e] && this.returnTexture(this._activeTextures[e].texture);
    this._activeTextures = null;
  }
}
it.extension = {
  type: [
    g.WebGLSystem,
    g.WebGPUSystem,
    g.CanvasSystem
  ],
  name: "canvasText"
};
T.add(Ge);
T.add(Ae);
T.add(He);
T.add(Tt);
T.add(Xe);
T.add(je);
T.add($e);
T.add(it);
T.add(st);
T.add(Ze);
T.add(rt);
T.add(et);
T.add(Je);
T.add(Qe);
T.add(We);
T.add(Oe);
