from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.paginated_v1_vehicle_list_list import PaginatedV1VehicleListList
from ...models.vehicles_api_v1_vehicles_list_body_type import check_vehicles_api_v1_vehicles_list_body_type
from ...models.vehicles_api_v1_vehicles_list_body_type import VehiclesApiV1VehiclesListBodyType
from ...models.vehicles_api_v1_vehicles_list_body_types_item import check_vehicles_api_v1_vehicles_list_body_types_item
from ...models.vehicles_api_v1_vehicles_list_body_types_item import VehiclesApiV1VehiclesListBodyTypesItem
from ...models.vehicles_api_v1_vehicles_list_color import check_vehicles_api_v1_vehicles_list_color
from ...models.vehicles_api_v1_vehicles_list_color import VehiclesApiV1VehiclesListColor
from ...models.vehicles_api_v1_vehicles_list_colors_item import check_vehicles_api_v1_vehicles_list_colors_item
from ...models.vehicles_api_v1_vehicles_list_colors_item import VehiclesApiV1VehiclesListColorsItem
from ...models.vehicles_api_v1_vehicles_list_fuel_types_item import check_vehicles_api_v1_vehicles_list_fuel_types_item
from ...models.vehicles_api_v1_vehicles_list_fuel_types_item import VehiclesApiV1VehiclesListFuelTypesItem
from ...models.vehicles_api_v1_vehicles_list_investment_grades_item import (
    check_vehicles_api_v1_vehicles_list_investment_grades_item,
)
from ...models.vehicles_api_v1_vehicles_list_investment_grades_item import VehiclesApiV1VehiclesListInvestmentGradesItem
from ...models.vehicles_api_v1_vehicles_list_risk_level import check_vehicles_api_v1_vehicles_list_risk_level
from ...models.vehicles_api_v1_vehicles_list_risk_level import VehiclesApiV1VehiclesListRiskLevel
from ...models.vehicles_api_v1_vehicles_list_risk_levels_item import (
    check_vehicles_api_v1_vehicles_list_risk_levels_item,
)
from ...models.vehicles_api_v1_vehicles_list_risk_levels_item import VehiclesApiV1VehiclesListRiskLevelsItem
from ...models.vehicles_api_v1_vehicles_list_status import check_vehicles_api_v1_vehicles_list_status
from ...models.vehicles_api_v1_vehicles_list_status import VehiclesApiV1VehiclesListStatus
from ...models.vehicles_api_v1_vehicles_list_transmission import check_vehicles_api_v1_vehicles_list_transmission
from ...models.vehicles_api_v1_vehicles_list_transmission import VehiclesApiV1VehiclesListTransmission
from ...models.vehicles_api_v1_vehicles_list_transmissions_item import (
    check_vehicles_api_v1_vehicles_list_transmissions_item,
)
from ...models.vehicles_api_v1_vehicles_list_transmissions_item import VehiclesApiV1VehiclesListTransmissionsItem
from ...types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import cast, Union
from typing import Union
import datetime


