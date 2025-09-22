from datamaestro_image.data import ImageClassification, LabelledImages, Base, IDXImage
from datamaestro.download.single import filedownloader
from datamaestro.definitions import dataset
from datamaestro.data.tensor import IDX


@filedownloader(
    "train_images.idx",
    "https://ossci-datasets.s3.amazonaws.com/mnist/train-images-idx3-ubyte.gz",
)
@filedownloader(
    "train_labels.idx",
    "https://ossci-datasets.s3.amazonaws.com/mnist/train-labels-idx1-ubyte.gz",
)
@filedownloader(
    "test_images.idx",
    "https://ossci-datasets.s3.amazonaws.com/mnist/t10k-images-idx3-ubyte.gz",
)
@filedownloader(
    "test_labels.idx",
    "https://ossci-datasets.s3.amazonaws.com/mnist/t10k-labels-idx1-ubyte.gz",
)
@dataset()
def mnist(train_images, train_labels, test_images, test_labels) -> ImageClassification:
    """The MNIST database

    The MNIST database of handwritten digits, available from this page, has a
    training set of 60,000 examples, and a test set of 10,000 examples. It is a
    subset of a larger set available from NIST. The digits have been
    size-normalized and centered in a fixed-size image.
    """
    return ImageClassification.C(
        train=LabelledImages.C(
            images=IDXImage.C(path=train_images), labels=IDX.C(path=train_labels)
        ),
        test=LabelledImages.C(
            images=IDXImage.C(path=test_images), labels=IDX.C(path=test_labels)
        ),
    )
