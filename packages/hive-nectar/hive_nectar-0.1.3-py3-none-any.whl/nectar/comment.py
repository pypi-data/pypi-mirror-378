# -*- coding: utf-8 -*-
import json
import logging
import math
from datetime import date, datetime, timezone

from nectar.constants import (
    HIVE_100_PERCENT,
    HIVE_REVERSE_AUCTION_WINDOW_SECONDS_HF6,
    HIVE_REVERSE_AUCTION_WINDOW_SECONDS_HF20,
    HIVE_REVERSE_AUCTION_WINDOW_SECONDS_HF21,
)
from nectarbase import operations

from .account import Account
from .amount import Amount
from .blockchainobject import BlockchainObject
from .exceptions import ContentDoesNotExistsException, VotingInvalidOnArchivedPost
from .instance import shared_blockchain_instance
from .price import Price
from .utils import (
    construct_authorperm,
    formatTimeString,
    formatToTimeStamp,
    make_patch,
    resolve_authorperm,
)

log = logging.getLogger(__name__)


class Comment(BlockchainObject):
    """Read data about a Comment/Post in the chain

    :param str authorperm: identifier to post/comment in the form of
        ``@author/permlink``
    :param str tags: defines which api is used. Can be bridge, tags, condenser or database (default = bridge)
    :param Blockchain blockchain_instance: Blockchain instance to use when accessing the RPC


    .. code-block:: python

    >>> from nectar.comment import Comment
    >>> from nectar.account import Account
    >>> # Create a Hive blockchain instance
    >>> from nectar import Hive
    >>> hv = Hive()
    >>> acc = Account("gtg", blockchain_instance=hv)
    >>> authorperm = acc.get_blog(limit=1)[0]["authorperm"]
    >>> c = Comment(authorperm)
    >>> postdate = c["created"]
    >>> postdate_str = c.json()["created"]

    """

    type_id = 8

    def __init__(
        self,
        authorperm,
        api="bridge",
        observer="",
        full=True,
        lazy=False,
        blockchain_instance=None,
    ):
        """
        Create a Comment object representing a Hive post or comment.

        Supports initializing from either an author/permlink string ("author/permlink") or a dict containing at least "author" and "permlink". For a string input the constructor resolves and stores author, permlink, and authorperm. For a dict input the constructor normalizes the dict via _parse_json_data (timestamps, amounts, metadata) and sets the canonical "authorperm" before delegating to the BlockchainObject constructor.

        Parameters:
            authorperm: Either an "author/permlink" string or a dict with "author" and "permlink".
            api: RPC bridge to use (defaults to "bridge"); stored on the instance.
            observer: Optional observer identifier stored on the instance.
            full: If True, load all fields immediately; if False, allow partial/lazy loading.
            lazy: If True, delay full object loading until needed.

        Note: The blockchain instance is taken from blockchain_instance (if provided) or the module's shared_blockchain_instance(). The constructor sets instance attributes and then calls the parent initializer with id_item="authorperm".
        """
        self.full = full
        self.lazy = lazy
        self.api = api
        self.observer = observer
        self.blockchain = blockchain_instance or shared_blockchain_instance()
        if isinstance(authorperm, str) and authorperm != "":
            [author, permlink] = resolve_authorperm(authorperm)
            self["id"] = 0
            self["author"] = author
            self["permlink"] = permlink
            self["authorperm"] = authorperm
        elif isinstance(authorperm, dict) and "author" in authorperm and "permlink" in authorperm:
            authorperm["authorperm"] = construct_authorperm(
                authorperm["author"], authorperm["permlink"]
            )
            authorperm = self._parse_json_data(authorperm)
        super(Comment, self).__init__(
            authorperm,
            id_item="authorperm",
            lazy=lazy,
            full=full,
            blockchain_instance=self.blockchain,
        )

    def _parse_json_data(self, comment):
        """
        Normalize and convert raw comment JSON fields into Python-native types.

        This parses and mutates the given comment dict in-place and returns it. Normalizations:
        - Converts known timestamp strings (e.g., "created", "last_update", "cashout_time") to datetime using formatTimeString.
        - Converts monetary fields backed by the chain's backed token (HBD) into Amount objects using the instance's backed_token_symbol.
        - Ensures a "community" key exists and parses `json_metadata` (string/bytes) into a dict; extracts `tags` and `community` from that metadata when present.
        - Converts numeric string fields like `author_reputation` and `net_rshares` to ints.
        - Normalizes each entry in `active_votes`: converts vote `time` to datetime and numeric strings (`rshares`, `reputation`) to ints (falling back to 0 on parse errors).

        Parameters:
            comment (dict): Raw comment/post data as returned by the node RPC.

        Returns:
            dict: The same comment dict with normalized fields (timestamps as datetimes, amounts as Amount objects, json_metadata as dict, numeric fields as ints).
        """
        parse_times = [
            "active",
            "cashout_time",
            "created",
            "last_payout",
            "last_update",
            "updated",
            "max_cashout_time",
        ]
        for p in parse_times:
            if p in comment and isinstance(comment.get(p), str):
                comment[p] = formatTimeString(comment.get(p, "1970-01-01T00:00:00"))
        # Parse Amounts
        hbd_amounts = [
            "total_payout_value",
            "max_accepted_payout",
            "pending_payout_value",
            "curator_payout_value",
            "total_pending_payout_value",
            "promoted",
        ]
        for p in hbd_amounts:
            if p in comment and isinstance(comment.get(p), (str, list, dict)):
                value = comment.get(p, "0.000 %s" % (self.blockchain.backed_token_symbol))
                if (
                    isinstance(value, str)
                    and value.split(" ")[1] != self.blockchain.backed_token_symbol
                ):
                    value = value.split(" ")[0] + " " + self.blockchain.backed_token_symbol
                comment[p] = Amount(value, blockchain_instance=self.blockchain)

        if "community" not in comment:
            comment["community"] = ""

        # turn json_metadata into python dict
        meta_str = comment.get("json_metadata", "{}")
        if meta_str == "{}":
            comment["json_metadata"] = meta_str
        if isinstance(meta_str, (str, bytes, bytearray)):
            try:
                comment["json_metadata"] = json.loads(meta_str)
            except Exception:
                comment["json_metadata"] = {}

        comment["tags"] = []
        if isinstance(comment["json_metadata"], dict):
            if "tags" in comment["json_metadata"]:
                comment["tags"] = comment["json_metadata"]["tags"]
            if "community" in comment["json_metadata"]:
                comment["community"] = comment["json_metadata"]["community"]

        parse_int = [
            "author_reputation",
            "net_rshares",
        ]
        for p in parse_int:
            if p in comment and isinstance(comment.get(p), str):
                comment[p] = int(comment.get(p, "0"))

        if "active_votes" in comment:
            new_active_votes = []
            for vote in comment["active_votes"]:
                if "time" in vote and isinstance(vote.get("time"), str):
                    vote["time"] = formatTimeString(vote.get("time", "1970-01-01T00:00:00"))
                parse_int = [
                    "rshares",
                    "reputation",
                ]
                for p in parse_int:
                    if p in vote and isinstance(vote.get(p), str):
                        try:
                            vote[p] = int(vote.get(p, "0"))
                        except ValueError:
                            vote[p] = int(0)
                new_active_votes.append(vote)
            comment["active_votes"] = new_active_votes
        return comment

    def refresh(self):
        if self.identifier == "":
            return
        if not self.blockchain.is_connected():
            return
        [author, permlink] = resolve_authorperm(self.identifier)
        self.blockchain.rpc.set_next_node_on_empty_reply(True)
        if self.blockchain.rpc.get_use_appbase():
            from nectarapi.exceptions import InvalidParameters

            try:
                if self.api == "tags":
                    content = self.blockchain.rpc.get_discussion(
                        {"author": author, "permlink": permlink}, api="tags"
                    )
                elif self.api == "database":
                    content = self.blockchain.rpc.list_comments(
                        {"start": [author, permlink], "limit": 1, "order": "by_permlink"},
                        api="database",
                    )
                elif self.api == "bridge":
                    content = self.blockchain.rpc.get_post(
                        {"author": author, "permlink": permlink, "observer": self.observer},
                        api="bridge",
                    )
                elif self.api == "condenser":
                    content = self.blockchain.rpc.get_content(author, permlink, api="condenser")
                else:
                    raise ValueError("api must be: tags, database, bridge or condenser")
                if content is not None and "comments" in content:
                    content = content["comments"]
                if isinstance(content, list) and len(content) > 0:
                    content = content[0]
            except InvalidParameters:
                raise ContentDoesNotExistsException(self.identifier)
        else:
            from nectarapi.exceptions import InvalidParameters

            try:
                content = self.blockchain.rpc.get_content(author, permlink)
            except InvalidParameters:
                raise ContentDoesNotExistsException(self.identifier)
        if not content or not content["author"] or not content["permlink"]:
            raise ContentDoesNotExistsException(self.identifier)
        content = self._parse_json_data(content)
        content["authorperm"] = construct_authorperm(content["author"], content["permlink"])
        super(Comment, self).__init__(
            content,
            id_item="authorperm",
            lazy=self.lazy,
            full=self.full,
            blockchain_instance=self.blockchain,
        )

    def json(self):
        """
        Return a JSON-serializable dict representation of the Comment.

        Removes internal-only keys (e.g., "authorperm", "tags"), ensures json-compatible types, and normalizes several fields so the result can be safely serialized to JSON and consumed by external callers or APIs. Normalizations performed:
        - Serializes `json_metadata` to a compact JSON string.
        - Converts datetime/date values in fields like "created", "updated", "last_payout", "cashout_time", "active", and "max_cashout_time" to formatted time strings.
        - Converts Amount instances in HBD-related fields (e.g., "total_payout_value", "pending_payout_value", "curator_payout_value", "promoted", etc.) to their JSON representation via Amount.json().
        - Converts selected integer fields ("author_reputation", "net_rshares") and vote numeric fields ("rshares", "reputation") to strings to preserve precision across transports.
        - Normalizes times and numeric fields inside each entry of "active_votes".

        Returns:
            dict: A JSON-safe copy of the comment data suitable for json.dumps or returning from an API.
        """
        output = self.copy()
        if "authorperm" in output:
            output.pop("authorperm")
        if "json_metadata" in output:
            output["json_metadata"] = json.dumps(output["json_metadata"], separators=[",", ":"])
        if "tags" in output:
            output.pop("tags")
        parse_times = [
            "active",
            "cashout_time",
            "created",
            "last_payout",
            "last_update",
            "updated",
            "max_cashout_time",
        ]
        for p in parse_times:
            if p in output:
                p_date = output.get(p, datetime(1970, 1, 1, 0, 0))
                if isinstance(p_date, (datetime, date)):
                    output[p] = formatTimeString(p_date)
                else:
                    output[p] = p_date
        hbd_amounts = [
            "total_payout_value",
            "max_accepted_payout",
            "pending_payout_value",
            "curator_payout_value",
            "total_pending_payout_value",
            "promoted",
        ]
        for p in hbd_amounts:
            if p in output and isinstance(output[p], Amount):
                output[p] = output[p].json()
        parse_int = [
            "author_reputation",
            "net_rshares",
        ]
        for p in parse_int:
            if p in output and isinstance(output[p], int):
                output[p] = str(output[p])
        if "active_votes" in output:
            new_active_votes = []
            for vote in output["active_votes"]:
                if "time" in vote:
                    p_date = vote.get("time", datetime(1970, 1, 1, 0, 0))
                    if isinstance(p_date, (datetime, date)):
                        vote["time"] = formatTimeString(p_date)
                    else:
                        vote["time"] = p_date
                parse_int = [
                    "rshares",
                    "reputation",
                ]
                for p in parse_int:
                    if p in vote and isinstance(vote[p], int):
                        vote[p] = str(vote[p])
                new_active_votes.append(vote)
            output["active_votes"] = new_active_votes
        return json.loads(str(json.dumps(output)))

    @property
    def id(self):
        return self["id"]

    @property
    def author(self):
        return self["author"]

    @property
    def permlink(self):
        return self["permlink"]

    @property
    def authorperm(self):
        return construct_authorperm(self["author"], self["permlink"])

    @property
    def category(self):
        if "category" in self:
            return self["category"]
        else:
            return ""

    @property
    def community(self):
        if "community" in self:
            return self["community"]
        else:
            return ""

    @property
    def community_title(self):
        """The Community title property."""
        if "community_title" in self:
            return self["community_title"]
        else:
            return ""

    @property
    def parent_author(self):
        if "parent_author" in self:
            return self["parent_author"]
        else:
            return ""

    @property
    def parent_permlink(self):
        if "parent_permlink" in self:
            return self["parent_permlink"]
        else:
            return ""

    @property
    def depth(self):
        return self["depth"]

    @property
    def title(self):
        if "title" in self:
            return self["title"]
        else:
            return ""

    @property
    def body(self):
        if "body" in self:
            return self["body"]
        else:
            return ""

    @property
    def json_metadata(self):
        if "json_metadata" in self:
            return self["json_metadata"]
        else:
            return {}

    def is_main_post(self):
        """Returns True if main post, and False if this is a comment (reply)."""
        if "depth" in self:
            return self["depth"] == 0
        else:
            return self["parent_author"] == ""

    def is_comment(self):
        """Returns True if post is a comment"""
        if "depth" in self:
            return self["depth"] > 0
        else:
            return self["parent_author"] != ""

    @property
    def reward(self):
        """
        Return the post's total estimated reward as an Amount.

        This is the sum of `total_payout_value`, `curator_payout_value`, and `pending_payout_value`
        (from the comment data). Each component is converted to an Amount using the comment's
        blockchain-backed token symbol before summing.

        Returns:
            Amount: Total estimated reward (in the blockchain's backed token, e.g., HBD).
        """
        a_zero = Amount(0, self.blockchain.backed_token_symbol, blockchain_instance=self.blockchain)
        author = Amount(self.get("total_payout_value", a_zero), blockchain_instance=self.blockchain)
        curator = Amount(
            self.get("curator_payout_value", a_zero), blockchain_instance=self.blockchain
        )
        pending = Amount(
            self.get("pending_payout_value", a_zero), blockchain_instance=self.blockchain
        )
        return author + curator + pending

    def is_pending(self):
        """Returns if the payout is pending (the post/comment
        is younger than 7 days)
        """
        a_zero = Amount(0, self.blockchain.backed_token_symbol, blockchain_instance=self.blockchain)
        total = Amount(self.get("total_payout_value", a_zero), blockchain_instance=self.blockchain)
        post_age_days = self.time_elapsed().total_seconds() / 60 / 60 / 24
        return post_age_days < 7.0 and float(total) == 0

    def time_elapsed(self):
        """
        Return the time elapsed since the post was created as a timedelta.

        The difference is computed as now (UTC) minus the post's `created` timestamp (a timezone-aware datetime).
        A positive timedelta indicates the post is in the past; a negative value can occur if `created` is in the future.
        """
        return datetime.now(timezone.utc) - self["created"]

    def curation_penalty_compensation_hbd(self):
        """
        Calculate the HBD payout a post would need (after 15 minutes) to fully compensate the curation penalty for voting earlier than 15 minutes.

        This refreshes the comment data, selects the reverse-auction window based on the blockchain hardfork (HF6/HF20/HF21), and computes the required payout using the post's current reward and age.

        Returns:
            Amount: Estimated HBD payout required to offset the early-vote curation penalty.
        """
        self.refresh()
        if self.blockchain.hardfork >= 21:
            reverse_auction_window_seconds = HIVE_REVERSE_AUCTION_WINDOW_SECONDS_HF21
        elif self.blockchain.hardfork >= 20:
            reverse_auction_window_seconds = HIVE_REVERSE_AUCTION_WINDOW_SECONDS_HF20
        else:
            reverse_auction_window_seconds = HIVE_REVERSE_AUCTION_WINDOW_SECONDS_HF6
        elapsed_minutes = max((self.time_elapsed()).total_seconds() / 60, 1e-6)
        return self.reward * reverse_auction_window_seconds / (elapsed_minutes**2)

    def estimate_curation_hbd(self, vote_value_hbd, estimated_value_hbd=None):
        """
        Estimate the curation reward (in HBD) for a given vote on this post.

        Refreshes the post data from the chain before computing. If `estimated_value_hbd` is not provided, the current post reward is used as the estimated total post value. The returned value is an estimate of the curator's HBD payout for a vote of size `vote_value_hbd`, accounting for the current curation penalty.

        Parameters:
            vote_value_hbd (float): Vote value in HBD used to compute the curation share.
            estimated_value_hbd (float, optional): Estimated total post value in HBD to scale the curation; defaults to the post's current reward.

        Returns:
            float: Estimated curation reward in HBD for the provided vote value.
        """
        self.refresh()
        if estimated_value_hbd is None:
            estimated_value_hbd = float(self.reward)
        t = 1.0 - self.get_curation_penalty()
        k = vote_value_hbd / (vote_value_hbd + float(self.reward))
        K = (1 - math.sqrt(1 - k)) / 4 / k
        return K * vote_value_hbd * t * math.sqrt(estimated_value_hbd)

    def get_curation_penalty(self, vote_time=None):
        """
        Return the curation penalty factor for a vote at a given time.

        Calculates a value in [0.0, 1.0] representing the fraction of curation rewards
        that will be removed due to early voting (0.0 = no penalty, 1.0 = full penalty).
        The penalty is based on the elapsed time between the post's creation and
        the vote time, scaled by the Hive reverse-auction window for the node's
        current hardfork (HF21, HF20, or HF6).

        Parameters:
            vote_time (datetime | date | str | None): Time of the vote. If None,
                the current time is used. If a string is given it will be parsed
                with the module's time formatter.

        Returns:
            float: Penalty fraction in the range [0.0, 1.0].

        Raises:
            ValueError: If vote_time is not None and not a datetime, date, or parseable string.
        """
        if vote_time is None:
            elapsed_seconds = self.time_elapsed().total_seconds()
        elif isinstance(vote_time, str):
            elapsed_seconds = (formatTimeString(vote_time) - self["created"]).total_seconds()
        elif isinstance(vote_time, (datetime, date)):
            elapsed_seconds = (vote_time - self["created"]).total_seconds()
        else:
            raise ValueError("vote_time must be a string or a datetime")
        if self.blockchain.hardfork >= 21:
            reward = elapsed_seconds / HIVE_REVERSE_AUCTION_WINDOW_SECONDS_HF21
        elif self.blockchain.hardfork >= 20:
            reward = elapsed_seconds / HIVE_REVERSE_AUCTION_WINDOW_SECONDS_HF20
        else:
            reward = elapsed_seconds / HIVE_REVERSE_AUCTION_WINDOW_SECONDS_HF6
        if reward > 1:
            reward = 1.0
        return 1.0 - reward

    def get_vote_with_curation(self, voter=None, raw_data=False, pending_payout_value=None):
        """
        Return the specified voter's vote for this comment, optionally augmented with curation data.

        If `voter` is not found in the comment's votes returns None. When a vote is found:
        - If `raw_data` is True or the post is not pending payout, returns the raw vote dict.
        - If the post is pending and `raw_data` is False, returns the vote dict augmented with:
          - `curation_reward`: the vote's curation reward (in HBD)
          - `ROI`: percent return on the voter's effective voting value

        Parameters:
            voter (str or Account, optional): Voter name or Account. If omitted, defaults to the post author as an Account.
            raw_data (bool, optional): If True, return the found vote without adding curation/ROI fields.
            pending_payout_value (float or str, optional): If provided, use this HBD value instead of the current pending payout when computing curation rewards.

        Returns:
            dict or None: The vote dictionary (possibly augmented with `curation_reward` and `ROI`) or None if the voter has not voted.
        """
        specific_vote = None
        if voter is None:
            voter = Account(self["author"], blockchain_instance=self.blockchain)
        else:
            voter = Account(voter, blockchain_instance=self.blockchain)
        if "active_votes" in self:
            for vote in self["active_votes"]:
                if voter["name"] == vote["voter"]:
                    specific_vote = vote
        else:
            active_votes = self.get_votes()
            for vote in active_votes:
                if voter["name"] == vote["voter"]:
                    specific_vote = vote
        if specific_vote is not None and (raw_data or not self.is_pending()):
            return specific_vote
        elif specific_vote is not None:
            curation_reward = self.get_curation_rewards(
                pending_payout_hbd=True, pending_payout_value=pending_payout_value
            )
            specific_vote["curation_reward"] = curation_reward["active_votes"][voter["name"]]
            specific_vote["ROI"] = (
                float(curation_reward["active_votes"][voter["name"]])
                / float(
                    voter.get_voting_value(
                        voting_power=None, voting_weight=specific_vote["percent"] / 100
                    )
                )
                * 100
            )
            return specific_vote
        else:
            return None

    def get_beneficiaries_pct(self):
        """
        Return the sum of beneficiary weights as a fraction of the full payout.

        If the post has a `beneficiaries` list of dicts with integer `weight` fields (0–10000 representing 0%–100%), this returns the total weight divided by 100.0 (i.e., a float in 0.0–100.0/100 range; typical values are 0.0–1.0).
        """
        beneficiaries = self["beneficiaries"]
        weight = 0
        for b in beneficiaries:
            weight += b["weight"]
        return weight / HIVE_100_PERCENT

    def get_rewards(self):
        """
        Return the post's total, author, and curator payouts as Amount objects (HBD).

        If the post is pending, returns an estimated total based on pending_payout_value and derives the author's share via get_author_rewards(); curator_payout is computed as the difference. For finalized posts, uses total_payout_value and curator_payout_value.

        Note: beneficiary rewards (if any) are already deducted from the returned author_payout and total_payout.

        Returns:
            dict: {
                "total_payout": Amount,
                "author_payout": Amount,
                "curator_payout": Amount,
            }
        """
        if self.is_pending():
            total_payout = Amount(self["pending_payout_value"], blockchain_instance=self.blockchain)
            author_payout = self.get_author_rewards()["total_payout_HBD"]
            curator_payout = total_payout - author_payout
        else:
            author_payout = Amount(self["total_payout_value"], blockchain_instance=self.blockchain)
            curator_payout = Amount(
                self["curator_payout_value"], blockchain_instance=self.blockchain
            )
            total_payout = author_payout + curator_payout
        return {
            "total_payout": total_payout,
            "author_payout": author_payout,
            "curator_payout": curator_payout,
        }

    def get_author_rewards(self):
        """
        Return the computed author-side rewards for this post.

        If the post payout is not pending, returns zero HP/HBD payouts and the concrete total payout as `total_payout_HBD`. If the payout is pending, computes the author’s share after curation and beneficiaries, and—when price history and percent_hbd are available—splits that share into HBD and HP equivalents.

        Returns:
            dict: A dictionary with the following keys:
                - pending_rewards (bool): True when the post payout is still pending.
                - payout_HP (Amount or None): Estimated Hive Power payout (Amount) when pending and convertible; otherwise 0 Amount (when not pending) or None.
                - payout_HBD (Amount or None): Estimated HBD payout (Amount) when pending and convertible; otherwise 0 Amount (when not pending) or None.
                - total_payout_HBD (Amount): Total author-side payout expressed in HBD-equivalent units when pending, or the concrete total payout when not pending.
                - total_payout (Amount, optional): Present only for pending payouts in the non-convertible branch; the author-side token amount before HBD/HP splitting.
                - Note: When price/percent data is not available, `payout_HP` and `payout_HBD` will be None and only `total_payout_HBD`/`total_payout` convey the author share.

        Example:
            {
                "pending_rewards": True,
                "payout_HP": Amount(...),         # HP equivalent (when convertible)
                "payout_HBD": Amount(...),        # HBD portion (when convertible)
                "total_payout_HBD": Amount(...)   # Total author share in HBD-equivalent
            }
        """
        if not self.is_pending():
            return {
                "pending_rewards": False,
                "payout_HP": Amount(
                    0, self.blockchain.token_symbol, blockchain_instance=self.blockchain
                ),
                "payout_HBD": Amount(
                    0, self.blockchain.backed_token_symbol, blockchain_instance=self.blockchain
                ),
                "total_payout_HBD": Amount(
                    self["total_payout_value"], blockchain_instance=self.blockchain
                ),
            }
        author_reward_factor = 0.5
        median_hist = self.blockchain.get_current_median_history()
        if median_hist is not None:
            median_price = Price(median_hist, blockchain_instance=self.blockchain)
        beneficiaries_pct = self.get_beneficiaries_pct()
        curation_tokens = self.reward * author_reward_factor
        author_tokens = self.reward - curation_tokens
        curation_rewards = self.get_curation_rewards()
        if self.blockchain.hardfork >= 20 and median_hist is not None:
            author_tokens += median_price * curation_rewards["unclaimed_rewards"]
        benefactor_tokens = author_tokens * beneficiaries_pct / HIVE_100_PERCENT
        author_tokens -= benefactor_tokens

        if median_hist is not None and "percent_hbd" in self:
            hbd_payout = author_tokens * self["percent_hbd"] / 20000.0
            hp_payout = median_price.as_base(self.blockchain.token_symbol) * (
                author_tokens - hbd_payout
            )
            return {
                "pending_rewards": True,
                "payout_HP": hp_payout,
                "payout_HBD": hbd_payout,
                "total_payout_HBD": author_tokens,
            }
        else:
            return {
                "pending_rewards": True,
                "total_payout": author_tokens,
                # HBD/HP primary fields
                "total_payout_HBD": author_tokens,
                "payout_HBD": None,
                "payout_HP": None,
            }

    def get_curation_rewards(self, pending_payout_hbd=False, pending_payout_value=None):
        """
        Calculate curation rewards for this post and distribute them across active voters.

        Parameters:
            pending_payout_hbd (bool): If True, compute and return rewards in HBD (do not convert to HIVE/HP). Default False.
            pending_payout_value (float | str | Amount | None): Optional override for the post's pending payout value used when the post is still pending.
                - If None and the post is pending, the function uses the post's stored pending_payout_value.
                - Accepted types: numeric, string amount, or an Amount instance.

        Returns:
            dict: {
                "pending_rewards": bool,        # True if the post is still within the payout window (uses pending_payout_value)
                "unclaimed_rewards": Amount,    # Amount reserved for unclaimed curation (e.g., self-votes or early votes)
                "active_votes": dict            # Mapping voter_name -> Amount of curation reward allocated to that voter
            }

        Notes:
            - The function splits the curation pool using the protocol's curator share (50% by default) and prorates per-voter claims by vote weight.
            - When a current median price history is available, rewards may be converted between HBD and the chain's token (HP) according to pending_payout_hbd.
        """
        median_hist = self.blockchain.get_current_median_history()
        if median_hist is not None:
            median_price = Price(median_hist, blockchain_instance=self.blockchain)
        pending_rewards = False
        active_votes_list = self.get_votes()
        curator_reward_factor = 0.5

        if "total_vote_weight" in self:
            total_vote_weight = self["total_vote_weight"]
        active_votes_json_list = []
        for vote in active_votes_list:
            if "weight" not in vote:
                vote.refresh()
                active_votes_json_list.append(vote.json())
            else:
                active_votes_json_list.append(vote.json())

        total_vote_weight = 0
        for vote in active_votes_json_list:
            total_vote_weight += vote["weight"]

        if not self.is_pending():
            if pending_payout_hbd or median_hist is None:
                max_rewards = Amount(
                    self["curator_payout_value"], blockchain_instance=self.blockchain
                )
            else:
                max_rewards = median_price.as_base(self.blockchain.token_symbol) * Amount(
                    self["curator_payout_value"], blockchain_instance=self.blockchain
                )
            unclaimed_rewards = Amount(
                0, self.blockchain.token_symbol, blockchain_instance=self.blockchain
            )
        else:
            if pending_payout_value is None and "pending_payout_value" in self:
                pending_payout_value = Amount(
                    self["pending_payout_value"], blockchain_instance=self.blockchain
                )
            elif pending_payout_value is None:
                pending_payout_value = 0
            elif isinstance(pending_payout_value, (float, int)):
                pending_payout_value = Amount(
                    pending_payout_value,
                    self.blockchain.backed_token_symbol,
                    blockchain_instance=self.blockchain,
                )
            elif isinstance(pending_payout_value, str):
                pending_payout_value = Amount(
                    pending_payout_value, blockchain_instance=self.blockchain
                )
            if pending_payout_hbd or median_hist is None:
                max_rewards = pending_payout_value * curator_reward_factor
            else:
                max_rewards = median_price.as_base(self.blockchain.token_symbol) * (
                    pending_payout_value * curator_reward_factor
                )
            unclaimed_rewards = max_rewards.copy()
            pending_rewards = True

        active_votes = {}

        for vote in active_votes_json_list:
            if total_vote_weight > 0:
                claim = max_rewards * int(vote["weight"]) / total_vote_weight
            else:
                claim = 0
            if claim > 0 and pending_rewards:
                unclaimed_rewards -= claim
            if claim > 0:
                active_votes[vote["voter"]] = claim
            else:
                active_votes[vote["voter"]] = 0

        return {
            "pending_rewards": pending_rewards,
            "unclaimed_rewards": unclaimed_rewards,
            "active_votes": active_votes,
        }

    def get_reblogged_by(self, identifier=None):
        """Shows in which blogs this post appears"""
        if not identifier:
            post_author = self["author"]
            post_permlink = self["permlink"]
        else:
            [post_author, post_permlink] = resolve_authorperm(identifier)
        if not self.blockchain.is_connected():
            return None
        self.blockchain.rpc.set_next_node_on_empty_reply(False)
        if self.blockchain.rpc.get_use_appbase():
            return self.blockchain.rpc.get_reblogged_by(
                {"author": post_author, "permlink": post_permlink}, api="condenser"
            )["accounts"]
        else:
            return self.blockchain.rpc.get_reblogged_by(post_author, post_permlink, api="condenser")

    def get_replies(self, raw_data=False, identifier=None):
        """Returns content replies

        :param bool raw_data: When set to False, the replies will be returned as Comment class objects
        """
        if not identifier:
            post_author = self["author"]
            post_permlink = self["permlink"]
        else:
            [post_author, post_permlink] = resolve_authorperm(identifier)
        if not self.blockchain.is_connected():
            return None
        self.blockchain.rpc.set_next_node_on_empty_reply(False)

        # Use bridge.get_discussion API
        content_replies = self.blockchain.rpc.get_discussion(
            {"author": post_author, "permlink": post_permlink, "observer": self.observer},
            api="bridge",
        )

        if not content_replies:
            return []

        # The response format is a dict with keys in 'author/permlink' format
        # We need to extract the replies by filtering out the original post
        original_key = f"{post_author}/{post_permlink}"
        replies = []

        for key, content in content_replies.items():
            # Skip the original post
            if key == original_key:
                continue
            # Add the reply
            replies.append(content)

        if raw_data:
            return replies
        return [Comment(c, blockchain_instance=self.blockchain) for c in replies]

    def get_all_replies(self, parent=None):
        """Returns all content replies"""
        if parent is None:
            parent = self
        if parent["children"] > 0:
            children = parent.get_replies()
            if children is None:
                return []
            for cc in children[:]:
                children.extend(self.get_all_replies(parent=cc))
            return children
        return []

    def get_parent(self, children=None):
        """Returns the parent post with depth == 0"""
        if children is None:
            children = self
        while children["depth"] > 0:
            children = Comment(
                construct_authorperm(children["parent_author"], children["parent_permlink"]),
                blockchain_instance=self.blockchain,
            )
        return children

    def get_votes(self, raw_data=False):
        """Returns all votes as ActiveVotes object"""
        if raw_data and "active_votes" in self:
            return self["active_votes"]
        from .vote import ActiveVotes

        authorperm = construct_authorperm(self["author"], self["permlink"])
        return ActiveVotes(authorperm, lazy=False, blockchain_instance=self.blockchain)

    def upvote(self, weight=+100, voter=None):
        """Upvote the post

        :param float weight: (optional) Weight for posting (-100.0 -
            +100.0) defaults to +100.0
        :param str voter: (optional) Voting account

        """
        if weight < 0:
            raise ValueError("Weight must be >= 0.")
        last_payout = self.get("last_payout", None)
        if last_payout is not None:
            if formatToTimeStamp(last_payout) > 0:
                raise VotingInvalidOnArchivedPost
        return self.vote(weight, account=voter)

    def downvote(self, weight=100, voter=None):
        """Downvote the post

        :param float weight: (optional) Weight for posting (-100.0 -
            +100.0) defaults to -100.0
        :param str voter: (optional) Voting account

        """
        if weight < 0:
            raise ValueError("Weight must be >= 0.")
        last_payout = self.get("last_payout", None)
        if last_payout is not None:
            if formatToTimeStamp(last_payout) > 0:
                raise VotingInvalidOnArchivedPost
        return self.vote(-weight, account=voter)

    def vote(self, weight, account=None, identifier=None, **kwargs):
        """Vote for a post

        :param float weight: Voting weight. Range: -100.0 - +100.0.
        :param str account: (optional) Account to use for voting. If
            ``account`` is not defined, the ``default_account`` will be used
            or a ValueError will be raised
        :param str identifier: Identifier for the post to vote. Takes the
            form ``@author/permlink``.

        """
        if not identifier:
            identifier = construct_authorperm(self["author"], self["permlink"])

        return self.blockchain.vote(weight, identifier, account=account)

    def edit(self, body, meta=None, replace=False):
        """Edit an existing post

        :param str body: Body of the reply
        :param json meta: JSON meta object that can be attached to the
            post. (optional)
        :param bool replace: Instead of calculating a *diff*, replace
            the post entirely (defaults to ``False``)

        """
        if not meta:
            meta = {}
        original_post = self

        if replace:
            newbody = body
        else:
            newbody = make_patch(original_post["body"], body)
            if not newbody:
                log.info("No changes made! Skipping ...")
                return

        reply_identifier = construct_authorperm(
            original_post["parent_author"], original_post["parent_permlink"]
        )

        new_meta = {}
        if meta is not None:
            if bool(original_post["json_metadata"]):
                new_meta = original_post["json_metadata"]
                for key in meta:
                    new_meta[key] = meta[key]
            else:
                new_meta = meta

        return self.blockchain.post(
            original_post["title"],
            newbody,
            reply_identifier=reply_identifier,
            author=original_post["author"],
            permlink=original_post["permlink"],
            json_metadata=new_meta,
        )

    def reply(self, body, title="", author="", meta=None):
        """Reply to an existing post

        :param str body: Body of the reply
        :param str title: Title of the reply post
        :param str author: Author of reply (optional) if not provided
            ``default_user`` will be used, if present, else
            a ``ValueError`` will be raised.
        :param json meta: JSON meta object that can be attached to the
            post. (optional)

        """
        return self.blockchain.post(
            title, body, json_metadata=meta, author=author, reply_identifier=self.identifier
        )

    def delete(self, account=None, identifier=None):
        """
        Delete this post or comment from the blockchain.

        If `identifier` is provided it must be an author/permlink string (e.g. "@author/permlink"); otherwise the current Comment's author and permlink are used. If `account` is not provided the method will use `blockchain.config["default_account"]` when present; otherwise a ValueError is raised.

        Note: a post/comment can only be deleted if it has no replies and no positive rshares.

        Parameters:
            account (str, optional): Account name to perform the deletion. If omitted, the configured default_account is used.
            identifier (str, optional): Author/permlink of the post to delete (format "@author/permlink"). Defaults to the current Comment.

        Returns:
            dict: Result of the blockchain finalizeOp / transaction broadcast.

        Raises:
            ValueError: If no account is provided and no default_account is configured.
        """
        if not account:
            if "default_account" in self.blockchain.config:
                account = self.blockchain.config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")
        account = Account(account, blockchain_instance=self.blockchain)
        if not identifier:
            post_author = self["author"]
            post_permlink = self["permlink"]
        else:
            [post_author, post_permlink] = resolve_authorperm(identifier)
        op = operations.Delete_comment(**{"author": post_author, "permlink": post_permlink})
        return self.blockchain.finalizeOp(op, account, "posting")

    def reblog(self, identifier=None, account=None):
        """
        Create a reblog (resteem) for the specified post.

        Parameters:
            identifier (str, optional): Post identifier in the form "@author/permlink". If omitted, uses this Comment's identifier.
            account (str, optional): Name of the posting account to perform the reblog. If omitted, the configured `default_account` is used.

        Returns:
            dict: Result from the blockchain custom_json operation.

        Raises:
            ValueError: If no account is provided and no `default_account` is configured.
        """
        if not account:
            account = self.blockchain.configStorage.get("default_account")
        if not account:
            raise ValueError("You need to provide an account")
        account = Account(account, blockchain_instance=self.blockchain)
        if identifier is None:
            identifier = self.identifier
        author, permlink = resolve_authorperm(identifier)
        json_body = ["reblog", {"account": account["name"], "author": author, "permlink": permlink}]
        return self.blockchain.custom_json(
            id="follow", json_data=json_body, required_posting_auths=[account["name"]]
        )


