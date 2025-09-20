import pytest

from noxus_sdk.client import Client
from noxus_sdk.workflows import ConfigError, WorkflowDefinition


@pytest.mark.test
def test_generate_text(client: Client):
    workflow = WorkflowDefinition(client=client, id="123")
    n = workflow.node("TextGenerationNode")
    with pytest.raises(ConfigError) as exc:
        n.config(foo="bar")
    assert str(exc.value).startswith("Invalid config key: foo (possible:")
    with pytest.raises(ConfigError) as exc:
        n.config(label="Test")
    assert str(exc.value).startswith("Missing required config value for ")
    n.config(label="Test", template="Write a poem about cars", model=["gpt-4o"])
    assert n.node_config["label"] == "Test"
    assert n.node_config["template"] == "Write a poem about cars"
    assert n.node_config["model"] == ["gpt-4o"]


def test_full_workflow(client: Client):
    workflow = WorkflowDefinition(client=client, id="123")
    input_node = workflow.node("InputNode")
    ai = workflow.node("TextGenerationNode").config(
        template="Write a poem about ((Input 1))",
    )
    output = workflow.node("OutputNode")
    with pytest.raises(ValueError) as exc:  # noqa: PT011 - Legacy... TODO(Andre) - Improve exceptions and remove this
        ai.input("variables")
    assert str(exc.value).startswith("key is required for variable_connector")
    workflow.link(input_node.output(), ai.input("variables", "Input 1"))
    workflow.link(ai.output(), output.input())

    with pytest.raises(KeyError) as exc2:
        output.output("FOOBAR")
    with pytest.raises(KeyError) as exc3:
        output.input("FOOBAR")

    assert len(workflow.nodes) == 3
    assert len(workflow.edges) == 2


def test_full_workflow_link_many(client: Client):
    workflow = WorkflowDefinition(client=client, id="123")
    input_node = workflow.node("InputNode")
    ai = workflow.node("TextGenerationNode").config(
        template="Write a poem about ((Input 1))",
    )
    output = workflow.node("OutputNode")
    workflow.link(input_node.output(), ai.input("variables", "Input 1"))
    workflow.link_many(ai, output)
    assert len(workflow.nodes) == 3
    assert len(workflow.edges) == 2
