from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.v1_vehicle_list_body_type import check_v1_vehicle_list_body_type
from ..models.v1_vehicle_list_body_type import V1VehicleListBodyType
from ..models.v1_vehicle_list_color import check_v1_vehicle_list_color
from ..models.v1_vehicle_list_color import V1VehicleListColor
from ..models.v1_vehicle_list_fuel_type import check_v1_vehicle_list_fuel_type
from ..models.v1_vehicle_list_fuel_type import V1VehicleListFuelType
from ..models.v1_vehicle_list_investment_grade import check_v1_vehicle_list_investment_grade
from ..models.v1_vehicle_list_investment_grade import V1VehicleListInvestmentGrade
from ..models.v1_vehicle_list_price_currency import check_v1_vehicle_list_price_currency
from ..models.v1_vehicle_list_price_currency import V1VehicleListPriceCurrency
from ..models.v1_vehicle_list_risk_level import check_v1_vehicle_list_risk_level
from ..models.v1_vehicle_list_risk_level import V1VehicleListRiskLevel
from ..models.v1_vehicle_list_transmission import check_v1_vehicle_list_transmission
from ..models.v1_vehicle_list_transmission import V1VehicleListTransmission
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import cast, Union
from typing import Union
from uuid import UUID
import datetime

if TYPE_CHECKING:
    from ..models.v1_vehicle_list_main_photo_type_0 import V1VehicleListMainPhotoType0


T = TypeVar("T", bound="V1VehicleList")


