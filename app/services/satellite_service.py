"""
Спутниковый сервис — NASA GIBS (бесплатно) + Planet (если есть ключ).
"""
import logging
from typing import Any, Dict, Optional

import aiohttp

logger = logging.getLogger("aurion-satellite")

# NASA GIBS — бесплатный тайловый сервис без ключа
NASA_GIBS_BASE = "https://gibs.earthdata.nasa.gov/wmts/epsg4326/best"
NASA_LAYER = "MODIS_Terra_CorrectedReflectance_TrueColor"


class SatelliteService:
    def __init__(self, planet_api_key: str = "") -> None:
        self.planet_api_key = planet_api_key

    async def get_imagery_url(
        self,
        lat: float,
        lon: float,
        zoom: int = 6,
        date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Возвращает URL тайла спутникового снимка.
        Основной источник — NASA GIBS (бесплатно).
        Если задан PLANET_API_KEY — добавляет ссылку на Planet.
        """
        # Конвертируем lat/lon/zoom в тайловые координаты (TMS)
        tile_x, tile_y = self._latlon_to_tile(lat, lon, zoom)

        nasa_url = (
            f"{NASA_GIBS_BASE}/{NASA_LAYER}/default/"
            f"{date or '2024-01-01'}/250m/{zoom}/{tile_y}/{tile_x}.jpg"
        )

        result: Dict[str, Any] = {
            "source": "NASA GIBS",
            "layer": NASA_LAYER,
            "url": nasa_url,
            "lat": lat,
            "lon": lon,
            "zoom": zoom,
            "tile_x": tile_x,
            "tile_y": tile_y,
        }

        # Planet — если есть ключ
        if self.planet_api_key:
            result["planet_available"] = True
            result["planet_search_url"] = (
                f"https://api.planet.com/data/v1/quick-search"
                f"?lat={lat}&lon={lon}"
            )
        else:
            result["planet_available"] = False

        return result

    async def verify_nasa_available(self) -> bool:
        """Проверяет доступность NASA GIBS."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(
                    NASA_GIBS_BASE,
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as resp:
                    return resp.status < 500
        except Exception:
            return False

    @staticmethod
    def _latlon_to_tile(lat: float, lon: float, zoom: int) -> tuple[int, int]:
        """Простая конвертация координат в тайловые индексы."""
        import math
        n = 2 ** zoom
        tile_x = int((lon + 180.0) / 360.0 * n)
        lat_rad = math.radians(lat)
        tile_y = int((1.0 - math.log(math.tan(lat_rad) + 1.0 / math.cos(lat_rad)) / math.pi) / 2.0 * n)
        return tile_x, tile_y


def get_satellite_service() -> SatelliteService:
    from ..config import settings
    return SatelliteService(planet_api_key=settings.PLANET_API_KEY)
