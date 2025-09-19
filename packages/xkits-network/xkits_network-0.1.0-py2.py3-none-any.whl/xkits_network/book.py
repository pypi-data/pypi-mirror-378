# coding:utf-8

from ipaddress import IPv4Address
from ipaddress import IPv6Address
from ipaddress import ip_address  # noqa:H306
from typing import Dict
from typing import Generic
from typing import Iterator
from typing import Optional
from typing import TypeVar
from typing import Union

IPVT = TypeVar("IPVT")
IPDT = TypeVar("IPDT")


class AddrBook(Generic[IPVT, IPDT]):

    def __init__(self):
        self.__mappings: Dict[int, IPDT] = {}

    def __iter__(self) -> Iterator[IPDT]:
        for addr in sorted(self.__mappings.keys()):
            yield self.__mappings[addr]

    def __len__(self) -> int:
        return len(self.__mappings)

    def __contains__(self, addr: IPVT) -> bool:
        return self.hash(addr) in self.__mappings

    def __getitem__(self, addr: IPVT) -> IPDT:
        if not (data := self.get(addr)):
            raise KeyError(f"{addr} not found")
        return data

    def __setitem__(self, addr: IPVT, data: IPDT) -> None:
        return self.set(addr, data)

    def hash(self, addr: IPVT) -> int:
        obj = ip_address(addr) if isinstance(addr, (int, str, bytes)) else addr

        if isinstance(obj, (IPv4Address, IPv6Address)):
            return int(obj)

        raise TypeError(f"Unsupported address type: {type(addr)}")  # noqa:E501 pragma: no cover

    def get(self, addr: IPVT) -> Optional[IPDT]:
        return self.__mappings.get(self.hash(addr))

    def set(self, addr: IPVT, data: IPDT) -> None:
        self.__mappings[self.hash(addr)] = data

    def setdefault(self, addr: IPVT, data: IPDT) -> IPDT:
        return self.__mappings.setdefault(self.hash(addr), data)

    def update(self, addr: IPVT, data: IPDT) -> None:
        return self.__mappings.update({self.hash(addr): data})


class IPv4Book(AddrBook[Union[IPv4Address, str], IPDT]):

    pass


class IPv6Book(AddrBook[Union[IPv6Address, str], IPDT]):

    pass


class IP64Book(AddrBook[Union[IPv6Address, IPv4Address, str], IPDT]):

    pass


if __name__ == "__main__":
    ipv4book: IPv4Book[str] = IPv4Book()
    ipv4book["127.0.0.1"] = "localhost"
    print(ipv4book.get("127.0.0.1"))
