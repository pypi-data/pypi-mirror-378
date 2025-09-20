import logging
import pytest
import torch

from spotiflow.augmentations.transforms.noise import GaussianNoise, SaltAndPepperNoise
from spotiflow.augmentations.transforms.utils import _generate_img_from_points
from typing import Tuple, Union


ABS_TOLERANCE = 1e-8

@pytest.mark.parametrize("img_size", [(4, 1, 224, 224), (5, 2, 512, 512), (1, 100, 100), (3, 327, 312)])
@pytest.mark.parametrize("sigma", [(0., 0.05), (0.4, 1.)])
@pytest.mark.parametrize("n_pts", [10, 100])
def test_gaussian_noise_augmentation(img_size: Tuple[int, ...],
                           sigma: Tuple[float, ...],
                           n_pts: int,
                           caplog):
    if caplog is not None:
        caplog.set_level(logging.CRITICAL)
    
    torch.manual_seed(img_size[-1]*n_pts)
    
    img = torch.zeros(img_size)
    msize = min(img_size[-2:])
    pts = torch.randint(0, msize, (n_pts, 2)).repeat(img_size[0], 1, 1)
    for b in range(img_size[0]):
        img[b] = torch.from_numpy(_generate_img_from_points(pts[b].numpy(), img_size[-2:], sigma=1.)) # Use deltas to avoid cropping at the border of the Gaussianized spot introducing non-existing errors
    aug = GaussianNoise(sigma=sigma)
    img_aug, pts_aug = aug(img, pts)

    img_from_aug_pts = torch.zeros(*img_size)
    assert torch.allclose(pts, pts_aug, atol=ABS_TOLERANCE), "Points changed after Gaussian noise addition, which should not be!"
    
    for b in range(img_size[0]):
        img_from_aug_pts[b] = torch.from_numpy(_generate_img_from_points(pts_aug[b].numpy(), img_size[-2:], sigma=1.))

    if __name__ == "__main__":
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(1, 2, figsize=(8, 4))
        ax[0].imshow(img[0], cmap="magma")
        ax[0].title.set_text("Original")
        ax[1].imshow(img_aug[0], cmap="magma")
        ax[1].title.set_text("Augmented")
        fig.show()

@pytest.mark.parametrize("img_size", [(4, 1, 224, 224), (5, 2, 512, 512), (1, 100, 100), (3, 327, 312)])
@pytest.mark.parametrize("prob_pepper", [(0., 0.0005), (0., 0.1), (0., 0.)])
@pytest.mark.parametrize("prob_salt", [(0., 0.0005), (0., 0.01), (0., 0.)])
@pytest.mark.parametrize("n_pts", [10, 100])
def test_saltpepper_noise_augmentation(img_size: Tuple[int, ...],
                                     prob_pepper: Tuple[float, ...],
                                     prob_salt: Tuple[float, ...],
                                     n_pts: int,
                                     caplog):
    if caplog is not None:
        caplog.set_level(logging.CRITICAL)
    
    torch.manual_seed(img_size[-1]*n_pts)
    
    img = torch.zeros(img_size)
    msize = min(img_size[-2:])
    pts = torch.randint(0, msize, (n_pts, 2)).repeat(img_size[0], 1, 1)
    for b in range(img_size[0]):
        img[b] = torch.from_numpy(_generate_img_from_points(pts[b].numpy(), img_size[-2:], sigma=1.)) # Use deltas to avoid cropping at the border of the Gaussianized spot introducing non-existing errors
    aug = SaltAndPepperNoise(prob_pepper=prob_pepper, prob_salt=prob_salt)
    img_aug, pts_aug = aug(img, pts)

    img_from_aug_pts = torch.zeros(*img_size)
    if all(p == 0 for p in prob_pepper) and all(p == 0 for p in prob_salt):
        assert torch.allclose(img, img_aug, atol=ABS_TOLERANCE), "Image changed, but should not!"
    assert torch.allclose(pts, pts_aug, atol=ABS_TOLERANCE), "Points changed after Gaussian noise addition, which should not be!"
    
    for b in range(img_size[0]):
        img_from_aug_pts[b] = torch.from_numpy(_generate_img_from_points(pts_aug[b].numpy(), img_size[-2:], sigma=1.))

    if __name__ == "__main__":
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(1, 2, figsize=(8, 4))
        ax[0].imshow(img[0], cmap="magma")
        ax[0].title.set_text("Original")
        ax[1].imshow(img_aug[0], cmap="magma")
        ax[1].title.set_text("Augmented")
        fig.show()

if __name__ == "__main__":
    # test_gaussian_noise_augmentation((3, 327, 312), (0, 0.05), 100, None)
    test_saltpepper_noise_augmentation((3, 327, 312), (0., 0.), (0, 0.005), 100, None)

