# -*- coding: utf-8 -*-
import logging

from nectargraphenebase.chains import known_chains
from nectargraphenebase.signedtransactions import Signed_Transaction as GrapheneSigned_Transaction

from .operations import Operation

log = logging.getLogger(__name__)


class Signed_Transaction(GrapheneSigned_Transaction):
    """Create a signed transaction and offer method to create the
    signature

    :param num refNum: parameter ref_block_num (see :func:`nectarbase.transactions.getBlockParams`)
    :param num refPrefix: parameter ref_block_prefix (see :func:`nectarbase.transactions.getBlockParams`)
    :param str expiration: expiration date
    :param array operations:  array of operations
    :param dict custom_chains: custom chain which should be added to the known chains
    """

    def __init__(self, *args, **kwargs):
        self.known_chains = known_chains
        custom_chain = kwargs.get("custom_chains", {})
        if len(custom_chain) > 0:
            for c in custom_chain:
                if c not in self.known_chains:
                    self.known_chains[c] = custom_chain[c]
        super(Signed_Transaction, self).__init__(*args, **kwargs)

    def add_custom_chains(self, custom_chain):
        """
        Add entries from custom_chain into this transaction's known chains without overwriting existing entries.

        Accepts a mapping of chain identifiers to chain configuration values and merges any keys not already present into self.known_chains. Existing known chains are left unchanged.
        Parameters:
            custom_chain (Mapping): Mapping of chain name -> chain data (e.g., RPC URL or chain parameters); keys present in self.known_chains are not replaced.
        """
        if len(custom_chain) > 0:
            for c in custom_chain:
                if c not in self.known_chains:
                    self.known_chains[c] = custom_chain[c]

    def sign(self, wifkeys, chain="HIVE"):
        """
        Sign the transaction using one or more WIF-format private keys.

        wifkeys: Single WIF string or iterable of WIF private key strings used to produce signatures.
        chain: Chain identifier to use for signing (defaults to "HIVE").

        Returns:
            The value returned by the superclass `sign` implementation.
        """
        return super(Signed_Transaction, self).sign(wifkeys, chain)

    def verify(self, pubkeys=None, chain="HIVE", recover_parameter=False):
        """
        Verify this transaction's signatures.

        Parameters:
            pubkeys (list[str] | None): Public keys to verify against. If None, an empty list is used (all signatures will be checked
                without restricting expected pubkeys).
            chain (str): Chain identifier to use for verification (defaults to "HIVE").
            recover_parameter (bool): If True, return signature recovery parameters alongside verification results.

        Returns:
            Any: The result returned by the superclass verify method (verification outcome as defined by the base implementation).
        """
        if pubkeys is None:
            pubkeys = []
        return super(Signed_Transaction, self).verify(pubkeys, chain, recover_parameter)

    def getOperationKlass(self):
        """
        Return the Operation class used to construct operations for this transaction.

        Returns:
            type: The Operation class used by this Signed_Transaction.
        """
        return Operation

    def getKnownChains(self):
        return self.known_chains
