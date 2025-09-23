# Copyright [2025] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

"""WXO mode detection utility for alternative tool naming convention."""

import importlib.metadata
from functools import lru_cache


@lru_cache(maxsize=1)
def is_wxo_mode_enabled() -> bool:
    """
    Check if WXO mode is enabled by detecting if the wxo optional dependency is installed.

    WXO mode changes tool naming convention from colon-separated to underscore-separated:
    - Standard: "data_product:attach_business_domain_to_data_product"
    - WXO mode: "data_product_attach_business_domain_to_data_product"

    Returns:
        bool: True if WXO mode is enabled, False otherwise
    """
    try:
        # Get the metadata for the installed package
        metadata = importlib.metadata.metadata("data-intelligence-mcp-server")

        # Check if wxo is in the installed extras
        # This is a bit tricky to detect, so we'll use an environment variable approach instead
        import os
        return os.environ.get("DI_WXO_MODE", "false").lower() in ("true", "1", "yes", "on")

    except (importlib.metadata.PackageNotFoundError, Exception):
        # If package not found or any error, default to False
        return False


def transform_tool_name_for_wxo(tool_name: str) -> str:
    """
    Transform tool name from colon-separated to underscore-separated format for WXO mode.

    Args:
        tool_name: Original tool name (e.g., "data_product:attach_business_domain_to_data_product")

    Returns:
        str: Transformed tool name (e.g., "data_product_attach_business_domain_to_data_product")
    """
    if not is_wxo_mode_enabled():
        return tool_name

    # Replace colons with underscores
    return tool_name.replace(":", "_")
