import { THEME } from "../brand/tokens";
import type { PlateStyle } from "./plate";

// The flat-map look for the current theme. Relief (the house look) and
// satellite themes lay a raster reprojected onto the plate
// (pipeline/textures.py, pipeline/reproject.py) under the vector lines;
// vector themes draw land and sea themselves.
const SATELLITE: PlateStyle = {
  ocean: "rgba(0,0,0,0)",
  land: "rgba(0,0,0,0)",
  graticule: "rgba(160,185,230,0.07)",
  border: "rgba(220,230,255,0.2)",
  coast: "rgba(220,230,255,0.3)",
};
// The relief raster has its own crisp 10m coastline, so only the graticule
// and the borders are drawn over it.
const RELIEF: PlateStyle = {
  ocean: "rgba(0,0,0,0)",
  land: "rgba(0,0,0,0)",
  graticule: "rgba(255,255,255,0.14)",
  border: "rgba(110,98,82,0.55)",
  coast: "rgba(0,0,0,0)",
};

export const plateLook = (projection: string, width: number, height: number): { raster?: string; style?: PlateStyle } => {
  if (THEME.plates === "satellite") return { raster: `textures/plate-${projection}.jpg`, style: SATELLITE };
  if (THEME.plates === "relief") return { raster: `textures/plate-${THEME.name}-${projection}-${width}x${height}.jpg`, style: RELIEF };
  return {};
};
