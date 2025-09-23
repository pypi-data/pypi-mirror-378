import {
    DiagramOverrideBase,
    DiagramOverrideTypeE
} from "./DiagramOverrideBase";
import { addTupleType } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "../_private/PluginNames";

/** Diagram Canvas Background Color Override Tuple
 *
 * This override applies a canvas background color override
 *
 */
@addTupleType
export class DiagramOverrideCanvasBackgroundColor extends DiagramOverrideBase {
    public static readonly tupleName =
        diagramTuplePrefix + "DiagramOverrideCanvasBackgroundColor";

    private darkBackgroundColor_: string | null = null;
    private lightBackgroundColor_: string | null = null;

    constructor() {
        super(
            null,
            null,
            DiagramOverrideTypeE.CanvasBackgroundColor,
            DiagramOverrideCanvasBackgroundColor.tupleName,
        );
    }

    get darkBackgroundColor(): string | null {
        return this.darkBackgroundColor_;
    }

    set darkBackgroundColor(value: string | null) {
        if (value != null && !this.isValidHashColor(value)) {
            throw new Error(`Invalid hash color: ${value}`);
        }
        this.darkBackgroundColor_ = value;
    }

    get lightBackgroundColor(): string | null {
        return this.lightBackgroundColor_;
    }

    set lightBackgroundColor(value: string | null) {
        if (value != null && !this.isValidHashColor(value)) {
            throw new Error(`Invalid hash color: ${value}`);
        }
        this.lightBackgroundColor_ = value;
    }

    private isValidHashColor(color: string): boolean {
        if (!color.startsWith("#")) {
            return false;
        }

        const hex = color.slice(1);

        // Valid hex color lengths: 3 (#RGB), 6 (#RRGGBB), 8 (#RRGGBBAA)
        if (hex.length !== 3 && hex.length !== 6 && hex.length !== 8) {
            return false;
        }

        // Check if all characters are valid hex digits
        return /^[0-9A-Fa-f]+$/.test(hex);
    }
}
