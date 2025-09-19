# -*- coding: utf-8 -*-
#!/usr/bin/python
import unittest
from datetime import datetime, timedelta, timezone

from nectar import Hive, exceptions
from nectar.account import Account
from nectar.comment import Comment
from nectar.instance import set_shared_blockchain_instance
from nectar.utils import (
    construct_authorperm,
    construct_authorpermvoter,
    resolve_authorpermvoter,
)
from nectar.vote import AccountVotes, ActiveVotes, Vote

from .nodes import get_hive_nodes

wif = "5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3"


class Testcases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bts = Hive(
            node=get_hive_nodes(), nobroadcast=True, keys={"active": wif}, num_retries=10
        )
        # from getpass import getpass
        # self.bts.wallet.unlock(getpass())
        set_shared_blockchain_instance(cls.bts)
        cls.bts.set_default_account("test")

        acc = Account("fullnodeupdate", blockchain_instance=cls.bts)
        n_votes = 0
        index = 0
        entries = acc.get_blog(limit=20)[::-1]
        while n_votes == 0:
            comment = Comment(entries[index], blockchain_instance=cls.bts)
            votes = comment.get_votes()
            n_votes = len(votes)
            index += 1

        last_vote = votes[0]

        cls.authorpermvoter = construct_authorpermvoter(
            last_vote["author"], last_vote["permlink"], last_vote["voter"]
        )
        [author, permlink, voter] = resolve_authorpermvoter(cls.authorpermvoter)
        cls.author = author
        cls.permlink = permlink
        cls.voter = voter
        cls.authorperm = construct_authorperm(author, permlink)

    def test_vote(self):
        bts = self.bts
        self.assertTrue(len(bts.get_reward_funds(use_stored_data=False)) > 0)
        vote = Vote(self.authorpermvoter, blockchain_instance=bts)
        self.assertEqual(self.voter, vote["voter"])
        self.assertEqual(self.author, vote["author"])
        self.assertEqual(self.permlink, vote["permlink"])

        vote = Vote(self.voter, authorperm=self.authorperm, blockchain_instance=bts)
        self.assertEqual(self.voter, vote["voter"])
        self.assertEqual(self.author, vote["author"])
        self.assertEqual(self.permlink, vote["permlink"])
        vote_json = vote.json()
        self.assertEqual(self.voter, vote_json["voter"])
        self.assertEqual(self.voter, vote.voter)
        self.assertTrue(vote.weight >= 0)
        if vote.percent >= 0:
            self.assertTrue(vote.hbd >= 0)
            self.assertTrue(vote.rshares >= 0)
        else:
            self.assertTrue(vote.hbd < 0)
            self.assertTrue(vote.rshares < 0)

        self.assertTrue(vote.reputation is not None)
        self.assertTrue(vote.rep is not None)
        self.assertTrue(vote.time is not None)
        vote.refresh()
        self.assertEqual(self.voter, vote["voter"])
        self.assertEqual(self.author, vote["author"])
        self.assertEqual(self.permlink, vote["permlink"])
        vote_json = vote.json()
        self.assertEqual(self.voter, vote_json["voter"])
        self.assertEqual(self.voter, vote.voter)
        self.assertTrue(vote.weight >= 0)
        if vote.percent >= 0:
            self.assertTrue(vote.hbd >= 0)
            self.assertTrue(vote.rshares >= 0)
        else:
            self.assertTrue(vote.hbd < 0)
            self.assertTrue(vote.rshares < 0)
        self.assertTrue(vote.reputation is not None)
        self.assertTrue(vote.rep is not None)
        self.assertTrue(vote.time is not None)

    def test_keyerror(self):
        bts = self.bts
        with self.assertRaises(exceptions.VoteDoesNotExistsException):
            Vote(
                construct_authorpermvoter(self.author, self.permlink, "asdfsldfjlasd"),
                blockchain_instance=bts,
            )

        with self.assertRaises(exceptions.VoteDoesNotExistsException):
            Vote(
                construct_authorpermvoter(self.author, "sdlfjd", "asdfsldfjlasd"),
                blockchain_instance=bts,
            )

        with self.assertRaises(exceptions.VoteDoesNotExistsException):
            Vote(
                construct_authorpermvoter("sdalfj", "dsfa", "asdfsldfjlasd"),
                blockchain_instance=bts,
            )

    def test_activevotes(self):
        bts = self.bts
        votes = ActiveVotes(self.authorperm, blockchain_instance=bts)
        votes.printAsTable()
        vote_list = votes.get_list()
        self.assertTrue(isinstance(vote_list, list))

    @unittest.skip
    def test_accountvotes(self):
        bts = self.bts
        limit_time = datetime.now(timezone.utc) - timedelta(days=7)
        votes = AccountVotes(self.voter, start=limit_time, blockchain_instance=bts)
        self.assertTrue(len(votes) > 0)
        self.assertTrue(isinstance(votes[0], Vote))