@_attrs_define
class V1VehicleList:
    """Lightweight vehicle serializer for list views.
    Optimized for performance with minimal data.

        Attributes:
            id (UUID):
            listing_id (str): Original listing ID from source
            source_name (str):
            source_country (str):
            source_flag (str):
            brand_name (str):
            model_name (str):
            full_name (str):
            price_usd (float): Convert price to USD using currency service
            has_major_issues (str):
            main_photo (Union['V1VehicleListMainPhotoType0', None]): Get main photo information with proxied URL
            photos_count (int): Get total photos count
            created_at (datetime.datetime):
            updated_at (datetime.datetime):
            title (Union[Unset, str]):
            year (Union[None, Unset, int]):
            price (Union[Unset, int]):
            price_currency (Union[Unset, V1VehicleListPriceCurrency]): * `KRW` - ₩ Korean Won
                * `USD` - $ US Dollar
                * `JPY` - ¥ Japanese Yen
                * `EUR` - € Euro
                * `CNY` - ¥ Chinese Yuan
                * `RUB` - ₽ Russian Ruble
                * `other` - Other
            mileage (Union[Unset, int]):
            fuel_type (Union[Unset, V1VehicleListFuelType]): * `gasoline` - ⛽ Gasoline
                * `diesel` - 🛢️ Diesel
                * `hybrid` - 🔋 Hybrid
                * `plug_hybrid` - 🔌 Plug-in Hybrid
                * `electric` - ⚡ Electric
                * `hydrogen` - 💨 Hydrogen
                * `cng` - 💨 CNG
                * `lpg` - 🔥 LPG
                * `other` - ❓ Other
                * `unknown` - ❓ Unknown
            transmission (Union[Unset, V1VehicleListTransmission]): * `manual` - Manual
                * `auto` - Automatic
                * `cvt` - CVT
                * `semi_auto` - Semi-Auto
                * `dct` - DCT
                * `other` - Other
                * `unknown` - Unknown
            body_type (Union[Unset, V1VehicleListBodyType]): * `sedan` - 🚗 Sedan
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
            color (Union[Unset, V1VehicleListColor]): * `white` - ⚪ White
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
            investment_grade (Union[Unset, V1VehicleListInvestmentGrade]): * `A+` - A+ (Excellent)
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
            risk_level (Union[Unset, V1VehicleListRiskLevel]): * `very_low` - Very Low
                * `low` - Low
                * `medium` - Medium
                * `high` - High
                * `very_high` - Very High
    """

    id: UUID
    listing_id: str
    source_name: str
    source_country: str
    source_flag: str
    brand_name: str
    model_name: str
    full_name: str
    price_usd: float
    has_major_issues: str
    main_photo: Union["V1VehicleListMainPhotoType0", None]
    photos_count: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    title: Union[Unset, str] = UNSET
    year: Union[None, Unset, int] = UNSET
    price: Union[Unset, int] = UNSET
    price_currency: Union[Unset, V1VehicleListPriceCurrency] = UNSET
    mileage: Union[Unset, int] = UNSET
    fuel_type: Union[Unset, V1VehicleListFuelType] = UNSET
    transmission: Union[Unset, V1VehicleListTransmission] = UNSET
    body_type: Union[Unset, V1VehicleListBodyType] = UNSET
    color: Union[Unset, V1VehicleListColor] = UNSET
    location: Union[Unset, str] = UNSET
    dealer_name: Union[Unset, str] = UNSET
    investment_grade: Union[Unset, V1VehicleListInvestmentGrade] = UNSET
    risk_level: Union[Unset, V1VehicleListRiskLevel] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.v1_vehicle_list_main_photo_type_0 import V1VehicleListMainPhotoType0

        id = str(self.id)

        listing_id = self.listing_id

        source_name = self.source_name

        source_country = self.source_country

        source_flag = self.source_flag

        brand_name = self.brand_name

        model_name = self.model_name

        full_name = self.full_name

        price_usd = self.price_usd

        has_major_issues = self.has_major_issues

        main_photo: Union[None, dict[str, Any]]
        if isinstance(self.main_photo, V1VehicleListMainPhotoType0):
            main_photo = self.main_photo.to_dict()
        else:
            main_photo = self.main_photo

        photos_count = self.photos_count

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        title = self.title

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

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "listing_id": listing_id,
                "source_name": source_name,
                "source_country": source_country,
                "source_flag": source_flag,
                "brand_name": brand_name,
                "model_name": model_name,
                "full_name": full_name,
                "price_usd": price_usd,
                "has_major_issues": has_major_issues,
                "main_photo": main_photo,
                "photos_count": photos_count,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if title is not UNSET:
            field_dict["title"] = title
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

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.v1_vehicle_list_main_photo_type_0 import V1VehicleListMainPhotoType0

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        listing_id = d.pop("listing_id")

        source_name = d.pop("source_name")

        source_country = d.pop("source_country")

        source_flag = d.pop("source_flag")

        brand_name = d.pop("brand_name")

        model_name = d.pop("model_name")

        full_name = d.pop("full_name")

        price_usd = d.pop("price_usd")

        has_major_issues = d.pop("has_major_issues")

        def _parse_main_photo(data: object) -> Union["V1VehicleListMainPhotoType0", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                main_photo_type_0 = V1VehicleListMainPhotoType0.from_dict(data)

                return main_photo_type_0
            except:  # noqa: E722
                pass
            return cast(Union["V1VehicleListMainPhotoType0", None], data)

        main_photo = _parse_main_photo(d.pop("main_photo"))

        photos_count = d.pop("photos_count")

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        title = d.pop("title", UNSET)

        def _parse_year(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        year = _parse_year(d.pop("year", UNSET))

        price = d.pop("price", UNSET)

        _price_currency = d.pop("price_currency", UNSET)
        price_currency: Union[Unset, V1VehicleListPriceCurrency]
        if isinstance(_price_currency, Unset):
            price_currency = UNSET
        else:
            price_currency = check_v1_vehicle_list_price_currency(_price_currency)

        mileage = d.pop("mileage", UNSET)

        _fuel_type = d.pop("fuel_type", UNSET)
        fuel_type: Union[Unset, V1VehicleListFuelType]
        if isinstance(_fuel_type, Unset):
            fuel_type = UNSET
        else:
            fuel_type = check_v1_vehicle_list_fuel_type(_fuel_type)

        _transmission = d.pop("transmission", UNSET)
        transmission: Union[Unset, V1VehicleListTransmission]
        if isinstance(_transmission, Unset):
            transmission = UNSET
        else:
            transmission = check_v1_vehicle_list_transmission(_transmission)

        _body_type = d.pop("body_type", UNSET)
        body_type: Union[Unset, V1VehicleListBodyType]
        if isinstance(_body_type, Unset):
            body_type = UNSET
        else:
            body_type = check_v1_vehicle_list_body_type(_body_type)

        _color = d.pop("color", UNSET)
        color: Union[Unset, V1VehicleListColor]
        if isinstance(_color, Unset):
            color = UNSET
        else:
            color = check_v1_vehicle_list_color(_color)

        location = d.pop("location", UNSET)

        dealer_name = d.pop("dealer_name", UNSET)

        _investment_grade = d.pop("investment_grade", UNSET)
        investment_grade: Union[Unset, V1VehicleListInvestmentGrade]
        if isinstance(_investment_grade, Unset):
            investment_grade = UNSET
        else:
            investment_grade = check_v1_vehicle_list_investment_grade(_investment_grade)

        _risk_level = d.pop("risk_level", UNSET)
        risk_level: Union[Unset, V1VehicleListRiskLevel]
        if isinstance(_risk_level, Unset):
            risk_level = UNSET
        else:
            risk_level = check_v1_vehicle_list_risk_level(_risk_level)

        v1_vehicle_list = cls(
            id=id,
            listing_id=listing_id,
            source_name=source_name,
            source_country=source_country,
            source_flag=source_flag,
            brand_name=brand_name,
            model_name=model_name,
            full_name=full_name,
            price_usd=price_usd,
            has_major_issues=has_major_issues,
            main_photo=main_photo,
            photos_count=photos_count,
            created_at=created_at,
            updated_at=updated_at,
            title=title,
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
        )

        v1_vehicle_list.additional_properties = d
        return v1_vehicle_list

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
