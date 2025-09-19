# -*- coding: utf-8 -*-
import os
import random
import shutil
import tempfile
import unittest

from nectar import Hive
from nectar.instance import set_shared_blockchain_instance
from nectar.memo import Memo

from .nodes import get_hive_nodes

wif = "5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3"
core_unit = "STM"


class Testcases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bts = Hive(node=get_hive_nodes(), nobroadcast=True, keys=[wif], num_retries=10)
        set_shared_blockchain_instance(cls.bts)

    def test_decryt_encrypt(self):
        memo = Memo(from_account=wif, to_account="thecrazygm")
        base_string_length = [
            1,
            2,
            3,
            4,
            5,
            7,
            8,
            9,
            15,
            16,
            17,
            32,
            63,
            64,
            65,
            127,
            255,
            511,
            1023,
            2047,
            4095,
        ]
        for n in base_string_length:
            test_string = str(random.getrandbits(n))
            ret = memo.encrypt(test_string)
            ret_string = memo.decrypt(ret["message"])
            self.assertEqual(test_string, ret_string[1:])

    def test_decrypt_encrypt_file(self):
        test_dir = tempfile.mkdtemp()
        outfile = os.path.join(test_dir, "test.txt")
        outfile_enc = os.path.join(test_dir, "test_enc.txt")
        test_string = str(random.getrandbits(1000))
        with open(outfile, "w") as f:
            f.write(test_string)
        memo = Memo(from_account=wif, to_account="thecrazygm")
        memo.encrypt_binary(outfile, outfile_enc)
        memo.decrypt_binary(outfile_enc, outfile)
        with open(outfile, "r") as f:
            content = f.read()
        self.assertEqual(test_string, content)
        shutil.rmtree(test_dir)
