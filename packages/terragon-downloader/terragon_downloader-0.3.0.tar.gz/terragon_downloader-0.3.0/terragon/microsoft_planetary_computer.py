import shutil
from typing import Union

import odc.stac
import planetary_computer as pc
import pystac_client
import requests
import xarray as xr
from joblib import Parallel, delayed

from .base import Base
from .utils import filter_stac_collections, gather_assign_meta, meters_to_crs_unit


class PC(Base):
    """The class for Microsoft Planetary Computer downloads. The package odc-stac will be used to download the images.

    :param Base: Base class defining the interface and some common methods
    :param credentials: credentials to authenticate, expected format: {'api_key': <key>}, defaults to None
    :param base_url: the URL for the STAC catalog, defaults to "https://planetarycomputer.microsoft.com/api/stac/v1/"
    """

    def __init__(
        self,
        credentials: dict = None,
        base_url: str = "https://planetarycomputer.microsoft.com/api/stac/v1/",
    ) -> None:
        """Initialize class and planetary computer, if credentials are provided.

        :param credentials: credentials to authenticate, expected format: {'api_key': <key>}, defaults to None
        :param base_url: the URL for the STAC catalog, defaults to "https://planetarycomputer.microsoft.com/api/stac/v1/"
        :raises ValueError: when the credentials are in the wrong format
        """
        super().__init__()
        self._base_url = base_url
        if credentials:
            if "api_key" not in credentials:
                raise ValueError("api_key not in credentials, could not initialize PC.")
            pc.set_subscription_key(credentials["api_key"])

    def retrieve_collections(self, query: dict = {}, fields: list[str] = []) -> list:
        """Search the collections provided by Microsoft Planetary Computer.

        :param query: query to filter the collections for in style '{<key>:<regex>}', defaults to {}
        :param fields: list of fields to include in the response, defaults to []
        :return: a list of dictionaries with collection metadata
        """
        catalog = pystac_client.Client.open(self._base_url)

        return filter_stac_collections(catalog, query, fields)

    def search(self, odc_stac_kwargs={}, *args, **kwargs):
        """Search for items in the Planetary Computer collections, return the items and their meta data,
        and store the parameters in the class in order to access them later in the download function.
        For a description of the args/kwargs parameters see the Base class function.

        :param odc_stac_kwargs: additional parameters for the odc.stac.load function, defaults to {}
        :param args/kwargs: Parameters which are handled by the parent class, these parameters are the same for all data providers. See the 'Base' class for more information.
        :raises ValueError: when no items are found or parameters are in the wrong format
        :return: a list of items
        """
        super().search(*args, **kwargs)
        self._parameters.update({"odc_stac_kwargs": odc_stac_kwargs})

        bounds_4326 = self._reproject_shp(self._param("shp")).total_bounds

        catalog = pystac_client.Client.open(
            self._base_url,
            modifier=pc.sign_inplace,
        )

        start_date = self._param("start_date")
        end_date = self._param("end_date")
        datetime = f"{start_date}/{end_date}" if start_date and end_date else None
        search = catalog.search(
            collections=self._param("collection"),
            bbox=bounds_4326,
            datetime=datetime,
            query=self._param("filter"),
        )

        items = search.item_collection()
        if len(items) == 0:
            raise ValueError("No items found")
        return items

    def download(self, items) -> Union[xr.Dataset, list]:
        """Download the items from the Planetary Computer and return a xarray.Dataset or download the files and return a list of filenames.
        If `create_minicube` is set to True, a xarray.Dataset will be returned, otherwise a list of filenames will be returned.

        :param items: items to download
        :return: xarray.Dataset or list of filenames
        """
        if len(items) < 1:
            raise ValueError("No items to download")

        shp = self._param("shp")
        bounds = list(shp.bounds.values[0])
        res = meters_to_crs_unit(self._param("resolution"), shp)

        if self._param("create_minicube"):
            # order items by time because odc.stac.load does not preserve the order (preserve_original_order does not work)
            items = sorted(items, key=lambda x: x.datetime)
            ds = odc.stac.load(
                items,
                bands=self._param("bands"),
                crs=shp.crs,
                resolution=odc.geo.resxy_(res[0], -res[1]),
                x=(bounds[0], bounds[2]),
                y=(bounds[1], bounds[3]),
                **self._param("odc_stac_kwargs", default={}),
            )
            ds = gather_assign_meta(self._param("save_metadata"), items, ds, prop_name="properties")
            ds = self._prepare_cube(ds)
            return ds
        else:
            bands = self._param("bands")
            if bands is None:
                bands = items[0].assets.keys()
            self._param("download_folder").mkdir(parents=True, exist_ok=True)
            file_ext = "nc" if "netcdf" in items[0].assets[bands[0]].media_type else "tiff"
            fns = [
                self._param("download_folder").joinpath(
                    f"{self._param('collection')}_{band}_{item.id}.{file_ext}"
                )
                for item in items
                for band in bands
            ]
            urls = [item.assets[band].href for item in items for band in bands]
            Parallel(n_jobs=self._param("num_workers"), backend="threading")(
                delayed(self._download_file)(url, fn) for url, fn in zip(urls, fns)
            )
            return fns

    def _download_file(self, url, fn):
        """download a file from a url into fn."""
        if fn.exists():
            return
        response = requests.get(url, stream=True)
        if response.status_code != 200:
            raise RuntimeError(f"Url {url} response code: {response.status_code}.")
        try:  # download the file
            with open(fn, "wb") as f:
                shutil.copyfileobj(response.raw, f)
        except Exception as e:
            if fn.exists():
                fn.unlink()
            raise RuntimeError(f"Failed to download {url} with error {e}")
        finally:
            response.close()
