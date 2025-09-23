import {
    PrivateDiagramLookupService
} from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramLookupService";
import {
    DiagramOverrideBase,
    DiagramOverrideTypeE
} from "@peek/peek_plugin_diagram/override/DiagramOverrideBase";
import {
    DiagramOverrideCanvasBackgroundColor
} from "@peek/peek_plugin_diagram/override/DiagramOverrideCanvasBackgroundColor";
import { PeekCanvasModelOverrideA } from "./PeekCanvasModelOverrideA";
import { PeekCanvasConfig } from "../canvas/PeekCanvasConfig.web";

/**
 * Peek Canvas Model Override Canvas Background Color
 *
 * This class manages canvas background color overrides
 *
 */
export class PeekCanvasModelOverrideCanvasBackgroundColor extends PeekCanvasModelOverrideA {
    private activeOverride: DiagramOverrideCanvasBackgroundColor | null = null;

    override appliesToShapes: boolean = false;

    constructor(
        private config: PeekCanvasConfig,
        private lookupCache: PrivateDiagramLookupService,
    ) {
        super();
    }

    // ------------------------------------------------------------------------
    setOverrides(overrides: DiagramOverrideBase[]): void {
        this.activeOverride = null;

        const canvasOverrides: DiagramOverrideCanvasBackgroundColor[] = [];
        for (const overrideBase of overrides) {
            if (
                overrideBase.overrideType !==
                DiagramOverrideTypeE.CanvasBackgroundColor
            )
                continue;

            canvasOverrides.push(<any>overrideBase);
        }

        for (let i = 0; i < canvasOverrides.length - 1; i++) {
            console.log(
                `Canvas background color override skipped: ${canvasOverrides[i].key}`,
            );
        }

        if (canvasOverrides.length > 0) {
            this.activeOverride = canvasOverrides[canvasOverrides.length - 1];
        }
    }

    // ------------------------------------------------------------------------
    override compile(disps: any[]): void {
        if (this.activeOverride != null) {
            const overrideColor = this.config.isLightMode
                ? this.activeOverride.lightBackgroundColor
                : this.activeOverride.darkBackgroundColor;

            if (overrideColor != null) {
                this.config.setCanvasBackgroundColor(overrideColor);
                return;
            }
        }

        // Reset to default behavior if no override is active
        this.config.resetCanvasBackgroundColor();
    }
}
