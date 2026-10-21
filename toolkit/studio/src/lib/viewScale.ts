// Sizes for the view, not for the planet. A marker sized in world units
// (a share of the planet's radius) swells as the camera closes in: a hole
// drawn 0.026 radii across ballooned three to six times in the close-ups,
// grew wider than the distance it marked, and covered labels and lines.
// So a marked place is a dot of a fixed size on screen, drawn as a 2D
// overlay from the globe's projection; when something must live in the
// 3D scene, `worldForPx` gives the world size that keeps it `px` tall on
// screen at the surface, for a camera `distance` radii from the centre.
// 3D is only for what is truly 3D (a cut-away planet, a shaft).
//
// No imports, so the self-test can load it with nothing installed.

// The globe camera's vertical field of view, in degrees (GlobeView uses it).
export const GLOBE_FOV = 30;

// The world size that is `px` tall on screen at the surface point nearest
// the camera (its depth is distance - 1), on a frame `height` px tall.
export const worldForPx = (px: number, distance: number, height = 1920, fov = GLOBE_FOV): number =>
  (px * 2 * (distance - 1) * Math.tan((fov * Math.PI) / 360)) / height;

// The inverse: how many px tall a world size shows at that surface point.
export const pxForWorld = (size: number, distance: number, height = 1920, fov = GLOBE_FOV): number =>
  (size * height) / (2 * (distance - 1) * Math.tan((fov * Math.PI) / 360));
