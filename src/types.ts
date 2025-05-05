
interface Stringer {
    toString(): string;
}

type ExtraFields = Record<string, Stringer>

type ProfileMeta = {
    name?: string | null;
    productName?: string | null;
    caliber?: string | null;
    bulletType?: string | null;
    bulletVendor?: string | null;
    cartridge?: string | null;
    cartridgeVendor?: string | null;
    url?: string | null;
    country?: string | null;
    bc?: number | null;
    g7?: number | null;
    weight?: number | null;
    muzzleVelocity?: number | null;
    author?: string | null;
    note?: string | null;
    path?: string | null;
    extra?: ExtraFields | null;
}

type ProfileIndex = {
    id: number;
    path: string,
    diameter?: number | null;
    weight?: number | null;
    length?: number | null;
    muzzleVelocity?: string | null;
    dragModelType?: "G1" | "G7" | "CUSTOM";
    meta?: ProfileMeta | null;
}
