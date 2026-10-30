// Builds the static PowerPoint deck for one day from a JSON spec.
// Usage: node build_pptx.js spec.json out.pptx
const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");
const { applyTheme } = require("./theme.js");

const spec = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const OUT = process.argv[3];
const BRAND = path.join(__dirname, "..", "assets", "brand");

const THEME = {
  name: "NIGCOMSAT Time-Series",
  headFontFace: "Arial",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "0B1622", lt1: "FFFFFF", dk2: "12233A", lt2: "EEF3F8",
    accent1: "0A5DB4", accent2: "008C7E", accent3: "C77700", accent4: "1E9E5A",
    accent5: "E5484D", accent6: "5B6B7D", hlink: "0A5DB4", folHlink: "008C7E",
  },
};
const HEX = THEME.colors;

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.author = "Publica Academy";
pres.company = "Publica Academy";
pres.title = `${spec.code} · ${spec.title}`;
const C = pres.SchemeColor;
const W = 13.333, H = 7.5, M = 0.6;

const NIG = path.join(BRAND, "nigcomsat-logo.png"); // 900x754
const PUB = path.join(BRAND, "publica-academy-logo.png"); // 400x318
const footText = `Publica Academy · Time-Series Programme · ${spec.code}`;

// ---------- layouts ----------
pres.defineSlideMaster({
  title: "LIGHT_CONTENT",
  background: { color: HEX.lt1 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: M, y: 0.35, w: W - 2 * M, h: 0.95, fontFace: THEME.headFontFace, fontSize: 32, bold: true, color: C.text1, valign: "middle", margin: 0 }, text: "" } },
    { image: { x: M, y: 6.93, w: 0.44, h: 0.35, path: PUB } },
    { text: { text: footText, options: { x: M + 0.55, y: 6.93, w: 7, h: 0.35, fontSize: 11, color: C.accent6, valign: "middle", margin: 0 } } },
    { image: { x: W - M - 0.6, y: 6.82, w: 0.6, h: 0.5, path: NIG } },
  ],
  slideNumber: { x: W - M - 1.35, y: 6.93, w: 0.6, h: 0.35, fontSize: 11, color: HEX.accent6, align: "right" },
});
pres.defineSlideMaster({
  title: "DARK_TITLE",
  background: { color: HEX.dk1 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: M + 0.2, y: 2.05, w: 7.6, h: 2.0, fontFace: THEME.headFontFace, fontSize: 42, bold: true, color: C.background1, align: "left", valign: "top", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: M + 0.2, y: 4.15, w: 7.4, h: 1.0, fontSize: 20, color: "C9D6E5", align: "left", valign: "top", margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "DARK_SECTION",
  background: { color: HEX.dk1 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: M, y: 2.7, w: W - 2 * M, h: 1.3, fontFace: THEME.headFontFace, fontSize: 48, bold: true, color: C.background1, align: "center", valign: "middle", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: M, y: 4.05, w: W - 2 * M, h: 0.7, fontSize: 22, color: "C9D6E5", align: "center", margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "DARK_RECAP",
  background: { color: HEX.dk1 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: M, y: 0.45, w: W - 2 * M, h: 0.95, fontFace: THEME.headFontFace, fontSize: 34, bold: true, color: C.background1, valign: "middle", margin: 0 }, text: "" } },
    { image: { x: M, y: 6.93, w: 0.44, h: 0.35, path: PUB } },
    { text: { text: footText, options: { x: M + 0.55, y: 6.93, w: 7, h: 0.35, fontSize: 11, color: "9DB0C6", valign: "middle", margin: 0 } } },
  ],
});

// ---------- helpers ----------
function emojiImg(slide, emoji, x, y, s, name = "icon") {
  const p = (spec.emoji || {})[emoji];
  if (p) slide.addImage({ path: p, x, y, w: s, h: s, altText: name, objectName: name });
  else slide.addText(emoji, { x, y, w: s, h: s, align: "center", valign: "middle", fontSize: Math.round(s * 40), margin: 0, isTextBox: true, objectName: name });
}
function emojiDot(slide, emoji, x, y, d, tint = C.accent1, name = "icon") {
  slide.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: tint, transparency: 84 }, line: { color: tint, width: 1, transparency: 60 }, objectName: name + " circle" });
  emojiImg(slide, emoji, x + d * 0.2, y + d * 0.2, d * 0.6, name);
}
function card(slide, x, y, w, h, name) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.18, fill: { color: C.background2 }, line: { color: "DCE4EC", width: 1 }, objectName: name });
}
function kicker(slide, text, x, y, w, color = C.accent2) {
  slide.addText(text.toUpperCase(), { x, y, w, h: 0.4, fontSize: 14, bold: true, charSpacing: 3, color, margin: 0, isTextBox: true, objectName: "kicker" });
}
const TINTS = [C.accent1, C.accent2, C.accent3, C.accent4, C.accent1];

