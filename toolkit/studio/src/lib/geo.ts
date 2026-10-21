import { geoCentroid } from "d3-geo";
import type { Feature, Geometry, MultiPolygon, Polygon, Position } from "geojson";
import { feature } from "topojson-client";
import type { GeometryCollection, Topology } from "topojson-specification";
import world from "world-atlas/countries-50m.json";

// Country outlines from Natural Earth 1:50m via world-atlas (public domain
// data). For maps that compute anything (areas, overlaps, point in land),
// use the official Natural Earth release with its version and checksum
// logged, and repair rings that cross the antimeridian first: tested as
// flat polygons they become planet-wide false bands of land. Disputed
// borders are drawn dashed or not at all, taking no side.
type Props = { name: string };
const topo = world as unknown as Topology<{ countries: GeometryCollection<Props> }>;
export const COUNTRIES = feature(topo, topo.objects.countries).features as Feature<Polygon | MultiPolygon, Props>[];

export const country = (name: string): Feature<Polygon | MultiPolygon, Props> => {
  const f = COUNTRIES.find((c) => c.properties.name === name);
  if (!f) throw new Error(`No country named ${name} in Natural Earth 1:50m`);
  return f;
};

const toXYZ = ([lon, lat]: Position): [number, number, number] => {
  const l = (lon * Math.PI) / 180;
  const p = (lat * Math.PI) / 180;
  return [Math.cos(p) * Math.cos(l), Math.cos(p) * Math.sin(l), Math.sin(p)];
};
const toLonLat = ([x, y, z]: [number, number, number]): Position => [
  (Math.atan2(y, x) * 180) / Math.PI,
  (Math.asin(Math.max(-1, Math.min(1, z))) * 180) / Math.PI,
];

type V3 = [number, number, number];
const cross3 = (a: V3, b: V3): V3 => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
// The point and its local north, as an orthonormal frame.
const northFrame = (p: Position): [V3, V3, V3] => {
  const l = (p[0] * Math.PI) / 180;
  const q = (p[1] * Math.PI) / 180;
  const e1 = toXYZ(p);
  const e2: V3 = [-Math.sin(q) * Math.cos(l), -Math.sin(q) * Math.sin(l), Math.cos(q)];
  return [e1, e2, cross3(e1, e2)];
};

// Moves a shape across the sphere, carrying its centroid to `to`, by
// fraction t. A rotation on the sphere keeps the shape's true area, and
// re-projecting is what makes it shrink or grow correctly on the map;
// sliding it on screen would keep the wrong size, which is the whole lie a
// "true size" comparison exists to correct. By default it travels along the
// great circle, which turns a shape that moves far east or west; `upright`
// keeps its north pointing north at the end, so it stays recognisable (a
// shape moved without it arrived on its side). Move its name with it, by
// the same rotation (`slider`).
export const slide = <G extends Polygon | MultiPolygon>(f: Feature<G>, to: Position, t: number, upright = false): Feature<G> => {
  const rot = slider(f, to, t, upright);
  const g = f.geometry as Geometry;
  const geometry =
    g.type === "Polygon"
      ? { type: "Polygon", coordinates: g.coordinates.map((r) => r.map(rot)) }
      : { type: "MultiPolygon", coordinates: (g as MultiPolygon).coordinates.map((p) => p.map((r) => r.map(rot))) };
  return { ...f, geometry: geometry as G };
};

// The rotation `slide` applies, for points that travel with the shape
// (its label's anchor).
export const slider = (f: Feature<Polygon | MultiPolygon>, to: Position, t: number, upright = false): ((p: Position) => Position) => {
  let ax: number[];
  let theta: number;
  if (upright) {
    // The rotation taking the centroid's north frame onto the target's,
    // M = F E^T, applied as a fraction t of its angle about its axis.
    const E = northFrame(geoCentroid(f));
    const F = northFrame(to);
    const M = [0, 1, 2].map((i) => [0, 1, 2].map((j) => F[0][i] * E[0][j] + F[1][i] * E[1][j] + F[2][i] * E[2][j]));
    const k = [M[2][1] - M[1][2], M[0][2] - M[2][0], M[1][0] - M[0][1]];
    const kn = Math.hypot(k[0], k[1], k[2]) || 1;
    ax = [k[0] / kn, k[1] / kn, k[2] / kn];
    theta = Math.acos(Math.max(-1, Math.min(1, (M[0][0] + M[1][1] + M[2][2] - 1) / 2))) * t;
  } else {
    const a = toXYZ(geoCentroid(f));
    const b = toXYZ(to);
    const k = [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
    const kn = Math.hypot(k[0], k[1], k[2]) || 1;
    ax = [k[0] / kn, k[1] / kn, k[2] / kn];
    theta = Math.acos(Math.max(-1, Math.min(1, a[0] * b[0] + a[1] * b[1] + a[2] * b[2]))) * t;
  }
  const c = Math.cos(theta);
  const s = Math.sin(theta);
  return (p: Position): Position => {
    const v = toXYZ(p);
    const kxv = [ax[1] * v[2] - ax[2] * v[1], ax[2] * v[0] - ax[0] * v[2], ax[0] * v[1] - ax[1] * v[0]];
    const kdv = ax[0] * v[0] + ax[1] * v[1] + ax[2] * v[2];
    return toLonLat([
      v[0] * c + kxv[0] * s + ax[0] * kdv * (1 - c),
      v[1] * c + kxv[1] * s + ax[1] * kdv * (1 - c),
      v[2] * c + kxv[2] * s + ax[2] * kdv * (1 - c),
    ]);
  };
};
