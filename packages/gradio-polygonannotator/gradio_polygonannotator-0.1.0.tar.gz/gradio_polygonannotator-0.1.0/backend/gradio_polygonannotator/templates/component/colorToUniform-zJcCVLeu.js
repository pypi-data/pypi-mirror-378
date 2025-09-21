const f = {
  normal: 0,
  add: 1,
  multiply: 2,
  screen: 3,
  overlay: 4,
  erase: 5,
  "normal-npm": 6,
  "add-npm": 7,
  "screen-npm": 8,
  min: 9,
  max: 10
}, n = 0, i = 1, r = 2, a = 3, l = 4, d = 5, h = class u {
  constructor() {
    this.data = 0, this.blendMode = "normal", this.polygonOffset = 0, this.blend = !0, this.depthMask = !0;
  }
  /**
   * Activates blending of the computed fragment color values.
   * @default true
   */
  get blend() {
    return !!(this.data & 1 << n);
  }
  set blend(t) {
    !!(this.data & 1 << n) !== t && (this.data ^= 1 << n);
  }
  /**
   * Activates adding an offset to depth values of polygon's fragments
   * @default false
   */
  get offsets() {
    return !!(this.data & 1 << i);
  }
  set offsets(t) {
    !!(this.data & 1 << i) !== t && (this.data ^= 1 << i);
  }
  /** The culling settings for this state none - No culling back - Back face culling front - Front face culling */
  set cullMode(t) {
    if (t === "none") {
      this.culling = !1;
      return;
    }
    this.culling = !0, this.clockwiseFrontFace = t === "front";
  }
  get cullMode() {
    return this.culling ? this.clockwiseFrontFace ? "front" : "back" : "none";
  }
  /**
   * Activates culling of polygons.
   * @default false
   */
  get culling() {
    return !!(this.data & 1 << r);
  }
  set culling(t) {
    !!(this.data & 1 << r) !== t && (this.data ^= 1 << r);
  }
  /**
   * Activates depth comparisons and updates to the depth buffer.
   * @default false
   */
  get depthTest() {
    return !!(this.data & 1 << a);
  }
  set depthTest(t) {
    !!(this.data & 1 << a) !== t && (this.data ^= 1 << a);
  }
  /**
   * Enables or disables writing to the depth buffer.
   * @default true
   */
  get depthMask() {
    return !!(this.data & 1 << d);
  }
  set depthMask(t) {
    !!(this.data & 1 << d) !== t && (this.data ^= 1 << d);
  }
  /**
   * Specifies whether or not front or back-facing polygons can be culled.
   * @default false
   */
  get clockwiseFrontFace() {
    return !!(this.data & 1 << l);
  }
  set clockwiseFrontFace(t) {
    !!(this.data & 1 << l) !== t && (this.data ^= 1 << l);
  }
  /**
   * The blend mode to be applied when this state is set. Apply a value of `normal` to reset the blend mode.
   * Setting this mode to anything other than NO_BLEND will automatically switch blending on.
   * @default 'normal'
   */
  get blendMode() {
    return this._blendMode;
  }
  set blendMode(t) {
    this.blend = t !== "none", this._blendMode = t, this._blendModeId = f[t] || 0;
  }
  /**
   * The polygon offset. Setting this property to anything other than 0 will automatically enable polygon offset fill.
   * @default 0
   */
  get polygonOffset() {
    return this._polygonOffset;
  }
  set polygonOffset(t) {
    this.offsets = !!t, this._polygonOffset = t;
  }
  toString() {
    return `[pixi.js/core:State blendMode=${this.blendMode} clockwiseFrontFace=${this.clockwiseFrontFace} culling=${this.culling} depthMask=${this.depthMask} polygonOffset=${this.polygonOffset}]`;
  }
  /**
   * A quickly getting an instance of a State that is configured for 2d rendering.
   * @returns a new State with values set for 2d rendering
   */
  static for2d() {
    const t = new u();
    return t.depthTest = !1, t.blend = !0, t;
  }
};
h.default2d = h.for2d();
let m = h;
const c = {
  name: "local-uniform-bit",
  vertex: {
    header: (
      /* wgsl */
      `

            struct LocalUniforms {
                uTransformMatrix:mat3x3<f32>,
                uColor:vec4<f32>,
                uRound:f32,
            }

            @group(1) @binding(0) var<uniform> localUniforms : LocalUniforms;
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
  }
}, g = {
  ...c,
  vertex: {
    ...c.vertex,
    // replace the group!
    header: c.vertex.header.replace("group(1)", "group(2)")
  }
}, p = {
  name: "local-uniform-bit",
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
            modelMatrix = uTransformMatrix;
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
  }
};
class b {
  constructor() {
    this.batcherName = "default", this.topology = "triangle-list", this.attributeSize = 4, this.indexSize = 6, this.packAsQuad = !0, this.roundPixels = 0, this._attributeStart = 0, this._batcher = null, this._batch = null;
  }
  get blendMode() {
    return this.renderable.groupBlendMode;
  }
  get color() {
    return this.renderable.groupColorAlpha;
  }
  reset() {
    this.renderable = null, this.texture = null, this._batcher = null, this._batch = null, this.bounds = null;
  }
  destroy() {
  }
}
function M(e, t, o) {
  const s = (e >> 24 & 255) / 255;
  t[o++] = (e & 255) / 255 * s, t[o++] = (e >> 8 & 255) / 255 * s, t[o++] = (e >> 16 & 255) / 255 * s, t[o++] = s;
}
export {
  b as B,
  m as S,
  c as a,
  p as b,
  M as c,
  g as l
};
