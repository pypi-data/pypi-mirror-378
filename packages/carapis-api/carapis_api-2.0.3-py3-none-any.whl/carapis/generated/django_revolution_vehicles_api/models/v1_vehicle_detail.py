from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.v1_vehicle_detail_body_type import check_v1_vehicle_detail_body_type
from ..models.v1_vehicle_detail_body_type import V1VehicleDetailBodyType
from ..models.v1_vehicle_detail_color import check_v1_vehicle_detail_color
from ..models.v1_vehicle_detail_color import V1VehicleDetailColor
from ..models.v1_vehicle_detail_fuel_type import check_v1_vehicle_detail_fuel_type
from ..models.v1_vehicle_detail_fuel_type import V1VehicleDetailFuelType
from ..models.v1_vehicle_detail_investment_grade import check_v1_vehicle_detail_investment_grade
from ..models.v1_vehicle_detail_investment_grade import V1VehicleDetailInvestmentGrade
from ..models.v1_vehicle_detail_price_currency import check_v1_vehicle_detail_price_currency
from ..models.v1_vehicle_detail_price_currency import V1VehicleDetailPriceCurrency
from ..models.v1_vehicle_detail_risk_level import check_v1_vehicle_detail_risk_level
from ..models.v1_vehicle_detail_risk_level import V1VehicleDetailRiskLevel
from ..models.v1_vehicle_detail_status import check_v1_vehicle_detail_status
from ..models.v1_vehicle_detail_status import V1VehicleDetailStatus
from ..models.v1_vehicle_detail_transmission import check_v1_vehicle_detail_transmission
from ..models.v1_vehicle_detail_transmission import V1VehicleDetailTransmission
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import cast, Union
from typing import Union
from uuid import UUID
import datetime

if TYPE_CHECKING:
    from ..models.v1_vehicle_photo import V1VehiclePhoto


T = TypeVar("T", bound="V1VehicleDetail")


