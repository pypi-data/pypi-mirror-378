#!/usr/bin/python
import sys

# mpl.use('Agg')
# mpl.use('TkAgg')
import matplotlib.pyplot as plt

from nectar.snapshot import AccountSnapshot

if __name__ == "__main__":
    if len(sys.argv) != 2:
        # print("ERROR: command line parameter mismatch!")
        # print("usage: %s [account]" % (sys.argv[0]))
        account = "thecrazygm"
    else:
        account = sys.argv[1]
    acc_snapshot = AccountSnapshot(account)
    acc_snapshot.get_account_history()
    acc_snapshot.build()
    # acc_snapshot.build(only_ops=["producer_reward"])
    # acc_snapshot.build(only_ops=["curation_reward"])
    # acc_snapshot.build(only_ops=["author_reward"])
    acc_snapshot.build_sp_arrays()
    timestamps = acc_snapshot.timestamps
    own_sp = acc_snapshot.own_sp
    eff_sp = acc_snapshot.eff_sp

    plt.figure(figsize=(12, 6))
    opts = {"linestyle": "-", "marker": "."}
    plt.plot_date(timestamps[1:], own_sp[1:], label="Own HP", **opts)
    plt.plot_date(timestamps[1:], eff_sp[1:], label="Effective HP", **opts)
    plt.grid()
    plt.legend()
    plt.title("HP over time - @%s" % (account))
    plt.xlabel("Date")
    plt.ylabel("Hive Power (HP)")
    # plt.show()
    plt.savefig("sp_over_time-%s.png" % (account))

    print("last effective HP: %.1f HP" % (eff_sp[-1]))
    print("last own HP: %.1f HP" % (own_sp[-1]))