function cardsRow(slide, cards, top = 1.85, h = 3.7) {
  const n = cards.length, gap = 0.4, w = (W - 2 * M - gap * (n - 1)) / n;
  cards.forEach((c, i) => {
    const x = M + i * (w + gap);
    card(slide, x, top, w, h, `card ${i + 1}`);
    emojiDot(slide, c[0], x + (n >= 5 ? 0.22 : 0.4), top + 0.45, 1.05, TINTS[i % TINTS.length], `icon ${i + 1}`);
    const pad = n >= 5 ? 0.22 : 0.4;
    slide.addText(c[1], { x: x + pad, y: top + 1.75, w: w - 2 * pad, h: 0.75, fontSize: n >= 5 ? 18 : 22, bold: true, color: C.text1, valign: "top", margin: 0, isTextBox: true, fontFace: THEME.headFontFace });
    if (c[2]) slide.addText(c[2], { x: x + 0.4, y: top + 2.5, w: w - 0.8, h: h - 2.8, fontSize: 16, color: C.accent6, valign: "top", margin: 0, isTextBox: true });
  });
}
function lineChart(slide, labels, values, x, y, w, h, color, opts = {}) {
  slide.addChart(pres.charts.LINE, [{ name: opts.name || "value", labels, values }], {
    x, y, w, h,
    chartColors: [color], lineSize: 2, lineDataSymbol: "none",
    showLegend: false, showTitle: false,
    catAxisLabelColor: "5B6B7D", valAxisLabelColor: "5B6B7D",
    catAxisLabelFontSize: 10, valAxisLabelFontSize: 10,
    catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt",
    valGridLine: { color: "E3E9F0", size: 0.75 }, catGridLine: { style: "none" },
    valAxisMinVal: opts.ymin, valAxisMaxVal: opts.ymax, valAxisLabelFormatCode: opts.fmt || "0.0",
    catAxisLabelFrequency: opts.freq || 6, catAxisLineShow: false, valAxisLineShow: false,
    objectName: opts.objectName || "line chart",
  });
}

