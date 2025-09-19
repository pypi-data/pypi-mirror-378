# -*- coding: utf-8 -*-

from nectar.constants import (
    EXEC_FOLLOW_CUSTOM_OP_SCALE,
    resource_execution_time,
    state_object_size_info,
)
from nectarbase import operations
from nectarbase.objects import Operation
from nectarbase.signedtransactions import Signed_Transaction

from .instance import shared_blockchain_instance


class RC(object):
    def __init__(self, blockchain_instance=None, **kwargs):
        """
        Initialize the RC helper with a blockchain instance.

        If `blockchain_instance` is provided it will be used for RC lookups and broadcasts;
        otherwise the module-wide shared_blockchain_instance() is used. Extra keyword
        arguments are accepted for compatibility but ignored.
        """
        self.blockchain = blockchain_instance or shared_blockchain_instance()

    def get_tx_size(self, op):
        """
        Estimate the serialized size (in bytes) of a signed transaction containing the given operation.

        This constructs a dummy Signed_Transaction using fixed reference fields and a hard-coded private key, signs it on the "HIVE" chain, and returns the length of the resulting serialized transaction in bytes. The value is an estimate useful for RC sizing and does not represent a real broadcastable transaction.

        Parameters:
            op: Operation or dict-like operation payload to include in the transaction.

        Returns:
            int: Number of bytes in the serialized, signed transaction.
        """
        ops = [Operation(op)]
        prefix = "HIVE"
        wif = "5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3"
        ref_block_num = 34294
        ref_block_prefix = 3707022213
        expiration = "2016-04-06T08:29:27"
        tx = Signed_Transaction(
            ref_block_num=ref_block_num,
            ref_block_prefix=ref_block_prefix,
            expiration=expiration,
            operations=ops,
        )
        tx = tx.sign([wif], chain=prefix)
        tx_size = len(bytes(tx))
        return tx_size

    def get_resource_count(
        self,
        tx_size,
        execution_time_count,
        state_bytes_count=0,
        new_account_op_count=0,
        market_op_count=0,
    ):
        """
        Build and return a resource_count mapping for RC cost calculation.

        Parameters:
            tx_size (int): Transaction size in bytes; used for history bytes and for market bytes when applicable.
            execution_time_count (int): Execution time units for the operation.
            state_bytes_count (int, optional): Additional state bytes contributed by the operation (default 0).
            new_account_op_count (int, optional): Number of new-account operations included (default 0).
            market_op_count (int, optional): If > 0, marks the transaction as a market operation and sets market bytes to tx_size (default 0).

        Returns:
            dict: A dictionary containing keys used by the RC pricing engine, including:
                - resource_history_bytes
                - resource_state_bytes
                - resource_new_accounts
                - resource_execution_time
                - resource_market_bytes (only present if market_op_count > 0)
        """
        resource_count = {"resource_history_bytes": tx_size}
        resource_count["resource_state_bytes"] = state_object_size_info[
            "transaction_object_base_size"
        ]
        resource_count["resource_state_bytes"] += (
            state_object_size_info["transaction_object_byte_size"] * tx_size
        )
        resource_count["resource_state_bytes"] += state_bytes_count
        resource_count["resource_new_accounts"] = new_account_op_count
        resource_count["resource_execution_time"] = execution_time_count
        if market_op_count > 0:
            resource_count["resource_market_bytes"] = tx_size
        return resource_count

    def comment_dict(self, comment_dict):
        """Calc RC costs for a comment dict object

        Example for calculating RC costs

        .. code-block:: python

            from nectar.rc import RC
            comment_dict = {
                            "permlink": "test", "author": "thecrazygm",
                            "body": "test", "parent_permlink": "",
                            "parent_author": "", "title": "test",
                            "json_metadata": {"foo": "bar"}
                           }

            rc = RC()
            print(rc.comment_from_dict(comment_dict))

        """
        op = operations.Comment(**comment_dict)
        tx_size = self.get_tx_size(op)
        permlink_length = len(comment_dict["permlink"])
        parent_permlink_length = len(comment_dict["parent_permlink"])
        return self.comment(
            tx_size=tx_size,
            permlink_length=permlink_length,
            parent_permlink_length=parent_permlink_length,
        )

    def comment(self, tx_size=1000, permlink_length=10, parent_permlink_length=10):
        """Calc RC for a comment"""
        state_bytes_count = state_object_size_info["comment_object_base_size"]
        state_bytes_count += (
            state_object_size_info["comment_object_permlink_char_size"] * permlink_length
        )
        state_bytes_count += (
            state_object_size_info["comment_object_parent_permlink_char_size"]
            * parent_permlink_length
        )
        execution_time_count = resource_execution_time["comment_operation_exec_time"]
        resource_count = self.get_resource_count(tx_size, execution_time_count, state_bytes_count)
        return self.blockchain.get_rc_cost(resource_count)

    def vote_dict(self, vote_dict):
        """Calc RC costs for a vote

        Example for calculating RC costs

        .. code-block:: python

            from nectar.rc import RC
            vote_dict = {
                         "voter": "foobara", "author": "foobarc",
                         "permlink": "foobard", "weight": 1000
                        }

            rc = RC()
            print(rc.comment(vote_dict))

        """
        op = operations.Vote(**vote_dict)
        tx_size = self.get_tx_size(op)
        return self.vote(tx_size=tx_size)

    def vote(self, tx_size=210):
        """Calc RC for a vote"""
        state_bytes_count = state_object_size_info["comment_vote_object_base_size"]
        execution_time_count = resource_execution_time["vote_operation_exec_time"]
        resource_count = self.get_resource_count(tx_size, execution_time_count, state_bytes_count)
        return self.blockchain.get_rc_cost(resource_count)

    def transfer_dict(self, transfer_dict):
        """
        Calculate Resource Credit (RC) cost for a transfer operation represented as a dict.

        The input dict must contain the fields required by a Transfer operation (for example: "from", "to", "amount", "memo"). This function builds a Transfer operation, estimates the signed transaction size, marks the operation as a market operation (market_op_count=1), and returns the RC cost computed by the blockchain instance.

        Parameters:
            transfer_dict (dict): Fields for a Transfer operation compatible with operations.Transfer.

        Returns:
            dict: RC cost structure as returned by the blockchain's get_rc_cost.
        """
        market_op_count = 1
        op = operations.Transfer(**transfer_dict)
        tx_size = self.get_tx_size(op)
        return self.transfer(tx_size=tx_size, market_op_count=market_op_count)

    def transfer(self, tx_size=290, market_op_count=1):
        """Calc RC of a transfer"""
        execution_time_count = resource_execution_time["transfer_operation_exec_time"]
        resource_count = self.get_resource_count(
            tx_size, execution_time_count, market_op_count=market_op_count
        )
        return self.blockchain.get_rc_cost(resource_count)

    def custom_json_dict(self, custom_json_dict):
        """Calc RC costs for a custom_json

        Example for calculating RC costs

        .. code-block:: python

            from nectar.rc import RC
            from collections import OrderedDict
            custom_json_dict = {
                                 "json": [
                                          "reblog", OrderedDict([("account", "xeroc"), ("author", "chainsquad"),
                                                                 ("permlink", "streemian-com-to-open-its-doors-and-offer-a-20-discount")
                                                                ])
                                         ],
                                 "required_auths": [],
                                 "required_posting_auths": ["xeroc"],
                                 "id": "follow"
                                }

            rc = RC()
            print(rc.comment(custom_json_dict))

        """
        op = operations.Custom_json(**custom_json_dict)
        tx_size = self.get_tx_size(op)
        follow_id = custom_json_dict["id"] == "follow"
        return self.custom_json(tx_size=tx_size, follow_id=follow_id)

    def custom_json(self, tx_size=444, follow_id=False):
        execution_time_count = resource_execution_time["custom_json_operation_exec_time"]
        if follow_id:
            execution_time_count *= EXEC_FOLLOW_CUSTOM_OP_SCALE
        resource_count = self.get_resource_count(tx_size, execution_time_count)
        return self.blockchain.get_rc_cost(resource_count)

    def account_update_dict(self, account_update_dict):
        """Calc RC costs for account update"""
        op = operations.Account_update(**account_update_dict)
        tx_size = self.get_tx_size(op)
        execution_time_count = resource_execution_time["account_update_operation_exec_time"]
        resource_count = self.get_resource_count(tx_size, execution_time_count)
        return self.blockchain.get_rc_cost(resource_count)

    def claim_account(self, tx_size=300):
        """Claim account"""
        execution_time_count = resource_execution_time["claim_account_operation_exec_time"]
        resource_count = self.get_resource_count(
            tx_size, execution_time_count, new_account_op_count=1
        )
        return self.blockchain.get_rc_cost(resource_count)

    def get_authority_byte_count(self, auth):
        return (
            state_object_size_info["authority_base_size"]
            + state_object_size_info["authority_account_member_size"] * len(auth["account_auths"])
            + state_object_size_info["authority_key_member_size"] * len(auth["key_auths"])
        )

    def account_create_dict(self, account_create_dict):
        """Calc RC costs for account create"""
        op = operations.Account_create(**account_create_dict)
        state_bytes_count = state_object_size_info["account_object_base_size"]
        state_bytes_count += state_object_size_info["account_authority_object_base_size"]
        state_bytes_count += self.get_authority_byte_count(account_create_dict["owner"])
        state_bytes_count += self.get_authority_byte_count(account_create_dict["active"])
        state_bytes_count += self.get_authority_byte_count(account_create_dict["posting"])
        tx_size = self.get_tx_size(op)
        execution_time_count = resource_execution_time["account_update_operation_exec_time"]
        resource_count = self.get_resource_count(tx_size, execution_time_count, state_bytes_count)
        return self.blockchain.get_rc_cost(resource_count)

    def create_claimed_account_dict(self, create_claimed_account_dict):
        """Calc RC costs for claimed account create"""
        op = operations.Create_claimed_account(**create_claimed_account_dict)
        state_bytes_count = state_object_size_info["account_object_base_size"]
        state_bytes_count += state_object_size_info["account_authority_object_base_size"]
        state_bytes_count += self.get_authority_byte_count(create_claimed_account_dict["owner"])
        state_bytes_count += self.get_authority_byte_count(create_claimed_account_dict["active"])
        state_bytes_count += self.get_authority_byte_count(create_claimed_account_dict["posting"])
        tx_size = self.get_tx_size(op)
        execution_time_count = resource_execution_time["account_update_operation_exec_time"]
        resource_count = self.get_resource_count(tx_size, execution_time_count, state_bytes_count)
        return self.blockchain.get_rc_cost(resource_count)

    def set_slot_delegator(self, from_pool, to_account, to_slot, signer):
        """Set a slot to receive RC from a pool

        :param str from_pool: Pool to set the slot to
        :param str to_account: Account on which we want to update the slot
        :param int to_slot: slot we want to set
        :param str signer: Account who broadcast this
        """
        json_body = [
            "set_slot_delegator",
            {
                "from_pool": from_pool,
                "to_account": to_account,
                "to_slot": to_slot,
                "signer": signer,
            },
        ]
        return self.blockchain.custom_json("rc", json_body, required_auths=[signer])

    def delegate_from_pool(self, from_pool, to_account, max_rc):
        """Set a slot to receive RC from a pool

        :param str from_pool: Pool to set the slot to
        :param str to_account: Account on which we want to update the slot
        :param int max_rc: max rc to delegate
        """
        json_body = [
            "delegate_drc_from_pool",
            {
                "from_pool": from_pool,
                "to_account": to_account,
                "asset_symbol": {"nai": "@@000000037", "decimals": 6},
                "drc_max_mana": max_rc,
            },
        ]
        return self.blockchain.custom_json("rc", json_body, required_auths=[from_pool])

    def delegate_to_pool(self, username, to_pool, rc):
        """Set a slot to receive RC from a pool

        :param str username: user delegating rc to the pool
        :param str to_pool: Pool to delegate to
        :param str rc: rc to delegate
        """
        json_body = [
            "delegate_to_pool",
            {
                "from_account": username,
                "to_pool": to_pool,
                "amount": {"symbol": "VESTS", "amount": rc, "precision": 6, "nai": "@@000000037"},
            },
        ]
        return self.blockchain.custom_json("rc", json_body, required_auths=[username])
