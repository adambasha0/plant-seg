import torch
from plantseg.models.zoo import model_zoo


def test_get_3D_model_by_id():
    """Try to load a 3D model from the BioImage.IO model zoo.

    Load Qin Yu's nuclear segmentation model 'efficient-chipmunk'.
    """
    model, model_config, model_path = model_zoo.get_model_by_id('efficient-chipmunk')
    state = torch.load(model_path, map_location='cpu')
    if 'model_state_dict' in state:  # Model weights format may vary between versions
        state = state['model_state_dict']
    model.load_state_dict(state)

def test_get_2D_model_by_id():
    """Try to load a 2D model from the BioImage.IO model zoo.

    Load Adrian's 2D cell-wall segmentation model 'pioneering-rhino'.
    """
    model, model_config, model_path = model_zoo.get_model_by_id('pioneering-rhino')
    state = torch.load(model_path, map_location='cpu')
    if 'model_state_dict' in state:  # Model weights format may vary between versions
        state = state['model_state_dict']
    model.load_state_dict(state)