// ---------- slide types ----------
const R = {
  title(s) {
    const sl = pres.addSlide({ masterName: "DARK_TITLE" });
    kicker(sl, s.kicker, M + 0.2, 1.55, 6, "F5B83D");
    sl.addText(s.title, { placeholder: "title" });
    sl.addText(s.sub, { placeholder: "body" });
    // logos on white cards
    sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: M + 0.2, y: 5.55, w: 1.75, h: 1.25, rectRadius: 0.15, fill: { color: C.background1 }, line: { color: C.background1 }, objectName: "NIGCOMSAT logo card" });
    sl.addImage({ path: NIG, x: M + 0.4, y: 5.65, w: 1.25, h: 1.05, altText: "NIGCOMSAT logo" });
    sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: M + 2.15, y: 5.55, w: 3.0, h: 1.25, rectRadius: 0.15, fill: { color: C.background1 }, line: { color: C.background1 }, objectName: "Publica logo card" });
    sl.addImage({ path: PUB, x: M + 2.35, y: 5.75, w: 1.07, h: 0.85, altText: "Publica Academy logo" });
    sl.addText("Publica\nAcademy", { x: M + 3.55, y: 5.7, w: 1.5, h: 0.95, fontSize: 18, bold: true, color: C.text1, valign: "middle", margin: 0, isTextBox: true, fontFace: THEME.headFontFace });
    // orbit motif
    sl.addShape(pres.shapes.OVAL, { x: 9.3, y: 1.4, w: 3.6, h: 3.6, fill: { color: C.accent1 }, line: { color: C.accent1 }, objectName: "earth" });
    sl.addShape(pres.shapes.OVAL, { x: 8.45, y: 0.55, w: 5.3, h: 5.3, fill: { type: "none" }, line: { color: "3B8BE0", width: 1.25, dashType: "dash" }, objectName: "orbit" });
    emojiImg(sl, s.icon || "🛰️", 12.2, 0.5, 1.0, "satellite");
    return sl;
  },
  section(s) {
    const sl = pres.addSlide({ masterName: "DARK_SECTION" });
    sl.addText(s.kicker.toUpperCase(), { x: M, y: 2.15, w: W - 2 * M, h: 0.45, fontSize: 16, bold: true, charSpacing: 4, color: "F5B83D", align: "center", margin: 0, isTextBox: true });
    sl.addText(s.title, { placeholder: "title" });
    sl.addText(s.sub, { placeholder: "body" });
    return sl;
  },
  cards(s) { const sl = pres.addSlide({ masterName: "LIGHT_CONTENT" }); sl.addText(s.title, { placeholder: "title" }); cardsRow(sl, s.cards); return sl; },
  cards4(s) { return R.cards(s); },
  cards5(s) { const sl = pres.addSlide({ masterName: "LIGHT_CONTENT" }); sl.addText(s.title, { placeholder: "title" }); cardsRow(sl, s.cards, 2.0, 3.2); return sl; },
  flow(s) {
    const sl = pres.addSlide({ masterName: "LIGHT_CONTENT" });
    sl.addText(s.title, { placeholder: "title" });
    const n = s.steps.length, aw = 0.7, w = (W - 2 * M - aw * (n - 1)) / n, top = 1.9, h = 3.3;
    s.steps.forEach((st, i) => {
      const x = M + i * (w + aw);
      card(sl, x, top, w, h, `step ${i + 1}`);
      emojiDot(sl, st[0], x + w / 2 - 0.55, top + 0.35, 1.1, TINTS[i], `step icon ${i + 1}`);
      sl.addText(st[1], { x: x + 0.3, y: top + 1.6, w: w - 0.6, h: 0.6, fontSize: 22, bold: true, align: "center", color: C.text1, margin: 0, isTextBox: true, fontFace: THEME.headFontFace });
      sl.addText(st[2], { x: x + 0.3, y: top + 2.25, w: w - 0.6, h: 0.8, fontSize: 16, align: "center", color: C.accent6, valign: "top", margin: 0, isTextBox: true });
      if (i < n - 1) sl.addShape(pres.shapes.RIGHT_ARROW, { x: x + w + 0.12, y: top + h / 2 - 0.25, w: aw - 0.24, h: 0.5, fill: { color: C.accent2 }, line: { color: C.accent2 }, objectName: `arrow ${i + 1}` });
    });
    if (s.footer) sl.addText(s.footer, { x: M, y: 5.65, w: W - 2 * M, h: 0.6, fontSize: 18, italic: true, color: C.accent1, align: "center", margin: 0, isTextBox: true });
    return sl;
  },
  compare(s) {
    const sl = pres.addSlide({ masterName: "LIGHT_CONTENT" });
    sl.addText(s.title, { placeholder: "title" });
    [s.left, s.right].forEach((c, i) => {
      const w = (W - 2 * M - 0.5) / 2, x = M + i * (w + 0.5), top = 1.8, h = 4.3;
      card(sl, x, top, w, h, i ? "right card" : "left card");
      emojiDot(sl, c[0], x + 0.45, top + 0.45, 1.2, i ? C.accent5 : C.accent4, i ? "right icon" : "left icon");
      sl.addText(c[1], { x: x + 0.45, y: top + 1.9, w: w - 0.9, h: 0.7, fontSize: 26, bold: true, color: C.text1, margin: 0, isTextBox: true, fontFace: THEME.headFontFace });
      sl.addText(c[2], { x: x + 0.45, y: top + 2.65, w: w - 0.9, h: 1.4, fontSize: 18, color: C.accent6, valign: "top", margin: 0, isTextBox: true });
    });
    return sl;
  },
  chart(s) {
    const sl = pres.addSlide({ masterName: "LIGHT_CONTENT" });
    sl.addText(s.title, { placeholder: "title" });
    if (s.series) {   // several lines: [{name, values, color}]
      sl.addChart(pres.charts.LINE, s.series.map((x) => ({ name: x.name, labels: s.labels, values: x.values })), {
        x: M, y: 1.5, w: W - 2 * M, h: 4.5, chartColors: s.series.map((x) => x.color || HEX.accent1),
        lineSize: 2, lineDataSymbol: "none", showLegend: true, legendPos: "t", legendFontSize: 12, legendFontFace: "+mn-lt",
        showTitle: false, catAxisLabelColor: "5B6B7D", valAxisLabelColor: "5B6B7D", catAxisLabelFontSize: 10, valAxisLabelFontSize: 10,
        catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt", valGridLine: { color: "E3E9F0", size: 0.75 }, catGridLine: { style: "none" },
        valAxisMinVal: s.ymin, valAxisMaxVal: s.ymax, valAxisLabelFormatCode: s.fmt || "0.0", catAxisLineShow: false, valAxisLineShow: false, objectName: "line chart",
      });
    } else {
      lineChart(sl, s.labels, s.values, M, 1.5, W - 2 * M, 4.5, s.color || HEX.accent1, { ymin: s.ymin, ymax: s.ymax, freq: s.freq || 3, name: s.name || "value", fmt: s.fmt });
    }
    sl.addText(s.caption, { x: M, y: 6.15, w: W - 2 * M, h: 0.5, fontSize: 16, color: C.accent6, italic: true, margin: 0, isTextBox: true });
    return sl;
  },
  twochart(s) {
    const sl = pres.addSlide({ masterName: "LIGHT_CONTENT" });
    sl.addText(s.title, { placeholder: "title" });
    [s.left, s.right].forEach((c, i) => {
      const w = (W - 2 * M - 0.5) / 2, x = M + i * (w + 0.5);
      card(sl, x, 1.55, w, 4.95, i ? "right card" : "left card");
      sl.addText(c.label, { x: x + 0.3, y: 1.7, w: w - 0.6, h: 0.6, fontSize: 18, bold: true, color: c.good ? C.accent2 : (i ? C.accent5 : C.accent2), margin: 0, isTextBox: true });
      lineChart(sl, c.labels, c.values, x + 0.2, 2.35, w - 0.4, 3.95, c.color || (i ? HEX.accent5 : HEX.accent1), { ymin: c.ymin ?? 97.5, ymax: c.ymax ?? 100.2, freq: c.freq || 6, fmt: c.fmt, objectName: i ? "right chart" : "left chart" });
    });
    return sl;
  },
  code(s) {
    const sl = pres.addSlide({ masterName: "LIGHT_CONTENT" });
    sl.addText(s.title, { placeholder: "title" });
    sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: M, y: 1.65, w: W - 2 * M, h: 3.6, rectRadius: 0.18, fill: { color: C.text1 }, line: { color: C.text1 }, objectName: "code panel" });
    sl.addText(s.code, { x: M + 0.45, y: 1.85, w: W - 2 * M - 0.9, h: 3.2, fontFace: "Courier New", fontSize: 18, color: "D7E3F1", valign: "middle", margin: 0, isTextBox: true, objectName: "code" });
    sl.addText(s.caption, { x: M, y: 5.55, w: W - 2 * M, h: 0.7, fontSize: 18, color: C.accent1, bold: true, margin: 0, isTextBox: true });
    return sl;
  },
  stats(s) {
    const sl = pres.addSlide({ masterName: "LIGHT_CONTENT" });
    sl.addText(s.title, { placeholder: "title" });
    sl.addText(s.sub, { x: M, y: 1.3, w: W - 2 * M, h: 0.5, fontSize: 18, color: C.accent6, margin: 0, isTextBox: true });
    const n = s.stats.length, gap = 0.35, w = (W - 2 * M - gap * (n - 1)) / n;
    s.stats.forEach((st, i) => {
      const x = M + i * (w + gap);
      card(sl, x, 2.2, w, 3.4, `stat ${i + 1}`);
      sl.addText(st[0], { x: x + 0.2, y: 2.6, w: w - 0.4, h: 1.5, fontSize: st[0].length > 7 ? 30 : 48, bold: true, color: TINTS[i], align: "center", valign: "middle", margin: 0, isTextBox: true, fontFace: THEME.headFontFace });
      sl.addText(st[1], { x: x + 0.25, y: 4.2, w: w - 0.5, h: 1.0, fontSize: 16, color: C.accent6, align: "center", valign: "top", margin: 0, isTextBox: true });
    });
    return sl;
  },
  statement(s) {   // one big message: emoji + headline + sub
    const sl = pres.addSlide({ masterName: "LIGHT_CONTENT" });
    sl.addText(s.title, { placeholder: "title" });
    emojiDot(sl, s.icon, W / 2 - 1.1, 1.6, 2.2, C.accent1, "big icon");
    sl.addText(s.big, { x: M + 0.5, y: 4.0, w: W - 2 * M - 1, h: 1.1, fontSize: 30, bold: true, color: C.text1, align: "center", valign: "middle", margin: 0, isTextBox: true, fontFace: THEME.headFontFace });
    if (s.sub) sl.addText(s.sub, { x: M + 1, y: 5.15, w: W - 2 * M - 2, h: 0.9, fontSize: 18, color: C.accent6, align: "center", valign: "top", margin: 0, isTextBox: true });
    return sl;
  },
  bar(s) {   // native bar chart: labels, values, optional highlight index list
    const sl = pres.addSlide({ masterName: "LIGHT_CONTENT" });
    sl.addText(s.title, { placeholder: "title" });
    const colors = s.labels.map((_, i) => ((s.highlight || []).includes(i) ? HEX.accent3 : HEX.accent1));
    sl.addChart(pres.charts.BAR, [{ name: s.name || "value", labels: s.labels, values: s.values }], {
      x: M, y: 1.5, w: W - 2 * M, h: 4.5, barDir: "col", chartColors: colors.length > 1 ? colors : [HEX.accent1], invertedColors: colors,
      showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 12, dataLabelColor: "0B1622", dataLabelFormatCode: s.fmt || "0.0",
      showLegend: false, showTitle: false, catAxisLabelColor: "5B6B7D", valAxisLabelColor: "5B6B7D", catAxisLabelFontSize: 12, valAxisLabelFontSize: 10,
      catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt", dataLabelFontFace: "+mn-lt",
      valGridLine: { color: "E3E9F0", size: 0.75 }, catGridLine: { style: "none" }, valAxisMinVal: s.ymin ?? 0, valAxisMaxVal: s.ymax,
      valAxisLabelFormatCode: s.fmt || "0.0", barGapWidthPct: 60, objectName: "bar chart",
    });
    if (s.caption) sl.addText(s.caption, { x: M, y: 6.15, w: W - 2 * M, h: 0.5, fontSize: 16, color: C.accent6, italic: true, margin: 0, isTextBox: true });
    return sl;
  },
  table(s) {   // header: [..], rows: [[..], ..]
    const sl = pres.addSlide({ masterName: "LIGHT_CONTENT" });
    sl.addText(s.title, { placeholder: "title" });
    const head = s.header.map((h) => ({ text: h, options: { bold: true, color: "FFFFFF", fill: { color: HEX.dk1 }, fontSize: 16 } }));
    const rows = s.rows.map((r, k) => r.map((c, j) => ({ text: String(c), options: { fontSize: 16, color: HEX.dk1, bold: j === 0, fill: { color: k % 2 ? "FFFFFF" : HEX.lt2 } } })));
    sl.addTable([head, ...rows], { x: M, y: 1.6, w: W - 2 * M, colW: s.colW, border: { type: "solid", pt: 0.75, color: "DCE4EC" }, margin: 0.08, valign: "middle", objectName: "table" });
    if (s.caption) sl.addText(s.caption, { x: M, y: 6.15, w: W - 2 * M, h: 0.5, fontSize: 16, color: C.accent6, italic: true, margin: 0, isTextBox: true });
    return sl;
  },
  steps(s) {
    const sl = pres.addSlide({ masterName: "LIGHT_CONTENT" });
    sl.addText(s.title, { placeholder: "title" });
    s.steps.forEach((t, i) => {
      const y = 1.75 + i * 1.12;
      sl.addShape(pres.shapes.OVAL, { x: M, y, w: 0.8, h: 0.8, fill: { color: C.accent1 }, line: { color: C.accent1 }, objectName: `number ${i + 1}` });
      sl.addText(String(i + 1), { x: M, y, w: 0.8, h: 0.8, fontSize: 24, bold: true, color: C.background1, align: "center", valign: "middle", margin: 0, isTextBox: true });
      sl.addText(t, { x: M + 1.1, y, w: 9.5, h: 0.8, fontSize: 24, color: C.text1, valign: "middle", margin: 0, isTextBox: true });
    });
    if (s.icon) emojiDot(sl, s.icon, 10.3, 2.2, 2.3, C.accent2, "icon");
    return sl;
  },
  recap(s) {
    const sl = pres.addSlide({ masterName: "DARK_RECAP" });
    sl.addText(s.title, { placeholder: "title" });
    s.points.forEach((p, i) => {
      const y = 1.75 + i * 1.3;
      sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: M, y, w: W - 2 * M, h: 1.05, rectRadius: 0.15, fill: { color: C.text2 }, line: { color: "24384F", width: 1 }, objectName: `recap ${i + 1}` });
      emojiImg(sl, p[0], M + 0.35, y + 0.2, 0.65, `recap icon ${i + 1}`);
      sl.addText(p[1], { x: M + 1.3, y, w: W - 2 * M - 1.6, h: 1.05, fontSize: 22, color: C.background1, valign: "middle", margin: 0, isTextBox: true });
    });
    sl.addText(s.next, { x: M, y: 5.85, w: W - 2 * M, h: 0.6, fontSize: 22, bold: true, color: "F5B83D", margin: 0, isTextBox: true });
    return sl;
  },
};

(async () => {
  for (const s of spec.slides) {
    if (!R[s.type]) throw new Error("unknown slide type " + s.type);
    const sl = R[s.type](s);
    if (s.notes) sl.addNotes(s.notes);
  }
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("wrote", OUT);
})();
