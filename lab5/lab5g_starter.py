"""Week 5 Lab - Hash Tables (Grokking Algorithms, chapter 5): STARTER CODE.

Complete every function marked TODO. Run this file to test your work:
    python lab5g_starter.py
Each test prints PASS, FAIL or TODO. Do not change the test functions.
"""
import hashlib
import random
import string

# ------------------------------------------------------------------ hash functions
PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
          73, 79, 83, 89, 97, 101]
LETTER_PRIME = dict(zip(string.ascii_lowercase, PRIMES))


def hash_a(s, m):
    """Book function A: always 1."""
    return 1 % m


def hash_b(s, m):
    """TODO B1: return the length of the string, mod m."""
    return len(s) % m


def hash_c(s, m):
    """TODO B1: return the index of the first letter (a = 0, b = 1, ...), mod m. Use
    s[0].lower()."""
    return (ord(s[0].lower()) - ord("a")) % m


def hash_d(s, m):
    """TODO B1: add LETTER_PRIME[ch] for every letter of s.lower() (ignore other
    characters), mod m."""
    return sum(LETTER_PRIME[ch] for ch in s.lower() if ch in LETTER_PRIME) % m


def hash_poly(s, m, base=31, mod=(1 << 61) - 1):
    """TODO B1: Horner's rule: h = (h * base + ord(ch)) % mod for every character;
    return h % m."""
    h = 0
    for ch in s:
        h = (h * base + ord(ch)) % mod
    return h % m


def hash_python(s, m):
    return hash(s) % m


def hash_sha256(s, m):
    """The book suggests SHA: excellent spread, but slow for tables."""
    return int.from_bytes(hashlib.sha256(s.encode()).digest()[:8], "big") % m


BOOK_FUNCTIONS = {"A: always 1": hash_a, "B: length": hash_b, "C: first letter": hash_c,
                  "D: prime-letter sum": hash_d}
GOOD_FUNCTIONS = {"polynomial (base 31)": hash_poly, "Python hash()": hash_python,
                  "SHA-256": hash_sha256}


# ------------------------------------------------------------------ chaining with linked lists
class Node:
    __slots__ = ("key", "value", "next")

    def __init__(self, key, value, next=None):
        self.key, self.value, self.next = key, value, next


class HashTable:
    """An array of slots; each slot holds a singly linked list of (key, value) nodes."""

    def __init__(self, size=8, max_load=0.7, hash_fn=hash_python, resize=True):
        self.size = size
        self.slots = [None] * size
        self.count = 0
        self.max_load = max_load
        self.hash_fn = hash_fn
        self.resize_enabled = resize
        self.steps = 0          # nodes visited (key comparisons)
        self.moves = 0          # nodes re-inserted by resizing
        self.resizes = 0

    def _index(self, key):
        return self.hash_fn(key, self.size)

    def load_factor(self):
        """TODO C1: number of items divided by number of slots."""
        return self.count / self.size

    def get(self, key, default=None):
        """TODO C2: walk the linked list in slot self._index(key); add 1 to self.steps
        per node; return the value or default."""
        node = self.slots[self._index(key)]
        while node is not None:
            self.steps += 1
            if node.key == key:
                return node.value
            node = node.next
        return default


    def __contains__(self, key):
        missing = object()
        return self.get(key, missing) is not missing

    def put(self, key, value):
        """TODO C2: if the key is in its slot list, update the value (count steps).
        Otherwise add a new Node at the front of the list, count += 1, and call
        self._resize(2 * self.size) if resize_enabled and load_factor() > max_load."""
        idx = self._index(key)
        node = self.slots[idx]

        while node is not None:
            self.steps += 1
            if node.key == key:
                node.value = value
                return
            node = node.next

        self.slots[idx] = Node(key, value, self.slots[idx])
        self.count += 1

        if self.resize_enabled and self.load_factor() > self.max_load:
            self._resize(2 * self.size)

    def delete(self, key):
        """TODO C2: unlink the node with this key from its list (count steps); count -=
        1; return True, or False if absent."""
        idx = self._index(key)
        prev, node = None, self.slots[idx]

        while node is not None:
            self.steps += 1
            if node.key == key:
                if prev is None:
                    self.slots[idx] = node.next
                else:
                    prev.next = node.next
                self.count -= 1
                return True
            prev, node = node, node.next

        return False

    def _resize(self, new_size):
        """TODO C3: make a new array of new_size empty slots and re-insert every node
        with the hash function (count self.moves); self.resizes += 1."""
        old_slots = self.slots
        self.size = new_size
        self.slots = [None] * new_size

        for head in old_slots:
            node = head
            while node is not None:
                nxt = node.next
                idx = self._index(node.key)
                node.next = self.slots[idx]
                self.slots[idx] = node
                self.moves += 1
                node = nxt

        self.resizes += 1


    def chain_lengths(self):
        out = []
        for head in self.slots:
            n, node = 0, head
            while node:
                n, node = n + 1, node.next
            out.append(n)
        return out

    def items(self):
        for head in self.slots:
            node = head
            while node:
                yield node.key, node.value
                node = node.next


