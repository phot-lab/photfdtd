""" Selects the backend for the fdtd-package.

The `fdtd` library allows to choose a backend. The ``numpy`` backend is the
default one, but there are also several additional PyTorch backends:

    - ``numpy`` (defaults to float64 arrays)
    - ``torch`` (defaults to float64 tensors)
    - ``torch.float32``
    - ``torch.float64``
    - ``torch.cuda`` (defaults to float64 tensors)
    - ``torch.cuda.float32``
    - ``torch.cuda.float64``

For example, this is how to choose the `"torch"` backend: ::

    fdtd.set_backend("torch")

In general, the ``numpy`` backend is preferred for standard CPU calculations
with `"float64"` precision. In general, ``float64`` precision is always
preferred over ``float32`` for FDTD simulations, however, ``float32`` might
give a significant performance boost.

The ``cuda`` backends are only available for computers with a GPU.

"""
# avoid duplicate library errors

import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
## Imports

# Numpy Backend
import numpy  # numpy has to be present
from functools import wraps

# used only by test runner.
# default must be idx 0.
backend_names = [
    dict(backends="numpy"),
    dict(backends="torch.float32"),
    dict(backends="torch.float64"),
    dict(backends="torch.cuda.float32"),
    dict(backends="torch.cuda.float64"),
]

numpy_float_dtypes = {
    getattr(numpy, "float_", numpy.float64),
    getattr(numpy, "float16", numpy.float64),
    getattr(numpy, "float32", numpy.float64),
    getattr(numpy, "float64", numpy.float64),
    getattr(numpy, "float128", numpy.float64),
}


# Torch Backends (and flags)
try:
    import torch

    torch.set_default_dtype(torch.float64)  # we need more precision for FDTD
    try:  # we don't need gradients (for now)
        torch._C.set_grad_enabled(False)  # type: ignore
    except AttributeError:
        torch._C._set_grad_enabled(False)
    TORCH_AVAILABLE = True
    TORCH_CUDA_AVAILABLE = torch.cuda.is_available()
except ImportError:
    TORCH_AVAILABLE = False
    TORCH_CUDA_AVAILABLE = False


# Base Class
class Backend:
    """Backend Base Class"""

    # constants
    pi = numpy.pi

    def __repr__(self):
        return self.__class__.__name__


def _replace_float(func):
    """replace the default dtype a function is called with
    替换函数调用时的默认数据类型"""

    # 预处理函数参数，确保都是numpy数组 / Pre-process function arguments to ensure they are numpy arrays
    def preprocess_args(*args, **kwargs):
        processed_args = []
        for arg in args:
            if hasattr(arg, 'device') and 'cuda' in str(arg.device):
                # GPU张量先转到CPU再转numpy / GPU tensor to CPU then numpy
                processed_args.append(arg.cpu().numpy())
            elif hasattr(arg, 'numpy') and callable(getattr(arg, 'numpy')):
                # CPU张量转numpy / CPU tensor to numpy
                processed_args.append(arg.numpy())
            elif hasattr(arg, 'device'):
                # 其他torch张量 / Other torch tensors
                processed_args.append(arg.detach().cpu().numpy())
            else:
                # 已经是numpy数组或其他类型 / Already numpy array or other types
                processed_args.append(arg)

        processed_kwargs = {}
        for key, value in kwargs.items():
            if hasattr(value, 'device') and 'cuda' in str(value.device):
                processed_kwargs[key] = value.cpu().numpy()
            elif hasattr(value, 'numpy') and callable(getattr(value, 'numpy')):
                processed_kwargs[key] = value.numpy()
            elif hasattr(value, 'device'):
                processed_kwargs[key] = value.detach().cpu().numpy()
            else:
                processed_kwargs[key] = value

        return processed_args, processed_kwargs

    @wraps(func)
    def new_func(self, *args, **kwargs):
        # 预处理参数 / Preprocess arguments
        processed_args, processed_kwargs = preprocess_args(*args, **kwargs)

        result = func(*processed_args, **processed_kwargs)
        if hasattr(result, 'dtype') and result.dtype in numpy_float_dtypes:
            result = numpy.asarray(result, dtype=self.float)
        return result

    return new_func


