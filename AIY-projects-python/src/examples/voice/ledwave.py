import time
import board
import neopixel

pixel_pin = board.D10
num_pixels = 142
ORDER = neopixel.RGBW
pixels = neopixel.NeoPixel(
  pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=ORDER
)
pixels.fill((50, 50, 50,0))
pixels.show()