@_attrs_define
class V1VehicleDetail:
    """Complete vehicle serializer for detail views.
    Includes all available information and related data.

        Attributes:
            id (UUID):
            listing_id (str): Original listing ID from source
            source_name (str):
            source_country (str):
            source_flag (str):
            source_currency (str):
            brand_name (str):
            brand_country (str):
            brand_logo (str):
            model_name (str):
            model_segment (str):
            full_name (str):
            price_usd (float): Convert price to USD using currency service
            has_major_issues (str):
            photos (list['V1VehiclePhoto']):
            photos_count (int): Get total photos count
            similar_count (int): Get count of similar vehicles
            created_at (datetime.datetime):
            updated_at (datetime.datetime):
            source_url (Union[Unset, str]): Direct URL to the listing
            title (Union[Unset, str]):
            year (Union[None, Unset, int]):
            price (Union[Unset, int]):
            price_currency (Union[Unset, V1VehicleDetailPriceCurrency]): * `KRW` - ₩ Korean Won
                * `USD` - $ US Dollar
                * `JPY` - ¥ Japanese Yen
                * `EUR` - € Euro
                * `CNY` - ¥ Chinese Yuan
                * `RUB` - ₽ Russian Ruble
                * `other` - Other
            mileage (Union[Unset, int]):
            engine_volume (Union[None, Unset, int]):
            fuel_type (Union[Unset, V1VehicleDetailFuelType]): * `gasoline` - ⛽ Gasoline
                * `diesel` - 🛢️ Diesel
                * `hybrid` - 🔋 Hybrid
                * `plug_hybrid` - 🔌 Plug-in Hybrid
                * `electric` - ⚡ Electric
                * `hydrogen` - 💨 Hydrogen
                * `cng` - 💨 CNG
                * `lpg` - 🔥 LPG
                * `other` - ❓ Other
                * `unknown` - ❓ Unknown
            transmission (Union[Unset, V1VehicleDetailTransmission]): * `manual` - Manual
                * `auto` - Automatic
                * `cvt` - CVT
                * `semi_auto` - Semi-Auto
                * `dct` - DCT
                * `other` - Other
                * `unknown` - Unknown
            body_type (Union[Unset, V1VehicleDetailBodyType]): * `sedan` - 🚗 Sedan
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
            color (Union[Unset, V1VehicleDetailColor]): * `white` - ⚪ White
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
            status (Union[Unset, V1VehicleDetailStatus]): * `active` - ✅ Active
                * `sold` - 💰 Sold
                * `reserved` - ⏳ Reserved
                * `inactive` - ❌ Inactive
            investment_grade (Union[Unset, V1VehicleDetailInvestmentGrade]): * `A+` - A+ (Excellent)
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
            risk_level (Union[Unset, V1VehicleDetailRiskLevel]): * `very_low` - Very Low
                * `low` - Low
                * `medium` - Medium
                * `high` - High
                * `very_high` - Very High
            llm_confidence (Union[None, Unset, float]):
            llm_analysis_date (Union[None, Unset, datetime.datetime]):
            accident_count (Union[Unset, int]):
            owner_count (Union[Unset, int]):
            parsed_at (Union[None, Unset, datetime.datetime]): When this vehicle was last parsed from source
    """

    id: UUID
    listing_id: str
    source_name: str
    source_country: str
    source_flag: str
    source_currency: str
    brand_name: str
    brand_country: str
    brand_logo: str
    model_name: str
    model_segment: str
    full_name: str
    price_usd: float
    has_major_issues: str
    photos: list["V1VehiclePhoto"]
    photos_count: int
    similar_count: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    source_url: Union[Unset, str] = UNSET
    title: Union[Unset, str] = UNSET
    year: Union[None, Unset, int] = UNSET
    price: Union[Unset, int] = UNSET
    price_currency: Union[Unset, V1VehicleDetailPriceCurrency] = UNSET
    mileage: Union[Unset, int] = UNSET
    engine_volume: Union[None, Unset, int] = UNSET
    fuel_type: Union[Unset, V1VehicleDetailFuelType] = UNSET
    transmission: Union[Unset, V1VehicleDetailTransmission] = UNSET
    body_type: Union[Unset, V1VehicleDetailBodyType] = UNSET
    color: Union[Unset, V1VehicleDetailColor] = UNSET
    location: Union[Unset, str] = UNSET
    dealer_name: Union[Unset, str] = UNSET
    status: Union[Unset, V1VehicleDetailStatus] = UNSET
    investment_grade: Union[Unset, V1VehicleDetailInvestmentGrade] = UNSET
    risk_level: Union[Unset, V1VehicleDetailRiskLevel] = UNSET
    llm_confidence: Union[None, Unset, float] = UNSET
    llm_analysis_date: Union[None, Unset, datetime.datetime] = UNSET
    accident_count: Union[Unset, int] = UNSET
    owner_count: Union[Unset, int] = UNSET
    parsed_at: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.v1_vehicle_photo import V1VehiclePhoto

        id = str(self.id)

        listing_id = self.listing_id

        source_name = self.source_name

        source_country = self.source_country

        source_flag = self.source_flag

        source_currency = self.source_currency

        brand_name = self.brand_name

        brand_country = self.brand_country

        brand_logo = self.brand_logo

        model_name = self.model_name

        model_segment = self.model_segment

        full_name = self.full_name

        price_usd = self.price_usd

        has_major_issues = self.has_major_issues

        photos = []
        for photos_item_data in self.photos:
            photos_item = photos_item_data.to_dict()
            photos.append(photos_item)

        photos_count = self.photos_count

        similar_count = self.similar_count

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        source_url = self.source_url

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

        engine_volume: Union[None, Unset, int]
        if isinstance(self.engine_volume, Unset):
            engine_volume = UNSET
        else:
            engine_volume = self.engine_volume

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

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status

        investment_grade: Union[Unset, str] = UNSET
        if not isinstance(self.investment_grade, Unset):
            investment_grade = self.investment_grade

        risk_level: Union[Unset, str] = UNSET
        if not isinstance(self.risk_level, Unset):
            risk_level = self.risk_level

        llm_confidence: Union[None, Unset, float]
        if isinstance(self.llm_confidence, Unset):
            llm_confidence = UNSET
        else:
            llm_confidence = self.llm_confidence

        llm_analysis_date: Union[None, Unset, str]
        if isinstance(self.llm_analysis_date, Unset):
            llm_analysis_date = UNSET
        elif isinstance(self.llm_analysis_date, datetime.datetime):
            llm_analysis_date = self.llm_analysis_date.isoformat()
        else:
            llm_analysis_date = self.llm_analysis_date

        accident_count = self.accident_count

        owner_count = self.owner_count

        parsed_at: Union[None, Unset, str]
        if isinstance(self.parsed_at, Unset):
            parsed_at = UNSET
        elif isinstance(self.parsed_at, datetime.datetime):
            parsed_at = self.parsed_at.isoformat()
        else:
            parsed_at = self.parsed_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "listing_id": listing_id,
                "source_name": source_name,
                "source_country": source_country,
                "source_flag": source_flag,
                "source_currency": source_currency,
                "brand_name": brand_name,
                "brand_country": brand_country,
                "brand_logo": brand_logo,
                "model_name": model_name,
                "model_segment": model_segment,
                "full_name": full_name,
                "price_usd": price_usd,
                "has_major_issues": has_major_issues,
                "photos": photos,
                "photos_count": photos_count,
                "similar_count": similar_count,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if source_url is not UNSET:
            field_dict["source_url"] = source_url
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
        if engine_volume is not UNSET:
            field_dict["engine_volume"] = engine_volume
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
        if status is not UNSET:
            field_dict["status"] = status
        if investment_grade is not UNSET:
            field_dict["investment_grade"] = investment_grade
        if risk_level is not UNSET:
            field_dict["risk_level"] = risk_level
        if llm_confidence is not UNSET:
            field_dict["llm_confidence"] = llm_confidence
        if llm_analysis_date is not UNSET:
            field_dict["llm_analysis_date"] = llm_analysis_date
        if accident_count is not UNSET:
            field_dict["accident_count"] = accident_count
        if owner_count is not UNSET:
            field_dict["owner_count"] = owner_count
        if parsed_at is not UNSET:
            field_dict["parsed_at"] = parsed_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.v1_vehicle_photo import V1VehiclePhoto

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        listing_id = d.pop("listing_id")

        source_name = d.pop("source_name")

        source_country = d.pop("source_country")

        source_flag = d.pop("source_flag")

        source_currency = d.pop("source_currency")

        brand_name = d.pop("brand_name")

        brand_country = d.pop("brand_country")

        brand_logo = d.pop("brand_logo")

        model_name = d.pop("model_name")

        model_segment = d.pop("model_segment")

        full_name = d.pop("full_name")

        price_usd = d.pop("price_usd")

        has_major_issues = d.pop("has_major_issues")

        photos = []
        _photos = d.pop("photos")
        for photos_item_data in _photos:
            photos_item = V1VehiclePhoto.from_dict(photos_item_data)

            photos.append(photos_item)

        photos_count = d.pop("photos_count")

        similar_count = d.pop("similar_count")

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        source_url = d.pop("source_url", UNSET)

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
        price_currency: Union[Unset, V1VehicleDetailPriceCurrency]
        if isinstance(_price_currency, Unset):
            price_currency = UNSET
        else:
            price_currency = check_v1_vehicle_detail_price_currency(_price_currency)

        mileage = d.pop("mileage", UNSET)

        def _parse_engine_volume(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        engine_volume = _parse_engine_volume(d.pop("engine_volume", UNSET))

        _fuel_type = d.pop("fuel_type", UNSET)
        fuel_type: Union[Unset, V1VehicleDetailFuelType]
        if isinstance(_fuel_type, Unset):
            fuel_type = UNSET
        else:
            fuel_type = check_v1_vehicle_detail_fuel_type(_fuel_type)

        _transmission = d.pop("transmission", UNSET)
        transmission: Union[Unset, V1VehicleDetailTransmission]
        if isinstance(_transmission, Unset):
            transmission = UNSET
        else:
            transmission = check_v1_vehicle_detail_transmission(_transmission)

        _body_type = d.pop("body_type", UNSET)
        body_type: Union[Unset, V1VehicleDetailBodyType]
        if isinstance(_body_type, Unset):
            body_type = UNSET
        else:
            body_type = check_v1_vehicle_detail_body_type(_body_type)

        _color = d.pop("color", UNSET)
        color: Union[Unset, V1VehicleDetailColor]
        if isinstance(_color, Unset):
            color = UNSET
        else:
            color = check_v1_vehicle_detail_color(_color)

        location = d.pop("location", UNSET)

        dealer_name = d.pop("dealer_name", UNSET)

        _status = d.pop("status", UNSET)
        status: Union[Unset, V1VehicleDetailStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = check_v1_vehicle_detail_status(_status)

        _investment_grade = d.pop("investment_grade", UNSET)
        investment_grade: Union[Unset, V1VehicleDetailInvestmentGrade]
        if isinstance(_investment_grade, Unset):
            investment_grade = UNSET
        else:
            investment_grade = check_v1_vehicle_detail_investment_grade(_investment_grade)

        _risk_level = d.pop("risk_level", UNSET)
        risk_level: Union[Unset, V1VehicleDetailRiskLevel]
        if isinstance(_risk_level, Unset):
            risk_level = UNSET
        else:
            risk_level = check_v1_vehicle_detail_risk_level(_risk_level)

        def _parse_llm_confidence(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        llm_confidence = _parse_llm_confidence(d.pop("llm_confidence", UNSET))

        def _parse_llm_analysis_date(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                llm_analysis_date_type_0 = isoparse(data)

                return llm_analysis_date_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        llm_analysis_date = _parse_llm_analysis_date(d.pop("llm_analysis_date", UNSET))

        accident_count = d.pop("accident_count", UNSET)

        owner_count = d.pop("owner_count", UNSET)

        def _parse_parsed_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                parsed_at_type_0 = isoparse(data)

                return parsed_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        parsed_at = _parse_parsed_at(d.pop("parsed_at", UNSET))

        v1_vehicle_detail = cls(
            id=id,
            listing_id=listing_id,
            source_name=source_name,
            source_country=source_country,
            source_flag=source_flag,
            source_currency=source_currency,
            brand_name=brand_name,
            brand_country=brand_country,
            brand_logo=brand_logo,
            model_name=model_name,
            model_segment=model_segment,
            full_name=full_name,
            price_usd=price_usd,
            has_major_issues=has_major_issues,
            photos=photos,
            photos_count=photos_count,
            similar_count=similar_count,
            created_at=created_at,
            updated_at=updated_at,
            source_url=source_url,
            title=title,
            year=year,
            price=price,
            price_currency=price_currency,
            mileage=mileage,
            engine_volume=engine_volume,
            fuel_type=fuel_type,
            transmission=transmission,
            body_type=body_type,
            color=color,
            location=location,
            dealer_name=dealer_name,
            status=status,
            investment_grade=investment_grade,
            risk_level=risk_level,
            llm_confidence=llm_confidence,
            llm_analysis_date=llm_analysis_date,
            accident_count=accident_count,
            owner_count=owner_count,
            parsed_at=parsed_at,
        )

        v1_vehicle_detail.additional_properties = d
        return v1_vehicle_detail

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
