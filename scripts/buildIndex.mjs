import path from "path";
import fs from "fs";
import vendors from "../src/vendors.js";
import caliberTagMapping from "../src/possibleCalibers.js";
import { decode } from "a7p-js";

const galleryPath = "gallery";
const excludeUnvalidated = path.join(galleryPath, ".unvalidated");
const indexPath = "public/profiles.json";
const assetsDir = path.dirname(indexPath);


async function parseA7P(filePath) {
    try {
        const fileBuffer = fs.readFileSync(filePath);
        const profile = decode(fileBuffer);
        return profile;
    } catch (error) {
        throw new Error(`Error parsing A7P file: ${filePath} ${error.message}`);
    }
}

const asPosix = (filePath) => {
    return path.posix.join(...filePath.split(path.sep));
};

const getFilteredTree = (dir, criteria) => {
    const result = [];

    const items = fs.readdirSync(dir, { withFileTypes: true });
    for (const item of items) {
        const fullPath = path.join(dir, item.name);

        if (item.isDirectory()) {
            // Recursively process the directory
            const children = getFilteredTree(fullPath, criteria);
            if (children.length > 0 || criteria(fullPath)) {
                result.push({
                    type: "directory",
                    name: item.name,
                    path: fullPath,
                    children,
                });
            }
        } else if (item.isFile() && criteria(fullPath)) {
            // Add the file if it matches the criteria
            result.push({
                type: "file",
                name: item.name,
                path: fullPath,
            });
        }
    }

    return result;
};

const extractFilePaths = (tree) => {
    const filePaths = [];

    for (const node of tree) {
        if (node.type === "file") {
            filePaths.push(node.path); // Add file path to the array
        } else if (node.type === "directory" && node.children) {
            filePaths.push(...extractFilePaths(node.children));
        }
    }

    return filePaths;
};

const resolveCaliber = (caliber, diameter) => {
    const keys = Object.keys(caliberTagMapping).map((item) =>
        item.toUpperCase(),
    );
    try {
        if (keys.includes(caliber.toUpperCase())) {
            if (caliberTagMapping[caliber]?.length === 1) {
                return caliberTagMapping[caliber][0];
            }
        }
        return caliber;
    } catch (error) {
        console.log(error);
    }
};

const resolveVendor = (vendor, filePath = "") => {
    const vendorUpper = vendor.toUpperCase();
    const words = vendorUpper.split(" ");

    let resolved = undefined; // Changed to `let`
    for (const word of words) {
        resolved = vendors[word]; // Assigning value to `resolved`
        if (resolved) {
            return resolved;
        }
    }

    const vendorKeys = Object.keys(vendors);
    for (const key of vendorKeys) {
        if (vendorUpper.includes(key)) {
            return vendorKeys[key];
        }
    }

    for (const key of vendorKeys) {
        if (filePath.includes(key)) {
            return vendorKeys[key];
        }
    }

    console.log("Undefined vendor", vendor, filePath);
    return resolved ?? null;
};

// Function to collect unique values for a given key
const collectUniqueValues = (data, key) => {
    return [
        ...new Set(
            data.map((item) =>
                item[key] != null
                    ? typeof item[key] === "string"
                        ? item[key].trim()
                        : item[key]
                    : undefined,
            ),
        ).values(),
    ].filter((value) => value != null); // Filter out null and undefined
};

const mergeProfilesIndex = ({ prevProfilesIndex, profilesIndex }) => {
    const mergedProfilesIndex = [];
    profilesIndex.map((cur) => {
        const found = prevProfilesIndex.find(
            (item) => item?.path === cur?.path,
        );
        if (found) {
            const prevIdx = prevProfilesIndex.indexOf(found);
            mergedProfilesIndex.push({
                ...cur,
                meta: { ...cur?.meta, ...prevProfilesIndex[prevIdx].meta },
            });
        } else {
            mergedProfilesIndex.push(cur);
        }
    });
    return mergedProfilesIndex;
};