def _get_kwargs(
    *,
    accident_count: Union[Unset, int] = UNSET,
    accident_count_lte: Union[Unset, int] = UNSET,
    body_type: Union[Unset, VehiclesApiV1VehiclesListBodyType] = UNSET,
    body_types: Union[Unset, list[VehiclesApiV1VehiclesListBodyTypesItem]] = UNSET,
    brand: Union[Unset, str] = UNSET,
    brand_code: Union[Unset, str] = UNSET,
    color: Union[Unset, VehiclesApiV1VehiclesListColor] = UNSET,
    colors: Union[Unset, list[VehiclesApiV1VehiclesListColorsItem]] = UNSET,
    country: Union[Unset, str] = UNSET,
    created_after: Union[Unset, datetime.datetime] = UNSET,
    created_before: Union[Unset, datetime.datetime] = UNSET,
    dealer: Union[Unset, str] = UNSET,
    engine_volume_max: Union[Unset, int] = UNSET,
    engine_volume_min: Union[Unset, int] = UNSET,
    fuel_type: Union[Unset, str] = UNSET,
    fuel_types: Union[Unset, list[VehiclesApiV1VehiclesListFuelTypesItem]] = UNSET,
    has_analysis: Union[Unset, bool] = UNSET,
    has_main_photo: Union[Unset, bool] = UNSET,
    has_major_issues: Union[Unset, bool] = UNSET,
    has_photos: Union[Unset, bool] = UNSET,
    high_quality: Union[Unset, bool] = UNSET,
    investment_grade: Union[Unset, str] = UNSET,
    investment_grades: Union[Unset, list[VehiclesApiV1VehiclesListInvestmentGradesItem]] = UNSET,
    listing_id: Union[Unset, str] = UNSET,
    listing_id_icontains: Union[Unset, str] = UNSET,
    location: Union[Unset, str] = UNSET,
    low_risk: Union[Unset, bool] = UNSET,
    mileage_max: Union[Unset, int] = UNSET,
    mileage_range_max: Union[Unset, int] = UNSET,
    mileage_range_min: Union[Unset, int] = UNSET,
    model: Union[Unset, int] = UNSET,
    model_code: Union[Unset, str] = UNSET,
    ordering: Union[Unset, str] = UNSET,
    owner_count: Union[Unset, int] = UNSET,
    owner_count_lte: Union[Unset, int] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    parsed_after: Union[Unset, datetime.datetime] = UNSET,
    price_max: Union[Unset, int] = UNSET,
    price_min: Union[Unset, int] = UNSET,
    price_range_max: Union[Unset, int] = UNSET,
    price_range_min: Union[Unset, int] = UNSET,
    price_usd_max: Union[Unset, float] = UNSET,
    price_usd_min: Union[Unset, float] = UNSET,
    risk_level: Union[Unset, VehiclesApiV1VehiclesListRiskLevel] = UNSET,
    risk_levels: Union[Unset, list[VehiclesApiV1VehiclesListRiskLevelsItem]] = UNSET,
    search: Union[Unset, str] = UNSET,
    source: Union[Unset, str] = UNSET,
    status: Union[Unset, VehiclesApiV1VehiclesListStatus] = UNSET,
    title_icontains: Union[Unset, str] = UNSET,
    transmission: Union[Unset, VehiclesApiV1VehiclesListTransmission] = UNSET,
    transmissions: Union[Unset, list[VehiclesApiV1VehiclesListTransmissionsItem]] = UNSET,
    year: Union[Unset, int] = UNSET,
    year_max: Union[Unset, int] = UNSET,
    year_min: Union[Unset, int] = UNSET,
    year_range_max: Union[None, Unset, int] = UNSET,
    year_range_min: Union[None, Unset, int] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["accident_count"] = accident_count

    params["accident_count__lte"] = accident_count_lte

    json_body_type: Union[Unset, str] = UNSET
    if not isinstance(body_type, Unset):
        json_body_type = body_type

    params["body_type"] = json_body_type

    json_body_types: Union[Unset, list[str]] = UNSET
    if not isinstance(body_types, Unset):
        json_body_types = []
        for body_types_item_data in body_types:
            body_types_item: str = body_types_item_data
            json_body_types.append(body_types_item)

    params["body_types"] = json_body_types

    params["brand"] = brand

    params["brand_code"] = brand_code

    json_color: Union[Unset, str] = UNSET
    if not isinstance(color, Unset):
        json_color = color

    params["color"] = json_color

    json_colors: Union[Unset, list[str]] = UNSET
    if not isinstance(colors, Unset):
        json_colors = []
        for colors_item_data in colors:
            colors_item: str = colors_item_data
            json_colors.append(colors_item)

    params["colors"] = json_colors

    params["country"] = country

    json_created_after: Union[Unset, str] = UNSET
    if not isinstance(created_after, Unset):
        json_created_after = created_after.isoformat()
    params["created_after"] = json_created_after

    json_created_before: Union[Unset, str] = UNSET
    if not isinstance(created_before, Unset):
        json_created_before = created_before.isoformat()
    params["created_before"] = json_created_before

    params["dealer"] = dealer

    params["engine_volume_max"] = engine_volume_max

    params["engine_volume_min"] = engine_volume_min

    params["fuel_type"] = fuel_type

    json_fuel_types: Union[Unset, list[str]] = UNSET
    if not isinstance(fuel_types, Unset):
        json_fuel_types = []
        for fuel_types_item_data in fuel_types:
            fuel_types_item: str = fuel_types_item_data
            json_fuel_types.append(fuel_types_item)

    params["fuel_types"] = json_fuel_types

    params["has_analysis"] = has_analysis

    params["has_main_photo"] = has_main_photo

    params["has_major_issues"] = has_major_issues

    params["has_photos"] = has_photos

    params["high_quality"] = high_quality

    params["investment_grade"] = investment_grade

    json_investment_grades: Union[Unset, list[str]] = UNSET
    if not isinstance(investment_grades, Unset):
        json_investment_grades = []
        for investment_grades_item_data in investment_grades:
            investment_grades_item: str = investment_grades_item_data
            json_investment_grades.append(investment_grades_item)

    params["investment_grades"] = json_investment_grades

    params["listing_id"] = listing_id

    params["listing_id__icontains"] = listing_id_icontains

    params["location"] = location

    params["low_risk"] = low_risk

    params["mileage_max"] = mileage_max

    params["mileage_range_max"] = mileage_range_max

    params["mileage_range_min"] = mileage_range_min

    params["model"] = model

    params["model_code"] = model_code

    params["ordering"] = ordering

    params["owner_count"] = owner_count

    params["owner_count__lte"] = owner_count_lte

    params["page"] = page

    params["page_size"] = page_size

    json_parsed_after: Union[Unset, str] = UNSET
    if not isinstance(parsed_after, Unset):
        json_parsed_after = parsed_after.isoformat()
    params["parsed_after"] = json_parsed_after

    params["price_max"] = price_max

    params["price_min"] = price_min

    params["price_range_max"] = price_range_max

    params["price_range_min"] = price_range_min

    params["price_usd_max"] = price_usd_max

    params["price_usd_min"] = price_usd_min

    json_risk_level: Union[Unset, str] = UNSET
    if not isinstance(risk_level, Unset):
        json_risk_level = risk_level

    params["risk_level"] = json_risk_level

    json_risk_levels: Union[Unset, list[str]] = UNSET
    if not isinstance(risk_levels, Unset):
        json_risk_levels = []
        for risk_levels_item_data in risk_levels:
            risk_levels_item: str = risk_levels_item_data
            json_risk_levels.append(risk_levels_item)

    params["risk_levels"] = json_risk_levels

    params["search"] = search

    params["source"] = source

    json_status: Union[Unset, str] = UNSET
    if not isinstance(status, Unset):
        json_status = status

    params["status"] = json_status

    params["title__icontains"] = title_icontains

    json_transmission: Union[Unset, str] = UNSET
    if not isinstance(transmission, Unset):
        json_transmission = transmission

    params["transmission"] = json_transmission

    json_transmissions: Union[Unset, list[str]] = UNSET
    if not isinstance(transmissions, Unset):
        json_transmissions = []
        for transmissions_item_data in transmissions:
            transmissions_item: str = transmissions_item_data
            json_transmissions.append(transmissions_item)

    params["transmissions"] = json_transmissions

    params["year"] = year

    params["year_max"] = year_max

    params["year_min"] = year_min

    json_year_range_max: Union[None, Unset, int]
    if isinstance(year_range_max, Unset):
        json_year_range_max = UNSET
    else:
        json_year_range_max = year_range_max
    params["year_range_max"] = json_year_range_max

    json_year_range_min: Union[None, Unset, int]
    if isinstance(year_range_min, Unset):
        json_year_range_min = UNSET
    else:
        json_year_range_min = year_range_min
    params["year_range_min"] = json_year_range_min

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/vehicles_api/v1/vehicles/",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[PaginatedV1VehicleListList]:
    if response.status_code == 200:
        response_200 = PaginatedV1VehicleListList.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[PaginatedV1VehicleListList]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    accident_count: Union[Unset, int] = UNSET,
    accident_count_lte: Union[Unset, int] = UNSET,
    body_type: Union[Unset, VehiclesApiV1VehiclesListBodyType] = UNSET,
    body_types: Union[Unset, list[VehiclesApiV1VehiclesListBodyTypesItem]] = UNSET,
    brand: Union[Unset, str] = UNSET,
    brand_code: Union[Unset, str] = UNSET,
    color: Union[Unset, VehiclesApiV1VehiclesListColor] = UNSET,
    colors: Union[Unset, list[VehiclesApiV1VehiclesListColorsItem]] = UNSET,
    country: Union[Unset, str] = UNSET,
    created_after: Union[Unset, datetime.datetime] = UNSET,
    created_before: Union[Unset, datetime.datetime] = UNSET,
    dealer: Union[Unset, str] = UNSET,
    engine_volume_max: Union[Unset, int] = UNSET,
    engine_volume_min: Union[Unset, int] = UNSET,
    fuel_type: Union[Unset, str] = UNSET,
    fuel_types: Union[Unset, list[VehiclesApiV1VehiclesListFuelTypesItem]] = UNSET,
    has_analysis: Union[Unset, bool] = UNSET,
    has_main_photo: Union[Unset, bool] = UNSET,
    has_major_issues: Union[Unset, bool] = UNSET,
    has_photos: Union[Unset, bool] = UNSET,
    high_quality: Union[Unset, bool] = UNSET,
    investment_grade: Union[Unset, str] = UNSET,
    investment_grades: Union[Unset, list[VehiclesApiV1VehiclesListInvestmentGradesItem]] = UNSET,
    listing_id: Union[Unset, str] = UNSET,
    listing_id_icontains: Union[Unset, str] = UNSET,
    location: Union[Unset, str] = UNSET,
    low_risk: Union[Unset, bool] = UNSET,
    mileage_max: Union[Unset, int] = UNSET,
    mileage_range_max: Union[Unset, int] = UNSET,
    mileage_range_min: Union[Unset, int] = UNSET,
    model: Union[Unset, int] = UNSET,
    model_code: Union[Unset, str] = UNSET,
    ordering: Union[Unset, str] = UNSET,
    owner_count: Union[Unset, int] = UNSET,
    owner_count_lte: Union[Unset, int] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    parsed_after: Union[Unset, datetime.datetime] = UNSET,
    price_max: Union[Unset, int] = UNSET,
    price_min: Union[Unset, int] = UNSET,
    price_range_max: Union[Unset, int] = UNSET,
    price_range_min: Union[Unset, int] = UNSET,
    price_usd_max: Union[Unset, float] = UNSET,
    price_usd_min: Union[Unset, float] = UNSET,
    risk_level: Union[Unset, VehiclesApiV1VehiclesListRiskLevel] = UNSET,
    risk_levels: Union[Unset, list[VehiclesApiV1VehiclesListRiskLevelsItem]] = UNSET,
    search: Union[Unset, str] = UNSET,
    source: Union[Unset, str] = UNSET,
    status: Union[Unset, VehiclesApiV1VehiclesListStatus] = UNSET,
    title_icontains: Union[Unset, str] = UNSET,
    transmission: Union[Unset, VehiclesApiV1VehiclesListTransmission] = UNSET,
    transmissions: Union[Unset, list[VehiclesApiV1VehiclesListTransmissionsItem]] = UNSET,
    year: Union[Unset, int] = UNSET,
    year_max: Union[Unset, int] = UNSET,
    year_min: Union[Unset, int] = UNSET,
    year_range_max: Union[None, Unset, int] = UNSET,
    year_range_min: Union[None, Unset, int] = UNSET,
) -> Response[PaginatedV1VehicleListList]:
    """List vehicles


            Get paginated list of vehicles with advanced filtering.

            Supports filtering by:
            - Brand, model, source
            - Year, price, mileage ranges
            - Fuel type, transmission, body type
            - Investment grade, risk level
            - Location, dealer
            - Photo availability, LLM analysis

            Full-text search across title, brand, model, location.


    Args:
        accident_count (Union[Unset, int]):
        accident_count_lte (Union[Unset, int]):
        body_type (Union[Unset, VehiclesApiV1VehiclesListBodyType]):
        body_types (Union[Unset, list[VehiclesApiV1VehiclesListBodyTypesItem]]):
        brand (Union[Unset, str]):
        brand_code (Union[Unset, str]):
        color (Union[Unset, VehiclesApiV1VehiclesListColor]):
        colors (Union[Unset, list[VehiclesApiV1VehiclesListColorsItem]]):
        country (Union[Unset, str]):
        created_after (Union[Unset, datetime.datetime]):
        created_before (Union[Unset, datetime.datetime]):
        dealer (Union[Unset, str]):
        engine_volume_max (Union[Unset, int]):
        engine_volume_min (Union[Unset, int]):
        fuel_type (Union[Unset, str]):
        fuel_types (Union[Unset, list[VehiclesApiV1VehiclesListFuelTypesItem]]):
        has_analysis (Union[Unset, bool]):
        has_main_photo (Union[Unset, bool]):
        has_major_issues (Union[Unset, bool]):
        has_photos (Union[Unset, bool]):
        high_quality (Union[Unset, bool]):
        investment_grade (Union[Unset, str]):
        investment_grades (Union[Unset, list[VehiclesApiV1VehiclesListInvestmentGradesItem]]):
        listing_id (Union[Unset, str]):
        listing_id_icontains (Union[Unset, str]):
        location (Union[Unset, str]):
        low_risk (Union[Unset, bool]):
        mileage_max (Union[Unset, int]):
        mileage_range_max (Union[Unset, int]):
        mileage_range_min (Union[Unset, int]):
        model (Union[Unset, int]):
        model_code (Union[Unset, str]):
        ordering (Union[Unset, str]):
        owner_count (Union[Unset, int]):
        owner_count_lte (Union[Unset, int]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        parsed_after (Union[Unset, datetime.datetime]):
        price_max (Union[Unset, int]):
        price_min (Union[Unset, int]):
        price_range_max (Union[Unset, int]):
        price_range_min (Union[Unset, int]):
        price_usd_max (Union[Unset, float]):
        price_usd_min (Union[Unset, float]):
        risk_level (Union[Unset, VehiclesApiV1VehiclesListRiskLevel]):
        risk_levels (Union[Unset, list[VehiclesApiV1VehiclesListRiskLevelsItem]]):
        search (Union[Unset, str]):
        source (Union[Unset, str]):
        status (Union[Unset, VehiclesApiV1VehiclesListStatus]):
        title_icontains (Union[Unset, str]):
        transmission (Union[Unset, VehiclesApiV1VehiclesListTransmission]):
        transmissions (Union[Unset, list[VehiclesApiV1VehiclesListTransmissionsItem]]):
        year (Union[Unset, int]):
        year_max (Union[Unset, int]):
        year_min (Union[Unset, int]):
        year_range_max (Union[None, Unset, int]):
        year_range_min (Union[None, Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedV1VehicleListList]
    """

    kwargs = _get_kwargs(
        accident_count=accident_count,
        accident_count_lte=accident_count_lte,
        body_type=body_type,
        body_types=body_types,
        brand=brand,
        brand_code=brand_code,
        color=color,
        colors=colors,
        country=country,
        created_after=created_after,
        created_before=created_before,
        dealer=dealer,
        engine_volume_max=engine_volume_max,
        engine_volume_min=engine_volume_min,
        fuel_type=fuel_type,
        fuel_types=fuel_types,
        has_analysis=has_analysis,
        has_main_photo=has_main_photo,
        has_major_issues=has_major_issues,
        has_photos=has_photos,
        high_quality=high_quality,
        investment_grade=investment_grade,
        investment_grades=investment_grades,
        listing_id=listing_id,
        listing_id_icontains=listing_id_icontains,
        location=location,
        low_risk=low_risk,
        mileage_max=mileage_max,
        mileage_range_max=mileage_range_max,
        mileage_range_min=mileage_range_min,
        model=model,
        model_code=model_code,
        ordering=ordering,
        owner_count=owner_count,
        owner_count_lte=owner_count_lte,
        page=page,
        page_size=page_size,
        parsed_after=parsed_after,
        price_max=price_max,
        price_min=price_min,
        price_range_max=price_range_max,
        price_range_min=price_range_min,
        price_usd_max=price_usd_max,
        price_usd_min=price_usd_min,
        risk_level=risk_level,
        risk_levels=risk_levels,
        search=search,
        source=source,
        status=status,
        title_icontains=title_icontains,
        transmission=transmission,
        transmissions=transmissions,
        year=year,
        year_max=year_max,
        year_min=year_min,
        year_range_max=year_range_max,
        year_range_min=year_range_min,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    accident_count: Union[Unset, int] = UNSET,
    accident_count_lte: Union[Unset, int] = UNSET,
    body_type: Union[Unset, VehiclesApiV1VehiclesListBodyType] = UNSET,
    body_types: Union[Unset, list[VehiclesApiV1VehiclesListBodyTypesItem]] = UNSET,
    brand: Union[Unset, str] = UNSET,
    brand_code: Union[Unset, str] = UNSET,
    color: Union[Unset, VehiclesApiV1VehiclesListColor] = UNSET,
    colors: Union[Unset, list[VehiclesApiV1VehiclesListColorsItem]] = UNSET,
    country: Union[Unset, str] = UNSET,
    created_after: Union[Unset, datetime.datetime] = UNSET,
    created_before: Union[Unset, datetime.datetime] = UNSET,
    dealer: Union[Unset, str] = UNSET,
    engine_volume_max: Union[Unset, int] = UNSET,
    engine_volume_min: Union[Unset, int] = UNSET,
    fuel_type: Union[Unset, str] = UNSET,
    fuel_types: Union[Unset, list[VehiclesApiV1VehiclesListFuelTypesItem]] = UNSET,
    has_analysis: Union[Unset, bool] = UNSET,
    has_main_photo: Union[Unset, bool] = UNSET,
    has_major_issues: Union[Unset, bool] = UNSET,
    has_photos: Union[Unset, bool] = UNSET,
    high_quality: Union[Unset, bool] = UNSET,
    investment_grade: Union[Unset, str] = UNSET,
    investment_grades: Union[Unset, list[VehiclesApiV1VehiclesListInvestmentGradesItem]] = UNSET,
    listing_id: Union[Unset, str] = UNSET,
    listing_id_icontains: Union[Unset, str] = UNSET,
    location: Union[Unset, str] = UNSET,
    low_risk: Union[Unset, bool] = UNSET,
    mileage_max: Union[Unset, int] = UNSET,
    mileage_range_max: Union[Unset, int] = UNSET,
    mileage_range_min: Union[Unset, int] = UNSET,
    model: Union[Unset, int] = UNSET,
    model_code: Union[Unset, str] = UNSET,
    ordering: Union[Unset, str] = UNSET,
    owner_count: Union[Unset, int] = UNSET,
    owner_count_lte: Union[Unset, int] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    parsed_after: Union[Unset, datetime.datetime] = UNSET,
    price_max: Union[Unset, int] = UNSET,
    price_min: Union[Unset, int] = UNSET,
    price_range_max: Union[Unset, int] = UNSET,
    price_range_min: Union[Unset, int] = UNSET,
    price_usd_max: Union[Unset, float] = UNSET,
    price_usd_min: Union[Unset, float] = UNSET,
    risk_level: Union[Unset, VehiclesApiV1VehiclesListRiskLevel] = UNSET,
    risk_levels: Union[Unset, list[VehiclesApiV1VehiclesListRiskLevelsItem]] = UNSET,
    search: Union[Unset, str] = UNSET,
    source: Union[Unset, str] = UNSET,
    status: Union[Unset, VehiclesApiV1VehiclesListStatus] = UNSET,
    title_icontains: Union[Unset, str] = UNSET,
    transmission: Union[Unset, VehiclesApiV1VehiclesListTransmission] = UNSET,
    transmissions: Union[Unset, list[VehiclesApiV1VehiclesListTransmissionsItem]] = UNSET,
    year: Union[Unset, int] = UNSET,
    year_max: Union[Unset, int] = UNSET,
    year_min: Union[Unset, int] = UNSET,
    year_range_max: Union[None, Unset, int] = UNSET,
    year_range_min: Union[None, Unset, int] = UNSET,
) -> Optional[PaginatedV1VehicleListList]:
    """List vehicles


            Get paginated list of vehicles with advanced filtering.

            Supports filtering by:
            - Brand, model, source
            - Year, price, mileage ranges
            - Fuel type, transmission, body type
            - Investment grade, risk level
            - Location, dealer
            - Photo availability, LLM analysis

            Full-text search across title, brand, model, location.


    Args:
        accident_count (Union[Unset, int]):
        accident_count_lte (Union[Unset, int]):
        body_type (Union[Unset, VehiclesApiV1VehiclesListBodyType]):
        body_types (Union[Unset, list[VehiclesApiV1VehiclesListBodyTypesItem]]):
        brand (Union[Unset, str]):
        brand_code (Union[Unset, str]):
        color (Union[Unset, VehiclesApiV1VehiclesListColor]):
        colors (Union[Unset, list[VehiclesApiV1VehiclesListColorsItem]]):
        country (Union[Unset, str]):
        created_after (Union[Unset, datetime.datetime]):
        created_before (Union[Unset, datetime.datetime]):
        dealer (Union[Unset, str]):
        engine_volume_max (Union[Unset, int]):
        engine_volume_min (Union[Unset, int]):
        fuel_type (Union[Unset, str]):
        fuel_types (Union[Unset, list[VehiclesApiV1VehiclesListFuelTypesItem]]):
        has_analysis (Union[Unset, bool]):
        has_main_photo (Union[Unset, bool]):
        has_major_issues (Union[Unset, bool]):
        has_photos (Union[Unset, bool]):
        high_quality (Union[Unset, bool]):
        investment_grade (Union[Unset, str]):
        investment_grades (Union[Unset, list[VehiclesApiV1VehiclesListInvestmentGradesItem]]):
        listing_id (Union[Unset, str]):
        listing_id_icontains (Union[Unset, str]):
        location (Union[Unset, str]):
        low_risk (Union[Unset, bool]):
        mileage_max (Union[Unset, int]):
        mileage_range_max (Union[Unset, int]):
        mileage_range_min (Union[Unset, int]):
        model (Union[Unset, int]):
        model_code (Union[Unset, str]):
        ordering (Union[Unset, str]):
        owner_count (Union[Unset, int]):
        owner_count_lte (Union[Unset, int]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        parsed_after (Union[Unset, datetime.datetime]):
        price_max (Union[Unset, int]):
        price_min (Union[Unset, int]):
        price_range_max (Union[Unset, int]):
        price_range_min (Union[Unset, int]):
        price_usd_max (Union[Unset, float]):
        price_usd_min (Union[Unset, float]):
        risk_level (Union[Unset, VehiclesApiV1VehiclesListRiskLevel]):
        risk_levels (Union[Unset, list[VehiclesApiV1VehiclesListRiskLevelsItem]]):
        search (Union[Unset, str]):
        source (Union[Unset, str]):
        status (Union[Unset, VehiclesApiV1VehiclesListStatus]):
        title_icontains (Union[Unset, str]):
        transmission (Union[Unset, VehiclesApiV1VehiclesListTransmission]):
        transmissions (Union[Unset, list[VehiclesApiV1VehiclesListTransmissionsItem]]):
        year (Union[Unset, int]):
        year_max (Union[Unset, int]):
        year_min (Union[Unset, int]):
        year_range_max (Union[None, Unset, int]):
        year_range_min (Union[None, Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedV1VehicleListList
    """

    return sync_detailed(
        client=client,
        accident_count=accident_count,
        accident_count_lte=accident_count_lte,
        body_type=body_type,
        body_types=body_types,
        brand=brand,
        brand_code=brand_code,
        color=color,
        colors=colors,
        country=country,
        created_after=created_after,
        created_before=created_before,
        dealer=dealer,
        engine_volume_max=engine_volume_max,
        engine_volume_min=engine_volume_min,
        fuel_type=fuel_type,
        fuel_types=fuel_types,
        has_analysis=has_analysis,
        has_main_photo=has_main_photo,
        has_major_issues=has_major_issues,
        has_photos=has_photos,
        high_quality=high_quality,
        investment_grade=investment_grade,
        investment_grades=investment_grades,
        listing_id=listing_id,
        listing_id_icontains=listing_id_icontains,
        location=location,
        low_risk=low_risk,
        mileage_max=mileage_max,
        mileage_range_max=mileage_range_max,
        mileage_range_min=mileage_range_min,
        model=model,
        model_code=model_code,
        ordering=ordering,
        owner_count=owner_count,
        owner_count_lte=owner_count_lte,
        page=page,
        page_size=page_size,
        parsed_after=parsed_after,
        price_max=price_max,
        price_min=price_min,
        price_range_max=price_range_max,
        price_range_min=price_range_min,
        price_usd_max=price_usd_max,
        price_usd_min=price_usd_min,
        risk_level=risk_level,
        risk_levels=risk_levels,
        search=search,
        source=source,
        status=status,
        title_icontains=title_icontains,
        transmission=transmission,
        transmissions=transmissions,
        year=year,
        year_max=year_max,
        year_min=year_min,
        year_range_max=year_range_max,
        year_range_min=year_range_min,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    accident_count: Union[Unset, int] = UNSET,
    accident_count_lte: Union[Unset, int] = UNSET,
    body_type: Union[Unset, VehiclesApiV1VehiclesListBodyType] = UNSET,
    body_types: Union[Unset, list[VehiclesApiV1VehiclesListBodyTypesItem]] = UNSET,
    brand: Union[Unset, str] = UNSET,
    brand_code: Union[Unset, str] = UNSET,
    color: Union[Unset, VehiclesApiV1VehiclesListColor] = UNSET,
    colors: Union[Unset, list[VehiclesApiV1VehiclesListColorsItem]] = UNSET,
    country: Union[Unset, str] = UNSET,
    created_after: Union[Unset, datetime.datetime] = UNSET,
    created_before: Union[Unset, datetime.datetime] = UNSET,
    dealer: Union[Unset, str] = UNSET,
    engine_volume_max: Union[Unset, int] = UNSET,
    engine_volume_min: Union[Unset, int] = UNSET,
    fuel_type: Union[Unset, str] = UNSET,
    fuel_types: Union[Unset, list[VehiclesApiV1VehiclesListFuelTypesItem]] = UNSET,
    has_analysis: Union[Unset, bool] = UNSET,
    has_main_photo: Union[Unset, bool] = UNSET,
    has_major_issues: Union[Unset, bool] = UNSET,
    has_photos: Union[Unset, bool] = UNSET,
    high_quality: Union[Unset, bool] = UNSET,
    investment_grade: Union[Unset, str] = UNSET,
    investment_grades: Union[Unset, list[VehiclesApiV1VehiclesListInvestmentGradesItem]] = UNSET,
    listing_id: Union[Unset, str] = UNSET,
    listing_id_icontains: Union[Unset, str] = UNSET,
    location: Union[Unset, str] = UNSET,
    low_risk: Union[Unset, bool] = UNSET,
    mileage_max: Union[Unset, int] = UNSET,
    mileage_range_max: Union[Unset, int] = UNSET,
    mileage_range_min: Union[Unset, int] = UNSET,
    model: Union[Unset, int] = UNSET,
    model_code: Union[Unset, str] = UNSET,
    ordering: Union[Unset, str] = UNSET,
    owner_count: Union[Unset, int] = UNSET,
    owner_count_lte: Union[Unset, int] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    parsed_after: Union[Unset, datetime.datetime] = UNSET,
    price_max: Union[Unset, int] = UNSET,
    price_min: Union[Unset, int] = UNSET,
    price_range_max: Union[Unset, int] = UNSET,
    price_range_min: Union[Unset, int] = UNSET,
    price_usd_max: Union[Unset, float] = UNSET,
    price_usd_min: Union[Unset, float] = UNSET,
    risk_level: Union[Unset, VehiclesApiV1VehiclesListRiskLevel] = UNSET,
    risk_levels: Union[Unset, list[VehiclesApiV1VehiclesListRiskLevelsItem]] = UNSET,
    search: Union[Unset, str] = UNSET,
    source: Union[Unset, str] = UNSET,
    status: Union[Unset, VehiclesApiV1VehiclesListStatus] = UNSET,
    title_icontains: Union[Unset, str] = UNSET,
    transmission: Union[Unset, VehiclesApiV1VehiclesListTransmission] = UNSET,
    transmissions: Union[Unset, list[VehiclesApiV1VehiclesListTransmissionsItem]] = UNSET,
    year: Union[Unset, int] = UNSET,
    year_max: Union[Unset, int] = UNSET,
    year_min: Union[Unset, int] = UNSET,
    year_range_max: Union[None, Unset, int] = UNSET,
    year_range_min: Union[None, Unset, int] = UNSET,
) -> Response[PaginatedV1VehicleListList]:
    """List vehicles


            Get paginated list of vehicles with advanced filtering.

            Supports filtering by:
            - Brand, model, source
            - Year, price, mileage ranges
            - Fuel type, transmission, body type
            - Investment grade, risk level
            - Location, dealer
            - Photo availability, LLM analysis

            Full-text search across title, brand, model, location.


    Args:
        accident_count (Union[Unset, int]):
        accident_count_lte (Union[Unset, int]):
        body_type (Union[Unset, VehiclesApiV1VehiclesListBodyType]):
        body_types (Union[Unset, list[VehiclesApiV1VehiclesListBodyTypesItem]]):
        brand (Union[Unset, str]):
        brand_code (Union[Unset, str]):
        color (Union[Unset, VehiclesApiV1VehiclesListColor]):
        colors (Union[Unset, list[VehiclesApiV1VehiclesListColorsItem]]):
        country (Union[Unset, str]):
        created_after (Union[Unset, datetime.datetime]):
        created_before (Union[Unset, datetime.datetime]):
        dealer (Union[Unset, str]):
        engine_volume_max (Union[Unset, int]):
        engine_volume_min (Union[Unset, int]):
        fuel_type (Union[Unset, str]):
        fuel_types (Union[Unset, list[VehiclesApiV1VehiclesListFuelTypesItem]]):
        has_analysis (Union[Unset, bool]):
        has_main_photo (Union[Unset, bool]):
        has_major_issues (Union[Unset, bool]):
        has_photos (Union[Unset, bool]):
        high_quality (Union[Unset, bool]):
        investment_grade (Union[Unset, str]):
        investment_grades (Union[Unset, list[VehiclesApiV1VehiclesListInvestmentGradesItem]]):
        listing_id (Union[Unset, str]):
        listing_id_icontains (Union[Unset, str]):
        location (Union[Unset, str]):
        low_risk (Union[Unset, bool]):
        mileage_max (Union[Unset, int]):
        mileage_range_max (Union[Unset, int]):
        mileage_range_min (Union[Unset, int]):
        model (Union[Unset, int]):
        model_code (Union[Unset, str]):
        ordering (Union[Unset, str]):
        owner_count (Union[Unset, int]):
        owner_count_lte (Union[Unset, int]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        parsed_after (Union[Unset, datetime.datetime]):
        price_max (Union[Unset, int]):
        price_min (Union[Unset, int]):
        price_range_max (Union[Unset, int]):
        price_range_min (Union[Unset, int]):
        price_usd_max (Union[Unset, float]):
        price_usd_min (Union[Unset, float]):
        risk_level (Union[Unset, VehiclesApiV1VehiclesListRiskLevel]):
        risk_levels (Union[Unset, list[VehiclesApiV1VehiclesListRiskLevelsItem]]):
        search (Union[Unset, str]):
        source (Union[Unset, str]):
        status (Union[Unset, VehiclesApiV1VehiclesListStatus]):
        title_icontains (Union[Unset, str]):
        transmission (Union[Unset, VehiclesApiV1VehiclesListTransmission]):
        transmissions (Union[Unset, list[VehiclesApiV1VehiclesListTransmissionsItem]]):
        year (Union[Unset, int]):
        year_max (Union[Unset, int]):
        year_min (Union[Unset, int]):
        year_range_max (Union[None, Unset, int]):
        year_range_min (Union[None, Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedV1VehicleListList]
    """

    kwargs = _get_kwargs(
        accident_count=accident_count,
        accident_count_lte=accident_count_lte,
        body_type=body_type,
        body_types=body_types,
        brand=brand,
        brand_code=brand_code,
        color=color,
        colors=colors,
        country=country,
        created_after=created_after,
        created_before=created_before,
        dealer=dealer,
        engine_volume_max=engine_volume_max,
        engine_volume_min=engine_volume_min,
        fuel_type=fuel_type,
        fuel_types=fuel_types,
        has_analysis=has_analysis,
        has_main_photo=has_main_photo,
        has_major_issues=has_major_issues,
        has_photos=has_photos,
        high_quality=high_quality,
        investment_grade=investment_grade,
        investment_grades=investment_grades,
        listing_id=listing_id,
        listing_id_icontains=listing_id_icontains,
        location=location,
        low_risk=low_risk,
        mileage_max=mileage_max,
        mileage_range_max=mileage_range_max,
        mileage_range_min=mileage_range_min,
        model=model,
        model_code=model_code,
        ordering=ordering,
        owner_count=owner_count,
        owner_count_lte=owner_count_lte,
        page=page,
        page_size=page_size,
        parsed_after=parsed_after,
        price_max=price_max,
        price_min=price_min,
        price_range_max=price_range_max,
        price_range_min=price_range_min,
        price_usd_max=price_usd_max,
        price_usd_min=price_usd_min,
        risk_level=risk_level,
        risk_levels=risk_levels,
        search=search,
        source=source,
        status=status,
        title_icontains=title_icontains,
        transmission=transmission,
        transmissions=transmissions,
        year=year,
        year_max=year_max,
        year_min=year_min,
        year_range_max=year_range_max,
        year_range_min=year_range_min,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    accident_count: Union[Unset, int] = UNSET,
    accident_count_lte: Union[Unset, int] = UNSET,
    body_type: Union[Unset, VehiclesApiV1VehiclesListBodyType] = UNSET,
    body_types: Union[Unset, list[VehiclesApiV1VehiclesListBodyTypesItem]] = UNSET,
    brand: Union[Unset, str] = UNSET,
    brand_code: Union[Unset, str] = UNSET,
    color: Union[Unset, VehiclesApiV1VehiclesListColor] = UNSET,
    colors: Union[Unset, list[VehiclesApiV1VehiclesListColorsItem]] = UNSET,
    country: Union[Unset, str] = UNSET,
    created_after: Union[Unset, datetime.datetime] = UNSET,
    created_before: Union[Unset, datetime.datetime] = UNSET,
    dealer: Union[Unset, str] = UNSET,
    engine_volume_max: Union[Unset, int] = UNSET,
    engine_volume_min: Union[Unset, int] = UNSET,
    fuel_type: Union[Unset, str] = UNSET,
    fuel_types: Union[Unset, list[VehiclesApiV1VehiclesListFuelTypesItem]] = UNSET,
    has_analysis: Union[Unset, bool] = UNSET,
    has_main_photo: Union[Unset, bool] = UNSET,
    has_major_issues: Union[Unset, bool] = UNSET,
    has_photos: Union[Unset, bool] = UNSET,
    high_quality: Union[Unset, bool] = UNSET,
    investment_grade: Union[Unset, str] = UNSET,
    investment_grades: Union[Unset, list[VehiclesApiV1VehiclesListInvestmentGradesItem]] = UNSET,
    listing_id: Union[Unset, str] = UNSET,
    listing_id_icontains: Union[Unset, str] = UNSET,
    location: Union[Unset, str] = UNSET,
    low_risk: Union[Unset, bool] = UNSET,
    mileage_max: Union[Unset, int] = UNSET,
    mileage_range_max: Union[Unset, int] = UNSET,
    mileage_range_min: Union[Unset, int] = UNSET,
    model: Union[Unset, int] = UNSET,
    model_code: Union[Unset, str] = UNSET,
    ordering: Union[Unset, str] = UNSET,
    owner_count: Union[Unset, int] = UNSET,
    owner_count_lte: Union[Unset, int] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    parsed_after: Union[Unset, datetime.datetime] = UNSET,
    price_max: Union[Unset, int] = UNSET,
    price_min: Union[Unset, int] = UNSET,
    price_range_max: Union[Unset, int] = UNSET,
    price_range_min: Union[Unset, int] = UNSET,
    price_usd_max: Union[Unset, float] = UNSET,
    price_usd_min: Union[Unset, float] = UNSET,
    risk_level: Union[Unset, VehiclesApiV1VehiclesListRiskLevel] = UNSET,
    risk_levels: Union[Unset, list[VehiclesApiV1VehiclesListRiskLevelsItem]] = UNSET,
    search: Union[Unset, str] = UNSET,
    source: Union[Unset, str] = UNSET,
    status: Union[Unset, VehiclesApiV1VehiclesListStatus] = UNSET,
    title_icontains: Union[Unset, str] = UNSET,
    transmission: Union[Unset, VehiclesApiV1VehiclesListTransmission] = UNSET,
    transmissions: Union[Unset, list[VehiclesApiV1VehiclesListTransmissionsItem]] = UNSET,
    year: Union[Unset, int] = UNSET,
    year_max: Union[Unset, int] = UNSET,
    year_min: Union[Unset, int] = UNSET,
    year_range_max: Union[None, Unset, int] = UNSET,
    year_range_min: Union[None, Unset, int] = UNSET,
) -> Optional[PaginatedV1VehicleListList]:
    """List vehicles


            Get paginated list of vehicles with advanced filtering.

            Supports filtering by:
            - Brand, model, source
            - Year, price, mileage ranges
            - Fuel type, transmission, body type
            - Investment grade, risk level
            - Location, dealer
            - Photo availability, LLM analysis

            Full-text search across title, brand, model, location.


    Args:
        accident_count (Union[Unset, int]):
        accident_count_lte (Union[Unset, int]):
        body_type (Union[Unset, VehiclesApiV1VehiclesListBodyType]):
        body_types (Union[Unset, list[VehiclesApiV1VehiclesListBodyTypesItem]]):
        brand (Union[Unset, str]):
        brand_code (Union[Unset, str]):
        color (Union[Unset, VehiclesApiV1VehiclesListColor]):
        colors (Union[Unset, list[VehiclesApiV1VehiclesListColorsItem]]):
        country (Union[Unset, str]):
        created_after (Union[Unset, datetime.datetime]):
        created_before (Union[Unset, datetime.datetime]):
        dealer (Union[Unset, str]):
        engine_volume_max (Union[Unset, int]):
        engine_volume_min (Union[Unset, int]):
        fuel_type (Union[Unset, str]):
        fuel_types (Union[Unset, list[VehiclesApiV1VehiclesListFuelTypesItem]]):
        has_analysis (Union[Unset, bool]):
        has_main_photo (Union[Unset, bool]):
        has_major_issues (Union[Unset, bool]):
        has_photos (Union[Unset, bool]):
        high_quality (Union[Unset, bool]):
        investment_grade (Union[Unset, str]):
        investment_grades (Union[Unset, list[VehiclesApiV1VehiclesListInvestmentGradesItem]]):
        listing_id (Union[Unset, str]):
        listing_id_icontains (Union[Unset, str]):
        location (Union[Unset, str]):
        low_risk (Union[Unset, bool]):
        mileage_max (Union[Unset, int]):
        mileage_range_max (Union[Unset, int]):
        mileage_range_min (Union[Unset, int]):
        model (Union[Unset, int]):
        model_code (Union[Unset, str]):
        ordering (Union[Unset, str]):
        owner_count (Union[Unset, int]):
        owner_count_lte (Union[Unset, int]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        parsed_after (Union[Unset, datetime.datetime]):
        price_max (Union[Unset, int]):
        price_min (Union[Unset, int]):
        price_range_max (Union[Unset, int]):
        price_range_min (Union[Unset, int]):
        price_usd_max (Union[Unset, float]):
        price_usd_min (Union[Unset, float]):
        risk_level (Union[Unset, VehiclesApiV1VehiclesListRiskLevel]):
        risk_levels (Union[Unset, list[VehiclesApiV1VehiclesListRiskLevelsItem]]):
        search (Union[Unset, str]):
        source (Union[Unset, str]):
        status (Union[Unset, VehiclesApiV1VehiclesListStatus]):
        title_icontains (Union[Unset, str]):
        transmission (Union[Unset, VehiclesApiV1VehiclesListTransmission]):
        transmissions (Union[Unset, list[VehiclesApiV1VehiclesListTransmissionsItem]]):
        year (Union[Unset, int]):
        year_max (Union[Unset, int]):
        year_min (Union[Unset, int]):
        year_range_max (Union[None, Unset, int]):
        year_range_min (Union[None, Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedV1VehicleListList
    """

    return (
        await asyncio_detailed(
            client=client,
            accident_count=accident_count,
            accident_count_lte=accident_count_lte,
            body_type=body_type,
            body_types=body_types,
            brand=brand,
            brand_code=brand_code,
            color=color,
            colors=colors,
            country=country,
            created_after=created_after,
            created_before=created_before,
            dealer=dealer,
            engine_volume_max=engine_volume_max,
            engine_volume_min=engine_volume_min,
            fuel_type=fuel_type,
            fuel_types=fuel_types,
            has_analysis=has_analysis,
            has_main_photo=has_main_photo,
            has_major_issues=has_major_issues,
            has_photos=has_photos,
            high_quality=high_quality,
            investment_grade=investment_grade,
            investment_grades=investment_grades,
            listing_id=listing_id,
            listing_id_icontains=listing_id_icontains,
            location=location,
            low_risk=low_risk,
            mileage_max=mileage_max,
            mileage_range_max=mileage_range_max,
            mileage_range_min=mileage_range_min,
            model=model,
            model_code=model_code,
            ordering=ordering,
            owner_count=owner_count,
            owner_count_lte=owner_count_lte,
            page=page,
            page_size=page_size,
            parsed_after=parsed_after,
            price_max=price_max,
            price_min=price_min,
            price_range_max=price_range_max,
            price_range_min=price_range_min,
            price_usd_max=price_usd_max,
            price_usd_min=price_usd_min,
            risk_level=risk_level,
            risk_levels=risk_levels,
            search=search,
            source=source,
            status=status,
            title_icontains=title_icontains,
            transmission=transmission,
            transmissions=transmissions,
            year=year,
            year_max=year_max,
            year_min=year_min,
            year_range_max=year_range_max,
            year_range_min=year_range_min,
        )
    ).parsed
