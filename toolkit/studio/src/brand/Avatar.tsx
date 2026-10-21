import { Img, staticFile } from "remotion";
import BRAND from "../../../brand.json";
import { COLORS } from "./tokens";
import { DISPLAY } from "./fonts";

// The account's picture, as the platform crops it (a circle). brand.json's
// `avatar` names an image in public/ (square, at least 1080 px); until one
// is set, a monogram of the series name stands in. An avatar is simple,
// bold and stylised, so it still reads at 110 px in a feed.
export const Avatar: React.FC<{ size: number }> = ({ size }) => {
  const initials = BRAND.series
    .replace(/[<>]/g, "")
    .split(/\s+/)
    .filter(Boolean)
    .map((w) => w[0].toUpperCase())
    .slice(0, 2)
    .join("");
  return (
    <div style={{ width: size, height: size, borderRadius: "50%", overflow: "hidden", background: COLORS.accent }}>
      {BRAND.avatar ? (
        <Img src={staticFile(BRAND.avatar)} style={{ width: size, height: size, objectFit: "cover" }} />
      ) : (
        <div style={{ width: size, height: size, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: DISPLAY, fontWeight: 850, fontSize: size * 0.4, color: COLORS.mark }}>
          {initials || "S"}
        </div>
      )}
    </div>
  );
};