# (LinearProbingTable is a stretch task: see the lab handout)


# ------------------------------------------------------------------ mini challenge: LRU cache
class _DNode:
    __slots__ = ("key", "value", "prev", "next")

    def __init__(self, key=None, value=None):
        self.key, self.value, self.prev, self.next = key, value, None, None


class LRUCache:
    """Bounded cache: dict for O(1) lookup + doubly linked list for recency order."""

    def __init__(self, capacity):
        self.capacity = capacity
        self.map = {}
        self.head, self.tail = _DNode(), _DNode()          # sentinels: head = most recent
        self.head.next, self.tail.prev = self.tail, self.head
        self.hits = self.misses = self.evictions = 0

    def _unlink(self, n):
        n.prev.next, n.next.prev = n.next, n.prev

    def _push_front(self, n):
        n.prev, n.next = self.head, self.head.next
        self.head.next.prev = n
        self.head.next = n

    def get(self, key, compute):
        """TODO Challenge: on a hit move the node to the front and return its value
        (hits += 1). On a miss call compute(key), add a node at the front, and if
        over capacity remove the node before the tail sentinel (evictions += 1)."""
        if key in self.map:
            self.hits += 1
            node = self.map[key]
            self._unlink(node)
            self._push_front(node)
            return node.value

        self.misses += 1
        value = compute(key)
        node = _DNode(key, value)
        self.map[key] = node
        self._push_front(node)

        if len(self.map) > self.capacity:
            old = self.tail.prev
            self._unlink(old)
            del self.map[old.key]
            self.evictions += 1

        return value

    def keys_by_recency(self):
        out, n = [], self.head.next
        while n is not self.tail:
            out.append(n.key)
            n = n.next
        return out


# ======================================================== tests (do not edit)
def run(name, fn):
    try:
        fn()
        print(f"PASS  {name}")
    except NotImplementedError:
        print(f"TODO  {name}")
    except AssertionError as e:
        print(f"FAIL  {name}  {e}")


def test_book_hashes():
    assert hash_b("Esther", 10) == 6 and hash_b("AAAA", 10) == 4, "B: length"
    assert hash_c("Ben", 10) == 1 and hash_c("Watchmen", 10) == 2, "C: first letter mod m"
    assert hash_d("bag", 10) == 2, "D: the book's worked example b + a + g = 22 -> 2"
    assert hash_d("Dan", 10) == 2, "D ignores case: d + a + n = 7 + 2 + 43 = 52 -> 2"


def test_poly_hash():
    assert hash_poly("ab", 1000) == (97 * 31 + 98) % 1000, "Horner's rule with base 31"
    different = hash_poly("listen", 1 << 30) != hash_poly("silent", 1 << 30)
    assert different, "anagrams must get different hash values"


def test_table_vs_dict():
    rng = random.Random(1)
    t, ref = HashTable(), {}
    for _ in range(5000):
        k = rng.choice([f"item{rng.randrange(300)}", rng.randrange(300)])
        r = rng.random()
        if r < 0.5:
            t.put(k, r)
            ref[k] = r
        elif r < 0.75:
            assert t.delete(k) == (k in ref), "delete returns the wrong answer"
            ref.pop(k, None)
        else:
            assert t.get(k) == ref.get(k), "get returns the wrong value"
    assert t.count == len(ref) and dict(t.items()) == ref, "contents differ from dict"


def test_resize():
    t = HashTable(4, max_load=0.7)
    for k in range(200):
        t.put(k, k)
    assert t.load_factor() <= 0.7, "resize when the load factor exceeds 0.7"
    assert t.size >= 286 and t.resizes > 0, "the array must double"
    assert all(t.get(k) == k for k in range(200)), "items lost while resizing"


def test_lru_cache():
    c = LRUCache(2)
    f = lambda k: k.upper()
    assert c.get("a", f) == "A" and c.get("b", f) == "B"
    c.get("a", f)                      # a becomes most recent
    c.get("c", f)                      # evicts b, the least recently used
    assert c.keys_by_recency() == ["c", "a"], "wrong eviction order"
    assert (c.hits, c.misses, c.evictions) == (1, 3, 1), "wrong counters"


if __name__ == "__main__":
    run("Part B book hash functions B, C, D", test_book_hashes)
    run("Part B polynomial hash", test_poly_hash)
    run("Part C HashTable vs dict", test_table_vs_dict)
    run("Part C resizing at 0.7", test_resize)
    run("Challenge LRU cache", test_lru_cache)
