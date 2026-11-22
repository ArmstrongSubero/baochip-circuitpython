# Dabao CircuitPython full test
#
# Four jumpers and nothing else:
#   PB1  to PB4    digitalio and pwmio
#   PB14 to PB13   busio.UART
#   PC1  to PC2    busio.SPI
#   PC8  to PC9    analogio
# Leave PB11 and PB12 (I2C) empty. Save as code.py.

import gc, sys, time, binascii, hashlib, aesio, baosec

# ---------------------------------------------------------------- software

def t_array():
    import array
    a = array.array("H", [1, 2, 3]); a.append(65535)
    return len(a) == 4 and a[3] == 65535 and bytes(a)[:2] == b"\x01\x00"

def t_binascii():
    import binascii
    return (binascii.hexlify(b"\x01\xab") == b"01ab" and binascii.unhexlify("01ab") == b"\x01\xab"
            and binascii.b2a_base64(b"Dabao").strip() == b"RGFiYW8=" and binascii.crc32(b"123456789") == 0xCBF43926)

def t_collections():
    import collections
    P = collections.namedtuple("P", ("x", "y"))
    d = collections.OrderedDict(); d["b"] = 1; d["a"] = 2
    q = collections.deque((), 4); q.append(1); q.append(2)
    return P(1, 2).y == 2 and list(d.keys()) == ["b", "a"] and q.popleft() == 1

def t_errno():
    import errno
    try:
        open("/no_such_file.txt")
    except OSError as e:
        return e.errno == errno.ENOENT
    return False

def t_io():
    import io
    s = io.StringIO(); s.write("abc"); s.seek(0)
    b = io.BytesIO(b"\x01\x02\x03")
    return s.read() == "abc" and b.read(2) == b"\x01\x02"

def t_json():
    import json
    d = json.loads('{"a": [1, 2.5, "x"], "b": {"c": null, "d": true}}')
    return d["a"][1] == 2.5 and d["b"]["c"] is None and json.loads(json.dumps(d)) == d

def t_math():
    import math
    return (abs(math.sin(math.pi / 6) - 0.5) < 1e-6 and math.sqrt(144) == 12
            and math.floor(-1.5) == -2 and abs(math.atan2(1, 1) - math.pi / 4) < 1e-6)

def t_os():
    import os
    a = os.urandom(16); b = os.urandom(16)
    return a != b and "code.py" in [n.lower() for n in os.listdir("/")] and os.stat("/code.py")[6] > 0 and os.uname().machine != ""

def t_random():
    import random
    v = [random.randint(0, 1000000) for _ in range(8)]
    return len(set(v)) > 4 and 0 <= random.random() < 1 and random.choice([7]) == 7

def t_re():
    import re
    m = re.match(r"(\w+)=(\d+)", "speed=350")
    return m.group(1) == "speed" and int(m.group(2)) == 350 and re.sub("a+", "-", "caaat") == "c-t"

def t_struct():
    import struct
    p = struct.pack("<HIb", 0x1234, 0xDEADBEEF, -5)
    return p == b"\x34\x12\xef\xbe\xad\xde\xfb" and struct.unpack(">h", b"\xff\xfe")[0] == -2

def t_sys():
    return sys.implementation.name == "circuitpython" and sys.byteorder == "little" and sys.maxsize > 1000

def t_time():
    a = time.monotonic(); n = time.monotonic_ns(); time.sleep(0.25)
    d = time.monotonic() - a
    return 0.24 < d < 0.30 and time.monotonic_ns() - n > 240000000

def t_traceback():
    import traceback
    try:
        1 / 0
    except Exception as e:
        return "ZeroDivisionError" in "".join(traceback.format_exception(e))

def t_zlib():
    import zlib
    return zlib.decompress(BLOB) == b"Dabao" * 20

def t_gc():
    for i in range(40):
        x = bytearray(200000)
        x[i] = i
    gc.collect()
    return gc.mem_free() > 200000 and gc.mem_alloc() > 0

def t_bigheap():
    x = bytearray(500000)
    x[499999] = 7
    return x[499999] == 7

def t_float_int():
    return 2 ** 100 == 1267650600228229401496703205376 and abs(0.1 + 0.2 - 0.3) < 1e-6 and int("ff", 16) == 255

def t_microcontroller():
    import microcontroller
    return len(microcontroller.cpu.uid) == 16 and microcontroller.cpu.frequency > 1000000

def t_supervisor():
    import supervisor
    return supervisor.runtime.serial_connected in (True, False) and supervisor.ticks_ms() >= 0

def t_storage():
    import storage
    m = storage.getmount("/")
    return m.label == "CIRCUITPY" or m.label != ""

def t_board():
    import board
    return board.board_id == "dabao" and hasattr(board, "SCL") and hasattr(board, "TX")

def t_asyncio():
    import asyncio
    log = []
    async def worker(name, delay, n):
        for i in range(n):
            await asyncio.sleep(delay)
            log.append(name)
        return name
    async def main():
        t0 = time.monotonic()
        r = await asyncio.gather(worker("a", 0.05, 4), worker("b", 0.10, 2))
        ev = asyncio.Event()
        async def setter():
            await asyncio.sleep(0.05); ev.set()
        asyncio.create_task(setter())
        await asyncio.wait_for(ev.wait(), 1)
        try:
            await asyncio.wait_for(worker("c", 1, 1), 0.05)
            timed = False
        except asyncio.TimeoutError:
            timed = True
        return r, time.monotonic() - t0, timed
    r, dt, timed = asyncio.run(main())
    return r == ["a", "b"] and log.count("a") == 4 and log.count("b") == 2 and 0.28 < dt < 0.50 and timed

def t_ticks():
    import adafruit_ticks
    a = adafruit_ticks.ticks_ms(); time.sleep(0.1)
    d = adafruit_ticks.ticks_diff(adafruit_ticks.ticks_ms(), a)
    return 95 <= d <= 130

def t_simpleio():
    import simpleio
    return simpleio.map_range(512, 0, 1024, 0, 3.3) == 1.65 and simpleio.map_range(2000, 0, 1024, 0, 10) == 10

def t_motor():
    import board, pwmio
    from adafruit_motor import servo
    p = pwmio.PWMOut(board.PB1, frequency=50, duty_cycle=0)
    try:
        s = servo.Servo(p, min_pulse=1000, max_pulse=2000)
        s.angle = 90
        return abs(p.duty_cycle - 4915) < 40
    finally:
        p.deinit()

def t_register():
    import board, busio
    from adafruit_bus_device.i2c_device import I2CDevice
    from adafruit_register.i2c_struct import UnaryStruct
    from adafruit_register.i2c_bit import RWBit
    class Part:
        who = UnaryStruct(0x75, "<B")
        sleep = RWBit(0x6B, 6)
        def __init__(self, i2c):
            self.i2c_device = I2CDevice(i2c, 0x68, probe=False)
    i2c = busio.I2C(board.SCL, board.SDA)
    try:
        part = Part(i2c)
        try:
            part.who
            return "a register read from an empty bus did not fail"
        except OSError:
            return True
    finally:
        i2c.deinit()

BLOB = b'x\x9csILJ\xccw\xa1-\x01\x00<S$\xcd'

SOFTWARE = [("array", t_array), ("binascii", t_binascii), ("collections", t_collections), ("errno", t_errno),
         ("io", t_io), ("json", t_json), ("math", t_math), ("os", t_os), ("random", t_random), ("re", t_re),
         ("struct", t_struct), ("sys", t_sys), ("time", t_time), ("traceback", t_traceback), ("zlib", t_zlib),
         ("gc", t_gc), ("500 KB allocation", t_bigheap), ("big int and float", t_float_int),
         ("microcontroller", t_microcontroller), ("supervisor", t_supervisor), ("storage", t_storage),
         ("board", t_board), ("asyncio", t_asyncio), ("adafruit_ticks", t_ticks), ("simpleio", t_simpleio),
         ("adafruit_motor", t_motor), ("adafruit_register and adafruit_bus_device", t_register)]


# ---------------------------------------------------------------- security

def hx(b):
    return binascii.hexlify(b).decode()

def unhx(s):
    return binascii.unhexlify(s)

def pat(n, seed):
    return bytes(((i * 31 + seed * 7) & 0xFF) for i in range(n))

def pieces(alg, data, sizes):
    h = hashlib.new(alg)
    at = 0
    for n in sizes:
        h.update(data[at:at + n])
        at += n
    h.update(data[at:])
    return hx(h.digest())

def again(alg):
    h = hashlib.new(alg, pat(100, 3))
    first = h.digest()
    h.update(pat(200, 4))
    return hx(first) + hx(h.digest())

def turns():
    a = hashlib.new("sha256")
    b = hashlib.new("sha512")
    c = hashlib.new("sha256")
    for i in range(5):
        a.update(pat(70, i))
        b.update(pat(130, i))
        c.update(pat(33, i + 9))
    return hx(a.digest()) + hx(b.digest()) + hx(c.digest())

def aes(way, key, mode, iv, parts):
    c = aesio.AES(key, mode, iv) if iv is not None else aesio.AES(key, mode)
    out = b""
    for p in parts:
        buf = bytearray(len(p))
        if way == "e":
            c.encrypt_into(p, buf)
        else:
            c.decrypt_into(p, buf)
        out += bytes(buf)
    return hx(out)

def two():
    a = aesio.AES(pat(16, 21), aesio.MODE_CBC, pat(16, 23))
    b = aesio.AES(pat(32, 22), aesio.MODE_CTR, pat(16, 24))
    src = pat(64, 25)
    x = b""
    y = b""
    buf = bytearray(32)
    a.encrypt_into(src[:32], buf)
    x += bytes(buf)
    small = bytearray(20)
    b.encrypt_into(pat(20, 26), small)
    y += bytes(small)
    a.encrypt_into(src[32:], buf)
    x += bytes(buf)
    small = bytearray(30)
    b.encrypt_into(pat(30, 26), small)
    y += bytes(small)
    return hx(x) + hx(y)

