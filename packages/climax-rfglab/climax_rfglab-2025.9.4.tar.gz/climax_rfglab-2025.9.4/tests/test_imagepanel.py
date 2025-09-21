# slider widget tests.
# for coverage, run:
# coverage run -m pytest -s
# or if you want to include branches:
# coverage run --branch -m pytest
# followed by:
# coverage report -i
# or coverage report --show-missing (to include missing lines)

import numpy
import pytest
from textual.events import MouseMove

from climax.climax  import climax
from climax._imagepanel import ImagePanel


pytest_plugins = ('pytest_asyncio',)


def test_imagepanel_basic():
    # Test basic initialization of ImagePanel
    image = numpy.random.randint(0, 256, (100, 100), dtype=numpy.uint8)  # Create a random grayscale image
    panel = ImagePanel(image)
    assert panel is not None
    assert panel.image is not None  # No image loaded initially
    assert panel.zoom_factor == 1.0  # Default zoom level

def test_imagepanel_rendering():
    # Test rendering functionality of ImagePanel
    image = numpy.random.randint(0, 256, (100, 100), dtype=numpy.uint8)  # Create a random grayscale image
    panel = ImagePanel(image)
    
    rendered_output = panel.render()  # Call the render method
    assert rendered_output is not None  # Should produce some output

@pytest.mark.parametrize(["x", "y"], [(10, 20), (50, 50), (99, 99), (0, 0), (25, 75), (200, 200)])  # image coordinates
@pytest.mark.asyncio
async def test_imagepanel_mousemove(x, y):
    app = climax()

    # Test mouse move event handling
    image = numpy.random.randint(0, 256, (100, 100), dtype=numpy.uint8)  # Create a random grayscale image
    app.volume = numpy.expand_dims(image, axis=(0, 1, 2))
    app.color = app.volume[0]
    app.slices = app.color[0]
    app.image_data = numpy.transpose(app.slices, climax.orientations[app.view_plane])
    app.display_slice(True, 0)

    async with app.run_test() as pilot:
        event = MouseMove(app.image_panel, x=int(round(x*app.image_panel.zoom_factor*app.image_panel.renderer_xscale)), y=int(round(y*app.image_panel.zoom_factor*app.image_panel.renderer_yscale)), screen_x=int(round(x*app.image_panel.zoom_factor*app.image_panel.renderer_xscale)), screen_y=int(round(y*app.image_panel.zoom_factor*app.image_panel.renderer_yscale)), delta_x=0, delta_y=0, button=None, shift=False, ctrl=False, meta=False)
        app.image_panel.post_message(event)
        await pilot.pause(0.1)
        
        col, row = int(event.x / (app.image_panel.zoom_factor*app.image_panel.renderer_xscale)), int(event.y / (app.image_panel.zoom_factor * app.image_panel.renderer_yscale))

        if col < image.shape[1] and row < image.shape[0]-1:
            assert app.image_panel.tooltip==f"(x={col},y={row}:{row+1})={image[row,col]}:{image[row+1,col]}"
        else :
            assert app.image_panel.tooltip is None