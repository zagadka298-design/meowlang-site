#!/usr/bin/env python3
"""
MeowLang v5.3
Esoteric programming language based on feline vocalizations.
Turing-complete.
License: MIT
"""

import random
import time
import os
import json
import math
import struct
import subprocess
import tempfile
import threading
import urllib.request
import urllib.error
import sqlite3
import hashlib
import base64
import socket

__version__ = "5.3.0"
__license__ = "MIT"

SAFE_MODE = True
MAX_MEMORY = 10000
MAX_FILE_SIZE = 1024 * 1024
MAX_URL_LENGTH = 2048
MAX_FETCH_SIZE = 10240
MAX_OPERATIONS = 100000

ALLOWED_PATHS = [
    os.path.expanduser("~/meowlang"),
    "/tmp"
]

BLOCKED_EXEC_PATTERNS = [
    "rm", "sudo", "chmod", "mkfs", "dd", "shutdown", "reboot",
    "poweroff", "halt", "kill", "pkill", "chown", "passwd",
    "mount", "umount", "fdisk", "iptables", "ufw",
    ">", "2>", "&>", "/dev/sd", "format", "scp", "ssh", "nc", "wget"
]

BLOCKED_URL_PATTERNS = ["127.0.0.1", "localhost", "0.0.0.0", "file://", "internal"]
ALLOWED_PROTOCOLS = ["http://", "https://"]
ALLOWED_IMPORTS = ["math", "random", "time", "json", "collections", "itertools", "hashlib", "base64"]
ALLOWED_EXEC = ["ls", "pwd", "date", "whoami", "uptime", "ping", "curl", "wget", "echo", "cat", "head", "tail", "grep", "find", "df", "du", "ps", "top", "htop", "neofetch", "clear", "mkdir", "touch", "cp", "mv"]


class SecurityError(Exception):
    pass


class CryptoUtils:
    @staticmethod
    def compute_hash(data):
        digest = hashlib.sha256(data.encode()).hexdigest()
        return f"meow_{digest[:16]}_purr"

    @staticmethod
    def encrypt(data, key="catnip"):
        result = []
        for i, ch in enumerate(data):
            key_char = key[i % len(key)]
            result.append(chr(ord(ch) ^ ord(key_char)))
        encoded = base64.b64encode("".join(result).encode()).decode()
        return f"\U0001f431{encoded}\U0001f431"

    @staticmethod
    def decrypt(data, key="catnip"):
        cleaned = data.strip("\U0001f431")
        try:
            decoded = base64.b64decode(cleaned).decode()
            result = []
            for i, ch in enumerate(decoded):
                key_char = key[i % len(key)]
                result.append(chr(ord(ch) ^ ord(key_char)))
            return "".join(result)
        except Exception:
            return None

    @staticmethod
    def scan_port(host, port, timeout=1):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        try:
            result = sock.connect_ex((host, port))
            return result == 0
        except Exception:
            return False
        finally:
            sock.close()

    @staticmethod
    def generate_password(length=16, style="strong"):
        if style == "passphrase":
            words = ["mew", "nya", "purr", "hiss", "mrr", "blep", "boop", "bonk"]
            parts = [random.choice(words) + str(random.randint(0, 99)) for _ in range(4)]
            return "-".join(parts)
        elif style == "pin":
            return "".join(str(random.randint(0, 9)) for _ in range(length))
        else:
            chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
            return "".join(random.choice(chars) for _ in range(length))