SECURITY = [
  ('sha256 0 bytes', lambda: hx(hashlib.new('sha256', bytes(((i * 31 + 1 * 7) & 0xFF) for i in range(0))).digest()), 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'),
  ('sha256 3 bytes', lambda: hx(hashlib.new('sha256', bytes(((i * 31 + 1 * 7) & 0xFF) for i in range(3))).digest()), '647674a296197442f518bcca323ec605dd8d098b2d4f22ee1fdcdd2bb753a189'),
  ('sha256 55 bytes', lambda: hx(hashlib.new('sha256', bytes(((i * 31 + 1 * 7) & 0xFF) for i in range(55))).digest()), '8aa994584139d128848eeebc4e815639ba5ab6e6e39574195a63ac4f14f7c43b'),
  ('sha256 56 bytes', lambda: hx(hashlib.new('sha256', bytes(((i * 31 + 1 * 7) & 0xFF) for i in range(56))).digest()), 'ad574708f75c044c9b85de64cb568ee7711ff4f36448c6242f053ba8f6cc2b63'),
  ('sha256 63 bytes', lambda: hx(hashlib.new('sha256', bytes(((i * 31 + 1 * 7) & 0xFF) for i in range(63))).digest()), '280ed3e8ff1df845b2e7dfe6ac6cee817bef20e783cc65abc41b818b4d2fe076'),
  ('sha256 64 bytes', lambda: hx(hashlib.new('sha256', bytes(((i * 31 + 1 * 7) & 0xFF) for i in range(64))).digest()), 'c6ab9724ade5b6a7a1edfffb12f3aa9181351355af8fd08c919952ad211339dd'),
  ('sha256 65 bytes', lambda: hx(hashlib.new('sha256', bytes(((i * 31 + 1 * 7) & 0xFF) for i in range(65))).digest()), '788367c73c7ddf4c53f65e68cc0d943e6227ab55b0e78ba63ace822b1c6301c0'),
  ('sha256 111 bytes', lambda: hx(hashlib.new('sha256', bytes(((i * 31 + 1 * 7) & 0xFF) for i in range(111))).digest()), 'dd1413178fb627f9abbc041ffe39c44aa7aaa0e2e6d2ca5c4528ac7073a2da45'),
  ('sha256 112 bytes', lambda: hx(hashlib.new('sha256', bytes(((i * 31 + 1 * 7) & 0xFF) for i in range(112))).digest()), 'a65c92dac124062d0ab951a42773cb04fc98d1d4bf8897b176f8cff3509d379e'),
  ('sha256 119 bytes', lambda: hx(hashlib.new('sha256', bytes(((i * 31 + 1 * 7) & 0xFF) for i in range(119))).digest()), '3d610547d68216dedf7435a4fb6260353911f6b3fd3f18805ddb8be285d726fe'),
  ('sha256 127 bytes', lambda: hx(hashlib.new('sha256', bytes(((i * 31 + 1 * 7) & 0xFF) for i in range(127))).digest()), '192409cd280e14b743642ad1343fbd3e82d9305de72c078117745a679210cc3d'),
  ('sha256 128 bytes', lambda: hx(hashlib.new('sha256', bytes(((i * 31 + 1 * 7) & 0xFF) for i in range(128))).digest()), 'cc548ca2dec1f6fe4f58b2e27aa9c7521607df1130d140b55a4dad0665302356'),
  ('sha256 129 bytes', lambda: hx(hashlib.new('sha256', bytes(((i * 31 + 1 * 7) & 0xFF) for i in range(129))).digest()), '81e89a7b2911aaa7795f9e3d4910cb47d6cd2b00d83b8399481527261a1a7519'),
  ('sha256 1000 bytes', lambda: hx(hashlib.new('sha256', bytes(((i * 31 + 1 * 7) & 0xFF) for i in range(1000))).digest()), '5097e7d587352f5097062ae679f37bda5802d9f875aba14c8cb4d1a188ada179'),
  ('sha256 5000 bytes', lambda: hx(hashlib.new('sha256', bytes(((i * 31 + 1 * 7) & 0xFF) for i in range(5000))).digest()), '1e92fd98f113aba0a78e0830ca06e2775912370feab112dfc57bf3258b810595'),
  ('sha256 in pieces', lambda: pieces('sha256', bytes(((i * 31 + 2 * 7) & 0xFF) for i in range(1000)), (7, 64, 1, 300, 128, 0, 500)), '2403092bab557d5305aa81041492fce49492ad2099fa6c5fabd9d7ddffa075e9'),
  ('sha256 digest then more', lambda: again('sha256'), 'c14afb856ca595ea8b2358b853c7734bb694f1d1292419fd8e8f0b2054a64d9ddb8a32486d5788bced6d1fa6db08318c909594d925902f22f19a59debcccee8c'),
  ('sha512 0 bytes', lambda: hx(hashlib.new('sha512', bytes(((i * 31 + 1 * 7) & 0xFF) for i in range(0))).digest()), 'cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e'),
  ('sha512 3 bytes', lambda: hx(hashlib.new('sha512', bytes(((i * 31 + 1 * 7) & 0xFF) for i in range(3))).digest()), 'a4fb160ae2ee41d19cbec56b514cc5fb0c07adb0a398968a15857c9ef56ba3813d640099a21cd216a543d7e3feb42493cdf5f5787ec7c0f0a853bcb245f8f243'),
  ('sha512 55 bytes', lambda: hx(hashlib.new('sha512', bytes(((i * 31 + 1 * 7) & 0xFF) for i in range(55))).digest()), '330eb5e81b4d722cae1e0efbf883efb180c3e346d2b3b797dafc90409583ed35af65dc2d7974a353f0c21663e196b60d3ee5a2c70c50b7b3bccdb93a5dbce6bf'),
  ('sha512 56 bytes', lambda: hx(hashlib.new('sha512', bytes(((i * 31 + 1 * 7) & 0xFF) for i in range(56))).digest()), '1b5b63bfd5420b2dc480abce3dbdb3e19e5f9d4fabffba7764883937eaae878a55362c938c141712c44c3076c3fabb2c60814c2994c311c33049a8d6de2a8898'),
  ('sha512 63 bytes', lambda: hx(hashlib.new('sha512', bytes(((i * 31 + 1 * 7) & 0xFF) for i in range(63))).digest()), 'b16f76c30db64b5ee1ef166d2d37e13ff6cee9fd88bae9ba283cd58e0a2133b220a76db56279406461f84ce2cffd1d116d38fd9f38fc5df18770a987ff695499'),
  ('sha512 64 bytes', lambda: hx(hashlib.new('sha512', bytes(((i * 31 + 1 * 7) & 0xFF) for i in range(64))).digest()), '4c7aba3659929c4fd87604c532a3b5f174d0626b2d661dbbbfac76c97a49a5a7789d2c68324c754f66bf629fa72054f334feaad8b1cf4c885ae03a1e634afc18'),
  ('sha512 65 bytes', lambda: hx(hashlib.new('sha512', bytes(((i * 31 + 1 * 7) & 0xFF) for i in range(65))).digest()), '31ad8ce60482e91ec7f83455c280f2dbb4940a400795ae90815bc86891210ebe07b51995eb2d123d6a55a79a998e20cc07716aea7848f6c955b4a4bf14ad0b0a'),
  ('sha512 111 bytes', lambda: hx(hashlib.new('sha512', bytes(((i * 31 + 1 * 7) & 0xFF) for i in range(111))).digest()), 'da780d8338a8a920ceb6892cb4ecbb0cc0c66956269aadd5dd0f48790a00857bd975890f3b2955a317738cc7a770820c29f922ffbc22020f1909d594cc987d1b'),
  ('sha512 112 bytes', lambda: hx(hashlib.new('sha512', bytes(((i * 31 + 1 * 7) & 0xFF) for i in range(112))).digest()), '053182f7fa4e59f8636e415a77ed4fdc650f0a43834c9d35adf899599c3ab9c4153f02ff50bd01888060cd36a6fa12d9db242fc35164c80135613514186d5843'),
  ('sha512 119 bytes', lambda: hx(hashlib.new('sha512', bytes(((i * 31 + 1 * 7) & 0xFF) for i in range(119))).digest()), 'c6203c98db894a187e332570d8b0c317766be115afc7afa530e00ef42f2aa7492a7a4bba9b81762cf2a635c9bd22bde8fd85868d1214e48ae057cd7b69fdd7ff'),
  ('sha512 127 bytes', lambda: hx(hashlib.new('sha512', bytes(((i * 31 + 1 * 7) & 0xFF) for i in range(127))).digest()), 'a7a75593826fd37d4e60f6101eabb9f8ab1cf4d5319ebc805266d5da8deb5097de1a235fc5d9d3d73c50ac100ffc75089fb454674ab61232091bd19cbdc67396'),
  ('sha512 128 bytes', lambda: hx(hashlib.new('sha512', bytes(((i * 31 + 1 * 7) & 0xFF) for i in range(128))).digest()), 'df007a08f3aaae47e0c92ef840ecd43645ae6098c819f2a4a66174ef1cd49e5c6dfccf0616895e570b7564af641de5863dff9f89c752913d30cf0ecf678e1635'),
  ('sha512 129 bytes', lambda: hx(hashlib.new('sha512', bytes(((i * 31 + 1 * 7) & 0xFF) for i in range(129))).digest()), 'a10ea769b79831bca33e9efb29fc501ded6e9c88885d079acb76eecaa8ac58d68bdc7e00103053e1519352c0d064c87accc3d553a6039decc2c4f1e7667eef79'),
  ('sha512 1000 bytes', lambda: hx(hashlib.new('sha512', bytes(((i * 31 + 1 * 7) & 0xFF) for i in range(1000))).digest()), 'b41d42e106eca6bf57123566b7ed1550c37d33af23afbfa8e302dfd44c988b3003a26b4140ef42f535e66ea424e7c4a31616307269e6d520a6508f726da23d0a'),
  ('sha512 5000 bytes', lambda: hx(hashlib.new('sha512', bytes(((i * 31 + 1 * 7) & 0xFF) for i in range(5000))).digest()), 'e15b57d1eabf16a1497d5fa36740126da5bd32ed9970239b0d71bc425f110164fa3288ee593d8677ee8818e0092752a6f714d5e2b540e99dd1ff6efa0e95eec6'),
  ('sha512 in pieces', lambda: pieces('sha512', bytes(((i * 31 + 2 * 7) & 0xFF) for i in range(1000)), (7, 64, 1, 300, 128, 0, 500)), '69e6b12bdb71009ea6cde6597f31da62ae202ca692508f6436796f1f2fbad06a593ccfb19bacd7e51276dbd850d3dd275a5b273e92595066dbef8d56d6164344'),
  ('sha512 digest then more', lambda: again('sha512'), '2642741d3d3b4e65eb7fddf055b04ee912502e9af59fd1f75a93fb41df889703436e86eab84f4ee38268d2ffb134e722e117bd26c6656ec9333d060defedb2c4a5f7649fda78b9dc56dd8af39953a211aff3d8462f906d6e5a1668cadd8c0bdbfd485793d0485d726fde1bc8ee2898c9aacd046a889eedc121fcbb9e6390fc87'),
  ('three hashes in turn', lambda: turns(), '0cad0a380b30354da834fcf6e0301befa78913216f63a95b89ef9d9f0d071ce275cd8d4cdd4daceb8ea5d41e64343c0955f765444c7a58594f56cd45840f7c93e963390cb8df86e7fb59e334fa66ef7aee59481a5c7de1c7c1d47ea6fe6b689f7b0b83c6f97d3f58812d071b3a18cf020bfe7d68f75ed331b948b3650e52f964'),
  ('hmac_sha256 key 1 msg 0', lambda: hx(baosec.hmac_sha256(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(1)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(0)))), 'fe23de9f5a983786ac8a7b7237e6ba9bfaaf6249d5ff0cca47e3c71cb5347247'),
  ('hmac_sha256 key 1 msg 1', lambda: hx(baosec.hmac_sha256(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(1)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(1)))), '71db96d0314ff6d72041a37c58fed25d3b80da44531bea811961b3e103371b54'),
  ('hmac_sha256 key 1 msg 64', lambda: hx(baosec.hmac_sha256(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(1)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(64)))), 'eddd0db4052cc9f387f7236bae27e89fd54cda65aa76e0b5447868c985fe1fb4'),
  ('hmac_sha256 key 1 msg 1000', lambda: hx(baosec.hmac_sha256(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(1)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(1000)))), '7f46b68d29188e99a3a32324f03b4e11f23cda82e0009f00ab50abecfbba1dcc'),
  ('hmac_sha256 key 20 msg 0', lambda: hx(baosec.hmac_sha256(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(20)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(0)))), '6feec965111c4c641ab174167a3dee77e2cafe86ee4c53de46f6bc14f1a330eb'),
  ('hmac_sha256 key 20 msg 1', lambda: hx(baosec.hmac_sha256(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(20)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(1)))), 'e5e93be276af780702923619c3b1b23c0d4236f7cf07ffcbded8f8f8aaeb9f4d'),
  ('hmac_sha256 key 20 msg 64', lambda: hx(baosec.hmac_sha256(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(20)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(64)))), '8b9702e090da00f4d62210ed255f45869d5d754f7583815e6793f58a1d2b052a'),
  ('hmac_sha256 key 20 msg 1000', lambda: hx(baosec.hmac_sha256(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(20)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(1000)))), '6d17c7d8d905100aaf4acd7f6be575c3b0fbf28d63ac48a6ce2562f3036cd375'),
  ('hmac_sha256 key 64 msg 0', lambda: hx(baosec.hmac_sha256(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(64)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(0)))), 'af3498aa3a0431461b2a2df5e08a42b0690db967eeec736f143bec833893e9a8'),
  ('hmac_sha256 key 64 msg 1', lambda: hx(baosec.hmac_sha256(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(64)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(1)))), '617d3329dc8c28b443432ed77fe781265ac3ef8bbd672748e63311125d3e2120'),
  ('hmac_sha256 key 64 msg 64', lambda: hx(baosec.hmac_sha256(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(64)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(64)))), '64dbaee650051760f73d170b67d0fd06ae7d989434c9edc2fffa69150645c8cb'),
  ('hmac_sha256 key 64 msg 1000', lambda: hx(baosec.hmac_sha256(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(64)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(1000)))), '0dd7241276e55cce88641f61040903726f4a38cb6ad3a08861fffcfb1b64b79a'),
  ('hmac_sha256 key 65 msg 0', lambda: hx(baosec.hmac_sha256(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(65)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(0)))), '20e57993050f1a8a0e96ea0129539b009db0f3a350c0a65e5b892558a422f675'),
  ('hmac_sha256 key 65 msg 1', lambda: hx(baosec.hmac_sha256(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(65)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(1)))), '6ee952a8fda5329b98cbf1e97c4a3987d208d5274cf8b839d10a74401f80d327'),
  ('hmac_sha256 key 65 msg 64', lambda: hx(baosec.hmac_sha256(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(65)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(64)))), '60c523a38d6b00a27cbbe60b3a1d608ef226131cb843931021aea6f16255e169'),
  ('hmac_sha256 key 65 msg 1000', lambda: hx(baosec.hmac_sha256(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(65)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(1000)))), '4b6a9830138bb4d3556291149096bc33413fc17ea927aa6f1b317653855df52e'),
  ('hmac_sha256 key 128 msg 0', lambda: hx(baosec.hmac_sha256(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(128)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(0)))), '9a18364b389317985955c9acda35850f71da94c0ead211ff1c5c9e81fd416bbc'),
  ('hmac_sha256 key 128 msg 1', lambda: hx(baosec.hmac_sha256(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(128)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(1)))), '6a1af0ca404fe0b562919d1852f7d54f4040db8e85e0ce13b0b955bed0263346'),
  ('hmac_sha256 key 128 msg 64', lambda: hx(baosec.hmac_sha256(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(128)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(64)))), 'a8f2d92514f13f42cd837269d857e79b3f1be3acb93fc6ce67205026ae108af9'),
  ('hmac_sha256 key 128 msg 1000', lambda: hx(baosec.hmac_sha256(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(128)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(1000)))), '352523dd3f35fa87774b245fee388d51f8e05a47b91a7960e1f2f13ad4addbcb'),
  ('hmac_sha256 key 129 msg 0', lambda: hx(baosec.hmac_sha256(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(129)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(0)))), '898c12013cec17c3581dae8721855f4054b39eb3106b16911e96cfb0094ae0e1'),
  ('hmac_sha256 key 129 msg 1', lambda: hx(baosec.hmac_sha256(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(129)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(1)))), 'bab41260c72fb35858b281c63640fec08f155988fb12ba4788e5e5287e4c07e4'),
  ('hmac_sha256 key 129 msg 64', lambda: hx(baosec.hmac_sha256(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(129)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(64)))), 'fe237346a2b96b94b3dcca09bd45c1bad663475be8b7e79951d583398a6b92d2'),
  ('hmac_sha256 key 129 msg 1000', lambda: hx(baosec.hmac_sha256(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(129)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(1000)))), 'b1c9b3057bcf79e9e457ada379dbbf6673d90ea3549027b23f4748d918464be3'),
  ('hmac_sha256 key 200 msg 0', lambda: hx(baosec.hmac_sha256(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(200)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(0)))), 'cbe798d1c5ea43c18371139dbb65c44c2e838c02a937a363ec816565f3bc31ae'),
  ('hmac_sha256 key 200 msg 1', lambda: hx(baosec.hmac_sha256(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(200)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(1)))), 'c19999b9eab672cd3d5aeb81b9ba99a28be72a214fbe75023d7784b74fb00cdd'),
  ('hmac_sha256 key 200 msg 64', lambda: hx(baosec.hmac_sha256(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(200)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(64)))), '29b08de46674d07a6873e74268db30a427da280b70d5ae8f8ba8e0d6451fac5e'),
  ('hmac_sha256 key 200 msg 1000', lambda: hx(baosec.hmac_sha256(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(200)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(1000)))), '1ec57e96af66b07d4c8230da94aae63b22d1f0f49b94ed8e4f693d65d5fc0100'),
  ('hmac_sha512 key 1 msg 0', lambda: hx(baosec.hmac_sha512(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(1)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(0)))), '007071566ae57d52e3bb23ccfe40ed9a222846104409e2fb6429bb63f686960fbba32fd269f5f04c6a023aa8d2e01324264b590f0aa21593097fbcc06c81eb88'),
  ('hmac_sha512 key 1 msg 1', lambda: hx(baosec.hmac_sha512(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(1)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(1)))), '70f6c9c2ef64f683b49ce3090f75c6cbb9775c4661ca36b19df0150bf489e8897ae6a295184a7a9eada70ce682a6bc6aef1a5758067ebeb64e1e637979b06a80'),
  ('hmac_sha512 key 1 msg 64', lambda: hx(baosec.hmac_sha512(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(1)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(64)))), '67a25ddf65ce36f3b2da49cb0b3c32e0bc718e909d49c5ed00fb4f09a1260fd584390f0b057c9cc51d777546484731829b827c48c7822f0cd58d78dc75149856'),
  ('hmac_sha512 key 1 msg 1000', lambda: hx(baosec.hmac_sha512(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(1)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(1000)))), 'bb0dc4c965a6ab3def5081639b12742b44aa8dfcc03cbed597e2261a7ef0a859047c32ef5ce483433ef3dfd9c9260c042e1b9cf67cb765f1c583a1376df66284'),
  ('hmac_sha512 key 20 msg 0', lambda: hx(baosec.hmac_sha512(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(20)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(0)))), '2b8222dfdb86d7eb84d41ae7ded3b9baacad1d9191d656130469cab9fbd8f96c0b97b34e02c0903f093a8c59211b7723051ba906236fa1d47837101db0e7c17b'),
  ('hmac_sha512 key 20 msg 1', lambda: hx(baosec.hmac_sha512(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(20)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(1)))), '2a960f63098dd5d48d5d7ff2a7eb39871027b1fa2757019c83ee740482580078e419f053eb0d72a9a9057a9ad2ae1f08e4b1cfa7d485b37ead84b48c3ec0c979'),
  ('hmac_sha512 key 20 msg 64', lambda: hx(baosec.hmac_sha512(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(20)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(64)))), '39ed37b7c3f1157feaaa6a87879ce5f00722eaed93c2e8aa4b84601e95f41c5626f36fbed4ee32c19cc9dc0f48a13a7a85c5d408c3abdf705d26abf5ef5a5736'),
  ('hmac_sha512 key 20 msg 1000', lambda: hx(baosec.hmac_sha512(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(20)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(1000)))), 'b75e21536ba25ef40057cc0fa4f30f727c9fef07518392d1ac27afbb1a1bf3c0fb9799cd9b97a19e18d3819da06d29d7d5f31a77eda8fb3d3111125e4909ec9b'),
  ('hmac_sha512 key 64 msg 0', lambda: hx(baosec.hmac_sha512(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(64)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(0)))), '89f8e447ce63ec47d950b4841af0c2c413f7f48c4aa9b0e46db1a2ef6031eed6e9a5d970f06638929e75c86c73f51d1808eaa204a113e493b1369394351aa571'),
  ('hmac_sha512 key 64 msg 1', lambda: hx(baosec.hmac_sha512(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(64)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(1)))), '395736cbd7d84c24f1548b1c9afe37da41daba39e80b72ae6e0df7dd4dc02bcb964521304367173bdbfa2d49526a769eb230a939343900aa2c6776ab7685136f'),
  ('hmac_sha512 key 64 msg 64', lambda: hx(baosec.hmac_sha512(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(64)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(64)))), '2886781d88339769aa0bddc2400fb86e97c7a07677f748a3d06421c06d072fa0578c6639555be2be8f97ba9322abfb4a0f0740efd79218fe845cdc11cbb501c6'),
  ('hmac_sha512 key 64 msg 1000', lambda: hx(baosec.hmac_sha512(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(64)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(1000)))), 'da151226764f57eea2b812f91aa4d297e4894a31e28e43a130d1b883732f7f6d7fb2016f37696a626ebcd3e0a78bb4f44061eccfbe8496e0ef797c7b186c270d'),
  ('hmac_sha512 key 65 msg 0', lambda: hx(baosec.hmac_sha512(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(65)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(0)))), 'ce83ce22ffa41086fca31a672e90a133a7fdf8cab307070e75fcc406878b3ff8adec103041837199d1dbc607f9f1597aa1a0dd1c0101303ed3528995b0b7fff7'),
  ('hmac_sha512 key 65 msg 1', lambda: hx(baosec.hmac_sha512(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(65)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(1)))), 'b13c2f1ca257af45d32e1dbaec547bef1563c0e90c8a40da63f51388073f34a9adb943bcc96a6d512a24fc39694d05a6177fb8257d7808e4284b029395e61875'),
  ('hmac_sha512 key 65 msg 64', lambda: hx(baosec.hmac_sha512(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(65)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(64)))), '92800d4034f74964acc17991e525d30ed30bc0aa580214a566328f42b1e42f79780df37b9e58ae7663bfdd706dd1d2ebfe082fe00c5b3f09452699c562598ea0'),
  ('hmac_sha512 key 65 msg 1000', lambda: hx(baosec.hmac_sha512(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(65)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(1000)))), 'ab16337a6df30fc4f182eed405aa30149206d0e210374e42a10d33c88e51a592323ca0c9e01b207069189dda0e3a39b93bcda3978295bbea2b5b0d07b3c9631d'),
  ('hmac_sha512 key 128 msg 0', lambda: hx(baosec.hmac_sha512(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(128)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(0)))), '5316e086156ed344792fdfde1c34e08f169f674738ab6e30dbb7aa53acc407d6fdd21e1d25b0961a283a0a4e422afb1de36cb938b4fe4490e544b753c8280db5'),
  ('hmac_sha512 key 128 msg 1', lambda: hx(baosec.hmac_sha512(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(128)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(1)))), '3713311cd920423e8b41699798f80e53c07ff70b8937e1cfe2b45cf0a211e074dd78474e61b323a3fb7a714ee9e7ce743c1ddee3953e8cbadf0b1d3deeb7046b'),
  ('hmac_sha512 key 128 msg 64', lambda: hx(baosec.hmac_sha512(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(128)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(64)))), '83abd33124be9bb521e4b271b4b91b01355b5725ec61104f5fef9a6c0be9820f0c5a809e7be213394b81a13702558c1e3bd0210a969745256782e251fde11fdb'),
  ('hmac_sha512 key 128 msg 1000', lambda: hx(baosec.hmac_sha512(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(128)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(1000)))), 'b6c8dfabb92b0be63806e0000d51fbc42ffaf72ba5e7cb262cb9e130820853d11c72fef2493e305d032fdf2a191086c32fe0a56c052f34b58be590117e14ec6a'),
  ('hmac_sha512 key 129 msg 0', lambda: hx(baosec.hmac_sha512(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(129)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(0)))), 'd94059214f55794aee01946c57b1eca6eed95fd0bb7ddc3dd5294a980d3368fe37f1a280e4c677da2396b9008134728ef2849bd1226309532b283cbd6fea14d4'),
  ('hmac_sha512 key 129 msg 1', lambda: hx(baosec.hmac_sha512(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(129)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(1)))), '46901b8be6ff38ab401e33abe9f4a182dd3207959afd83f340be0a28e9a4c2c169183083303d9894423019986e0ba394f21f69d295ef9632331f019c83e9bc1f'),
  ('hmac_sha512 key 129 msg 64', lambda: hx(baosec.hmac_sha512(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(129)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(64)))), '5d5d45300fb3dc0980d93564307f162f86dca502aa176408b621a9e8285d33b9aece04e5b8e770f81358416305a7e404dddc352134a01d307305faed65458415'),
  ('hmac_sha512 key 129 msg 1000', lambda: hx(baosec.hmac_sha512(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(129)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(1000)))), '7b8d84f8cfabb0fa71710e327117fb9520e566587d745e02a1ac79c0859b7951b8c21ad5463aa76c980b1d2fae02d57345aa7b97474138b3efdcba7da2cc28fa'),
  ('hmac_sha512 key 200 msg 0', lambda: hx(baosec.hmac_sha512(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(200)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(0)))), '2f2e1a765eed52561db20d2dbddf074ff589814f30984d8c49261d29d490794e5add19be831ae0d8b977cf1c2a2f95fd6058a70e182c142961f3dd35a0212a6f'),
  ('hmac_sha512 key 200 msg 1', lambda: hx(baosec.hmac_sha512(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(200)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(1)))), '3bf7142169bd2782c46c45b2d00288a834d8c8127a722e3a697c6340b699fce47075486316faefdd092cd3f3053ade6fb71f433a84a53c4dd025d76228e9adf5'),
  ('hmac_sha512 key 200 msg 64', lambda: hx(baosec.hmac_sha512(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(200)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(64)))), '4b3a3e6b67aa06447baf5dfa7f0e01ee6ddf49d9bc6f52bf381b623d7ce637b4a45d5240a2c6dfe77df29fba8ad721b260498eb3e5a4fc14445fb994414a0442'),
  ('hmac_sha512 key 200 msg 1000', lambda: hx(baosec.hmac_sha512(bytes(((i * 31 + 5 * 7) & 0xFF) for i in range(200)), bytes(((i * 31 + 6 * 7) & 0xFF) for i in range(1000)))), '3068ebd701babd4d0f28888dbda8187fcfbbd59c03872516ae8bf2a57ac8d17f2738fba53b09f3695964d6714c9e704685a6054203bfa1934dbcf205578b0a0e'),
  ('ECB 128 encrypt', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(16)), 1, None, [bytes(((i * 31 + 12 * 7) & 0xFF) for i in range(16))]), '1b9c5b873166ad72fc6e1b26fbc73378'),
  ('ECB 128 decrypt', lambda: aes('d', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(16)), 1, None, [bytes(((i * 31 + 12 * 7) & 0xFF) for i in range(16))]), 'c7eaa6297f5885d6a9eebf2a4a4a68a3'),
  ('CBC 128 encrypt 16', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(16)), 2, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 14 * 7) & 0xFF) for i in range(16))]), 'd111dfc2e4421c99defc8aefd2a3a80a'),
  ('CBC 128 decrypt 16', lambda: aes('d', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(16)), 2, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 14 * 7) & 0xFF) for i in range(16))]), '3e42989aa3d835c7ecc9dce8d0ed9d55'),
  ('CBC 128 encrypt 48', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(16)), 2, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 14 * 7) & 0xFF) for i in range(48))]), 'd111dfc2e4421c99defc8aefd2a3a80a662881708afd389c9251464f7aa76068184a697a7683ddbba545b2669c302cf4'),
  ('CBC 128 decrypt 48', lambda: aes('d', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(16)), 2, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 14 * 7) & 0xFF) for i in range(48))]), '3e42989aa3d835c7ecc9dce8d0ed9d5530095cd209050c45abcd159135a83f2eb98e3e52d711d8299eda1165c1d17c05'),
  ('CBC 128 encrypt 256', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(16)), 2, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 14 * 7) & 0xFF) for i in range(256))]), 'd111dfc2e4421c99defc8aefd2a3a80a662881708afd389c9251464f7aa76068184a697a7683ddbba545b2669c302cf48bead6b3b7081adaabaf3b85ec2548fdcc9e87fc5f8b47cd4919dcf01a4762d5d5f6261e0b0d3382c097e946853b2657d69c7b719f34dc8cbc073c3659dcd5244fed5c2c1ffbe3adf9188960b3534dc46686a4208482133c46d318d4b570aa3bf7211ba11794ef53c4c6b382c0aa43167bc315051ebbf4eb3bef2f01d3e42076621ab60b996c9ca20dd3e778513957abb681fd29f7b0092151b520389799d136720ed4365e0928615645db21aab6afae4e4937df3b7950272116242a4e194b4d18f694d9ac3b428bbcf653ddbd849658'),
  ('CBC 128 decrypt 256', lambda: aes('d', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(16)), 2, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 14 * 7) & 0xFF) for i in range(256))]), '3e42989aa3d835c7ecc9dce8d0ed9d5530095cd209050c45abcd159135a83f2eb98e3e52d711d8299eda1165c1d17c05ae71eb922e7151d1ddde77ca15ee08ec0edd3a7447ffe9eb1f7489b4f68c2402f5fdabed9e0d534a57f4efa45178f20a41928d6ecf1ae629f345777161e6d6c441d2fb6fb45196d68b0170877cbefa965e03b36a7275c1ce50b6d824a4207bcdc7e7e94917c06168af8e08401bb386c7c6efb088ff87e0b28a85f3b8929d5d73fb66c66b6a387eaccf5464ca3f03d409dfc886134638b5e6e94a5faa27ad9bb52ae4c9767deec6111d7407f091411c5588379c73dee40c476a1c3aaeff0b1297625c3af3e86584cc92f79eb7ba44d833'),
  ('CBC 128 encrypt 272', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(16)), 2, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 14 * 7) & 0xFF) for i in range(272))]), 'd111dfc2e4421c99defc8aefd2a3a80a662881708afd389c9251464f7aa76068184a697a7683ddbba545b2669c302cf48bead6b3b7081adaabaf3b85ec2548fdcc9e87fc5f8b47cd4919dcf01a4762d5d5f6261e0b0d3382c097e946853b2657d69c7b719f34dc8cbc073c3659dcd5244fed5c2c1ffbe3adf9188960b3534dc46686a4208482133c46d318d4b570aa3bf7211ba11794ef53c4c6b382c0aa43167bc315051ebbf4eb3bef2f01d3e42076621ab60b996c9ca20dd3e778513957abb681fd29f7b0092151b520389799d136720ed4365e0928615645db21aab6afae4e4937df3b7950272116242a4e194b4d18f694d9ac3b428bbcf653ddbd849658bc8770b8607a8d84e3dab814ef6ef014'),
  ('CBC 128 decrypt 272', lambda: aes('d', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(16)), 2, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 14 * 7) & 0xFF) for i in range(272))]), '3e42989aa3d835c7ecc9dce8d0ed9d5530095cd209050c45abcd159135a83f2eb98e3e52d711d8299eda1165c1d17c05ae71eb922e7151d1ddde77ca15ee08ec0edd3a7447ffe9eb1f7489b4f68c2402f5fdabed9e0d534a57f4efa45178f20a41928d6ecf1ae629f345777161e6d6c441d2fb6fb45196d68b0170877cbefa965e03b36a7275c1ce50b6d824a4207bcdc7e7e94917c06168af8e08401bb386c7c6efb088ff87e0b28a85f3b8929d5d73fb66c66b6a387eaccf5464ca3f03d409dfc886134638b5e6e94a5faa27ad9bb52ae4c9767deec6111d7407f091411c5588379c73dee40c476a1c3aaeff0b1297625c3af3e86584cc92f79eb7ba44d83317a9b1ed9a230cb8d532e59ff906b43a'),
  ('CBC 128 encrypt 1024', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(16)), 2, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 14 * 7) & 0xFF) for i in range(1024))]), 'd111dfc2e4421c99defc8aefd2a3a80a662881708afd389c9251464f7aa76068184a697a7683ddbba545b2669c302cf48bead6b3b7081adaabaf3b85ec2548fdcc9e87fc5f8b47cd4919dcf01a4762d5d5f6261e0b0d3382c097e946853b2657d69c7b719f34dc8cbc073c3659dcd5244fed5c2c1ffbe3adf9188960b3534dc46686a4208482133c46d318d4b570aa3bf7211ba11794ef53c4c6b382c0aa43167bc315051ebbf4eb3bef2f01d3e42076621ab60b996c9ca20dd3e778513957abb681fd29f7b0092151b520389799d136720ed4365e0928615645db21aab6afae4e4937df3b7950272116242a4e194b4d18f694d9ac3b428bbcf653ddbd849658bc8770b8607a8d84e3dab814ef6ef014dbbe8e1b24f36a1cba2ccb85fcf509713b1ec388521182906217703fbdb595f8f9f00afc5c40605e05db4a27ba62e47a76bd97ba23d4c6fabcefce5b31884bdea153c57e75bde6c4305f6026b63576a75111eac7979c3da0846f67491dbb66280f25f828f6caa9c89ca42398f850a99beb283e74f40fe693874e932ef2a30b43d703399f4191d66c7a88b2710d8416cc970d8e37b8d2ca66ee63c8c3a24bf57a5299fec2e89c3ba2dd6f68b5961b7b5fe9194387e13088b1278f7f323c31e399ef921f2c1e7dcb098b1067d26f59671a4be9890ae67bc00066ece7c2a1d7b0c95d34b8badc3d5d349d1330323f55e7ab5a030623ee4b4e25c2f700362ac44aca607f5bbffa1979048c181d1691792038439b1f63f46ec0da1c4f2c4c5cbac28d63cbdbb45cf408668c7b2b66a432cbc979be142c7e23225830ed20ebd5661cd1e480eed48bd6287a90c937e695f347e1a1cb670e4dbdd3449a2fdcd8aa5b901553dc6c00b70b2704d1de2f32b3c208513052bc22dc340975f3e8d5d843501eb61f0e26b8a6f8103c78d646767b39e5339c0e990413851554ff6bcf42a6707d16b1a46a0d2b36ffc6b43a76b63ce838d3af8b1f05190d4ad02869405455e34a12bc7ede52202e3ecd80c516cca0d65571e572003d0e4f9ab87c23eaa11785d346eb8ed111155c4f2c4592d9692345e308a1667b908cdcdd037e3934af9b0e10cd21d59fe2074406c758fce75a817483604e09ee66d97efcf8b29a62064c88fbf40c3362223b1d53598df6f672328d6f91d93058c969a360fa27ec5e876129922403d2a4d770b2600849e20395266c786ba6928c93e2adeaf54fdf74c5357820588d78473d72349b492eed60ed440ae202da210cc393d4548cc1c60315416f4bcb3d90be8fdf21a48acdf7e2a4216b3f005ca1f3889414dfb4b8d5c24687711c335c37ee432a31174cee4261adc1b18bab51cfbd64ea6e8391656ff5615fe8ab5206495cbe1f1e8cb44d67a9737bcb1be5d9f3206b95b210869f1b477b264fce928226d784c42fcfa09b23b2da43865616'),
  ('CBC 128 decrypt 1024', lambda: aes('d', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(16)), 2, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 14 * 7) & 0xFF) for i in range(1024))]), '3e42989aa3d835c7ecc9dce8d0ed9d5530095cd209050c45abcd159135a83f2eb98e3e52d711d8299eda1165c1d17c05ae71eb922e7151d1ddde77ca15ee08ec0edd3a7447ffe9eb1f7489b4f68c2402f5fdabed9e0d534a57f4efa45178f20a41928d6ecf1ae629f345777161e6d6c441d2fb6fb45196d68b0170877cbefa965e03b36a7275c1ce50b6d824a4207bcdc7e7e94917c06168af8e08401bb386c7c6efb088ff87e0b28a85f3b8929d5d73fb66c66b6a387eaccf5464ca3f03d409dfc886134638b5e6e94a5faa27ad9bb52ae4c9767deec6111d7407f091411c5588379c73dee40c476a1c3aaeff0b1297625c3af3e86584cc92f79eb7ba44d83317a9b1ed9a230cb8d532e59ff906b43a30095cd209050c45abcd159135a83f2eb98e3e52d711d8299eda1165c1d17c05ae71eb922e7151d1ddde77ca15ee08ec0edd3a7447ffe9eb1f7489b4f68c2402f5fdabed9e0d534a57f4efa45178f20a41928d6ecf1ae629f345777161e6d6c441d2fb6fb45196d68b0170877cbefa965e03b36a7275c1ce50b6d824a4207bcdc7e7e94917c06168af8e08401bb386c7c6efb088ff87e0b28a85f3b8929d5d73fb66c66b6a387eaccf5464ca3f03d409dfc886134638b5e6e94a5faa27ad9bb52ae4c9767deec6111d7407f091411c5588379c73dee40c476a1c3aaeff0b1297625c3af3e86584cc92f79eb7ba44d83317a9b1ed9a230cb8d532e59ff906b43a30095cd209050c45abcd159135a83f2eb98e3e52d711d8299eda1165c1d17c05ae71eb922e7151d1ddde77ca15ee08ec0edd3a7447ffe9eb1f7489b4f68c2402f5fdabed9e0d534a57f4efa45178f20a41928d6ecf1ae629f345777161e6d6c441d2fb6fb45196d68b0170877cbefa965e03b36a7275c1ce50b6d824a4207bcdc7e7e94917c06168af8e08401bb386c7c6efb088ff87e0b28a85f3b8929d5d73fb66c66b6a387eaccf5464ca3f03d409dfc886134638b5e6e94a5faa27ad9bb52ae4c9767deec6111d7407f091411c5588379c73dee40c476a1c3aaeff0b1297625c3af3e86584cc92f79eb7ba44d83317a9b1ed9a230cb8d532e59ff906b43a30095cd209050c45abcd159135a83f2eb98e3e52d711d8299eda1165c1d17c05ae71eb922e7151d1ddde77ca15ee08ec0edd3a7447ffe9eb1f7489b4f68c2402f5fdabed9e0d534a57f4efa45178f20a41928d6ecf1ae629f345777161e6d6c441d2fb6fb45196d68b0170877cbefa965e03b36a7275c1ce50b6d824a4207bcdc7e7e94917c06168af8e08401bb386c7c6efb088ff87e0b28a85f3b8929d5d73fb66c66b6a387eaccf5464ca3f03d409dfc886134638b5e6e94a5faa27ad9bb52ae4c9767deec6111d7407f091411c5588379c73dee40c476a1c3aaeff0b1297625c3af3e86584cc92f79eb7ba44d833'),
  ('CBC 128 encrypt in 3 calls', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(16)), 2, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 15 * 7) & 0xFF) for i in range(96))[:32], bytes(((i * 31 + 15 * 7) & 0xFF) for i in range(96))[32:48], bytes(((i * 31 + 15 * 7) & 0xFF) for i in range(96))[48:]]), 'c6abd2dee8bab465f7fdcea2ac16b19238d4df06596cff28a9e00f017651635aba7d29e8b1505ad771b71c4560b2d81583e51fb196f87bfc8083400004885d8b2be8b5e697bf71be19c9efd5de50dfc6babfa949913d37b96299c08727acb00e'),
  ('CBC 128 decrypt in 3 calls', lambda: aes('d', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(16)), 2, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [unhx('c6abd2dee8bab465f7fdcea2ac16b19238d4df06596cff28a9e00f017651635a'), unhx('ba7d29e8b1505ad771b71c4560b2d815'), unhx('83e51fb196f87bfc8083400004885d8b2be8b5e697bf71be19c9efd5de50dfc6babfa949913d37b96299c08727acb00e')]), '6988a7c6e504234261809fbeddfc1b3a597897b6d5f4133251708faecdec0b2a496887a6c5e4032241607f9ebddcfb1a39587796b5d4f31231506f8eadcceb0a29486786a5c4e30221405f7e9dbcdbfa1938577695b4d3f211304f6e8daccbea'),
  ('CTR 128 lengths 1', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(16)), 6, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 16 * 7) & 0xFF) for i in range(1))]), '13'),
  ('CTR 128 lengths 16', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(16)), 6, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 16 * 7) & 0xFF) for i in range(16))]), '13a13d614b0ee7b00a0b644e8e0bcb4a'),
  ('CTR 128 lengths 17', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(16)), 6, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 16 * 7) & 0xFF) for i in range(17))]), '13a13d614b0ee7b00a0b644e8e0bcb4aeb'),
  ('CTR 128 lengths 300', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(16)), 6, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 16 * 7) & 0xFF) for i in range(300))]), '13a13d614b0ee7b00a0b644e8e0bcb4aeb1ba9f0ccb1b17dc830cf09c027f01ddbb28ae7d8f3e29d3a16c63f0afc1f77826b3e92a6f843c7a994d0d4fe04924ead3f030115aba32eb9d098c0cc3fafe7c11aae5dab6daecbbf523164b2b95a1b680c985e21ea242408d9509e54fc0c0479cea48efb38c1bc92cd89b2b1b5e1d4a58e2aaa56834190f0141c4b315b0f38cdb0e3b833ef3502d70842fa4fe8a8570afe341c3e34b530a7f28e4059eb8f64166ff47443924de062a978cd983c733a95c6b264974a23dab46fafdc9ac857d4c80e6d4696a1dbff4bcf26288427e92567c346f05801c9ffd9fffe17ae99edc24fb0b046a863c0d2a3b6ffa77316cc4d5baa43f2d922457570d267ec00075b5acc2288368233507345f97de308308131cae6ee96d205aac241083cf8'),
  ('CTR 128 lengths 5+16+33+256+257', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(16)), 6, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 16 * 7) & 0xFF) for i in range(5)), bytes(((i * 31 + 16 * 7) & 0xFF) for i in range(16)), bytes(((i * 31 + 16 * 7) & 0xFF) for i in range(33)), bytes(((i * 31 + 16 * 7) & 0xFF) for i in range(256)), bytes(((i * 31 + 16 * 7) & 0xFF) for i in range(257))]), '13a13d614bfbeb9980fc41810df8c0ff79f0d7c06dfb52aa87f813c2fd1af6e65f2a1c3f17a24bdeb2c6d8a3e7c9b430f49e24726ecd91aa5eeddbdd5e7bcfe2c1d4c209aaab185c488e71baf4f45889804e04acdcd429be147e4b48714c22bd394201c5512415de7a7a86d3114020444c9be10b5fe81d009308c35f45b227b8324abf58d8e7fa2e644ceee4e5607722de10893bdf34c69f4404f362fd90d259c8bd28ccc34a25166234c79af38ae4bf7f8cca18878498be9df6e6112b4f3b7fd698f4971995179396200851192f89af2ec7fec93d121fc000b61813702213c64f57c3667cbdebfa1322097215a5a082373cd0570b8a1c92f886728320c3b5490d53f880f1813a36bec602d5fa9291d86ca89230ee88ce173606f1798bf2ca15fc6d192e617c995326a6c239e627b0a2a15ea742e826eaa8ef8f9a0b05339cf3981627c178b9b302b386a0d681f5ec227d8cecac982929b6691a01a2c2bccc1a519e31e268d0fce10debbbf992decefd32f056d935e36850393da938b0f9ec607a0050d76fba83c0a6076d7bfd496d258bbaad7eb701c28776c8a650d20cf3b3d36019d591c608a0172c62c2dc847dfc693ead132acf4cc42ea0dd101f8f4f59b22dca606cfb6b42d782a25015a986ae0ad0672c04e5995f470aaf84fb10e3bc15f96987b2dc560ddee0f2d39462cb54d8bef39786e082bcdf95109769700ba247e5e5d72dd489d20d0980742a67a1dbe04e8363dee46ea94fc52f01e1c41c5724349219065df81e7691010b834f450b967d4a0bf33f7d'),
  ('CTR 128 lengths 1000', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(16)), 6, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 16 * 7) & 0xFF) for i in range(1000))]), '13a13d614b0ee7b00a0b644e8e0bcb4aeb1ba9f0ccb1b17dc830cf09c027f01ddbb28ae7d8f3e29d3a16c63f0afc1f77826b3e92a6f843c7a994d0d4fe04924ead3f030115aba32eb9d098c0cc3fafe7c11aae5dab6daecbbf523164b2b95a1b680c985e21ea242408d9509e54fc0c0479cea48efb38c1bc92cd89b2b1b5e1d4a58e2aaa56834190f0141c4b315b0f38cdb0e3b833ef3502d70842fa4fe8a8570afe341c3e34b530a7f28e4059eb8f64166ff47443924de062a978cd983c733a95c6b264974a23dab46fafdc9ac857d4c80e6d4696a1dbff4bcf26288427e92567c346f05801c9ffd9fffe17ae99edc24fb0b046a863c0d2a3b6ffa77316cc4d5baa43f2d922457570d267ec00075b5acc2288368233507345f97de308308131cae6ee96d205aac241083cf842e0bed81ee7867641893b827ae54c1da9ded10c2983f6f692e93677e072710ef7923876ba181f3feabbf583ec4368a657718809c3526356f0865125bc72ad5cbcfc48f979c6d9eab1d2724c7c6ae16e8192d8204cb15d3b6ba9c20e1ead622086896533b8e0498d5988c0491cd00ab0a0671f0a7310f657bdabad19bdf5dbea7daee7511277c6b816a0627c43436310a92521b6b870c77c32120cd42d2cb96efdc3fa9f1c74de10ada0ef3f3fe9429dbad09c4b1b120752f200c579d6feda00377cd435c92ff7fa1ff44be053cca509d9f7022ce65d8e302283c4b21b04886e23c7d630520caf25e02719c0fb12375515675d6479025d5950a47a37710bb01e53b38eb4be59ffb59ff151b4aca7944422e9b62d48cea6c151db531f15db462d1adb236f2dddd318e2f04b22d233873c5f5b5165011114477437b35c5e816c78a1e40c4c376aac39844ff0066d52632b2aac9b673ba5f5c2616fcc86776e5aec5ce78484d1dcf7fe83eb50c6541c4933767891e8efdca81d0d3a50c79da518d6cb0067a460fe761caab05d43ce04188d3cf20a4114dcd42e5f9a9a02e93c0dc532173230ff441ebccd84e1f4c58e36592b09ef34978b8198c7d1b40e7a83c9aa19f760963700353d6aa1e3a871bf8bbb12bc11bbfbb9283d89aa5774dfad200031e14bd7be41b54245908de9cd8b4b83526e2a262ed3af685aef8c450a12692d83423dbcb9645fcd48a0eb4773c8fff16e8a0153f5fb874024ab52af10239974cf7af6818fa3099dc31d2a6e3f67f7cc11adfe9efe9f059da98c7880d2cfcf713d42e7fa5574f6810333380b039e92b40cb975ba88c0606e8e377cdd5e9cc59416cbda1a4281122ac513157c1cf5a95b3fdf13c1b56d9f46baa583f55fd14fdc387570816d99e4ebc9625dab673ba935fc835d286268df5f0e1e51b0d27f7743ba4a270246f2e4f2cb4cb5d927ab9b045f0eeef8934f5b2483179a0b'),
  ('CTR 128 low word wraps', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(16)), 6, unhx('000000000000000000000000fffffffe'), [bytes(((i * 31 + 17 * 7) & 0xFF) for i in range(100))]), '97b92829093c01eadda4688c341fe09b92f6fef5fe9f8e860a15518450c25163f38978ce0065b65e51759f3eb0435a7982d253e3a353782013106b79d2d607ed74cd921eb093e2d7ba7e998bd9f8b2c739be25b58e90473dfe3e94bd4a5f331fbfe6b3e3'),
  ('CTR 128 whole counter wraps', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(16)), 6, unhx('fffffffffffffffffffffffffffffffd'), [bytes(((i * 31 + 17 * 7) & 0xFF) for i in range(100))]), 'c68f0ce6076fb3a3f911ed36a320f9eaf104306958f6decdcfb623267ba472ef8873771233bd45b349038b3a180041b7af53bd4a8bb91574994fa3239b444e8bafd5f68b4a06b2dcb58ae28e34f1a0848398c440edc9c14c80e1ff9b4586f41ac752f0a5'),
  ('CTR 128 carry through 8 bytes', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(16)), 6, unhx('0101010101010101fffffffffffffffe'), [bytes(((i * 31 + 17 * 7) & 0xFF) for i in range(100))]), 'dd90d638b91d17ea8f9617821cc46028de588677ff3fc8d106b14b7ac7945704b1dea68fbe3381f45b9ab8cf3653a46c7f904b143bd84bd412e1edd802b3e283b6a018ef2e42ac7de18231fd4cad2e124ff07ac43672764d91b6eebe23c470964f8a1dc8'),
  ('ECB 192 encrypt', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(24)), 1, None, [bytes(((i * 31 + 12 * 7) & 0xFF) for i in range(16))]), 'c71fd827bfdc530a57e5394a277f0af3'),
  ('ECB 192 decrypt', lambda: aes('d', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(24)), 1, None, [bytes(((i * 31 + 12 * 7) & 0xFF) for i in range(16))]), '06a9279a39553d67cae43c7b357e3105'),
  ('CBC 192 encrypt 16', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(24)), 2, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 14 * 7) & 0xFF) for i in range(16))]), 'c5d790db7eb8e995a437030698dbee31'),
  ('CBC 192 decrypt 16', lambda: aes('d', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(24)), 2, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 14 * 7) & 0xFF) for i in range(16))]), '8a747ca037dcae6898a7785997a9d9da'),
  ('CBC 192 encrypt 48', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(24)), 2, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 14 * 7) & 0xFF) for i in range(48))]), 'c5d790db7eb8e995a437030698dbee313d2e7641e0c90dfc4345d5978348f681f2121d2f281a0ff3659ddb0b2ec97889'),
  ('CBC 192 decrypt 48', lambda: aes('d', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(24)), 2, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 14 * 7) & 0xFF) for i in range(48))]), '8a747ca037dcae6898a7785997a9d9da8107226e2b32a9610e5b618b247bb563b85d155d554ac11bd50b3bae5668f0a0'),
  ('CBC 192 encrypt 256', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(24)), 2, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 14 * 7) & 0xFF) for i in range(256))]), 'c5d790db7eb8e995a437030698dbee313d2e7641e0c90dfc4345d5978348f681f2121d2f281a0ff3659ddb0b2ec97889d6f6445a05e4d02517a74b4855bc75cf34126c2273a94dd1903f3ae712e790b62010cd9c24b4b51aefedaef0c90e03b244bd4ce1da3937b5c39118c431bc2b64931d3852ff2893b7e5f32eeec90e16262f6c146c9046ee2b6809f0c16d032083257e3d6c32826c9aa4337ee1c0123c7858589123d0e8efec56cbf082f3494d9d1274a6c566f16faf04a5fd41c5ef4e00c4a9323b7b4b3c691ada80730ec4ff7212c94fddde2184889a08efd80ade8b90097fedc35cb967736c966be656fb4a4d6746accdd9f8f75dc39659e35719f4f3'),
  ('CBC 192 decrypt 256', lambda: aes('d', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(24)), 2, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 14 * 7) & 0xFF) for i in range(256))]), '8a747ca037dcae6898a7785997a9d9da8107226e2b32a9610e5b618b247bb563b85d155d554ac11bd50b3bae5668f0a0939068d3a2489b8b88dae001ba5b499c7af28978685fe5422417092a6c534a5540b5dd720b2d3e14c8603a2a8f7769634da7c8e7e4002f6178ce5015b92b3add140b6c3e91f4153a9caa17b044557023a481930e04b5aad6f8e932ad0bba0d5af1a3eb84713fee5154b994e10b7611c3217154826ae9a203f7bd4324e11d3626b575df66925bb099740982da52a3960769313938371c4691b51dc4a6f08f194447f2837013f554662db47c62fe9663874c407ca2a50df4f9de72f07435763c2ea0c7d3cce4bdaad57325623b15440cba'),
  ('CBC 192 encrypt 272', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(24)), 2, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 14 * 7) & 0xFF) for i in range(272))]), 'c5d790db7eb8e995a437030698dbee313d2e7641e0c90dfc4345d5978348f681f2121d2f281a0ff3659ddb0b2ec97889d6f6445a05e4d02517a74b4855bc75cf34126c2273a94dd1903f3ae712e790b62010cd9c24b4b51aefedaef0c90e03b244bd4ce1da3937b5c39118c431bc2b64931d3852ff2893b7e5f32eeec90e16262f6c146c9046ee2b6809f0c16d032083257e3d6c32826c9aa4337ee1c0123c7858589123d0e8efec56cbf082f3494d9d1274a6c566f16faf04a5fd41c5ef4e00c4a9323b7b4b3c691ada80730ec4ff7212c94fddde2184889a08efd80ade8b90097fedc35cb967736c966be656fb4a4d6746accdd9f8f75dc39659e35719f4f3af832cfc4b492eaea5206eb2cdb541b0'),
  ('CBC 192 decrypt 272', lambda: aes('d', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(24)), 2, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 14 * 7) & 0xFF) for i in range(272))]), '8a747ca037dcae6898a7785997a9d9da8107226e2b32a9610e5b618b247bb563b85d155d554ac11bd50b3bae5668f0a0939068d3a2489b8b88dae001ba5b499c7af28978685fe5422417092a6c534a5540b5dd720b2d3e14c8603a2a8f7769634da7c8e7e4002f6178ce5015b92b3add140b6c3e91f4153a9caa17b044557023a481930e04b5aad6f8e932ad0bba0d5af1a3eb84713fee5154b994e10b7611c3217154826ae9a203f7bd4324e11d3626b575df66925bb099740982da52a3960769313938371c4691b51dc4a6f08f194447f2837013f554662db47c62fe9663874c407ca2a50df4f9de72f07435763c2ea0c7d3cce4bdaad57325623b15440cbaa39f55d70e279717a15c412ebe42f0b5'),
  ('CBC 192 encrypt 1024', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(24)), 2, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 14 * 7) & 0xFF) for i in range(1024))]), 'c5d790db7eb8e995a437030698dbee313d2e7641e0c90dfc4345d5978348f681f2121d2f281a0ff3659ddb0b2ec97889d6f6445a05e4d02517a74b4855bc75cf34126c2273a94dd1903f3ae712e790b62010cd9c24b4b51aefedaef0c90e03b244bd4ce1da3937b5c39118c431bc2b64931d3852ff2893b7e5f32eeec90e16262f6c146c9046ee2b6809f0c16d032083257e3d6c32826c9aa4337ee1c0123c7858589123d0e8efec56cbf082f3494d9d1274a6c566f16faf04a5fd41c5ef4e00c4a9323b7b4b3c691ada80730ec4ff7212c94fddde2184889a08efd80ade8b90097fedc35cb967736c966be656fb4a4d6746accdd9f8f75dc39659e35719f4f3af832cfc4b492eaea5206eb2cdb541b0b589586186333a43a6a7ca1a0cc1a56999d65986b4b29cc35e432f49efd42f5d33a53d01562a35aca6d2e13a5b8431f89c268d39a083319f3925703f304d69bbbe2516cdba2d045995de99f54ec92690b3deab04dc9d5cd56f74204bd74b3fc7ec8b2780f149dc8e7395a4215bcde3e7019fb013d1e57a2a989e6bee030239233960cfdd9ef42dd1ca344eae54eb086d7711106f114c9a8fa1a436c608eabcab6dd25f7ad629d469bf7ce21c93ff7ec3330f83db021327a173764199985040674f47d5a09d330607cf7539ca5c6bd4c1cb3a3b5f2389d7734f43087999292626e391448f747bf166d8ae75744d16b6f6e3d6e736c7f7d617f89f5b3947fb6e6e77d475a01f061fd1078ffe88dc1a2ef3b6cf5be7f0b9908e9a82c7532f9b52a8f535f13792a111797cbbf4dec75b2a2d63825aa427f619f04a1c2f2c08eeaac83024732f6e6b330fcdab522c52ff4e24e5cf963a0c2447318df516e5ddf38a22896be5a96670085b6edcce3c9b3d9827916fc7c67d54b341fb7f78541bf707dac82fa50adc38eab6cc964c3a26aaa277c001b4fa62a0ca1e31cfbe46b25866c3c9707170778889e958fbf93de7a22c79166ef279f8400f794880c37274cfc8563256a59776a25e8c9fd72c5423f31ff27c4ed9f8d7a5f5ea9e7d5fb41fb3ce5623d67882d2b853c17cc99436cb46e1605a87bedeab5d9b921f74884730f63d98cb1aa0fc7df0671f5ea579f7e7f2f21b9c86a99b5a3a26204b9734d20f4ad15fb23f30c7c3369ce0f1e60a5defc05ec93b1ae4d18ef54cf43085aea01dbe15859823a97a6c3e9f6f739c14d24371cf042050e3415883b33ff5f537925702f42966588eb09c8ffad55aa9cb4d5339cdd7e0548a2783b3abb88552d4cbcadd63ec2b0185c250b2fe55edb3809f1bf01f1337e8f390c5bc993e28f95c0c63644dd0ab100bc7be251aaefce47f0ea998ae39ff96cca097437dbfe06e80e8ce23de56da6a8f8febce292051bf06a775de5f48eef0d40d8a5488f3fa90bb8584ab00e64c1f6772cf5c4a6df0d5c748c010e568'),
  ('CBC 192 decrypt 1024', lambda: aes('d', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(24)), 2, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 14 * 7) & 0xFF) for i in range(1024))]), '8a747ca037dcae6898a7785997a9d9da8107226e2b32a9610e5b618b247bb563b85d155d554ac11bd50b3bae5668f0a0939068d3a2489b8b88dae001ba5b499c7af28978685fe5422417092a6c534a5540b5dd720b2d3e14c8603a2a8f7769634da7c8e7e4002f6178ce5015b92b3add140b6c3e91f4153a9caa17b044557023a481930e04b5aad6f8e932ad0bba0d5af1a3eb84713fee5154b994e10b7611c3217154826ae9a203f7bd4324e11d3626b575df66925bb099740982da52a3960769313938371c4691b51dc4a6f08f194447f2837013f554662db47c62fe9663874c407ca2a50df4f9de72f07435763c2ea0c7d3cce4bdaad57325623b15440cbaa39f55d70e279717a15c412ebe42f0b58107226e2b32a9610e5b618b247bb563b85d155d554ac11bd50b3bae5668f0a0939068d3a2489b8b88dae001ba5b499c7af28978685fe5422417092a6c534a5540b5dd720b2d3e14c8603a2a8f7769634da7c8e7e4002f6178ce5015b92b3add140b6c3e91f4153a9caa17b044557023a481930e04b5aad6f8e932ad0bba0d5af1a3eb84713fee5154b994e10b7611c3217154826ae9a203f7bd4324e11d3626b575df66925bb099740982da52a3960769313938371c4691b51dc4a6f08f194447f2837013f554662db47c62fe9663874c407ca2a50df4f9de72f07435763c2ea0c7d3cce4bdaad57325623b15440cbaa39f55d70e279717a15c412ebe42f0b58107226e2b32a9610e5b618b247bb563b85d155d554ac11bd50b3bae5668f0a0939068d3a2489b8b88dae001ba5b499c7af28978685fe5422417092a6c534a5540b5dd720b2d3e14c8603a2a8f7769634da7c8e7e4002f6178ce5015b92b3add140b6c3e91f4153a9caa17b044557023a481930e04b5aad6f8e932ad0bba0d5af1a3eb84713fee5154b994e10b7611c3217154826ae9a203f7bd4324e11d3626b575df66925bb099740982da52a3960769313938371c4691b51dc4a6f08f194447f2837013f554662db47c62fe9663874c407ca2a50df4f9de72f07435763c2ea0c7d3cce4bdaad57325623b15440cbaa39f55d70e279717a15c412ebe42f0b58107226e2b32a9610e5b618b247bb563b85d155d554ac11bd50b3bae5668f0a0939068d3a2489b8b88dae001ba5b499c7af28978685fe5422417092a6c534a5540b5dd720b2d3e14c8603a2a8f7769634da7c8e7e4002f6178ce5015b92b3add140b6c3e91f4153a9caa17b044557023a481930e04b5aad6f8e932ad0bba0d5af1a3eb84713fee5154b994e10b7611c3217154826ae9a203f7bd4324e11d3626b575df66925bb099740982da52a3960769313938371c4691b51dc4a6f08f194447f2837013f554662db47c62fe9663874c407ca2a50df4f9de72f07435763c2ea0c7d3cce4bdaad57325623b15440cba'),
  ('CBC 192 encrypt in 3 calls', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(24)), 2, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 15 * 7) & 0xFF) for i in range(96))[:32], bytes(((i * 31 + 15 * 7) & 0xFF) for i in range(96))[32:48], bytes(((i * 31 + 15 * 7) & 0xFF) for i in range(96))[48:]]), 'be84a081fb3c38a38247b07dcb988b505837f5c300572b58b3c03a56900001d595c68350dda19a6ab303d398531691480b0ac08a5efbfb8761cf7ef2d5bded3b7093e61e00725a159b6dbe4e57a3b4534eed5826146167f6650faa3c56e9be0e'),
  ('CBC 192 decrypt in 3 calls', lambda: aes('d', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(24)), 2, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [unhx('be84a081fb3c38a38247b07dcb988b505837f5c300572b58b3c03a56900001d5'), unhx('95c68350dda19a6ab303d39853169148'), unhx('0b0ac08a5efbfb8761cf7ef2d5bded3b7093e61e00725a159b6dbe4e57a3b4534eed5826146167f6650faa3c56e9be0e')]), '6988a7c6e504234261809fbeddfc1b3a597897b6d5f4133251708faecdec0b2a496887a6c5e4032241607f9ebddcfb1a39587796b5d4f31231506f8eadcceb0a29486786a5c4e30221405f7e9dbcdbfa1938577695b4d3f211304f6e8daccbea'),
  ('CTR 192 lengths 1', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(24)), 6, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 16 * 7) & 0xFF) for i in range(1))]), 'b5'),
  ('CTR 192 lengths 16', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(24)), 6, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 16 * 7) & 0xFF) for i in range(16))]), 'b510d7b647a2b125cf295425e27b0707'),
  ('CTR 192 lengths 17', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(24)), 6, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 16 * 7) & 0xFF) for i in range(17))]), 'b510d7b647a2b125cf295425e27b070772'),
  ('CTR 192 lengths 300', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(24)), 6, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 16 * 7) & 0xFF) for i in range(300))]), 'b510d7b647a2b125cf295425e27b07077296f8b964a3ba8648b4fbe408ba3ae4dd690d9b6ad2fca95533476c580c475acbe8ca22041769ec1ab2faa053df44eb95afa4dcd2a73eb939f942f0788722335d4749847421e74e8d57b3e7817e472c9d56501bee13cf97a22c893657829c72c7e13e6f524b37074a029c0b569d8ea74e59925ac71d955791904e53948326c42e385514d273a7abcb0b35044ddf572dd32609099c80af01391b3a1f2410bf37e8c840e168f4cded9ad482de7e3e73e0af2a0475d5afb8c8f24ba0d0d4e501e38ec03a804e3bfd245136b07b15c6131659df7782a7b22397c2a4a1b66b7d6c664362c8de755afdca7c902b406f71af761b2abe0c44b829622ac1548050e85ccbf127d62bdea9cfc3b09b27401559fcfcef0e53a2e6755b8d9badcd4f'),
  ('CTR 192 lengths 5+16+33+256+257', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(24)), 6, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 16 * 7) & 0xFF) for i in range(5)), bytes(((i * 31 + 16 * 7) & 0xFF) for i in range(16)), bytes(((i * 31 + 16 * 7) & 0xFF) for i in range(33)), bytes(((i * 31 + 16 * 7) & 0xFF) for i in range(256)), bytes(((i * 31 + 16 * 7) & 0xFF) for i in range(257))]), 'b510d7b6476266c8c954538af67844cb94384a0a94fd892dfb4a32dcc975d3670c78ec673aebc82a02643789cc7a921a8033ffa4cbf50df7b934049117fefde74357f1ceb79ced0680cbbe431f47f27c59e607d24ca297918e9fe23b87f7fa722cfbe6ed3e57fe09c28a174dc58741c01e8344d37614fe8825a422c3d71b3bbb45b4bd6f279d23f659594c50ff51e9cb6a4ff4c0ef673838f091d8047d9d2a2432aececec3901ffad425857f6898a29b70808435d1b3de70ca303e8b0d94218640cb6576e3a6298fa752f7e2f34792f471663b2dbcb61312782ec52a4d3acce09bb0df011f86ab7aeedc94e879b2fa91045080b80c1b2197a69b2e19bf73402b57f0e5e98c4c1fde03f236a50bdd4b7d9d1fcc2eaff8bee80c4c808da6f67163da4d550f02c2ecbd4cb19dfd46daa1062269282a053f963528c9905d1b9abbfa800d89b2856745fd959c1170ac7b31c37932a03ed0df9e7a8519547d57cf67cedbb3fc2a69c0d81b01b7b478cd22bc04e44120352f5137a903ca5de9a0397b9ce1fa6935712308fc52110ae50dfa6e7dfd7e21fa69b78000dfb1537d5e637f73aff363544047dd8acd3c58af512bbe6f839d3954ccee66b60070111f2575972537cb3f9cd616a2f2927242dc7be43d01e5fe8d526e6a5dfff8b1ff6077b4a1fbedafc589d736193d4a20c5cf9158f9dedb3c95ed7c1780a96791ee4849aeca12144532830620fb407d2bba56eb9b7bf2ab159f68bee5b775bbf1d35b4a86325b1e6f6695eb2b4aeaa2ac477f418b1a4c76241217a92414'),
  ('CTR 192 lengths 1000', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(24)), 6, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 16 * 7) & 0xFF) for i in range(1000))]), 'b510d7b647a2b125cf295425e27b07077296f8b964a3ba8648b4fbe408ba3ae4dd690d9b6ad2fca95533476c580c475acbe8ca22041769ec1ab2faa053df44eb95afa4dcd2a73eb939f942f0788722335d4749847421e74e8d57b3e7817e472c9d56501bee13cf97a22c893657829c72c7e13e6f524b37074a029c0b569d8ea74e59925ac71d955791904e53948326c42e385514d273a7abcb0b35044ddf572dd32609099c80af01391b3a1f2410bf37e8c840e168f4cded9ad482de7e3e73e0af2a0475d5afb8c8f24ba0d0d4e501e38ec03a804e3bfd245136b07b15c6131659df7782a7b22397c2a4a1b66b7d6c664362c8de755afdca7c902b406f71af761b2abe0c44b829622ac1548050e85ccbf127d62bdea9cfc3b09b27401559fcfcef0e53a2e6755b8d9badcd4f1cfeffa86e18bc3c307d1686c1936a3de5ffb2b25c6d9ce1cd2d968af1d6f23978fad56fc685d879e0edeb2acb4a70bdf90275d735ad454c41207cab6193a9e2f06e000fce0a35e9e40de73fd7be6b434c5ad930684b516764289df26c54b491f0657f81e719737aad59d0898b2c914a99850193f82c0241da355daabeadad2ef12a39e750f06fc1e38dee13cf831f83d3a4f0376d5a1d6c087f817beebf53cd69841cbe3606f0c061afd5c5e795c77b4f2c26a6d2a242a2128cab346d51352edd02beba0d8f48414f10c744118b5d5f75f967c6a96d1af0159fc188298e8bec45bd2cc7501917211ef8391e3aa264f5c23376900b902d7b6a86bbcbab22fb454fb8eeb567850b8163abfaf682abae1fd6655b5bfa3a72fc17af91db4a9ca67442c7797444713a9f20699f7da8b50787cc040feb853195fa022d632eb408ff233403550281db41ad3df422cbcbf14573454cb9e17243e25d764c9da3ea1a2ba7d3be214bd93316f0c80c87c90f75e6afff9ef692f8c9b32576c1bf993919c99f7ace7ba57452daa4f4afe9af1076cc43da8f218e915fc273f0991ae680b05175aa3d3d08bd9112107756a74d67977cce445952cbabcc5e8027db442f2f4d4fbda577657930f815c8eb731153299d37e82d78cab095ab41e5b95e3088cd38bfe2a5307bc01a4d148ffc8b92ba2e47bac075c689e858ea7d2f703ef3aca8478eb3219c3fd3aa5c747518bf7a8d766ce1aeb3a042bbe455235ba3c469f9ea2405ad82449878b487eba83505a29ec68f216939b53b087a5a13fc9ee42867abe60b2a3f95215678341c01180c7755e0791f9183d5706d1a85f2d4cf59f70a4f57161a39ee666e7a416eb84f92d463034b83164a2fbe2594155a1ab912e64a482afdd3f1709ce82a35e6a558b6264b6822c8f8d67d6975eab3a599e16c90299c0f4c1e8545ec24f39fd5da2fa4339bc46ea8fe5675feead600930331c21c1e'),
  ('CTR 192 low word wraps', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(24)), 6, unhx('000000000000000000000000fffffffe'), [bytes(((i * 31 + 17 * 7) & 0xFF) for i in range(100))]), '53ecb42979bf85a70c01d63463e3ce62db4cc186d894cbaf60d90eda38eabad124ff95ee7082c46e2452c8f576354b191e4d9ead579d67080f07e3d30fe2c22ce342ef5697d8b80c868ff81874fbb3cd4da77266bc8a5518bdbd0424afbf578d16353241'),
  ('CTR 192 whole counter wraps', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(24)), 6, unhx('fffffffffffffffffffffffffffffffd'), [bytes(((i * 31 + 17 * 7) & 0xFF) for i in range(100))]), '7da28bd943e9d71fa5bfe3d5997567cb38a5aa01562e4a4c74f4efe09055ef97b5167e402004cb61950e350f63e024354742c85b338e43a464b686905dbe5e958244ada10d5893f99606f3e945078999ec66fbf54b4cc4ca179acf524a302e99d111ac84'),
  ('CTR 192 carry through 8 bytes', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(24)), 6, unhx('0101010101010101fffffffffffffffe'), [bytes(((i * 31 + 17 * 7) & 0xFF) for i in range(100))]), '8c191bfa3015eb0857f4b069f5b1ed7d947f6b7feccacdb510fc3801a51db3702a36c6921809125fd85b2de510b7e66b04aa69f7ba582efa30c12af8bd6d35eb05cee37246d3906ffc1e49f7b3870f9a88ca12cd318d7bdf68408de6fbfb2ddfcf4b0149'),
  ('ECB 256 encrypt', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(32)), 1, None, [bytes(((i * 31 + 12 * 7) & 0xFF) for i in range(16))]), 'da1f358f33d9983e6ccbd35aae4d5e34'),
  ('ECB 256 decrypt', lambda: aes('d', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(32)), 1, None, [bytes(((i * 31 + 12 * 7) & 0xFF) for i in range(16))]), '4581f89ef16e29fded1ea1a4037c3ea4'),
  ('CBC 256 encrypt 16', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(32)), 2, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 14 * 7) & 0xFF) for i in range(16))]), '9cde573a2caaae47dc8fc8e82f4dcaf6'),
  ('CBC 256 decrypt 16', lambda: aes('d', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(32)), 2, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 14 * 7) & 0xFF) for i in range(16))]), 'e3ec0fbedcab3de05786773d1fcb5d5d'),
  ('CBC 256 encrypt 48', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(32)), 2, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 14 * 7) & 0xFF) for i in range(48))]), '9cde573a2caaae47dc8fc8e82f4dcaf6e4323045ffdfac7f672909c73bb8359475276769cae141325ea84e078b38ed8d'),
  ('CBC 256 decrypt 48', lambda: aes('d', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(32)), 2, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 14 * 7) & 0xFF) for i in range(48))]), 'e3ec0fbedcab3de05786773d1fcb5d5dc66cac7762032f091a4207a5943994d4f49596c3cdec40ac00ab4fdc57b52a8d'),
  ('CBC 256 encrypt 256', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(32)), 2, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 14 * 7) & 0xFF) for i in range(256))]), '9cde573a2caaae47dc8fc8e82f4dcaf6e4323045ffdfac7f672909c73bb8359475276769cae141325ea84e078b38ed8d5106cad0fa8d915d4be7d3cdbc4ab47ce7daff1db05cf5d85971a297e72039c69f40b93ff135bdcce2427acbc078e15efaef808900f34144c2e7a03bd3fb8092579282c77b8cbb749bb9104f9af7d87f27c07dabd0eb52348fd941c648bc91cc9d0de7ff2d8bbf4969491a5d3a736ab69453ee373d8fea62eaf942363025c6f9825691531380baf7a3e3260ef86a1374d287d2648f8d169c0612dee30623c81e6f37f5cc866db103baf373940e8513a9a3ef445b64bcb6f9b95fd1fe7322ad4f68c53455201801ff91da17835de25cfa'),
  ('CBC 256 decrypt 256', lambda: aes('d', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(32)), 2, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 14 * 7) & 0xFF) for i in range(256))]), 'e3ec0fbedcab3de05786773d1fcb5d5dc66cac7762032f091a4207a5943994d4f49596c3cdec40ac00ab4fdc57b52a8dba714d0043b018293f7d5351260968c5fa3ce36a3b96971559512f1883ed49b6e508861b3f46ab8e7c4540df49a08edeb6d0c687b6f1dd51ffb31fc0bda5813125a987dc767b039afeceb70ba62af7acfffa29a138a278a509a5887c52e17a78ff8a9d3bab7025376868594c08c58654ce7dc605ea1ba932286bcda8edacabdc0eb331d232d098e2d5010323195d0d54f370e449f8914fdc97b9f9a398e82261577d38c952f169d8173e5a97bad79d663af6d18ea29ac0674ddbfc73f90fe72c23e286060a131af5037398852190da1d'),
  ('CBC 256 encrypt 272', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(32)), 2, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 14 * 7) & 0xFF) for i in range(272))]), '9cde573a2caaae47dc8fc8e82f4dcaf6e4323045ffdfac7f672909c73bb8359475276769cae141325ea84e078b38ed8d5106cad0fa8d915d4be7d3cdbc4ab47ce7daff1db05cf5d85971a297e72039c69f40b93ff135bdcce2427acbc078e15efaef808900f34144c2e7a03bd3fb8092579282c77b8cbb749bb9104f9af7d87f27c07dabd0eb52348fd941c648bc91cc9d0de7ff2d8bbf4969491a5d3a736ab69453ee373d8fea62eaf942363025c6f9825691531380baf7a3e3260ef86a1374d287d2648f8d169c0612dee30623c81e6f37f5cc866db103baf373940e8513a9a3ef445b64bcb6f9b95fd1fe7322ad4f68c53455201801ff91da17835de25cfad03655a28ede1119e361c22af2070755'),
  ('CBC 256 decrypt 272', lambda: aes('d', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(32)), 2, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 14 * 7) & 0xFF) for i in range(272))]), 'e3ec0fbedcab3de05786773d1fcb5d5dc66cac7762032f091a4207a5943994d4f49596c3cdec40ac00ab4fdc57b52a8dba714d0043b018293f7d5351260968c5fa3ce36a3b96971559512f1883ed49b6e508861b3f46ab8e7c4540df49a08edeb6d0c687b6f1dd51ffb31fc0bda5813125a987dc767b039afeceb70ba62af7acfffa29a138a278a509a5887c52e17a78ff8a9d3bab7025376868594c08c58654ce7dc605ea1ba932286bcda8edacabdc0eb331d232d098e2d5010323195d0d54f370e449f8914fdc97b9f9a398e82261577d38c952f169d8173e5a97bad79d663af6d18ea29ac0674ddbfc73f90fe72c23e286060a131af5037398852190da1dca0726c9e550049f6e7d4e4a36207432'),
  ('CBC 256 encrypt 1024', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(32)), 2, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 14 * 7) & 0xFF) for i in range(1024))]), '9cde573a2caaae47dc8fc8e82f4dcaf6e4323045ffdfac7f672909c73bb8359475276769cae141325ea84e078b38ed8d5106cad0fa8d915d4be7d3cdbc4ab47ce7daff1db05cf5d85971a297e72039c69f40b93ff135bdcce2427acbc078e15efaef808900f34144c2e7a03bd3fb8092579282c77b8cbb749bb9104f9af7d87f27c07dabd0eb52348fd941c648bc91cc9d0de7ff2d8bbf4969491a5d3a736ab69453ee373d8fea62eaf942363025c6f9825691531380baf7a3e3260ef86a1374d287d2648f8d169c0612dee30623c81e6f37f5cc866db103baf373940e8513a9a3ef445b64bcb6f9b95fd1fe7322ad4f68c53455201801ff91da17835de25cfad03655a28ede1119e361c22af20707555bd99868cb48a8ed71d2a24ca2ed22c1ef76533f7de50bff357bc82388b27c0d2f2b91d245f68a9478fc2a4f62ba687483a2dec77f5fba7a74d17812daf768e92d55679b83e6628a3f2acddf011ee666dfeb8dab690d242d0e4ffb04763e216c8597b19dbcba4a680978dbe986f30ad60bc02e5ecf338169ac109823ce330e8b5dccb1f094399a0195aedde3bc372de81571b4ff688073961bef67964e6abd5ecaf3e51a8e622289da86af5312984a5cb05507764dae90cf3a6ccb06c281aa7aef49ff5a836983d1c8bbe5d08c70a837517558cf923a9c7ef93ac52a831f2b2c844fd4f44766f21c62e5f47fc64a3ccd979723c7ef0b4b6066b7d929e1368c45e5ce81bf1ac5c010d6dc794c6e19c4227ae3e2061e0273f43cbff5829ab98278772bcaa1c57abb25de81ddfaa6f4685ba95e46fb14ab59af92c5b8f3d457450c5ffdfa42f30c6c6ef1db17c1b4e59c308005828810c849d082d2395fb0cabb9feafec22d774910a83e54420edc1c6f249408f2a35593321f397876d9ea78a02897ff5638bfe135a5f324513f8e0f123428263e0ebc3878bc4458d231e5789bd4f52af0a39a0ac3b189b8b102dccc2702c0e3c247d3a863e754d88a7baa642aa58b2eb822bd883977249c7e70e813b673d8176afe4edb692f4518a1076bb66045e51ce95afacaeae36736457d8378638eeaf0ba31785ca5b70b037ac98bcb4c345d72ead08274efe06f73bf5eb81f9265a59a5aee35a1d405b1dba1b4ebe647dc332c47b3e0a3e74a51b5f6bd8280e01da0aa79f885f905b413563b39c904a3af48e2d31e8432774e5d4b2529e36a95df96d16f04ba78c8ca17d4a483851c50f8c0a0cc1802b2d743efc9f1a03642e18ed7950c9c3c8e2fcb35fccc835b12be735e5b8451aeaf271b27c6c448c60934ad726398f86e03857836e5c1a8d4645c062a2871d4d6d08516418d3451d31da44be5a4a1be840ed91ce7f649f20c5a3d86e091995e6cc1720aeb26d19721623bd47542597b8c3b6187b9a29db513a5311d7e48713ce52e07db23ab487df773cf39'),
  ('CBC 256 decrypt 1024', lambda: aes('d', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(32)), 2, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 14 * 7) & 0xFF) for i in range(1024))]), 'e3ec0fbedcab3de05786773d1fcb5d5dc66cac7762032f091a4207a5943994d4f49596c3cdec40ac00ab4fdc57b52a8dba714d0043b018293f7d5351260968c5fa3ce36a3b96971559512f1883ed49b6e508861b3f46ab8e7c4540df49a08edeb6d0c687b6f1dd51ffb31fc0bda5813125a987dc767b039afeceb70ba62af7acfffa29a138a278a509a5887c52e17a78ff8a9d3bab7025376868594c08c58654ce7dc605ea1ba932286bcda8edacabdc0eb331d232d098e2d5010323195d0d54f370e449f8914fdc97b9f9a398e82261577d38c952f169d8173e5a97bad79d663af6d18ea29ac0674ddbfc73f90fe72c23e286060a131af5037398852190da1dca0726c9e550049f6e7d4e4a36207432c66cac7762032f091a4207a5943994d4f49596c3cdec40ac00ab4fdc57b52a8dba714d0043b018293f7d5351260968c5fa3ce36a3b96971559512f1883ed49b6e508861b3f46ab8e7c4540df49a08edeb6d0c687b6f1dd51ffb31fc0bda5813125a987dc767b039afeceb70ba62af7acfffa29a138a278a509a5887c52e17a78ff8a9d3bab7025376868594c08c58654ce7dc605ea1ba932286bcda8edacabdc0eb331d232d098e2d5010323195d0d54f370e449f8914fdc97b9f9a398e82261577d38c952f169d8173e5a97bad79d663af6d18ea29ac0674ddbfc73f90fe72c23e286060a131af5037398852190da1dca0726c9e550049f6e7d4e4a36207432c66cac7762032f091a4207a5943994d4f49596c3cdec40ac00ab4fdc57b52a8dba714d0043b018293f7d5351260968c5fa3ce36a3b96971559512f1883ed49b6e508861b3f46ab8e7c4540df49a08edeb6d0c687b6f1dd51ffb31fc0bda5813125a987dc767b039afeceb70ba62af7acfffa29a138a278a509a5887c52e17a78ff8a9d3bab7025376868594c08c58654ce7dc605ea1ba932286bcda8edacabdc0eb331d232d098e2d5010323195d0d54f370e449f8914fdc97b9f9a398e82261577d38c952f169d8173e5a97bad79d663af6d18ea29ac0674ddbfc73f90fe72c23e286060a131af5037398852190da1dca0726c9e550049f6e7d4e4a36207432c66cac7762032f091a4207a5943994d4f49596c3cdec40ac00ab4fdc57b52a8dba714d0043b018293f7d5351260968c5fa3ce36a3b96971559512f1883ed49b6e508861b3f46ab8e7c4540df49a08edeb6d0c687b6f1dd51ffb31fc0bda5813125a987dc767b039afeceb70ba62af7acfffa29a138a278a509a5887c52e17a78ff8a9d3bab7025376868594c08c58654ce7dc605ea1ba932286bcda8edacabdc0eb331d232d098e2d5010323195d0d54f370e449f8914fdc97b9f9a398e82261577d38c952f169d8173e5a97bad79d663af6d18ea29ac0674ddbfc73f90fe72c23e286060a131af5037398852190da1d'),
  ('CBC 256 encrypt in 3 calls', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(32)), 2, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 15 * 7) & 0xFF) for i in range(96))[:32], bytes(((i * 31 + 15 * 7) & 0xFF) for i in range(96))[32:48], bytes(((i * 31 + 15 * 7) & 0xFF) for i in range(96))[48:]]), '288ba0c4f5105e1643f7eddf85103c1cdbf05d624a07317d1a1b89425ea8645a27b7897b3542b6dffe2bdbf09e61e6af75cb6cc0034dfd55741cf678b8e45b62e78e584862d0b81e4a7cc61fc61acc0242798223fbfc7a0cdcdd0ff835f7cf33'),
  ('CBC 256 decrypt in 3 calls', lambda: aes('d', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(32)), 2, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [unhx('288ba0c4f5105e1643f7eddf85103c1cdbf05d624a07317d1a1b89425ea8645a'), unhx('27b7897b3542b6dffe2bdbf09e61e6af'), unhx('75cb6cc0034dfd55741cf678b8e45b62e78e584862d0b81e4a7cc61fc61acc0242798223fbfc7a0cdcdd0ff835f7cf33')]), '6988a7c6e504234261809fbeddfc1b3a597897b6d5f4133251708faecdec0b2a496887a6c5e4032241607f9ebddcfb1a39587796b5d4f31231506f8eadcceb0a29486786a5c4e30221405f7e9dbcdbfa1938577695b4d3f211304f6e8daccbea'),
  ('CTR 256 lengths 1', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(32)), 6, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 16 * 7) & 0xFF) for i in range(1))]), '6a'),
  ('CTR 256 lengths 16', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(32)), 6, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 16 * 7) & 0xFF) for i in range(16))]), '6a5354821243c62d1ddeda1396dc9588'),
  ('CTR 256 lengths 17', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(32)), 6, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 16 * 7) & 0xFF) for i in range(17))]), '6a5354821243c62d1ddeda1396dc958807'),
  ('CTR 256 lengths 300', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(32)), 6, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 16 * 7) & 0xFF) for i in range(300))]), '6a5354821243c62d1ddeda1396dc9588079fc37754eec17b2e5bc7c3301a0dd751a3df84dbffab2ec26ea8ba4827b24bab60934d745f7b6384c6b6394831d0512cd8716be45f4d2da4f1fc63b25412ecbc7ffe2e18e40a14cc7f16f8366dab699fcebd300ccf46a4c3cf5b66cfed043d4b209aef04112292227d5ec076bde45eb6d6da56d4d9bde2a058474ddd6161434ef216b68a2c0c5d0b5d5efa3971a260f6c7bfb836fe6217f0c5f0c2aecfd97d6b110cd130d0e3874bb5bc639a858c85ee1cf0dd5a24c417a81e5317e6a5bc069cd1d2459c89111ff66364592617abbaffcc2acb349fd5c26adbd3c046a66e12b731541029fe4c466ffd8a0ae0a0553e2bc04c544fe1f129ce232fddab1a8bec6009d796f2a75c438031597600ed78cdd2e3e5759aa8937ed67e4dd6'),
  ('CTR 256 lengths 5+16+33+256+257', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(32)), 6, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 16 * 7) & 0xFF) for i in range(5)), bytes(((i * 31 + 16 * 7) & 0xFF) for i in range(16)), bytes(((i * 31 + 16 * 7) & 0xFF) for i in range(33)), bytes(((i * 31 + 16 * 7) & 0xFF) for i in range(256)), bytes(((i * 31 + 16 * 7) & 0xFF) for i in range(257))]), '6a53548212176ff307641ef10b1eabf7b300ea3da77143ffe4fb1f8b4ee28e88da68c7922b8b40736d147f9b43e4e65619281130714ceccf0e9e6854faa4bccfe64846dd5bd9ef9e6de05c9f9674939f8bb69fbdd4ed1b502a1fb4619262920dee30c6cd54ae06868a860489ed327008179d0d3131939e4266067a9c7cedfbed2e4ac9c1d2d00617efe8e62e32472015a0927e1f892dbbe1bca1802053f7fb450c132a753cf55ecc208d0af41447f8ce8347b6756c56cc6122f5ec39e1af86d394e956a75b0a8f9cfa1b64cf05123a8b031016f6bec2e741e4e0998efcb6df8d3afa50d0e5ce9b901c849fb1a1f91e737f0d7b4adb3cb0b9a72602172cf3708129c6f05d087d2233b5254a78c32e06ae1d8617d0d19a3bbe421d79ad29cd36c1fe9f869584cc3a31768bea3ffc845c58f9f3d956cdd087c59a4f0686464f96b1d4d378f31b210e4936f6f2472ea4dd9daa0ec24b7413d5dd4233faacb0add9e73b94e3fa41e3416faf9ccb544a014e8a69cb0dcdb5d85035b3a89aa58599e249d7be01d9f1a728286477473d11abd7d7f9f531fcc68fedee89110862a03db5d60da24aac01dd01d5541cd92bbc2c5ddb222b5cf2e31cc2964075bdb7c0a43d4fad66bdd6d4b4447d87245dc880fe40a5f760736a775c29bff9678f22c426f65252064054a15da61969f940a5d4313cc5374e3bd033d07658e533be3029496e261d703e4e8dc0d62c3596fd04ffa403dd04f67b61a61e53474ebd0d18194fc9a5da1739e6aba0ddd14e355a1d2be1e1ea4316da799b9a1b'),
  ('CTR 256 lengths 1000', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(32)), 6, bytes(((i * 31 + 13 * 7) & 0xFF) for i in range(16)), [bytes(((i * 31 + 16 * 7) & 0xFF) for i in range(1000))]), '6a5354821243c62d1ddeda1396dc9588079fc37754eec17b2e5bc7c3301a0dd751a3df84dbffab2ec26ea8ba4827b24bab60934d745f7b6384c6b6394831d0512cd8716be45f4d2da4f1fc63b25412ecbc7ffe2e18e40a14cc7f16f8366dab699fcebd300ccf46a4c3cf5b66cfed043d4b209aef04112292227d5ec076bde45eb6d6da56d4d9bde2a058474ddd6161434ef216b68a2c0c5d0b5d5efa3971a260f6c7bfb836fe6217f0c5f0c2aecfd97d6b110cd130d0e3874bb5bc639a858c85ee1cf0dd5a24c417a81e5317e6a5bc069cd1d2459c89111ff66364592617abbaffcc2acb349fd5c26adbd3c046a66e12b731541029fe4c466ffd8a0ae0a0553e2bc04c544fe1f129ce232fddab1a8bec6009d796f2a75c438031597600ed78cdd2e3e5759aa8937ed67e4dd6c70081caeb4ef26dc95d99bd86314eef366534bc8ae1a6dbbaef2cd40c8829a389861d80d7756aff7636b6ffe60124630843eb917e19e626a217fe748dcd7ade921ba4c385adf2c34adc005d69978b64538af113f13fff4c1b041ad19eda391bdd9de5088085c3186a15f52912f9a70ef1698117d8f8342797ed41fb0707a9a5e12c96df3d1e3961b892104d0526bdd2fa5cb1adb105844c89fb6c7c0d0bf27b0c22334c9226b0c5cd0730144dff5dd6cd662404342d57f40d98502e10f527b0233aa78c79cf49973f5274d64622e2f6f02411ad1649392990f584e1ec95679eeb806300a6e895834e8059f99e966dc0cefefd7026fc65c62dd4aff4d30d54a6abb1f64e83b7fecdbde8a93f79556a6789161bd06d019e650acdfbb1b13a93468aa94bca4b7256e16b7af47dce5ba0f81a7604ad0e21b7bf09d9e965dff75d834d3d04bbe1d4d6c05294116660c28f50e8e6b56d7d5035d96a27377961c8272661fa1da9e6c9b245bdb0319cb067dcdb53eec3495b5075ea3238b0e24afd67f429f2ebbb5cb5ff31b7ec6b3a3954ffcf204a5d2e40698f24e2f08692ecf06952f290b471eae130d526a487e5a89be2332c24cb9e7ca49198090c2a2e2b1cefce9a825c182d6802e28a33be839c8d7d7e53c1323d389c8b82857d413283a03221d8705fd0eb31e5efac649a263639bdbcdb1294965df376a604b85b98105f2397840f9e21168ea711fa572009691354e98bfe85f6ebba8f72c33688f051c41ada0a104426c81f52cdcc51c829fb2bd365df2c05ef8767d4898af78e4006e5a3c9364468ee47fb592c6e17e31bd5ee80a8cb07f364545bd33b8f3fecfec1a406567465e353d3572d37cd7e4e71463184f2618ee3bb8db7fc079ab191e339593e3f8e5a3c362848ed5e9a720c6ae656ff06bf8982e2113be8e5822dafbb66b97174dfd1a656862b65e8ad940eae09cf076d2e80a2b3f8f57f55824e8d7e'),
  ('CTR 256 low word wraps', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(32)), 6, unhx('000000000000000000000000fffffffe'), [bytes(((i * 31 + 17 * 7) & 0xFF) for i in range(100))]), 'a3c96bbf86a11bcdd312f3321504e4b9ea2853fc6ec232391d13ac77324d4fd3fabf2c281ccc6be02f6831d32b707bc47f35cd766c66380d902f99647ea5b335c433ea6ef30bd95b2118c2667a580333a382475b26c0fe918ecbc083daf6512c6f8579c7'),
  ('CTR 256 whole counter wraps', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(32)), 6, unhx('fffffffffffffffffffffffffffffffd'), [bytes(((i * 31 + 17 * 7) & 0xFF) for i in range(100))]), 'e7efe747646e6ed60b8bc6c3d35243e81902e6303e70bcd165744508432ea186e1f235a60a29195bed778a7395727baca8f76c20b61a1bd08e7ded7e508978ccc7c31610cf8947d82c63800caf008e91d366d2b05b897bdb03ae417ea48478e6b0591baa'),
  ('CTR 256 carry through 8 bytes', lambda: aes('e', bytes(((i * 31 + 11 * 7) & 0xFF) for i in range(32)), 6, unhx('0101010101010101fffffffffffffffe'), [bytes(((i * 31 + 17 * 7) & 0xFF) for i in range(100))]), '69fffb4d50897954722d0b1e78b657b1de087a727b6a0942db76423f7cc194bab2e53b1567e7010a919b42938d220f992aa525a10ae8fdb2866cb6fcd14ef908ba000fc3381aab07cd360f95e33e9746060401129e9f03022cb75ea4eb9135f9796d8e2a'),
  ('two AES objects in turn', lambda: two(), '12a3b94d8bbe6f6768cf95a86c2d2b8f42d698be432763490dc8cb2e646f2532deb71ec6aacfe5dfa29839354636a5b7627fb51dd93ecfa4c2d7680856f7b4882ef534465642115edc9c65bb95b2953658a6fbe0b8a3bb904ebff5e81037487ccfd68478410ba7f194db1668dcab1aa2761f'),
]

