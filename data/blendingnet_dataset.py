import os
from data.base_dataset import BaseDataset, get_params, get_transform
from data.image_folder import make_dataset
from PIL import Image

class BlendingnetDataset(BaseDataset):
    """
    Dataset for mouth blendingnet
    pass args:
        --dataset_mode blendingnet
    """
    def __init__(self, opt):
        """Initialize this dataset class.

        Parameters:
            opt (Option class) -- stores all the experiment flags; needs to be a subclass of BaseOptions

        A few things can be done here.
        - save the options (have been done in BaseDataset)
        - get image paths and meta information of the dataset.
        - define the image transformation.
        """
        # save the options and dataset root
        BaseDataset.__init__(self, opt)
        self.dir_AB = os.path.join(opt.dataroot, opt.phase)  # get the image directory
        self.AB_paths = sorted(
            make_dataset(self.dir_AB, opt.max_dataset_size)
        )  # get image paths
        assert (
            self.opt.load_size >= self.opt.crop_size
        )  # crop_size should be smaller than the size of loaded image
        self.input_nc = (
            self.opt.output_nc if self.opt.direction == "BtoA" else self.opt.input_nc
        )
        self.output_nc = (
            self.opt.input_nc if self.opt.direction == "BtoA" else self.opt.output_nc
        )

    @staticmethod
    def modify_commandline_options(parser, is_train):
        """Add new dataset-specific options, and rewrite default values for existing options.

        Parameters:
            parser          -- original option parser
            is_train (bool) -- whether training phase or test phase. You can use this flag to add training-specific or test-specific options.

        Returns:
            the modified parser.
        """
        parser.set_defaults(
            preprocess='scale_width', input_nc=7, output_nc=3, direction="AtoB"
        )  # specify dataset-specific default values
        return parser
    
    def __getitem__(self, index):
        """Return a data point and its metadata information.

        Parameters:
            index - - a random integer for data indexing

        Returns a dictionary that contains A, B, A_paths and B_paths
            A (tensor) - - an image in the input domain
            B (tensor) - - its corresponding image in the target domain
            A_paths (str) - - image paths
            B_paths (str) - - image paths (same as A_paths)
        """
        # read a image given a random integer index
        AB_path = self.AB_paths[index]
        AB = Image.open(AB_path).convert("RGB")
        # split AB image into A and B
        w, h = AB.size
        w2 = int(w / 2)
        A = AB.crop((0, 0, w2, h))
        B = AB.crop((w2, 0, w, h))

        # apply the same transform to both A and B
        transform_params = get_params(self.opt, A.size)
        A_transform = get_transform(
            self.opt, transform_params, grayscale=(self.input_nc == 1)
        )
        B_transform = get_transform(
            self.opt, transform_params, grayscale=(self.output_nc == 1)
        )

        A = A_transform(A)
        B = B_transform(B)

        return {"A": A, "B": B, "A_paths": AB_path, "B_paths": AB_path}
    
    def __len__(self):
        """Return the total number of images in the dataset."""
        return len(self.AB_paths)
