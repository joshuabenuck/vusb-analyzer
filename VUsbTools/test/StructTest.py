# vim: ts=4:sw=4:et:ai:hls
import unittest
from VUsbTools import Struct

class EnumDictTest(unittest.TestCase):
    def test_dict(self):
        edict = Struct.EnumDict({
            0x00: "Test"
            })
        self.assertEquals("Test", edict[0x00])
        self.assertEquals('0x01', edict[0x01])


class ItemTest(unittest.TestCase):
    def test_is_abstract_class(self):
        item = Struct.Item("Name")
        threw = False
        try:
            item.decode("")
        except TypeError:
            threw = True
        self.assertTrue(threw)

    def test_matched_bytes_removed(self):
        item = Struct.UInt8("Name")
        buffer = chr(0x01) + chr(0x02)
        self.assertEquals(buffer[1:], item.decode(buffer))

    def value_checker(self, constructor, buffer, value, string):
        item = constructor("Name")
        retbuffer = item.decode(buffer)
        self.assertEquals(value, item._value)
        self.assertEquals(string, str(item))
        return retbuffer

    def test_uint8(self):
        self.value_checker(Struct.UInt8, chr(0x01), 0x01, '1')

    def test_uint8hex(self):
        self.value_checker(Struct.UInt8Hex, chr(0x01), 0x01, '0x01')

    def test_uint16_not_enough_bytes(self):
        self.assertEquals('',
            self.value_checker(Struct.UInt16, chr(0x01), None, 'None'))

    def test_uint16(self):
        self.value_checker(Struct.UInt16,
            chr(0x02) + chr(0x01), 258, "258")

    def test_uint16hex(self):
        self.value_checker(Struct.UInt16Hex,
            chr(0x02) + chr(0x01), 258, "0x0102")

    def test_uint16be(self):
        self.value_checker(Struct.UInt16BE,
            chr(0x01) + chr(0x02), 258, "258")

    def test_uint16behex(self):
        self.value_checker(Struct.UInt16BEHex,
            chr(0x01) + chr(0x02), 258, "0x0102")

    def test_uint32(self):
        self.value_checker(Struct.UInt32,
            chr(0x00) + chr(0x00) + chr(0x00) + chr(0x01), 
            1 << 24, "16777216")

    def test_uint32hex(self):
        self.value_checker(Struct.UInt32Hex,
            chr(0x00) + chr(0x00) + chr(0x00) + chr(0x01), 
            1 << 24, "0x01000000")

    def test_uint32be(self):
        self.value_checker(Struct.UInt32BE,
            chr(0x01) + chr(0x00) + chr(0x00) + chr(0x00), 
            1 << 24, '16777216')

    def test_uint32behex(self):
        self.value_checker(Struct.UInt32BEHex,
            chr(0x01) + chr(0x00) + chr(0x00) + chr(0x00), 
            1 << 24, '0x01000000')

    def _utf16(self):
        pass # TODO: Write a test for this...

class GroupTest(unittest.TestCase):
    pass # TODO: Write tests for this class once I understand it.

if __name__ == "__main__":
    unittest.main()