# ---------------------------------------------------------------- hardware

def h_identity():
    import board, microcontroller
    uid = microcontroller.cpu.uid
    if board.board_id != "dabao":
        return "board_id " + board.board_id
    if len(uid) != 16 or uid == bytes(16):
        return "uid " + repr(uid)
    if hasattr(board, "PROG") or hasattr(board, "PC13") or hasattr(microcontroller.pin, "PC13"):
        return "PC13 is offered"
    return True

def h_drive():
    import os, storage, baochip
    if "code.py" not in [n.lower() for n in os.listdir("/")]:
        return "code.py not listed"
    st = os.statvfs("/")
    size = st[0] * st[2]
    if not 400000 < size < 600000:
        return "drive size %d" % size
    p = baochip.pending()
    if not isinstance(p, int) or p < 0:
        return "pending " + repr(p)
    return True

def h_sleep():
    a = time.monotonic()
    time.sleep(1.0)
    d = time.monotonic() - a
    return True if 0.98 < d < 1.05 else "1 s sleep took %.3f" % d

def h_trng():
    import os
    data = os.urandom(4096)
    ones = 0
    for b in data:
        while b:
            ones += b & 1
            b >>= 1
    share = ones / (4096 * 8)
    if not 0.48 < share < 0.52:
        return "share of one bits %.4f" % share
    blocks = set(data[i:i + 16] for i in range(0, 4096, 16))
    if len(blocks) != 256:
        return "repeated blocks"
    if len(set(data)) < 250:
        return "only %d byte values seen" % len(set(data))
    return True

