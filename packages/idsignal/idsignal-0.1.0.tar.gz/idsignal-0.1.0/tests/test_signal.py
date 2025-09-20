"""
This module defines tests for module signal - use pytest to run them.
"""

from idsignal.signal import *

def test_0_argument_signal() -> None:
    signal = IDSignal()

    class B:
        def __init__(self) -> None:
            self.signal_received = False

        def callback(self) -> None:
            self.signal_received = True
            
    component_B1 = B()
    component_B2 = B()
    assert not component_B1.signal_received
    assert not component_B2.signal_received
    signal.connect(component_B1.callback)
    signal.connect(component_B2.callback)
    signal.emit()
    assert component_B1.signal_received
    assert component_B2.signal_received


def test_1_argument_signal() -> None:
    signal = IDSignal()

    class B:
        def __init__(self) -> None:
            self.signal_received = False
            self.message = ""

        def callback(self, message: str) -> None:
            self.signal_received = True
            self.message = message
            
    component_B1 = B()
    component_B2 = B()
    assert not component_B1.signal_received
    assert not component_B2.signal_received
    assert component_B1.message == ""
    assert component_B2.message == ""
    signal.connect(component_B1.callback)
    signal.connect(component_B2.callback)
    signal.emit("Hello!")
    assert component_B1.signal_received
    assert component_B2.signal_received
    assert component_B1.message == "Hello!"
    assert component_B2.message == "Hello!"


def test_2_argument_signal() -> None:
    signal = IDSignal()

    class B:
        def __init__(self) -> None:
            self.signal_received = False
            self.message = ""
            self.integer = 0

        def callback(self, message: str, integer: int) -> None:
            self.signal_received = True
            self.message = message
            self.integer = integer
            
    component_B1 = B()
    component_B2 = B()
    assert not component_B1.signal_received
    assert not component_B2.signal_received
    assert component_B1.message == ""
    assert component_B2.message == ""
    assert component_B1.integer == 0
    assert component_B2.integer == 0
    signal.connect(component_B1.callback)
    signal.connect(component_B2.callback)
    signal.emit("Hello!", 77)
    assert component_B1.signal_received
    assert component_B2.signal_received
    assert component_B1.message == "Hello!"
    assert component_B2.message == "Hello!"
    assert component_B1.integer == 77
    assert component_B2.integer == 77


def test_chaining_signals() -> None:
    signal_1 = IDSignal()
    signal_2 = IDSignal()

    signal_received = False

    def function_1() -> None:
        nonlocal signal_received
        signal_received = True

    signal_2.connect(function_1)
    signal_1.connect(signal_2)

    signal_1.emit()

    assert signal_received


if __name__ == "__main__":
    print(__file__)
    import pytest
    pytest.main()