class AudioBackend:
    sample_rate = 22050

    @classmethod
    def _generate_wav(cls, samples):
        if len(samples) > cls.sample_rate * 10:
            raise SecurityError("audio duration exceeds limit")
        count = len(samples)
        data_size = count * 2
        header = struct.pack(
            "<4sI4s4sIHHIIHH4sI",
            b"RIFF", 36 + data_size,
            b"WAVE", b"fmt ",
            16, 1, 1,
            cls.sample_rate,
            cls.sample_rate * 2,
            2, 16,
            b"data", data_size
        )
        body = b"".join(
            struct.pack("<h", max(-32767, min(32767, int(s * 32767))))
            for s in samples
        )
        return header + body

    @classmethod
    def play(cls, samples):
        wav_data = cls._generate_wav(samples)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(wav_data)
            tmp_path = f.name
        players = [
            ["aplay", "-q", tmp_path],
            ["paplay", tmp_path],
            ["pw-play", tmp_path],
            ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", tmp_path],
        ]
        for cmd in players:
            try:
                subprocess.run(cmd, timeout=3, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                break
            except Exception:
                continue
        time.sleep(0.03)
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

    @classmethod
    def tone(cls, freq, duration=0.2, volume=0.5, waveform="sine"):
        if duration > 5:
            raise SecurityError("tone duration exceeds limit")
        if freq < 20 or freq > 20000:
            raise SecurityError("frequency out of audible range")
        n = int(cls.sample_rate * duration)
        samples = []
        for i in range(n):
            t = i / cls.sample_rate
            envelope = 1.0 - i / n
            if waveform == "square":
                signal = 1.0 if math.sin(2 * math.pi * freq * t) > 0 else -1.0
            elif waveform == "saw":
                signal = 2.0 * (freq * t % 1.0) - 1.0
            elif waveform == "triangle":
                signal = 4.0 * abs(freq * t % 1.0 - 0.5) - 1.0
            else:
                signal = math.sin(2 * math.pi * freq * t)
            samples.append(signal * envelope * volume)
        cls.play(samples)

    @classmethod
    def noise(cls, duration=0.2, volume=0.4):
        if duration > 5:
            raise SecurityError("noise duration exceeds limit")
        n = int(cls.sample_rate * duration)
        samples = [random.uniform(-1, 1) * volume * (1 - i / n) for i in range(n)]
        cls.play(samples)


class SoundEffects:
    @staticmethod
    def meow():
        rate = 22050
        duration = 0.6
        n = int(rate * duration)
        samples = []
        for i in range(n):
            t = i / rate
            p = t / duration
            if p < 0.3:
                freq = 400 + p * 1000
            elif p < 0.6:
                freq = 700 + (p - 0.3) * 800
            else:
                freq = 940 - (p - 0.6) * 600
            if p < 0.1:
                envelope = p / 0.1
            elif p < 0.6:
                envelope = 1.0
            else:
                envelope = 1.0 - (p - 0.6) / 0.4
            vibrato = math.sin(2 * math.pi * 7 * t) * 30
            samples.append(math.sin(2 * math.pi * (freq + vibrato) * t) * envelope * 0.6)
        AudioBackend.play(samples)

    @staticmethod
    def short_meow():
        rate = 22050
        duration = 0.35
        n = int(rate * duration)
        samples = []
        for i in range(n):
            t = i / rate
            p = t / duration
            freq = 500 + p * 400
            if p < 0.15:
                envelope = p / 0.15
            elif p < 0.6:
                envelope = 1.0
            else:
                envelope = 1.0 - (p - 0.6) / 0.4
            vibrato = math.sin(2 * math.pi * 8 * t) * 15
            samples.append(math.sin(2 * math.pi * (freq + vibrato) * t) * envelope * 0.5)
        AudioBackend.play(samples)

    @staticmethod
    def angry_meow():
        rate = 22050
        duration = 0.5
        n = int(rate * duration)
        samples = []
        for i in range(n):
            t = i / rate
            p = t / duration
            freq = 600 + p * 500
            if p < 0.05:
                envelope = p / 0.05
            elif p < 0.5:
                envelope = 1.0
            else:
                envelope = 1.0 - (p - 0.5) / 0.5
            noise = random.uniform(-0.1, 0.1)
            samples.append((math.sin(2 * math.pi * freq * t) * 0.7 + noise * 0.3) * envelope * 0.7)
        AudioBackend.play(samples)

    @staticmethod
    def purr():
        rate = 22050
        duration = 0.8
        n = int(rate * duration)
        samples = []
        for i in range(n):
            t = i / rate
            tremolo = 0.6 + 0.4 * math.sin(2 * math.pi * 8 * t)
            base = math.sin(2 * math.pi * 30 * t) * 0.4
            harmonic = math.sin(2 * math.pi * 60 * t) * 0.2
            jitter = random.uniform(-0.05, 0.05)
            samples.append((base + harmonic + jitter) * tremolo * 0.5)
        AudioBackend.play(samples)

    @staticmethod
    def hiss():
        AudioBackend.noise(0.5, 0.7)

    @staticmethod
    def bonk():
        AudioBackend.tone(200, 0.08, 0.8)
        time.sleep(0.02)
        AudioBackend.tone(120, 0.12, 0.5)

    @staticmethod
    def yeet():
        for freq in [900, 600, 350, 180]:
            AudioBackend.tone(freq, 0.06, 0.5)
            time.sleep(0.02)

    @staticmethod
    def trill():
        rate = 22050
        duration = 0.3
        n = int(rate * duration)
        samples = []
        for i in range(n):
            t = i / rate
            p = t / duration
            freq = 500 + math.sin(2 * math.pi * 20 * t) * 200
            envelope = p / 0.1 if p < 0.1 else 1.0 - (p - 0.1) / 0.9
            samples.append(math.sin(2 * math.pi * freq * t) * envelope * 0.5)
        AudioBackend.play(samples)

    @staticmethod
    def coin():
        AudioBackend.tone(1200, 0.05, 0.5)
        time.sleep(0.03)
        AudioBackend.tone(1600, 0.1, 0.6)

    @staticmethod
    def dice():
        for _ in range(4):
            AudioBackend.tone(random.randint(200, 600), 0.03, 0.3)
            time.sleep(0.02)

    @staticmethod
    def win_jingle():
        for freq in [523, 659, 784, 1047]:
            AudioBackend.tone(freq, 0.15, 0.6)
            time.sleep(0.05)

    @staticmethod
    def lose_jingle():
        for freq in [400, 300, 200]:
            AudioBackend.tone(freq, 0.2, 0.5)
            time.sleep(0.08)


class Canvas:
    def __init__(self, width=40, height=20):
        self.width = width
        self.height = height
        self.buffer = [[" "] * width for _ in range(height)]

    def clear(self):
        self.buffer = [[" "] * self.width for _ in range(self.height)]

    def rect(self, x, y, w, h, char="#"):
        if w > self.width or h > self.height:
            raise SecurityError("rectangle exceeds canvas bounds")
        for row in range(h):
            for col in range(w):
                cx, cy = x + col, y + row
                if 0 <= cx < self.width and 0 <= cy < self.height:
                    self.buffer[cy][cx] = char

    def circle(self, cx, cy, radius, char="@"):
        if radius > self.width:
            raise SecurityError("circle exceeds canvas bounds")
        for row in range(self.height):
            for col in range(self.width):
                if (row - cy) ** 2 + (col - cx) ** 2 <= radius ** 2:
                    self.buffer[row][col] = char

    def text(self, x, y, message):
        if len(message) > 100:
            raise SecurityError("text exceeds length limit")
        for i, ch in enumerate(message):
            cx = x + i
            if 0 <= cx < self.width and 0 <= y < self.height:
                self.buffer[y][cx] = ch

    def render(self):
        for row in self.buffer:
            print("".join(row))


class MeowLang:
    def __init__(self):
        self.memory = [0] * MAX_MEMORY
        self.pointer = 0
        self.stack = []
        self.variables = {}
        self.programs = {}
        self.functions = {}
        self.labels = {}
        self.arrays = {}
        self.database = None
        self.threads = []
        self.modules = {}
        self.canvas = Canvas()
        self.operation_counter = 0
        self.muted = False
        self.proxy_enabled = False
        self.proxy_addr = "socks5h://127.0.0.1:9050"
        self.crypto = CryptoUtils()
        self.audio = AudioBackend()
        self.sfx = SoundEffects()

    def _validate_path(self, path):
        resolved = os.path.realpath(os.path.expanduser(path))
        for allowed in ALLOWED_PATHS:
            base = os.path.realpath(os.path.expanduser(allowed))
            if resolved.startswith(base):
                return True
        raise SecurityError(f"path not allowed: {path}")

    def _validate_exec(self, command):
        lowered = command.lower()
        base_cmd = lowered.split()[0] if lowered.split() else ""
        for pattern in BLOCKED_EXEC_PATTERNS:
            if pattern in lowered or pattern in command:
                raise SecurityError(f"blocked pattern in exec: {pattern}")
        dangerous = [";", "&&", "||", "`", "$(", ">", "<", "&"]
        for char in dangerous:
            if char in command:
                raise SecurityError(f"dangerous character in exec: {char}")
        if base_cmd and base_cmd not in ALLOWED_EXEC:
            raise SecurityError(f"command not in whitelist: {base_cmd}")
        return True

    def _validate_url(self, url):
        if len(url) > MAX_URL_LENGTH:
            raise SecurityError(f"url exceeds length limit: {url}")
        if False and not any(url.startswith(proto) for proto in ALLOWED_PROTOCOLS):
            raise SecurityError(f"protocol not allowed: {url}")
        for pattern in BLOCKED_URL_PATTERNS:
            if pattern in url:
                raise SecurityError(f"url pattern blocked: {pattern}")
        return True

    def _check_operation_limit(self):
        self.operation_counter += 1
        if self.operation_counter > MAX_OPERATIONS:
            raise SecurityError("operation limit reached")

    @staticmethod
    def _tokenize(source):
        if len(source) > 50000:
            raise SecurityError("source code exceeds size limit")
        import re
        lines = []
        for line in source.split("\n"):
            s = line.strip()
            if not s:
                continue
            c = s.find("//")
            if c >= 0:
                s = s[:c].strip()
            if s:
                lines.append(s)
        text = " ".join(lines)
        urls = re.findall(r"https?://\S+", text)
        for i, u in enumerate(urls):
            text = text.replace(u, "<<<URL" + str(i) + ">>>")
        text = text.lower()
        tokens = text.split()
        for i, u in enumerate(urls):
            tokens = [t.replace("<<<url" + str(i) + ">>>", u) for t in tokens]
        return tokens
    @staticmethod
    def _build_loop_map(tokens):
        loop_map = {}
        stack = []
        for index, token in enumerate(tokens):
            if token == "purr":
                if len(stack) >= 50:
                    raise SecurityError("loop nesting depth exceeded")
                stack.append(index)
            elif token == "hiss":
                if not stack:
                    raise SecurityError("unmatched hiss")
                start = stack.pop()
                loop_map[start] = index
                loop_map[index] = start
        if stack:
            raise SecurityError("unclosed purr loop")
        return loop_map

    @staticmethod
    def _build_control_map(tokens):
        control_map = {}
        stack = []
        for i, token in enumerate(tokens):
            if token == "if":
                stack.append(i)
            elif token == "else":
                if not stack:
                    raise SecurityError("else without if")
                if_idx = stack.pop()
                control_map[if_idx] = i
                stack.append(i)
            elif token == "endif":
                if not stack:
                    raise SecurityError("endif without if")
                start = stack.pop()
                control_map[start] = i
        if stack:
            raise SecurityError("unclosed if/else block")
        return control_map

    def _fetch(self, url, use_proxy=False):
        self._validate_url(url)
        agents = [
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/605.1.15",
            "Lynx/2.8.9rel.1 libwww-FM/2.14",
            "curl/7.68.0",
        ]
        ua = random.choice(agents)
        try:
            if use_proxy or self.proxy_enabled:
                proxy_handler = urllib.request.ProxyHandler({
                    "http": self.proxy_addr,
                    "https": self.proxy_addr,
                })
                opener = urllib.request.build_opener(proxy_handler)
            else:
                opener = urllib.request.build_opener()
            request = urllib.request.Request(url, headers={"User-Agent": ua})
            with opener.open(request, timeout=10) as response:
                body = response.read(MAX_FETCH_SIZE)
                return body.decode("utf-8", errors="ignore")
        except urllib.error.URLError as exc:
            return f"network error: {exc}"
        except Exception as exc:
            return f"fetch error: {exc}"

    def execute(self, source):
        try:
            return self._execute(source)
        except SecurityError as exc:
            return f"[security] {exc}"
        except Exception as exc:
            return f"[error] {exc}"

    def _execute(self, source):
        self.memory = [0] * MAX_MEMORY
        self.pointer = 0
        self.stack.clear()
        saved_progs = dict(self.programs)
        self.variables.clear()
        self.programs = saved_progs
        self.functions.clear()
        self.labels.clear()
        self.arrays.clear()
        self.canvas.clear()
        self.threads.clear()
        self.modules.clear()
        self.operation_counter = 0

        tokens = self._tokenize(source)
        loop_map = self._build_loop_map(tokens)
        control_map = self._build_control_map(tokens)
        output = []

        reserved_words = {
            "endlist", "mew", "mrr", "nya", "aww", "meow", "purr", "hiss",
            "bonk", "yeet", "boop", "snip", "var", "call", "jump", "print",
            "yell", "save", "load", "exec", "wipe", "nap", "beep", "coin",
            "dice", "box", "hunt", "laser", "rps", "list", "draw", "wave",
            "fetch", "dbopen", "dbset", "dbget", "fork", "wait", "stretch",
            "loaf", "bap", "zoomies", "hash", "encrypt", "decrypt", "scan",
            "pwdgen", "cert", "endfunc", "return", "trill", "angry",
            "meowsnd", "purrsnd", "hisssnd", "bonksnd", "yeetsnd",
            "catnip", "arrget", "arrset", "arrlen", "note", "melody",
            "alarm", "rnd", "time", "len", "str", "puts", "mrow",
            "sniff", "pounce", "hide", "not", "and", "or",
            "blep", "swap", "stash", "grab", "zoom", "bonk?",
            "set", "get", "label", "jif", "import", "mute", "unmute", "tor", "proxy", "anon"
        }

        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token == "func" and i + 1 < len(tokens):
                name = tokens[i + 1]
                start = i + 2
                depth = 0
                j = start
                while j < len(tokens):
                    if tokens[j] == "func":
                        depth += 1
                    elif tokens[j] == "endfunc":
                        if depth == 0:
                            self.functions[name] = (start, j)
                            break
                        depth -= 1
                    j += 1
                i = j
            elif token == "label" and i + 1 < len(tokens):
                self.labels[tokens[i + 1]] = i + 2
            i += 1

        ip = 0
        call_stack = []

        while ip < len(tokens):
            self._check_operation_limit()
            token = tokens[ip]

            if token == "meowsnd":
                self.sfx.meow()
                print("  meow")
            elif token == "mew":
                if not self.muted:
                    self.sfx.short_meow()
                self.memory[self.pointer] = (self.memory[self.pointer] + 1) % 256
            elif token == "angry":
                if not self.muted:
                    self.sfx.angry_meow()
                print("  angry meow")
            elif token == "trill":
                if not self.muted:
                    self.sfx.trill()
                print("  trill")
            elif token == "purrsnd":
                if not self.muted:
                    self.sfx.purr()
                print("  purring")
            elif token == "hisssnd":
                if not self.muted:
                    self.sfx.hiss()
                print("  hiss")
            elif token == "bonksnd":
                if not self.muted:
                    self.sfx.bonk()
                print("  bonk")
            elif token == "yeetsnd":
                if not self.muted:
                    self.sfx.yeet()
                print("  yeet")
            elif token == "beep":
                freq = self.memory[self.pointer] * 8 + 200
                freq = max(50, min(8000, freq))
                self.audio.tone(freq, 0.3, 0.5)
            elif token == "note" and ip + 1 < len(tokens):
                scale = {"c": 262, "d": 294, "e": 330, "f": 349, "g": 392, "a": 440, "b": 494, "c2": 523}
                ip += 1
                self.audio.tone(scale.get(tokens[ip], 440), 0.3, 0.5)
            elif token == "melody" and ip + 1 < len(tokens):
                ip += 1
                scale = {"c": 262, "d": 294, "e": 330, "f": 349, "g": 392, "a": 440, "b": 494}
                for note in tokens[ip]:
                    if note in scale:
                        self.audio.tone(scale[note], 0.2, 0.5)
                        time.sleep(0.08)
            elif token == "alarm":
                count = min(self.memory[self.pointer] if self.memory[self.pointer] > 0 else 3, 20)
                for _ in range(count):
                    self.audio.tone(800, 0.2, 0.7)
                    time.sleep(0.15)
            elif token == "wave" and ip + 2 < len(tokens):
                waveform = tokens[ip + 1]
                if waveform not in ("sine", "square", "saw", "triangle"):
                    waveform = "sine"
                freq = int(tokens[ip + 2]) if tokens[ip + 2].isdigit() else 440
                self.audio.tone(freq, 0.5, 0.5, waveform)
                ip += 2

            elif token == "coin":
                self.sfx.coin()
                self.memory[self.pointer] = random.randint(0, 1)
                output.append("HEAD" if self.memory[self.pointer] else "TAIL")
            elif token == "dice":
                self.sfx.dice()
                self.memory[self.pointer] = random.randint(1, 6)
                output.append(str(self.memory[self.pointer]))
            elif token == "catnip":
                self.memory[self.pointer] = random.randint(0, 255)
                output.append(str(self.memory[self.pointer]))
            elif token == "box":
                prizes = ["fish", "yarn", "empty box", "mouse", "shiny thing", "nothing"]
                prize = random.choice(prizes)
                print(f"  box: {prize}")
                self.memory[self.pointer] = prizes.index(prize)
                if prize == "nothing":
                    self.sfx.lose_jingle()
                else:
                    self.sfx.win_jingle()
            elif token == "hunt":
                secret = random.randint(1, 10)
                print("  hunt: guess 1-10")
                for _ in range(10):
                    try:
                        guess = int(input("  guess> "))
                    except (ValueError, EOFError):
                        continue
                    if guess < secret:
                        print("    too low")
                    elif guess > secret:
                        print("    too high")
                    else:
                        self.sfx.win_jingle()
                        print("    caught!")
                        self.memory[self.pointer] = 1
                        break
                else:
                    print("    missed")
                    self.sfx.lose_jingle()
            elif token == "laser":
                print("  laser: press ENTER when ready")
                time.sleep(random.uniform(1.0, 4.0))
                print("    go!")
                start = time.time()
                try:
                    input()
                except EOFError:
                    pass
                elapsed = time.time() - start
                print(f"    {elapsed:.2f}s")
                self.memory[self.pointer] = int(elapsed * 100) % 256
                if elapsed < 0.3:
                    self.sfx.win_jingle()
                else:
                    self.sfx.lose_jingle()
            elif token == "rps" and ip + 1 < len(tokens):
                ip += 1
                moves = {"rock": 0, "paper": 1, "scissors": 2}
                player_move = tokens[ip]
                cpu_move = random.choice(list(moves.keys()))
                print(f"  rps: you={player_move} cpu={cpu_move}")
                pi = moves.get(player_move, -1)
                ci = moves[cpu_move]
                if pi == ci:
                    print("    tie")
                    self.memory[self.pointer] = 0
                elif pi == -1:
                    print("    invalid move")
                elif (pi - ci) % 3 == 1:
                    self.sfx.win_jingle()
                    print("    win")
                    self.memory[self.pointer] = 1
                else:
                    self.sfx.lose_jingle()
                    print("    lose")
                    self.memory[self.pointer] = 2

            elif token == "hash" and ip + 1 < len(tokens):
                ip += 1
                result = self.crypto.compute_hash(tokens[ip])
                output.append(result)
            elif token == "encrypt":
                if ip + 1 < len(tokens) and tokens[ip + 1] not in reserved_words:
                    ip += 1
                    data = tokens[ip]
                else:
                    j = self.pointer
                    chars = []
                    while j < MAX_MEMORY and self.memory[j] != 0:
                        chars.append(chr(self.memory[j] if 32 <= self.memory[j] <= 126 else 63))
                        j += 1
                    data = "".join(chars) if chars else "empty"
                result = self.crypto.encrypt(data)
                output.append(result)
            elif token == "decrypt":
                if ip + 1 < len(tokens) and tokens[ip + 1] not in reserved_words:
                    ip += 1
                    data = tokens[ip]
                else:
                    j = self.pointer
                    chars = []
                    while j < MAX_MEMORY and self.memory[j] != 0:
                        chars.append(chr(self.memory[j] if 32 <= self.memory[j] <= 126 else 63))
                        j += 1
                    data = "".join(chars) if chars else "empty"
                result = self.crypto.decrypt(data)
                if result:
                    output.append(result)
                else:
                    output.append("decrypt_failed")
            elif token == "scan" and ip + 1 < len(tokens):
                ip += 1
                target = tokens[ip]
                if target not in ("localhost", "127.0.0.1", "example.com"):
                    raise SecurityError(f"scan target not allowed: {target}")
                print(f"  scanning {target}")
                for port in (22, 80, 443):
                    status = "open" if self.crypto.scan_port(target, port) else "closed"
                    print(f"    port {port}: {status}")
                    time.sleep(0.3)
            elif token == "pwdgen" and ip + 1 < len(tokens):
                ip += 1
                style = tokens[ip]
                if style not in ("strong", "passphrase", "pin"):
                    style = "strong"
                password = self.crypto.generate_password(16, style)
                start = self.pointer
                for j, ch in enumerate(password):
                    if start + j < MAX_MEMORY:
                        self.memory[start + j] = ord(ch) % 256
                self.pointer = start
                output.append(password)
            elif token == "cert" and ip + 1 < len(tokens):
                ip += 1
                name = tokens[ip]
                lines = [
                    "=" * 40,
                    f"  CERTIFICATE: {name}",
                    "  issuer: MeowLang CA",
                    "  status: valid",
                    "=" * 40,
                ]
                print("\n".join(lines))

            elif token == "list" and ip + 1 < len(tokens):
                ip += 1
                name = tokens[ip]
                values = []
                while ip + 1 < len(tokens) and tokens[ip + 1] not in reserved_words:
                    ip += 1
                    try:
                        values.append(int(tokens[ip]) % 256)
                    except ValueError:
                        values.append(0)
                if len(values) > 1000:
                    raise SecurityError("array size exceeds limit")
                self.arrays[name] = values
                ip += 1
            elif token == "arrget" and ip + 1 < len(tokens):
                ip += 1
                name = tokens[ip]
                arr = self.arrays.get(name, [])
                idx = self.memory[self.pointer]
                if idx < len(arr):
                    self.memory[self.pointer] = arr[idx]
            elif token == "arrset" and ip + 2 < len(tokens):
                ip += 1
                name = tokens[ip]
                idx = int(tokens[ip + 1])
                arr = self.arrays.get(name, [])
                if idx < len(arr):
                    arr[idx] = self.memory[self.pointer]
                ip += 1
            elif token == "arrlen" and ip + 1 < len(tokens):
                ip += 1
                name = tokens[ip]
                self.memory[self.pointer] = len(self.arrays.get(name, []))

            elif token == "draw" and ip + 1 < len(tokens):
                ip += 1
                shape = tokens[ip]
                if shape == "box" and ip + 2 < len(tokens):
                    w = int(tokens[ip + 1])
                    h = int(tokens[ip + 2])
                    ip += 2
                    self.canvas.rect(
                        self.memory[self.pointer] % 40,
                        (self.memory[self.pointer + 1]) % 20,
                        w, h
                    )
                elif shape == "circle" and ip + 1 < len(tokens):
                    r = int(tokens[ip + 1])
                    ip += 1
                    self.canvas.circle(
                        self.memory[self.pointer] % 40,
                        self.memory[self.pointer + 1] % 20,
                        r
                    )
                elif shape == "text" and ip + 1 < len(tokens):
                    ip += 1
                    self.canvas.text(
                        self.memory[self.pointer] % 40,
                        self.memory[self.pointer + 1] % 20,
                        tokens[ip]
                    )
                elif shape == "show":
                    self.canvas.render()

            elif token == "fork" and ip + 1 < len(tokens):
                if len(self.threads) > 10:
                    raise SecurityError("thread limit exceeded")
                ip += 1
            elif token == "spawn" and ip + 1 < len(tokens):
                import threading, copy
                ip += 1
                name = tokens[ip]
                if name in self.programs:
                    mem_copy = copy.deepcopy(self.memory)
                    vars_copy = copy.deepcopy(self.variables)
                    progs_copy = copy.deepcopy(self.programs)
                    funcs_copy = copy.deepcopy(self.functions)
                    def thread_run(src, mem, vars_dict, progs, funcs):
                        saved_mem = self.memory
                        saved_vars = self.variables
                        saved_progs = self.programs
                        saved_funcs = self.functions
                        self.memory = mem
                        self.variables = vars_dict
                        self.programs = progs
                        self.functions = funcs
                        try:
                            self._execute(src)
                        finally:
                            self.memory = saved_mem
                            self.variables = saved_vars
                            self.programs = saved_progs
                            self.functions = saved_funcs
                    t = threading.Thread(target=thread_run, args=(self.programs[name], mem_copy, vars_copy, progs_copy, funcs_copy))
                    t.start()
                    self.threads.append(t)
                    print(f"  spawned {name}")
                else:
                    print(f"  not found: {name}")
            elif token == "wait":
                for t in self.threads:
                    t.join(timeout=5)
                self.threads.clear()
            elif token == "require" and ip + 1 < len(tokens):
                ip += 1
                filename = tokens[ip]
                try:
                    with open(filename, 'r') as f:
                        src = f.read()
                    self.execute(src)
                except FileNotFoundError:
                    print(f"  file not found: {filename}")
            elif token == "os_exec" and ip + 1 < len(tokens):
                ip += 1
                cmd = tokens[ip]
                try:
                    self._validate_exec(cmd)
                    import subprocess as _sp
                    import datetime as _dt
                    print(f"  os_exec: {cmd}")
                    result = _sp.run(cmd.split(), capture_output=True, text=True, timeout=10)
                    if result.stdout:
                        output.append(result.stdout.strip())
                    with open("/tmp/meow_os.log", "a") as log:
                        log.write(f"[{_dt.datetime.now()}] {cmd} | OK\n")
                except SecurityError as e:
                    print(f"  [SECURITY] {e}")
                except _sp.TimeoutExpired:
                    print("  timeout")
                except FileNotFoundError:
                    print("  not found")

            elif token == "zoomies":
                print("  zoomies mode")
                for _ in range(5):
                    ip += 1
                    if ip < len(tokens):
                        if tokens[ip] == "mew":
                            self.memory[self.pointer] = (self.memory[self.pointer] + 1) % 256
                        elif tokens[ip] == "nya":
                            self.pointer = (self.pointer + 1) % MAX_MEMORY
            elif token == "loaf":
                print("  loaf mode")
                time.sleep(1)
            elif token == "tor":
                self.proxy_enabled = True
                self.proxy_addr = "socks5h://127.0.0.1:9050"
                print("  tor mode enabled")
            elif token == "proxy" and ip + 1 < len(tokens):
                ip += 1
                self.proxy_addr = tokens[ip]
                self.proxy_enabled = True
                print(f"  proxy set: {self.proxy_addr}")
                self.proxy_enabled = True
                self.proxy_addr = "socks5h://127.0.0.1:9050"
                ip += 1
                url = tokens[ip]
                if not url.startswith("http"):
                    url = "https://" + url
                html = self._fetch(url, use_proxy=True)
                import re
                body = re.sub(r'<[^>]+>', ' ', html)
                body = re.sub(r'\s+', ' ', body).strip()
                links = re.findall(r"https?://[^\s\"\'<>]+", html)
                print(f"  --- {url} ---")
                print(body[:500])
                if links:
                    print(f"  --- links ({len(links)}) ---")
                    for l in links[:10]:
                        print(f"  {l}")
                print("  --- end ---")
            elif token == "ghost":
                self.proxy_enabled = True
                self.proxy_addr = "socks5h://127.0.0.1:9050"
                print("  ghost mode")
            elif token == "browse" and ip + 1 < len(tokens):
                ip += 1
                url = tokens[ip]
                if not url.startswith("http"):
                    url = "https://" + url
                import re
                html = self._fetch(url, use_proxy=True)
                text = re.sub(r"<[^>]+>", " ", html)
                text = re.sub(r"\s+", " ", text).strip()
                links = re.findall(r"https?://[^\s<>\"\']+", html)
                print(f"  --- {url} ---")
                print(text[:500])
                if links:
                    print(f"  --- links ({len(links)}) ---")
                    for lnk in links[:10]:
                        print(f"  {lnk}")
                print("  --- end ---")
            elif token == "jsonp" and ip + 1 < len(tokens):
                ip += 1
                try:
                    import json as _json
                    data = _json.loads(tokens[ip])
                    output.append(_json.dumps(data, indent=2, ensure_ascii=False))
                except:
                    output.append("invalid json")
            elif token == "b64e" and ip + 1 < len(tokens):
                ip += 1
                import base64 as _b64
                output.append(_b64.b64encode(tokens[ip].encode()).decode())
            elif token == "b64d" and ip + 1 < len(tokens):
                ip += 1
                import base64 as _b64
                try:
                    output.append(_b64.b64decode(tokens[ip]).decode())
                except:
                    output.append("invalid base64")
            elif token == "urle" and ip + 1 < len(tokens):
                ip += 1
                import urllib.parse as _up
                output.append(_up.quote(tokens[ip], safe=''))
            elif token == "urld" and ip + 1 < len(tokens):
                ip += 1
                import urllib.parse as _up
                output.append(_up.unquote(tokens[ip]))
            elif token == "uuid":
                import uuid as _uuid
                output.append(str(_uuid.uuid4()))
            elif token == "qrc" and ip + 1 < len(tokens):
                ip += 1
                import shutil as _sh
                qr_text = tokens[ip]
                try:
                    import qrcode as _qr
                    img = _qr.make(qr_text)
                    img.save("/tmp/meow_qr.png")
                    print("  QR saved to /tmp/meow_qr.png")
                except ImportError:
                    output.append(qr_text)
                    print("  install qrcode: pip install qrcode[pil]")
            elif token == "date":
                import datetime as _dt
                output.append(_dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            elif token == "timer" and ip + 1 < len(tokens):
                ip += 1
                try:
                    secs = int(tokens[ip])
                    print(f"  timer: {secs}s")
                    time.sleep(secs)
                    print("  done!")
                except:
                    pass
            elif token == "count" and ip + 1 < len(tokens):
                ip += 1
                target = tokens[ip]
                j = self.pointer
                n = 0
                while j < MAX_MEMORY and self.memory[j] != 0:
                    if chr(self.memory[j]) == target:
                        n += 1
                    j += 1
                self.memory[self.pointer] = min(n, 255)
            elif token == "sort":
                arr = [self.memory[j] for j in range(self.pointer, min(self.pointer + 50, MAX_MEMORY)) if self.memory[j] != 0]
                arr.sort()
                for j, v in enumerate(arr):
                    if self.pointer + j < MAX_MEMORY:
                        self.memory[self.pointer + j] = v
                for j in range(len(arr), 50):
                    if self.pointer + j < MAX_MEMORY:
                        self.memory[self.pointer + j] = 0
            elif token == "pick" and ip + 1 < len(tokens):
                ip += 1
                options = []
                while ip < len(tokens) and tokens[ip] not in reserved_words:
                    options.append(tokens[ip])
                    ip += 1
                ip -= 1
                if options:
                    chosen = random.choice(options)
                    output.append(chosen)
                    for j, ch in enumerate(chosen):
                        if self.pointer + j < MAX_MEMORY:
                            self.memory[self.pointer + j] = ord(ch) % 256
            elif token == "ip":
                try:
                    import urllib.request as _ur
                    resp = _ur.urlopen("https://ifconfig.me", timeout=5).read().decode().strip()
                    output.append(str(resp))
                except Exception as e:
                    output.append("offline")
            elif token == "ping" and ip + 1 < len(tokens):
                ip += 1
                host = tokens[ip]
                import subprocess as _sp
                try:
                    result = _sp.run(["ping", "-c", "2", "-W", "2", host], capture_output=True, text=True, timeout=5)
                    output.append("up" if result.returncode == 0 else "down")
                except:
                    output.append("timeout")
            elif token == "edit" and ip + 1 < len(tokens):
                ip += 1
                name = tokens[ip]
                print(f"  editing {name} (type 'end' to finish):")
                lines = []
                while True:
                    try:
                        line = input(f"  {len(lines)+1:02d} ")
                        if line.strip().lower() == "end":
                            break
                        lines.append(line)
                    except (EOFError, KeyboardInterrupt):
                        break
                self.programs[name] = "\n".join(lines)
                print(f"  saved ({len(lines)} lines)")
            elif token == "code" and ip + 1 < len(tokens):
                ip += 1
                name = tokens[ip]
                if name in self.programs:
                    src = self.programs[name]
                    result = self.execute(src)
                    if result and result.strip():
                        print(result)
                else:
                    print(f"  not found: {name}")
            elif token == "list":
                for k, v in self.programs.items():
                    count = v.count("\n") + 1
                    print(f"  {k}: {count} lines")
            elif token == "help":
                print("  edit NAME  - write program")
                print("  code NAME  - run program")
                print("  list       - show programs")
                print("  save FILE  - save program to file")
                print("  load FILE  - load program from file")
            elif token == "anon":
                self.proxy_enabled = False
                print("  direct mode")
            elif token == "mute":
                self.muted = True
                print("  muted")
            elif token == "unmute":
                self.muted = False
                print("  unmuted")
            elif token == "bap":
                print("  bap")
                ip = len(tokens)
            elif token == "stretch":
                print("  stretch")
                for j in range(self.pointer, min(self.pointer + 5, MAX_MEMORY)):
                    self.memory[j] = self.memory[self.pointer]

            elif token == "fetch" and ip + 1 < len(tokens):
                ip += 1
                url = tokens[ip]
                print(f"  fetching {url}")
                body = self._fetch(url)
                for j, ch in enumerate(body[:100]):
                    if self.pointer + j < MAX_MEMORY:
                        self.memory[self.pointer + j] = ord(ch) % 256
                print(f"  received {len(body)} bytes")

            elif token == "dbopen" and ip + 1 < len(tokens):
                ip += 1
                path = tokens[ip]
                self._validate_path(path)
                try:
                    self.database = sqlite3.connect(path)
                    self.database.execute(
                        "CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY, value TEXT)"
                    )
                    print("  database opened")
                except Exception as exc:
                    print(f"  db error: {exc}")
            elif token == "dbset" and ip + 1 < len(tokens):
                ip += 1
                key = tokens[ip]
                if ip + 1 < len(tokens) and tokens[ip + 1] not in reserved_words:
                    value = tokens[ip + 1]
                    ip += 1
                else:
                    value = str(self.memory[self.pointer])
                if self.database:
                    self.database.execute(
                        "INSERT OR REPLACE INTO kv VALUES (?, ?)", (key, value)
                    )
                    self.database.commit()
                    print("  db saved")
            elif token == "dbget" and ip + 1 < len(tokens):
                ip += 1
                key = tokens[ip]
                if self.database:
                    row = self.database.execute(
                        "SELECT value FROM kv WHERE key = ?", (key,)
                    ).fetchone()
                    if row:
                        for j, ch in enumerate(row[0][:100]):
                            if self.pointer + j < MAX_MEMORY:
                                self.memory[self.pointer + j] = ord(ch) % 256
                        print("  db found")

            elif token == "import" and ip + 1 < len(tokens):
                ip += 1
                module_name = tokens[ip]
                if SAFE_MODE and module_name not in ALLOWED_IMPORTS:
                    raise SecurityError(f"import not allowed: {module_name}")
                try:
                    self.modules[module_name] = __import__(module_name)
                    print(f"  imported {module_name}")
                except ImportError:
                    print(f"  import failed: {module_name}")

            elif token == "var" and ip + 2 < len(tokens):
                try:
                    self.variables[tokens[ip + 1]] = int(tokens[ip + 2]) % 256
                except ValueError:
                    self.variables[tokens[ip + 1]] = 0
                ip += 2
            elif token == "set" and ip + 1 < len(tokens):
                self.variables[tokens[ip + 1]] = self.memory[self.pointer]
                ip += 1
            elif token == "get" and ip + 1 < len(tokens):
                self.memory[self.pointer] = self.variables.get(tokens[ip + 1], 0)
                ip += 1
            elif token == "print" and ip + 1 < len(tokens):
                output.append(str(self.variables.get(tokens[ip + 1], "?")))
                ip += 1

            # === HashMaps (Fixed v2.5.1) ===
            elif token == "dict" and ip + 1 < len(tokens):
                self.variables[tokens[ip + 1]] = {}
                ip += 1
            elif token == "dictset" and ip + 2 < len(tokens):
                var_name = tokens[ip + 1]
                dict_key = tokens[ip + 2]
                ip += 2
                if var_name not in self.variables or not isinstance(self.variables[var_name], dict):
                    self.variables[var_name] = {}
                self.variables[var_name][dict_key] = self.memory[self.pointer]
            elif token == "dictget" and ip + 2 < len(tokens):
                var_name = tokens[ip + 1]
                dict_key = tokens[ip + 2]
                ip += 2
                if var_name in self.variables and isinstance(self.variables[var_name], dict):
                    val = self.variables[var_name].get(dict_key, 0)
                    try:
                        self.memory[self.pointer] = int(val) % 256
                    except (ValueError, TypeError):
                        self.memory[self.pointer] = 0
                else:
                    self.memory[self.pointer] = 0

            # === Assertions (Fixed v2.5.1) ===
            elif token == "assert" and ip + 1 < len(tokens):
                ip += 1
                expected = int(tokens[ip])
                if self.memory[self.pointer] != expected:
                    print(f"[ASSERT FAILED] expected {expected} got {self.memory[self.pointer]} at ptr {self.pointer}")
                    return ""

            # === String Concat (Fixed v2.5.1) ===
            elif token == "dictkeys" and ip + 1 < len(tokens):
                ip += 1
                name = tokens[ip]
                if name in self.variables and isinstance(self.variables[name], dict):
                    output.append(str(list(self.variables[name].keys())))
                else:
                    output.append("[]")
            elif token == "dictvals" and ip + 1 < len(tokens):
                ip += 1
                name = tokens[ip]
                if name in self.variables and isinstance(self.variables[name], dict):
                    output.append(str(list(self.variables[name].values())))
                else:
                    output.append("[]")
            elif token == "concat" and ip + 2 < len(tokens):
                var1 = tokens[ip + 1]
                var2 = tokens[ip + 2]
                ip += 2
                val1 = str(self.variables.get(var1, var1))
                val2 = str(self.variables.get(var2, var2))
                self.variables[var1] = val1 + val2

            elif token == "call" and ip + 1 < len(tokens):
                name = tokens[ip + 1]
                if len(call_stack) > 100:
                    raise SecurityError("call stack overflow")
                if name in self.functions:
                    call_stack.append(ip + 2)
                    ip = self.functions[name][0] - 1
                ip += 1
            elif token == "endfunc":
                if call_stack:
                    ip = call_stack.pop() - 1
            elif token == "return":
                if call_stack:
                    ip = call_stack.pop() - 1

            elif token == "jump" and ip + 1 < len(tokens):
                label = tokens[ip + 1]
                if label in self.labels:
                    ip = self.labels[label] - 1
                ip += 1
            elif token == "jif" and ip + 1 < len(tokens):
                label = tokens[ip + 1]
                if self.memory[self.pointer] != 0 and label in self.labels:
                    ip = self.labels[label] - 1
                ip += 1

            elif token == "mrr":
                self.memory[self.pointer] = (self.memory[self.pointer] - 1) % 256
            elif token == "prr":
                self.memory[self.pointer] = 0
            elif token == "nya":
                self.pointer = (self.pointer + 1) % MAX_MEMORY
            elif token == "aww":
                self.pointer = (self.pointer - 1) % MAX_MEMORY
            elif token == "paw":
                try:
                    self.memory[self.pointer] = int(input("input> ")) % 256
                except (ValueError, EOFError):
                    self.memory[self.pointer] = 0
            elif token == "meow":
                output.append(str(self.memory[self.pointer]))
            elif token == "mrow":
                val = self.memory[self.pointer]
                output.append(chr(val) if 32 <= val <= 126 else f"[{val}]")
            elif token == "yell" and ip + 1 < len(tokens):
                output.append(tokens[ip + 1])
                ip += 1

            elif token == "bonk":
                self.memory[self.pointer] = (self.memory[self.pointer] + self.memory[self.pointer + 1]) % 256
            elif token == "yeet":
                self.memory[self.pointer] = (self.memory[self.pointer] - self.memory[self.pointer + 1]) % 256
            elif token == "boop":
                self.memory[self.pointer] = (self.memory[self.pointer] * self.memory[self.pointer + 1]) % 256
            elif token == "snip":
                divisor = self.memory[self.pointer + 1]
                self.memory[self.pointer] = self.memory[self.pointer] // divisor if divisor else 0
            elif token == "bonk?":
                divisor = self.memory[self.pointer + 1]
                self.memory[self.pointer] = self.memory[self.pointer] % divisor if divisor else 0
            elif token == "+":
                self.memory[self.pointer] = (self.memory[self.pointer] + self.memory[self.pointer + 1]) % 256
            elif token == "-":
                self.memory[self.pointer] = (self.memory[self.pointer] - self.memory[self.pointer + 1]) % 256
            elif token == "*":
                self.memory[self.pointer] = (self.memory[self.pointer] * self.memory[self.pointer + 1]) % 256
            elif token == "/":
                b = self.memory[self.pointer + 1]
                self.memory[self.pointer] = self.memory[self.pointer] // b if b else 0
            elif token == "%":
                b = self.memory[self.pointer + 1]
                self.memory[self.pointer] = self.memory[self.pointer] % b if b else 0
            elif token == "**":
                val = self.memory[self.pointer]
                exp = self.memory[self.pointer + 1]
                self.memory[self.pointer] = (val ** min(exp, 10)) % 256
            elif token == "zoom":
                val = self.memory[self.pointer]
                self.memory[self.pointer] = (val * val) % 256

            elif token == "blep":
                if self.pointer + 1 < MAX_MEMORY:
                    self.memory[self.pointer + 1] = self.memory[self.pointer]
            elif token == "swap":
                if self.pointer + 1 < MAX_MEMORY:
                    self.memory[self.pointer], self.memory[self.pointer + 1] = (
                        self.memory[self.pointer + 1],
                        self.memory[self.pointer],
                    )
            elif token == "stash":
                self.stack.append(self.memory[self.pointer])
            elif token == "grab":
                if self.stack:
                    self.memory[self.pointer] = self.stack.pop()

            elif token == "if":
                self._check_operation_limit()
                if self.memory[self.pointer] == 0:
                    if ip in control_map:
                        ip = control_map[ip]
                    else:
                        depth = 1
                        while depth > 0 and ip + 1 < len(tokens):
                            ip += 1
                            if tokens[ip] == "if": depth += 1
                            elif tokens[ip] == "endif": depth -= 1
                            elif tokens[ip] == "else" and depth == 1: depth -= 1
            elif token == "else":
                depth = 1
                while depth > 0 and ip + 1 < len(tokens):
                    ip += 1
                    if tokens[ip] == "if": depth += 1
                    elif tokens[ip] == "endif": depth -= 1
                ip -= 1
            elif token == "endif":
                pass
            elif token == "purr":
                if self.memory[self.pointer] == 0 and ip in loop_map:
                    ip = loop_map[ip]
            elif token == "hiss":
                if self.memory[self.pointer] != 0 and ip in loop_map:
                    ip = loop_map[ip]

            elif token == "sniff":
                self.memory[self.pointer] = 1 if self.memory[self.pointer] == self.memory[self.pointer + 1] else 0
            elif token == "pounce":
                self.memory[self.pointer] = 1 if self.memory[self.pointer] > self.memory[self.pointer + 1] else 0
            elif token == "hide":
                self.memory[self.pointer] = 1 if self.memory[self.pointer] < self.memory[self.pointer + 1] else 0
            elif token == "not":
                self.memory[self.pointer] = 1 if self.memory[self.pointer] == 0 else 0
            elif token == "and":
                self.memory[self.pointer] = 1 if (self.memory[self.pointer] and self.memory[self.pointer + 1]) else 0
            elif token == "or":
                self.memory[self.pointer] = 1 if (self.memory[self.pointer] or self.memory[self.pointer + 1]) else 0

            elif token == "str" and ip + 1 < len(tokens):
                text = tokens[ip + 1]
                for j, ch in enumerate(text):
                    if self.pointer + j < MAX_MEMORY:
                        self.memory[self.pointer + j] = ord(ch) % 256
                ip += 1
            elif token == "puts":
                chars = []
                j = self.pointer
                while j < MAX_MEMORY and self.memory[j] != 0:
                    val = self.memory[j]
                    chars.append(chr(val) if 32 <= val <= 126 else "?")
                    j += 1
                output.append("".join(chars))

            elif token == "save" and ip + 1 < len(tokens):
                path = tokens[ip + 1]
                self._validate_path(path)
                data = [str(x) for x in self.memory[:50]]
                if len(json.dumps(data)) > MAX_FILE_SIZE:
                    raise SecurityError("file size exceeds limit")
                with open(path, "w") as fh:
                    json.dump(data, fh)
                print("  saved")
                ip += 1
            elif token == "load" and ip + 1 < len(tokens):
                path = tokens[ip + 1]
                self._validate_path(path)
                try:
                    if os.path.getsize(path) > MAX_FILE_SIZE:
                        raise SecurityError("file size exceeds limit")
                    with open(path) as fh:
                        records = json.load(fh)
                    for j, val in enumerate(records[:100]):
                        self.memory[j] = int(val) % 256
                    print("  loaded")
                except FileNotFoundError:
                    print("  file not found")
                except Exception as exc:
                    print(f"  load error: {exc}")
                ip += 1

            elif token == "exec" and ip + 1 < len(tokens):
                command = tokens[ip + 1]
                self._validate_exec(command)
                print(f"  exec: {command}")
                try:
                    subprocess.run(command, shell=True, timeout=10)
                except subprocess.TimeoutExpired:
                    raise SecurityError("exec timeout")
                ip += 1

            elif token == "server":
                import http.server
                import socketserver
                port = self.memory[self.pointer] if self.memory[self.pointer] > 0 else 8080
                routes = dict(self.variables.get("_routes", {}))
                class MeowHandler(http.server.SimpleHTTPRequestHandler):
                    def do_GET(self):
                        path = self.path
                        if path in routes:
                            self.send_response(200)
                            self.send_header("Content-type", "text/html; charset=utf-8")
                            self.end_headers()
                            self.wfile.write(routes[path].encode())
                        else:
                            self.send_response(404)
                            self.send_header("Content-type", "text/html; charset=utf-8")
                            self.end_headers()
                            self.wfile.write(b"<h1>404 - Mouse not found!</h1>")
                    def log_message(self, format, *args):
                        print(f"  🐾 {args[0]}")
                print(f"  🌐 Server running at http://localhost:{port}")
                print(f"  Press Ctrl+C to stop")
                try:
                    with socketserver.TCPServer(("", port), MeowHandler) as httpd:
                        httpd.serve_forever()
                except KeyboardInterrupt:
                    print("  Server stopped")
            elif token == "route" and ip + 2 < len(tokens):
                ip += 1
                path = tokens[ip]
                ip += 1
                content = tokens[ip]
                if "_routes" not in self.variables:
                    self.variables["_routes"] = {}
                self.variables["_routes"][path] = content
                print(f"  route {path} added")
            elif token == "html" and ip + 1 < len(tokens):
                ip += 1
                content = tokens[ip]
                html = f"<html><head><meta charset='utf-8'></head><body>{content}</body></html>"
                output.append(html)
            elif token == "css" and ip + 1 < len(tokens):
                ip += 1
                content = tokens[ip]
                css = f"<style>{content}</style>"
                output.append(css)
            elif token == "wipe":
                os.system("clear")
            elif token == "nap":
                delay = self.memory[self.pointer] / 100 if self.memory[self.pointer] > 0 else 0.5
                time.sleep(min(delay, 5))
            elif token == "time":
                self.memory[self.pointer] = int(time.time()) % 256
            elif token == "rnd":
                self.memory[self.pointer] = random.randint(0, 255)
            elif token == "len":
                count = 0
                j = self.pointer
                while j < MAX_MEMORY and self.memory[j] != 0 and count < 1000:
                    count += 1
                    j += 1
                self.memory[self.pointer] = count

            ip += 1

        if self.database:
            self.database.close()
            self.database = None

        return " ".join(output)


def main():
    import sys

    interpreter = MeowLang()

    if len(sys.argv) > 1:
        try:
            with open(sys.argv[1]) as file_handle:
                source = file_handle.read()
            result = interpreter.execute(source)
            if result.strip():
                print(result)
        except FileNotFoundError:
            print(f"file not found: {sys.argv[1]}")
        except Exception as exc:
            print(f"error: {exc}")
    else:
        print(f"MeowLang v{__version__}")
        print("type commands or 'exit'")
        print()
        while True:
            try:
                line = input(">> ")
                if line.strip().lower() == "exit":
                    break
                if line.strip():
                    result = interpreter.execute(line)
                    if result.strip():
                        print(result)
            except (EOFError, KeyboardInterrupt):
                print()
                break


if __name__ == "__main__":
    main()