def h_gpio_loop():
    import board, digitalio
    out = digitalio.DigitalInOut(board.PB1)
    inp = digitalio.DigitalInOut(board.PB4)
    try:
        inp.switch_to_input()
        out.switch_to_output(False)
        for want in (True, False, True, True, False, False, True, False):
            out.value = want
            time.sleep(0.002)
            if inp.value != want:
                return "PB1 drove %s, PB4 read %s (jumper PB1 to PB4?)" % (want, inp.value)
        out.switch_to_input()
        inp.switch_to_output(False)
        for want in (True, False, True, False):
            inp.value = want
            time.sleep(0.002)
            if out.value != want:
                return "PB4 drove %s, PB1 read %s" % (want, out.value)
        inp.switch_to_input(pull=digitalio.Pull.UP)
        time.sleep(0.002)
        if out.value is not True:
            return "pull up on PB4 did not lift the line"
        try:
            inp.switch_to_input(pull=digitalio.Pull.DOWN)
            return "pull down was accepted"
        except ValueError:
            pass
        return True
    finally:
        out.deinit()
        inp.deinit()

def measure(pin, ms):
    from adafruit_ticks import ticks_ms, ticks_diff
    gc.collect()
    high = 0
    count = 0
    edges = 0
    last = pin.value
    start = ticks_ms()
    while ticks_diff(ticks_ms(), start) < ms:
        v = pin.value
        high += v
        edges += v != last
        last = v
        count += 1
    return high / count, edges * 500 / ms, count