const createIndex = async () => {
    const profilesIndex = [];

    // Filter criteria: Include only JavaScript and Markdown files
    const criteria = (filePath) => [".a7p"].includes(path.extname(filePath));

    // Get the filtered tree
    const filteredTree = getFilteredTree(galleryPath, criteria);
    console.log(filteredTree)
    const flatFilePaths = extractFilePaths(filteredTree);
    // const validFilePaths = flatFilePaths.filter(filePath => !asPosix(filePath).startsWith(excludeUnvalidated))
    const validFilePaths = flatFilePaths.filter(
        (filePath) =>
            !asPosix(filePath).startsWith(asPosix(excludeUnvalidated)),
    );

    // Use Promise.all to wait for all asynchronous parseA7P operations to finish
    const parsePromises = validFilePaths.map((filePath, index) =>
        parseA7P(filePath, true)
            .then((result) => {
                // console.log(result.profile);
                const normalizedPath = path
                    .normalize(filePath)
                    .replace(/\\/g, "/")
                    .split("/");
                const finalPath = normalizedPath
                    .slice(normalizedPath.indexOf("gallery"))
                    .join("/");

                if (result && result.profile) {
                    const profile = result?.profile;
                    profilesIndex.push({
                        id: index,
                        diameter: profile.bDiameter / 1000,
                        weight: profile.bWeight / 10,
                        caliber: resolveCaliber(
                            profile.caliber,
                            profile.bDiameter / 1000,
                        ),
                        path: finalPath,
                        profileName: profile.profileName,
                        name: `${profile.caliber} ${profile.cartridgeName} ${profile.bulletName}`,
                        cartridge: profile.cartridgeName,
                        bullet: profile.bulletName,
                        cartridgeVendor: resolveVendor(
                            profile.cartridgeName,
                            filePath,
                        ),
                        bulletVendor: resolveVendor(profile.bulletName),
                        dragModelType: profile.bcType,
                        meta: {
                            productName: "",
                            vendor: "",
                            bulletVendor: "",
                            caliber: "",
                            muzzle_velocity: null,
                            bc: null,
                            g7: null,
                            bulletType: "",
                            weight: null,
                            country: "",
                            url: null,
                            // downloadUrl: null,
                        },
                    });
                } else {
                    throw new Error(`Error on file: ${filePath}`);
                }
            })
            .catch((error) => console.error(`Error on file: ${filePath}`)),
    );

    try {
        await Promise.all(parsePromises);
        let prevProfilesIndex = [];
        try {
            const fileData = fs.readFileSync(indexPath, "utf8");
            const fileJsonData = JSON.parse(fileData);
            prevProfilesIndex = fileJsonData.profiles || [];
        } catch {
            console.log("Error load lastIndex");
        }

        const mergedIndex = mergeProfilesIndex({
            prevProfilesIndex,
            profilesIndex,
        });
        const mergedMeta = mergedIndex.map((item) => item.meta);

        const outputData = {
            profiles: mergedIndex,
            uniqueKeys: {
                calibers: collectUniqueValues(mergedMeta, "caliber"),
                diameters: collectUniqueValues(mergedIndex, "diameter"),
                bulletVendors: collectUniqueValues(mergedMeta, "bulletVendor"),
                cartridgeVendors: collectUniqueValues(mergedMeta, "vendor"),
            },
        };

        const jsonString = JSON.stringify(outputData, null, 2);

        fs.mkdirSync(assetsDir, { recursive: true });
        fs.writeFileSync(indexPath, jsonString, "utf8");

        console.log("Files saved successfully!");

        console.log("Profiles updated:", validFilePaths.length);
    } catch (error) {
        console.error(`Error during parsing: ${error.message}`);
    }

    // Wait for all parsing operations to finish
    // Promise.all(parsePromises)
    //     .then(() => {
    //         // After all promises are resolved, save the file

    //         let prevProfilesIndex = [];
    //         try {
    //             const fileData = JSON.parse(fs.readFileSync(indexPath, 'utf8'));
    //             prevProfilesIndex = fileData?.profiles || [];
    //         } catch {
    //             console.log("Error load lastIndex")
    //         }
    //         console.log(prevProfilesIndex)
    //         const outputData = {
    //             profiles: mergeProfilesIndex(prevProfilesIndex, profileIndex),
    //             uniqueKeys: {
    //                 calibers: collectUniqueValues(profileIndex, 'caliber'),
    //                 diameters: collectUniqueValues(profileIndex, 'diameter'),
    //                 bulletVendors: collectUniqueValues(profileIndex, 'bulletVendor'),
    //                 cartridgeVendors: collectUniqueValues(profileIndex, 'cartridgeVendor')
    //             }
    //         }

    //         const jsonString = JSON.stringify(outputData, null, 2);

    //         fs.mkdirSync(assetsDir, { recursive: true });
    //         fs.writeFileSync(indexPath, jsonString, 'utf8');

    //         console.log('Files saved successfully!');

    //         console.log("Profiles updated:", validFilePaths.length)
    //     })
    //     .catch(error => {
    //         console.error('Error during parsing:', error.message);
    //     });
};

createIndex();