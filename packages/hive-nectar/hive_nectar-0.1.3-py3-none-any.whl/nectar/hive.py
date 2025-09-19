# -*- coding: utf-8 -*-
import logging
import math
from datetime import date, datetime, timezone

from nectar.blockchaininstance import BlockChainInstance
from nectar.constants import HIVE_100_PERCENT
from nectargraphenebase.chains import known_chains

from .amount import Amount
from .utils import formatToTimeStamp

log = logging.getLogger(__name__)


class Hive(BlockChainInstance):
    """Connect to the Hive network.

    :param str node: Node to connect to *(optional)*
    :param str rpcuser: RPC user *(optional)*
    :param str rpcpassword: RPC password *(optional)*
    :param bool nobroadcast: Do **not** broadcast a transaction!
        *(optional)*
    :param bool unsigned: Do **not** sign a transaction! *(optional)*
    :param bool debug: Enable Debugging *(optional)*
    :param keys: Predefine the wif keys to shortcut the
        wallet database *(optional)*
    :type keys: array, dict, string
    :param wif: Predefine the wif keys to shortcut the
            wallet database *(optional)*
    :type wif: array, dict, string
    :param bool offline: Boolean to prevent connecting to network (defaults
        to ``False``) *(optional)*
    :param int expiration: Delay in seconds until transactions are supposed
        to expire *(optional)* (default is 30)
    :param str blocking: Wait for broadcasted transactions to be included
        in a block and return full transaction (can be "head" or
        "irreversible")
    :param bool bundle: Do not broadcast transactions right away, but allow
        to bundle operations. It is not possible to send out more than one
        vote operation and more than one comment operation in a single broadcast *(optional)*
    :param bool appbase: Use the new appbase rpc protocol on nodes with version
        0.19.4 or higher. The settings has no effect on nodes with version of 0.19.3 or lower.
    :param int num_retries: Set the maximum number of reconnects to the nodes before
        NumRetriesReached is raised. Disabled for -1. (default is -1)
    :param int num_retries_call: Repeat num_retries_call times a rpc call on node error (default is 5)
    :param int timeout: Timeout setting for https nodes (default is 60)
    :param bool use_hs: When True, a hivesigner object is created. Can be used for
        broadcast posting op or creating hot_links (default is False)
    :param HiveSigner hivesigner: A HiveSigner object can be set manually, set use_hs to True
    :param dict custom_chains: custom chain which should be added to the known chains

    Three wallet operation modes are possible:

    * **Wallet Database**: Here, the nectarlibs load the keys from the
      locally stored wallet SQLite database (see ``storage.py``).
      To use this mode, simply call ``Hive()`` without the
      ``keys`` parameter
    * **Providing Keys**: Here, you can provide the keys for
      your accounts manually. All you need to do is add the wif
      keys for the accounts you want to use as a simple array
      using the ``keys`` parameter to ``Hive()``.
    * **Force keys**: This more is for advanced users and
      requires that you know what you are doing. Here, the
      ``keys`` parameter is a dictionary that overwrite the
      ``active``, ``owner``, ``posting`` or ``memo`` keys for
      any account. This mode is only used for *foreign*
      signatures!

    If no node is provided, it will connect to default nodes from
    nectar.NodeList. Default settings can be changed with:

    .. code-block:: python

        hive = Hive(<host>)

    where ``<host>`` starts with ``https://``, ``ws://`` or ``wss://``.

    The purpose of this class it to simplify interaction with
    Hive.

    The idea is to have a class that allows to do this:

    .. code-block:: python

        >>> from nectar import Hive
        >>> hive = Hive()
        >>> print(hive.get_blockchain_version())  # doctest: +SKIP

    This class also deals with edits, votes and reading content.

    Example for adding a custom chain:

    .. code-block:: python

        from nectar import Hive
        hv = Hive(node=["https://mytstnet.com"], custom_chains={"MYTESTNET":
            {'chain_assets': [{'asset': 'HBD', 'id': 0, 'precision': 3, 'symbol': 'HBD'},
                              {'asset': 'HIVE', 'id': 1, 'precision': 3, 'symbol': 'HIVE'},
                              {'asset': 'VESTS', 'id': 2, 'precision': 6, 'symbol': 'VESTS'}],
             'chain_id': '79276aea5d4877d9a25892eaa01b0adf019d3e5cb12a97478df3298ccdd01674',
             'min_version': '0.0.0',
             'prefix': 'MTN'}
            }
        )

    """

    def get_network(self, use_stored_data=True, config=None):
        """Identify the network

        :param bool use_stored_data: if True, stored data will be returned. If stored data are
                                     empty or old, refresh_data() is used.

        :returns: Network parameters
        :rtype: dictionary
        """
        if use_stored_data:
            self.refresh_data("config")
            return self.data["network"]

        if self.rpc is None:
            return known_chains["HIVE"]
        try:
            return self.rpc.get_network(props=config)
        except Exception:
            return known_chains["HIVE"]

    def rshares_to_token_backed_dollar(
        self, rshares, not_broadcasted_vote=False, use_stored_data=True
    ):
        return self.rshares_to_hbd(
            rshares, not_broadcasted_vote=not_broadcasted_vote, use_stored_data=use_stored_data
        )

    def rshares_to_hbd(self, rshares, not_broadcasted_vote=False, use_stored_data=True):
        """Calculates the current HBD value of a vote"""
        payout = float(rshares) * self.get_hbd_per_rshares(
            use_stored_data=use_stored_data,
            not_broadcasted_vote_rshares=rshares if not_broadcasted_vote else 0,
        )
        return payout

    def get_hbd_per_rshares(self, not_broadcasted_vote_rshares=0, use_stored_data=True):
        """Returns the current rshares to HBD ratio"""
        reward_fund = self.get_reward_funds(use_stored_data=use_stored_data)
        reward_balance = float(Amount(reward_fund["reward_balance"], blockchain_instance=self))
        recent_claims = float(reward_fund["recent_claims"]) + not_broadcasted_vote_rshares
        if recent_claims == 0:
            return 0
        fund_per_share = reward_balance / (recent_claims)
        median_price = self.get_median_price(use_stored_data=use_stored_data)
        if median_price is None:
            return 0
        HBD_price = float(median_price * (Amount(1, self.hive_symbol, blockchain_instance=self)))
        return fund_per_share * HBD_price

    def get_token_per_mvest(self, time_stamp=None, use_stored_data=True):
        return self.get_hive_per_mvest(time_stamp=time_stamp, use_stored_data=use_stored_data)

    def get_hive_per_mvest(self, time_stamp=None, use_stored_data=True):
        """Returns the MVEST to HIVE ratio

        :param int time_stamp: (optional) if set, return an estimated
            HIVE per MVEST ratio for the given time stamp. If unset the
            current ratio is returned (default). (can also be a datetime object)
        """
        if self.offline and time_stamp is None:
            time_stamp = datetime.now(timezone.utc)

        if time_stamp is not None:
            if isinstance(time_stamp, (datetime, date)):
                time_stamp = formatToTimeStamp(time_stamp)
            a = 2.1325476281078992e-05
            b = -31099.685481490847
            a2 = 2.9019227739473682e-07
            b2 = 48.41432402074669

            if time_stamp < (b2 - b) / (a - a2):
                return a * time_stamp + b
            else:
                return a2 * time_stamp + b2
        global_properties = self.get_dynamic_global_properties(use_stored_data=use_stored_data)
        return float(
            Amount(global_properties["total_vesting_fund_hive"], blockchain_instance=self)
        ) / (
            float(Amount(global_properties["total_vesting_shares"], blockchain_instance=self)) / 1e6
        )

    def vests_to_hp(self, vests, timestamp=None, use_stored_data=True):
        """Converts vests to HP

        :param amount.Amount vests/float vests: Vests to convert
        :param int timestamp: (Optional) Can be used to calculate
            the conversion rate from the past

        """
        if isinstance(vests, Amount):
            vests = float(vests)
        return (
            float(vests) / 1e6 * self.get_hive_per_mvest(timestamp, use_stored_data=use_stored_data)
        )

    def vests_to_token_power(self, vests, timestamp=None, use_stored_data=True):
        return self.vests_to_hp(vests, timestamp=timestamp, use_stored_data=use_stored_data)

    def hp_to_vests(self, hp, timestamp=None, use_stored_data=True):
        """Converts HP to vests

        :param float hp: Hive power to convert
        :param datetime timestamp: (Optional) Can be used to calculate
            the conversion rate from the past
        """
        return hp * 1e6 / self.get_hive_per_mvest(timestamp, use_stored_data=use_stored_data)

    def token_power_to_vests(self, token_power, timestamp=None, use_stored_data=True):
        return self.hp_to_vests(token_power, timestamp=timestamp, use_stored_data=use_stored_data)

    def token_power_to_token_backed_dollar(
        self,
        token_power,
        post_rshares=0,
        voting_power=HIVE_100_PERCENT,
        vote_pct=HIVE_100_PERCENT,
        not_broadcasted_vote=True,
        use_stored_data=True,
    ):
        """
        Convert token power (Hive Power) to its token-backed dollar equivalent (HBD).

        Parameters:
            token_power: Hive Power amount (numeric or Amount-like) to convert.
            post_rshares (int): Optional existing rshares on the post to include when estimating payout.
            voting_power (int): Voter's current voting power (use HIVE_100_PERCENT for full power).
            vote_pct (int): Vote weight to apply (use HIVE_100_PERCENT for 100%).
            not_broadcasted_vote (bool): If True, include the vote as not-yet-broadcasted when computing reward pool effects.
            use_stored_data (bool): If True, prefer cached chain data when available.

        Returns:
            The estimated HBD value (token-backed dollar) corresponding to the provided token power.
        """
        return self.hp_to_hbd(
            token_power,
            post_rshares=post_rshares,
            voting_power=voting_power,
            vote_pct=vote_pct,
            not_broadcasted_vote=not_broadcasted_vote,
            use_stored_data=use_stored_data,
        )

    def hp_to_hbd(
        self,
        hp,
        post_rshares=0,
        voting_power=HIVE_100_PERCENT,
        vote_pct=HIVE_100_PERCENT,
        not_broadcasted_vote=True,
        use_stored_data=True,
    ):
        """
        Convert Hive Power (HP) to the estimated HBD payout this vote would produce.

        Parameters:
            hp (number): Amount of Hive Power to convert.
            post_rshares (int): Current post rshares to include when computing marginal effect of this vote.
            voting_power (int): Voter's current voting power (100% = 10000).
            vote_pct (int): Vote percentage to apply (100% = 10000).
            not_broadcasted_vote (bool): If True, treat the vote as not yet broadcast — the function will account for the vote reducing the available reward pool when applicable.
            use_stored_data (bool): If True, use cached chain/state data when available.

        Returns:
            HBD value corresponding to the provided HP under the current reward pool and price conditions (same type/format as the library's Amount/HBD results).
        """
        vesting_shares = int(self.hp_to_vests(hp, use_stored_data=use_stored_data))
        return self.vests_to_hbd(
            vesting_shares,
            post_rshares=post_rshares,
            voting_power=voting_power,
            vote_pct=vote_pct,
            not_broadcasted_vote=not_broadcasted_vote,
            use_stored_data=use_stored_data,
        )

    def vests_to_hbd(
        self,
        vests,
        post_rshares=0,
        voting_power=HIVE_100_PERCENT,
        vote_pct=HIVE_100_PERCENT,
        not_broadcasted_vote=True,
        use_stored_data=True,
    ):
        """
        Convert vesting shares to their equivalent HBD payout for a single vote.

        Given vesting shares, computes the vote's r-shares (taking into account post r-shares,
        voter power and percentage) and converts that r-shares value to an HBD payout.

        Parameters:
            vests: Vesting shares to use for the vote (number or Amount-like).
            post_rshares (int): Existing r-shares of the post being voted on; affects the r-shares calculation.
            voting_power (int): Voter's current voting power (units where 100% == HIVE_100_PERCENT).
            vote_pct (int): Vote percentage to apply (units where 100% == HIVE_100_PERCENT).
            not_broadcasted_vote (bool): If True, treat this as a not-yet-broadcast vote (it reduces the effective reward pool);
                if False, treat as already-applied (affects conversion math for very large votes).
            use_stored_data (bool): Whether to use cached chain parameters/reward state or query fresh data.

        Returns:
            The estimated HBD value (same type returned by rshares_to_hbd) for the vote.
        """
        vote_rshares = self.vests_to_rshares(
            vests, post_rshares=post_rshares, voting_power=voting_power, vote_pct=vote_pct
        )
        return self.rshares_to_hbd(
            vote_rshares, not_broadcasted_vote=not_broadcasted_vote, use_stored_data=use_stored_data
        )

    def hp_to_rshares(
        self,
        hive_power,
        post_rshares=0,
        voting_power=HIVE_100_PERCENT,
        vote_pct=HIVE_100_PERCENT,
        use_stored_data=True,
    ):
        """
        Convert Hive Power (HP) to r-shares used for voting.

        Given a Hive Power amount, computes the equivalent vesting shares and then the r-shares that a vote with the specified voting_power and vote_pct would produce against a post that currently has post_rshares. `voting_power` and `vote_pct` use the chain-normalized scale (100% == HIVE_100_PERCENT).

        Parameters:
            hive_power (number): Hive Power (HP) value to convert.
            post_rshares (int, optional): Current r-shares of the post being voted on; used to adjust the resulting r-shares. Defaults to 0.
            voting_power (int, optional): Voter's current voting power on the HIVE_100_PERCENT scale. Defaults to HIVE_100_PERCENT.
            vote_pct (int, optional): Vote percentage to apply on the HIVE_100_PERCENT scale. Defaults to HIVE_100_PERCENT.
            use_stored_data (bool, optional): Whether to use cached chain data when performing conversions. Defaults to True.

        Returns:
            int: The computed r-shares produced by the specified vote.
        """
        # calculate our account voting shares (from vests)
        vesting_shares = int(self.hp_to_vests(hive_power, use_stored_data=use_stored_data))
        rshares = self.vests_to_rshares(
            vesting_shares,
            post_rshares=post_rshares,
            voting_power=voting_power,
            vote_pct=vote_pct,
            use_stored_data=use_stored_data,
        )
        return rshares

    def vests_to_rshares(
        self,
        vests,
        post_rshares=0,
        voting_power=HIVE_100_PERCENT,
        vote_pct=HIVE_100_PERCENT,
        subtract_dust_threshold=True,
        use_stored_data=True,
    ):
        """
        Convert vesting shares to vote r-shares.

        Detailed behavior:
        - `vests` is the voter's vesting amount in VESTS (not in micro-vests); the implementation multiplies this value by 1e6 internally.
        - Computes the effective voting power using `voting_power` and `vote_pct`, applies Hive's normalization (HIVE_100_PERCENT), and returns the signed r-shares for that vote.
        - If `subtract_dust_threshold` is True, results at or below the chain dust threshold return 0; otherwise the threshold is subtracted from the computed r-shares.
        - The final r-shares are adjusted by `post_rshares` using the chain's vote-claim logic before being returned.

        Parameters:
            vests (int|float|Amount): Vesting shares in VESTS.
            post_rshares (int): Current r-shares on the post being voted (used to compute claim adjustment).
            voting_power (int): Voter's current voting power (100% == HIVE_100_PERCENT).
            vote_pct (int): Vote percentage to apply (100% == HIVE_100_PERCENT); sign of this value determines vote direction.
            subtract_dust_threshold (bool): If True, apply/subtract the chain dust threshold from the computed r-shares.
            use_stored_data (bool): Whether to use cached chain data for thresholds and calculations.

        Returns:
            int: Signed r-shares resulting from the provided vesting shares and vote parameters.
        """
        used_power = self._calc_resulting_vote(
            voting_power=voting_power, vote_pct=vote_pct, use_stored_data=use_stored_data
        )
        # calculate vote rshares
        rshares = int(math.copysign(vests * 1e6 * used_power / HIVE_100_PERCENT, vote_pct))
        if subtract_dust_threshold:
            if abs(rshares) <= self.get_dust_threshold(use_stored_data=use_stored_data):
                return 0
            rshares -= math.copysign(
                self.get_dust_threshold(use_stored_data=use_stored_data), vote_pct
            )
        rshares = self._calc_vote_claim(rshares, post_rshares)
        return rshares

    def hbd_to_rshares(self, hbd, not_broadcasted_vote=False, use_stored_data=True):
        """Obtain the r-shares from HBD

        :param hbd: HBD
        :type hbd: str, int, amount.Amount
        :param bool not_broadcasted_vote: not_broadcasted or already broadcasted vote (True = not_broadcasted vote).
         Only impactful for very high amounts of HBD. Slight modification to the value calculation, as the not_broadcasted
         vote rshares decreases the reward pool.

        """
        if isinstance(hbd, Amount):
            hbd = Amount(hbd, blockchain_instance=self)
        elif isinstance(hbd, str):
            hbd = Amount(hbd, blockchain_instance=self)
        else:
            hbd = Amount(hbd, self.hbd_symbol, blockchain_instance=self)
        if hbd["symbol"] != self.hbd_symbol:
            raise AssertionError("Should input HBD, not any other asset!")

        # If the vote was already broadcasted we can assume the blockchain values to be true
        if not not_broadcasted_vote:
            return int(float(hbd) / self.get_hbd_per_rshares(use_stored_data=use_stored_data))

        # If the vote wasn't broadcasted (yet), we have to calculate the rshares while considering
        # the change our vote is causing to the recent_claims. This is more important for really
        # big votes which have a significant impact on the recent_claims.
        reward_fund = self.get_reward_funds(use_stored_data=use_stored_data)
        median_price = self.get_median_price(use_stored_data=use_stored_data)
        recent_claims = int(reward_fund["recent_claims"])
        reward_balance = Amount(reward_fund["reward_balance"], blockchain_instance=self)
        reward_pool_hbd = median_price * reward_balance
        if hbd > reward_pool_hbd:
            raise ValueError("Provided more HBD than available in the reward pool.")

        # This is the formula we can use to determine the "true" rshares.
        # We get this formula by some math magic using the previous used formulas
        # FundsPerShare = (balance / (claims + newShares)) * Price
        # newShares = amount / FundsPerShare
        # We can now resolve both formulas for FundsPerShare and set the formulas to be equal
        # (balance / (claims + newShares)) * price = amount / newShares
        # Now we resolve for newShares resulting in:
        # newShares = claims * amount / (balance * price - amount)
        rshares = (
            recent_claims
            * float(hbd)
            / ((float(reward_balance) * float(median_price)) - float(hbd))
        )
        return int(rshares)

    def rshares_to_vote_pct(
        self,
        rshares,
        post_rshares=0,
        hive_power=None,
        vests=None,
        voting_power=HIVE_100_PERCENT,
        use_stored_data=True,
    ):
        """
        Compute the voting percentage required to achieve a target r-shares value.

        Given a desired r-shares (positive for upvotes, negative for downvotes) and either
        hive_power or vests (exactly one must be provided), return the voting percentage
        where 100% = 10000. The calculation accounts for post-vote r-shares adjustments,
        current dust-threshold behavior (post-hardfork), and the configured voting power.

        Parameters:
            rshares (int | float): Target r-shares value (signed).
            post_rshares (int, optional): R-shares already present on the post (positive
                for existing upvotes, negative for downvotes). Defaults to 0.
            hive_power (float, optional): Hive Power to use for the calculation. Provide
                this or `vests`, not both. If given, it is converted to vesting shares.
            vests (int, optional): Vesting shares (in micro-vests, i.e., vest*1e6). Provide
                this or `hive_power`, not both.
            voting_power (int, optional): Voter's current voting power where 100% = 10000.
                Defaults to HIVE_100_PERCENT.
            use_stored_data (bool, optional): Whether to use cached chain properties when
                available. Defaults to True.

        Returns:
            int: Signed voting percentage required (100% = 10000). The sign matches the
            sign of `rshares`.

        Raises:
            ValueError: If neither or both of `hive_power` and `vests` are provided.
        """
        if hive_power is None and vests is None:
            raise ValueError("Either hive_power or vests has to be set!")
        if hive_power is not None and vests is not None:
            raise ValueError("Either hive_power or vests has to be set. Not both!")
        if hive_power is not None:
            vests = int(self.hp_to_vests(hive_power, use_stored_data=use_stored_data) * 1e6)

        if self.hardfork >= 20:
            rshares += math.copysign(
                self.get_dust_threshold(use_stored_data=use_stored_data), rshares
            )

        if post_rshares >= 0 and rshares > 0:
            rshares = math.copysign(
                self._calc_revert_vote_claim(abs(rshares), post_rshares), rshares
            )
        elif post_rshares < 0 and rshares < 0:
            rshares = math.copysign(
                self._calc_revert_vote_claim(abs(rshares), abs(post_rshares)), rshares
            )
        elif post_rshares < 0 and rshares > 0:
            rshares = math.copysign(self._calc_revert_vote_claim(abs(rshares), 0), rshares)
        elif post_rshares > 0 and rshares < 0:
            rshares = math.copysign(
                self._calc_revert_vote_claim(abs(rshares), post_rshares), rshares
            )

        max_vote_denom = self._max_vote_denom(use_stored_data=use_stored_data)

        used_power = int(math.ceil(abs(rshares) * HIVE_100_PERCENT / vests))
        used_power = used_power * max_vote_denom

        vote_pct = used_power * HIVE_100_PERCENT / (60 * 60 * 24) / voting_power
        return int(math.copysign(vote_pct, rshares))

    def hbd_to_vote_pct(
        self,
        hbd,
        post_rshares=0,
        hive_power=None,
        vests=None,
        voting_power=HIVE_100_PERCENT,
        not_broadcasted_vote=True,
        use_stored_data=True,
    ):
        """
        Calculate the voting percentage required to achieve a target HBD payout for a given voting power and stake.

        Given a desired HBD amount, this returns the vote percentage (100% == 10000) that, when applied from the provided Hive Power or vesting shares, would produce approximately that payout. Exactly one of `hive_power` or `vests` must be provided.

        Parameters:
            hbd (str|int|Amount): Desired HBD payout. Accepts an Amount, numeric value, or asset string; will be converted to an Amount in the chain's HBD symbol.
            hive_power (number, optional): Voter's Hive Power. Mutually exclusive with `vests`.
            vests (number, optional): Voter's vesting shares. Mutually exclusive with `hive_power`.
            voting_power (int, optional): Current voting power normalization constant (default HIVE_100_PERCENT).
            not_broadcasted_vote (bool, optional): If True, treat the vote as not yet broadcast; this slightly changes calculations for very large HBD amounts because an unbroadcasted vote reduces the available reward pool.
            post_rshares (int, optional): rshares already present on the post (used when calculating required vote to reach a target).
            use_stored_data (bool, optional): Use cached chain properties when available.

        Returns:
            int: Required vote percentage where 100% == 10000. Values >10000 or < -10000 indicate the requested HBD is too large for a single vote.

        Raises:
            AssertionError: If the provided `hbd` cannot be interpreted as the chain's HBD asset.
        """
        if isinstance(hbd, Amount):
            hbd = Amount(hbd, blockchain_instance=self)
        elif isinstance(hbd, str):
            hbd = Amount(hbd, blockchain_instance=self)
        else:
            hbd = Amount(hbd, self.hbd_symbol, blockchain_instance=self)
        if hbd["symbol"] != self.hbd_symbol:
            raise AssertionError()
        rshares = self.hbd_to_rshares(
            hbd, not_broadcasted_vote=not_broadcasted_vote, use_stored_data=use_stored_data
        )
        return self.rshares_to_vote_pct(
            rshares,
            post_rshares=post_rshares,
            hive_power=hive_power,
            vests=vests,
            voting_power=voting_power,
            use_stored_data=use_stored_data,
        )

    @property
    def chain_params(self):
        if self.offline or self.rpc is None:
            return known_chains["HIVE"]
        else:
            return self.get_network()

    @property
    def hardfork(self):
        if self.offline or self.rpc is None:
            versions = known_chains["HIVE"]["min_version"]
        else:
            hf_prop = self.get_hardfork_properties()
            if "current_hardfork_version" in hf_prop:
                versions = hf_prop["current_hardfork_version"]
            else:
                versions = self.get_blockchain_version()
        return int(versions.split(".")[1])

    @property
    def is_hive(self):
        config = self.get_config()
        if config is None:
            return True
        return "HIVE_CHAIN_ID" in self.get_config()

    @property
    def hbd_symbol(self):
        """get the current chains symbol for HBD (e.g. "TBD" on testnet)"""
        return self.backed_token_symbol

    @property
    def hive_symbol(self):
        """get the current chains symbol for HIVE (e.g. "TESTS" on testnet)"""
        return self.token_symbol

    @property
    def vests_symbol(self):
        """get the current chains symbol for VESTS"""
        return self.vest_token_symbol
