import asyncio
import datetime
import itertools
from datetime import timedelta
from decimal import Decimal
from enum import Enum, auto
from typing import List, Dict, Any, Type, Set, Optional

import httpx

from sirius import common
from sirius.common import DataClass, Currency
from sirius.exceptions import OperationNotSupportedException
from sirius.http_requests import AsyncHTTPSession, HTTPResponse

_account_list: List["IBKRAccount"] = []
_account_list_lock = asyncio.Lock()

base_url: str = common.get_environmental_secret("IBKR_SERVICE_BASE_URL", "https://ibkr-service:5000/v1/api/")
session: AsyncHTTPSession = AsyncHTTPSession(base_url)
session.client = httpx.AsyncClient(verify=False, timeout=60)


class ContractType(Enum):
    STOCK = "STK"
    OPTION = "OPT"
    FUTURE = "FUT"
    FUTURE_OPTION = "FOP"
    BOND = "BND"


class OptionContractType(Enum):
    PUT = auto()
    CALL = auto()


class Exchange(Enum):
    NASDAQ = "NASDAQ"


class IBKRAccount(DataClass):
    id: str
    name: str

    @staticmethod
    async def get_all_ibkr_accounts() -> List["IBKRAccount"]:
        global _account_list
        if len(_account_list) == 0:
            async with _account_list_lock:
                if len(_account_list) == 0:
                    response: HTTPResponse = await session.get(f"{base_url}/portfolio/accounts/")
                    _account_list = [IBKRAccount(id=data["id"], name=data["accountAlias"] if data["accountAlias"] else data["id"]) for data in response.data]

        return _account_list


class Contract(DataClass):
    id: int
    name: str
    symbol: str
    currency: Currency

    @staticmethod
    def _get_contract_subclass(contract_type_str: str) -> Type["Contract"]:
        try:
            return {  # type: ignore[return-value]
                "STK": StockContract,
                "OPT": OptionContract,
                "FUT": FutureContract,
                "FOP": FuturesOptionContract,
                "BOND": BondContract,
            }[contract_type_str]
        except KeyError:
            raise OperationNotSupportedException(f"Unknown contract type string: {contract_type_str}")

    @staticmethod
    async def get(contract_id: int) -> "Contract":
        response: HTTPResponse = await session.get(f"{base_url}iserver/contract/{contract_id}/info")
        cls: Type[Contract] = Contract._get_contract_subclass(response.data["instrument_type"])
        return cls(
            id=contract_id,
            name=response.data["company_name"],
            symbol=response.data["symbol"],
            currency=Currency(response.data["currency"]),
        )

    @staticmethod
    async def find_contract_id(ticker: str, contract_type: ContractType) -> List[int]:
        response: HTTPResponse = await session.get(f"{base_url}iserver/secdef/search?symbol={ticker}&secType={contract_type.value}")
        valid_result_list: List[Dict[str, Any]] = list(filter(lambda d: d["description"] in Exchange, response.data))
        return [int(data["conid"]) for data in valid_result_list]

    @staticmethod
    async def find_contract(ticker: str, contract_type: ContractType) -> List["Contract"]:
        contract_id_list: List[int] = await Contract.find_contract_id(ticker, contract_type)
        return [await Contract.get(contract_id) for contract_id in contract_id_list]


class StockContract(Contract):
    pass


class OptionContract(Contract):
    strike_price: Decimal
    expiry_month_str: str
    type: OptionContractType

    @staticmethod
    async def get_all(underlying_contract: StockContract, expiry_month_str: str, strike_price: Decimal) -> List["OptionContract"]:
        response: HTTPResponse = await session.get(
            f"{base_url}iserver/secdef/info",
            query_params={
                "conid": underlying_contract.id,
                "sectype": ContractType.OPTION.value,
                "month": expiry_month_str,
                "strike": float(strike_price)}
        )

        return [OptionContract(
            **underlying_contract.model_dump(exclude={"id"}),
            id=data["conid"],
            strike_price=strike_price,
            expiry_month_str=expiry_month_str,
            type=OptionContractType.CALL if data["right"] == "C" else OptionContractType.PUT
        ) for data in response.data]

    @staticmethod
    async def find_all(underlying_contract: StockContract) -> List["OptionContract"]:
        option_contract_list: List[OptionContract] = []
        response: HTTPResponse = await session.get(f"{base_url}iserver/secdef/search?symbol={underlying_contract.symbol}&secType={ContractType.STOCK.value}")
        data: Dict[str, Any] = next(filter(lambda c: int(c["conid"]) == underlying_contract.id, response.data))
        option_data: Dict[str, Any] = next(filter(lambda o: ContractType(o["secType"]) == ContractType.OPTION, data["sections"]))
        expiry_month_str_list: List[str] = option_data["months"].split(";")

        responses: List[HTTPResponse] = await asyncio.gather(*[
            session.get(f"{base_url}iserver/secdef/strikes", query_params={"conid": underlying_contract.id, "sectype": ContractType.OPTION.value, "month": expiry_month_str})
            for expiry_month_str in expiry_month_str_list
        ])
        for expiry_month_str, response in zip(expiry_month_str_list, responses):
            all_strike_price_set: Set[Decimal] = set([Decimal(str(strike_price)) for strike_price in response.data.get("call", [])])
            all_strike_price_set.update([Decimal(str(strike_price)) for strike_price in response.data.get("put", [])])
            sub_option_contract_list: List[List[OptionContract]] = await asyncio.gather(*[
                OptionContract.get_all(underlying_contract, expiry_month_str, strike_price)
                for strike_price in all_strike_price_set
            ])

            option_contract_list.extend(list(itertools.chain.from_iterable(sub_option_contract_list)))

        return option_contract_list


