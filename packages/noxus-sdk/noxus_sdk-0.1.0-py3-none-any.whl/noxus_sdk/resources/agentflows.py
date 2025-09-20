from __future__ import annotations

from noxus_sdk.resources.base import BaseService
from noxus_sdk.workflows.agentflow import AgentFlowDefinition


class AgentFlowService(BaseService[AgentFlowDefinition]):
    async def alist(
        self,
        page: int = 1,
        page_size: int = 10,
    ) -> list[AgentFlowDefinition]:
        workflows_data = await self.client.apget(
            "/v1/workflows",
            params={"page": page, "page_size": page_size, "type": "agent_flow"},
            page=page,
            page_size=page_size,
        )
        return [AgentFlowDefinition.model_validate({"client": self.client, **data}) for data in workflows_data]

    def list(self, page: int = 1, page_size: int = 10) -> list[AgentFlowDefinition]:
        workflows_data = self.client.pget(
            "/v1/workflows",
            params={"page": page, "page_size": page_size, "type": "agent_flow"},
            page=page,
            page_size=page_size,
        )
        return [AgentFlowDefinition.model_validate({"client": self.client, **data}) for data in workflows_data]

    def delete(self, workflow_id: str) -> None:
        self.client.delete(f"/v1/workflows/{workflow_id}")

    async def adelete(self, workflow_id: str) -> None:
        await self.client.adelete(f"/v1/workflows/{workflow_id}")

    def save(self, workflow: AgentFlowDefinition) -> AgentFlowDefinition:
        w = self.client.post("/v1/workflows", workflow.to_noxus())
        workflow.refresh_from_data(client=self.client, **w)
        return workflow

    async def asave(self, workflow: AgentFlowDefinition) -> AgentFlowDefinition:
        w = await self.client.apost("/v1/workflows", workflow.to_noxus())
        workflow.refresh_from_data(client=self.client, **w)
        return workflow

    def get(self, workflow_id: str) -> AgentFlowDefinition:
        w = self.client.get(f"/v1/workflows/{workflow_id}")
        return AgentFlowDefinition.model_validate({"client": self.client, **w})

    async def aget(self, workflow_id: str) -> AgentFlowDefinition:
        w = await self.client.aget(f"/v1/workflows/{workflow_id}")
        return AgentFlowDefinition.model_validate({"client": self.client, **w})

    def update(
        self,
        workflow_id: str,
        workflow: AgentFlowDefinition,
        *,
        force: bool = False,
    ) -> AgentFlowDefinition:
        w = self.client.patch(
            f"/v1/workflows/{workflow_id}?force={force}",
            workflow.to_noxus(),
        )
        workflow.refresh_from_data(client=self.client, **w)
        return workflow

    async def aupdate(
        self,
        workflow_id: str,
        workflow: AgentFlowDefinition,
        *,
        force: bool = False,
    ) -> AgentFlowDefinition:
        w = await self.client.apatch(
            f"/v1/workflows/{workflow_id}?force={force}",
            workflow.to_noxus(),
        )
        workflow.refresh_from_data(client=self.client, **w)
        return workflow
