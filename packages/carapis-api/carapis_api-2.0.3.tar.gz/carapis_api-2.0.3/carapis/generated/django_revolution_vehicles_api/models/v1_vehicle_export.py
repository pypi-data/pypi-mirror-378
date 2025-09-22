from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.v1_vehicle_export_body_type import check_v1_vehicle_export_body_type
from ..models.v1_vehicle_export_body_type import V1VehicleExportBodyType
from ..models.v1_vehicle_export_color import check_v1_vehicle_export_color
from ..models.v1_vehicle_export_color import V1VehicleExportColor
from ..models.v1_vehicle_export_fuel_type import check_v1_vehicle_export_fuel_type
from ..models.v1_vehicle_export_fuel_type import V1VehicleExportFuelType
from ..models.v1_vehicle_export_investment_grade import check_v1_vehicle_export_investment_grade
from ..models.v1_vehicle_export_investment_grade import V1VehicleExportInvestmentGrade
from ..models.v1_vehicle_export_price_currency import check_v1_vehicle_export_price_currency
from ..models.v1_vehicle_export_price_currency import V1VehicleExportPriceCurrency
from ..models.v1_vehicle_export_risk_level import check_v1_vehicle_export_risk_level
from ..models.v1_vehicle_export_risk_level import V1VehicleExportRiskLevel
from ..models.v1_vehicle_export_status import check_v1_vehicle_export_status
from ..models.v1_vehicle_export_status import V1VehicleExportStatus
from ..models.v1_vehicle_export_transmission import check_v1_vehicle_export_transmission
from ..models.v1_vehicle_export_transmission import V1VehicleExportTransmission
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import cast, Union
from typing import Union
import datetime


T = TypeVar("T", bound="V1VehicleExport")


