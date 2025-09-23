# Copyright [2025] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

from app.shared.exceptions.base import ExternalAPIError, ServiceError
from app.shared.utils.http_client import get_http_client
from app.services.constants import JSON_CONTENT_TYPE
from app.core.settings import settings


async def create_part_asset_and_set_relationship(
    asset_name: str, target_asset_id: str, dph_catalog_id: str, token: str
) -> None:
    """This common method can be called from create data product tools to:
    1. Create a part asset.
    2. Set relationship between the part asset and the target asset.
    """
    # LOGGER.info("Creating ibm_data_product_part asset and setting relationship.")
    DPH_CATALOG_ID = dph_catalog_id

    headers = {
        "Content-Type": JSON_CONTENT_TYPE,
        "Authorization": token,
    }
    json = {
        "metadata": {
            "name": asset_name,
            "asset_type": "ibm_data_product_part",
            "rov": {"mode": 0},
        },
        "entity": {"ibm_data_product_part": {"dataset": True}},
    }
    client = get_http_client()

    try:
        response = await client.post(
            f"{settings.service_url}/v2/assets?catalog_id={DPH_CATALOG_ID}&hide_deprecated_response_fields=false",
            headers=headers,
            data=json,
        )
    except ExternalAPIError:
        raise
    except Exception as e:
        # LOGGER.error(f"Failed to run create_part_asset_and_set_relationship. Error while creating ibm_data_product_part asset in CAMS: {str(e)}")
        raise ServiceError(
            f"Failed to run create_part_asset_and_set_relationship. Error while creating ibm_data_product_part asset in CAMS: {str(e)}"
        )

    data_product_part_asset_id = response["metadata"]["asset_id"]

    # LOGGER.info(
    #     f"Created ibm_data_product_part asset with id {data_product_part_asset_id}."
    # )

    # creating relationship
    json = {
        "relationships": [
            {
                "relationship_name": "has_part",
                "source": {"catalog_id": DPH_CATALOG_ID, "asset_id": target_asset_id},
                "target": {
                    "catalog_id": DPH_CATALOG_ID,
                    "asset_id": data_product_part_asset_id,
                },
            }
        ]
    }

    try:
        response = await client.post(
            f"{settings.service_url}/v2/assets/set_relationships",
            headers=headers,
            data=json,
        )
    except ExternalAPIError:
        raise
    except Exception as e:
        # LOGGER.error(f"Failed to run create_part_asset_and_set_relationship. Error while creating relationship: {str(e)}")
        raise ServiceError(
            f"Failed to run create_part_asset_and_set_relationship. Error while creating relationship: {str(e)}"
        )

    # LOGGER.info(
    #     f"Created relationship between {target_asset_id} and {data_product_part_asset_id}."
    # )
