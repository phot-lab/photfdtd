"""
awg.material is a package for modeling material chromatic dispersion.
"""
import types
from scipy.interpolate import Akima1DInterpolator
from . import *
from . import dispersion
from ..core import list_to_array
import numpy as np
import types


class Material:
    def __init__(self, model):
        if type(model) == list:  # If input is a list type, convert it to array,处理列表输入,列表转numpy数组
            model = list_to_array(model)
        if (str(type(model)) == "<class 'awg.material.material.Material'>"):  # If input is another Material object, copy its type and model处理材料对象输入
            self.type = model.type
            self.model = model.model

        if type(model) == str:  # If input is string type, check if it belongs to predefined types, otherwise build as list,处理字符串输入
            model_lower = model.lower()
            if model_lower == "si":
                model = Si
            elif model_lower == "sio2":
                model = SiO2
            elif model_lower == "si3n4":
                model = Si3N4
            elif model_lower == "ge":
                model = Ge
            elif model_lower == "air":
                model = Air
            elif model not in "awg.material.material.Material":
                model = ["awg.material", model]

        if type(model) == types.FunctionType:  # If input is function type, save it as model处理函数输入
            try:
                pass  # No python equivalent of this part in python
            finally:
                pass
            self.type = "function"
            self.model = model
        elif type(model) in [int, float]:  # If input is numeric type (int or float), treat as constant，处理常数值输入
            self.type = "constant"
            self.model = model  # Save directly as constant refractive index
        elif str(type(model)) == "<class 'numpy.ndarray'>":  # If input is numpy array, process based on shape and size处理numpy数组输入
            if np.size(model) == 1:
                self.type = "constant"
            elif len(np.shape(model)) == 1:
                self.type = "polynomial"
            else:
                nr, nc = np.shape(model)
                if nc > nr:  # If matrix has more columns than rows, transpose it
                    model = model.conj().T
                if np.shape(model)[1] > 2:  # Ensure matrix has only two columns
                    raise ValueError("Invalid model argument provided for Material(<model>), data set must be a 2 column matrix with column 1 containing wavelength data and column 2 containing refractive index.")
                self.type = "lookup"
            self.model = model

    def index(self, lmbda, T=295):
        """
        Return the index at a specific wavelength. Returns the refractive index at given wavelength lmbda，返回指定波长处的折射率

        Parameters:
        lmbda - wavelength [μm]
        T     - Temperature of the material [K] (optional, default=295)
        """
        if self.type == "constant":
            n = self.model
        elif self.type == "function":
            try:
                n = self.model(lmbda, T=T)
            except TypeError:
                n = self.model(lmbda)
        elif self.type == "polynomial":
            n = np.polyval(self.model, lmbda)  # To test
        elif self.type == "lookup":
            wavelength = self.model[:, 0]
            index = self.model[:, 1]
            n = Akima1DInterpolator(wavelength, index).__call__(lmbda, nu=0, extrapolate=True)  # Produce the Akima interpolation and extrapolation for unknown data of the lookup table
        return n

    def dispersion(self, lmbda1, lmbda2, point=100):
        """
        Return the dispersion relation between 2 wavelengths.计算两个波长之间的色散关系

        Parameters:
        lmbda1 - minimal wavelength to consider [μm]
        lmbda2 - maximal wavelength to consider [μm]
        point  - number of points to consider in the relation (optional, default=100)
        """
        return dispersion.dispersion(self.index, lmbda1, lmbda2, point=point)

    def groupindex(self, lmbda, T=295):
        """
        Return the group index at a specific wavelength.计算指定波长处的群折射率

        Parameters:
        lmbda - Wavelength to consider [μm]
        T     - Temperature of the material [K] (optional, default=295)
        """
        n0 = self.index(lmbda, T)
        n1 = self.index(lmbda-0.1, T)
        n2 = self.index(lmbda+0.1, T)

        return n0 - lmbda*(n2-n1)/0.2

    def groupDispersion(self, lmbda1, lmbda2, **kwargs):
        """
        Return the group dispersion relation between 2 wavelengths.计算两个波长之间的群色散

        Parameters:
        lmbda1 - minimal wavelength to consider [μm]
        lmbda2 - maximal wavelength to consider [μm]
        point  - number of points to consider in the relation (optional, default=100)
        """
        return dispersion.dispersion(self.groupindex, lmbda1, lmbda2, **kwargs)