# Numpy Backend
class NumpyBackend(Backend):
    """Numpy Backend"""

    # types
    abs = numpy.abs

    int = numpy.int64
    """ integer type for array"""

    float = numpy.float64
    """ floating type for array """

    @staticmethod
    def astype(arr, dtype):
        """convert array to specified type"""
        if hasattr(arr, 'astype'):
            return arr.astype(dtype)
        else:
            return numpy.asarray(arr, dtype=dtype)

    @staticmethod
    def to_float(arr):
        """ convert array to float type, same to numpy.float64 """
        if isinstance(arr, numpy.ndarray):
            return arr.astype(float)
        else:
            return numpy.asarray(arr, dtype=float)
    """ convert array to float type, same to numpy.float64. This is to sync with torch.to_float() """

    
    complex = numpy.complex128
    """ complex type for array """

    # methods
    empty = staticmethod(numpy.empty)

    asarray = _replace_float(numpy.asarray)

    exp = staticmethod(numpy.exp)
    """ exponential of all elements in array """

    sin = staticmethod(numpy.sin)
    """ sine of all elements in array """

    cos = staticmethod(numpy.cos)
    """ cosine of all elements in array """

    cross = staticmethod(numpy.cross)
    """ cross product of two arrays, only for fourier.FrequencyRountines.FFT """

    arctan2 = staticmethod(numpy.arctan2)
    """ arctangent of y/x with correct quadrant """

    any = staticmethod(numpy.any)
    """ test whether any array element along a given axis evaluates to True """

    @staticmethod
    def shape(x):
        """return the shape of an array"""
        if hasattr(x, 'shape'):
            return x.shape
        else:
            return numpy.array(x).shape

    radians = staticmethod(numpy.radians)
    """ convert degrees to radians """

    # 在 NumpyBackend 类中
    @staticmethod
    def sum(x, axis=None, **kwargs):
        """sum elements in array with axis support"""
        if isinstance(x, numpy.ndarray):
            return numpy.sum(x, axis=axis)
        elif hasattr(x, 'sum'):  # PyTorch tensor
            return x.sum(dim=axis)
        else:
            return numpy.sum(numpy.asarray(x), axis=axis)
    """ sum elements in array """

    min = staticmethod(numpy.min)
    """ min element in array """

    max = staticmethod(numpy.max)
    """ max element in array """

    arg = staticmethod(numpy.argmax)
    """ index of max element in array """

    where = staticmethod(numpy.where)
    """ return elements of array where condition is True, otherwise return other elements """

    sqrt = staticmethod(numpy.sqrt)
    """ max element in array """

    stack = staticmethod(numpy.stack)
    """ stack multiple arrays """

    transpose = staticmethod(numpy.transpose)
    """ transpose array by flipping two dimensions """

    reshape = staticmethod(numpy.reshape)
    """ reshape array into given shape """

    squeeze = staticmethod(numpy.squeeze)
    """ remove dim-1 dimensions """

    round = staticmethod(numpy.round)
    """ round array elements to nearest integer """

    broadcast_arrays = staticmethod(numpy.broadcast_arrays)
    """ broadcast arrays """

    broadcast_to = staticmethod(numpy.broadcast_to)
    """ broadcast array into shape """

    cat = staticmethod(numpy.concatenate)
    """ concatenate multiple arrays along a given dimension, only for fourier.FrequencyRountines.FFT """

    full = staticmethod(numpy.full)
    """ create an array filled with a constant value """

    @staticmethod
    def bmm(arr1, arr2):
        """batch matrix multiply two arrays"""
        return numpy.einsum("ijk,ikl->ijl", arr1, arr2)

    @staticmethod
    def is_array(arr):
        """check if an object is an array"""
        return isinstance(arr, numpy.ndarray)

    # constructors
    array = _replace_float(numpy.array)
    """ create an array from an array-like sequence """

    ones = _replace_float(numpy.ones)
    """ create an array filled with ones """

    zeros = _replace_float(numpy.zeros)
    """ create an array filled with zeros """

    meshgrid = staticmethod(numpy.meshgrid)
    """ create coordinate matrices from coordinate vectors """

    @staticmethod
    def zeros_like(arr):
        """create an array filled with zeros with same shape as input
        创建与输入相同形状的零填充数组"""
        # 检查是否是GPU张量 / Check if GPU tensor
        if hasattr(arr, 'device') and 'cuda' in str(arr.device):
            arr = arr.cpu()
        # 检查是否是torch张量 / Check if torch tensor
        if hasattr(arr, 'numpy') and callable(getattr(arr, 'numpy')):
            arr = arr.numpy()
        return numpy.zeros_like(arr)
    """ create an array filled with zeros """

    linspace = _replace_float(numpy.linspace)
    """ create a linearly spaced array between two points """

    arange = _replace_float(numpy.arange)
    """ create a range of values """

    pad = staticmethod(numpy.pad)

    fftfreq = staticmethod(numpy.fft.fftfreq)

    fft = staticmethod(numpy.fft.fft)

    exp = staticmethod(numpy.exp)

    divide = staticmethod(numpy.divide)

    """ create an uninitialized array """

    # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    # beware to future people:
    # because this line *redefines numpy*,
    # you have to add your new staticmethods /above/ this line to avoid mystification.
    # <3 <3 <3 <3
    #
    # could this (and below) perhaps be changed to "to_numpy()"
    # or maybe "check_numpy" ?
    numpy = _replace_float(numpy.asarray)
    """ convert the array to numpy array """

    @staticmethod
    def void(data):
        if isinstance(data, bytes):
            # 检查数据大小，如果太大则分块处理
            if len(data) > 2 ** 31 - 1:  # numpy.void 的最大限制
                # 对于大型数据，直接返回原始字节数据
                return data
            return numpy.void(data)
        else:
            arr_bytes = numpy.asarray(data).tobytes()
            if len(arr_bytes) > 2 ** 31 - 1:
                return arr_bytes
            return numpy.void(arr_bytes)
    """convert data to void array for HDF5 storage"""