class RecentReplies(list):
    """Obtain a list of recent replies

    :param str author: author
    :param bool skip_own: (optional) Skip replies of the author to him/herself.
        Default: True
    :param Blockchain blockchain_instance: Blockchain instance to use when accessing the RPC
    """

    def __init__(
        self,
        author,
        skip_own=True,
        start_permlink="",
        limit=100,
        lazy=False,
        full=True,
        blockchain_instance=None,
    ):
        """
        Create a list of recent replies to a given account.

        Initializes the instance as a list of Comment objects built from the account's recent "replies" feed. By default replies authored by the same account are omitted when skip_own is True. If no blockchain connection is available during construction, initialization is aborted (the constructor returns early).

        Parameters:
            author (str): Account name whose replies to collect.
            skip_own (bool): If True, omit replies authored by `author`. Default True.
            start_permlink (str): Legacy/paging parameter; currently ignored by this implementation.
            limit (int): Maximum number of replies to collect; currently ignored (the underlying API call controls results).
            lazy (bool): If True, create Comment objects in lazy mode.
            full (bool): If True, create Comment objects with full data populated.

        Notes:
            - The blockchain_instance parameter is used to resolve RPC access and is intentionally undocumented here as a shared service.
            - The underlying account.get_account_posts(sort="replies", raw_data=True) call provides the source data; when it returns None or the instance is not connected, construction exits early.
        """
        self.blockchain = blockchain_instance or shared_blockchain_instance()
        if not self.blockchain.is_connected():
            return None
        self.blockchain.rpc.set_next_node_on_empty_reply(True)
        account = Account(author, blockchain_instance=self.blockchain)
        replies = account.get_account_posts(sort="replies", raw_data=True)
        comments = []
        if replies is None:
            replies = []
        for post in replies:
            if skip_own and post["author"] == author:
                continue
            comments.append(
                Comment(post, lazy=lazy, full=full, blockchain_instance=self.blockchain)
            )
        super(RecentReplies, self).__init__(comments)


