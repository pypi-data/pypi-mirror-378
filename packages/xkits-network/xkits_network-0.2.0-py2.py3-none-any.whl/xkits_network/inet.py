# coding:utf-8

from ipaddress import IPv4Address
from ipaddress import IPv6Address
from ipaddress import ip_address  # noqa:H306
from typing import Any
from typing import Generator
from typing import Optional
from typing import Tuple
from typing import Union

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

    def ping(self, timeout: Optional[int] = None, count: int = 3) -> Generator[float, Any, Tuple[float, float]]:  # noqa:E501
        def once(address: str, timeout: int, sequence: int) -> float:
            from ping3 import ping  # pylint:disable=import-outside-toplevel
            result = ping(address, timeout=timeout, seq=sequence)
            return result if isinstance(result, float) else -float(timeout)

        _address: str = str(self.address)
        _timeout: int = min(max(self.TOMIN, timeout or self.timeout), self.TOMAX)  # noqa:E501

        from random import randint  # pylint:disable=import-outside-toplevel
        _seq: int = randint(8192, 32767)  # 2 bytes sequence number
        _sum: float = 0.0
        _cnt: int = 0

        for i in range(_len := min(max(1, count), 32768)):  # range 0-65535
            if (_rtt := once(_address, _timeout, _seq + i)) > 0:
                yield _rtt  # RTT(Round-Trip Time)
                _sum += _rtt
                _cnt += 1

        # calculate the average RTT and DR(Delivery Rate)
        return _sum / _cnt if _cnt > 0 else _sum, _cnt / _len

    def ping_once(self, timeout: Optional[int] = None, retries: int = 5) -> float:  # noqa:E501
        """ping until successful or reach retries"""
        for rtt in (generator := self.ping(timeout, retries)):
            generator.close()
            return rtt
        return -float(timeout or self.timeout)

    @classmethod
    def from_string(cls, address: str, timeout: int = TODEF) -> "Peer":
        assert isinstance(address, str), f"Unexpected type: {type(address)}"
        assert isinstance(timeout, int), f"Unexpected type: {type(timeout)}"
        return cls(ip_address(address), timeout)
