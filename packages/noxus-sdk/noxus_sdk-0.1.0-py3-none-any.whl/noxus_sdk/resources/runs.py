from __future__ import annotations

import asyncio
import time
from typing import TYPE_CHECKING

from pydantic import ConfigDict

from noxus_sdk.resources.base import BaseResource, BaseService

if TYPE_CHECKING:
    import builtins


class RunFailureError(Exception):
    pass


class Run(BaseResource):
    model_config = ConfigDict(validate_assignment=True)

    id: str
    group_id: str
    workflow_id: str
    input: dict
    node_ids: list[str] | None = None
    status: str
    progress: int
    progress_details: dict | None = None
    created_at: str
    finished_at: str | None = None
    output: dict | None = None
    workflow_definition: dict | None = None

    def refresh(self) -> Run:
        response = self.client.get(f"/v1/workflows/{self.workflow_id}/runs/{self.id}")
        for key, value in response.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self

    async def arefresh(self) -> Run:
        response = await self.client.aget(
            f"/v1/workflows/{self.workflow_id}/runs/{self.id}",
        )
        for key, value in response.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self

    def wait(
        self,
        interval: int = 5,
        *,
        output_only: bool = False,
    ) -> Run | dict | None:
        while self.status not in ["failed", "completed", "awaiting_human_feedback"]:
            time.sleep(interval)
            self.refresh()

        if self.status == "failed":
            raise RunFailureError(self.status)

        if output_only:
            return self.output
        return self

    async def a_wait(
        self,
        interval: int = 5,
        *,
        output_only: bool = False,
    ) -> Run | dict | None:
        while self.status not in ["failed", "completed", "awaiting_human_feedback"]:
            await asyncio.sleep(interval)
            await self.arefresh()

        if self.status == "failed":
            raise RunFailureError(self.status)

        if output_only:
            return self.output
        return self

    def get_status(self) -> str:
        return self.status


class RunService(BaseService[Run]):
    def get(self, workflow_id: str, run_id: str) -> Run:
        response = self.client.get(f"/v1/workflows/{workflow_id}/run/{run_id}")
        return Run(client=self.client, **response)

    async def aget(self, workflow_id: str, run_id: str) -> Run:
        response = await self.client.aget(f"/v1/workflows/{workflow_id}/run/{run_id}")
        return Run(client=self.client, **response)

    def list(self, workflow_id: str, page: int = 1, page_size: int = 10) -> list[Run]:
        response = self.client.pget(
            f"/v1/workflows/{workflow_id}/runs",
            params={"page": page, "page_size": page_size},
        )
        return [Run(client=self.client, **run) for run in response]

    async def alist(
        self,
        workflow_id: str,
        page: int = 1,
        page_size: int = 10,
    ) -> builtins.list[Run]:
        response = await self.client.apget(
            f"/v1/workflows/{workflow_id}/runs",
            params={"page": page, "page_size": page_size},
            page=page,
            page_size=page_size,
        )
        return [Run(client=self.client, **run) for run in response]
