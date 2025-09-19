# -*- coding: utf-8 -*-
import json
import warnings
from datetime import date, datetime, timezone

from prettytable import PrettyTable

from nectarapi.exceptions import InvalidParameters, UnknownKey

from .account import Account
from .blockchainobject import BlockchainObject
from .comment import Comment
from .exceptions import VoteDoesNotExistsException
from .instance import shared_blockchain_instance
from .utils import (
    addTzInfo,
    construct_authorperm,
    construct_authorpermvoter,
    formatTimeString,
    reputation_to_score,
    resolve_authorperm,
    resolve_authorpermvoter,
)


class Vote(BlockchainObject):
    """Read data about a Vote in the chain

    :param str authorperm: perm link to post/comment
    :param nectar.nectar.nectar blockchain_instance: nectar
        instance to use when accesing a RPC
    :param steem_instance: (deprecated) use blockchain_instance instead
    :param hive_instance: (deprecated) use blockchain_instance instead
    """

    def __init__(
        self, voter, authorperm=None, lazy=False, full=False, blockchain_instance=None, **kwargs
    ):
        # Handle legacy parameters
        """
        Initialize a Vote object representing a single vote on a post or comment.

        Supports multiple input shapes for `voter`:
        - voter as str with `authorperm` provided: `voter` is the voter name; `authorperm` is parsed into author/permlink.
        - voter as dict containing "author", "permlink", and "voter": uses those fields directly.
        - voter as dict with "authorperm" plus an external `authorperm` argument: resolves author/permlink and fills missing fields.
        - voter as dict with "voter" plus an external `authorperm` argument: resolves author/permlink and fills missing fields.
        - otherwise treats `voter` as an authorpermvoter token (author+permlink+voter), resolving author, permlink, and voter from it.

        Behavior:
        - Normalizes numeric/time fields via internal parsing before initializing the underlying BlockchainObject.
        - Chooses the blockchain instance in this order: explicit `blockchain_instance`, a deprecated legacy instance passed via `steem_instance` or `hive_instance` (emits DeprecationWarning), then a shared default instance.
        - Validates keyword arguments and raises on unknown or conflicting legacy instance keys.

        Raises:
        - ValueError: if more than one legacy instance key is supplied.
        - TypeError: if unexpected keyword arguments are present.
        """
        legacy_keys = {"steem_instance", "hive_instance"}
        legacy_instance = None
        for key in legacy_keys:
            if key in kwargs:
                if legacy_instance is not None:
                    raise ValueError(
                        f"Cannot specify both {key} and another legacy instance parameter"
                    )
                legacy_instance = kwargs.pop(key)
                warnings.warn(
                    f"Parameter '{key}' is deprecated. Use 'blockchain_instance' instead.",
                    DeprecationWarning,
                    stacklevel=2,
                )

        # Check for unknown kwargs
        if kwargs:
            raise TypeError(f"Unexpected keyword arguments: {list(kwargs.keys())}")

        # Prefer explicit blockchain_instance, then legacy
        if blockchain_instance is None and legacy_instance is not None:
            blockchain_instance = legacy_instance

        self.full = full
        self.lazy = lazy
        self.blockchain = blockchain_instance or shared_blockchain_instance()
        if isinstance(voter, str) and authorperm is not None:
            [author, permlink] = resolve_authorperm(authorperm)
            self["voter"] = voter
            self["author"] = author
            self["permlink"] = permlink
            authorpermvoter = construct_authorpermvoter(author, permlink, voter)
            self["authorpermvoter"] = authorpermvoter
        elif (
            isinstance(voter, dict)
            and "author" in voter
            and "permlink" in voter
            and "voter" in voter
        ):
            authorpermvoter = voter
            authorpermvoter["authorpermvoter"] = construct_authorpermvoter(
                voter["author"], voter["permlink"], voter["voter"]
            )
            authorpermvoter = self._parse_json_data(authorpermvoter)
        elif isinstance(voter, dict) and "authorperm" in voter and authorperm is not None:
            [author, permlink] = resolve_authorperm(voter["authorperm"])
            authorpermvoter = voter
            authorpermvoter["voter"] = authorperm
            authorpermvoter["author"] = author
            authorpermvoter["permlink"] = permlink
            authorpermvoter["authorpermvoter"] = construct_authorpermvoter(
                author, permlink, authorperm
            )
            authorpermvoter = self._parse_json_data(authorpermvoter)
        elif isinstance(voter, dict) and "voter" in voter and authorperm is not None:
            [author, permlink] = resolve_authorperm(authorperm)
            authorpermvoter = voter
            authorpermvoter["author"] = author
            authorpermvoter["permlink"] = permlink
            authorpermvoter["authorpermvoter"] = construct_authorpermvoter(
                author, permlink, voter["voter"]
            )
            authorpermvoter = self._parse_json_data(authorpermvoter)
        else:
            authorpermvoter = voter
            [author, permlink, voter] = resolve_authorpermvoter(authorpermvoter)
            self["author"] = author
            self["permlink"] = permlink

        super(Vote, self).__init__(
            authorpermvoter,
            id_item="authorpermvoter",
            lazy=lazy,
            full=full,
            blockchain_instance=self.blockchain,
        )

    def refresh(self):
        """
        Refresh the Vote object from the blockchain RPC, replacing its internal data with the latest on-chain vote.

        If the object has no identifier or the blockchain is not connected, this method returns immediately. It resolves author, permlink, and voter from the stored identifier and queries the node for active votes (preferring appbase paths with a condenser fallback). If the matching vote is found, the object is reinitialized with the normalized vote data; otherwise VoteDoesNotExistsException is raised.

        Raises:
            VoteDoesNotExistsException: if the vote cannot be found or the RPC indicates the vote does not exist.
        """
        if self.identifier is None:
            return
        if not self.blockchain.is_connected():
            return
        [author, permlink, voter] = resolve_authorpermvoter(self.identifier)
        try:
            self.blockchain.rpc.set_next_node_on_empty_reply(True)
            if self.blockchain.rpc.get_use_appbase():
                try:
                    votes = self.blockchain.rpc.get_active_votes(
                        {"author": author, "permlink": permlink}, api="condenser"
                    )["votes"]
                except InvalidParameters:
                    raise VoteDoesNotExistsException(self.identifier)
                except Exception:  # Fallback to condenser API
                    votes = self.blockchain.rpc.get_active_votes(author, permlink, api="condenser")
            else:
                votes = self.blockchain.rpc.get_active_votes(author, permlink, api="condenser")
        except UnknownKey:
            raise VoteDoesNotExistsException(self.identifier)

        vote = None
        if votes is not None:
            for x in votes:
                if x["voter"] == voter:
                    vote = x
        if not vote:
            raise VoteDoesNotExistsException(self.identifier)
        vote = self._parse_json_data(vote)
        vote["authorpermvoter"] = construct_authorpermvoter(author, permlink, voter)
        super(Vote, self).__init__(
            vote,
            id_item="authorpermvoter",
            lazy=self.lazy,
            full=self.full,
            blockchain_instance=self.blockchain,
        )

    def _parse_json_data(self, vote):
        parse_int = [
            "rshares",
            "reputation",
        ]
        for p in parse_int:
            if p in vote and isinstance(vote.get(p), str):
                vote[p] = int(vote.get(p, "0"))

        if "time" in vote and isinstance(vote.get("time"), str) and vote.get("time") != "":
            vote["time"] = formatTimeString(vote.get("time", "1970-01-01T00:00:00"))
        elif (
            "timestamp" in vote
            and isinstance(vote.get("timestamp"), str)
            and vote.get("timestamp") != ""
        ):
            vote["time"] = formatTimeString(vote.get("timestamp", "1970-01-01T00:00:00"))
        elif (
            "last_update" in vote
            and isinstance(vote.get("last_update"), str)
            and vote.get("last_update") != ""
        ):
            vote["last_update"] = formatTimeString(vote.get("last_update", "1970-01-01T00:00:00"))
        else:
            vote["time"] = formatTimeString("1970-01-01T00:00:00")
        return vote

    def json(self):
        output = self.copy()
        if "author" in output:
            output.pop("author")
        if "permlink" in output:
            output.pop("permlink")
        parse_times = ["time"]
        for p in parse_times:
            if p in output:
                p_date = output.get(p, datetime(1970, 1, 1, 0, 0))
                if isinstance(p_date, (datetime, date)):
                    output[p] = formatTimeString(p_date)
                else:
                    output[p] = p_date
        parse_int = [
            "rshares",
            "reputation",
        ]
        for p in parse_int:
            if p in output and isinstance(output[p], int):
                output[p] = str(output[p])
        return json.loads(str(json.dumps(output)))

    @property
    def voter(self):
        return self["voter"]

    @property
    def authorperm(self):
        if "authorperm" in self:
            return self["authorperm"]
        elif "authorpermvoter" in self:
            [author, permlink, voter] = resolve_authorpermvoter(self["authorpermvoter"])
            return construct_authorperm(author, permlink)
        elif "author" in self and "permlink" in self:
            return construct_authorperm(self["author"], self["permlink"])
        else:
            return ""

    @property
    def votee(self):
        votee = ""
        authorperm = self.get("authorperm", "")
        authorpermvoter = self.get("authorpermvoter", "")
        if authorperm != "":
            votee = resolve_authorperm(authorperm)[0]
        elif authorpermvoter != "":
            votee = resolve_authorpermvoter(authorpermvoter)[0]
        return votee

    @property
    def weight(self):
        """
        Return the raw vote weight stored for this vote.

        The value is read directly from the underlying vote data (self["weight"]) and
        represents the weight field provided by the blockchain (type may be int).
        """
        return self["weight"]

    @property
    def hbd(self):
        """
        Return the HBD value equivalent of this vote's rshares.

        Uses the bound blockchain instance's rshares_to_hbd to convert the vote's integer `rshares` (defaults to 0).

        Returns:
            float: HBD amount corresponding to the vote's rshares.
        """
        return self.blockchain.rshares_to_hbd(int(self.get("rshares", 0)))

    @property
    def token_backed_dollar(self):
        # Hive-only: always convert to HBD
        """
        Convert this vote's rshares to HBD (Hive-backed dollar).

        Uses the associated blockchain instance's rshares_to_hbd conversion on the vote's "rshares" field (defaults to 0 if missing). This is Hive-specific and always returns HBD-equivalent value for the vote.
        """
        return self.blockchain.rshares_to_hbd(int(self.get("rshares", 0)))

    @property
    def rshares(self):
        """
        Return the vote's raw `rshares` as an integer.

        Converts the stored `rshares` value (which may be a string or number) to an int and returns it.
        If `rshares` is missing, returns 0.
        """
        return int(self.get("rshares", 0))

    @property
    def percent(self):
        return self.get("percent", 0)

    @property
    def reputation(self):
        return self.get("reputation", 0)

    @property
    def rep(self):
        return reputation_to_score(int(self.reputation))

    @property
    def time(self):
        return self["time"]


