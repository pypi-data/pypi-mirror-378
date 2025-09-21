import { D as n, n as c, G as r } from "./Index-Ct_1BCRd.js";
class l {
  constructor(a) {
    this._canvasPool = /* @__PURE__ */ Object.create(null), this.canvasOptions = a || {}, this.enableFullScreen = !1;
  }
  /**
   * Creates texture with params that were specified in pool constructor.
   * @param pixelWidth - Width of texture in pixels.
   * @param pixelHeight - Height of texture in pixels.
   */
  _createCanvasAndContext(a, s) {
    const t = n.get().createCanvas();
    t.width = a, t.height = s;
    const e = t.getContext("2d");
    return { canvas: t, context: e };
  }
  /**
   * Gets a Power-of-Two render texture or fullScreen texture
   * @param minWidth - The minimum width of the render texture.
   * @param minHeight - The minimum height of the render texture.
   * @param resolution - The resolution of the render texture.
   * @returns The new render texture.
   */
  getOptimalCanvasAndContext(a, s, t = 1) {
    a = Math.ceil(a * t - 1e-6), s = Math.ceil(s * t - 1e-6), a = c(a), s = c(s);
    const e = (a << 17) + (s << 1);
    this._canvasPool[e] || (this._canvasPool[e] = []);
    let o = this._canvasPool[e].pop();
    return o || (o = this._createCanvasAndContext(a, s)), o;
  }
  /**
   * Place a render texture back into the pool.
   * @param canvasAndContext
   */
  returnCanvasAndContext(a) {
    const s = a.canvas, { width: t, height: e } = s, o = (t << 17) + (e << 1);
    a.context.resetTransform(), a.context.clearRect(0, 0, t, e), this._canvasPool[o].push(a);
  }
  clear() {
    this._canvasPool = {};
  }
}
const v = new l();
r.register(v);
export {
  v as C
};
