import pytest
from invertcolor import invert_rgb_color

def test_invert_black():
    assert invert_rgb_color((0, 0, 0)) == (255, 255, 255)

def test_invert_white():
    assert invert_rgb_color((255, 255, 255)) == (0, 0, 0)

def test_invert_mid_gray():
    assert invert_rgb_color((128, 128, 128)) == (127, 127, 127)

def test_invert_custom_color():
    assert invert_rgb_color((100, 200, 50)) == (155, 55, 205)

def test_invalid_input_type():
    with pytest.raises(TypeError):
        invert_rgb_color("not a tuple")

def test_invalid_tuple_length():
    with pytest.raises(TypeError):
        invert_rgb_color((10, 20))

def test_invalid_value_type():
    with pytest.raises(TypeError):
        invert_rgb_color((10, 20, 30.5))

def test_value_out_of_range():
    with pytest.raises(ValueError):
        invert_rgb_color((300, 10, -5))