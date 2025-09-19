# -*- coding: utf-8 -*-
import json
import unittest

from nectar.profile import Profile


class Testcases(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_profile(self):
        keys = ["profile.url", "profile.img"]
        values = ["http:", "foobar"]
        profile = Profile(keys, values)
        profile_ref = {"profile": {"url": "http:", "img": "foobar"}}
        self.assertTrue(profile, profile_ref)
        self.assertTrue(json.loads(str(profile)), profile_ref)
        profile.update(profile_ref)
        self.assertTrue(profile, profile_ref)
        profile.remove("img")
        profile_ref = {"profile": {"url": "http:"}}
        self.assertTrue(profile, profile_ref)
        profile = Profile({"foo": "bar"})
        self.assertTrue(profile, {"foo": "bar"})
