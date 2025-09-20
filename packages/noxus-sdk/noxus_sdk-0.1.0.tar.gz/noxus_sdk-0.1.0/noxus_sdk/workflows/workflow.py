from __future__ import annotations

import enum
import uuid
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field, TypeAdapter, model_validator
from pydantic.config import ConfigDict

from noxus_sdk.client import Client

if TYPE_CHECKING:
    from noxus_sdk.resources.runs import Run
    from noxus_sdk.resources.workflows import WorkflowVersion


class ConfigError(Exception):
    pass


DATA_TYPE_MAP = {
    "int": int,
    "float": (float, int),
    "bool": bool,
    "dict": dict,
    "str": str,
    "list": list,
}


class DataType(str, enum.Enum):
    int = "int"
    float = "float"
    bool = "bool"
    dict = "dict"
    str = "str"
    list = "list"
    Image = "Image"
    Audio = "Audio"
    File = "File"
    Quote = "Quote"
    Custom = "Custom"
    NoxusAny = "Any"
    GoogleSheet = "GoogleSheet"
    SourceType = "SourceType"

    def validate(self, value: Any) -> Any:  # noqa: ANN401 - This is a valid use case for Any
        if self.value in DATA_TYPE_MAP and not isinstance(
            value,
            DATA_TYPE_MAP[self.value],
        ):
            raise TypeError(
                f"value '{value}' for data type {self} is invalid",
            )

        return value


class ConfigDefinition(BaseModel):
    type: DataType
    description: str | None
    visible: bool
    optional: bool
    default: Any

    def check_value(self, key: str, value: Any) -> None:  # noqa: ANN401 - This is a valid use case for Any
        if value is None:
            if not self.optional:
                raise ConfigError(f"Missing required config value for {key}")
            if self.default is not None:
                value = self.default
            if value == self.default:
                return
        try:
            self.type.validate(value)
        except Exception as e:
            raise ConfigError(f"Invalid config value for {key}: [{e}]") from e


class NodeDefinition(BaseModel):
    type: str
    title: str
    description: str
    integrations: list[str]
    inputs: list[dict]
    outputs: list[dict]
    config: dict[str, ConfigDefinition]
    is_available: bool
    visible: bool
    config_endpoint: str | None


NODE_TYPES: dict[str, NodeDefinition] = {}


def load_node_types(nodes_: list[dict]) -> None:
    NODE_TYPES.clear()
    nodes: list[NodeDefinition] = TypeAdapter(list[NodeDefinition]).validate_python(
        nodes_,
    )
    for node in nodes:
        NODE_TYPES[node.type] = node


class ConnectorType(str, enum.Enum):
    variable_connector = "variable_connector"
    variable_type_connector = "variable_type_connector"
    variable_type_size_connector = "variable_type_size_connector"
    variable_type_input = "variable_type_input"
    variable_type_output = "variable_type_output"
    connector = "connector"
    input = "input"
    output = "output"


class NodeInput(BaseModel):
    node_id: str
    name: str
    fixed_value: Any = None
    type: ConnectorType

    @property
    def id(self) -> str:
        return f"{self.node_id}::{self.name}"


class EdgePoint(BaseModel):
    node_id: str
    connector_name: str
    key: str | None = None
    optional: bool = False


class Edge(BaseModel):
    from_id: EdgePoint
    to_id: EdgePoint
    id: str | None = None


class NodeOutput(BaseModel):
    node_id: str
    name: str
    type: ConnectorType

    @property
    def id(self) -> str:
        return f"{self.node_id}::{self.name}"


