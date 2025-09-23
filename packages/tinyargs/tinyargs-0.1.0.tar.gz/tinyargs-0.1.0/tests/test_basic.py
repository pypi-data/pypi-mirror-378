import sys
import pytest
from tinyargs import get, flag, args, TinyArgsError

def set_argv(argv):
    sys.argv = ["prog"] + argv

def test_get_value():
    set_argv(["--name", "Alice"])
    assert get("--name") == "Alice"

def test_get_with_type():
    set_argv(["--age", "20"])
    assert get("--age", type=int) == 20

def test_default_and_required():
    set_argv([])
    assert get("--age", type=int, default=18) == 18
    with pytest.raises(TinyArgsError):
        get("--age", required=True)

def test_flag_present():
    set_argv(["--verbose"])
    assert flag("--verbose") is True
    set_argv([])
    assert flag("--verbose") is False

def test_args_unpack():
    set_argv(["--w", "640", "--h", "480"])
    w, h = args("--w", "--h", types={"--w": int, "--h": int})
    assert (w, h) == (640, 480)

def test_equals_syntax():
    set_argv(["--name=Alice"])
    name, = args("--name")
    assert name == "Alice"
