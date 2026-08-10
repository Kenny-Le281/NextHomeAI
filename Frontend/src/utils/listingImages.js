export const NO_IMAGE_URL = "https://placehold.co/900x500?text=No+Image";

function uniqueStrings(values) {
  return [...new Set(values.filter((value) => typeof value === "string" && value.trim()))];
}

export function getListingImages(listing) {
  if (Array.isArray(listing?.image_urls)) {
    return uniqueStrings(listing.image_urls);
  }

  if (Array.isArray(listing?.photos)) {
    return uniqueStrings(listing.photos);
  }

  const singleImage =
    listing?.main_image ||
    listing?.image_url ||
    listing?.photo_url ||
    null;

  return singleImage ? [singleImage] : [];
}

function getImageCandidates(url) {
  const candidates = [url];

  try {
    const parsedUrl = new URL(url);
    if (!parsedUrl.hostname.endsWith("cdn-redfin.com")) {
      return candidates;
    }

    const match = parsedUrl.pathname.match(
      /^(.*_)(\d+)(\.(?:jpe?g|png|webp))$/i,
    );
    if (!match) {
      return candidates;
    }

    const currentVersion = Number(match[2]);
    for (let distance = 1; distance <= 6; distance += 1) {
      for (const version of [currentVersion + distance, currentVersion - distance]) {
        if (version < 1) continue;

        const candidateUrl = new URL(parsedUrl);
        candidateUrl.pathname = `${match[1]}${version}${match[3]}`;
        candidates.push(candidateUrl.toString());
      }
    }
  } catch {
    // The original URL will fail validation and be removed below.
  }

  return uniqueStrings(candidates);
}

function canLoadImage(url) {
  return new Promise((resolve) => {
    const image = new Image();
    image.onload = () => resolve(true);
    image.onerror = () => resolve(false);
    image.src = url;
  });
}

async function resolveImage(url) {
  const candidates = getImageCandidates(url);

  for (const candidate of candidates) {
    if (await canLoadImage(candidate)) {
      return candidate;
    }
  }

  return null;
}

export async function resolveListingImages(images) {
  const resolved = await Promise.all(uniqueStrings(images).map(resolveImage));
  return uniqueStrings(resolved);
}

export async function resolveFirstListingImage(images) {
  for (const image of uniqueStrings(images)) {
    const resolved = await resolveImage(image);
    if (resolved) return resolved;
  }

  return null;
}