class Node(BaseModel):
    type: str
    id: str
    name: str = ""
    display: dict = {}

    node_config: dict = {}
    connector_config: dict = {}
    config_definition: dict[str, ConfigDefinition] = {}
    subflow_config: dict | None = None
    subflow_id: str | None = None
    inputs: list[NodeInput] = []
    outputs: list[NodeOutput] = []

    def input(
        self,
        name: str | None = None,
        key: str | None = None,
        type_definition: str | None = None,
        *,
        type_definition_is_list: bool = False,
    ) -> EdgePoint:
        if name is None:
            if len(self.inputs) != 1:
                raise ValueError("Multiple inputs found, please specify a name")
            name = self.inputs[0].name
        i = {i.name: i for i in self.inputs}
        if name not in i:
            raise KeyError(f"Input {name} not found (possible: {list(i.keys())})")
        _input = i[name]
        if _input.type in ["variable_connector", "variable_type_size_connector"]:
            if key is None:
                raise ValueError("key is required for variable_connector")
            connector_config = self.connector_config.get("inputs")
            if not connector_config:
                raise ValueError(f"connector_config is missing {self.connector_config}")
            connector_inputs = {i["name"]: i for i in connector_config}
            if name not in connector_inputs:
                raise ValueError(
                    f"Invalid key: {name} (possible: {list(connector_inputs.keys())})",
                )
            connector_keys = connector_inputs[name].get("keys", [])
            if key not in connector_keys:
                connector_keys.append(key)
            if _input.type == "variable_type_size_connector":
                if type_definition is not None:
                    raise ValueError(
                        f"type_definition is required for variable_type_size_connector ({self.type}.{name})",
                    )
                type_definitions = connector_inputs[name].get("type_definitions", {})
                choices = connector_inputs[name].get("choices", [])
                if key not in type_definitions:
                    typedef = {
                        "data_type": type_definition,
                        "is_list": type_definition_is_list,
                    }
                    type_definitions[key] = typedef
                    if type_definition not in [c["data_type"] for c in choices]:
                        choices.append(typedef)
                    connector_inputs[name]["choices"] = choices
                    connector_inputs[name]["type_definitions"] = type_definitions
            return EdgePoint(
                node_id=_input.node_id,
                connector_name=_input.name,
                key=key,
            )
        return EdgePoint(node_id=_input.node_id, connector_name=_input.name, key=None)

    def output(
        self,
        name: str | None = None,
        key: str | None = None,
        type_definition: str | None = None,
        *,
        type_definition_is_list: bool = False,
    ) -> EdgePoint:
        if name is None:
            if len(self.outputs) != 1:
                raise ValueError("Multiple outputs found, please specify a name")
            name = self.outputs[0].name
        i = {i.name: i for i in self.outputs}
        if name not in i:
            raise KeyError(f"Output {name} not found (possible: {list(i.keys())})")
        output = i[name]
        if output.type in ["variable_connector", "variable_type_size_connector"]:
            if key is None:
                raise ValueError("key is required for variable_connector")
            connector_config = self.connector_config.get("outputs")
            if not connector_config:
                raise ValueError("connector_config is missing")
            connector_outputs = {o["name"]: o for o in connector_config}
            if name not in connector_outputs:
                raise ValueError(
                    f"Invalid key: {name} (possible: {list(connector_outputs.keys())})",
                )
            connector_keys = connector_outputs[name].get("keys", [])
            if key not in connector_keys:
                connector_keys.append(key)
            if output.type == "variable_type_size_connector":
                if type_definition is not None:
                    raise ValueError(
                        f"type_definition is required for variable_type_size_connector ({self.type}.{name})",
                    )
                type_definitions = connector_outputs[name].get("type_definitions", {})
                choices = connector_outputs[name].get("choices", [])
                if key not in type_definitions:
                    typedef = {
                        "data_type": type_definition,
                        "is_list": type_definition_is_list,
                    }
                    type_definitions[key] = typedef
                    if type_definition not in [c["data_type"] for c in choices]:
                        choices.append(typedef)
                    connector_outputs[name]["type_definitions"] = type_definitions
                    connector_outputs[name]["choices"] = choices
            return EdgePoint(
                node_id=output.node_id,
                connector_name=output.name,
                key=key,
            )
        return EdgePoint(node_id=output.node_id, connector_name=output.name, key=None)

    def create(self, x: int, y: int) -> Node:
        node_type = NODE_TYPES.get(self.type)
        if not node_type:
            raise ValueError(f"Node type {self.type} not found")
        self.config_definition = node_type.config
        self.inputs = [NodeInput(node_id=str(self.id), name=i["name"], type=i["type"]) for i in node_type.inputs]
        self.outputs = [
            NodeOutput(node_id=str(self.id), name=output["name"], type=output["type"]) for output in node_type.outputs
        ]
        if not self.connector_config:
            self.connector_config = {
                "inputs": node_type.inputs,
                "outputs": node_type.outputs,
            }
        self.name = node_type.title
        self.display = {"position": {"x": x, "y": y}}
        return self

    def config(self, **kwargs) -> Node:
        for key, value in kwargs.items():
            if key not in self.config_definition:
                raise ConfigError(
                    f"Invalid config key: {key} (possible: {[k for k,v in self.config_definition.items() if v.visible]})",
                )
            self.config_definition[key].check_value(key, value)
            self.node_config[key] = value
        for k, v in self.config_definition.items():
            if k not in self.node_config:
                v.check_value(k, None)
        return self

    @model_validator(mode="after")
    def call_create_after_validate(self) -> Node:
        old_display = dict(self.display)
        self.create(0, 0)
        if old_display:
            self.display = old_display
        return self


