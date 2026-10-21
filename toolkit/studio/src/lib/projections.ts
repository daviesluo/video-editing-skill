import { geoAzimuthalEqualArea, geoConicEqualArea, geoEqualEarth, geoMercator, type GeoProjection } from "d3-geo";

// Every map projection an episode uses is defined here, once. Scenes call
// these factories, and scripts/plate-params.ts and scripts/plate-grid.ts
// read the same factories, so pipeline/reproject.py warps imagery onto
// exactly the plate the vector layers use. Plain TypeScript, no JSX: Node
// runs this file with --experimental-strip-types.
//
// Choose with a reason: Equal Earth for the world (it keeps area);
// Mercator only when its distortion is the point; an equal-area conic or
// azimuthal for a country or region, centred on it.

const box = (west: number, south: number, east: number, north: number) => ({
  type: "Polygon" as const,
  coordinates: [
    [
      [west, south],
      [east, south],
      [east, north],
      [west, north],
      [west, south],
    ],
  ],
});

// The same box as points along its edges, one per degree. Fit regional
// projections to these: d3 reads a box polygon by the winding rule and can
// take it as its complement, so a conic or azimuthal fitted to it fits the
// whole world.
export const edges = (west: number, south: number, east: number, north: number) => {
  const pts: [number, number][] = [];
  for (let x = west; x <= east; x += 1) pts.push([x, south], [x, north]);
  for (let y = south; y <= north; y += 1) pts.push([west, y], [east, y]);
  return { type: "MultiPoint" as const, coordinates: pts };
};

export const PROJECTIONS: Record<string, (w: number, h: number) => GeoProjection> = {
  // The default flat world map.
  "equalearth-world": (w, h) => geoEqualEarth().fitExtent([[0, 0], [w, h]], { type: "Sphere" }),
  // World Mercator clipped to 58S..78N, for showing what Mercator distorts.
  "mercator-world": (w, h) => geoMercator().fitExtent([[0, 0], [w, h]], box(-179.9, -58, 179.9, 78)),
  // World Mercator 75S..84N: all of Greenland on the plate, and room for a
  // tall frame.
  "mercator-world84": (w, h) => geoMercator().fitExtent([[0, 0], [w, h]], box(-179.9, -75, 179.9, 84)),
  // A region on an azimuthal equal-area centred on it (Europe, as on the
  // EU's own EPSG:3035).
  "laea-europe": (w, h) => geoAzimuthalEqualArea().rotate([-10, -52]).fitExtent([[0, 0], [w, h]], edges(-24, 34, 42, 71.2)),
  // A country on an equal-area conic with standard parallels inside it
  // (the contiguous United States, Albers).
  "conic-usa": (w, h) => geoConicEqualArea().parallels([29.5, 45.5]).rotate([96, 0]).fitExtent([[0, 0], [w, h]], edges(-125, 24, -66, 50)),
};

export type ProjectionName = keyof typeof PROJECTIONS;
