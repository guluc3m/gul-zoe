import unittest
import sys
import os

sys.path[0:0] = [os.path.join(os.path.dirname(__file__), ".."),]

import zoe

class TestMessageParser (unittest.TestCase):
    def test_smoke (self):
        message = "a=b"
        mp = zoe.MessageParser (message)
        self.assertEqual (mp.msg(), message)

    def test_twopairs (self):
        message = "key1=value1&key2=value2"
        mp = zoe.MessageParser (message)
        self.assertEqual ("value1", mp.get("key1")) 
        self.assertEqual ("value2", mp.get("key2")) 

    def test_multiple_values (self):
        message = "key1=value1&key1=value1bis&key2=value2"
        mp = zoe.MessageParser (message)
        self.assertTrue  (mp.get("key1").__class__ is list)
        self.assertTrue  (mp.get("key2").__class__ is str)
        self.assertEqual (mp.get("key1")[0], "value1")
        self.assertEqual (mp.get("key1")[1], "value1bis")

    def test_base64 (self):
        message = "key1=value1&key2=abc=="
        mp = zoe.MessageParser (message)
        self.assertEqual ("value1", mp.get("key1")) 
        self.assertEqual ("abc==", mp.get("key2")) 

    def test_tags (self):
        message = "tag=a&tag=b&key1=value1&key2=value2&tag=c"
        mp = zoe.MessageParser (message)
        tags = mp.tags()
        self.assertEqual (["a", "b", "c"], tags)
    

class TestMessageBuilder (unittest.TestCase):
    def test_smoke (self):
        aMap = {"key1":"value1", "key2":"value2"}
        mb = zoe.MessageBuilder (aMap)
        mp = zoe.MessageParser (mb.msg())
        self.assertEqual ("value1", mp.get("key1")) 
        self.assertEqual ("value2", mp.get("key2")) 
        
    def test_multiple (self):
        aMap = {"key1":["value1", "value1bis"], "key2":"value2"}
        mb = zoe.MessageBuilder (aMap)
        mp = zoe.MessageParser (mb.msg())
        self.assertTrue  (mp.get("key1").__class__ is list)
        self.assertTrue  (mp.get("key2").__class__ is str)
        self.assertEqual (mp.get("key1")[0], "value1")
        self.assertEqual (mp.get("key1")[1], "value1bis")

    def test_override (self):
        msg = "key1=value1&key2=value2&key3=value3"
        mb = zoe.MessageBuilder.override (msg, {"key1":"new_value1"})
        mp = zoe.MessageParser (mb.msg())
        self.assertEqual (mp.get("key1"), "new_value1")
        self.assertEqual (mp.get("key2"), "value2")
        self.assertEqual (mp.get("key3"), "value3")
    
    def test_override2 (self):
        msg = "key1=value1&key2=value2&key3=value3"
        mp = zoe.MessageParser (msg)
        mb = zoe.MessageBuilder.override (mp, {"key1":"new_value1"})
        mp = zoe.MessageParser (mb.msg())
        self.assertEqual (mp.get("key1"), "new_value1")
        self.assertEqual (mp.get("key2"), "value2")
        self.assertEqual (mp.get("key3"), "value3")

if __name__ == "__main__":
    unittest.main()