class RecentByPath(list):
    """Obtain a list of posts recent by path, does the same as RankedPosts

    :param str path: path
    :param str tag: tag
    :param str observer: observer
    :param Blockchain blockchain_instance: Blockchain instance to use when accessing the RPC
    """

    def __init__(
        self,
        path="trending",
        tag="",
        observer="",
        lazy=False,
        full=True,
        limit=20,
        blockchain_instance=None,
    ):
        """
        Create a RecentByPath list by fetching ranked posts for a given path/tag and initializing the list with those posts.

        Parameters:
            path (str): Ranking category to fetch (e.g., "trending", "hot").
            tag (str): Optional tag to filter posts.
            observer (str): Observer account used for context-aware fetches (affects reward/curation visibility).
            lazy (bool): If True, create Comment objects lazily (defer full data loading).
            full (bool): If True, initialize Comment objects with full data when available.
            limit (int): Maximum number of posts to fetch.
        """
        self.blockchain = blockchain_instance or shared_blockchain_instance()

        # Create RankedPosts with proper parameters
        ranked_posts = RankedPosts(
            sort=path,
            tag=tag,
            observer=observer,
            limit=limit,
            lazy=lazy,
            full=full,
            blockchain_instance=self.blockchain,
        )

        super(RecentByPath, self).__init__(ranked_posts)


