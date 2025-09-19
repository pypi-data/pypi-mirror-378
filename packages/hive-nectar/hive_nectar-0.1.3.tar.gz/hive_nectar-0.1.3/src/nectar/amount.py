# -*- coding: utf-8 -*-
from decimal import ROUND_DOWN, Decimal

from nectar.asset import Asset
from nectar.instance import shared_blockchain_instance


def check_asset(other, self, hv):
    """
    Assert that two asset representations refer to the same asset.

    If both `other` and `self` are dicts containing an "asset" key, each asset id is wrapped in an Asset using the provided blockchain instance and compared for equality. Otherwise the two values are compared directly. Raises AssertionError if the values do not match.
    """
    if isinstance(other, dict) and "asset" in other and isinstance(self, dict) and "asset" in self:
        if not Asset(other["asset"], blockchain_instance=hv) == Asset(
            self["asset"], blockchain_instance=hv
        ):
            raise AssertionError()
    else:
        if not other == self:
            raise AssertionError()


def quantize(amount, precision):
    # make sure amount is decimal and has the asset precision
    amount = Decimal(amount)
    places = Decimal(10) ** (-precision)
    return amount.quantize(places, rounding=ROUND_DOWN)


class Amount(dict):
    """This class deals with Amounts of any asset to simplify dealing with the tuple::

        (amount, asset)

    :param list args: Allows to deal with different representations of an amount
    :param float amount: Let's create an instance with a specific amount
    :param str asset: Let's you create an instance with a specific asset (symbol)
    :param boolean fixed_point_arithmetic: when set to True, all operations are fixed
        point operations and the amount is always be rounded down to the precision
    :param Blockchain blockchain_instance: Blockchain instance
    :returns: All data required to represent an Amount/Asset
    :rtype: dict
    :raises ValueError: if the data provided is not recognized

    Way to obtain a proper instance:

        * ``args`` can be a string, e.g.:  "1 HBD"
        * ``args`` can be a dictionary containing ``amount`` and ``asset_id``
        * ``args`` can be a dictionary containing ``amount`` and ``asset``
        * ``args`` can be a list of a ``float`` and ``str`` (symbol)
        * ``args`` can be a list of a ``float`` and a :class:`nectar.asset.Asset`
        * ``amount`` and ``asset`` are defined manually

    An instance is a dictionary and comes with the following keys:

        * ``amount`` (float)
        * ``symbol`` (str)
        * ``asset`` (instance of :class:`nectar.asset.Asset`)

    Instances of this class can be used in regular mathematical expressions
    (``+-*/%``) such as:

    .. testcode::

        from nectar.amount import Amount
        from nectar.asset import Asset
        a = Amount("1 HIVE")
        b = Amount(1, "HIVE")
        c = Amount("20", Asset("HIVE"))
        a + b
        a * 2
        a += b
        a /= 2.0

    .. testoutput::

        2.000 HIVE
        2.000 HIVE

    """

    def __init__(
        self,
        amount,
        asset=None,
        fixed_point_arithmetic=False,
        new_appbase_format=True,
        blockchain_instance=None,
        **kwargs,
    ):
        """
        Initialize an Amount object representing a quantity of a specific blockchain asset.

        The constructor accepts many input formats and normalizes them into internal keys:
        - amount may be another Amount, a three-element list [amount, precision, asset],
          a new appbase-format dict with keys ("amount", "nai", "precision"), a legacy dict
          with ("amount", "asset_id") or ("amount", "asset"), a string like "1.000 HIVE",
          or a numeric value (int, float, Decimal) paired with an `asset` argument.
        - asset may be an Asset instance, an asset dict, or a symbol string; when omitted,
          the asset will be inferred from the provided `amount` representation.

        After parsing, the instance stores:
        - "amount" as a Decimal (or quantized Decimal when fixed-point mode is enabled),
        - "symbol" as the asset symbol,
        - "asset" as an Asset-like object.

        Parameters:
            amount: Various accepted formats (see description) representing the quantity.
            asset: Asset instance, asset dict, or asset symbol string used when `amount`
                is a bare numeric value or when explicit asset resolution is required.
            fixed_point_arithmetic (bool): When True, the numeric amount is quantized
                to the asset's precision using floor rounding.
            new_appbase_format (bool): Indicates whether to prefer the new appbase JSON
                format when producing serialized representations.

        Raises:
            ValueError: If `amount` and `asset` do not match any supported input format.
        """
        self["asset"] = {}
        self.new_appbase_format = new_appbase_format
        self.fixed_point_arithmetic = fixed_point_arithmetic

        self.blockchain = blockchain_instance or shared_blockchain_instance()

        if amount and asset is None and isinstance(amount, Amount):
            # Copy Asset object
            self["amount"] = amount["amount"]
            self["symbol"] = amount["symbol"]
            self["asset"] = amount["asset"]

        elif amount and asset is None and isinstance(amount, list) and len(amount) == 3:
            # Copy Asset object
            self["amount"] = Decimal(amount[0]) / Decimal(10 ** amount[1])
            self["asset"] = Asset(amount[2], blockchain_instance=self.blockchain)
            self["symbol"] = self["asset"]["symbol"]

        elif (
            amount
            and asset is None
            and isinstance(amount, dict)
            and "amount" in amount
            and "nai" in amount
            and "precision" in amount
        ):
            # Copy Asset object
            self.new_appbase_format = True
            self["amount"] = Decimal(amount["amount"]) / Decimal(10 ** amount["precision"])
            self["asset"] = Asset(amount["nai"], blockchain_instance=self.blockchain)
            self["symbol"] = self["asset"]["symbol"]

        elif amount is not None and asset is None and isinstance(amount, str):
            self["amount"], self["symbol"] = amount.split(" ")
            self["asset"] = Asset(self["symbol"], blockchain_instance=self.blockchain)

        elif (
            amount
            and asset is None
            and isinstance(amount, dict)
            and "amount" in amount
            and "asset_id" in amount
        ):
            self["asset"] = Asset(amount["asset_id"], blockchain_instance=self.blockchain)
            self["symbol"] = self["asset"]["symbol"]
            self["amount"] = Decimal(amount["amount"]) / Decimal(10 ** self["asset"]["precision"])

        elif (
            amount
            and asset is None
            and isinstance(amount, dict)
            and "amount" in amount
            and "asset" in amount
        ):
            self["asset"] = Asset(amount["asset"], blockchain_instance=self.blockchain)
            self["symbol"] = self["asset"]["symbol"]
            self["amount"] = Decimal(amount["amount"]) / Decimal(10 ** self["asset"]["precision"])

        elif isinstance(amount, (float)) and asset and isinstance(asset, Asset):
            self["amount"] = str(amount)
            self["asset"] = asset
            self["symbol"] = self["asset"]["symbol"]

        elif isinstance(amount, (int, Decimal)) and asset and isinstance(asset, Asset):
            self["amount"] = amount
            self["asset"] = asset
            self["symbol"] = self["asset"]["symbol"]

        elif isinstance(amount, (float)) and asset and isinstance(asset, dict):
            self["amount"] = str(amount)
            self["asset"] = asset
            self["symbol"] = self["asset"]["symbol"]

        elif isinstance(amount, (int, Decimal)) and asset and isinstance(asset, dict):
            self["amount"] = amount
            self["asset"] = asset
            self["symbol"] = self["asset"]["symbol"]

        elif isinstance(amount, (float)) and asset and isinstance(asset, str):
            self["amount"] = str(amount)
            self["asset"] = Asset(asset, blockchain_instance=self.blockchain)
            self["symbol"] = asset

        elif isinstance(amount, (int, Decimal)) and asset and isinstance(asset, str):
            self["amount"] = amount
            self["asset"] = Asset(asset, blockchain_instance=self.blockchain)
            self["symbol"] = asset
        elif amount and asset and isinstance(asset, Asset):
            self["amount"] = amount
            self["symbol"] = asset["symbol"]
            self["asset"] = asset
        elif amount and asset and isinstance(asset, str):
            self["amount"] = amount
            self["asset"] = Asset(asset, blockchain_instance=self.blockchain)
            self["symbol"] = self["asset"]["symbol"]
        else:
            raise ValueError
        if self.fixed_point_arithmetic:
            self["amount"] = quantize(self["amount"], self["asset"]["precision"])
        else:
            self["amount"] = Decimal(self["amount"])

    def copy(self):
        """Copy the instance and make sure not to use a reference"""
        return Amount(
            amount=self["amount"],
            asset=self["asset"].copy(),
            new_appbase_format=self.new_appbase_format,
            fixed_point_arithmetic=self.fixed_point_arithmetic,
            blockchain_instance=self.blockchain,
        )

    @property
    def amount(self):
        """Returns the amount as float"""
        return float(self["amount"])

    @property
    def amount_decimal(self):
        """Returns the amount as decimal"""
        return self["amount"]

    @property
    def symbol(self):
        """Returns the symbol of the asset"""
        return self["symbol"]

    def tuple(self):
        return float(self), self.symbol

    @property
    def asset(self):
        """
        Return the Asset object for this Amount, constructing it lazily if missing.

        If the internal 'asset' entry is falsy, this creates a nectar.asset.Asset using the stored symbol
        and this Amount's blockchain instance, stores it in 'asset', and returns it. Always returns an
        Asset instance.
        """
        if not isinstance(self["asset"], Asset):
            self["asset"] = Asset(self["symbol"], blockchain_instance=self.blockchain)
        return self["asset"]

    def json(self):
        if self.blockchain.is_connected() and self.blockchain.rpc.get_use_appbase():
            if self.new_appbase_format:
                return {
                    "amount": str(int(self)),
                    "nai": self["asset"]["asset"],
                    "precision": self["asset"]["precision"],
                }
            else:
                return [str(int(self)), self["asset"]["precision"], self["asset"]["asset"]]
        else:
            return str(self)

    def __str__(self):
        amount = quantize(self["amount"], self["asset"]["precision"])
        symbol = self["symbol"]
        return "{:.{prec}f} {}".format(amount, symbol, prec=self["asset"]["precision"])

    def __float__(self):
        if self.fixed_point_arithmetic:
            return float(quantize(self["amount"], self["asset"]["precision"]))
        else:
            return float(self["amount"])

    def __int__(self):
        amount = quantize(self["amount"], self["asset"]["precision"])
        return int(amount * 10 ** self["asset"]["precision"])

    def __add__(self, other):
        a = self.copy()
        if isinstance(other, Amount):
            check_asset(other["asset"], self["asset"], self.blockchain)
            a["amount"] += other["amount"]
        else:
            a["amount"] += Decimal(other)
        if self.fixed_point_arithmetic:
            a["amount"] = quantize(a["amount"], self["asset"]["precision"])
        return a

    def __sub__(self, other):
        a = self.copy()
        if isinstance(other, Amount):
            check_asset(other["asset"], self["asset"], self.blockchain)
            a["amount"] -= other["amount"]
        else:
            a["amount"] -= Decimal(other)
        if self.fixed_point_arithmetic:
            a["amount"] = quantize(a["amount"], self["asset"]["precision"])
        return a

    def __mul__(self, other):
        from .price import Price

        a = self.copy()
        if isinstance(other, Amount):
            check_asset(other["asset"], self["asset"], self.blockchain)
            a["amount"] *= other["amount"]
        elif isinstance(other, Price):
            if not self["asset"] == other["quote"]["asset"]:
                raise AssertionError()
            a = self.copy() * other["price"]
            a["asset"] = other["base"]["asset"].copy()
            a["symbol"] = other["base"]["asset"]["symbol"]
        else:
            a["amount"] *= Decimal(other)
        if self.fixed_point_arithmetic:
            a["amount"] = quantize(a["amount"], self["asset"]["precision"])
        return a

    def __floordiv__(self, other):
        a = self.copy()
        if isinstance(other, Amount):
            from .price import Price

            check_asset(other["asset"], self["asset"], self.blockchain)
            return Price(self, other, blockchain_instance=self.blockchain)
        else:
            a["amount"] //= Decimal(other)
        if self.fixed_point_arithmetic:
            a["amount"] = quantize(a["amount"], self["asset"]["precision"])
        return a

    def __div__(self, other):
        from .price import Price

        a = self.copy()
        if isinstance(other, Amount):
            check_asset(other["asset"], self["asset"], self.blockchain)
            return Price(self, other, blockchain_instance=self.blockchain)
        elif isinstance(other, Price):
            if not self["asset"] == other["base"]["asset"]:
                raise AssertionError()
            a = self.copy()
            a["amount"] = a["amount"] / other["price"]
            a["asset"] = other["quote"]["asset"].copy()
            a["symbol"] = other["quote"]["asset"]["symbol"]
        else:
            a["amount"] /= Decimal(other)
        if self.fixed_point_arithmetic:
            a["amount"] = quantize(a["amount"], self["asset"]["precision"])
        return a

    def __mod__(self, other):
        a = self.copy()
        if isinstance(other, Amount):
            check_asset(other["asset"], self["asset"], self.blockchain)
            a["amount"] %= other["amount"]
        else:
            a["amount"] %= Decimal(other)
        if self.fixed_point_arithmetic:
            a["amount"] = quantize(a["amount"], self["asset"]["precision"])
        return a

    def __pow__(self, other):
        a = self.copy()
        if isinstance(other, Amount):
            check_asset(other["asset"], self["asset"], self.blockchain)
            a["amount"] **= other["amount"]
        else:
            a["amount"] **= Decimal(other)
        if self.fixed_point_arithmetic:
            a["amount"] = quantize(a["amount"], self["asset"]["precision"])
        return a

    def __iadd__(self, other):
        if isinstance(other, Amount):
            check_asset(other["asset"], self["asset"], self.blockchain)
            self["amount"] += other["amount"]
        else:
            self["amount"] += Decimal(other)
        if self.fixed_point_arithmetic:
            self["amount"] = quantize(self["amount"], self["asset"]["precision"])
        return self

    def __isub__(self, other):
        if isinstance(other, Amount):
            check_asset(other["asset"], self["asset"], self.blockchain)
            self["amount"] -= other["amount"]
        else:
            self["amount"] -= Decimal(other)
        if self.fixed_point_arithmetic:
            self["amount"] = quantize(self["amount"], self["asset"]["precision"])
        return self

    def __imul__(self, other):
        if isinstance(other, Amount):
            check_asset(other["asset"], self["asset"], self.blockchain)
            self["amount"] *= other["amount"]
        else:
            self["amount"] *= Decimal(other)

        self["amount"] = quantize(self["amount"], self["asset"]["precision"])
        return self

    def __idiv__(self, other):
        """
        In-place division: divide this Amount by another Amount or numeric value and return self.

        If `other` is an Amount, asserts asset compatibility and divides this object's internal amount by the other's amount. If `other` is numeric, divides by Decimal(other). When `fixed_point_arithmetic` is enabled, the result is quantized to this asset's precision.

        Returns:
            self (Amount): The mutated Amount instance.

        Raises:
            AssertionError: If `other` is an Amount with a different asset (via check_asset).
        """
        if isinstance(other, Amount):
            check_asset(other["asset"], self["asset"], self.blockchain)
            self["amount"] = self["amount"] / other["amount"]
        else:
            self["amount"] /= Decimal(other)
        if self.fixed_point_arithmetic:
            self["amount"] = quantize(self["amount"], self["asset"]["precision"])
        return self

    def __ifloordiv__(self, other):
        if isinstance(other, Amount):
            self["amount"] //= other["amount"]
        else:
            self["amount"] //= Decimal(other)
        self["amount"] = quantize(self["amount"], self["asset"]["precision"])
        return self

    def __imod__(self, other):
        if isinstance(other, Amount):
            check_asset(other["asset"], self["asset"], self.blockchain)
            self["amount"] %= other["amount"]
        else:
            self["amount"] %= Decimal(other)
        if self.fixed_point_arithmetic:
            self["amount"] = quantize(self["amount"], self["asset"]["precision"])
        return self

    def __ipow__(self, other):
        if isinstance(other, Amount):
            self["amount"] **= other
        else:
            self["amount"] **= Decimal(other)
        if self.fixed_point_arithmetic:
            self["amount"] = quantize(self["amount"], self["asset"]["precision"])
        return self

    def __lt__(self, other):
        quant_amount = quantize(self["amount"], self["asset"]["precision"])
        if isinstance(other, Amount):
            check_asset(other["asset"], self["asset"], self.blockchain)
            return quant_amount < quantize(other["amount"], self["asset"]["precision"])
        else:
            return quant_amount < quantize((other or 0), self["asset"]["precision"])

    def __le__(self, other):
        quant_amount = quantize(self["amount"], self["asset"]["precision"])
        if isinstance(other, Amount):
            check_asset(other["asset"], self["asset"], self.blockchain)
            return quant_amount <= quantize(other["amount"], self["asset"]["precision"])
        else:
            return quant_amount <= quantize((other or 0), self["asset"]["precision"])

    def __eq__(self, other):
        quant_amount = quantize(self["amount"], self["asset"]["precision"])
        if isinstance(other, Amount):
            check_asset(other["asset"], self["asset"], self.blockchain)
            return quant_amount == quantize(other["amount"], self["asset"]["precision"])
        else:
            return quant_amount == quantize((other or 0), self["asset"]["precision"])

    def __ne__(self, other):
        """
        Return True if this Amount is not equal to `other`.

        Compares values after quantizing both sides to this amount's asset precision. If `other` is an Amount, its asset must match this Amount's asset (an assertion is raised on mismatch) and the comparison uses both amounts quantized to the shared precision. If `other` is numeric or None, it is treated as a numeric value (None → 0) and compared after quantization.

        Returns:
                bool: True when the quantized values differ, False otherwise.
        """
        quant_amount = quantize(self["amount"], self["asset"]["precision"])
        if isinstance(other, Amount):
            check_asset(other["asset"], self["asset"], self.blockchain)
            return quantize(self["amount"], self["asset"]["precision"]) != quantize(
                other["amount"], self["asset"]["precision"]
            )
        else:
            return quant_amount != quantize((other or 0), self["asset"]["precision"])

    def __ge__(self, other):
        """
        Return True if this Amount is greater than or equal to `other`.

        Performs comparison after quantizing both values to this Amount's asset precision. If `other` is an Amount, its asset must match this Amount's asset (an AssertionError is raised on mismatch). If `other` is None, it is treated as zero. Returns a boolean.
        """
        quant_amount = quantize(self["amount"], self["asset"]["precision"])
        if isinstance(other, Amount):
            check_asset(other["asset"], self["asset"], self.blockchain)
            return quant_amount >= quantize(other["amount"], self["asset"]["precision"])
        else:
            return quant_amount >= quantize((other or 0), self["asset"]["precision"])

    def __gt__(self, other):
        quant_amount = quantize(self["amount"], self["asset"]["precision"])
        if isinstance(other, Amount):
            check_asset(other["asset"], self["asset"], self.blockchain)
            return quant_amount > quantize(other["amount"], self["asset"]["precision"])
        else:
            return quant_amount > quantize((other or 0), self["asset"]["precision"])

    __repr__ = __str__
    __truediv__ = __div__
    __itruediv__ = __idiv__
    __truemul__ = __mul__
