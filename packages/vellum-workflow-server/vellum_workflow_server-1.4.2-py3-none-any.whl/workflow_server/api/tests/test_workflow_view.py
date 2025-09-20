import logging
import re
from unittest.mock import patch
from uuid import UUID

from deepdiff import DeepDiff

from workflow_server.server import create_app


def test_version_route():
    flask_app = create_app()

    with flask_app.test_client() as test_client:
        response = test_client.get("/workflow/version")
        assert response.status_code == 200
        assert re.match(r"[0-9]*\.[0-9]*\.[0-9]*", response.json["sdk_version"])
        assert response.json["server_version"] == "local"


def test_version_route__with_single_node_file(tmp_path):
    # GIVEN a temporary custom_nodes directory with a test node
    custom_nodes_dir = tmp_path / "vellum_custom_nodes"
    custom_nodes_dir.mkdir()

    node_file = custom_nodes_dir / "test_node.py"
    node_file.write_text(
        """
from vellum.workflows.nodes import BaseNode

class TestNode(BaseNode):
    \"""A test node for processing data.\"""
"""
    )

    flask_app = create_app()

    # WHEN we make a request to the version route
    with patch("os.getcwd", return_value=str(tmp_path)), flask_app.test_client() as test_client:
        response = test_client.get("/workflow/version")

    # THEN we should get a successful response
    assert response.status_code == 200

    # AND we should find exactly one node
    nodes = response.json["nodes"]
    assert len(nodes) == 1

    # AND the node should have the correct metadata
    node = nodes[0]
    assert UUID(node["id"])
    assert node["module"] == ["vellum_custom_nodes", "test_node"]
    assert node["name"] == "TestNode"
    assert node["label"] == "Test Node"
    assert "A test node for processing data." in node["description"]
    assert node["exec_config"] == {
        "adornments": None,
        "attributes": [],
        "base": {"module": ["vellum", "workflows", "nodes", "bases", "base"], "name": "BaseNode"},
        "definition": {"module": ["vellum_custom_nodes", "test_node"], "name": "TestNode"},
        "display_data": {
            "comment": {"expanded": True, "value": "A test node for processing data."},
            "position": {"x": 0.0, "y": 0.0},
        },
        "id": "7a8b251d-f5ca-462a-b293-071d219460fb",
        "label": "Test Node",
        "outputs": [],
        "ports": [{"id": "a3a0eefd-45d0-4f13-8c58-a836a9f7f9ed", "name": "default", "type": "DEFAULT"}],
        "trigger": {"id": "a022e36c-9852-4772-9be3-3c6c147fd811", "merge_behavior": "AWAIT_ATTRIBUTES"},
        "type": "GENERIC",
    }


def test_version_route__with_nodes_in_multiple_files(tmp_path):
    # GIVEN a temporary custom_nodes directory
    custom_nodes_dir = tmp_path / "vellum_custom_nodes"
    custom_nodes_dir.mkdir()

    # AND a first node file
    first_node_file = custom_nodes_dir / "first_node.py"
    first_node_file.write_text(
        """
from vellum.workflows.nodes import BaseNode

class SomeNode(BaseNode):
    \"""This is Some Node.\"""
"""
    )

    # AND a second node file
    second_node_file = custom_nodes_dir / "second_node.py"
    second_node_file.write_text(
        """
from vellum.workflows.nodes import BaseNode

class SomeOtherNode(BaseNode):
    \"""This is Some Other Node.\"""
"""
    )

    flask_app = create_app()

    # WHEN we make a request to the version route
    with patch("os.getcwd", return_value=str(tmp_path)), flask_app.test_client() as test_client:
        response = test_client.get("/workflow/version")

    # THEN we should get a successful response
    assert response.status_code == 200

    # AND we should find both nodes
    nodes = response.json["nodes"]
    assert len(nodes) == 2

    # AND the first node should have correct metadata
    some_node = nodes[0]
    assert some_node["label"] == "Some Node"
    assert some_node["description"] == "This is Some Node."
    assert UUID(some_node["id"])
    assert some_node["module"] == ["vellum_custom_nodes", "first_node"]
    assert some_node["exec_config"] == {
        "adornments": None,
        "attributes": [],
        "base": {"module": ["vellum", "workflows", "nodes", "bases", "base"], "name": "BaseNode"},
        "definition": {"module": ["vellum_custom_nodes", "first_node"], "name": "SomeNode"},
        "display_data": {
            "comment": {"expanded": True, "value": "This is Some Node."},
            "position": {"x": 0.0, "y": 0.0},
        },
        "id": "1e559c2e-db82-41f0-9ceb-5e89b0c5a0a3",
        "label": "Some Node",
        "outputs": [],
        "ports": [{"id": "48e39e97-5fd4-471e-b4f2-51d3baf06456", "name": "default", "type": "DEFAULT"}],
        "trigger": {"id": "e3381fb7-61fc-4c46-ae8e-51fc463b6a59", "merge_behavior": "AWAIT_ATTRIBUTES"},
        "type": "GENERIC",
    }

    # AND the second node should have correct metadata
    some_other_node = nodes[1]
    assert some_other_node["label"] == "Some Other Node"
    assert some_other_node["description"] == "This is Some Other Node."
    assert UUID(some_other_node["id"])
    assert some_other_node["module"] == ["vellum_custom_nodes", "second_node"]
    assert some_other_node["exec_config"] == {
        "adornments": None,
        "attributes": [],
        "base": {"module": ["vellum", "workflows", "nodes", "bases", "base"], "name": "BaseNode"},
        "definition": {"module": ["vellum_custom_nodes", "second_node"], "name": "SomeOtherNode"},
        "display_data": {
            "comment": {"expanded": True, "value": "This is Some Other Node."},
            "position": {"x": 0.0, "y": 0.0},
        },
        "id": "7aee541b-b245-4c8a-9137-3e4631d5100c",
        "label": "Some Other Node",
        "outputs": [],
        "ports": [{"id": "fb66b46a-d970-4bc9-83ea-70c154c57ddd", "name": "default", "type": "DEFAULT"}],
        "trigger": {"id": "13fa2714-20b3-4bc3-ab79-621a188e3bfa", "merge_behavior": "AWAIT_ATTRIBUTES"},
        "type": "GENERIC",
    }