class RankedPosts(list):
    """Obtain a list of ranked posts

    :param str sort: can be: trending, hot, created, promoted, payout, payout_comments, muted
    :param str tag: tag, when used my, the community posts of the observer are shown
    :param str observer: Observer name
    :param int limit: limits the number of returns comments
    :param str start_author: start author
    :param str start_permlink: start permlink
    :param Blockchain blockchain_instance: Blockchain instance to use when accessing the RPC
    """

    def __init__(
        self,
        sort,
        tag="",
        observer="",
        limit=21,
        start_author="",
        start_permlink="",
        lazy=False,
        full=True,
        raw_data=False,
        blockchain_instance=None,
    ):
        """
        Initialize a RankedPosts list by fetching paginated ranked posts from the blockchain.

        Fetches up to `limit` posts for the given `sort` and `tag` using the bridge `get_ranked_posts`
        RPC, paging with `start_author` / `start_permlink`. Results are appended to the list as raw
        post dicts when `raw_data` is True, or as Comment objects otherwise. The constructor:
        - uses `blockchain_instance` (or the shared instance) and returns early (None) if not connected;
        - pages through results with an API page size up to 100, updating `start_author`/`start_permlink`;
        - avoids repeating the last item returned by the API; and
        - on an RPC error, returns partial results if any posts were already collected, otherwise re-raises.

        Parameters:
            sort (str): Ranking to query (e.g., "trending", "hot", "created").
            tag (str): Optional tag/category to filter by.
            observer (str): Optional observer account used by the bridge API (affects personalized results).
            limit (int): Maximum number of posts to return.
            start_author (str): Author to start paging from (inclusive/exclusive depends on the API).
            start_permlink (str): Permlink to start paging from.
            lazy (bool): If False, wrap results in Comment objects fully; if True, create Comment objects in lazy mode.
            full (bool): If True, request full Comment initialization when wrapping results.
            raw_data (bool): If True, return raw post dictionaries instead of Comment objects.
        """
        self.blockchain = blockchain_instance or shared_blockchain_instance()
        if not self.blockchain.is_connected():
            return None
        comments = []
        # Bridge API enforces a maximum page size (typically 20). Cap
        # per-request size accordingly and page until `limit` is reached.
        # Previously capped to 100 which can trigger Invalid parameters.
        api_limit = min(limit, 20)
        last_n = -1
        while len(comments) < limit and last_n != len(comments):
            last_n = len(comments)
            self.blockchain.rpc.set_next_node_on_empty_reply(False)
            try:
                posts = self.blockchain.rpc.get_ranked_posts(
                    {
                        "sort": sort,
                        "tag": tag,
                        "observer": observer,
                        "limit": api_limit,
                        "start_author": start_author,
                        "start_permlink": start_permlink,
                    },
                    api="bridge",
                )
                if posts is None:
                    continue
                for post in posts:
                    if (
                        len(comments) > 0
                        and comments[-1]["author"] == post["author"]
                        and comments[-1]["permlink"] == post["permlink"]
                    ):
                        continue
                    if len(comments) >= limit:
                        continue
                    if raw_data:
                        comments.append(post)
                    else:
                        comments.append(
                            Comment(post, lazy=lazy, full=full, blockchain_instance=self.blockchain)
                        )
                if len(comments) > 0:
                    start_author = comments[-1]["author"]
                    start_permlink = comments[-1]["permlink"]
                # Recompute per-request limit, capped to bridge max (20)
                remaining = limit - len(comments)
                api_limit = min(20, remaining + 1) if remaining < 20 else 20
            except Exception as e:
                # If we get an error but have some posts, return what we have
                if len(comments) > 0:
                    logging.warning(f"Error in RankedPosts: {str(e)}. Returning partial results.")
                    break
                # Otherwise, re-raise the exception
                raise
        super(RankedPosts, self).__init__(comments)


