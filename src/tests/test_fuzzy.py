import unittest
import sys
import os

sys.path[0:0] = [os.path.join(os.path.dirname(__file__), ".."),]

import zoe

class TestCmd:
    def execute(self, r):
        return True
    
TestCmd.commands = [
                    ("abc/def <integer> ghi <string>", TestCmd()), 
                    ("jkl <integer> <string>", TestCmd())
                   ]

class TestFuzzy (unittest.TestCase):

    def test_extract_strings(self):
        f = zoe.Fuzzy()
        cmd = '"abc" def "ghi" j "k"'
        after = '<string> def <string> j <string>'
        (strings, cmd) = f.extract_strings(cmd)
        self.assertEqual (["abc", "ghi", "k"], strings)
        self.assertEqual (after, cmd)

    def test_extract_integers(self):
        f = zoe.Fuzzy()
        cmd = '123 abc 456 def 1'
        after = '<integer> abc <integer> def <integer>'
        (integers, cmd) = f.extract_integers(cmd)
        self.assertEqual (['123', '456', '1'], integers)
        self.assertEqual (after, cmd)

    def test_extract_floats(self):
        f = zoe.Fuzzy()
        cmd = '123.4 abc 56.7 def .5'
        after = '<float> abc <float> def <float>'
        (floats, cmd) = f.extract_floats(cmd)
        self.assertEqual (['123.4', '56.7', '.5'], floats)
        self.assertEqual (after, cmd)

    def test_extract_users(self):
        f = zoe.Fuzzy()
        cmd = 'voiser abc roberto def fer'
        after = '<user> abc <user> def <user>'
        (users, cmd) = f.extract_users(cmd)
        self.assertEqual (after, cmd)
    
    def test_fuzzy_result(self):
        f = zoe.Fuzzy()
        cmd = 'abc voiser def 5 "ghi" 6.7'
        r = f.analyze(cmd)
        self.assertEqual (["ghi"], r["strings"])
        self.assertEqual (["5"], r["integers"])
        self.assertEqual (["6.7"], r["floats"])
        self.assertEqual (1, len(r["users"]))
        self.assertEqual ("abc <user> def <integer> <string> <float>", r["stripped"])

    def test_pattern(self):
        f = zoe.Fuzzy()
        p = "abc/def/ghi jkl mn/op"
        ps = f.patterns(p)
        self.assertEqual (6, len(ps))
        ps.remove("abc jkl mn")
        ps.remove("abc jkl op")
        ps.remove("def jkl mn")
        ps.remove("def jkl op")
        ps.remove("ghi jkl mn")
        ps.remove("ghi jkl op")
        self.assertEqual (0, len(ps))

    def test_command(self):
        f = zoe.Fuzzy()
        f.register(TestCmd)
        c, r = f.commandfor('jkl 5 "string string"')
        self.assertEqual (TestCmd, c.__class__)
        c, r = f.commandfor('idontknow')
        self.assertEqual (zoe.SmallTalkCmd, c.__class__)

    def test_execute(self):
        f = zoe.Fuzzy()
        f.register(TestCmd())
        r2 = f.execute('jkl 5 "string string"')
        self.assertTrue (r2)


if __name__ == "__main__":
    unittest.main()

