"""Test each exposed MCP tool function"""
import pytest
from biolink_mcp.server import (
    get_element,
    get_ancestors,
    get_descendants,
    get_all_classes,
    get_all_slots,
    get_all_entities,
    get_element_by_mapping,
    is_predicate,
    get_slot_domain,
    get_slot_range,
)


def test_get_element():
    """Test get_element tool"""
    result = get_element.fn("small molecule")
    assert isinstance(result, dict)
    assert result["name"] == "small molecule"
    assert result["class_uri"] == "biolink:SmallMolecule"


def test_get_element_not_found():
    """Test get_element with non-existent element"""
    result = get_element.fn("nonexistent_element_12345")
    assert result == {}


def test_get_ancestors():
    """Test get_ancestors tool"""
    result = get_ancestors.fn("disease")
    assert isinstance(result, list)
    assert len(result) > 0
    assert "named thing" in result


def test_get_descendants():
    """Test get_descendants tool"""
    result = get_descendants.fn("named thing")
    assert isinstance(result, list)
    assert len(result) > 0
    assert "disease" in result


def test_get_all_classes():
    """Test get_all_classes tool"""
    result = get_all_classes.fn()
    assert isinstance(result, list)
    assert len(result) > 0
    assert "disease" in result
    assert "gene" in result


def test_get_all_slots():
    """Test get_all_slots tool"""
    result = get_all_slots.fn()
    assert isinstance(result, list)
    assert len(result) > 0


def test_get_all_entities():
    """Test get_all_entities tool"""
    result = get_all_entities.fn()
    assert isinstance(result, list)
    assert len(result) > 0


def test_get_element_by_mapping():
    """Test get_element_by_mapping tool"""
    # This should map to a Biolink element
    result = get_element_by_mapping.fn("STY:T047")
    assert result is not None


def test_is_predicate():
    """Test is_predicate tool"""
    # Test a known predicate
    assert is_predicate.fn("related_to") is True
    # Test a known class (not a predicate)
    assert is_predicate.fn("Disease") is False


def test_get_slot_domain():
    """Test get_slot_domain tool"""
    result = get_slot_domain.fn("related_to")
    assert isinstance(result, list)
    assert len(result) > 0
    assert "named thing" in result


def test_get_slot_range():
    """Test get_slot_range tool"""
    result = get_slot_range.fn("related_to")
    assert isinstance(result, list)
    assert len(result) > 0
    assert "named thing" in result
