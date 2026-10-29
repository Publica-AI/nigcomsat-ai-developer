// Writes our brand colours into the deck's theme (pptxgenjs only sets fonts, not colours).
const fs = require("fs");
const JSZip = require(require.resolve("jszip", { paths: [require.resolve("pptxgenjs")] }));

const SLOTS = ["dk1", "lt1", "dk2", "lt2", "accent1", "accent2", "accent3", "accent4", "accent5", "accent6", "hlink", "folHlink"];

async function applyTheme(deckPath, theme) {
  const zip = await JSZip.loadAsync(fs.readFileSync(deckPath));
  const part = "ppt/theme/theme1.xml";
  const name = theme.name.replace(/&/g, "&amp;").replace(/"/g, "&quot;");
  const scheme = `<a:clrScheme name="${name}">` +
    SLOTS.map((k) => `<a:${k}><a:srgbClr val="${theme.colors[k]}"/></a:${k}>`).join("") + "</a:clrScheme>";
  let xml = await zip.file(part).async("string");
  xml = xml.replace(/<a:clrScheme\b[\s\S]*?<\/a:clrScheme>/, () => scheme)
           .replace(/(<a:(?:theme|fontScheme)\b[^>]*?\bname=")[^"]*"/g, (_, h) => `${h}${name}"`);
  zip.file(part, xml);
  for (const f of Object.keys(zip.files)) {           // a scheme colour in a hex-only option breaks the file
    if (!f.endsWith(".xml")) continue;
    const bad = (await zip.file(f).async("string")).match(/<a:srgbClr val="((?![0-9A-Fa-f]{6}")[^"]*)"/);
    if (bad) throw new Error(`${f}: colour "${bad[1]}" is not 6-digit hex`);
  }
  fs.writeFileSync(deckPath, await zip.generateAsync({ type: "nodebuffer", compression: "DEFLATE" }));
}
module.exports = { applyTheme };
