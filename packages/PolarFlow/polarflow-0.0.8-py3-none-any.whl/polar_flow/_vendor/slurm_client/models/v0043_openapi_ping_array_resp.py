from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.v0043_controller_ping import V0043ControllerPing
    from ..models.v0043_openapi_error import V0043OpenapiError
    from ..models.v0043_openapi_meta import V0043OpenapiMeta
    from ..models.v0043_openapi_warning import V0043OpenapiWarning


T = TypeVar("T", bound="V0043OpenapiPingArrayResp")


@_attrs_define
class V0043OpenapiPingArrayResp:
    pings: list["V0043ControllerPing"]
    meta: Union[Unset, "V0043OpenapiMeta"] = UNSET
    errors: Union[Unset, list["V0043OpenapiError"]] = UNSET
    warnings: Union[Unset, list["V0043OpenapiWarning"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        pings = []
        for componentsschemasv0_0_43_controller_ping_array_item_data in self.pings:
            componentsschemasv0_0_43_controller_ping_array_item = (
                componentsschemasv0_0_43_controller_ping_array_item_data.to_dict()
            )
            pings.append(componentsschemasv0_0_43_controller_ping_array_item)

        meta: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.meta, Unset):
            meta = self.meta.to_dict()

        errors: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.errors, Unset):
            errors = []
            for componentsschemasv0_0_43_openapi_errors_item_data in self.errors:
                componentsschemasv0_0_43_openapi_errors_item = (
                    componentsschemasv0_0_43_openapi_errors_item_data.to_dict()
                )
                errors.append(componentsschemasv0_0_43_openapi_errors_item)

        warnings: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.warnings, Unset):
            warnings = []
            for componentsschemasv0_0_43_openapi_warnings_item_data in self.warnings:
                componentsschemasv0_0_43_openapi_warnings_item = (
                    componentsschemasv0_0_43_openapi_warnings_item_data.to_dict()
                )
                warnings.append(componentsschemasv0_0_43_openapi_warnings_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "pings": pings,
            }
        )
        if meta is not UNSET:
            field_dict["meta"] = meta
        if errors is not UNSET:
            field_dict["errors"] = errors
        if warnings is not UNSET:
            field_dict["warnings"] = warnings

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.v0043_controller_ping import V0043ControllerPing
        from ..models.v0043_openapi_error import V0043OpenapiError
        from ..models.v0043_openapi_meta import V0043OpenapiMeta
        from ..models.v0043_openapi_warning import V0043OpenapiWarning

        d = dict(src_dict)
        pings = []
        _pings = d.pop("pings")
        for componentsschemasv0_0_43_controller_ping_array_item_data in _pings:
            componentsschemasv0_0_43_controller_ping_array_item = V0043ControllerPing.from_dict(
                componentsschemasv0_0_43_controller_ping_array_item_data
            )

            pings.append(componentsschemasv0_0_43_controller_ping_array_item)

        _meta = d.pop("meta", UNSET)
        meta: Union[Unset, V0043OpenapiMeta]
        if isinstance(_meta, Unset):
            meta = UNSET
        else:
            meta = V0043OpenapiMeta.from_dict(_meta)

        errors = []
        _errors = d.pop("errors", UNSET)
        for componentsschemasv0_0_43_openapi_errors_item_data in _errors or []:
            componentsschemasv0_0_43_openapi_errors_item = V0043OpenapiError.from_dict(
                componentsschemasv0_0_43_openapi_errors_item_data
            )

            errors.append(componentsschemasv0_0_43_openapi_errors_item)

        warnings = []
        _warnings = d.pop("warnings", UNSET)
        for componentsschemasv0_0_43_openapi_warnings_item_data in _warnings or []:
            componentsschemasv0_0_43_openapi_warnings_item = V0043OpenapiWarning.from_dict(
                componentsschemasv0_0_43_openapi_warnings_item_data
            )

            warnings.append(componentsschemasv0_0_43_openapi_warnings_item)

        v0043_openapi_ping_array_resp = cls(
            pings=pings,
            meta=meta,
            errors=errors,
            warnings=warnings,
        )

        v0043_openapi_ping_array_resp.additional_properties = d
        return v0043_openapi_ping_array_resp

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
