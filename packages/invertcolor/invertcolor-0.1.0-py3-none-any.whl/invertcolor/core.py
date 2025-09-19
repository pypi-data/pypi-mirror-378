from typing import Tuple

def invert_rgb_color(rgb_tuple: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """
    Inverts an RGB color tuple.
    
    Args:
        rgb_tuple (tuple): A tuple containing (R, G, B) values, each from 0-255.
        
    Returns:
        tuple: A new tuple with the inverted (R, G, B) values.
    """
    if not isinstance(rgb_tuple, tuple) or len(rgb_tuple) != 3:
        raise TypeError("Input must be a tuple of three integers.")
        
    for value in rgb_tuple:
        if not isinstance(value, int):
            raise TypeError("All values in the tuple must be integers.")
        if not (0 <= value <= 255):
            raise ValueError("All color values must be between 0 and 255.")
            
    inverted_r = 255 - rgb_tuple[0]
    inverted_g = 255 - rgb_tuple[1]
    inverted_b = 255 - rgb_tuple[2]
    
    return (inverted_r, inverted_g, inverted_b)