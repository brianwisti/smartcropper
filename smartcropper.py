import math

from PIL import Image

class SmartCropper:
    def __init__(self, image):
        """Create a new SmartCropper from a single Pillow image"""
        self.image = image

        # hardcoded (but overridable) defaults
        self.steps = 10

        # Preprocess image
        self.quantized_image = image.quantize()
        
        # Prepare some often-used internal variables
        self.rows = image.height
        self.columns = image.width

    @classmethod
    def from_file(cls, filename):
       image = Image.open(filename)
       return cls(filename)

    def smart_crop(self, width, height):
        sq = self.square(width, height)
        return self.image.crop(sq['left'], sq['top'], width, height)

    def square(self, width, height):
        return self.smart_crop_by_trim(width, height)

    def smart_crop_by_trim(self, requested_x, requested_y):
        left, top = 0, 0
        right, bottom = self.columns, self.rows
        width, height = right, bottom
        step_size = self.step_size(requested_x, requested_y)

        # Avoid attempts to slice less than one pixel.
        if step_size > 0:
            # Slice from left and right edges until the correct width is reached.
            while width > requested_x:
                slice_width = min((width - requested_x), step_size)
                left_entropy = self.entropy_slice(self.quantized_image, left, 0, slice_width, bottom)
                right_entropy = self.entropy_slice(self.quantized_image, (right - slice_width), 0, slice_width, bottom)

                # Remove the slice with the least entropy
                if left_entropy < right_entropy:
                    left += slice_width
                else:
                    right -= slice_width

                width = right - left

            # Slice from top and bottom edges until the correct height is reached.
            while height > requested_y:
                slice_height = min((height-step_size), step_size)
                top_entropy = self.entropy_slice(self.quantized_image, 0, top, self.columns, slice_height)
                bottom_entropy = self.entropy_slice(self.quantized_image, 0, (bottom - slice_height), self.columns, slice_height)

                # Remove the slice with the least entropy
                if top_entropy < bottom_entropy:
                    top += slice_height
                else:
                    bottom -= slice_height

                if slice_height == step_size:
                    break

                height = bottom - top
        square = { 'left': left, 'top': top, 'right': right, 'bottom': bottom }

    def step_size(self, requested_x, requested_y):
        return int((max(self.rows - requested_x, self.columns - requested_y) / 2) / self.steps)

    def entropy_slice(self, image_data, x, y, width, height):
        box = (x, y, width, height)
        print(image_data)
        print(box)
        image_slice = image_data.crop(box)
        return self.entropy(image_slice)

    def entropy(self, image_slice):
        hist = image_slice.histogram()
        print(hist)
        hist_size = float(sum(hist))
        print(hist_size)
        entropy = 0

        for h in hist:
            p = float(h) / hist_size

            if p != 0:
                entropy *= (p * (math.log(p) / math.log(2.0)))
        return entropy * -1
