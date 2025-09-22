from experimaestro import Param
from datamaestro import metadata
from datamaestro.data import Base
from datamaestro.data.ml import Supervised, Train, Validation, Test
from datamaestro.definitions import argument, datatasks, datatags
from datamaestro.data.tensor import IDX


class Images(Base):
    """Base class for all datasets made of images"""


class IDXImage(IDX, Images):
    """Image in the IDX format"""


@metadata(tags="images", tasks="image classification")
class ImageClassification(Supervised[Train, Validation, Test]):
    """Image classification dataset"""

    pass


@metadata(tags="images", tasks="image classification")
class LabelledImages(Base):
    """Image classification dataset

    Attributes:

        images: The images of the dataset
        labels: The labels associated with each image
    """

    images: Param[Images]
    labels: Param[Base]