def test_version_route__no_custom_nodes_dir(tmp_path):
    # GIVEN a Flask application and an empty temp directory
    flask_app = create_app()

    # WHEN we make a request to the version route
    with patch("os.getcwd", return_value=str(tmp_path)), flask_app.test_client() as test_client:
        response = test_client.get("/workflow/version")

    # THEN we should get a successful response
    assert response.status_code == 200

    # AND the nodes list should be empty
    assert response.json["nodes"] == []


def test_version_route__with_multiple_nodes_in_file(tmp_path):
    # Create a temporary custom_nodes directory with multiple nodes in one file
    custom_nodes_dir = tmp_path / "vellum_custom_nodes"
    custom_nodes_dir.mkdir()

    # Create a test node file with multiple nodes
    node_file = custom_nodes_dir / "multiple_nodes.py"
    node_file.write_text(
        """
from vellum.workflows.nodes import BaseNode

class ProcessingNode(BaseNode):
    \"""Processes input data.\"""

class TransformationNode(BaseNode):
    \"""Transforms data format.\"""

# This class should not be discovered
class HelperClass:
    pass
"""
    )

    flask_app = create_app()

    # Mock the current working directory to point to our temp directory
    with patch("os.getcwd", return_value=str(tmp_path)), flask_app.test_client() as test_client:
        response = test_client.get("/workflow/version")

        assert response.status_code == 200
        nodes = response.json["nodes"]
        assert len(nodes) == 2

        # Nodes should be discovered regardless of their order in the file
        node_names = {node["name"] for node in nodes}
        assert node_names == {"ProcessingNode", "TransformationNode"}

        # Find and assert each node individually
        processing_node = next(node for node in nodes if node["name"] == "ProcessingNode")
        assert processing_node["exec_config"] == {
            "adornments": None,
            "attributes": [],
            "base": {"module": ["vellum", "workflows", "nodes", "bases", "base"], "name": "BaseNode"},
            "definition": {"module": ["vellum_custom_nodes", "multiple_nodes"], "name": "ProcessingNode"},
            "display_data": {
                "comment": {"expanded": True, "value": "Processes input data."},
                "position": {"x": 0.0, "y": 0.0},
            },
            "id": "f92c09f0-0434-46cb-829d-a73f801d6343",
            "label": "Processing Node",
            "outputs": [],
            "ports": [{"id": "abaa2984-b312-4491-b069-e689759f72c8", "name": "default", "type": "DEFAULT"}],
            "trigger": {"id": "35378c2b-f089-44af-ac37-efe4ea42c817", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "type": "GENERIC",
        }

        transformation_node = next(node for node in nodes if node["name"] == "TransformationNode")
        assert transformation_node["exec_config"] == {
            "adornments": None,
            "attributes": [],
            "base": {"module": ["vellum", "workflows", "nodes", "bases", "base"], "name": "BaseNode"},
            "definition": {"module": ["vellum_custom_nodes", "multiple_nodes"], "name": "TransformationNode"},
            "display_data": {
                "comment": {"expanded": True, "value": "Transforms data format."},
                "position": {"x": 0.0, "y": 0.0},
            },
            "id": "09ca32f7-c8f2-4469-97e5-1f288f85127a",
            "label": "Transformation Node",
            "outputs": [],
            "ports": [{"id": "88778117-fbfc-4b44-964b-5a4994aa2f24", "name": "default", "type": "DEFAULT"}],
            "trigger": {"id": "5d096263-7fbf-490a-83b7-e441852b5fb6", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "type": "GENERIC",
        }


def test_version_route__with_invalid_node_file(tmp_path, caplog):
    caplog.set_level(logging.WARNING)

    # GIVEN a temporary custom_nodes directory
    custom_nodes_dir = tmp_path / "vellum_custom_nodes"
    custom_nodes_dir.mkdir()

    # AND a valid node file
    valid_node_file = custom_nodes_dir / "valid_node.py"
    valid_node_file.write_text(
        """
from vellum.workflows.nodes import BaseNode

class SomeNode(BaseNode):
    \"\"\"This is Some Node.\"\"\"
"""
    )

    # AND an invalid node file with syntax error of missing colon in the class
    invalid_node_file = custom_nodes_dir / "invalid_node.py"
    invalid_node_file.write_text(
        """
from vellum.workflows.nodes import BaseNode

class BrokenNode(BaseNode)
    \"\"\"This node has a syntax error.\"\"\"
"""
    )

    flask_app = create_app()

    # WHEN we make a request to the version route
    with patch("os.getcwd", return_value=str(tmp_path)), flask_app.test_client() as test_client:
        response = test_client.get("/workflow/version")

    # THEN we should get a successful response
    assert response.status_code == 200

    # AND we should find only the valid node
    nodes = response.json["nodes"]
    assert len(nodes) == 1

    # AND the valid node should have correct metadata
    valid_node = nodes[0]
    assert valid_node["label"] == "Some Node"
    assert valid_node["description"] == "This is Some Node."
    assert UUID(valid_node["id"])
    assert valid_node["module"] == ["vellum_custom_nodes", "valid_node"]
    assert valid_node["exec_config"] == {
        "adornments": None,
        "attributes": [],
        "base": {"module": ["vellum", "workflows", "nodes", "bases", "base"], "name": "BaseNode"},
        "definition": {"module": ["vellum_custom_nodes", "valid_node"], "name": "SomeNode"},
        "display_data": {
            "comment": {"expanded": True, "value": "This is Some Node."},
            "position": {"x": 0.0, "y": 0.0},
        },
        "id": "1e559c2e-db82-41f0-9ceb-5e89b0c5a0a3",
        "label": "Some Node",
        "outputs": [],
        "ports": [{"id": "48e39e97-5fd4-471e-b4f2-51d3baf06456", "name": "default", "type": "DEFAULT"}],
        "trigger": {"id": "e3381fb7-61fc-4c46-ae8e-51fc463b6a59", "merge_behavior": "AWAIT_ATTRIBUTES"},
        "type": "GENERIC",
    }

    # AND the error should be logged with full traceback
    assert len(caplog.records) > 0
    error_message = caplog.records[0].message
    assert "Failed to load node from module invalid_node" in error_message
    assert "invalid_node.py, line 4" in error_message


def test_version_route__with_attributes(tmp_path):
    # GIVEN a temporary custom_nodes directory
    custom_nodes_dir = tmp_path / "vellum_custom_nodes"
    custom_nodes_dir.mkdir()

    # AND an addition node file
    node_file = custom_nodes_dir / "addition_node.py"
    node_file.write_text(
        """
from vellum.workflows.nodes import BaseNode


class MyAdditionNode(BaseNode):
    \"\"\"Custom node that performs simple addition.\"\"\"
    arg1: int
    arg2: int

    class Outputs(BaseNode.Outputs):
        result: int

    def run(self) -> BaseNode.Outputs:
        result = self.arg1 + self.arg2
        return self.Outputs(result=result)
"""
    )

    flask_app = create_app()

    # WHEN we make a request to the version route
    with patch("os.getcwd", return_value=str(tmp_path)), flask_app.test_client() as test_client:
        response = test_client.get("/workflow/version")

    # THEN we should get a successful response
    assert response.status_code == 200

    # AND we should find the addition node
    nodes = response.json["nodes"]
    assert len(nodes) == 1

    # AND the node should have the correct metadata
    node = nodes[0]
    assert node["label"] == "My Addition Node"
    assert node["description"] == "Custom node that performs simple addition."
    assert UUID(node["id"])
    assert node["module"] == ["vellum_custom_nodes", "addition_node"]
    assert node["name"] == "MyAdditionNode"
    assert node["exec_config"] == {
        "adornments": None,
        "attributes": [
            {
                "id": "aed3bcbb-d243-4a77-bb5e-409e9a28e868",
                "name": "arg1",
                "value": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}},
            },
            {
                "id": "9225d225-a41b-4642-8964-f28f58dcf4bf",
                "name": "arg2",
                "value": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}},
            },
        ],
        "base": {"module": ["vellum", "workflows", "nodes", "bases", "base"], "name": "BaseNode"},
        "definition": {"module": ["vellum_custom_nodes", "addition_node"], "name": "MyAdditionNode"},
        "display_data": {
            "comment": {"expanded": True, "value": "Custom node that performs simple addition."},
            "position": {"x": 0.0, "y": 0.0},
        },
        "id": "195cd69d-3d2d-41e4-a432-16c433cb8d34",
        "label": "My Addition Node",
        "outputs": [{"id": "3d8e40cb-2aa8-44bd-ae6a-708a9fbc4779", "name": "result", "type": "NUMBER", "value": None}],
        "ports": [{"id": "9a9e4ef6-febf-4093-a515-217bbb1373db", "name": "default", "type": "DEFAULT"}],
        "trigger": {"id": "a5298668-d808-4a45-a62e-790943948e8a", "merge_behavior": "AWAIT_ATTRIBUTES"},
        "type": "GENERIC",
        "should_file_merge": True,
    }


