# coding:utf-8

from ipaddress import IPv4Address
from ipaddress import IPv6Address
from ipaddress import ip_address  # noqa:H306
from random import randint
from typing import Optional
from typing import Union

from ping3 import ping

IPAddress = Union[IPv4Address, IPv6Address]


class Peer():

    TOMAX = 60  # maximum timeout value
    TODEF = 3  # default timeout value
    TOMIN = 1  # minimum timeout value

    def __init__(self, address: IPAddress, timeout: int = TODEF):
        self.__address: IPAddress = address
        self.__timeout: int = timeout

    @property
    def address(self) -> IPAddress:
        return self.__address

    @property
    def timeout(self) -> int:
        return self.__timeout

    def ping(self, timeout: Optional[int] = None) -> float:
        sequence: int = randint(8192, 32767)

        def once(address: str, timeout: int) -> float:
            result = ping(address, timeout=timeout, seq=sequence)
            return result if isinstance(result, float) else -float(timeout)

        _timeout: int = min(max(self.TOMIN, timeout or self.timeout), self.TOMAX)  # noqa:E501
        _address: str = str(self.address)
        return once(_address, _timeout)

    @classmethod
    def from_string(cls, address: str, timeout: int = TODEF) -> "Peer":
        assert isinstance(address, str), f"Unexpected type: {type(address)}"
        assert isinstance(timeout, int), f"Unexpected type: {type(timeout)}"
        return cls(ip_address(address), timeout)