def h_pwm():
    import board, digitalio, pwmio
    inp = digitalio.DigitalInOut(board.PB4)
    inp.switch_to_input()
    pwm = pwmio.PWMOut(board.PB1, frequency=50, duty_cycle=0)
    try:
        if pwm.frequency != 50:
            return "frequency reads %d" % pwm.frequency
        seen = []
        for duty in (16384, 32768, 49152):
            pwm.duty_cycle = duty
            time.sleep(0.05)
            share, hz, n = measure(inp, 1000)
            seen.append("%.3f" % share)
            want = duty / 65536
            if abs(share - want) > 0.05:
                return "duty %.2f measured %.3f over %d samples (jumper PB1 to PB4?)" % (want, share, n)
            if not 47 <= hz <= 53:
                return "50 Hz measured %.1f" % hz
        print("  pwm duty 0.25 0.50 0.75 measured", " ".join(seen), "at %.0f Hz, %d samples a second" % (hz, n))
        pwm.duty_cycle = 0
        time.sleep(0.05)
        share, hz, n = measure(inp, 200)
        if share > 0.01:
            return "duty 0 measured %.3f" % share
        pwm.duty_cycle = 65535
        time.sleep(0.05)
        share, hz, n = measure(inp, 200)
        if share < 0.99:
            return "duty 65535 measured %.3f" % share
        return True
    finally:
        pwm.deinit()
        inp.deinit()

