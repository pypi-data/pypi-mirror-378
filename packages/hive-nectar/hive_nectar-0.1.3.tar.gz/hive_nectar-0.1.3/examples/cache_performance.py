from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import sys
import time

from nectar import Hive as Hive
from nectar.blockchain import Blockchain
from nectar.nodelist import NodeList

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def stream_votes(hv, threading, thread_num):
    """
    Stream "vote" operations from the blockchain and return the count and elapsed time.

    Streams operations with opName "vote" over the hard-coded block range 23,483,000–23,485,000 using a Blockchain backed by the provided Hive instance. Writes the latest operation's block number to stdout (overwriting the same line) as operations are received.

    Parameters:
        threading (bool): Whether to use the Blockchain.stream threading mode.
        thread_num (int): Number of threads to use when threading is enabled.

    Returns:
        tuple: (opcount, total_duration) where opcount is the number of vote operations processed
        and total_duration is the elapsed time in seconds.
    """
    b = Blockchain(blockchain_instance=hv)
    opcount = 0
    start_time = time.time()
    for op in b.stream(
        start=23483000, stop=23485000, threading=threading, thread_num=thread_num, opNames=["vote"]
    ):
        sys.stdout.write("\r%s" % op["block_num"])
        opcount += 1
    now = time.time()
    total_duration = now - start_time
    print(" votes: %d, time %.2f" % (opcount, total_duration))
    return opcount, total_duration


if __name__ == "__main__":
    node_setup = 1
    threading = True
    thread_num = 8
    timeout = 10
    nodes = NodeList()
    nodes.update_nodes(weights={"block": 1})
    node_list = nodes.get_nodes()[:5]

    vote_result = []
    duration = []

    hv = Hive(node=node_list, timeout=timeout)
    b = Blockchain(blockchain_instance=hv)
    block = b.get_current_block()
    block.set_cache_auto_clean(False)
    opcount, total_duration = stream_votes(hv, threading, thread_num)
    print("Finished!")
    block.set_cache_auto_clean(True)
    cache_len = len(list(block._cache))
    start_time = time.time()
    block.clear_cache_from_expired_items()
    clear_duration = time.time() - start_time
    time.sleep(5)
    cache_len_after = len(list(block._cache))
    start_time = time.time()
    print(str(block._cache))
    clear_duration2 = time.time() - start_time
    print("Results:")
    print(
        "%d Threads with https duration: %.2f s - votes: %d" % (thread_num, total_duration, opcount)
    )
    print(
        "Clear %d items in %.3f s (%.3f s) (%d remaining)"
        % (cache_len, clear_duration, clear_duration2, cache_len_after)
    )