class VotesObject(list):
    def get_sorted_list(self, sort_key="time", reverse=True):
        sortedList = sorted(
            self,
            key=lambda x: (datetime.now(timezone.utc) - x.time).total_seconds(),
            reverse=reverse,
        )
        return sortedList

    def printAsTable(
        self,
        voter=None,
        votee=None,
        start=None,
        stop=None,
        start_percent=None,
        stop_percent=None,
        sort_key="time",
        reverse=True,
        allow_refresh=True,
        return_str=False,
        **kwargs,
    ):
        """
        Render the votes collection as a formatted table, with optional filtering and sorting.

        Detailed behavior:
        - Filters votes by voter name, votee (author), time window (start/stop), and percent range (start_percent/stop_percent).
        - Sorts votes using sort_key (default "time") and reverse order flag.
        - Formats columns: Voter, Votee, HBD (token equivalent), Time (human-readable delta), Rshares, Percent, Weight.
        - If return_str is True, returns the table string; otherwise prints it to stdout.

        Parameters:
            voter (str, optional): Only include votes by this voter name.
            votee (str, optional): Only include votes targeting this votee (author).
            start (datetime or str, optional): Inclusive lower bound for vote time; timezone info is added if missing.
            stop (datetime or str, optional): Inclusive upper bound for vote time; timezone info is added if missing.
            start_percent (int, optional): Inclusive lower bound for vote percent.
            stop_percent (int, optional): Inclusive upper bound for vote percent.
            sort_key (str, optional): Attribute name used to sort votes (default "time").
            reverse (bool, optional): If True, sort in descending order (default True).
            allow_refresh (bool, optional): If False, prevents refreshing votes during iteration by marking them as cached.
            return_str (bool, optional): If True, return the rendered table as a string; otherwise print it.
            **kwargs: Passed through to PrettyTable.get_string when rendering the table.

        Returns:
            str or None: The table string when return_str is True; otherwise None (table is printed).
        """
        table_header = ["Voter", "Votee", "HBD", "Time", "Rshares", "Percent", "Weight"]
        t = PrettyTable(table_header)
        t.align = "l"
        start = addTzInfo(start)
        stop = addTzInfo(stop)
        for vote in self.get_sorted_list(sort_key=sort_key, reverse=reverse):
            if not allow_refresh:
                vote.cached = True

            d_time = vote.time
            if d_time != formatTimeString("1970-01-01T00:00:00"):
                td = datetime.now(timezone.utc) - d_time
                timestr = (
                    str(td.days)
                    + " days "
                    + str(td.seconds // 3600)
                    + ":"
                    + str((td.seconds // 60) % 60)
                )
            else:
                start = None
                stop = None
                timestr = ""

            percent = vote.get("percent", "")
            if percent == "":
                start_percent = None
                stop_percent = None
            if (
                (start is None or d_time >= start)
                and (stop is None or d_time <= stop)
                and (start_percent is None or percent >= start_percent)
                and (stop_percent is None or percent <= stop_percent)
                and (voter is None or vote["voter"] == voter)
                and (votee is None or vote.votee == votee)
            ):
                percent = vote.get("percent", "")
                if percent == "":
                    percent = vote.get("vote_percent", "")
                t.add_row(
                    [
                        vote["voter"],
                        vote.votee,
                        str(round(vote.token_backed_dollar, 2)).ljust(5) + "$",
                        timestr,
                        vote.get("rshares", ""),
                        str(percent),
                        str(vote["weight"]),
                    ]
                )

        if return_str:
            return t.get_string(**kwargs)
        else:
            print(t.get_string(**kwargs))

    def get_list(
        self,
        var="voter",
        voter=None,
        votee=None,
        start=None,
        stop=None,
        start_percent=None,
        stop_percent=None,
        sort_key="time",
        reverse=True,
    ):
        vote_list = []
        start = addTzInfo(start)
        stop = addTzInfo(stop)
        for vote in self.get_sorted_list(sort_key=sort_key, reverse=reverse):
            d_time = vote.time
            if d_time != formatTimeString("1970-01-01T00:00:00"):
                start = None
                stop = None
            percent = vote.get("percent", "")
            if percent == "":
                percent = vote.get("vote_percent", "")
            if percent == "":
                start_percent = None
                stop_percent = None
            if (
                (start is None or d_time >= start)
                and (stop is None or d_time <= stop)
                and (start_percent is None or percent >= start_percent)
                and (stop_percent is None or percent <= stop_percent)
                and (voter is None or vote["voter"] == voter)
                and (votee is None or vote.votee == votee)
            ):
                v = ""
                if var == "voter":
                    v = vote["voter"]
                elif var == "votee":
                    v = vote.votee
                elif var == "sbd" or var == "hbd":
                    v = vote.token_backed_dollar
                elif var == "time":
                    v = d_time
                elif var == "rshares":
                    v = vote.get("rshares", 0)
                elif var == "percent":
                    v = percent
                elif var == "weight":
                    v = vote["weight"]
                vote_list.append(v)
        return vote_list

    def print_stats(self, return_str=False, **kwargs):
        # Using built-in timezone support
        """
        Print or return a summary table of vote statistics for this collection.

        If return_str is True, the formatted table is returned as a string; otherwise it is printed.
        Accepts the same filtering and formatting keyword arguments used by printAsTable (e.g., voter, votee, start, stop, start_percent, stop_percent, sort_key, reverse).
        """
        table_header = ["voter", "votee", "hbd", "time", "rshares", "percent", "weight"]
        t = PrettyTable(table_header)
        t.align = "l"

    def __contains__(self, item):
        if isinstance(item, Account):
            name = item["name"]
            authorperm = ""
        elif isinstance(item, Comment):
            authorperm = item.authorperm
            name = ""
        else:
            name = item
            authorperm = item

        return (
            any([name == x.voter for x in self])
            or any([name == x.votee for x in self])
            or any([authorperm == x.authorperm for x in self])
        )

    def __str__(self):
        return self.printAsTable(return_str=True)

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, str(self.identifier))


class ActiveVotes(VotesObject):
    """Obtain a list of votes for a post

    :param str authorperm: authorperm link
    :param Blockchain blockchain_instance: Blockchain instance to use when accessing RPC
    """

    def __init__(self, authorperm, lazy=False, full=False, blockchain_instance=None, **kwargs):
        # Handle legacy parameters
        """
        Initialize an ActiveVotes collection for a post's active votes.

        Creates Vote objects for each active vote on the given post (author/permlink) and stores them in the list.
        Accepts multiple input shapes for authorperm:
        - Comment: extracts author/permlink and uses its `active_votes` via RPC.
        - str: an authorperm string, resolved to author and permlink.
        - list: treated as a pre-fetched list of vote dicts.
        - dict: expects keys "active_votes" and "authorperm".

        Handles legacy keyword parameters "steem_instance" and "hive_instance" (deprecated; a DeprecationWarning is emitted). If no explicit blockchain instance is provided, a shared instance is used. If the blockchain is not connected or no votes are found, initialization returns without populating the collection.

        Raises:
            ValueError: if multiple legacy instance parameters are provided.
            VoteDoesNotExistsException: when the RPC reports invalid parameters for the requested post (no such post).
        """
        legacy_keys = {"steem_instance", "hive_instance"}
        legacy_instance = None
        for key in legacy_keys:
            if key in kwargs:
                if legacy_instance is not None:
                    raise ValueError(
                        f"Cannot specify both {key} and another legacy instance parameter"
                    )
                legacy_instance = kwargs.pop(key)
                warnings.warn(
                    f"Parameter '{key}' is deprecated. Use 'blockchain_instance' instead.",
                    DeprecationWarning,
                    stacklevel=2,
                )

        # Prefer explicit blockchain_instance, then legacy
        if blockchain_instance is None and legacy_instance is not None:
            blockchain_instance = legacy_instance

        self.blockchain = blockchain_instance or shared_blockchain_instance()
        votes = None
        if not self.blockchain.is_connected():
            return None
        self.blockchain.rpc.set_next_node_on_empty_reply(False)

        if isinstance(authorperm, Comment):
            # if 'active_votes' in authorperm and len(authorperm["active_votes"]) > 0:
            #    votes = authorperm["active_votes"]
            if self.blockchain.rpc.get_use_appbase():
                self.blockchain.rpc.set_next_node_on_empty_reply(False)
                from nectarapi.exceptions import InvalidParameters

                try:
                    votes = self.blockchain.rpc.get_active_votes(
                        authorperm["author"], authorperm["permlink"], api="condenser"
                    )
                except InvalidParameters:
                    raise VoteDoesNotExistsException(
                        construct_authorperm(authorperm["author"], authorperm["permlink"])
                    )
                except Exception:  # Fallback to tags API
                    votes = self.blockchain.rpc.get_active_votes(
                        {"author": authorperm["author"], "permlink": authorperm["permlink"]},
                        api="tags",
                    )["votes"]
            else:
                votes = self.blockchain.rpc.get_active_votes(
                    authorperm["author"], authorperm["permlink"], api="condenser"
                )
            authorperm = authorperm["authorperm"]
        elif isinstance(authorperm, str):
            [author, permlink] = resolve_authorperm(authorperm)
            if self.blockchain.rpc.get_use_appbase():
                self.blockchain.rpc.set_next_node_on_empty_reply(False)
                from nectarapi.exceptions import InvalidParameters

                try:
                    votes = self.blockchain.rpc.get_active_votes(author, permlink, api="condenser")
                except InvalidParameters:
                    raise VoteDoesNotExistsException(construct_authorperm(author, permlink))
                except Exception:  # Fallback to tags API
                    votes = self.blockchain.rpc.get_active_votes(
                        {"author": author, "permlink": permlink}, api="tags"
                    )["votes"]
            else:
                votes = self.blockchain.rpc.get_active_votes(author, permlink, api="condenser")
        elif isinstance(authorperm, list):
            votes = authorperm
            authorperm = None
        elif isinstance(authorperm, dict):
            votes = authorperm["active_votes"]
            authorperm = authorperm["authorperm"]
        if votes is None:
            return
        self.identifier = authorperm
        super(ActiveVotes, self).__init__(
            [
                Vote(
                    x,
                    authorperm=authorperm,
                    lazy=lazy,
                    full=full,
                    blockchain_instance=self.blockchain,
                )
                for x in votes
            ]
        )


class AccountVotes(VotesObject):
    """Obtain a list of votes for an account
    Lists the last 100+ votes on the given account.

    :param str account: Account name
    :param Blockchain blockchain_instance: Blockchain instance to use when accessing RPC
    """

    def __init__(
        self,
        account,
        start=None,
        stop=None,
        raw_data=False,
        lazy=False,
        full=False,
        blockchain_instance=None,
    ):
        """
        Initialize AccountVotes by loading votes for a given account within an optional time window.

        Creates a collection of votes retrieved from the account's historical votes. Each entry is either a Vote object (default) or the raw vote dict when `raw_data` is True. Time filtering is applied using `start` and `stop` (inclusive). Empty or missing timestamps are treated as the Unix epoch.

        Parameters:
            account: Account or str
                Account name or Account object whose votes to load.
            start: datetime | str | None
                Inclusive lower bound for vote time. Accepts a timezone-aware datetime or a time string; None disables the lower bound.
            stop: datetime | str | None
                Inclusive upper bound for vote time. Accepts a timezone-aware datetime or a time string; None disables the upper bound.
            raw_data: bool
                If True, return raw vote dictionaries instead of Vote objects.
            lazy: bool
                Passed to Vote when constructing Vote objects; controls lazy loading behavior.
            full: bool
                Passed to Vote when constructing Vote objects; controls whether to fully populate vote data.
        """
        self.blockchain = blockchain_instance or shared_blockchain_instance()
        start = addTzInfo(start)
        stop = addTzInfo(stop)
        account = Account(account, blockchain_instance=self.blockchain)
        votes = account.get_account_votes()
        self.identifier = account["name"]
        vote_list = []
        if votes is None:
            votes = []
        for x in votes:
            time = x.get("time", "")
            if time == "":
                time = x.get("last_update", "")
                if time != "":
                    x["time"] = time
            if time != "" and isinstance(time, str):
                d_time = formatTimeString(time)
            elif isinstance(time, datetime):
                d_time = time
            else:
                d_time = addTzInfo(datetime(1970, 1, 1, 0, 0, 0))
            if (start is None or d_time >= start) and (stop is None or d_time <= stop):
                if not raw_data:
                    vote_list.append(
                        Vote(
                            x,
                            authorperm=account["name"],
                            lazy=lazy,
                            full=full,
                            blockchain_instance=self.blockchain,
                        )
                    )
                else:
                    vote_list.append(x)

        super(AccountVotes, self).__init__(vote_list)