def h_pwm_shared():
    import board, pwmio
    a = pwmio.PWMOut(board.PB2, frequency=1000, duty_cycle=1000)
    try:
        try:
            b = pwmio.PWMOut(board.PB3, frequency=2000, duty_cycle=1000)
            b.deinit()
            return "two frequencies in one group were accepted"
        except ValueError:
            pass
        b = pwmio.PWMOut(board.PB3, frequency=1000, duty_cycle=30000)
        ok = abs(b.duty_cycle - 30000) < 200 and abs(a.duty_cycle - 1000) < 200
        b.deinit()
        return True if ok else "duty read back %d and %d" % (a.duty_cycle, b.duty_cycle)
    finally:
        a.deinit()

def h_uart():
    import board, busio
    u = busio.UART(board.TX, board.RX, baudrate=115200, timeout=0.5)
    try:
        msg = b"Dabao UART loopback 0123456789"
        u.reset_input_buffer()
        u.write(msg)
        time.sleep(0.1)
        got = u.read(len(msg))
        if got != msg:
            return "115200 got %r (jumper PB14 to PB13?)" % (got,)
        big = bytes(range(256))
        u.write(big)
        time.sleep(0.2)
        got = u.read(256)
        if got != big:
            return "256 bytes came back wrong, %d bytes" % (len(got) if got else 0)
        if u.read(1) is not None:
            return "extra bytes after the message"
        u.baudrate = 9600
        if not 9590 <= u.baudrate <= 9610:
            return "baudrate reads %d" % u.baudrate
        u.write(b"slow")
        time.sleep(0.2)
        got = u.read(4)
        if got != b"slow":
            return "9600 got %r" % (got,)
        t = time.monotonic()
        if u.read(1) is not None:
            return "read with nothing sent returned data"
        waited = time.monotonic() - t
        if not 0.4 < waited < 0.7:
            return "0.5 s timeout took %.3f" % waited
        return True
    finally:
        u.deinit()

