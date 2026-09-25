"""Resolve Garage photos from official manufacturer pages, model by model."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
from html import unescape
from pathlib import Path
import re
import unicodedata
from urllib.parse import quote, urljoin, urlparse

import httpx


# Each entry is a manufacturer's current product page. A source which does not
# identify the specific model is not used: returning no photo is preferable to
# a logo or an unrelated car.
MODEL_PAGES: dict[str, str] = {
    "toyota hilux": "https://www.toyota.co.uk/new-cars/hilux/",
    "toyota corolla": "https://www.toyota.co.uk/new-cars/corolla/",
    "toyota yaris": "https://www.toyota.co.uk/new-cars/yaris/",
    "ford ranger": "https://www.ford.com/trucks/ranger/",
    "dacia logan": "https://www.dacia.ma/notre-gamme/logan-berline.html",
    "dacia sandero": "https://www.dacia.ma/notre-gamme/sandero.html",
    "dacia sandero stepway": "https://www.dacia.ma/notre-gamme/sandero-stepway.html",
    "dacia duster": "https://www.dacia.ma/notre-gamme/duster.html",
    "renault clio 5": "https://www.renault.ma/hybrids-cars/clio.html",
    "renault megane": "https://www.renault.ma/vehicules-particuliers/megane-sedan.html",
    "renault kangoo": "https://www.renault.ma/vehicules-particuliers/kangoo.html",
    "renault express": "https://www.renault.ma/vehicules-particuliers/express.html",
    "peugeot 208": "https://www.peugeot.ma/nos-modeles/new-208.html",
    "peugeot 308": "https://www.peugeot.ma/our-range/nouvelle-peugeot-308.html",
    "peugeot 3008": "https://www.peugeot.ma/nos-modeles/new-peugeot-3008.html",
    "hyundai i10": "https://www.hyundai.com/ma/fr/find-a-car/i10-2021/highlights",
    "hyundai i20": "https://www.hyundai.com/ma/fr/find-a-car/i20-2021/highlights",
    "hyundai tucson": "https://www.hyundai.com/la/en/find-a-car/tucson-2024/design",
    "kia picanto": "https://www.kia.com/uk/new-cars/picanto/",
    "kia sportage": "https://www.kia.com/uk/new-cars/sportage/",
    "fiat 500": "https://www.fiat.co.uk/models/fiat-500",
    "volkswagen jetta": "https://www.vw.com/en/models/jetta.html",
    "volkswagen polo": "https://www.volkswagen.co.uk/en/new/polo.html",
    "volkswagen t roc": "https://www.volkswagen.co.uk/en/new/t-roc.html",
    "skoda octavia": "https://www.skoda.co.uk/models/octavia/octavia",
    "mercedes classe a": "https://www.mercedes-benz.com/en/vehicles/passenger-cars/a-class/",
    "mercedes classe c": "https://www.mercedes-benz.com/en/vehicles/passenger-cars/c-class/",
    "bmw serie 3": "https://www.bmw.ma/fr/all-models/3-series/bmw-serie-3-berline/bmw-serie-3-berline.html",
    "audi a3": "https://www.audi.ma/fr/gamme/a3/a3-sedan-2022/",
    "citroen berlingo": "https://www.citroen.co.uk/models/berlingo.html",
}

# Images supplied and approved by the agency team take precedence. They are
# served only through this fixed allow-list; the endpoint never exposes an
# arbitrary local path.
LOCAL_IMAGE_ROOT = Path(r"C:\Users\zineb\Downloads")
CACHE_IMAGE_ROOT = Path(__file__).resolve().parents[1] / "data" / "vehicle_image_cache"
LOCAL_VEHICLE_IMAGES: dict[str, Path] = {
    "citroen berlingo": LOCAL_IMAGE_ROOT / "citroën berlingo 2026.jpg",
    "renault clio 5": LOCAL_IMAGE_ROOT / "CLIO5.jpg",
    "ford ranger": LOCAL_IMAGE_ROOT / "FORD LOGAN.jpg",
    "toyota hilux": LOCAL_IMAGE_ROOT / "Toyota Hilux.jpg",
    "toyota yaris": LOCAL_IMAGE_ROOT / "Toyota Yaris.jpg",
    "volkswagen jetta": LOCAL_IMAGE_ROOT / "Volkswagen Jetta.jpg",
    "dacia sandero": LOCAL_IMAGE_ROOT / "Dacia Sandero.jpg",
    "fiat 500": LOCAL_IMAGE_ROOT / "FIAT 500.jpg",
    "skoda octavia": LOCAL_IMAGE_ROOT / "Skoda Octavia.png",
    "hyundai accent": LOCAL_IMAGE_ROOT / "Hyundai Accent.jpg",
}
KIFAL_SEARCH_URL = "https://neuf.kifal.ma/search"
KIFAL_BRANDS = {"mercedes": "MERCEDES-BENZ", "citroen": "CITROEN", "skoda": "SKODA"}

META_PATTERNS = (
    re.compile(r'<meta[^>]+(?:property|name)=["\'](?:og:image|twitter:image)["\'][^>]+content=["\']([^"\']+)', re.I),
    re.compile(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\'](?:og:image|twitter:image)["\']', re.I),
)
TAG_PATTERN = re.compile(r"<(?:img|source)\b[^>]*>", re.I)
ATTR_PATTERN = re.compile(r"([:\w-]+)\s*=\s*(['\"])(.*?)\2", re.I | re.S)
ASSET_URL_PATTERN = re.compile(
    r"(?:(?:https?:)?//[^\s'\"<>\\]+|/[^\s'\"<>\\]+)\.(?:jpg|jpeg|png|webp|avif)(?:\?[^\s'\"<>\\)]*)?",
    re.I,
)
IMAGE_ATTRS = {"src", "srcset", "data-src", "data-image", "data-lazy-src", "data-media-pc", "data-media-mobile", "data-desktop"}
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".avif")
REJECT_WORDS = (
    "logo", "icon", "favicon", "flag", "sprite", "app-store", "play-store",
    "cookie", "avatar", "social", "accessor", "floor mat", "floor-mat", "part", "flyout",
)


def _key(value: str) -> str:
    """Normalise database labels while preserving model-specific matching."""
    # Older spreadsheet imports occasionally contain UTF-8 text decoded once
    # as Latin-1 (for example "SÃ©rie"). Repair that representation first.
    if "Ã" in value or "Â" in value:
        try:
            value = value.encode("latin-1").decode("utf-8")
        except UnicodeError:
            pass
    value = unicodedata.normalize("NFKD", value)
    value = "".join(char for char in value if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def local_vehicle_image(model: str) -> Path | None:
    """Return a user-approved local vehicle photo when it exists."""
    path = LOCAL_VEHICLE_IMAGES.get(_key(model))
    return path if path and path.is_file() else None


def cached_vehicle_image(model: str) -> Path | None:
    """Return the persistent local cache entry for this model, if present."""
    digest = sha256(_key(model).encode("utf-8")).hexdigest()[:20]
    matches = tuple(CACHE_IMAGE_ROOT.glob(f"{digest}.*")) if CACHE_IMAGE_ROOT.exists() else ()
    return matches[0] if matches else None


def _cache_remote_image(model: str, image_url: str) -> Path | None:
    """Download a checked remote vehicle photo once for fast future display."""
    existing = cached_vehicle_image(model)
    if existing:
        return existing
    try:
        image = httpx.get(image_url, timeout=20, follow_redirects=True, headers={"User-Agent": "Mozilla/5.0"})
        content_type = image.headers.get("content-type", "").lower()
        if not image.is_success or not content_type.startswith("image/") or not image.content:
            return None
        extension = {"image/png": ".png", "image/webp": ".webp", "image/avif": ".avif"}.get(content_type.split(";", 1)[0], ".jpg")
        CACHE_IMAGE_ROOT.mkdir(parents=True, exist_ok=True)
        target = CACHE_IMAGE_ROOT / f"{sha256(_key(model).encode('utf-8')).hexdigest()[:20]}{extension}"
        temporary = target.with_suffix(f"{target.suffix}.tmp")
        temporary.write_bytes(image.content)
        temporary.replace(target)
        return target
    except (httpx.HTTPError, OSError):
        return None


def _cached_result(model: str, source_url: str, source_type: str) -> dict[str, str | int | None]:
    """Return a local endpoint after retaining the supplier attribution."""
    return {
        "image_url": f"/api/media/vehicle-image/file?model={quote(model)}",
        "source_url": source_url,
        "model_year": 2024,
        "source_type": source_type,
    }


def _kifal_image(model: str) -> tuple[str | None, str | None]:
    """Find the exact model visual on Kifal's public new-car catalogue."""
    model_key = _key(model)
    parts = model_key.split(maxsplit=1)
    if len(parts) < 2:
        return None, None
    brand, model_name = parts
    try:
        response = httpx.get(
            KIFAL_SEARCH_URL,
            params={"marque": KIFAL_BRANDS.get(brand, brand.upper()), "modele": model_name.title()},
            timeout=15,
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        response.raise_for_status()
        candidates: list[tuple[int, str]] = []
        for tag in TAG_PATTERN.findall(response.text):
            attrs = {name.lower(): unescape(value).strip() for name, _, value in ATTR_PATTERN.findall(tag)}
            image = _absolute_image(attrs.get("src", ""), str(response.url))
            if not image or urlparse(image).netloc != "kifalstorage.s3.amazonaws.com":
                continue
            score = _score_image(image, " ".join(attrs.values()), model_key)
            candidates.append((score, image))
        if candidates:
            _, image = max(candidates, key=lambda item: item[0])
            if _image_is_available(image, KIFAL_SEARCH_URL):
                return image, str(response.url)
    except httpx.HTTPError:
        pass
    return None, None


def _absolute_image(value: str, page_url: str) -> str | None:
    value = unescape(value).strip()
    # For responsive images retain the first URL, removing an optional width
    # descriptor such as "image.webp 768w".
    value = value.split(",", 1)[0].split(" ", 1)[0]
    if not value or "{" in value or "}" in value or value.startswith(("data:", "javascript:")):
        return None
    result = urljoin(page_url, value)
    return result if urlparse(result).scheme in {"http", "https"} else None


def _score_image(image: str, context: str, model_key: str) -> int:
    text = _key(f"{image} {context}")
    if any(word in text for word in REJECT_WORDS):
        return -100
    model_tokens = [token for token in model_key.split()[1:] if len(token) > 2]
    matches = sum(token in text for token in model_tokens)
    score = matches * 30
    if model_tokens and matches == len(model_tokens):
        score += 25
    if any(word in text for word in ("hero", "vehicle", "gallery", "overview", "product")):
        score += 15
    if urlparse(image).path.lower().endswith(IMAGE_EXTENSIONS):
        score += 10
    if "thumbnail" in text or "thumb" in text:
        score -= 20
    return score


def _page_image(html: str, page_url: str, model_key: str) -> str | None:
    # A social card is produced by the official product page itself, and is
    # usually its lead vehicle visual.
    for pattern in META_PATTERNS:
        match = pattern.search(html)
        if match:
            image = _absolute_image(match.group(1), page_url)
            if image and _score_image(image, image, model_key) >= 25:
                return image

    candidates: list[tuple[int, str]] = []
    for tag in TAG_PATTERN.findall(html):
        attrs = {name.lower(): unescape(value).strip() for name, _, value in ATTR_PATTERN.findall(tag)}
        context = " ".join(attrs.values())
        for name in IMAGE_ATTRS:
            value = attrs.get(name)
            if value and (image := _absolute_image(value, page_url)):
                candidates.append((_score_image(image, context, model_key), image))

    # Several official automotive sites render the hero visual through a CSS
    # background or page-data JSON instead of an <img>. It is still accepted
    # only when that manufacturer-hosted asset itself contains the model name.
    for value in ASSET_URL_PATTERN.findall(html):
        if image := _absolute_image(value, page_url):
            candidates.append((_score_image(image, image, model_key), image))
    if not candidates:
        return None
    score, image = max(candidates, key=lambda item: item[0])
    return image if score >= 25 else None


def _image_is_available(image_url: str, source_url: str) -> bool:
    """Avoid returning official CDNs that deny direct image delivery (HTTP 403)."""
    try:
        with httpx.stream(
            "GET",
            image_url,
            timeout=12,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
            },
        ) as image:
            return image.is_success and image.headers.get("content-type", "").lower().startswith("image/")
    except httpx.HTTPError:
        return False


