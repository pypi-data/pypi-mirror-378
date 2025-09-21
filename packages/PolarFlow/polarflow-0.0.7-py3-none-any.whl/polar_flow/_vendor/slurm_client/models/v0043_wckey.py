from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.v0043_wckey_flags_item import V0043WckeyFlagsItem
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.v0043_accounting import V0043Accounting


T = TypeVar("T", bound="V0043Wckey")


@_attrs_define
class V0043Wckey:
    cluster: str
    """ Cluster name """
    name: str
    """ WCKey name """
    user: str
    """ User name """
    accounting: Union[Unset, list["V0043Accounting"]] = UNSET
    id: Union[Unset, int] = UNSET
    """ Unique ID for this user-cluster-wckey combination """
    flags: Union[Unset, list[V0043WckeyFlagsItem]] = UNSET
    """ Flags associated with this WCKey """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        cluster = self.cluster

        name = self.name

        user = self.user

        accounting: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.accounting, Unset):
            accounting = []
            for componentsschemasv0_0_43_accounting_list_item_data in self.accounting:
                componentsschemasv0_0_43_accounting_list_item = (
                    componentsschemasv0_0_43_accounting_list_item_data.to_dict()
                )
                accounting.append(componentsschemasv0_0_43_accounting_list_item)

        id = self.id

        flags: Union[Unset, list[str]] = UNSET
        if not isinstance(self.flags, Unset):
            flags = []
            for flags_item_data in self.flags:
                flags_item = flags_item_data.value
                flags.append(flags_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "cluster": cluster,
                "name": name,
                "user": user,
            }
        )
        if accounting is not UNSET:
            field_dict["accounting"] = accounting
        if id is not UNSET:
            field_dict["id"] = id
        if flags is not UNSET:
            field_dict["flags"] = flags

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.v0043_accounting import V0043Accounting

        d = dict(src_dict)
        cluster = d.pop("cluster")

        name = d.pop("name")

        user = d.pop("user")

        accounting = []
        _accounting = d.pop("accounting", UNSET)
        for componentsschemasv0_0_43_accounting_list_item_data in _accounting or []:
            componentsschemasv0_0_43_accounting_list_item = V0043Accounting.from_dict(
                componentsschemasv0_0_43_accounting_list_item_data
            )

            accounting.append(componentsschemasv0_0_43_accounting_list_item)

        id = d.pop("id", UNSET)

        flags = []
        _flags = d.pop("flags", UNSET)
        for flags_item_data in _flags or []:
            flags_item = V0043WckeyFlagsItem(flags_item_data)

            flags.append(flags_item)

        v0043_wckey = cls(
            cluster=cluster,
            name=name,
            user=user,
            accounting=accounting,
            id=id,
            flags=flags,
        )

        v0043_wckey.additional_properties = d
        return v0043_wckey

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
