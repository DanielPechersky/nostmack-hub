from nostmack_hub.saturating_number import SaturatingNumber


def test_max():
    n = SaturatingNumber(0, min=0, max=5)
    n.add(10)
    assert n.inner == 5


def test_min():
    n = SaturatingNumber(2, min=0, max=5)
    n.sub(5)
    assert n.inner == 0


def test_is_max():
    assert not SaturatingNumber(0, min=0, max=5).is_max
    assert SaturatingNumber(5, min=0, max=5).is_max


def test_is_min():
    assert not SaturatingNumber(5, min=0, max=5).is_min
    assert SaturatingNumber(0, min=0, max=5).is_min
