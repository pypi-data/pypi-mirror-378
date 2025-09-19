# -*- coding: utf-8 -*-
import logging

from nectarstorage import SqliteConfigurationStore, SqliteEncryptedKeyStore

from .nodelist import NodeList

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())


timeformat = "%Y%m%d-%H%M%S"


def generate_config_store(config, blockchain="hive"):
    #: Default configuration
    """
    Populate a configuration mapping with sensible defaults for Hive-related settings and return it.

    This function mutates the provided mapping in-place by ensuring a set of default configuration keys exist and returns the same mapping. When `blockchain` is "hive" it fills the "node" entry with a current list of Hive nodes; for other values "node" is set to an empty list. Defaults include client and RPC placeholders, order expiration (7 days), HiveSigner endpoints (`hs_api_url`, `hs_oauth_base_url`) and a backward-compatible `oauth_base_url` pointing to the HiveSigner OAuth base URL, canonical URL, default derivation path, and boolean switches for `use_condenser` and `use_tor`.

    Parameters:
        config (MutableMapping): A dict-like configuration object to populate. It will be modified in place.
        blockchain (str): Chain identifier; "hive" populates Hive nodes, any other value leaves the node list empty.

    Returns:
        MutableMapping: The same `config` mapping after defaults have been set.
    """
    nodelist = NodeList()
    if blockchain == "hive":
        nodes = nodelist.get_hive_nodes(testnet=False)
    else:
        # Hive-only
        nodes = []

    config.setdefault("node", nodes)
    config.setdefault("default_chain", blockchain)
    config.setdefault("password_storage", "environment")
    config.setdefault("rpcpassword", "")
    config.setdefault("rpcuser", "")
    config.setdefault("order-expiration", 7 * 24 * 60 * 60)
    config.setdefault("client_id", "")
    config.setdefault("hs_client_id", None)
    config.setdefault("hot_sign_redirect_uri", None)
    # HiveSigner defaults
    config.setdefault("hs_api_url", "https://hivesigner.com/api/")
    config.setdefault("hs_oauth_base_url", "https://hivesigner.com/oauth2/")
    # Backward-compat key used elsewhere; keep but point to HiveSigner
    config.setdefault("oauth_base_url", config["hs_oauth_base_url"])
    config.setdefault("default_canonical_url", "https://hive.blog")
    config.setdefault("default_path", "48'/13'/0'/0'/0'")
    config.setdefault("use_condenser", True)
    config.setdefault("use_tor", False)
    return config


def get_default_config_store(*args, **kwargs):
    return generate_config_store(SqliteConfigurationStore, blockchain="hive")(*args, **kwargs)


def get_default_key_store(config, *args, **kwargs):
    return SqliteEncryptedKeyStore(config=config, **kwargs)
