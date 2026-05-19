import importlib
import sys
import types
import unittest
from pathlib import Path
from unittest import mock


BACKEND_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR_STR = str(BACKEND_DIR)
ADDED_BACKEND_PATH = BACKEND_DIR_STR not in sys.path
if ADDED_BACKEND_PATH:
    sys.path.insert(0, BACKEND_DIR_STR)


def _cleanup_import_state():
    sys.modules.pop("routers.medicines", None)
    if ADDED_BACKEND_PATH and BACKEND_DIR_STR in sys.path:
        sys.path.remove(BACKEND_DIR_STR)


unittest.addModuleCleanup(_cleanup_import_state)


class _APIRouter:
    def get(self, *args, **kwargs):
        def decorator(func):
            return func

        return decorator


class _HTTPException(Exception):
    pass


class _BaseModel:
    pass


fastapi_module = types.ModuleType("fastapi")
fastapi_module.APIRouter = _APIRouter
fastapi_module.HTTPException = _HTTPException

pydantic_module = types.ModuleType("pydantic")
pydantic_module.BaseModel = _BaseModel

database_module = types.ModuleType("database")
database_module.supabase = object()

with mock.patch.dict(
    sys.modules,
    {
        "fastapi": fastapi_module,
        "pydantic": pydantic_module,
        "database": database_module,
    },
):
    medicines = importlib.import_module("routers.medicines")


class DefaultLocationCacheTest(unittest.TestCase):
    def setUp(self):
        medicines._fetch_ip_location.cache_clear()

    def test_dependency_stubs_are_scoped_to_import(self):
        self.assertIsNot(sys.modules.get("fastapi"), fastapi_module)
        self.assertIsNot(sys.modules.get("pydantic"), pydantic_module)

    def test_default_location_fetch_is_cached_without_mutable_globals(self):
        response = mock.Mock()
        response.read.return_value = b'{"latitude": 12.34, "longitude": 56.78}'

        with mock.patch.object(medicines.urllib.request, "urlopen") as urlopen:
            urlopen.return_value.__enter__.return_value = response

            self.assertEqual(medicines.get_default_location(), (12.34, 56.78))
            self.assertEqual(medicines.get_default_location(), (12.34, 56.78))

        self.assertEqual(urlopen.call_count, 1)
        self.assertFalse(hasattr(medicines, "LAST_IP_LAT"))
        self.assertFalse(hasattr(medicines, "LAST_IP_LON"))
        self.assertFalse(hasattr(medicines, "IP_FETCHED"))

    def test_default_location_falls_back_without_caching_failure(self):
        response = mock.Mock()
        response.read.return_value = b'{"latitude": 23.45, "longitude": 67.89}'
        successful_lookup = mock.MagicMock()
        successful_lookup.__enter__.return_value = response

        with mock.patch.object(
            medicines.urllib.request,
            "urlopen",
            side_effect=[OSError("network unavailable"), successful_lookup],
        ) as urlopen:
            self.assertEqual(medicines.get_default_location(), medicines.DEFAULT_LOCATION)
            self.assertEqual(medicines.get_default_location(), (23.45, 67.89))

        self.assertEqual(urlopen.call_count, 2)

    def test_default_location_rejects_invalid_coordinates(self):
        response = mock.Mock()
        response.read.return_value = b'{"latitude": 1000, "longitude": 67.89}'

        with mock.patch.object(medicines.urllib.request, "urlopen") as urlopen:
            urlopen.return_value.__enter__.return_value = response

            self.assertEqual(medicines.get_default_location(), medicines.DEFAULT_LOCATION)


if __name__ == "__main__":
    unittest.main()
