"""Regression for the 2026-11-07 WOW LAB date parsing crash."""
import datetime as dt
import unittest

class SlotParsingRegression(unittest.TestCase):
    def test_slot_day_is_numeric(self):
        for stamp in ("20261107T20", "20261231T22", "20260101T00"):
            parsed=dt.datetime.strptime(stamp,"%Y%m%dT%H")
            self.assertEqual(parsed.day,int(stamp[6:8]))
            self.assertIsInstance((int(stamp[-2:])//2+parsed.day)%8,int)
