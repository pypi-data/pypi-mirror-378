const {
  SvelteComponent: q,
  append_hydration: u,
  attr: c,
  children: I,
  claim_element: h,
  claim_space: D,
  claim_text: _,
  detach: g,
  element: m,
  empty: v,
  init: V,
  insert_hydration: p,
  noop: y,
  safe_not_equal: C,
  set_data: b,
  space: G,
  src_url_equal: k,
  text: d,
  toggle_class: r
} = window.__gradio__svelte__internal;
function w(a) {
  let e, l, o, s, t = (
    /*value*/
    a[0].polygons && /*value*/
    a[0].polygons.length > 0 && E(a)
  );
  return {
    c() {
      e = m("div"), l = m("img"), s = G(), t && t.c(), this.h();
    },
    l(n) {
      e = h(n, "DIV", { class: !0 });
      var i = I(e);
      l = h(i, "IMG", { src: !0, alt: !0, class: !0 }), s = D(i), t && t.l(i), i.forEach(g), this.h();
    },
    h() {
      k(l.src, o = /*value*/
      a[0].image.url || /*value*/
      a[0].image.path) || c(l, "src", o), c(l, "alt", ""), c(l, "class", "svelte-84dw5"), c(e, "class", "container svelte-84dw5"), r(
        e,
        "table",
        /*type*/
        a[1] === "table"
      ), r(
        e,
        "gallery",
        /*type*/
        a[1] === "gallery"
      ), r(
        e,
        "selected",
        /*selected*/
        a[2]
      );
    },
    m(n, i) {
      p(n, e, i), u(e, l), u(e, s), t && t.m(e, null);
    },
    p(n, i) {
      i & /*value*/
      1 && !k(l.src, o = /*value*/
      n[0].image.url || /*value*/
      n[0].image.path) && c(l, "src", o), /*value*/
      n[0].polygons && /*value*/
      n[0].polygons.length > 0 ? t ? t.p(n, i) : (t = E(n), t.c(), t.m(e, null)) : t && (t.d(1), t = null), i & /*type*/
      2 && r(
        e,
        "table",
        /*type*/
        n[1] === "table"
      ), i & /*type*/
      2 && r(
        e,
        "gallery",
        /*type*/
        n[1] === "gallery"
      ), i & /*selected*/
      4 && r(
        e,
        "selected",
        /*selected*/
        n[2]
      );
    },
    d(n) {
      n && g(e), t && t.d();
    }
  };
}
function E(a) {
  let e, l = (
    /*value*/
    a[0].polygons.length + ""
  ), o, s, t = (
    /*value*/
    a[0].polygons.length !== 1 ? "s" : ""
  ), n;
  return {
    c() {
      e = m("div"), o = d(l), s = d(" polygon"), n = d(t), this.h();
    },
    l(i) {
      e = h(i, "DIV", { class: !0 });
      var f = I(e);
      o = _(f, l), s = _(f, " polygon"), n = _(f, t), f.forEach(g), this.h();
    },
    h() {
      c(e, "class", "polygon-count svelte-84dw5");
    },
    m(i, f) {
      p(i, e, f), u(e, o), u(e, s), u(e, n);
    },
    p(i, f) {
      f & /*value*/
      1 && l !== (l = /*value*/
      i[0].polygons.length + "") && b(o, l), f & /*value*/
      1 && t !== (t = /*value*/
      i[0].polygons.length !== 1 ? "s" : "") && b(n, t);
    },
    d(i) {
      i && g(e);
    }
  };
}
function M(a) {
  var o;
  let e, l = (
    /*value*/
    ((o = a[0]) == null ? void 0 : o.image) && w(a)
  );
  return {
    c() {
      l && l.c(), e = v();
    },
    l(s) {
      l && l.l(s), e = v();
    },
    m(s, t) {
      l && l.m(s, t), p(s, e, t);
    },
    p(s, [t]) {
      var n;
      /*value*/
      (n = s[0]) != null && n.image ? l ? l.p(s, t) : (l = w(s), l.c(), l.m(e.parentNode, e)) : l && (l.d(1), l = null);
    },
    i: y,
    o: y,
    d(s) {
      s && g(e), l && l.d(s);
    }
  };
}
function N(a, e, l) {
  let { value: o } = e, { type: s } = e, { selected: t = !1 } = e;
  const n = 0;
  return a.$$set = (i) => {
    "value" in i && l(0, o = i.value), "type" in i && l(1, s = i.type), "selected" in i && l(2, t = i.selected);
  }, [o, s, t, n];
}
class S extends q {
  constructor(e) {
    super(), V(this, e, N, M, C, { value: 0, type: 1, selected: 2, index: 3 });
  }
  get index() {
    return this.$$.ctx[3];
  }
}
export {
  S as default
};
