# Copyright [2025] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.
from ..models.get_lineage_graph_by_cams_id import (
    GetLineageGraphByCamsIdRequest,
    GetLineageGraphByCamsIdResponse,
)
from ..models.lineage_asset import LineageAsset
from .utils import call_get_lineage_graph, convert_to_lineage_id

from app.core.registry import service_registry
from app.services.constants import LINEAGE_UI_BASE_ENDPOINT
from app.core.settings import settings


@service_registry.tool(
    name="lineage:get_lineage_graph_by_cams_id",
    description="""This function takes container_id (this is either catalog_id or project_id) and
                       asset_id as parameters and returns upstream and downstream lineage graph accessible under the url.""",
)
async def get_lineage_graph_by_cams_id(
    request: GetLineageGraphByCamsIdRequest,
) -> GetLineageGraphByCamsIdResponse:
    lineage_id = await convert_to_lineage_id(request.container_id, request.asset_id)

    get_lineage_graph_response = await call_get_lineage_graph(lineage_id)

    assets_in_view = get_lineage_graph_response.get("assets_in_view")
    lineage_assets = list(
        map(lambda asset: LineageAsset.model_validate(asset), assets_in_view)
    )
    url = f"{settings.ui_url}{LINEAGE_UI_BASE_ENDPOINT}/?assetsIds={lineage_id}&startingAssetDirection=upstreamDownstream&numberOfHops=3&assetTypes=deduced&featureFiltersScopeSettingsCloud=false&context=df"
    return GetLineageGraphByCamsIdResponse(lineage_assets=lineage_assets, url=url)