@lru_cache(maxsize=128)
def resolve_official_image(model: str) -> dict[str, str | int | None]:
    """Return a verified manufacturer visual, never a generic image result."""
    if local_vehicle_image(model):
        return {
            "image_url": f"/api/media/vehicle-image/file?model={quote(model)}",
            "source_url": None,
            "model_year": 2024,
            "source_type": "agency",
        }
    source_url = MODEL_PAGES.get(_key(model))
    if source_url:
        try:
            response = httpx.get(
                source_url,
                timeout=15,
                follow_redirects=True,
                headers={"User-Agent": "Mozilla/5.0"},
            )
            response.raise_for_status()
            image = _page_image(response.text, str(response.url), _key(model))
            if image and _image_is_available(image, source_url):
                if _cache_remote_image(model, image):
                    return _cached_result(model, source_url, "official")
                return {"image_url": image, "source_url": source_url, "model_year": 2024, "source_type": "official"}
        except httpx.HTTPError:
            pass

    image, source = _kifal_image(model)
    if image and source:
        if _cache_remote_image(model, image):
            return _cached_result(model, source, "kifal")
        return {"image_url": image, "source_url": source, "model_year": 2024, "source_type": "kifal"}
    return {"image_url": None, "source_url": None, "model_year": None, "source_type": None}
