# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Generic, TypeVar, Optional
from typing_extensions import override

from ._base_client import BasePage, PageInfo, BaseSyncPage, BaseAsyncPage

__all__ = ["SyncMyOffsetPage", "AsyncMyOffsetPage"]

_T = TypeVar("_T")


class SyncMyOffsetPage(BaseSyncPage[_T], BasePage[_T], Generic[_T]):
    objects: List[_T]
    meta: Optional[object] = None

    @override
    def _get_page_items(self) -> List[_T]:
        objects = self.objects
        if not objects:
            return []
        return objects

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        offset = self._options.params.get("offset") or 0
        if not isinstance(offset, int):
            raise ValueError(f'Expected "offset" param to be an integer but got {offset}')

        length = len(self._get_page_items())
        current_count = offset + length

        return PageInfo(params={"offset": current_count})


class AsyncMyOffsetPage(BaseAsyncPage[_T], BasePage[_T], Generic[_T]):
    objects: List[_T]
    meta: Optional[object] = None

    @override
    def _get_page_items(self) -> List[_T]:
        objects = self.objects
        if not objects:
            return []
        return objects

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        offset = self._options.params.get("offset") or 0
        if not isinstance(offset, int):
            raise ValueError(f'Expected "offset" param to be an integer but got {offset}')

        length = len(self._get_page_items())
        current_count = offset + length

        return PageInfo(params={"offset": current_count})
