import napari

from plantseg.viewer_napari import log
from plantseg.viewer_napari.containers import (
    get_data_io_tab,
    get_extras_tab,
    get_postprocessing_tab,
    get_preprocessing_tab,
    get_proofreading_tab,
    get_segmentation_tab,
)
from plantseg.viewer_napari.widgets.proofreading import setup_proofreading_keybindings


def run_viewer():
    viewer = napari.Viewer(title='PlantSeg v2')
    setup_proofreading_keybindings(viewer)

    # Create and add tabs
    for _containers, name in [
        (get_data_io_tab(), 'Input/Output'),
        (get_preprocessing_tab(), 'Image Processing'),
        (get_segmentation_tab(), 'Segmentation'),
        (get_postprocessing_tab(), 'Label Processing'),
        (get_proofreading_tab(), 'Proofreading'),
        (get_extras_tab(), 'Models'),
    ]:
        viewer.window.add_dock_widget(_containers, name=name, tabify=True)

    # Show data tab by default
    viewer.window._dock_widgets['Input/Output'].show()
    viewer.window._dock_widgets['Input/Output'].raise_()

    log('Plantseg is ready!', thread='Run viewer', level='info')
    napari.run()
