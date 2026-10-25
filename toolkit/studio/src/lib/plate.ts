import { geoGraticule10, geoPath, type GeoProjection } from "d3-geo";
import { feature } from "topojson-client";
import type { GeometryCollection, Topology } from "topojson-specification";
import countries50 from "world-atlas/countries-50m.json";
import boundaries from "../data/ne50-boundaries.json";
import { COLORS } from "../brand/tokens";

// A "fixed map plate": the basemap is rasterised once per page into an image,
// and camera moves transform that image. Redrawing 60k vertices of live SVG
// every frame costs about 1 s/frame on the CPU renderer; the plate costs
// almost nothing after the first draw.

const topo = countries50 as unknown as Topology<{
  countries: GeometryCollection<{ name: string }>;
  land: GeometryCollection;
}>;
export const LAND = feature(topo, topo.objects.land);
export const COUNTRIES = feature(topo, topo.objects.countries);
// Land borders from Natural Earth 1:50m boundary lines (data/
// ne50-boundaries.json, written by `globetex.py borderlines`): a settled
// international boundary solid, every other line (disputed, line of
// control, indefinite, unrecognized) dashed, taking no side.
const B = boundaries as unknown as Record<"solid" | "dashed", GeoJSON.MultiLineString>;

export type PlateStyle = {
  ocean?: string;
  land?: string;
  border?: string;
  coast?: string;
  graticule?: string | null;
};

const cache = new Map<string, string>();

// Draws the plate at `width` x `height` with `projection` already fitted to
// that size, and returns a PNG data URL. Cached by `key` for the page's life.
export const renderPlate = (
  key: string,
  projection: GeoProjection,
  width: number,
  height: number,
  style: PlateStyle = {},
): string => {
  const hit = cache.get(key);
  if (hit) return hit;
  const canvas = document.createElement("canvas");
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext("2d");
  if (!ctx) throw new Error("2D canvas unavailable");
  const path = geoPath(projection, ctx);

  ctx.fillStyle = style.ocean ?? COLORS.ocean;
  ctx.fillRect(0, 0, width, height);
  if (style.graticule !== null) {
    ctx.beginPath();
    path(geoGraticule10());
    ctx.strokeStyle = style.graticule ?? COLORS.graticule;
    ctx.lineWidth = Math.max(1, width / 2000);
    ctx.stroke();
  }
  ctx.beginPath();
  path(LAND);
  ctx.fillStyle = style.land ?? COLORS.land;
  ctx.fill();
  ctx.strokeStyle = style.border ?? "rgba(120, 145, 190, 0.35)";
  ctx.lineWidth = Math.max(1, width / 1800);
  ctx.beginPath();
  path(B.solid);
  ctx.stroke();
  ctx.beginPath();
  path(B.dashed);
  ctx.setLineDash([ctx.lineWidth * 4, ctx.lineWidth * 3]);
  ctx.stroke();
  ctx.setLineDash([]);
  ctx.beginPath();
  path(LAND);
  ctx.strokeStyle = style.coast ?? COLORS.landEdge;
  ctx.lineWidth = Math.max(1.2, width / 1400);
  ctx.stroke();

  const url = canvas.toDataURL("image/png");
  cache.set(key, url);
  return url;
};

export const countryByName = (name: string) => {
  const f = COUNTRIES.features.find((c) => c.properties?.name === name);
  if (!f) throw new Error(`No country named ${name} in world-atlas 50m`);
  return f;
};
