import type { GeoProjection } from "d3-geo";
import { useMemo } from "react";
import { AbsoluteFill, Img, staticFile, useVideoConfig } from "remotion";
import { renderPlate, type PlateStyle } from "../lib/plate";

export type LonLat = readonly [number, number];
export type Camera = { center: LonLat; zoom: number };
export type Project = (p: LonLat) => [number, number];
// What overlays need to draw in plate coordinates: the plate projection and
// the SVG transform that puts plate coordinates on screen.
export type Plate = { projection: GeoProjection; transform: string; scale: number; tx: number; ty: number };

// A map camera over a fixed plate. `zoom` 1 shows the plate's full width
// across the frame; keep zoom at or below plateWidth / frameWidth so the
// plate is never upscaled. Children receive `project`, which maps lon/lat to
// screen pixels for overlays (routes, markers, labels) drawn in screen space.
export const MapView: React.FC<{
  plateKey: string;
  makeProjection: (w: number, h: number) => GeoProjection;
  plateWidth: number;
  plateHeight: number;
  camera: Camera;
  style?: PlateStyle;
  plateOpacity?: number;
  // An image in public/ already reprojected to the same projection and plate
  // size (see pipeline/reproject.py); drawn under the vector plate.
  raster?: string;
  children?: (project: Project, scale: number, plate: Plate) => React.ReactNode;
}> = ({ plateKey, makeProjection, plateWidth, plateHeight, camera, style, plateOpacity = 1, raster, children }) => {
  const { width, height } = useVideoConfig();
  const projection = useMemo(
    () => makeProjection(plateWidth, plateHeight),
    [makeProjection, plateWidth, plateHeight],
  );
  const src = useMemo(
    () => renderPlate(plateKey, projection, plateWidth, plateHeight, style),
    [plateKey, projection, plateWidth, plateHeight, style],
  );
  const s = (camera.zoom * width) / plateWidth;
  const c = projection(camera.center as [number, number]) ?? [plateWidth / 2, plateHeight / 2];
  const tx = width / 2 - c[0] * s;
  const ty = height / 2 - c[1] * s;
  const project: Project = (p) => {
    const q = projection(p as [number, number]) ?? [NaN, NaN];
    return [q[0] * s + tx, q[1] * s + ty];
  };
  const layer: React.CSSProperties = {
    position: "absolute",
    left: 0,
    top: 0,
    width: plateWidth,
    height: plateHeight,
    transformOrigin: "0 0",
    transform: `translate(${tx}px, ${ty}px) scale(${s})`,
    opacity: plateOpacity,
  };
  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      {raster ? <Img src={staticFile(raster)} style={layer} /> : null}
      <Img src={src} style={layer} />
      {children ? children(project, s, { projection, transform: `translate(${tx} ${ty}) scale(${s})`, scale: s, tx, ty }) : null}
    </AbsoluteFill>
  );
};
