Quickstart
==========

Hive blockchain
---------------------

Nodes for using nectar with the Hive blockchain can be set by the command line tool with:

.. code-block:: bash

   hive-nectar updatenodes --hive

Nodes for the Hive blockchain are set with

.. code-block:: bash

   hive-nectar updatenodes


Hive nodes can be set in a python script with

.. code-block:: python

   from nectar import Hive
   from nectar.nodelist import NodeList
   nodelist = NodeList()
   nodelist.update_nodes()
   nodes = nodelist.get_hive_nodes()
   hive = Hive(node=nodes)
   print(hive.is_hive)

Hive nodes can be set in a python script with

.. code-block:: python

   from nectar import Hive
   from nectar.nodelist import NodeList
   nodelist = NodeList()
   nodelist.update_nodes()
   nodes = nodelist.get_hive_nodes()
   hive = Hive(node=nodes)
   print(hive.is_hive)


Hive
----
The hive object is the connection to the Hive blockchain.
By creating this object different options can be set.

.. note:: All init methods of nectar classes can be given
          the ``blockchain_instance=`` parameter to assure that
          all objects use the same Hive object. When the
          ``blockchain_instance=`` parameter is not used, the 
          hive object is taken from shared_blockchain_instance().

          :func:`nectar.instance.shared_blockchain_instance` returns a global instance of Hive.
          It can be set by :func:`nectar.instance.set_shared_blockchain_instance` otherwise it is created
          on the first call.

.. code-block:: python

   from nectar import Hive
   from nectar.account import Account
   hive = Hive()
   account = Account("test", blockchain_instance=hive)

.. code-block:: python

   from nectar import Hive
   from nectar.account import Account
   from nectar.instance import set_shared_blockchain_instance
   hive = Hive()
   set_shared_blockchain_instance(hive)
   account = Account("test")

Wallet and Keys
---------------
Each account has the following keys:

* Posting key (allows accounts to post, vote, edit, reblog and follow/mute)
* Active key (allows accounts to transfer, power up/down, voting for witness, ...)
* Memo key (Can be used to encrypt/decrypt memos)
* Owner key (The most important key, should not be used with nectar)

Outgoing operation, which will be stored in the hive blockchain, have to be
signed by a private key. E.g. Comment or Vote operation need to be signed by the posting key
of the author or upvoter. Private keys can be provided to nectar temporary or can be
stored encrypted in a sql-database (wallet).

.. note:: Before using the wallet the first time, it has to be created and a password has
          to set. The wallet content is available to hive-nectar and all python scripts, which have
          access to the sql database file.

Creating a wallet
~~~~~~~~~~~~~~~~~
``hive.wallet.wipe(True)`` is only necessary when there was already an wallet created.

.. code-block:: python

   from nectar import Hive
   hive = Hive()
   hive.wallet.wipe(True)
   hive.wallet.unlock("wallet-passphrase")

Adding keys to the wallet
~~~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: python

   from nectar import Hive
   hive = Hive()
   hive.wallet.unlock("wallet-passphrase")
   hive.wallet.addPrivateKey("xxxxxxx")
   hive.wallet.addPrivateKey("xxxxxxx")

Using the keys in the wallet
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from nectar import Hive
   hive = Hive()
   hive.wallet.unlock("wallet-passphrase")
   account = Account("test", blockchain_instance=hive)
   account.transfer("<to>", "<amount>", "<asset>", "<memo>")

Private keys can also set temporary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from nectar import Hive
   hive = Hive(keys=["xxxxxxxxx"])
   account = Account("test", blockchain_instance=hive)
   account.transfer("<to>", "<amount>", "<asset>", "<memo>")

Receiving information about blocks, accounts, votes, comments, market and witness
---------------------------------------------------------------------------------

Receive all Blocks from the Blockchain

.. code-block:: python

   from nectar.blockchain import Blockchain
   blockchain = Blockchain()
   for op in blockchain.stream():
       print(op)

Access one Block

.. code-block:: python

   from nectar.block import Block
   print(Block(1))

Access an account

.. code-block:: python

   from nectar.account import Account
   account = Account("test")
   print(account.balances)
   for h in account.history():
       print(h)

A single vote

.. code-block:: python

   from nectar.vote import Vote
   vote = Vote(u"@gtg/ffdhu-gtg-witness-log|gandalf")
   print(vote.json())

All votes from an account

.. code-block:: python

   from nectar.vote import AccountVotes
   allVotes = AccountVotes("gtg")

Access a post

.. code-block:: python

   from nectar.comment import Comment
   comment = Comment("@gtg/ffdhu-gtg-witness-log")
   print(comment["active_votes"])

Access the market

.. code-block:: python

   from nectar.market import Market
   market = Market("HBD:HIVE")
   print(market.ticker())

Access a witness

.. code-block:: python

   from nectar.witness import Witness
   witness = Witness("gtg")
   print(witness.is_active)

Sending transaction to the blockchain
-------------------------------------

Sending a Transfer

.. code-block:: python

   from nectar import Hive
   hive = Hive()
   hive.wallet.unlock("wallet-passphrase")
   account = Account("test", blockchain_instance=hive)
   account.transfer("null", 1, "SBD", "test")

Upvote a post

.. code-block:: python

   from nectar.comment import Comment
   from nectar import Hive
   hive = Hive()
   hive.wallet.unlock("wallet-passphrase")
   comment = Comment("@gtg/ffdhu-gtg-witness-log", blockchain_instance=hive)
   comment.upvote(weight=10, voter="test")

Publish a post to the blockchain

.. code-block:: python

   from nectar import Hive
   hive = Hive()
   hive.wallet.unlock("wallet-passphrase")
   hive.post("title", "body", author="test", tags=["a", "b", "c", "d", "e"], self_vote=True)

Sell HIVE on the market

.. code-block:: python

   from nectar.market import Market
   from nectar import Hive
   hive.wallet.unlock("wallet-passphrase")
   market = Market("HBD:HIVE", blockchain_instance=hive)
   print(market.ticker())
   market.hive.wallet.unlock("wallet-passphrase")
   print(market.sell(300, 100))  # sell 100 HIVE for 300 HIVE/HBD