# Torch Backend
if TORCH_AVAILABLE:
    import torch

    class TorchBackend(Backend):
        """Torch Backend"""

        # types
        abs = torch.abs

        int = torch.int64
        """ integer type for array"""

        float = torch.get_default_dtype()
        """ floating type for array """

        empty = staticmethod(numpy.empty)
        """ create an uninitialized array """

        @staticmethod
        def to_float(tensor):
            if hasattr(tensor, 'to'):  # 检查是否是 PyTorch 张量
                return tensor.to(dtype=torch.float)
            elif hasattr(tensor, 'astype'):  # 检查是否是 NumPy 数组
                return tensor.astype(float)
            else:
                raise TypeError("Unsupported tensor type for conversion to float.")
        """ convert tensor to float type, same to numpy.float64 """

        if float is torch.float32:
            complex = torch.complex64
        else:
            complex = torch.complex128
        """ complex type for array """

        @staticmethod
        def astype(arr, dtype):
            """convert tensor to specified type"""
            if torch.is_tensor(arr):
                if dtype == float:
                    return arr.to(torch.get_default_dtype())
                elif hasattr(torch, str(dtype)):
                    return arr.to(getattr(torch, str(dtype)))
                else:
                    return arr.to(dtype)
            else:
                return torch.tensor(arr, dtype=dtype)

        # methods
        asarray = staticmethod(torch.as_tensor)
        """ create an array """

        exp = staticmethod(torch.exp)
        """ exponential of all elements in array """

        sin = staticmethod(torch.sin)
        """ sine of all elements in array """

        cos = staticmethod(torch.cos)
        """ cosine of all elements in array """

        @staticmethod
        def sum(x, axis=None, **kwargs):
            """sum elements in array with axis support"""
            # 将 axis 参数转换为 PyTorch 的 dim 参数
            if axis is not None:
                kwargs['dim'] = axis
            return torch.sum(x, **kwargs)
        """ sum elements in array """

        min = staticmethod(torch.min)
        """ min element in array """

        max = staticmethod(torch.max)
        """ max element in array """

        argmax = staticmethod(torch.argmax)
        """ index of max element in array """

        where = staticmethod(torch.where)
        """ return elements of array where condition is True, otherwise return other elements """

        stack = staticmethod(torch.stack)
        """ stack multiple arrays """

        cat = staticmethod(torch.cat)
        """ concatenate multiple arrays along a given dimension, only for fourier.FrequencyRountines.FFT """

        @staticmethod
        def cross(a, b, axis=-1):
            """计算两个张量的叉积"""
            if not torch.is_tensor(a):
                a = torch.tensor(a)
            if not torch.is_tensor(b):
                b = torch.tensor(b)
            return torch.cross(a, b, dim=axis)

        arctan2 = staticmethod(torch.atan2)
        """ arctangent of y/x with correct quadrant """

        @staticmethod
        def any(x, axis=None, **kwargs):
            """test whether any array element along a given axis evaluates to True"""
            if axis is not None:
                kwargs['dim'] = axis
            return torch.any(x, **kwargs)

        @staticmethod
        def shape(x):
            """return the shape of an array"""
            if torch.is_tensor(x):
                return x.shape
            else:
                return torch.tensor(x).shape

        @staticmethod
        def radians(x):
            """convert degrees to radians"""
            if torch.is_tensor(x):
                return torch.deg2rad(x)
            else:
                return torch.deg2rad(torch.tensor(x))

        @staticmethod
        def sqrt(x):
            if isinstance(x, torch.Tensor):
                return torch.sqrt(x)
            else:
                return torch.sqrt(torch.tensor(x, dtype=torch.get_default_dtype()))

        @staticmethod
        def round(x):
            if isinstance(x, torch.Tensor):
                return torch.round(x)
            else:
                return round(x)

        @staticmethod
        def full(shape, fill_value, dtype=None):
            if isinstance(shape, int):
                shape = (shape,)
            if dtype is None:
                return torch.full(shape, fill_value)
            else:
                return torch.full(shape, fill_value, dtype=getattr(torch, str(dtype)))

        @staticmethod
        def transpose(arr, axes=None):
            """transpose array by flipping two dimensions"""
            import numpy
            if isinstance(arr, numpy.ndarray):
                return numpy.transpose(arr, axes)
            if axes is None:
                axes = tuple(range(len(arr.shape) - 1, -1, -1))
            return arr.permute(*axes)

        squeeze = staticmethod(torch.squeeze)
        """ remove dim-1 dimensions """

        broadcast_arrays = staticmethod(torch.broadcast_tensors)
        """ broadcast arrays """

        broadcast_to = staticmethod(torch.broadcast_to)
        """ broadcast array into shape """

        reshape = staticmethod(torch.reshape)
        """ reshape array into given shape """

        bmm = staticmethod(torch.bmm)
        """ batch matrix multiply two arrays """

        @staticmethod
        def void(data):
            """convert data to void array for HDF5 storage"""
            import numpy
            if isinstance(data, bytes):
                # 检查数据大小，如果太大则分块处理
                if len(data) > 2 ** 31 - 1:  # numpy.void 的最大限制
                    # 对于大型数据，直接返回原始字节数据
                    return data
                return numpy.void(data)
            else:
                # 如果是torch张量，先转到CPU
                if hasattr(data, 'cpu'):
                    data = data.cpu()
                if hasattr(data, 'numpy'):
                    data = data.numpy()
                arr_bytes = numpy.asarray(data).tobytes()
                if len(arr_bytes) > 2 ** 31 - 1:
                    return arr_bytes
                return numpy.void(arr_bytes)
        """ convert data to void array for HDF5 storage """

        @staticmethod
        def is_array(arr):
            """check if an object is an array"""
            # is this a reasonable implemenation?
            return isinstance(arr, numpy.ndarray) or torch.is_tensor(arr)

        def array(self, arr, dtype=None):
            """create an array from an array-like sequence"""
            if dtype is None:
                dtype = torch.get_default_dtype()
            if torch.is_tensor(arr):
                return arr.clone().to(device="cpu", dtype=dtype)
            return torch.tensor(arr, device="cpu", dtype=dtype)

        # constructors
        ones = staticmethod(torch.ones)
        """ create an array filled with ones """

        zeros = staticmethod(torch.zeros)
        """ create an array filled with zeros """

        zeros_like = staticmethod(torch.zeros_like)

        meshgrid = staticmethod(torch.meshgrid)
        """ create coordinate matrices from coordinate vectors """

        def linspace(self, start, stop, num=50, endpoint=True):
            """create a linearly spaced array between two points"""
            delta = (stop - start) / float(num - float(endpoint))
            if not delta:
                return self.array([start] * num)
            return torch.arange(start, stop + 0.5 * float(endpoint) * delta, delta)

        arange = staticmethod(torch.arange)
        """ create a range of values """

        pad = staticmethod(torch.nn.functional.pad)  # type: ignore

        fftfreq = staticmethod(torch.fft.fftfreq)

        fft = staticmethod(torch.fft.fft)  # type: ignore

        divide = staticmethod(torch.div)

        exp = staticmethod(torch.exp)
        # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        # The same warning applies here.
        # <3 <3 <3 <3

        def numpy(self, arr):
            """convert the array to numpy array"""
            if torch.is_tensor(arr):
                return arr.numpy()
            else:
                return numpy.asarray(arr)

    # Torch Cuda Backend
    if TORCH_CUDA_AVAILABLE:

        class TorchCudaBackend(TorchBackend):
            """Torch Cuda Backend"""
            #TODO: max, abs?
            def ones(self, shape, dtype=None):
                """create an array filled with ones"""
                return torch.ones(shape, device="cuda", dtype=dtype)

            def zeros(self, shape, dtype=None):
                """create an array filled with zeros"""
                return torch.zeros(shape, device="cuda", dtype=dtype)

            def empty(self, shape, dtype=None):
                """create an uninitialized tensor on CUDA"""
                if dtype is None:
                    dtype = torch.get_default_dtype()
                return torch.empty(shape, device="cuda", dtype=dtype)

            @staticmethod
            def astype(arr, dtype):
                """convert tensor to specified type on CUDA"""
                if torch.is_tensor(arr):
                    if dtype == float:
                        return arr.to(torch.get_default_dtype()).cuda()
                    elif hasattr(torch, str(dtype)):
                        return arr.to(getattr(torch, str(dtype))).cuda()
                    else:
                        return arr.to(dtype).cuda()
                else:
                    return torch.tensor(arr, dtype=dtype, device="cuda")

            @staticmethod
            def arctan2(y, x):
                """arctangent of y/x with correct quadrant on CUDA"""
                if not torch.is_tensor(y):
                    y = torch.tensor(y, device="cuda")
                if not torch.is_tensor(x):
                    x = torch.tensor(x, device="cuda")
                return torch.atan2(y.cuda(), x.cuda())

            @staticmethod
            def radians(x):
                """convert degrees to radians on CUDA"""
                if not torch.is_tensor(x):
                    x = torch.tensor(x, device="cuda")
                return torch.deg2rad(x.cuda())

            @staticmethod
            def meshgrid(*tensors, **kwargs):
                """create coordinate matrices from coordinate vectors"""
                # 确保张量在 CUDA 设备上
                cuda_tensors = []
                for tensor in tensors:
                    if torch.is_tensor(tensor):
                        cuda_tensors.append(tensor.cuda())
                    else:
                        cuda_tensors.append(torch.tensor(tensor, device="cuda"))
                return torch.meshgrid(*cuda_tensors, **kwargs)
            """ create coordinate matrices from coordinate vectors """

            def array(self, arr, dtype=None):
                """create an array from an array-like sequence"""
                if dtype is None:
                    dtype = torch.get_default_dtype()
                if torch.is_tensor(arr):
                    return arr.clone().to(device="cuda", dtype=dtype)
                return torch.tensor(arr, device="cuda", dtype=dtype)

            # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            # The same warning applies here.
            def numpy(self, arr):
                """convert the array to numpy array"""
                if torch.is_tensor(arr):
                    return arr.cpu().numpy()
                else:
                    return numpy.asarray(arr)

            def linspace(self, start, stop, num=50, endpoint=True):
                """convert a linearly spaced interval of values"""
                delta = (stop - start) / float(num - float(endpoint))
                if not delta:
                    return self.array([start] * num)
                return torch.arange(
                    start, stop + 0.5 * float(endpoint) * delta, delta, device="cuda"
                )

            @staticmethod
            def void(data):
                """convert data to void array for HDF5 storage"""
                import numpy
                if isinstance(data, bytes):
                    # 检查数据大小，如果太大则分块处理
                    if len(data) > 2 ** 31 - 1:  # numpy.void 的最大限制
                        # 对于大型数据，直接返回原始字节数据
                        return data
                    return numpy.void(data)
                else:
                    arr_bytes = numpy.asarray(data).tobytes()
                    if len(arr_bytes) > 2 ** 31 - 1:
                        return arr_bytes
                    return numpy.void(arr_bytes)