def test_serialize_route__with_no_files():
    # GIVEN a Flask application
    flask_app = create_app()

    # WHEN we make a request with no files
    with flask_app.test_client() as test_client:
        response = test_client.post("/workflow/serialize", json={"files": {}})

    # THEN we should get a bad request response
    assert response.status_code == 400

    # AND the response should contain an error message
    assert "detail" in response.json
    assert "No files received" in response.json["detail"]


def test_serialize_route__with_invalid_python_syntax():
    # GIVEN a Flask application
    flask_app = create_app()

    # AND a file with invalid Python syntax
    invalid_content = """
from vellum.workflows.nodes import BaseNode

class BrokenNode(BaseNode)  # Missing colon
    \"\"\"This node has a syntax error.\"\"\"
"""

    # WHEN we make a request to the serialize route
    with flask_app.test_client() as test_client:
        response = test_client.post("/workflow/serialize", json={"files": {"broken_node.py": invalid_content}})

    # THEN we should get a 4xx response
    assert response.status_code == 400

    # AND the response should contain an error message
    assert "detail" in response.json
    assert "Serialization failed" in response.json["detail"]


def test_serialize_route__with__workflow():
    # GIVEN a Flask application
    flask_app = create_app()

    # AND a complete workflow with multiple files
    workflow_files = {
        "__init__.py": "# flake8: noqa: F401, F403\n\n",
        "inputs.py": "from typing import Any, Optional\n\nfrom vellum.workflows.inputs import BaseInputs\n\n\nclass Inputs(BaseInputs):\n    text: str\n    var_1: Optional[Any]\n",  # noqa: E501
        "workflow.py": "from vellum.workflows import BaseWorkflow\nfrom vellum.workflows.state import BaseState\n\nfrom .inputs import Inputs\nfrom .nodes.final_output import FinalOutput\nfrom .nodes.templating_node import TemplatingNode\n\n\nclass Workflow(BaseWorkflow[Inputs, BaseState]):\n    graph = TemplatingNode >> FinalOutput\n\n    class Outputs(BaseWorkflow.Outputs):\n        final_output = FinalOutput.Outputs.value\n",  # noqa: E501
        "nodes/__init__.py": 'from .final_output import FinalOutput\nfrom .templating_node import TemplatingNode\n\n__all__ = [\n    "FinalOutput",\n    "TemplatingNode",\n]\n',  # noqa: E501
        "nodes/templating_node.py": 'from vellum.workflows.nodes.displayable import TemplatingNode as BaseTemplatingNode\nfrom vellum.workflows.state import BaseState\n\nfrom ..inputs import Inputs\n\n\nclass TemplatingNode(BaseTemplatingNode[BaseState, str]):\n    template = """{{ text }}"""\n    inputs = {\n        "text": Inputs.text,\n    }\n',  # noqa: E501
        "nodes/final_output.py": "from vellum.workflows.nodes.displayable import FinalOutputNode\nfrom vellum.workflows.state import BaseState\n\nfrom .templating_node import TemplatingNode\n\n\nclass FinalOutput(FinalOutputNode[BaseState, str]):\n    class Outputs(FinalOutputNode.Outputs):\n        value = TemplatingNode.Outputs.result\n",  # noqa: E501
    }

    # WHEN we make a request to the serialize route
    with flask_app.test_client() as test_client:
        response = test_client.post("/workflow/serialize", json={"files": workflow_files})

    # THEN we should get a successful response
    assert response.status_code == 200

    # AND the response should contain the full WorkflowSerializationResult
    assert "exec_config" in response.json
    assert "errors" in response.json
    assert "dataset" in response.json or response.json.get("dataset") is None
    exec_config = response.json["exec_config"]

    # AND the exec_config should have workflow_raw_data
    assert "workflow_raw_data" in exec_config
    nodes = exec_config["workflow_raw_data"]["nodes"]

    # AND we should find the workflow nodes
    node_labels = {node["data"]["label"] for node in nodes}
    expected_nodes = {"Templating Node", "Final Output", "Entrypoint Node"}

    # AND at least some of the expected nodes should be present
    assert not DeepDiff(node_labels, expected_nodes, ignore_order=True)