def h_spi():
    import board, busio
    spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
    try:
        while not spi.try_lock():
            pass
        for hz in (1000000, 8000000, 250000):
            spi.configure(baudrate=hz)
            if not hz * 0.85 <= spi.frequency <= hz:
                return "asked %d Hz, got %d" % (hz, spi.frequency)
            out = bytes([0xA5, 0x5A, 0x00, 0xFF, 0x12, 0x34])
            back = bytearray(len(out))
            spi.write_readinto(out, back)
            if bytes(back) != out:
                return "%d Hz got %r (jumper PC1 to PC2?)" % (hz, bytes(back))
        spi.configure(baudrate=4000000)
        big = bytes((i * 7 + 3) & 0xFF for i in range(1000))
        back = bytearray(1000)
        spi.write_readinto(big, back)
        if bytes(back) != big:
            return "1000 bytes came back wrong"
        spi.unlock()
        return True
    finally:
        spi.deinit()

def h_i2c():
    import board, busio
    i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)
    try:
        while not i2c.try_lock():
            pass
        found = i2c.scan()
        if found:
            return "scan found %s with nothing connected" % [hex(a) for a in found]
        for addr in (0x08, 0x50, 0x68, 0x77):
            try:
                i2c.writeto(addr, b"\x00")
                return "a write to empty address 0x%02x did not fail" % addr
            except OSError:
                pass
        try:
            i2c.readfrom_into(0x68, bytearray(2))
            return "a read from an empty address did not fail"
        except OSError:
            pass
        i2c.unlock()
        i2c.deinit()
        i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
        while not i2c.try_lock():
            pass
        if i2c.scan():
            return "scan at 100 kHz found something"
        i2c.unlock()
        return True
    finally:
        i2c.deinit()

