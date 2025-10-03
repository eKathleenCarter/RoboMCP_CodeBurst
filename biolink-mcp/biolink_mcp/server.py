import os
import json
from typing import Optional, List
from fastmcp import FastMCP
from bmt import Toolkit
from linkml_runtime.dumpers import json_dumper

mcp = FastMCP("biolink", version="0.1.0")

# Initialize BMT toolkit with optional version from environment variable
biolink_version = os.getenv("BIOLINK_VERSION")
toolkit = Toolkit(biolink_version) if biolink_version else Toolkit()


@mcp.tool()
def get_element(name: str) -> dict:
    """Get a Biolink Model element by name (class or slot)"""
    element = toolkit.get_element(name)
    if element:
        return json.loads(json_dumper.dumps(element))
    return {}


@mcp.tool()
def get_ancestors(name: str, formatted: bool = False, mixin: bool = True) -> List[str]:
    """Get ancestors of a Biolink Model element

    Args:
        name: Name of the Biolink element
        formatted: Whether to return formatted CURIEs
        mixin: Whether to include mixin ancestors
    """
    return toolkit.get_ancestors(name, formatted=formatted, mixin=mixin)


@mcp.tool()
def get_descendants(name: str, formatted: bool = False, mixin: bool = True) -> List[str]:
    """Get descendants of a Biolink Model element

    Args:
        name: Name of the Biolink element
        formatted: Whether to return formatted CURIEs
        mixin: Whether to include mixin descendants
    """
    return toolkit.get_descendants(name, formatted=formatted, mixin=mixin)


@mcp.tool()
def get_all_classes(formatted: bool = False) -> List[str]:
    """Get all Biolink Model classes

    Args:
        formatted: Whether to return formatted CURIEs
    """
    return toolkit.get_all_classes(formatted=formatted)


@mcp.tool()
def get_all_slots(formatted: bool = False) -> List[str]:
    """Get all Biolink Model slots

    Args:
        formatted: Whether to return formatted CURIEs
    """
    return toolkit.get_all_slots(formatted=formatted)


@mcp.tool()
def get_all_entities(formatted: bool = False) -> List[str]:
    """Get all Biolink Model entities

    Args:
        formatted: Whether to return formatted CURIEs
    """
    return toolkit.get_all_entities(formatted=formatted)


@mcp.tool()
def get_element_by_mapping(identifier: str) -> Optional[str]:
    """Get a Biolink Model element by an external CURIE/IRI mapping

    Args:
        identifier: External CURIE or IRI
    """
    return toolkit.get_element_by_mapping(identifier)


@mcp.tool()
def is_predicate(name: str) -> bool:
    """Check if a name is a Biolink predicate

    Args:
        name: Name to check
    """
    return toolkit.is_predicate(name)


@mcp.tool()
def get_slot_domain(slot_name: str) -> List[str]:
    """Get the domain (subject types) for a Biolink slot

    Args:
        slot_name: Name of the slot
    """
    return toolkit.get_slot_domain(slot_name)


@mcp.tool()
def get_slot_range(slot_name: str) -> List[str]:
    """Get the range (object types) for a Biolink slot

    Args:
        slot_name: Name of the slot
    """
    return toolkit.get_slot_range(slot_name)


def main():
    mcp.run()
