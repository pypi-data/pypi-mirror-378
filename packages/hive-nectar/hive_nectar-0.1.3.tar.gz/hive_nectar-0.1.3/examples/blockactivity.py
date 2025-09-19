import argparse
import logging
import sys
from datetime import timedelta
from timeit import default_timer as timer

from nectar import Hive
from nectar.block import Block
from nectar.blockchain import Blockchain
from nectar.nodelist import NodeList
from nectar.utils import parse_time

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def parse_args(args=None):
    """
    Parse command-line arguments for the blocktivity CLI.

    One-line summary:
        Parse arguments and return the parsed namespace.

    Detailed description:
        Recognizes a single optional positional argument "blockchain" (default: sys.stdin) which
        should be the target blockchain identifier (currently "hive"). The optional `args`
        parameter can be used to pass an argument list for testing or programmatic invocation.

    Parameters:
        args (list or None): Optional list of argument strings to parse. If None, the parser
            reads from sys.argv.

    Returns:
        argparse.Namespace: Parsed arguments with attribute `blockchain`.
    """
    d = "Verify blocktivity by counting operations and trx for the last 24 hours."
    parser = argparse.ArgumentParser(description=d)
    parser.add_argument(
        "blockchain",
        type=str,
        nargs="?",
        default="hive",
        choices=["hive"],
        help="Blockchain (hive)",
    )
    return parser.parse_args(args)


def main(args=None):
    """
    Run a block activity (blocktivity) check over the last 24 hours for the Hive blockchain and print a summary.

    This function parses CLI arguments to select the blockchain (Hive only), builds a node/client, scans the most recent ~24 hours of blocks (assuming ~3s block interval) to count:
    - total transactions and operations (first pass),
    - virtual operations (second pass),
    and prints throughput and per-day totals.

    Parameters:
        args (list or None): Optional list of command-line arguments to parse (passed to parse_args). If None, parse_args reads from sys.argv.

    Raises:
        Exception: If the `blockchain` argument is provided and is not "hive".
    """
    args = parse_args(args)
    blockchain = args.blockchain

    nodelist = NodeList()
    nodelist.update_nodes(weights={"block": 1})

    if blockchain == "hive" or blockchain is None:
        max_batch_size = 50
        threading = False
        thread_num = 16
        block_debug = 1000

        nodes = nodelist.get_hive_nodes()
        blk_inst = Hive(node=nodes, num_retries=3, num_retries_call=3, timeout=30)
    else:
        raise Exception("Wrong parameter, can be hive")
    print(blk_inst)
    block_count = 0
    total_ops = 0
    total_virtual_ops = 0
    total_trx = 0
    duration_s = 60 * 60 * 24
    blocksperday = int(duration_s / 3)

    blockchain = Blockchain(
        blockchain_instance=blk_inst,
    )
    current_block_num = blockchain.get_current_block_num()
    last_block_id = current_block_num - blocksperday

    last_block = Block(last_block_id, blockchain_instance=blk_inst)

    stopTime = last_block.time() + timedelta(seconds=duration_s)

    start = timer()
    for entry in blockchain.blocks(
        start=last_block_id,
        max_batch_size=max_batch_size,
        threading=threading,
        thread_num=thread_num,
    ):
        if "block" in entry:
            block_time = parse_time(entry["block"]["timestamp"])
        else:
            block_time = entry["timestamp"]
        if block_time > stopTime:
            break
        block_count += 1
        if "block" in entry:
            trxs = entry["block"]["transactions"]
        else:
            trxs = entry["transactions"]
        for tx in trxs:
            total_trx += 1
            for op in tx["operations"]:
                total_ops += 1

        ops_per_day = total_ops / block_count * blocksperday
        if block_count % (block_debug) == 0:
            print(
                "%d blocks remaining... estimated ops per day: %.1f"
                % (blocksperday - block_count, ops_per_day)
            )

    duration = timer() - start

    stopTime = last_block.time() + timedelta(seconds=duration_s)
    start = timer()
    for entry in blockchain.blocks(
        start=last_block_id,
        max_batch_size=max_batch_size,
        threading=threading,
        thread_num=thread_num,
        only_virtual_ops=True,
    ):
        block_time = entry["timestamp"]
        if block_time > stopTime:
            break
        for tx in entry["operations"]:
            for op in tx["op"]:
                total_virtual_ops += 1

    duration = timer() - start

    print("Received %.2f blocks/s." % (block_count / duration))
    print("Bocks: %d, duration %.3f s" % (block_count, duration))
    print("Operations per day: %d" % total_ops)
    print("Trx per day: %d" % total_trx)
    print("Virtual Operations per day: %d" % total_virtual_ops)


if __name__ == "__main__":
    sys.exit(main())
