import requests
import aiohttp
import asyncio
from datetime import datetime

class PyPi:
    """
    A class to interact with the PyPI API, with support for both synchronous and 
    asynchronous operations. It automatically detects the execution environment.
    """
    def __init__(self):
        self.base_url = "https://pypi.org/pypi/"

    def _is_async(self):
        """Checks if we are running in an asynchronous event loop."""
        try:
            # This will raise a RuntimeError if no loop is running.
            asyncio.get_running_loop()
            return True
        except RuntimeError:
            return False

    # ------------------- Core Method -------------------
    def get_package_info(self, package_name):
        """Returns package information based on the sync or async environment."""
        if self._is_async():
            return self._get_package_info_async(package_name)
        else:
            return self._get_package_info_sync(package_name)

    def _get_package_info_sync(self, package_name):
        """Fetches package information synchronously."""
        url = f"{self.base_url}{package_name}/json"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise ValueError(f"Package '{package_name}' not found or an error occurred.")

    async def _get_package_info_async(self, package_name):
        """Fetches package information asynchronously."""
        url = f"{self.base_url}{package_name}/json"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise ValueError(f"Package '{package_name}' not found or an error occurred.")

    # ------------------- Wrapper Methods -------------------
    def __wrap_sync_async(self, method_sync, method_async, *args, **kwargs):
        """Internal helper to call the correct sync/async method."""
        if self._is_async():
            return method_async(*args, **kwargs)
        else:
            return method_sync(*args, **kwargs)

    def get_releases(self, package_name):
        """Gets all release versions for a given package."""
        return self.__wrap_sync_async(
            self._get_releases_sync,
            self._get_releases_async,
            package_name
        )

    def is_package_updated(self, package_name):
        """Checks if the package has been updated in the last 30 days."""
        return self.__wrap_sync_async(
            self._is_package_updated_sync,
            self._is_package_updated_async,
            package_name
        )

    def show_package_author_info(self, package_name):
        """Retrieves the author's name and email for a given package."""
        return self.__wrap_sync_async(
            self._show_package_author_info_sync,
            self._show_package_author_info_async,
            package_name
        )

    def show_last_update_date(self, package_name):
        """Shows the date of the last update for a given package."""
        return self.__wrap_sync_async(
            self._show_last_update_date_sync,
            self._show_last_update_date_async,
            package_name
        )

    def get_popular_packages(self, limit=10):
        """
        Fetches a list of popular packages. 
        Note: This scrapes the HTML from pypi.org/stats/ and may be unstable.
        """
        return self.__wrap_sync_async(
            self._get_popular_packages_sync,
            self._get_popular_packages_async,
            limit
        )

    def get_package_url(self, package_name):
        """Gets the homepage URL for a given package."""
        return self.__wrap_sync_async(
            self._get_package_url_sync,
            self._get_package_url_async,
            package_name
        )

    def get_first_release_date(self, package_name):
        """
        Finds the upload date of the first release.
        Note: This assumes the first version is '0.1', which may not always be correct.
        """
        return self.__wrap_sync_async(
            self._get_first_release_date_sync,
            self._get_first_release_date_async,
            package_name
        )

    def check_package_status(self, package_name):
        """Checks if a package exists on PyPI."""
        return self.__wrap_sync_async(
            self._check_package_status_sync,
            self._check_package_status_async,
            package_name
        )

    # ------------------- Sync Implementations -------------------
    def _get_releases_sync(self, package_name):
        info = self._get_package_info_sync(package_name)
        return {"releases": list(info.get('releases', {}).keys())}

    def _is_package_updated_sync(self, package_name):
        info = self._get_package_info_sync(package_name)
        releases = info.get('releases', {})
        if not releases:
            return {"is_updated": False}
        latest_version = sorted(releases.keys(), reverse=True)[0]
        last_updated_str = releases.get(latest_version, [])[0].get('upload_time')
        last_updated_datetime = datetime.strptime(last_updated_str, "%Y-%m-%dT%H:%M:%S")
        return {"is_updated": (datetime.now() - last_updated_datetime).days <= 30}

    def _show_package_author_info_sync(self, package_name):
        info = self._get_package_info_sync(package_name).get('info', {})
        return {
            "author": info.get('author', 'Unknown'),
            "author_email": info.get('author_email', 'Unknown')
        }

    def _show_last_update_date_sync(self, package_name):
        info = self._get_package_info_sync(package_name)
        releases = info.get('releases', {})
        if not releases:
            return {"last_update_date": "Not available"}
        latest_version = sorted(releases.keys(), reverse=True)[0]
        last_updated_str = releases.get(latest_version, [])[0].get('upload_time')
        return {"last_update_date": datetime.strptime(last_updated_str, "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")}

    def _get_popular_packages_sync(self, limit=10):
        # This method is brittle as it relies on scraping.
        response = requests.get("https://pypi.org/stats/")
        if response.status_code == 200:
            # A real implementation should parse the HTML, not return it raw.
            # This is kept as-is to match the original code's behavior.
            return {"popular_packages": response.text}
        else:
            raise ValueError("Error fetching popular packages.")

    def _get_package_url_sync(self, package_name):
        info = self._get_package_info_sync(package_name).get('info', {})
        return {"home_page": info.get('home_page', 'Homepage not available.')}

    def _get_first_release_date_sync(self, package_name):
        info = self._get_package_info_sync(package_name)
        first_release = info.get('releases', {}).get('0.1', [])
        if first_release:
            first_release_date_str = first_release[0].get('upload_time')
            return {"first_release_date": datetime.strptime(first_release_date_str, "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")}
        return {"first_release_date": "First release date for version '0.1' not available."}

    def _check_package_status_sync(self, package_name):
        try:
            self._get_package_info_sync(package_name)
            return {"status": True}
        except ValueError:
            return {"status": False}

    # ------------------- Async Implementations -------------------
    async def _get_releases_async(self, package_name):
        info = await self._get_package_info_async(package_name)
        return {"releases": list(info.get('releases', {}).keys())}

    async def _is_package_updated_async(self, package_name):
        info = await self._get_package_info_async(package_name)
        releases = info.get('releases', {})
        if not releases:
            return {"is_updated": False}
        latest_version = sorted(releases.keys(), reverse=True)[0]
        last_updated_str = releases.get(latest_version, [])[0].get('upload_time')
        last_updated_datetime = datetime.strptime(last_updated_str, "%Y-%m-%dT%H:%M:%S")
        return {"is_updated": (datetime.now() - last_updated_datetime).days <= 30}

    async def _show_package_author_info_async(self, package_name):
        info = (await self._get_package_info_async(package_name)).get('info', {})
        return {
            "author": info.get('author', 'Unknown'),
            "author_email": info.get('author_email', 'Unknown')
        }

    async def _show_last_update_date_async(self, package_name):
        info = await self._get_package_info_async(package_name)
        releases = info.get('releases', {})
        if not releases:
            return {"last_update_date": "Not available"}
        latest_version = sorted(releases.keys(), reverse=True)[0]
        last_updated_str = releases.get(latest_version, [])[0].get('upload_time')
        return {"last_update_date": datetime.strptime(last_updated_str, "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")}

    async def _get_popular_packages_async(self, limit=10):
        # This method is brittle as it relies on scraping.
        async with aiohttp.ClientSession() as session:
            async with session.get("https://pypi.org/stats/") as response:
                if response.status == 200:
                    # A real implementation should parse the HTML, not return it raw.
                    return {"popular_packages": await response.text()}
                else:
                    raise ValueError("Error fetching popular packages.")

    async def _get_package_url_async(self, package_name):
        info = (await self._get_package_info_async(package_name)).get('info', {})
        return {"home_page": info.get('home_page', 'Homepage not available.')}

    async def _get_first_release_date_async(self, package_name):
        info = await self._get_package_info_async(package_name)
        first_release = info.get('releases', {}).get('0.1', [])
        if first_release:
            first_release_date_str = first_release[0].get('upload_time')
            return {"first_release_date": datetime.strptime(first_release_date_str, "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")}
        return {"first_release_date": "First release date for version '0.1' not available."}

    async def _check_package_status_async(self, package_name):
        try:
            await self._get_package_info_async(package_name)
            return {"status": True}
        except ValueError:
            return {"status": False}