// Applies to `npx remotion render` and `npx remotion studio`; the Node
// scripts in scripts/ pass the same options to the renderer directly.
import { Config } from "@remotion/cli/config";

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
Config.setDefaultPremountInSeconds(2);