def test_serialize_route__with_workspace_api_key():
    """
    Tests that the serialize route accepts workspace_api_key and passes it through serialization.
    """
    # GIVEN a Flask application
    flask_app = create_app()

    # AND a complete workflow with multiple files
    workflow_files = {
        "__init__.py": "# flake8: noqa: F401, F403\n\n",
        "inputs.py": "from typing import Any, Optional\n\nfrom vellum.workflows.inputs import BaseInputs\n\n\nclass Inputs(BaseInputs):\n    text: str\n    var_1: Optional[Any]\n",  # noqa: E501
        "workflow.py": "from vellum.workflows import BaseWorkflow\nfrom vellum.workflows.state import BaseState\n\nfrom .inputs import Inputs\nfrom .nodes.final_output import FinalOutput\nfrom .nodes.templating_node import TemplatingNode\n\n\nclass Workflow(BaseWorkflow[Inputs, BaseState]):\n    graph = TemplatingNode >> FinalOutput\n\n    class Outputs(BaseWorkflow.Outputs):\n        final_output = FinalOutput.Outputs.value\n",  # noqa: E501
        "nodes/__init__.py": 'from .final_output import FinalOutput\nfrom .templating_node import TemplatingNode\n\n__all__ = [\n    "FinalOutput",\n    "TemplatingNode",\n]\n',  # noqa: E501
        "nodes/templating_node.py": 'from vellum.workflows.nodes.displayable import TemplatingNode as BaseTemplatingNode\nfrom vellum.workflows.state import BaseState\n\nfrom ..inputs import Inputs\n\n\nclass TemplatingNode(BaseTemplatingNode[BaseState, str]):\n    template = """{{ text }}"""\n    inputs = {\n        "text": Inputs.text,\n    }\n',  # noqa: E501
        "nodes/final_output.py": "from vellum.workflows.nodes.displayable import FinalOutputNode\nfrom vellum.workflows.state import BaseState\n\nfrom .templating_node import TemplatingNode\n\n\nclass FinalOutput(FinalOutputNode[BaseState, str]):\n    class Outputs(FinalOutputNode.Outputs):\n        value = TemplatingNode.Outputs.result\n",  # noqa: E501
    }

    # WHEN we make a request to the serialize route with workspace_api_key
    with flask_app.test_client() as test_client:
        response = test_client.post(
            "/workflow/serialize", json={"files": workflow_files, "workspace_api_key": "test_workspace_key"}
        )

    # THEN we should get a successful response
    assert response.status_code == 200

    # AND the response should contain the full WorkflowSerializationResult
    assert "exec_config" in response.json
    assert "errors" in response.json


def test_serialize_route__with_invalid_workspace_api_key():
    """
    Tests that the serialize route handles invalid workspace_api_key gracefully.
    """
    # GIVEN a Flask application
    flask_app = create_app()

    workflow_files = {
        "__init__.py": "",
        "workflow.py": (
            "from vellum.workflows import BaseWorkflow\n\n"
            "class Workflow(BaseWorkflow):\n"
            "    class Outputs(BaseWorkflow.Outputs):\n"
            "        foo = 'hello'\n"
        ),
    }

    # WHEN we make a request with an invalid workspace_api_key
    with flask_app.test_client() as test_client:
        response = test_client.post(
            "/workflow/serialize", json={"files": workflow_files, "workspace_api_key": ""}  # Invalid empty key
        )

    # THEN we should still get a successful response (graceful degradation)
    assert response.status_code == 200

    # AND the response should contain the serialization result
    assert "exec_config" in response.json