@_attrs_define
class V1VehicleExport:
    """Serializer for vehicle data export (CSV, Excel).
    Includes all essential fields in flat structure.

        Attributes:
            listing_id (str): Original listing ID from source
            source_name (str):
            brand_name (str):
            model_name (str):
            full_name (str):
            price_usd (float): Convert price to USD using currency service
            created_at (datetime.datetime):
            year (Union[None, Unset, int]):
            price (Union[Unset, int]):
            price_currency (Union[Unset, V1VehicleExportPriceCurrency]): * `KRW` - ₩ Korean Won
                * `USD` - $ US Dollar
                * `JPY` - ¥ Japanese Yen
                * `EUR` - € Euro
                * `CNY` - ¥ Chinese Yuan
                * `RUB` - ₽ Russian Ruble
                * `other` - Other
            mileage (Union[Unset, int]):
            fuel_type (Union[Unset, V1VehicleExportFuelType]): * `gasoline` - ⛽ Gasoline
                * `diesel` - 🛢️ Diesel
                * `hybrid` - 🔋 Hybrid
                * `plug_hybrid` - 🔌 Plug-in Hybrid
                * `electric` - ⚡ Electric
                * `hydrogen` - 💨 Hydrogen
                * `cng` - 💨 CNG
                * `lpg` - 🔥 LPG
                * `other` - ❓ Other
                * `unknown` - ❓ Unknown
            transmission (Union[Unset, V1VehicleExportTransmission]): * `manual` - Manual
                * `auto` - Automatic
                * `cvt` - CVT
                * `semi_auto` - Semi-Auto
                * `dct` - DCT
                * `other` - Other
                * `unknown` - Unknown
            body_type (Union[Unset, V1VehicleExportBodyType]): * `sedan` - 🚗 Sedan
                * `hatchback` - 🚙 Hatchback
                * `coupe` - 🏎️ Coupe
                * `convertible` - 🏎️ Convertible
                * `suv` - 🚐 SUV
                * `wagon` - 🚛 Wagon
                * `pickup` - 🛻 Pickup
                * `van` - 🚐 Van
                * `minivan` - 🚌 Minivan
                * `crossover` - 🚙 Crossover
                * `truck` - 🚚 Truck
                * `bus` - 🚌 Bus
                * `other` - ❓ Other
                * `unknown` - ❓ Unknown
            color (Union[Unset, V1VehicleExportColor]): * `white` - ⚪ White
                * `black` - ⚫ Black
                * `gray` - 🔘 Gray
                * `silver` - 🔘 Silver
                * `red` - 🔴 Red
                * `blue` - 🔵 Blue
                * `yellow` - 🟡 Yellow
                * `green` - 🟢 Green
                * `brown` - 🟤 Brown
                * `purple` - 🟣 Purple
                * `orange` - 🟠 Orange
                * `pink` - 🩷 Pink
                * `gold` - 🟡 Gold
                * `beige` - 🟤 Beige
                * `other` - ❓ Other
                * `unknown` - ❓ Unknown
            location (Union[Unset, str]):
            dealer_name (Union[Unset, str]):
            investment_grade (Union[Unset, V1VehicleExportInvestmentGrade]): * `A+` - A+ (Excellent)
                * `A` - A (Very Good)
                * `A-` - A- (Good Plus)
                * `B+` - B+ (Good)
                * `B` - B (Above Average)
                * `B-` - B- (Average Plus)
                * `C+` - C+ (Average)
                * `C` - C (Below Average)
                * `C-` - C- (Poor Plus)
                * `D` - D (Poor)
                * `F` - F (Avoid)
            risk_level (Union[Unset, V1VehicleExportRiskLevel]): * `very_low` - Very Low
                * `low` - Low
                * `medium` - Medium
                * `high` - High
                * `very_high` - Very High
            accident_count (Union[Unset, int]):
            owner_count (Union[Unset, int]):
            status (Union[Unset, V1VehicleExportStatus]): * `active` - ✅ Active
                * `sold` - 💰 Sold
                * `reserved` - ⏳ Reserved
                * `inactive` - ❌ Inactive
    """

    listing_id: str
    source_name: str
    brand_name: str
    model_name: str
    full_name: str
    price_usd: float
    created_at: datetime.datetime
    year: Union[None, Unset, int] = UNSET
    price: Union[Unset, int] = UNSET
    price_currency: Union[Unset, V1VehicleExportPriceCurrency] = UNSET
    mileage: Union[Unset, int] = UNSET
    fuel_type: Union[Unset, V1VehicleExportFuelType] = UNSET
    transmission: Union[Unset, V1VehicleExportTransmission] = UNSET
    body_type: Union[Unset, V1VehicleExportBodyType] = UNSET
    color: Union[Unset, V1VehicleExportColor] = UNSET
    location: Union[Unset, str] = UNSET
    dealer_name: Union[Unset, str] = UNSET
    investment_grade: Union[Unset, V1VehicleExportInvestmentGrade] = UNSET
    risk_level: Union[Unset, V1VehicleExportRiskLevel] = UNSET
    accident_count: Union[Unset, int] = UNSET
    owner_count: Union[Unset, int] = UNSET
    status: Union[Unset, V1VehicleExportStatus] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        listing_id = self.listing_id

        source_name = self.source_name

        brand_name = self.brand_name

        model_name = self.model_name

        full_name = self.full_name

        price_usd = self.price_usd

        created_at = self.created_at.isoformat()

        year: Union[None, Unset, int]
        if isinstance(self.year, Unset):
            year = UNSET
        else:
            year = self.year

        price = self.price

        price_currency: Union[Unset, str] = UNSET
        if not isinstance(self.price_currency, Unset):
            price_currency = self.price_currency

        mileage = self.mileage

        fuel_type: Union[Unset, str] = UNSET
        if not isinstance(self.fuel_type, Unset):
            fuel_type = self.fuel_type

        transmission: Union[Unset, str] = UNSET
        if not isinstance(self.transmission, Unset):
            transmission = self.transmission

        body_type: Union[Unset, str] = UNSET
        if not isinstance(self.body_type, Unset):
            body_type = self.body_type

        color: Union[Unset, str] = UNSET
        if not isinstance(self.color, Unset):
            color = self.color

        location = self.location

        dealer_name = self.dealer_name

        investment_grade: Union[Unset, str] = UNSET
        if not isinstance(self.investment_grade, Unset):
            investment_grade = self.investment_grade

        risk_level: Union[Unset, str] = UNSET
        if not isinstance(self.risk_level, Unset):
            risk_level = self.risk_level

        accident_count = self.accident_count

        owner_count = self.owner_count

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "listing_id": listing_id,
                "source_name": source_name,
                "brand_name": brand_name,
                "model_name": model_name,
                "full_name": full_name,
                "price_usd": price_usd,
                "created_at": created_at,
            }
        )
        if year is not UNSET:
            field_dict["year"] = year
        if price is not UNSET:
            field_dict["price"] = price
        if price_currency is not UNSET:
            field_dict["price_currency"] = price_currency
        if mileage is not UNSET:
            field_dict["mileage"] = mileage
        if fuel_type is not UNSET:
            field_dict["fuel_type"] = fuel_type
        if transmission is not UNSET:
            field_dict["transmission"] = transmission
        if body_type is not UNSET:
            field_dict["body_type"] = body_type
        if color is not UNSET:
            field_dict["color"] = color
        if location is not UNSET:
            field_dict["location"] = location
        if dealer_name is not UNSET:
            field_dict["dealer_name"] = dealer_name
        if investment_grade is not UNSET:
            field_dict["investment_grade"] = investment_grade
        if risk_level is not UNSET:
            field_dict["risk_level"] = risk_level
        if accident_count is not UNSET:
            field_dict["accident_count"] = accident_count
        if owner_count is not UNSET:
            field_dict["owner_count"] = owner_count
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        listing_id = d.pop("listing_id")

        source_name = d.pop("source_name")

        brand_name = d.pop("brand_name")

        model_name = d.pop("model_name")

        full_name = d.pop("full_name")

        price_usd = d.pop("price_usd")

        created_at = isoparse(d.pop("created_at"))

        def _parse_year(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        year = _parse_year(d.pop("year", UNSET))

        price = d.pop("price", UNSET)

        _price_currency = d.pop("price_currency", UNSET)
        price_currency: Union[Unset, V1VehicleExportPriceCurrency]
        if isinstance(_price_currency, Unset):
            price_currency = UNSET
        else:
            price_currency = check_v1_vehicle_export_price_currency(_price_currency)

        mileage = d.pop("mileage", UNSET)

        _fuel_type = d.pop("fuel_type", UNSET)
        fuel_type: Union[Unset, V1VehicleExportFuelType]
        if isinstance(_fuel_type, Unset):
            fuel_type = UNSET
        else:
            fuel_type = check_v1_vehicle_export_fuel_type(_fuel_type)

        _transmission = d.pop("transmission", UNSET)
        transmission: Union[Unset, V1VehicleExportTransmission]
        if isinstance(_transmission, Unset):
            transmission = UNSET
        else:
            transmission = check_v1_vehicle_export_transmission(_transmission)

        _body_type = d.pop("body_type", UNSET)
        body_type: Union[Unset, V1VehicleExportBodyType]
        if isinstance(_body_type, Unset):
            body_type = UNSET
        else:
            body_type = check_v1_vehicle_export_body_type(_body_type)

        _color = d.pop("color", UNSET)
        color: Union[Unset, V1VehicleExportColor]
        if isinstance(_color, Unset):
            color = UNSET
        else:
            color = check_v1_vehicle_export_color(_color)

        location = d.pop("location", UNSET)

        dealer_name = d.pop("dealer_name", UNSET)

        _investment_grade = d.pop("investment_grade", UNSET)
        investment_grade: Union[Unset, V1VehicleExportInvestmentGrade]
        if isinstance(_investment_grade, Unset):
            investment_grade = UNSET
        else:
            investment_grade = check_v1_vehicle_export_investment_grade(_investment_grade)

        _risk_level = d.pop("risk_level", UNSET)
        risk_level: Union[Unset, V1VehicleExportRiskLevel]
        if isinstance(_risk_level, Unset):
            risk_level = UNSET
        else:
            risk_level = check_v1_vehicle_export_risk_level(_risk_level)

        accident_count = d.pop("accident_count", UNSET)

        owner_count = d.pop("owner_count", UNSET)

        _status = d.pop("status", UNSET)
        status: Union[Unset, V1VehicleExportStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = check_v1_vehicle_export_status(_status)

        v1_vehicle_export = cls(
            listing_id=listing_id,
            source_name=source_name,
            brand_name=brand_name,
            model_name=model_name,
            full_name=full_name,
            price_usd=price_usd,
            created_at=created_at,
            year=year,
            price=price,
            price_currency=price_currency,
            mileage=mileage,
            fuel_type=fuel_type,
            transmission=transmission,
            body_type=body_type,
            color=color,
            location=location,
            dealer_name=dealer_name,
            investment_grade=investment_grade,
            risk_level=risk_level,
            accident_count=accident_count,
            owner_count=owner_count,
            status=status,
        )

        v1_vehicle_export.additional_properties = d
        return v1_vehicle_export

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