class AccountPosts(list):
    """Obtain a list of account related posts

    :param str sort: can be: comments, posts, blog, replies, feed
    :param str account: Account name
    :param str observer: Observer name
    :param int limit: limits the number of returns comments
    :param str start_author: start author
    :param str start_permlink: start permlink
    :param Blockchain blockchain_instance: Blockchain instance to use when accessing the RPC
    """

    def __init__(
        self,
        sort,
        account,
        observer="",
        limit=20,
        start_author="",
        start_permlink="",
        lazy=False,
        full=True,
        raw_data=False,
        blockchain_instance=None,
    ):
        """
        Initialize an AccountPosts list by fetching posts for a given account (paginated).

        This constructor populates the list with posts returned by the bridge.get_account_posts RPC call,
        respecting paging (start_author/start_permlink) and the requested limit. Each item is either the
        raw post dict (when raw_data=True) or a Comment object constructed with the same blockchain instance.

        Parameters:
            sort (str): The post list type to fetch (e.g., "blog", "comments", "replies", "feed").
            account (str): Account name whose posts are requested.
            observer (str): Optional observer account name used by the API (affects visibility/context).
            limit (int): Maximum number of posts to collect.
            start_author (str): Author to start paging from (inclusive/exclusive depends on API).
            start_permlink (str): Permlink to start paging from.
            lazy (bool): If False, Comment objects are fully loaded; if True, they are initialized lazily.
            full (bool): If True, Comment objects include full data; otherwise minimal fields.
            raw_data (bool): If True, return raw post dicts instead of Comment objects.

        Behavior notes:
            - If the blockchain instance is not connected, initialization returns early (no posts are fetched).
            - On an RPC error, if some posts have already been collected, the constructor returns those partial results;
              if no posts were collected, the exception is propagated.
        """
        self.blockchain = blockchain_instance or shared_blockchain_instance()
        if not self.blockchain.is_connected():
            return None
        comments = []
        # Bridge API typically restricts page size to 20; cap per-request size
        # and page as needed until overall `limit` is satisfied.
        api_limit = min(limit, 20)
        last_n = -1
        while len(comments) < limit and last_n != len(comments):
            last_n = len(comments)
            self.blockchain.rpc.set_next_node_on_empty_reply(False)
            try:
                posts = self.blockchain.rpc.get_account_posts(
                    {
                        "sort": sort,
                        "account": account,
                        "observer": observer,
                        "limit": api_limit,
                        "start_author": start_author,
                        "start_permlink": start_permlink,
                    },
                    api="bridge",
                )
                if posts is None:
                    continue
                for post in posts:
                    if (
                        len(comments) > 0
                        and comments[-1]["author"] == post["author"]
                        and comments[-1]["permlink"] == post["permlink"]
                    ):
                        continue
                    if len(comments) >= limit:
                        continue
                    if raw_data:
                        comments.append(post)
                    else:
                        comments.append(
                            Comment(post, lazy=lazy, full=full, blockchain_instance=self.blockchain)
                        )
                if len(comments) > 0:
                    start_author = comments[-1]["author"]
                    start_permlink = comments[-1]["permlink"]
                # Recompute per-request limit for next page, still capped at 20
                remaining = limit - len(comments)
                api_limit = min(20, remaining + 1) if remaining < 20 else 20
            except Exception as e:
                # If we get an error but have some posts, return what we have
                if len(comments) > 0:
                    logging.warning(f"Error in AccountPosts: {str(e)}. Returning partial results.")
                    break
                # Otherwise, re-raise the exception
                raise
        super(AccountPosts, self).__init__(comments)
