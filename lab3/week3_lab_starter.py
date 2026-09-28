"""Week 3 Lab - Advanced Trees: starter code.

Fill in every function marked TODO. Run this file to test your work:
    python week3_lab_starter.py
Each test prints PASS, FAIL or TODO. Do not change the test functions.
"""
import bisect
import random
import sys
import time

sys.setrecursionlimit(10000)


# ======================================================== Part A: plain BST
class BSTNode:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None


class BST:
    def __init__(self):
        self.root = None

    def insert(self, key):
        """TODO A1: iterative insertion (no recursion). Ignore duplicates."""
        raise NotImplementedError

    def search(self, key):
        """TODO A2: iterative search. Return True if key is present."""
        raise NotImplementedError

    def height(self):
        """TODO A3: height in edges (empty tree = -1). Must work for a
        7,999-level chain, so use an explicit stack or queue, not recursion."""
        raise NotImplementedError


# ======================================================== Part B: rotations
def rotate_left(x):
    """TODO B1: rotate left at x and return the new subtree root."""
    raise NotImplementedError


def rotate_right(y):
    """TODO B2: rotate right at y and return the new subtree root."""
    raise NotImplementedError


# ======================================================== Part C: AVL tree
class AVLNode:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None
        self.height = 0


def h(node):
    return node.height if node else -1


def update(node):
    node.height = 1 + max(h(node.left), h(node.right))


def balance(node):
    return h(node.left) - h(node.right)


class AVLTree:
    def __init__(self):
        self.root = None
        self.rotations = 0

    def rotate_left(self, x):
        """TODO C1: as rotate_left above, plus update heights (lower node first)
        and add 1 to self.rotations."""
        raise NotImplementedError

    def rotate_right(self, y):
        """TODO C2: mirror of rotate_left."""
        raise NotImplementedError

    def rebalance(self, node):
        """TODO C3: update node's height; if |BF| > 1 apply the LL, LR, RR
        or RL fix; return the (possibly new) subtree root."""
        raise NotImplementedError

    def insert(self, key):
        self.root = self._insert(self.root, key)

    def _insert(self, node, key):
        """TODO C4: recursive BST insertion that returns self.rebalance(node)."""
        raise NotImplementedError

    def search(self, key):
        cur = self.root
        while cur:
            if key == cur.key:
                return True
            cur = cur.left if key < cur.key else cur.right
        return False

    def height(self):
        return h(self.root)

    def is_valid(self):
        """TODO C5: return True only if (1) BST order holds, (2) every stored
        height is correct and (3) every balance factor is -1, 0 or +1."""
        raise NotImplementedError


# ======================================================== Part D: Red-Black validator
# A Red-Black tree is given as nested tuples: (key, colour, left, right)
# where colour is "R" or "B" and an empty child (NIL) is None.
def is_valid_rb(t):
    """TODO D3: return (True, black_height) for a valid Red-Black tree and
    (False, reason) otherwise. Check BST order and properties 2, 4 and 5.
    black_height counts the black nodes on any root-to-NIL path,
    including the root and the NIL itself."""
    raise NotImplementedError


# ======================================================== tests (do not edit)
def run(name, fn):
    try:
        fn()
        print(f"PASS  {name}")
    except NotImplementedError:
        print(f"TODO  {name}")
    except AssertionError as e:
        print(f"FAIL  {name}  {e}")


def inorder(n, out):
    if n:
        inorder(n.left, out)
        out.append(n.key)
        inorder(n.right, out)
    return out


def test_bst():
    t = BST()
    for k in range(2000):
        t.insert(k)
    assert t.height() == 1999, "sorted input should give a chain"
    assert t.search(1234) and not t.search(5000)


def test_rotations():
    rng = random.Random(0)
    for _ in range(100):
        t = BST()
        for k in rng.sample(range(500), 40):
            t.insert(k)
        before = inorder(t.root, [])
        t.root = rotate_left(t.root) if t.root.right else rotate_right(t.root)
        assert inorder(t.root, []) == before, "rotation changed the in-order sequence"


def test_avl():
    rng = random.Random(1)
    for order in ("sorted", "random"):
        keys = list(range(3000))
        if order == "random":
            rng.shuffle(keys)
        t = AVLTree()
        for k in keys:
            t.insert(k)
        assert t.is_valid(), f"invalid AVL tree ({order} input)"
        assert t.height() <= 1.44 * 11.56 + 1, "AVL tree too tall"


def test_rb():
    good = (13, "B", (8, "R", (1, "B", None, None), (11, "B", None, None)),
            (17, "R", (15, "B", None, None), (25, "B", None, None)))
    red_red = (20, "B", (10, "B", None, None), (30, "B", (25, "R", None, (27, "R", None, None)), None))
    assert is_valid_rb(good) == (True, 3), "tree 1 is valid with black-height 3 (counting NIL)"
    assert is_valid_rb(red_red)[0] is False, "tree 2 has a red node with a red child"


if __name__ == "__main__":
    run("Part A  BST on 2,000 sorted keys", test_bst)
    run("Part B  rotations keep in-order", test_rotations)
    run("Part C  AVL insert + validator", test_avl)
    run("Part D  Red-Black validator", test_rb)
