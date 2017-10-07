# SmartCropper

An experiment with porting [smartcropper][] from Ruby to Python, using [Pillow][] instead of [RMagick][].

Note that it doesn't work right now.

[smartcropper]: https://github.com/berkes/smartcropper
[Pillow]: https://python-pillow.org/
[RMagick]: https://rmagick.github.io/

## Setup

I used Python 3.6.2 during development.

    $ pip install -r requirements.txt
    $ pytest
    # Look at failing test output
