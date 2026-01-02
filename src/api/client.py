import logging

from api.base_client import BaseAPIClient
from api.endpoints import ScheduleEndpoint
from api.schemas.requests import ScheduleFilters
from api.schemas.responses import (
    PaginatedResponse,
    XlsxScheduleDetail,
    XlsxScheduleSummary,
)

logger = logging.getLogger(__name__)


class ScheduleAPIClient(BaseAPIClient):
    """Client for university schedule API."""

    async def get_schedules_page(
        self,
        page: int = 0,
        filters: ScheduleFilters | None = None,
        page_size: int = 20,
    ) -> PaginatedResponse:
        """
        Get a single page of schedules with optional filtering.

        Args:
            page: Page number (0-based)
            filters: Optional filters for schedules
            page_size: Number of items per page

        Returns:
            PaginatedResponse with schedule summaries for the page
        """
        endpoint = ScheduleEndpoint.find_all(page)

        params = {
            "size": page_size,
            "sort": "id,desc",
        }

        if not filters:
            filters = ScheduleFilters()
        filters_data = filters.model_dump(
            mode="json",
            exclude_none=True,
            by_alias=True,
        )

        logger.debug(
            "Fetching page %d with filters: %s",
            page,
            {k: v for k, v in filters_data.items() if v},  # Show only non-empty filters
        )

        response = await self.post(
            endpoint,
            json=filters_data,
            params=params,
        )

        return PaginatedResponse.model_validate(response)

    async def get_schedule_details(self, schedule_id: int) -> XlsxScheduleDetail | None:
        """
        Get detailed information for a specific schedule.

        Args:
            schedule_id: Schedule ID

        Returns:
            Detailed schedule information including lessons
        """
        endpoint = ScheduleEndpoint.find_by_id()
        params = {"xlsxScheduleId": schedule_id}

        logger.info("Fetching details for schedule ID: %d", schedule_id)

        try:
            response = await self.get(endpoint, params=params)

            if isinstance(response, dict) and not response:
                logger.info("Schedule %d not found or no content", schedule_id)
                return None

            return XlsxScheduleDetail.model_validate(response)

        except Exception as e:
            logger.error("Unexpected error for schedule %d: %s", schedule_id, e)
            return None

    async def search_schedules(
        self,
        filters: ScheduleFilters | None = None,
        max_pages: int = 5,
    ) -> list[XlsxScheduleSummary]:
        """
        Search schedules across multiple pages (pagination).

        Args:
            filters: Optional filters for schedules
            max_pages: Maximum number of pages to fetch
            page_size: Number of items per page

        Returns:
            Combined list of schedule summaries from all fetched pages
        """
        all_schedules: list[XlsxScheduleSummary] = []
        filters = filters or ScheduleFilters()

        logger.info(
            "Starting search across %d pages with filters: %s",
            max_pages,
            filters.model_dump(exclude_none=True, by_alias=True),
        )

        for page in range(max_pages):
            try:
                logger.debug("Fetching page %d/%d", page + 1, max_pages)
                response = await self.get_schedules_page(
                    page=page,
                    filters=filters,
                )

                schedules_on_page = response.content
                all_schedules.extend(schedules_on_page)

                logger.debug(
                    "Page %d: got %d schedules, total so far: %d",
                    page,
                    len(schedules_on_page),
                    len(all_schedules),
                )

                # Stop if this is the last page or page is empty
                if response.last or not schedules_on_page:
                    logger.debug("Reached last page or empty page, stopping")
                    break

            except Exception as e:
                logger.error("Error fetching page %d: %s", page, e)
                if page == 0:  # Re-raise if first page fails
                    raise
                break

        logger.info("Search completed, found %d schedules total", len(all_schedules))
        return all_schedules

    async def get_all_schedules(self, max_pages: int = 100) -> list[XlsxScheduleSummary]:
        """
        Get all available schedules (no filters).

        Returns:
            All schedule summaries
        """
        logger.info("Fetching all schedules")
        return await self.search_schedules(filters=None, max_pages=max_pages)
