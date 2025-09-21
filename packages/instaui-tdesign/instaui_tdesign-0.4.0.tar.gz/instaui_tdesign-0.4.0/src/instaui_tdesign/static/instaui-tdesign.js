import { defineComponent as l, useAttrs as p, useSlots as _, createBlock as m, openBlock as h, mergeProps as d, unref as o, createSlots as g, renderList as A, withCtx as x, renderSlot as P, normalizeProps as b, guardReactiveProps as $, computed as C } from "vue";
import * as f from "tdesign-vue-next";
function D(n) {
  const { container: t = ".insta-main" } = n;
  return t;
}
const S = /* @__PURE__ */ l({
  inheritAttrs: !1,
  __name: "Affix",
  setup(n) {
    const t = p(), r = _(), e = D(t);
    return (s, a) => (h(), m(f.Affix, d(o(t), { container: o(e) }), g({ _: 2 }, [
      A(o(r), (w, c) => ({
        name: c,
        fn: x((i) => [
          P(s.$slots, c, b($(i)))
        ])
      }))
    ]), 1040, ["container"]));
  }
});
function v(n) {
  return C(() => {
    const { pagination: t, data: r = [] } = n;
    let e;
    if (typeof t == "boolean") {
      if (!t)
        return;
      e = {
        defaultPageSize: 10
      };
    }
    return typeof t == "number" && t > 0 && (e = {
      defaultPageSize: t
    }), typeof t == "object" && t !== null && (e = t), {
      defaultCurrent: 1,
      total: r.length,
      ...e
    };
  });
}
function y(n) {
  return C(
    () => ({
      hover: !0,
      bordered: !0,
      tableLayout: "auto",
      ...n
    })
  );
}
const z = /* @__PURE__ */ l({
  inheritAttrs: !1,
  __name: "Table",
  setup(n) {
    const t = p(), r = v(t), e = y(t), s = _();
    return (a, w) => (h(), m(f.Table, d(o(e), { pagination: o(r) }), g({ _: 2 }, [
      A(o(s), (c, i) => ({
        name: i,
        fn: x((u) => [
          P(a.$slots, i, b($(u)))
        ])
      }))
    ]), 1040, ["pagination"]));
  }
});
function T(n) {
  const { affixProps: t = {} } = n;
  return {
    container: ".insta-main",
    ...t
  };
}
function k(n) {
  const { container: t = ".insta-main" } = n;
  return t;
}
const B = /* @__PURE__ */ l({
  inheritAttrs: !1,
  __name: "Anchor",
  setup(n) {
    const t = p(), r = _(), e = T(t), s = k(t);
    return (a, w) => (h(), m(f.Anchor, d(o(t), {
      container: o(s),
      "affix-props": o(e)
    }), g({ _: 2 }, [
      A(o(r), (c, i) => ({
        name: i,
        fn: x((u) => [
          P(a.$slots, i, b($(u)))
        ])
      }))
    ]), 1040, ["container", "affix-props"]));
  }
});
function j(n) {
  n.use(f), n.component("t-table", z), n.component("t-affix", S), n.component("t-anchor", B);
}
export {
  j as install
};
