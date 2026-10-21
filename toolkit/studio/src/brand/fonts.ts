import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";
import BRAND from "../../../brand.json";

// One typeface, the caption typeface, everywhere: Archivo at normal width,
// sentence case. Mixed faces, monospace labels and condensed or wide
// variants read as a template. The font is vendored in public/fonts (SIL
// OFL 1.1, licence beside it), so a render never fetches a font over the
// network, and loadFont() holds the render until it has loaded.
export const DISPLAY = BRAND.type.family;

loadFont({
  family: DISPLAY,
  url: staticFile(BRAND.type.fontFile),
  weight: "100 900",
  stretch: "62% 125%",
  format: "woff2",
});
