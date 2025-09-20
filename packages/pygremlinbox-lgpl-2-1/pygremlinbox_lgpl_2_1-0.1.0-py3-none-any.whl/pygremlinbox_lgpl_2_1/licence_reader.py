"""Licence content management for PyGremlinBox LGPL-2.1."""

import importlib.resources as pkg_resources


def retrieve_licence_content() -> str:
    """Retrieve the full text of the LGPL-2.1 licence.
    
    Returns:
        str: The complete LGPL-2.1 licence text.
    """
    try:
        # Read licence from package root
        with pkg_resources.path("pygremlinbox_lgpl_2_1", "..") as package_path:
            licence_path = package_path.parent.parent / "LICENCE"
            return licence_path.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError) as e:
        return f"Error reading licence file: {e}"


def get_licence_identifier() -> str:
    """Get the SPDX licence identifier.
    
    Returns:
        str: The SPDX identifier for LGPL-2.1.
    """
    return "LGPL-2.1"


def get_package_metadata() -> dict:
    """Get package metadata including licence information.
    
    Returns:
        dict: Package metadata with licence details.
    """
    return {
        "name": "PyGremlinBox-LGPL-2.1",
        "version": "0.1.0",
        "licence": "LGPL-2.1",
        "licence_name": "GNU Lesser General Public License v2.1",
        "copyleft": "weak",
        "osi_approved": True,
        "description": "Supply chain security testing package with LGPL-2.1 licence"
    }