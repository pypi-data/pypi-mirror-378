"""Licence content management for PyGremlinBox EPL-2.0."""

import importlib.resources as pkg_resources


def retrieve_licence_content() -> str:
    """Retrieve the full text of the EPL-2.0 licence.
    
    Returns:
        str: The complete EPL-2.0 licence text.
    """
    try:
        # Read licence from package root
        with pkg_resources.path("pygremlinbox_epl_2_0", "..") as package_path:
            licence_path = package_path.parent.parent / "LICENCE"
            return licence_path.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError) as e:
        return f"Error reading licence file: {e}"


def get_licence_identifier() -> str:
    """Get the SPDX licence identifier.
    
    Returns:
        str: The SPDX identifier for EPL-2.0.
    """
    return "EPL-2.0"


def get_package_metadata() -> dict:
    """Get package metadata including licence information.
    
    Returns:
        dict: Package metadata with licence details.
    """
    return {
        "name": "PyGremlinBox-EPL-2.0",
        "version": "0.1.0",
        "licence": "EPL-2.0",
        "licence_name": "Eclipse Public License 2.0",
        "copyleft": "weak",
        "osi_approved": True,
        "description": "Supply chain security testing package with EPL-2.0 licence"
    }