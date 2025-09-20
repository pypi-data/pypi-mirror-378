import logging
import pytest
import torch

from spotiflow.augmentations.transforms import Rotation
from spotiflow.augmentations.transforms.utils import _generate_img_from_points
from typing import Tuple



MSE_TOLERANCE = 1e-2


@pytest.mark.parametrize("img_size", [(4, 1, 224, 224), (5, 2, 512, 512), (1, 100, 100), (3, 327, 312)])
@pytest.mark.parametrize("angle", [(-180, 180), (3, 10), None, (0, 0)])
@pytest.mark.parametrize("n_pts", [10, 100])
def test_rotation_augmentation(img_size: Tuple[int, ...],
                                  angle: Tuple[int, ...],
                                  n_pts: int,
                                  caplog):
    if caplog is not None:
        caplog.set_level(logging.CRITICAL)

    torch.manual_seed(img_size[-1]*n_pts)

    img = torch.zeros(img_size)
    msize = min(img_size[-2:])
    pts = torch.randint(msize//3, msize-msize//3, (img_size[0], n_pts, 2))
    for b in range(img_size[0]):
        img[b] = torch.from_numpy(_generate_img_from_points(pts[b].numpy(), img_size[-2:]))
    if angle is not None and (angle == (0, 0) or any(phi is None for phi in angle)):
        with pytest.raises(ValueError):
            aug = Rotation(order=1, angle=angle)
    else:
        aug = Rotation(order=1, angle=angle)
        img_aug, pts_aug = aug(img, pts)
        img_from_aug_pts = torch.zeros(img_size)
        for b in range(img_size[0]):
            img_from_aug_pts[b] = torch.from_numpy(_generate_img_from_points(pts_aug[b].numpy(), img_size[-2:]))
        mse = ((img_aug - img_from_aug_pts)**2).mean()
        if __name__ == "__main__":
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(1, 4, figsize=(16, 4))
            ax[0].imshow(img[0], cmap="magma")
            ax[0].title.set_text("Original")
            ax[1].imshow(img_aug[0], cmap="magma")
            ax[1].title.set_text("Augmented")
            ax[2].imshow(img_from_aug_pts[0], cmap="magma")
            ax[2].title.set_text("From Augmented Points")
            ax[3].imshow((img_aug[0]-img_from_aug_pts[0])**2, cmap="magma")
            ax[3].title.set_text(f"Squared Difference (MSE: {mse:.5f})")
            fig.show()
        assert mse < MSE_TOLERANCE, "Image augmentation is not correct."

if __name__ == "__main__":
    test_rotation_augmentation((1, 224, 224), (-180, 180), 10, None)