def adc_volts(a):
    total = 0
    for i in range(16):
        total += a.value
    return total / 16 / 65535 * a.reference_voltage

def h_adc():
    import board, analogio, digitalio
    drive = digitalio.DigitalInOut(board.PC8)
    a = analogio.AnalogIn(board.A0)
    try:
        if abs(a.reference_voltage - 1.208) > 0.001:
            return "reference reads %.3f" % a.reference_voltage
        drive.switch_to_output(False)
        time.sleep(0.05)
        low = adc_volts(a)
        drive.value = True
        time.sleep(0.05)
        high = adc_volts(a)
        print("  adc reads %.3f V with PC8 low and %.3f V with PC8 high" % (low, high))
        drive.value = False
        time.sleep(0.05)
        low2 = adc_volts(a)
        if low > 0.15 or low2 > 0.15:
            return "PC8 low read %.3f V and %.3f V (jumper PC8 to PC9?)" % (low, low2)
        if high < 1.15:
            return "PC8 high read %.3f V, want the top of the scale (jumper PC8 to PC9?)" % high
        return True
    finally:
        a.deinit()
        drive.deinit()

def h_pins_released():
    import board, digitalio, busio, pwmio
    for i in range(3):
        d = digitalio.DigitalInOut(board.PB5)
        d.deinit()
        p = pwmio.PWMOut(board.PC0, frequency=1000)
        p.deinit()
        s = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        s.deinit()
        u = busio.UART(board.TX, board.RX)
        u.deinit()
        c = busio.I2C(board.SCL, board.SDA)
        c.deinit()
    d = digitalio.DigitalInOut(board.PB5)
    try:
        digitalio.DigitalInOut(board.PB5)
        return "a pin in use was handed out twice"
    except ValueError:
        return True
    finally:
        d.deinit()

HARDWARE = [
    ("board identity and serial number", h_identity),
    ("CIRCUITPY drive and baochip.pending", h_drive),
    ("1 second sleep", h_sleep),
    ("true random numbers", h_trng),
    ("digitalio through the PB1 to PB4 jumper", h_gpio_loop),
    ("pwmio duty and frequency measured on PB4", h_pwm),
    ("pwmio shared frequency rule", h_pwm_shared),
    ("busio.UART through the PB14 to PB13 jumper", h_uart),
    ("busio.SPI through the PC1 to PC2 jumper", h_spi),
    ("busio.I2C with an empty bus", h_i2c),
    ("analogio through the PC8 to PC9 jumper", h_adc),
    ("pins are released and guarded", h_pins_released),
]


# ------------------------------------------------------------------ runner

total = 0
failed = 0

def section(title, rows, compare):
    global total, failed
    bad = 0
    for row in rows:
        name, fn = row[0], row[1]
        want = row[2] if compare else True
        try:
            got = fn()
        except Exception as e:
            got = "error " + repr(e)
        if got != want:
            bad += 1
            print("FAIL", title + ":", name)
            print("     ", str(got)[:150])
        gc.collect()
    total += len(rows)
    failed += bad
    print("%-9s %d of %d passed" % (title, len(rows) - bad, len(rows)))

print("Dabao CircuitPython full test")
print(sys.implementation.version, "uid", binascii.hexlify(__import__("microcontroller").cpu.uid).decode())
started = time.monotonic()
section("hardware", HARDWARE, False)
section("software", SOFTWARE, False)
section("security", SECURITY, True)
print("FULL TEST: %d of %d passed in %.1f s" % (total - failed, total, time.monotonic() - started))
print("RESULT:", "PASS" if failed == 0 else "FAIL")
print("ALL_DONE")