class FutureContract(Contract):
    pass


class FuturesOptionContract(Contract):
    pass


class BondContract(Contract):
    pass


class MarketData(DataClass):
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    date: datetime.date

    @staticmethod
    def _get_from_ohlc_data(ohlc_data: Dict[str, float]) -> "MarketData":
        return MarketData(
            open=Decimal(str(ohlc_data["o"])),
            high=Decimal(str(ohlc_data["h"])),
            low=Decimal(str(ohlc_data["l"])),
            close=Decimal(str(ohlc_data["c"])),
            volume=Decimal(str(ohlc_data["v"])),
            date=datetime.datetime.fromtimestamp(ohlc_data["t"] / 1000).date(),
        )

    @staticmethod
    async def _get_ohlc_data(contract_id: int, from_date: datetime.date, to_date: datetime.date) -> List[Dict[str, float]]:
        number_of_days: int = (to_date - from_date).days
        date_format_code: str = "%Y%m%d-%H:%M:%S"
        response: HTTPResponse = await session.get(
            f"{base_url}iserver/marketdata/history",
            query_params={
                "conid": contract_id,
                "period": f"{min(number_of_days, 999)}d",
                "bar": "1d",
                "startTime": (to_date + timedelta(days=1)).strftime(date_format_code),  # There is a +1 since some timezones are on the next day
                "direction": "-1"
            }
        )

        response_from_time: datetime.date = datetime.datetime.strptime(response.data["startTime"], date_format_code).date()
        raw_ohlc_data = list(filter(lambda data: from_date <= datetime.datetime.fromtimestamp(data["t"] / 1000).date() <= to_date, response.data["data"]))

        if from_date < response_from_time:
            new_raw_ohlc_data: List[Dict[str, float]] = await MarketData._get_ohlc_data(contract_id, from_date, response_from_time)
            raw_ohlc_data = list(itertools.chain.from_iterable([raw_ohlc_data, new_raw_ohlc_data]))

        return raw_ohlc_data

    @staticmethod
    async def get(contract_id: int, from_time: datetime.date, to_time: datetime.date | None = None) -> Dict[datetime.date, "MarketData"]:
        to_time = to_time if to_time else datetime.datetime.now().date()
        market_data_list: List[MarketData] = [MarketData._get_from_ohlc_data(ohlc_data) for ohlc_data in await MarketData._get_ohlc_data(contract_id, from_time, to_time)]
        return {market_data.date: market_data for market_data in market_data_list}


class ContractPerformance(DataClass):
    position_open: MarketData
    position_close: MarketData
    absolute_return: Decimal
    annualized_return: Decimal

    @staticmethod
    def _construct(position_open: MarketData, position_close: MarketData) -> "ContractPerformance":
        absolute_return: Decimal = (position_close.close - position_open.close) / position_open.close
        number_of_days = Decimal((position_close.date - position_open.date).days)
        annualized_return = (position_close.close / position_open.close) ** (Decimal("365") / number_of_days) - Decimal("1")

        return ContractPerformance(
            position_open=position_open,
            position_close=position_close,
            absolute_return=absolute_return,
            annualized_return=annualized_return
        )

    @staticmethod
    async def get(contract_id: int, position_start_date: datetime.date, number_of_days: int) -> Optional["ContractPerformance"]:
        position_close_date: datetime.date = position_start_date + timedelta(days=number_of_days)
        market_data_map: Dict[datetime.date, MarketData] = await MarketData.get(contract_id, position_start_date, position_close_date)
        position_open = market_data_map.get(position_start_date)
        position_close = market_data_map.get(position_close_date)

        if not position_open or not position_close:
            return None

        return ContractPerformance._construct(position_open, position_close)
