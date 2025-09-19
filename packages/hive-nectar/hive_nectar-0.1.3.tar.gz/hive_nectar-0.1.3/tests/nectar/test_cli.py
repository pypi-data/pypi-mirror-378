# -*- coding: utf-8 -*-
import os
import unittest

from click.testing import CliRunner

from nectar.cli import cli
from nectar.instance import shared_blockchain_instance
from nectar.utils import import_pubkeys

from .nodes import get_hive_nodes

wif = "5Jt2wTfhUt5GkZHV1HYVfkEaJ6XnY8D2iA4qjtK9nnGXAhThM3w"
posting_key = "5Jh1Gtu2j4Yi16TfhoDmg8Qj3ULcgRi7A49JXdfUUTVPkaFaRKz"
memo_key = "5KPbCuocX26aMxN9CDPdUex4wCbfw9NoT5P7UhcqgDwxXa47bit"
pub_key = "STX52xMqKegLk4tdpNcUXU9Rw5DtdM9fxf3f12Gp55v1UjLX3ELZf"


class Testcases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Prepare the test environment for the suite by configuring the CLI and initializing a wallet with test keys.

        This class-level setup:
        - Retrieves the hive node list and stores it on the class.
        - Uses Click's CliRunner to set default CLI options (default vote weight, default account, nodes).
        - Creates a new test wallet (wiping any existing wallet) and imports three predefined keys (WIF, posting, memo).
        - Raises AssertionError if any CLI invocation exits with a non-zero code, including the CliRunner result in the error.

        Side effects:
        - Modifies global CLI configuration and the on-disk wallet state via the Nectar CLI.
        - Relies on module-level key constants and get_hive_nodes().
        """
        cls.node_list = get_hive_nodes()

        # hv = shared_blockchain_instance()
        # hv.config.refreshBackup()
        runner = CliRunner()
        result = runner.invoke(cli, ["-o", "set", "default_vote_weight", "100"])
        if result.exit_code != 0:
            raise AssertionError(str(result))
        result = runner.invoke(cli, ["-o", "set", "default_account", "nectarflower"])
        if result.exit_code != 0:
            raise AssertionError(str(result))
        result = runner.invoke(cli, ["-o", "set", "nodes", str(cls.node_list)])
        if result.exit_code != 0:
            raise AssertionError(str(result))
        result = runner.invoke(cli, ["createwallet", "--wipe"], input="test\ntest\n")
        if result.exit_code != 0:
            raise AssertionError(str(result))
        result = runner.invoke(cli, ["addkey"], input="test\n" + wif + "\n")
        if result.exit_code != 0:
            raise AssertionError(str(result))
        result = runner.invoke(cli, ["addkey"], input="test\n" + posting_key + "\n")
        if result.exit_code != 0:
            raise AssertionError(str(result))
        result = runner.invoke(cli, ["addkey"], input="test\n" + memo_key + "\n")
        if result.exit_code != 0:
            raise AssertionError(str(result))

    @classmethod
    def tearDownClass(cls):
        """
        Restore shared blockchain state and refresh CLI node list after tests.

        This class teardown recovers the shared blockchain instance from the latest backup to restore global state modified by the tests, then invokes the CLI's `updatenodes --hive` command to refresh the configured node list.
        """
        hv = shared_blockchain_instance()
        hv.config.recover_with_latest_backup()
        runner = CliRunner()
        _ = runner.invoke(cli, ["updatenodes", "--hive"])

    def test_balance(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["balance", "thecrazygm", "nectarflower"])
        self.assertEqual(result.exit_code, 0)

    def test_interest(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["-dx", "interest", "thecrazygm", "nectarflower"])
        self.assertEqual(result.exit_code, 0)

    def test_config(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["config"])
        self.assertEqual(result.exit_code, 0)

    def test_addkey(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["createwallet", "--wipe"], input="test\ntest\n")
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(cli, ["addkey"], input="test\n" + wif + "\n")
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(cli, ["addkey"], input="test\n" + posting_key + "\n")
        self.assertEqual(result.exit_code, 0)

    def test_parsewif(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["parsewif"], input=wif + "\nexit\n")
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(cli, ["parsewif", "--unsafe-import-key", wif])
        self.assertEqual(result.exit_code, 0)

    def test_changerecovery(self):
        runner = CliRunner()
        result = runner.invoke(
            cli, ["-dx", "changerecovery", "-a", "thecrazygm", "thecrazygm"], input=wif + "\nexit\n"
        )
        self.assertEqual(result.exit_code, 0)

    def test_delkey(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["delkey", "--confirm", pub_key], input="test\n")
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(cli, ["addkey"], input="test\n" + posting_key + "\n")
        # self.assertEqual(result.exit_code, 0)

    def test_listkeys(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["listkeys"])
        self.assertEqual(result.exit_code, 0)

    def test_listaccounts(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["listaccounts"])
        self.assertEqual(result.exit_code, 0)

    def test_info(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["info"])
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(cli, ["info", "thecrazygm"])
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(cli, ["info", "100"])
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(cli, ["info", "--", "-1"])
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(cli, ["info", pub_key])
        self.assertEqual(result.exit_code, 0)

    def test_info2(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["info", "--", "42725832:-1"])
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(cli, ["info", "--", "42725832:1"])
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(cli, ["info", "gtg"])
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(cli, ["info", "@gtg/witness-gtg-log"])
        self.assertEqual(result.exit_code, 0)

    def test_changepassword(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["changewalletpassphrase"], input="test\ntest\ntest\n")
        self.assertEqual(result.exit_code, 0)

    def test_walletinfo(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["walletinfo"])
        self.assertEqual(result.exit_code, 0)

    def test_keygen(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["keygen"])
        self.assertEqual(result.exit_code, 0)

    def test_passwordgen(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["passwordgen"])
        self.assertEqual(result.exit_code, 0)
        data_dir = os.path.join(os.path.dirname(__file__), "data")
        file = os.path.join(data_dir, "drv-wif-idx100.txt")
        file2 = os.path.join(data_dir, "wif_pub_temp.json")
        result = runner.invoke(cli, ["passwordgen", "-a", "test", "-o", file, "-u", file2, "-w", 1])
        self.assertEqual(result.exit_code, 0)
        owner, active, posting, memo = import_pubkeys(file2)
        self.assertEqual(owner, "STM7d8DzUzjs5jbSkBVNctRaZFGe991MhzzTrqMoTVvZJ5oyZN7Cj")
        self.assertEqual(active, "STM7oADsCds97GqyEDY4cQC66brVrg7XHuRa2MLvYbuGrdKnNoQa6")
        self.assertEqual(posting, "STM5fpGcVwvUFF55EzWQ35oJeERcWvt4M9dXwehdpYmKaFCCqihL7")
        self.assertEqual(memo, "STM6A7DywWvMZRokxAK5CpTo8XAPKbrMennAs4ntwRFq5nj2jR7nG")
        os.remove(file2)

    def test_set(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["-o", "set", "set_default_vote_weight", "100"])
        self.assertEqual(result.exit_code, 0)

    def test_upvote(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["-dx", "upvote", "@steemit/firstpost"], input="test\n")
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(
            cli, ["-dx", "upvote", "--weight", "100", "@steemit/firstpost"], input="test\n"
        )
        self.assertEqual(result.exit_code, 0)

    def test_downvote(self):
        runner = CliRunner()
        result = runner.invoke(
            cli, ["-dx", "downvote", "--weight", "100", "@steemit/firstpost"], input="test\n"
        )
        self.assertEqual(result.exit_code, 0)

    def test_download(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["-dx", "download", "-a", "steemit", "firstpost"])
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(cli, ["-dx", "download", "@steemit/firstpost"])
        self.assertEqual(result.exit_code, 0)

    def test_transfer(self):
        hv = shared_blockchain_instance()
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["-dx", "transfer", "thecrazygm", "1", hv.backed_token_symbol, "test"],
            input="test\n",
        )
        self.assertEqual(result.exit_code, 0)

    def test_powerdownroute(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["-dx", "powerdownroute", "thecrazygm"], input="test\n")
        self.assertEqual(result.exit_code, 0)

    def test_convert(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["-dx", "convert", "1"], input="test\n")
        self.assertEqual(result.exit_code, 0)

    def test_powerup(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["-dx", "powerup", "1"], input="test\n")
        self.assertEqual(result.exit_code, 0)

    def test_powerdown(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["-dx", "powerdown", "1e3"], input="test\n")
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(cli, ["-dx", "powerdown", "0"], input="test\n")
        self.assertEqual(result.exit_code, 0)

    def test_updatememokey(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["-dx", "updatememokey"], input="test\ntest\ntest\n")
        self.assertEqual(result.exit_code, 0)

    def test_permissions(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["permissions", "thecrazygm"])
        self.assertEqual(result.exit_code, 0)

    def test_follower(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["follower", "thecrazygm"])
        self.assertEqual(result.exit_code, 0)

    def test_following(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["following", "thecrazygm"])
        self.assertEqual(result.exit_code, 0)

    def test_muter(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["muter", "thecrazygm"])
        self.assertEqual(result.exit_code, 0)

    def test_about(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["about"])
        self.assertEqual(result.exit_code, 0)

    def test_muting(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["muting", "thecrazygm"])
        self.assertEqual(result.exit_code, 0)

    def test_allow_disallow(self):
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["-dx", "allow", "--account", "nectarflower", "--permission", "posting", "thecrazygm"],
            input="test\n",
        )
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(
            cli,
            [
                "-dx",
                "disallow",
                "--account",
                "nectarflower",
                "--permission",
                "posting",
                "thecrazygm",
            ],
            input="test\n",
        )
        self.assertEqual(result.exit_code, 0)

    def test_witnesses(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["witnesses"])
        self.assertEqual(result.exit_code, 0)

    @unittest.skip
    def test_votes(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["votes", "--direction", "out", "nectarflower"])
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(cli, ["votes", "--direction", "in", "nectarflower"])
        self.assertEqual(result.exit_code, 0)

    def test_approvewitness(self):
        runner = CliRunner()
        result = runner.invoke(
            cli, ["-dx", "approvewitness", "-a", "nectarflower", "synergy.witness"], input="test\n"
        )
        self.assertEqual(result.exit_code, 0)

    def test_disapprovewitness(self):
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["-dx", "disapprovewitness", "-a", "nectarflower", "synergy.witness"],
            input="test\n",
        )
        self.assertEqual(result.exit_code, 0)

    def test_addproxy(self):
        runner = CliRunner()
        result = runner.invoke(
            cli, ["-dx", "setproxy", "-a", "nectarflower", "thecrazygm"], input="test\n"
        )
        self.assertEqual(result.exit_code, 0)

    def test_delproxy(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["-dx", "delproxy", "-a", "nectarflower"], input="test\n")
        self.assertEqual(result.exit_code, 0)

    def test_newaccount(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["-dx", "newaccount", "nectar3"], input="test\ntest\n")
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(
            cli,
            [
                "-dx",
                "newaccount",
                "--owner",
                "STM7mLs2hns87f7kbf3o2HBqNoEaXiTeeU89eVF6iUCrMQJFzBsPo",
                "--active",
                "STM7rUmnpnCp9oZqMQeRKDB7GvXTM9KFvhzbA3AKcabgTBfQZgHZp",
                "--posting",
                "STM6qGWHsCpmHbphnQbS2yfhvhJXDUVDwnsbnrMZkTqfnkNEZRoLP",
                "--memo",
                "STM8Wvi74GYzBKgnUmiLvptzvxmPtXfjGPJL8QY3rebecXaxGGQyV",
                "nectar3",
            ],
            input="test\ntest\n",
        )
        self.assertEqual(result.exit_code, 0)

    def test_changekeys(self):
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "-dx",
                "changekeys",
                "--owner",
                "STM7mLs2hns87f7kbf3o2HBqNoEaXiTeeU89eVF6iUCrMQJFzBsPo",
                "--active",
                "STM7rUmnpnCp9oZqMQeRKDB7GvXTM9KFvhzbA3AKcabgTBfQZgHZp",
                "--posting",
                "STM6qGWHsCpmHbphnQbS2yfhvhJXDUVDwnsbnrMZkTqfnkNEZRoLP",
                "--memo",
                "STM8Wvi74GYzBKgnUmiLvptzvxmPtXfjGPJL8QY3rebecXaxGGQyV",
                "nectar",
            ],
            input="test\ntest\n",
        )
        self.assertEqual(result.exit_code, 0)

    @unittest.skip
    def test_importaccount(self):
        runner = CliRunner()
        runner.invoke(cli, ["-o", "set", "nodes", str(self.node_list)])
        result = runner.invoke(
            cli,
            ["importaccount", "--roles", '["owner", "active", "posting", "memo"]', "nectar2"],
            input="test\numybjvCafrt8LdoCjEimQiQ4\n",
        )
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(
            cli,
            ["delkey", "--confirm", "STX7mLs2hns87f7kbf3o2HBqNoEaXiTeeU89eVF6iUCrMQJFzBsPo"],
            input="test\n",
        )
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(
            cli,
            ["delkey", "--confirm", "STX7rUmnpnCp9oZqMQeRKDB7GvXTM9KFvhzbA3AKcabgTBfQZgHZp"],
            input="test\n",
        )
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(
            cli,
            ["delkey", "--confirm", "STX6qGWHsCpmHbphnQbS2yfhvhJXDUVDwnsbnrMZkTqfnkNEZRoLP"],
            input="test\n",
        )
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(
            cli,
            ["delkey", "--confirm", "STX8Wvi74GYzBKgnUmiLvptzvxmPtXfjGPJL8QY3rebecXaxGGQyV"],
            input="test\n",
        )
        self.assertEqual(result.exit_code, 0)

    def test_orderbook(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["orderbook"])
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(cli, ["orderbook", "--show-date"])
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(cli, ["orderbook", "--chart"])
        self.assertEqual(result.exit_code, 0)

    def test_buy(self):
        hv = shared_blockchain_instance()
        runner = CliRunner()
        result = runner.invoke(
            cli, ["-dt", "-x", "buy", "0.001", hv.token_symbol, "0.002"], input="test\n"
        )
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(
            cli, ["-dt", "-x", "buy", "0.001", hv.token_symbol], input="y\ntest\n"
        )
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(
            cli, ["-dt", "-x", "buy", "0.001", hv.backed_token_symbol, "0.002"], input="test\n"
        )
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(
            cli, ["-dt", "-x", "buy", "0.001", hv.backed_token_symbol], input="y\ntest\n"
        )
        self.assertEqual(result.exit_code, 0)

    def test_sell(self):
        hv = shared_blockchain_instance()
        runner = CliRunner()
        result = runner.invoke(
            cli, ["-dt", "-x", "sell", "1", hv.token_symbol, "2.2"], input="test\n"
        )
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(
            cli, ["-dt", "-x", "sell", "1", hv.backed_token_symbol, "2.2"], input="test\n"
        )
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(cli, ["-dt", "-x", "sell", "1", hv.token_symbol], input="y\ntest\n")
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(
            cli, ["-dt", "-x", "sell", "1", hv.backed_token_symbol], input="y\ntest\n"
        )
        self.assertEqual(result.exit_code, 0)

    def test_cancel(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["-dx", "cancel", "5"], input="test\n")
        self.assertEqual(result.exit_code, 0)

    def test_openorders(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["openorders"])
        self.assertEqual(result.exit_code, 0)

    def test_reblog(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["-dto", "reblog", "@steemit/firstpost"], input="test\n")
        self.assertEqual(result.exit_code, 0)

    def test_follow_unfollow(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["-dto", "follow", "nectarflower"], input="test\n")
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(cli, ["-dto", "unfollow", "nectarflower"], input="test\n")
        self.assertEqual(result.exit_code, 0)

    def test_mute_unmute(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["-dto", "mute", "nectarflower"], input="test\n")
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(cli, ["-dto", "unfollow", "nectarflower"], input="test\n")
        self.assertEqual(result.exit_code, 0)

    def test_witnesscreate(self):
        runner = CliRunner()
        _ = runner.invoke(cli, ["-dx", "witnesscreate", "nectarflower", pub_key], input="test\n")

    def test_witnessupdate(self):
        runner = CliRunner()
        runner.invoke(
            cli,
            [
                "-dx",
                "witnessupdate",
                "gtg",
                "--maximum_block_size",
                65000,
                "--account_creation_fee",
                0.1,
                "--sbd_interest_rate",
                0,
                "--url",
                "https://google.de",
                "--signing_key",
                wif,
            ],
        )

    def test_profile(self):
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["-dx", "setprofile", "-a", "nectarflower", "url", "https://google.de"],
            input="test\n",
        )
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(
            cli, ["-dx", "delprofile", "-a", "nectarflower", "url"], input="test\n"
        )
        self.assertEqual(result.exit_code, 0)

    def test_claimreward(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["-dx", "claimreward"], input="test\n")
        result = runner.invoke(cli, ["-dx", "claimreward", "--claim_all_steem"], input="test\n")
        result = runner.invoke(cli, ["-dx", "claimreward", "--claim_all_sbd"], input="test\n")
        result = runner.invoke(cli, ["-dx", "claimreward", "--claim_all_vests"], input="test\n")
        self.assertEqual(result.exit_code, 0)

    def test_claimaccount(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["-dx", "claimaccount", "thecrazygm"])
        result = runner.invoke(cli, ["-dx", "claimaccount", "-n", "2", "thecrazygm"])
        self.assertEqual(result.exit_code, 0)

    def test_power(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["power", "thecrazygm"])
        self.assertEqual(result.exit_code, 0)

    def test_history(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["history", "thecrazygm"])
        self.assertEqual(result.exit_code, 0)

    def test_draw(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["draw"])
        self.assertEqual(result.exit_code, 0)

    def test_witnessenable(self):
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["-dx", "witnessenable", "gtg", "STM1111111111111111111111111111111114T1Anm"],
        )
        self.assertEqual(result.exit_code, 0)

    def test_witnessdisable(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["-dx", "witnessdisable", "gtg"])
        self.assertEqual(result.exit_code, 0)

    def test_nextnode(self):
        runner = CliRunner()
        runner.invoke(cli, ["-o", "set", "nodes", self.node_list])
        result = runner.invoke(cli, ["-o", "nextnode"])
        self.assertEqual(result.exit_code, 0)
        runner.invoke(cli, ["-o", "set", "nodes", str(self.node_list)])

    def test_pingnode(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["pingnode"])
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(cli, ["pingnode", "--sort"])
        self.assertEqual(result.exit_code, 0)

    def test_updatenodes(self):
        runner = CliRunner()
        runner.invoke(cli, ["-o", "set", "nodes", self.node_list])
        result = runner.invoke(cli, ["updatenodes"])
        self.assertEqual(result.exit_code, 0)
        runner.invoke(cli, ["-o", "set", "nodes", str(self.node_list)])

    def test_currentnode(self):
        runner = CliRunner()
        runner.invoke(cli, ["-o", "set", "nodes", self.node_list])
        result = runner.invoke(cli, ["currentnode"])
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(cli, ["currentnode", "--url"])
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(cli, ["currentnode", "--version"])
        self.assertEqual(result.exit_code, 0)
        runner.invoke(cli, ["-o", "set", "nodes", str(self.node_list)])

    def test_ticker(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["ticker"])
        self.assertEqual(result.exit_code, 0)

    def test_pricehistory(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["pricehistory"])
        self.assertEqual(result.exit_code, 0)

    def test_notifications(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["notifications", "nectarflower"])
        self.assertEqual(result.exit_code, 0)

    def test_pending(self):
        runner = CliRunner()
        account_name = "nectarflower"
        result = runner.invoke(cli, ["pending", account_name])
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(cli, ["pending", "--post", "--comment", account_name])
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(
            cli, ["pending", "--curation", "--permlink", "--days", "1", account_name]
        )
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(
            cli,
            [
                "pending",
                "--post",
                "--comment",
                "--author",
                "--permlink",
                "--length",
                "30",
                "--days",
                "1",
                account_name,
            ],
        )
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(
            cli, ["pending", "--post", "--author", "--title", "--days", "1", account_name]
        )
        self.assertEqual(result.exit_code, 0)

    def test_rewards(self):
        runner = CliRunner()
        account_name = "nectarflower"
        result = runner.invoke(cli, ["rewards", account_name])
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(cli, ["rewards", "--post", "--comment", "--curation", account_name])
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(
            cli, ["rewards", "--post", "--comment", "--curation", "--permlink", account_name]
        )
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(
            cli, ["rewards", "--post", "--comment", "--curation", "--author", account_name]
        )
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(
            cli, ["rewards", "--post", "--comment", "--author", "--title", account_name]
        )
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(
            cli,
            [
                "rewards",
                "--post",
                "--comment",
                "--author",
                "--permlink",
                "--length",
                "30",
                account_name,
            ],
        )
        self.assertEqual(result.exit_code, 0)

    def test_curation(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["curation", "@gtg/witness-gtg-log"])
        self.assertEqual(result.exit_code, 0)

    def test_verify(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["verify", "--trx", "3", "25304468"])
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(cli, ["verify", "--trx", "5", "25304468"])
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(cli, ["verify", "--trx", "0"])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.exit_code, 0)

    def test_tradehistory(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["tradehistory"])
        self.assertEqual(result.exit_code, 0)
