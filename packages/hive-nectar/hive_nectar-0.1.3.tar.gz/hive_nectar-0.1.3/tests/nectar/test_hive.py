# -*- coding: utf-8 -*-
import json
import random
import string

# Py3 compatibility
import sys
import unittest

from nectar import Hive, exceptions
from nectar.account import Account
from nectar.amount import Amount
from nectar.version import version as nectar_version
from nectargraphenebase.account import PrivateKey

from .nodes import get_hive_nodes

wif = "5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3"
wif2 = "5JKu2dFfjKAcD6aP1HqBDxMNbdwtvPS99CaxBzvMYhY94Pt6RDS"
wif3 = "5K1daXjehgPZgUHz6kvm55ahEArBHfCHLy6ew8sT7sjDb76PU2P"


class Testcases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Set up shared test fixtures for the test class.

        Creates a Hive blockchain client configured for offline/no-broadcast testing and a populated Account instance named "test" bound to that client. The Hive client is stored on the class as `bts` and the Account as `account`, making them available to all test methods.
        """
        cls.bts = Hive(
            node=get_hive_nodes(),
            nobroadcast=True,
            unsigned=True,
            data_refresh_time_seconds=900,
            keys={"active": wif, "owner": wif2, "memo": wif3},
            num_retries=10,
        )
        cls.account = Account("test", full=True, blockchain_instance=cls.bts)

    def test_transfer(self):
        bts = self.bts
        acc = self.account
        acc.blockchain.txbuffer.clear()
        tx = acc.transfer(
            "test", 1.33, acc.blockchain.backed_token_symbol, memo="Foobar", account="test1"
        )
        self.assertEqual(len(tx["operations"]), 1)
        if isinstance(tx["operations"][0], list):
            self.assertEqual(tx["operations"][0][0], "transfer")
            op = tx["operations"][0][1]
        else:
            self.assertEqual(tx["operations"][0]["type"], "transfer_operation")

            op = tx["operations"][0]["value"]
        self.assertIn("memo", op)
        self.assertEqual(op["memo"], "Foobar")
        self.assertEqual(op["from"], "test1")
        self.assertEqual(op["to"], "test")
        amount = Amount(op["amount"], blockchain_instance=bts)
        self.assertEqual(float(amount), 1.33)

    def test_create_account(self):
        bts = Hive(
            node=get_hive_nodes(),
            nobroadcast=True,
            unsigned=True,
            data_refresh_time_seconds=900,
            keys={"active": wif, "owner": wif2, "memo": wif3},
            num_retries=10,
        )
        core_unit = "STM"
        name = "".join(random.choice(string.ascii_lowercase) for _ in range(12))
        key1 = PrivateKey()
        key2 = PrivateKey()
        key3 = PrivateKey()
        key4 = PrivateKey()
        key5 = PrivateKey()
        bts.txbuffer.clear()
        tx = bts.create_account(
            name,
            creator="test",  # 1.2.7
            owner_key=format(key1.pubkey, core_unit),
            active_key=format(key2.pubkey, core_unit),
            posting_key=format(key3.pubkey, core_unit),
            memo_key=format(key4.pubkey, core_unit),
            additional_owner_keys=[format(key5.pubkey, core_unit)],
            additional_active_keys=[format(key5.pubkey, core_unit)],
            additional_posting_keys=[format(key5.pubkey, core_unit)],
            additional_owner_accounts=["test1"],  # 1.2.0
            additional_active_accounts=["test2"],
            additional_posting_accounts=["test3"],
            storekeys=False,
        )
        if isinstance(tx["operations"][0], list):
            self.assertEqual(tx["operations"][0][0], "account_create")
            op = tx["operations"][0][1]
        else:
            self.assertEqual(tx["operations"][0]["type"], "account_create_operation")
            op = tx["operations"][0]["value"]
        role = "active"
        self.assertIn(format(key5.pubkey, core_unit), [x[0] for x in op[role]["key_auths"]])
        self.assertIn(format(key5.pubkey, core_unit), [x[0] for x in op[role]["key_auths"]])
        self.assertIn("test2", [x[0] for x in op[role]["account_auths"]])
        role = "posting"
        self.assertIn(format(key5.pubkey, core_unit), [x[0] for x in op[role]["key_auths"]])
        self.assertIn(format(key5.pubkey, core_unit), [x[0] for x in op[role]["key_auths"]])
        self.assertIn("test3", [x[0] for x in op[role]["account_auths"]])
        role = "owner"
        self.assertIn(format(key5.pubkey, core_unit), [x[0] for x in op[role]["key_auths"]])
        self.assertIn(format(key5.pubkey, core_unit), [x[0] for x in op[role]["key_auths"]])
        self.assertIn("test1", [x[0] for x in op[role]["account_auths"]])
        self.assertEqual(op["creator"], "test")

    def test_create_account_password(self):
        bts = Hive(
            node=get_hive_nodes(),
            nobroadcast=True,
            unsigned=True,
            data_refresh_time_seconds=900,
            keys={"active": wif, "owner": wif2, "memo": wif3},
            num_retries=10,
        )
        core_unit = "STM"
        name = "".join(random.choice(string.ascii_lowercase) for _ in range(12))
        key5 = PrivateKey()
        bts.txbuffer.clear()
        tx = bts.create_account(
            name,
            creator="test",  # 1.2.7
            password="abcdefg",
            additional_owner_keys=[format(key5.pubkey, core_unit)],
            additional_active_keys=[format(key5.pubkey, core_unit)],
            additional_posting_keys=[format(key5.pubkey, core_unit)],
            additional_owner_accounts=["test1"],  # 1.2.0
            additional_active_accounts=["test1"],
            storekeys=False,
        )
        if isinstance(tx["operations"][0], list):
            self.assertEqual(tx["operations"][0][0], "account_create")
            op = tx["operations"][0][1]
        else:
            self.assertEqual(tx["operations"][0]["type"], "account_create_operation")
            op = tx["operations"][0]["value"]
        role = "active"
        self.assertIn(format(key5.pubkey, core_unit), [x[0] for x in op[role]["key_auths"]])
        self.assertIn(format(key5.pubkey, core_unit), [x[0] for x in op[role]["key_auths"]])
        self.assertIn("test1", [x[0] for x in op[role]["account_auths"]])
        role = "owner"
        self.assertIn(format(key5.pubkey, core_unit), [x[0] for x in op[role]["key_auths"]])
        self.assertIn(format(key5.pubkey, core_unit), [x[0] for x in op[role]["key_auths"]])
        self.assertIn("test1", [x[0] for x in op[role]["account_auths"]])
        self.assertEqual(op["creator"], "test")

    def test_connect(self):
        bts = self.bts
        bts.connect()

    def test_info(self):
        bts = self.bts
        info = bts.info()
        for key in [
            "current_witness",
            "head_block_id",
            "head_block_number",
            "id",
            "last_irreversible_block_num",
            "current_witness",
            "total_pow",
            "time",
        ]:
            self.assertTrue(key in info)

    def test_finalizeOps(self):
        bts = self.bts
        acc = self.account
        tx1 = bts.new_tx()
        tx2 = bts.new_tx()

        acc.transfer("test1", 1, bts.token_symbol, append_to=tx1)
        acc.transfer("test1", 2, bts.token_symbol, append_to=tx2)
        acc.transfer("test1", 3, bts.token_symbol, append_to=tx1)
        tx1 = tx1.json()
        tx2 = tx2.json()
        ops1 = tx1["operations"]
        ops2 = tx2["operations"]
        self.assertEqual(len(ops1), 2)
        self.assertEqual(len(ops2), 1)

    def test_weight_threshold(self):
        bts = self.bts
        pkey1 = "STM55VCzsb47NZwWe5F3qyQKedX9iHBHMVVFSc96PDvV7wuj7W86n"
        pkey2 = "STM7GM9YXcsoAJAgKbqW2oVj7bnNXFNL4pk9NugqKWPmuhoEDbkDv"

        auth = {
            "account_auths": [["test", 1]],
            "extensions": [],
            "key_auths": [[pkey1, 1], [pkey2, 1]],
            "weight_threshold": 3,
        }  # threshold fine
        bts._test_weights_treshold(auth)
        auth = {
            "account_auths": [["test", 1]],
            "extensions": [],
            "key_auths": [[pkey1, 1], [pkey2, 1]],
            "weight_threshold": 4,
        }  # too high

        with self.assertRaises(ValueError):
            bts._test_weights_treshold(auth)

    def test_allow(self):
        bts = self.bts
        acc = self.account
        prefix = "STM"
        wif = "STM55VCzsb47NZwWe5F3qyQKedX9iHBHMVVFSc96PDvV7wuj7W86n"

        self.assertIn(bts.prefix, prefix)
        tx = acc.allow(
            wif,
            account="test",
            weight=1,
            threshold=1,
            permission="owner",
        )
        if isinstance(tx["operations"][0], list):
            self.assertEqual((tx["operations"][0][0]), "account_update")
            op = tx["operations"][0][1]
        else:
            self.assertEqual((tx["operations"][0]["type"]), "account_update_operation")
            op = tx["operations"][0]["value"]
        self.assertIn("owner", op)
        self.assertIn([wif, "1"], op["owner"]["key_auths"])
        self.assertEqual(op["owner"]["weight_threshold"], 1)

    def test_disallow(self):
        acc = self.account
        pkey1 = "STM55VCzsb47NZwWe5F3qyQKedX9iHBHMVVFSc96PDvV7wuj7W86n"
        pkey2 = "STM6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV"
        if sys.version > "3":
            _assertRaisesRegex = self.assertRaisesRegex
        else:
            _assertRaisesRegex = self.assertRaisesRegexp
        with _assertRaisesRegex(ValueError, ".*Changes nothing.*"):
            acc.disallow(pkey1, weight=1, threshold=1, permission="owner")
        with _assertRaisesRegex(ValueError, ".*Changes nothing!.*"):
            acc.disallow(pkey2, weight=1, threshold=1, permission="owner")

    def test_update_memo_key(self):
        acc = self.account
        prefix = "STM"
        pkey = "STM55VCzsb47NZwWe5F3qyQKedX9iHBHMVVFSc96PDvV7wuj7W86n"
        self.assertEqual(acc.blockchain.prefix, prefix)
        acc.blockchain.txbuffer.clear()
        tx = acc.update_memo_key(pkey)
        if isinstance(tx["operations"][0], list):
            self.assertEqual((tx["operations"][0][0]), "account_update")
            op = tx["operations"][0][1]
        else:
            self.assertEqual((tx["operations"][0]["type"]), "account_update_operation")
            op = tx["operations"][0]["value"]

        self.assertEqual(op["memo_key"], pkey)

    def test_approvewitness(self):
        w = self.account
        w.blockchain.txbuffer.clear()
        tx = w.approvewitness("test1")
        if isinstance(tx["operations"][0], list):
            self.assertEqual((tx["operations"][0][0]), "account_witness_vote")
            op = tx["operations"][0][1]
        else:
            self.assertEqual((tx["operations"][0]["type"]), "account_witness_vote_operation")
            op = tx["operations"][0]["value"]
        self.assertIn("test1", op["witness"])

    def test_post(self):
        bts = self.bts
        bts.txbuffer.clear()
        tx = bts.post(
            "title",
            "body",
            author="test",
            permlink=None,
            reply_identifier=None,
            json_metadata=None,
            comment_options=None,
            community="test",
            tags=["a", "b", "c", "d", "e"],
            beneficiaries=[
                {"account": "test1", "weight": 5000},
                {"account": "test2", "weight": 5000},
            ],
            self_vote=True,
        )
        if isinstance(tx["operations"][0], list):
            self.assertEqual((tx["operations"][0][0]), "comment")
            op = tx["operations"][0][1]
        else:
            self.assertEqual((tx["operations"][0]["type"]), "comment_operation")
            op = tx["operations"][0]["value"]
        self.assertEqual(op["body"], "body")
        self.assertEqual(op["title"], "title")
        self.assertTrue(op["permlink"].startswith("title"))
        self.assertEqual(op["parent_author"], "")
        self.assertEqual(op["parent_permlink"], "test")
        json_metadata = json.loads(op["json_metadata"])
        self.assertEqual(json_metadata["tags"], ["a", "b", "c", "d", "e"])
        self.assertEqual(json_metadata["app"], "nectar/%s" % (nectar_version))
        if isinstance(tx["operations"][1], list):
            self.assertEqual((tx["operations"][1][0]), "comment_options")
            op = tx["operations"][1][1]
        else:
            self.assertEqual((tx["operations"][1]["type"]), "comment_options_operation")
            op = tx["operations"][1]["value"]
        self.assertEqual(len(op["extensions"][0][1]["beneficiaries"]), 2)

    def test_comment_option(self):
        bts = self.bts
        bts.txbuffer.clear()
        tx = bts.comment_options({}, "@gtg/witness-gtg-log", account="test")
        if isinstance(tx["operations"][0], list):
            self.assertEqual((tx["operations"][0][0]), "comment_options")
            op = tx["operations"][0][1]
        else:
            self.assertEqual((tx["operations"][0]["type"]), "comment_options_operation")
            op = tx["operations"][0]["value"]

        self.assertIn("gtg", op["author"])
        self.assertEqual("1000000.000 HBD", op["max_accepted_payout"])
        self.assertEqual(10000, op["percent_hbd"])
        self.assertEqual(True, op["allow_votes"])
        self.assertEqual(True, op["allow_curation_rewards"])
        self.assertEqual("witness-gtg-log", op["permlink"])

    def test_online(self):
        bts = self.bts
        self.assertFalse(bts.get_blockchain_version() == "0.0.0")

    def test_offline(self):
        # In offline mode, avoid fetching/updating remote node lists
        bts = Hive(
            offline=True,
            data_refresh_time_seconds=900,
            keys={"active": wif, "owner": wif2, "memo": wif3},
        )
        bts.refresh_data("feed_history")
        self.assertTrue(bts.get_feed_history(use_stored_data=False) is None)
        self.assertTrue(bts.get_feed_history(use_stored_data=True) is None)
        bts.refresh_data("reward_funds")
        self.assertTrue(bts.get_reward_funds(use_stored_data=False) is None)
        self.assertTrue(bts.get_reward_funds(use_stored_data=True) is None)
        self.assertTrue(bts.get_current_median_history(use_stored_data=False) is None)
        self.assertTrue(bts.get_current_median_history(use_stored_data=True) is None)
        bts.refresh_data("hardfork_properties")
        self.assertTrue(bts.get_hardfork_properties(use_stored_data=False) is None)
        self.assertTrue(bts.get_hardfork_properties(use_stored_data=True) is None)
        bts.refresh_data("config")
        self.assertTrue(bts.get_network(use_stored_data=False) is not None)
        self.assertTrue(bts.get_network(use_stored_data=True) is not None)
        bts.refresh_data("witness_schedule")
        self.assertTrue(bts.get_witness_schedule(use_stored_data=False) is None)
        self.assertTrue(bts.get_witness_schedule(use_stored_data=True) is None)
        self.assertTrue(bts.get_config(use_stored_data=False) is None)
        self.assertTrue(bts.get_config(use_stored_data=True) is None)
        self.assertEqual(bts.get_block_interval(), 3)
        self.assertEqual(bts.get_blockchain_version(), "0.0.0")
        self.assertTrue(bts.is_hive)
        self.assertFalse(bts.is_steem)

    def test_properties(self):
        bts = Hive(
            node=get_hive_nodes(),
            nobroadcast=True,
            data_refresh_time_seconds=900,
            keys={"active": wif, "owner": wif2, "memo": wif3},
            num_retries=10,
        )
        self.assertTrue(bts.is_hive)
        self.assertTrue(bts.get_feed_history(use_stored_data=False) is not None)
        self.assertTrue(bts.get_reward_funds(use_stored_data=False) is not None)
        self.assertTrue(bts.get_current_median_history(use_stored_data=False) is not None)
        self.assertTrue(bts.get_hardfork_properties(use_stored_data=False) is not None)
        self.assertTrue(bts.get_network(use_stored_data=False) is not None)
        self.assertTrue(bts.get_witness_schedule(use_stored_data=False) is not None)
        self.assertTrue(bts.get_config(use_stored_data=False) is not None)
        self.assertTrue(bts.get_block_interval() is not None)
        self.assertTrue(bts.get_blockchain_version() is not None)
        self.assertTrue(bts.get_blockchain_name() == "hive")
        self.assertTrue(bts.is_hive)
        self.assertFalse(bts.is_steem)

    def test_hp_to_rshares(self):
        hv = self.bts
        rshares = hv.hp_to_rshares(hv.vests_to_hp(1e6), post_rshares=1e19)
        self.assertTrue(abs(rshares - 20000000000.0) < 2)

    def test_rshares_to_vests(self):
        hv = self.bts
        rshares = hv.hp_to_rshares(hv.vests_to_hp(1e6))
        rshares2 = hv.vests_to_rshares(1e6)
        self.assertTrue(abs(rshares - rshares2) < 2)

    def test_hp_to_hbd(self):
        hv = self.bts
        sp = 500
        ret = hv.hp_to_hbd(sp)
        self.assertTrue(ret is not None)

    def test_hbd_to_rshares(self):
        hv = self.bts
        test_values = [1, 10, 100, 1e3, 1e4, 1e5, 1e6, 1e7]
        for v in test_values:
            try:
                sbd = round(hv.rshares_to_hbd(hv.hbd_to_rshares(v)), 5)
            except (
                ValueError
            ):  # Reward pool smaller than 1e7 HBD (e.g. caused by a very low hive price)
                continue
            self.assertEqual(sbd, v)

    def test_rshares_to_vote_pct(self):
        hv = self.bts
        sp = 1000
        voting_power = 9000
        for vote_pct in range(500, 10000, 500):
            rshares = hv.hp_to_rshares(sp, voting_power=voting_power, vote_pct=vote_pct)
            vote_pct_ret = hv.rshares_to_vote_pct(rshares, hive_power=sp, voting_power=voting_power)
            self.assertEqual(vote_pct_ret, vote_pct)

    def test_sign(self):
        bts = self.bts
        with self.assertRaises(exceptions.MissingKeyError):
            bts.sign()

    def test_broadcast(self):
        bts = self.bts
        bts.txbuffer.clear()
        tx = bts.comment_options({}, "@gtg/witness-gtg-log", account="test")
        # tx = bts.sign()
        with self.assertRaises(exceptions.MissingKeyError):
            bts.broadcast(tx=tx)

    def test_switch_blockchain(self):
        bts = self.bts
        # Hive-only: switching to non-Hive should raise
        with self.assertRaises(AssertionError):
            bts.switch_blockchain("steem", update_nodes=True)
        bts.switch_blockchain("hive", update_nodes=True)
        assert bts.is_hive
