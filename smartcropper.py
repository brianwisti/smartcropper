import math

from PIL import Image

class SmartCropper:
    def __init__(self, image):
        """Create a new SmartCropper from a single Pillow image"""
        self.image = image

        # hardcoded (but overridable) defaults
        self.steps = 10

    @classmethod
    def from_file(cls, filename):
       image = Image.open(filename)
       return cls(image)

    def smart_crop(self, width, height):
        sq = self.square(width, height)
        return self.image.crop(sq)

    def square(self, width, height):
        return self.smart_crop_by_trim(width, height)

    def smart_crop_by_trim(self, requested_x, requested_y):
        left, top = 0, 0
        right, bottom = self.image.width, self.image.height
        width, height = right, bottom
        step_size = self.step_size(requested_x, requested_y)
        quantized = self.image.convert("P", dither=1)

        # Avoid attempts to slice less than one pixel.
        if step_size > 0:
            # Slice from left and right edges until the correct width is reached.
            while width > requested_x:
                slice_width = min((width - requested_x), step_size)
                left_entropy = self.entropy_slice(quantized, left, 0, slice_width, bottom)
                right_entropy = self.entropy_slice(quantized, (right - slice_width), 0, slice_width, bottom)

                # Remove the slice with the least entropy
                if left_entropy < right_entropy:
                    left += slice_width
                else:
                    right -= slice_width

                width = right - left

            # Slice from top and bottom edges until the correct height is reached.
            while height > requested_y:
                slice_height = min((height - step_size), step_size)

                # Avoid shrinking past requested height
                if height - slice_height < requested_y:
                    slice_height = height - requested_y

                top_entropy = self.entropy_slice(quantized, 0, top, self.image.width, slice_height)
                bottom_entropy = self.entropy_slice(quantized, 0, (bottom - slice_height), self.image.width, slice_height)

                # Remove the slice with the least entropy
                if top_entropy < bottom_entropy:
                    top += slice_height
                else:
                    bottom -= slice_height

                height = bottom - top
        return (left, top, right, bottom)

    def smart_crop_and_scale(self, width, height):
        squared = self.smart_square()
        return squared.resize((width, height))

    def smart_square(self):
        rows = self.image.height
        columns = self.image.width

        if rows != columns:
            if rows < columns:
                crop_height = crop_width = rows
            else:
                crop_height = crop_width = columns

        squared = self.square(crop_width, crop_height)
        return self.image.crop(squared)

    def step_size(self, requested_x, requested_y):
        # Yes this is too verbose but I needed to understand the steps.
        height_difference = self.image.height - requested_x
        width_difference = self.image.width - requested_y
        biggest_difference = max(height_difference, width_difference)
        average_difference = biggest_difference / 2
        # NOTE: Ceiling so I can do a 1 pixel crop
        return math.ceil( average_difference / self.steps)

    def entropy_slice(self, image_data, x, y, width, height):
        bottom = y + height
        right = x + width
        box = (x, y, right, bottom)
        image_slice = image_data.crop(box)

        if image_slice.height == 0 or image_slice.width == 0:
            return 0

        return self.entropy(image_slice)

    def entropy(self, image_slice):
        hist = image_slice.histogram()
        hist_size = float(sum(hist))

        entropy = 0
        for h in hist:
            if h == 0:
                continue

            p = float(h) / hist_size
            if p != 0:
                entropy += (p * (math.log(p) / math.log(2.0)))

        return entropy * -1
