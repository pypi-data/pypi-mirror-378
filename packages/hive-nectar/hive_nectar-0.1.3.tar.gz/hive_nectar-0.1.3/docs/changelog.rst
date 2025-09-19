Changelog
=========

0.1.3 - 2025-09-18
------------------

-  **Test**: Working on getting 100% test coverage
-  **Feature**: Added some HAF features for things like reputation.

.. _section-1:

0.1.2 - 2025-09-17
------------------

-  **Fix**: Replaced missing ``**kwargs`` in ``Blocks`` constructor.

.. _section-2:

0.1.1 - 2025-09-17
------------------

-  **Fix**: Added support for ``only_ops`` and ``only_virtual_ops``
   parameters in ``Blocks`` constructor.

0.1.0b - 2025-09-17
-------------------

-  **Breaking Change**: Killed everything that was not specifcally HIVE
   related. If you used this for STEEM and / or Blurt, they are no
   longer supported.
-  **Fix**: Corrected inverted fallback logic in chain detection to
   prefer HIVE over STEEM when ``blockchain_name`` is None.
-  **Fix**: Restored backward compatibility for constructor parameters:

   -  ``Vote.__init__``: Added support for deprecated ``steem_instance``
      and ``hive_instance`` kwargs with deprecation warnings.
   -  ``ActiveVotes.__init__``: Added support for deprecated
      ``steem_instance`` and ``hive_instance`` kwargs with deprecation
      warnings.
   -  ``Witness.__init__``: Added ``**kwargs`` with warnings for
      unexpected parameters.
   -  ``Comment_options.__init__``: Added fallback support for
      deprecated ``percent_steem_dollars`` parameter.

-  **Improvement**: Removed deprecated websocket support from
   GrapheneRPC, now only supports HTTP/requests for better reliability
   and maintainability.
-  **Improvement**: Simplified ecdsasig.py to use only cryptography
   library, removing complex conditional logic for different secp256k1
   implementations. The ``tweak_add`` operation now raises
   NotImplementedError when called.
-  **Major Feature**: Implemented pure Python secp256k1 elliptic curve
   operations for PublicKey.add() method, restoring compatibility with
   existing code that relies on key derivation. The implementation
   includes proper validation, error handling, and maintains the same
   API as before. All unit tests pass successfully.
-  **Fix**: Fixed HiveSigner integration in TransactionBuilder:

   -  Updated appendSigner() to restrict permissions to ‘posting’ when
      using HiveSigner
   -  Fixed sign() method to properly call hivesigner.sign() and attach
      signatures instead of returning early
   -  Fixed broadcast() method to use hivesigner.broadcast() when use_hs
      is True
   -  Added proper error handling and fallbacks for non-HiveSigner flows
   -  **Fix**: Fixed HiveSigner.broadcast() call in TransactionBuilder
      to pass operations list instead of full transaction JSON, and
      include username when available

-  **Fix**: Fixed Claim_reward_balance operation serialization in
   nectarbase/operations.py:

   -  Removed incorrect mutually-exclusive logic between reward_hive and
      reward_hbd
   -  Updated to always serialize all four fields in canonical order:
      account, reward_hive, reward_hbd, reward_vests
   -  Added proper zero-amount defaults (“0.000 HIVE”/“0.000 HBD”) for
      missing reward fields
   -  Updated docstring to reflect correct behavior and field
      requirements

-  **Fix**: Convert beneficiary weights from ``HIVE_100_PERCENT`` units
   (10000) to percentages in ``Comment.get_beneficiaries_pct()`` to
   ensure accurate outputs.
-  **Fix**: Improve ECDSA signing to correctly handle prehashed messages
   and tighten signature canonicalization checks for better
   interoperability.
-  **Refactor**: Reorder wallet lock verification to run after
   HiveSigner validation in ``TransactionBuilder``, preventing premature
   lock errors for HiveSigner flows.
-  **Refactor**: Replace implicit stdin default with an explicit
   blockchain selection in the CLI argument parser to avoid ambiguous
   behavior.
-  **Refactor**: Update default Hive node configuration to use HTTPS
   endpoints instead of WSS.
-  **Feature**: Add a pure-Python fallback for public key derivation
   when the ``ecdsa`` library is unavailable, improving portability.

.. _section-3:

0.0.11 - 2025-07-25
-------------------

-  Fixed handling of missing ``community`` field in comments
   (``Comment``) and improved ``weighted_score`` type check in node list
   ranking (``NodeList``).

.. _section-4:

0.0.10 - 2025-07-12
-------------------

-  Emergency hotfix: lower-case the UTC timestamp suffix during permlink
   generation (in ``derive_permlink``) to resolve validation errors
   caused by the uppercase ``U``.

.. _section-5:

0.0.9 - 2025-07-12
------------------

-  Refactored ``nodelist`` logic:

   -  ``update_nodes`` now reads authoritative node metadata from
      ``nectarflower`` account ``json_metadata`` only.
   -  Uses ``weighted_score`` directly for ranking and zeroes scores for
      nodes missing from the report.
   -  Dynamically adds new nodes from the report and failing list,
      ensuring completeness.
   -  Removed unused fall-back paths and cleaned up internal code.

.. _section-6:

0.0.8
-----

Added new documentation and type hints to community

.. _section-7:

0.0.7
-----

Removed all python2 legacy dependencies, drop python3 version
requirement to >=3.10

.. _section-8:

0.0.6
-----

Updated to more robust error reporting

.. _section-9:

0.0.5
-----

More community fixes, including the Community Title Property

.. _section-10:

0.0.4
-----

Small community fixes

.. _section-11:

0.0.3
-----

Working on bridge api

.. _section-12:

0.0.2
-----

Rebranded to Nectar

.. _section-13:

0.0.1
-----

-  Initial release
-  Beem stops and Nectar starts