## Default Backend
# this backend object will be used for all array/tensor operations.
# the backend is changed by changing the class of the backend
# using the "set_backend" function. This "monkeypatch" will replace all the methods
# of the backend object by the methods supplied by the new class.
backend = NumpyBackend()


## Set backend
def set_backend(name: str):
    """Set the backend for the FDTD simulations

    This function monkeypatches the backend object by changing its class.
    This way, all methods of the backend object will be replaced.

    Args:
        name: name of the backend. Allowed backend names:
            - ``numpy`` (defaults to float64 arrays)
            - ``numpy.float16``
            - ``numpy.float32``
            - ``numpy.float64``
            - ``numpy.float128``
            - ``torch`` (defaults to float64 tensors)
            - ``torch.float16``
            - ``torch.float32``
            - ``torch.float64``
            - ``torch.cuda`` (defaults to float64 tensors)
            - ``torch.cuda.float16``
            - ``torch.cuda.float32``
            - ``torch.cuda.float64``

    """
    # perform checks
    if name.startswith("torch") and not TORCH_AVAILABLE:
        raise RuntimeError("Torch backend is not available. Is PyTorch installed?")
    if name.startswith("torch.cuda") and not TORCH_CUDA_AVAILABLE:
        raise RuntimeError(
            "Torch cuda backend is not available.\n"
            "Do you have a GPU on your computer?\n"
            "Is PyTorch with cuda support installed?"
        )

    if name.count(".") == 0:
        dtype, device = "float64", "cpu"
    elif name.count(".") == 1:
        name, dtype = name.split(".")
        if dtype == "cuda":
            device, dtype = "cuda", "float64"
        else:
            device = "cpu"
    elif name.count(".") == 2:
        name, device, dtype = name.split(".")
    else:
        raise ValueError(f"Unknown backend '{name}'")

    if name == "numpy":
        if device == "cpu":
            backend.__class__ = NumpyBackend
            backend.float = getattr(numpy, dtype)
        elif device == "cuda":
            raise ValueError(
                "Device 'cuda' not available for numpy backend. Use 'torch' backend in stead."
            )
        else:
            raise ValueError(
                "Unknown device '{device}'. Available devices: 'cpu', 'cuda'"
            )
    elif name == "torch":
        if device == "cpu":
            backend.__class__ = TorchBackend
            backend.float = getattr(torch, dtype)
        elif device == "cuda":
            backend.__class__ = TorchCudaBackend
            backend.float = getattr(torch, dtype)
        else:
            raise ValueError(
                "Unknown device '{device}'. Available devices: 'cpu', 'cuda'"
            )
    else:
        raise ValueError(
            "Unknown backend '{name}'. Available backends: 'numpy', 'torch'"
        )