class WorkflowDefinition(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    client: Client | None = Field(default=None, exclude=True)
    id: str = ""
    group_id: str | None = Field(default=None, exclude=True)
    name: str = "Untitled Workflow"
    type: str = "flow"
    nodes: list[Node] = []
    edges: list[Edge] = []
    x: int = 0
    error_handler: uuid.UUID | None = None

    @model_validator(mode="before")
    @classmethod
    def _definition_flattener(cls, values: dict) -> dict:
        if "definition" in values:
            values["nodes"] = values["definition"]["nodes"]
            values["edges"] = values["definition"]["edges"]
        return values

    def to_noxus(self) -> dict:
        d = {
            "name": self.name,
            "type": self.type,
            "definition": {
                "nodes": [n.model_dump() for n in self.nodes],
                "edges": [e.model_dump() for e in self.edges],
            },
        }
        if self.error_handler:
            d["error_handler"] = str(self.error_handler)
        return d

    def refresh_from_data(
        self,
        client: Client | None = None,
        **data,
    ) -> WorkflowDefinition:
        n = self.__class__.model_validate(data)
        for k in n.model_fields_set:
            v = getattr(n, k)
            setattr(self, k, v)
        self.client = client
        return self

    def refresh(self) -> WorkflowDefinition:
        if not self.client:
            raise ValueError("Client not set")
        response = self.client.get(f"/v1/workflows/{self.id}")
        self.refresh_from_data(client=self.client, **response)
        return self

    async def arefresh(self) -> WorkflowDefinition:
        if not self.client:
            raise ValueError("Client not set")
        response = await self.client.aget(f"/v1/workflows/{self.id}")
        self.refresh_from_data(client=self.client, **response)
        return self

    def run(
        self,
        body: dict[str, Any],
        workflow_version_id: uuid.UUID | str | None = None,
    ) -> Run:
        from noxus_sdk.resources.runs import Run

        if not self.client:
            raise ValueError("Client not set")
        url = f"/v1/workflows/{self.id}/runs"
        req: dict[str, Any] = {"input": body}
        if workflow_version_id:
            req["workflow_version_id"] = str(workflow_version_id)

        response = self.client.post(url, req)
        return Run(client=self.client, **response)

    async def arun(
        self,
        body: dict[str, Any],
        workflow_version_id: uuid.UUID | str | None = None,
    ) -> Run:
        if not self.client:
            raise ValueError("Client not set")
        from noxus_sdk.resources.runs import Run

        req: dict[str, Any] = {"input": body}
        if workflow_version_id:
            req["workflow_version_id"] = str(workflow_version_id)
        response = await self.client.apost(f"/v1/workflows/{self.id}/runs", req)
        return Run(client=self.client, **response)

    def update(self, *, force: bool = False) -> WorkflowDefinition:
        if not self.client:
            raise ValueError("Client not set")
        w = self.client.workflows.update(self.id, self, force=force)
        self.refresh_from_data(client=self.client, **w.model_dump())
        return w

    async def aupdate(self, *, force: bool = False) -> WorkflowDefinition:
        if not self.client:
            raise ValueError("Client not set")
        w = await self.client.workflows.aupdate(self.id, self, force=force)
        self.refresh_from_data(client=self.client, **w.model_dump())
        return w

    def save(self) -> WorkflowDefinition:
        if not self.client:
            raise ValueError("Client not set")
        return self.client.workflows.save(self)

    async def asave(self) -> WorkflowDefinition:
        if not self.client:
            raise ValueError("Client not set")
        return await self.client.workflows.asave(self)

    def save_version(
        self,
        name: str,
        description: str | None = None,
    ) -> WorkflowVersion:
        if not self.client:
            raise ValueError("Client not set")
        return self.client.workflows.save_version(self.id, self, name, description)

    async def asave_version(
        self,
        name: str,
        description: str | None = None,
    ) -> WorkflowVersion:
        if not self.client:
            raise ValueError("Client not set")
        return await self.client.workflows.asave_version(
            self.id,
            self,
            name,
            description,
        )

    def update_version(
        self,
        version_id: str,
        name: str,
        description: str | None,
    ) -> WorkflowVersion:
        if not self.client:
            raise ValueError("Client not set")
        return self.client.workflows.update_version(
            self.id,
            version_id,
            name,
            description,
            self,
        )

    async def aupdate_version(
        self,
        version_id: str,
        name: str,
        description: str | None,
    ) -> WorkflowVersion:
        if not self.client:
            raise ValueError("Client not set")
        return await self.client.workflows.aupdate_version(
            self.id,
            version_id,
            name,
            description,
            self,
        )

    def list_versions(self) -> list[WorkflowVersion]:
        if not self.client:
            raise ValueError("Client not set")
        return self.client.workflows.list_versions(self.id)

    async def alist_versions(self) -> list[WorkflowVersion]:
        if not self.client:
            raise ValueError("Client not set")
        return await self.client.workflows.alist_versions(self.id)

    def verify_name_legal(self, name: str) -> None:
        if name in [
            "AgentStartNode",
            "AgentEndNode",
            "AgentMessageSendNode",
            "ChoiceAgentNode",
            "FormExtractionAgentNode",
            "BasicAgentNode",
            "ChatAgentNode",
        ]:
            raise ValueError(f"Invalid node name: {name}")

    def node(self, name: str) -> Node:
        self.verify_name_legal(name)
        self.x += 350
        n = Node(id=str(uuid.uuid4()), type=name)
        n.create(x=self.x, y=0)
        self.nodes.append(n)
        return n

    def link(self, from_node: EdgePoint, to_node: EdgePoint) -> Edge:
        e = Edge(id=str(uuid.uuid4()), from_id=from_node, to_id=to_node)
        self.edges.append(e)
        return e

    def link_many(self, *nodes: Node) -> None:
        for i in range(len(nodes) - 1):
            if not len(nodes[i].outputs) == 1:
                raise ValueError(
                    f"Expected 1 output for {nodes[i].type}, got {len(nodes[i].outputs)}",
                )

            if nodes[i].outputs[0].type == "variable_connector":
                raise ValueError(
                    f"A key is required for variable_connector output so unable to link {nodes[i].type} to {nodes[i + 1].type} automatically",
                )
            if not len(nodes[i + 1].inputs) == 1:
                raise ValueError(
                    f"Expected 1 input for {nodes[i + 1].type}, got {len(nodes[i + 1].inputs)}",
                )
            if nodes[i + 1].inputs[0].type == "variable_connector":
                raise ValueError(
                    f"A key is required for variable_connector input so unable to link {nodes[i].type} to {nodes[i + 1].type} automatically",
                )
            self.link(nodes[i].output(), nodes[i + 1].input())
