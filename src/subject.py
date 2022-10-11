import os
import re
from pathlib import Path as p
from typing import List, Tuple

import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import seaborn as sns
from nibabel.spatialimages import SpatialImage
import pandas as pd


class Subject(object):

    def __init__(self, path: p | None = None):
        self.path: p | None = path
        self.heart_seq: int | None = None
        self.heart_coords: Tuple[int, int] | None = None
        self.brain_seq: int | None = None
        self.brain_coords: Tuple[int, int] | None = None

    @staticmethod
    def builder(path: p):
        return Subject.__Builder(path)

    def plot_qflow(self, output: p | None = None):
        if self.path is None or self.heart_seq is None or self.heart_coords is None or self.brain_seq is None or self.brain_coords is None: return
        self._heart_file = next(filter(lambda x: re.search(fr"{self.heart_seq}.*ph.*\.nii\.gz", x.name), self.path.iterdir()))
        self._brain_file = next(filter(lambda x: re.search(fr"{self.brain_seq}.*ph.*\.nii\.gz", x.name), self.path.iterdir()))

        heart_img : SpatialImage = nib.load(self._heart_file)
        brain_img : SpatialImage = nib.load(self._brain_file)
        data = pd.DataFrame({
            'heart': heart_img.get_fdata()[self.heart_coords[0], self.heart_coords[1], 0, :],
            'brain': brain_img.get_fdata()[self.brain_coords[0], self.brain_coords[1], 0, :]
        }).melt(var_name="area", value_name="value")
        g = sns.FacetGrid(data, col="area", aspect=(1 + 5 ** 0.5) / 2)  # type: ignore
        g.figure.suptitle(f"{self.path.name} qflow")
        g.map(plt.plot, "value")
        if output != None:
            plt.savefig(output/f"{self.path.name}.png")
            plt.close()
        

    class __Builder():

        class UnfinishedBuilderException(Exception):
            pass

        def __init__(self, path: p | None):
            self.subject = Subject(path)

        def set_path(self, path: p):
            self.subject.path = path

        def set_heart(self, sequence: int, coords: Tuple[int, int]):
            self.subject.heart_seq = sequence
            self.subject.heart_coords = coords
            return self

        def set_brain(self, sequence: int, coords: Tuple[int, int]):
            self.subject.brain_seq = sequence
            self.subject.brain_coords = coords
            return self

        def build(self):
            if self.subject.path == None:
                print(f"Missing path for subject")
            if self.subject.brain_seq == None or self.subject.heart_seq == None:
                print(f"Missing sequence for subject {self.subject.path}")
            return self.subject

