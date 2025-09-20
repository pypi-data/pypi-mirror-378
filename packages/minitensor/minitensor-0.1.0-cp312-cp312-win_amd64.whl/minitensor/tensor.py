# Copyright (c) 2025 Soumyadip Sarkar.
# All rights reserved.
#
# This source code is licensed under the Apache-style license found in the
# LICENSE file in the root directory of this source tree.

"""
Tensor class with NumPy compatibility and automatic differentiation support.
"""

try:
    from . import _core as _minitensor_core
except ImportError as e:
    raise ImportError(
        "The minitensor core extension is not built. "
        "Run `pip install -e .` or `maturin develop` to compile the Rust backend."
    ) from e

from typing import Any, List, Optional, Sequence, Tuple, Union

import numpy as np

# Mapping between NumPy dtypes and Tensor dtype strings
_TENSOR_TO_NP_DTYPE = {
    "float32": np.dtype(np.float32),
    "float64": np.dtype(np.float64),
    "int32": np.dtype(np.int32),
    "int64": np.dtype(np.int64),
    "bool": np.dtype(np.bool_),
}

_NP_TO_TENSOR_DTYPE = {v: k for k, v in _TENSOR_TO_NP_DTYPE.items()}

# Global default dtype management
_DEFAULT_DTYPE = "float32"
_VALID_DTYPES = set(_TENSOR_TO_NP_DTYPE.keys())


def set_default_dtype(dtype: str) -> None:
    """Set the global default data type for new tensors."""
    if dtype not in _VALID_DTYPES:
        raise ValueError(f"Unsupported dtype '{dtype}'")
    global _DEFAULT_DTYPE
    _DEFAULT_DTYPE = dtype


def get_default_dtype() -> str:
    """Get the current global default data type."""
    return _DEFAULT_DTYPE


def _resolve_dtype(dtype: Optional[str]) -> str:
    return dtype if dtype is not None else _DEFAULT_DTYPE


class Tensor:
    """
    A multi-dimensional array with automatic differentiation support and NumPy compatibility.
    This class wraps a Rust backend for efficient tensor computations and provides a unified interface
    for both NumPy and Python.
    """

    # Ensure NumPy treats Tensor as having higher priority in operations
    # so that dispatch prefers Tensor's implementations over NumPy's defaults.
    __array_priority__ = 1000

    # Mapping of NumPy ufuncs to Tensor operations. These lambdas ensure that
    # all computations are executed by the Rust backend by leveraging the
    # Tensor's arithmetic and math methods.
    _UFUNC_BINARY_MAP = {
        np.add: lambda a, b: a + b,
        np.subtract: lambda a, b: a - b,
        np.multiply: lambda a, b: a * b,
        np.true_divide: lambda a, b: a / b,
        np.power: lambda a, b: a.pow(b),
        np.maximum: lambda a, b: a.maximum(b),
        np.minimum: lambda a, b: a.minimum(b),
    }

    _UFUNC_UNARY_MAP = {
        np.negative: lambda a: -a,
        np.exp: lambda a: a.exp(),
        np.log: lambda a: a.log(),
        np.sqrt: lambda a: a.sqrt(),
        np.abs: lambda a: a.abs(),
        np.sin: lambda a: a.sin(),
        np.cos: lambda a: a.cos(),
        np.tan: lambda a: a.tan(),
    }

    def __init__(
        self,
        data: Any,
        requires_grad: bool = False,
        dtype: Optional[str] = None,
        device=None,
    ):
        """
        Initialize a tensor.

        Args:
            data: Input data (list, numpy array, scalar, or another tensor)
            requires_grad: Whether to track gradients for automatic differentiation
            dtype: Data type ('float32', 'float64', 'int32', 'int64', 'bool')
            device: Device to place tensor on (CPU, CUDA, etc.)

        Examples:
            >>> t1 = Tensor([1, 2, 3])
            >>> t2 = Tensor([[1, 2], [3, 4]], dtype='float64')
            >>> t3 = Tensor(np.array([1.0, 2.0]), requires_grad=True)
        """
        if isinstance(data, Tensor):
            # Copy constructor
            self._tensor = data._tensor.clone()
        else:
            # Create new tensor from data
            dtype = _resolve_dtype(dtype)
            self._tensor = _minitensor_core.Tensor(data, dtype, device, requires_grad)

    # Core properties
    @property
    def shape(self) -> Tuple[int, ...]:
        """Get tensor shape as tuple."""
        return tuple(self._tensor.shape)

    @property
    def dtype(self) -> str:
        """Get tensor data type."""
        return self._tensor.dtype

    @property
    def device(self) -> str:
        """Get tensor device."""
        return self._tensor.device

    @property
    def requires_grad(self) -> bool:
        """Check if tensor requires gradients."""
        return self._tensor.requires_grad

    @property
    def grad(self) -> Optional["Tensor"]:
        """Get gradient tensor from the global autograd graph."""
        rust_grad = _minitensor_core.get_gradient(self._tensor)
        if rust_grad is not None:
            result = Tensor.__new__(Tensor)
            result._tensor = rust_grad
            return result
        return None

    # NumPy compatibility properties
    @property
    def size(self) -> int:
        """Total number of elements."""
        return self._tensor.size

    @property
    def itemsize(self) -> int:
        """Size of each element in bytes."""
        return self._tensor.itemsize

    @property
    def nbytes(self) -> int:
        """Total bytes consumed by the tensor."""
        return self._tensor.nbytes

    @property
    def strides(self) -> Tuple[int, ...]:
        """Strides of the tensor."""
        return tuple(self._tensor.strides)

    @property
    def ndim(self) -> int:
        """Number of dimensions."""
        return self._tensor.ndim()

    @property
    def T(self) -> "Tensor":
        """Transpose."""
        return self.transpose()

    # Basic tensor info methods
    def numel(self) -> int:
        """Get total number of elements."""
        return self._tensor.numel()

    def dim(self) -> int:
        """Get number of dimensions."""
        return self.ndim

    def is_contiguous(self) -> bool:
        """Check if tensor is contiguous in memory."""
        return self._tensor.is_contiguous()

    def element_size(self) -> int:
        """Get size of each element in bytes."""
        return self.itemsize

    # Data conversion methods
    def numpy(self) -> np.ndarray:
        """Convert to numpy array with zero-copy when possible."""
        try:
            return self._tensor.numpy()
        except NotImplementedError:
            return self._tensor.numpy_copy()

    def numpy_copy(self) -> np.ndarray:
        """Convert to numpy array with explicit copy."""
        return self._tensor.numpy_copy()

    def __array__(self, dtype: Optional[np.dtype] = None) -> np.ndarray:
        """Support NumPy's array protocol for seamless interoperability."""
        array = self.numpy()
        if dtype is not None:
            return array.astype(dtype, copy=False)
        return array

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        """Dispatch NumPy ufuncs to Tensor operations executed in Rust."""
        if method != "__call__" or kwargs.get("out") is not None:
            return NotImplemented

        np_dtypes = []
        tensor_inputs = []

        for x in inputs:
            if isinstance(x, Tensor):
                tensor_inputs.append(x)
                np_dtypes.append(_TENSOR_TO_NP_DTYPE[x.dtype])
            elif isinstance(x, np.ndarray):
                if x.dtype in _NP_TO_TENSOR_DTYPE:
                    arr_tensor = Tensor.from_numpy(x)
                else:
                    arr_tensor = Tensor(x.tolist())
                tensor_inputs.append(arr_tensor)
                np_dtypes.append(x.dtype)
            else:
                arr_tensor = Tensor(x)
                tensor_inputs.append(arr_tensor)
                np_dtypes.append(np.array(x).dtype)

        result_np_dtype = np.result_type(*np_dtypes)
        target_dtype = _NP_TO_TENSOR_DTYPE.get(np.dtype(result_np_dtype), "float32")
        tensor_inputs = [
            t if t.dtype == target_dtype else t.astype(target_dtype)
            for t in tensor_inputs
        ]

        if ufunc in self._UFUNC_BINARY_MAP and len(tensor_inputs) == 2:
            return self._UFUNC_BINARY_MAP[ufunc](tensor_inputs[0], tensor_inputs[1])

        if ufunc in self._UFUNC_UNARY_MAP and len(tensor_inputs) == 1:
            return self._UFUNC_UNARY_MAP[ufunc](tensor_inputs[0])

        return NotImplemented

    def tolist(self) -> List:
        """Convert to Python list."""
        if self.numel() == 0:
            return []
        return self._tensor.tolist()

    def item(self) -> Union[float, int, bool]:
        """Get scalar value from single-element tensor."""
        if self.numel() != 1:
            raise ValueError("item() can only be called on tensors with one element")
        return self.tolist()

    # Tensor manipulation methods
    def reshape(self, *shape: Union[int, Sequence[int]]) -> "Tensor":
        """Reshape tensor to new shape."""
        if len(shape) == 1 and isinstance(shape[0], (list, tuple)):
            shape = list(shape[0])
        else:
            shape = list(shape)

        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.reshape(shape)
        return result

    def view(self, *shape: Union[int, Sequence[int]]) -> "Tensor":
        """Alias for reshape."""
        return self.reshape(*shape)

    def transpose(self, dim0: int = 0, dim1: int = 1) -> "Tensor":
        """Transpose tensor dimensions."""
        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.transpose(dim0, dim1)
        return result

    def permute(self, *dims: int) -> "Tensor":
        """Permute tensor dimensions."""
        if len(dims) == 1 and isinstance(dims[0], (list, tuple)):
            dims = list(dims[0])
        else:
            dims = list(dims)
        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.permute(dims)
        return result

    def movedim(
        self, source: Union[int, Sequence[int]], destination: Union[int, Sequence[int]]
    ) -> "Tensor":
        """Move tensor dimensions to new positions."""

        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.movedim(source, destination)
        return result

    moveaxis = movedim

    def swapaxes(self, axis0: int, axis1: int) -> "Tensor":
        """Swap two dimensions of the tensor."""

        return self.transpose(axis0, axis1)

    swapdims = swapaxes

    def squeeze(self, dim: Optional[int] = None) -> "Tensor":
        """Remove dimensions of size 1."""
        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.squeeze(dim)
        return result

    def unsqueeze(self, dim: int) -> "Tensor":
        """Add a dimension of size 1."""
        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.unsqueeze(dim)
        return result

    def expand(self, *shape: int) -> "Tensor":
        """Expand tensor dimensions without allocating new memory."""
        if len(shape) == 1 and isinstance(shape[0], (list, tuple)):
            dims = list(shape[0])
        else:
            dims = list(shape)
        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.expand(dims)
        return result

    def repeat(self, *repeats: int) -> "Tensor":
        """Repeat the tensor along each dimension."""

        if len(repeats) == 1 and isinstance(repeats[0], (list, tuple)):
            repeats = tuple(repeats[0])
        if len(repeats) < self.ndim:
            raise ValueError(
                "number of dimensions of repeat dims can not be smaller than number of dimensions of tensor"
            )

        repeats = tuple(int(r) for r in repeats)
        if any(r <= 0 for r in repeats):
            raise ValueError("repeats must be positive")

        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.repeat(list(repeats))
        return result

    def flip(self, dims: Union[int, Sequence[int]]) -> "Tensor":
        """Flip the tensor along given dimensions."""

        if isinstance(dims, int):
            dims_list = [dims]
        else:
            dims_list = list(dims)

        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.flip(dims_list)
        return result

    def roll(
        self,
        shifts: Union[int, Sequence[int]],
        dims: Optional[Union[int, Sequence[int]]] = None,
    ) -> "Tensor":
        """Roll the tensor along given dimensions with wrap-around."""

        if isinstance(shifts, int):
            shift_list = [int(shifts)]
        else:
            shift_list = [int(s) for s in shifts]

        if dims is None:
            dims_list = None
        else:
            if isinstance(dims, int):
                dims_list = [int(dims)]
            else:
                dims_list = [int(d) for d in dims]

        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.roll(shift_list, dims_list)
        return result

    def narrow(self, dim: int, start: int, length: int) -> "Tensor":
        """Narrow the tensor along ``dim`` starting at ``start`` for ``length`` elements."""

        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.narrow(dim, start, length)
        return result

    def index_select(self, dim: int, indices: Sequence[int]) -> "Tensor":
        """Select elements along ``dim`` using integer ``indices``."""

        idx_list = [int(i) for i in indices]
        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.index_select(dim, idx_list)
        return result

    def gather(self, dim: int, index: "Tensor") -> "Tensor":
        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.gather(dim, index._tensor)
        return result

    def flatten(self, start_dim: int = 0, end_dim: int = -1) -> "Tensor":
        """Flatten tensor dimensions."""
        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.flatten(start_dim, end_dim)
        return result

    def ravel(self) -> "Tensor":
        """Return flattened tensor (NumPy compatibility)."""
        return self.flatten()

    def split(
        self,
        split_size_or_sections: Union[int, Sequence[int]],
        dim: int = 0,
    ) -> List["Tensor"]:
        """Split the tensor into chunks along ``dim``.

        Args:
            split_size_or_sections: Size of each chunk or list/tuple of sizes
                for each chunk.
            dim: Dimension along which to split. May be negative to index
                from the end.

        Returns:
            List[Tensor]: Tensors resulting from the split.
        """

        if not isinstance(split_size_or_sections, int):
            split_size_or_sections = list(split_size_or_sections)
        parts = self._tensor.split(split_size_or_sections, dim)
        result: List[Tensor] = []
        for p in parts:
            t = Tensor.__new__(Tensor)
            t._tensor = p
            result.append(t)
        return result

    def chunk(self, chunks: int, dim: int = 0) -> List["Tensor"]:
        """Split the tensor into equal sized chunks along ``dim``.

        Args:
            chunks: Number of chunks to return. The tensor size along ``dim``
                must be divisible by ``chunks``.
            dim: Dimension along which to split the tensor.

        Returns:
            List[Tensor]: List of ``chunks`` tensors split from this tensor.
        """

        parts = self._tensor.chunk(int(chunks), dim)
        result = []
        for p in parts:
            t = Tensor.__new__(Tensor)
            t._tensor = p
            result.append(t)
        return result

    # Tensor operations
    def clone(self) -> "Tensor":
        """Create a copy of the tensor."""
        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.clone()
        return result

    def copy(self) -> "Tensor":
        """Create a copy of the tensor (NumPy compatibility)."""
        return self.clone()

    def detach(self) -> "Tensor":
        """Detach tensor from computation graph."""
        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.detach()
        return result

    def contiguous(self) -> "Tensor":
        """Create a contiguous copy of the tensor."""
        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.contiguous()
        return result

    def to(self, device_or_dtype: Union[str, "Tensor"]) -> "Tensor":
        """Move tensor to device or convert dtype."""
        if isinstance(device_or_dtype, str):
            if device_or_dtype in ["cpu", "cuda", "metal"]:
                # Device conversion
                result = Tensor.__new__(Tensor)
                result._tensor = self._tensor.to(device_or_dtype)
                return result
            else:
                return self.astype(device_or_dtype)
        else:
            raise TypeError("to() expects device string or dtype")

    def cpu(self) -> "Tensor":
        """Move tensor to CPU."""
        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.cpu()
        return result

    def cuda(self, device: Optional[int] = None) -> "Tensor":
        """Move tensor to CUDA device."""
        # Simplified - would need proper CUDA device handling
        return self.to("cuda")

    def astype(self, dtype: str) -> "Tensor":
        """Convert tensor to a different data type."""
        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.astype(dtype)
        return result

    # Gradient operations
    def backward(
        self,
        gradient: Optional["Tensor"] = None,
        retain_graph: bool = False,
        create_graph: bool = False,
    ):
        """Compute gradients via backpropagation."""
        if gradient is None:
            self._tensor.backward(None)
        else:
            self._tensor.backward(gradient._tensor)

    def requires_grad_(self, requires_grad: bool = True) -> "Tensor":
        """Set requires_grad flag in-place."""
        self._tensor.requires_grad_(requires_grad)
        return self

    def zero_grad(self, set_to_none: bool = False):
        """Zero the gradient."""
        self._tensor.zero_grad(set_to_none)

    # Arithmetic operations with broadcasting support
    def __neg__(self) -> "Tensor":
        """Unary negation returning a Tensor."""
        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.__neg__()
        return result

    def __add__(self, other: Union["Tensor", float, int]) -> "Tensor":
        if not isinstance(other, Tensor):
            other = Tensor(other, dtype=self.dtype)

        if self.numel() == 0 or other.numel() == 0:
            if self.dtype != other.dtype:
                raise TypeError("Cannot add tensors with different dtypes")
            try:
                result_shape = np.broadcast_shapes(self.shape, other.shape)
            except ValueError as e:
                raise ValueError("Shapes are not broadcastable") from e
            result = Tensor.__new__(Tensor)
            result._tensor = _minitensor_core.Tensor.zeros(
                list(result_shape), self.dtype, None, False
            )
            return result

        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.__add__(other._tensor)
        return result

    def __radd__(self, other: Union[float, int]) -> "Tensor":
        return self.__add__(other)

    def __sub__(self, other: Union["Tensor", float, int]) -> "Tensor":
        if not isinstance(other, Tensor):
            other = Tensor(other, dtype=self.dtype)

        if self.numel() == 0 or other.numel() == 0:
            if self.dtype != other.dtype:
                raise TypeError("Cannot subtract tensors with different dtypes")
            try:
                result_shape = np.broadcast_shapes(self.shape, other.shape)
            except ValueError as e:
                raise ValueError("Shapes are not broadcastable") from e
            result = Tensor.__new__(Tensor)
            result._tensor = _minitensor_core.Tensor.zeros(
                list(result_shape), self.dtype, None, False
            )
            return result

        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.__sub__(other._tensor)
        return result

    def __rsub__(self, other: Union[float, int]) -> "Tensor":
        scalar_tensor = Tensor(other)
        return scalar_tensor.__sub__(self)

    def __mul__(self, other: Union["Tensor", float, int]) -> "Tensor":
        if not isinstance(other, Tensor):
            other = Tensor(other, dtype=self.dtype)

        if self.numel() == 0 or other.numel() == 0:
            if self.dtype != other.dtype:
                raise TypeError("Cannot multiply tensors with different dtypes")
            try:
                result_shape = np.broadcast_shapes(self.shape, other.shape)
            except ValueError as e:
                raise ValueError("Shapes are not broadcastable") from e
            result = Tensor.__new__(Tensor)
            result._tensor = _minitensor_core.Tensor.zeros(
                list(result_shape), self.dtype, None, False
            )
            return result

        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.__mul__(other._tensor)
        return result

    def __rmul__(self, other: Union[float, int]) -> "Tensor":
        return self.__mul__(other)

    def __truediv__(self, other: Union["Tensor", float, int]) -> "Tensor":
        if not isinstance(other, Tensor):
            other = Tensor(other, dtype=self.dtype)

        if self.numel() == 0 or other.numel() == 0:
            if self.dtype != other.dtype:
                raise TypeError("Cannot divide tensors with different dtypes")
            try:
                result_shape = np.broadcast_shapes(self.shape, other.shape)
            except ValueError as e:
                raise ValueError("Shapes are not broadcastable") from e
            result = Tensor.__new__(Tensor)
            result._tensor = _minitensor_core.Tensor.zeros(
                list(result_shape), self.dtype, None, False
            )
            return result

        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.__truediv__(other._tensor)
        return result

    def __rtruediv__(self, other: Union[float, int]) -> "Tensor":
        scalar_tensor = Tensor(other)
        return scalar_tensor.__truediv__(self)

    def __pow__(self, exponent: Union["Tensor", float, int]) -> "Tensor":
        """Element-wise power operation."""
        exp_tensor = exponent._tensor if isinstance(exponent, Tensor) else exponent
        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.pow(exp_tensor)
        if isinstance(exponent, Tensor):
            exp_floor = exponent.astype("int64").astype(exponent.dtype)
            frac_mask = exponent.ne(exp_floor).astype("int32")
            neg_mask = self.lt(0).astype("int32")
            mask = (neg_mask * frac_mask).astype("bool")
            if bool(mask.any().numpy()):
                res_np = result.numpy()
                mask_np = mask.numpy().astype(bool)
                res_np[mask_np] = 0.0
                result = Tensor(res_np, dtype=self.dtype)
        return result

    def pow(self, exponent: Union["Tensor", float, int]) -> "Tensor":
        """Alias for the ``**`` operator."""
        return self.__pow__(exponent)

    def __matmul__(self, other: "Tensor") -> "Tensor":
        """Matrix multiplication operator (@)."""
        return self.matmul(other)

    # Matrix operations
    def matmul(self, other: "Tensor") -> "Tensor":
        """Matrix multiplication."""
        if not isinstance(other, Tensor):
            raise TypeError("matmul requires another Tensor")
        if self.dtype != other.dtype:
            raise TypeError("matmul requires tensors to have the same dtype")
        if self.dtype == "bool":
            raise ValueError("matmul does not support bool tensors")
        if self.ndim < 2 or other.ndim < 2:
            raise ValueError("matmul requires tensors with at least 2 dims")
        if self.shape[:-2] != other.shape[:-2]:
            raise ValueError("matmul batch dimensions must match")
        if self.shape[-1] != other.shape[-2]:
            raise ValueError("matmul dimension mismatch")

        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.matmul(other._tensor)
        return result

    def mm(self, other: "Tensor") -> "Tensor":
        """Matrix multiplication."""
        return self.matmul(other)

    def dot(self, other: "Tensor") -> "Tensor":
        """Dot product."""
        if self.ndim == 1 and other.ndim == 1:
            return (self * other).sum()
        else:
            return self.matmul(other)

    def cross(self, other: "Tensor", axis: int = -1) -> "Tensor":
        """Compute the 3D cross product with another tensor.

        Args:
            other: The tensor to compute the cross product with. If a plain
                Python value is provided it will be converted to a ``Tensor``
                with the same dtype as ``self``.
            axis: The axis along which to compute the cross product. Defaults
                to the last dimension.

        Returns:
            Tensor: The resulting cross product tensor.
        """
        if not isinstance(other, Tensor):
            other = Tensor(other, dtype=self.dtype)

        result = Tensor.__new__(Tensor)
        result._tensor = _minitensor_core.numpy_compat.cross(
            self._tensor, other._tensor, axis=axis
        )
        return result

    # Reduction operations
    def prod(
        self, dim: Optional[Union[int, Tuple[int, ...]]] = None, keepdim: bool = False
    ) -> "Tensor":
        """Product along specified dimensions."""
        if isinstance(dim, int):
            dim = [dim]
        elif isinstance(dim, tuple):
            dim = list(dim)

        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.prod(dim, keepdim)
        return result

    def sum(
        self, dim: Optional[Union[int, Tuple[int, ...]]] = None, keepdim: bool = False
    ) -> "Tensor":
        """Sum along specified dimensions."""
        if isinstance(dim, int):
            dim = [dim]
        elif isinstance(dim, tuple):
            dim = list(dim)

        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.sum(dim, keepdim)
        return result

    def mean(
        self, dim: Optional[Union[int, Tuple[int, ...]]] = None, keepdim: bool = False
    ) -> "Tensor":
        """Mean along specified dimensions."""
        if isinstance(dim, int):
            dim = [dim]
        elif isinstance(dim, tuple):
            dim = list(dim)

        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.mean(dim, keepdim)
        return result

    def max(
        self, dim: Optional[int] = None, keepdim: bool = False
    ) -> Union["Tensor", Tuple["Tensor", "Tensor"]]:
        """Maximum values along dimension."""
        if dim is None:
            result = Tensor.__new__(Tensor)
            result._tensor = self._tensor.max(dim, keepdim)
            return result

        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.max(dim, keepdim)
        indices = Tensor.__new__(Tensor)
        indices._tensor = self._tensor.argmax(dim, keepdim)

        return result, indices

    def min(
        self, dim: Optional[int] = None, keepdim: bool = False
    ) -> Union["Tensor", Tuple["Tensor", "Tensor"]]:
        """Minimum values along dimension."""
        if dim is None:
            result = Tensor.__new__(Tensor)
            result._tensor = self._tensor.min(dim, keepdim)
            return result

        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.min(dim, keepdim)
        indices = Tensor.__new__(Tensor)
        indices._tensor = self._tensor.argmin(dim, keepdim)

        return result, indices

    def argmax(self, dim: Optional[int] = None, keepdim: bool = False) -> "Tensor":
        """Indices of maximum values."""
        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.argmax(dim, keepdim)
        return result

    def argmin(self, dim: Optional[int] = None, keepdim: bool = False) -> "Tensor":
        """Indices of minimum values."""
        if dim is not None:
            dim = dim + self.ndim if dim < 0 else dim
            if dim < 0 or dim >= self.ndim:
                raise IndexError("Dimension out of range")
        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.argmin(dim, keepdim)
        return result

    def std(
        self, dim: Optional[int] = None, keepdim: bool = False, unbiased: bool = True
    ) -> "Tensor":
        """Standard deviation along dimension."""
        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.std(dim, keepdim)
        return result

    def var(
        self, dim: Optional[int] = None, keepdim: bool = False, unbiased: bool = True
    ) -> "Tensor":
        """Variance along dimension."""
        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.var(dim, keepdim)
        return result

    # Mathematical functions
    def abs(self) -> "Tensor":
        """Absolute value."""
        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.abs()
        return result

    def sqrt(self) -> "Tensor":
        """Square root."""
        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.sqrt()
        return result

    def exp(self) -> "Tensor":
        """Exponential function."""
        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.exp()
        return result

    def log(self) -> "Tensor":
        """Natural logarithm."""
        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.log()
        return result

    def sin(self) -> "Tensor":
        """Element-wise sine computed in Rust."""
        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.sin()
        return result

    def cos(self) -> "Tensor":
        """Element-wise cosine computed in Rust."""
        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.cos()
        return result

    def tan(self) -> "Tensor":
        """Element-wise tangent computed in Rust."""
        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.tan()
        return result

    # Activation functions
    def relu(self) -> "Tensor":
        """ReLU activation function."""
        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.relu()
        return result

    def sigmoid(self) -> "Tensor":
        """Sigmoid activation function."""
        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.sigmoid()
        return result

    def tanh(self) -> "Tensor":
        """Hyperbolic tangent activation function."""
        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.tanh()
        return result

    def softmax(self, dim: int = -1) -> "Tensor":
        """Softmax activation function."""
        # Numerically stable softmax implementation
        x_max, _ = self.max(dim=dim, keepdim=True)
        x_shifted = self - x_max
        exp_x = x_shifted.exp()
        return exp_x / exp_x.sum(dim=dim, keepdim=True)

    def log_softmax(self, dim: int = -1) -> "Tensor":
        """Log-softmax activation function."""
        return self.softmax(dim).log()

    # Comparison operations
    def eq(self, other: Any) -> "Tensor":
        """Element-wise equality comparison."""
        if not isinstance(other, Tensor):
            other = Tensor(other, dtype=self.dtype)
        elif other.dtype != self.dtype:
            raise TypeError("Cannot compare tensors with different dtypes")
        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.eq(other._tensor)
        return result

    def ne(self, other: Any) -> "Tensor":
        """Element-wise not-equal comparison."""
        if not isinstance(other, Tensor):
            other = Tensor(other, dtype=self.dtype)
        elif other.dtype != self.dtype:
            raise TypeError("Cannot compare tensors with different dtypes")
        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.ne(other._tensor)
        return result

    def lt(self, other: Any) -> "Tensor":
        """Element-wise less-than comparison."""
        if not isinstance(other, Tensor):
            other = Tensor(other, dtype=self.dtype)
        elif other.dtype != self.dtype:
            raise TypeError("Cannot compare tensors with different dtypes")
        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.lt(other._tensor)
        return result

    def le(self, other: Any) -> "Tensor":
        """Element-wise less-than-or-equal comparison."""
        if not isinstance(other, Tensor):
            other = Tensor(other, dtype=self.dtype)
        elif other.dtype != self.dtype:
            raise TypeError("Cannot compare tensors with different dtypes")
        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.le(other._tensor)
        return result

    def gt(self, other: Any) -> "Tensor":
        """Element-wise greater-than comparison."""
        if not isinstance(other, Tensor):
            other = Tensor(other, dtype=self.dtype)
        elif other.dtype != self.dtype:
            raise TypeError("Cannot compare tensors with different dtypes")
        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.gt(other._tensor)
        return result

    def ge(self, other: Any) -> "Tensor":
        """Element-wise greater-than-or-equal comparison."""
        if not isinstance(other, Tensor):
            other = Tensor(other, dtype=self.dtype)
        elif other.dtype != self.dtype:
            raise TypeError("Cannot compare tensors with different dtypes")
        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.ge(other._tensor)
        return result

    def maximum(self, other: "Tensor") -> "Tensor":
        """Element-wise maximum computed via Rust-backed operations."""
        if not isinstance(other, Tensor):
            other = Tensor(other, dtype=self.dtype)
        elif other.dtype != self.dtype:
            other = other.astype(self.dtype)

        if self.dtype == "bool" and other.dtype == "bool":
            return self.astype("int32").maximum(other.astype("int32")).astype("bool")

        mask = self.ge(other).astype(self.dtype)
        one = Tensor(1, dtype=self.dtype)
        return mask * self + (one - mask) * other

    def minimum(self, other: "Tensor") -> "Tensor":
        """Element-wise minimum computed via Rust-backed operations."""
        if not isinstance(other, Tensor):
            other = Tensor(other, dtype=self.dtype)
        elif other.dtype != self.dtype:
            other = other.astype(self.dtype)

        if self.dtype == "bool" and other.dtype == "bool":
            return self.astype("int32").minimum(other.astype("int32")).astype("bool")

        mask = self.le(other).astype(self.dtype)
        one = Tensor(1, dtype=self.dtype)
        return mask * self + (one - mask) * other

    # Python special methods for comparisons
    def __eq__(self, other: object) -> "Tensor":
        if not isinstance(other, Tensor):
            try:
                other = Tensor(other, dtype=self.dtype)
            except Exception:
                return NotImplemented
        return self.eq(other)

    def __ne__(self, other: object) -> "Tensor":
        if not isinstance(other, Tensor):
            try:
                other = Tensor(other, dtype=self.dtype)
            except Exception:
                return NotImplemented
        return self.ne(other)

    def __lt__(self, other: object) -> "Tensor":
        if not isinstance(other, Tensor):
            try:
                other = Tensor(other, dtype=self.dtype)
            except Exception:
                return NotImplemented
        return self.lt(other)

    def __le__(self, other: object) -> "Tensor":
        if not isinstance(other, Tensor):
            try:
                other = Tensor(other, dtype=self.dtype)
            except Exception:
                return NotImplemented
        return self.le(other)

    def __gt__(self, other: object) -> "Tensor":
        if not isinstance(other, Tensor):
            try:
                other = Tensor(other, dtype=self.dtype)
            except Exception:
                return NotImplemented
        return self.gt(other)

    def __ge__(self, other: object) -> "Tensor":
        if not isinstance(other, Tensor):
            try:
                other = Tensor(other, dtype=self.dtype)
            except Exception:
                return NotImplemented
        return self.ge(other)

    # Utility methods
    def all(self, dim: Optional[int] = None, keepdim: bool = False) -> "Tensor":
        """Test if all elements evaluate to True."""
        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.all(dim, keepdim)
        return result

    def any(self, dim: Optional[int] = None, keepdim: bool = False) -> "Tensor":
        """Test if any element evaluates to True."""
        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.any(dim, keepdim)
        return result

    def cumsum(self, dim: int) -> "Tensor":
        """Cumulative sum along a dimension."""
        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.cumsum(dim)
        return result

    def cumprod(self, dim: int) -> "Tensor":
        """Cumulative product along a dimension."""
        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.cumprod(dim)
        return result

    def clamp(
        self, min_val: Optional[float] = None, max_val: Optional[float] = None
    ) -> "Tensor":
        """Clamp tensor values to range."""
        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.clamp(min_val, max_val)
        return result

    def clip(
        self, min_val: Optional[float] = None, max_val: Optional[float] = None
    ) -> "Tensor":
        """Clip tensor values to range (NumPy compatibility)."""
        return self.clamp(min_val, max_val)

    # Array testing
    def isnan(self) -> "Tensor":
        """Test for NaN values."""
        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.isnan()
        return result

    def isinf(self) -> "Tensor":
        """Test for infinite values."""
        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.isinf()
        return result

    def isfinite(self) -> "Tensor":
        """Test for finite values."""
        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.isfinite()
        return result

    # Comparison with other tensors
    def allclose(self, other: "Tensor", rtol: float = 1e-5, atol: float = 1e-8) -> bool:
        """Check if tensors are approximately equal."""
        return self._tensor.allclose(other._tensor, rtol, atol)

    def array_equal(self, other: "Tensor") -> bool:
        """Check if tensors are exactly equal."""
        return self._tensor.array_equal(other._tensor)

    # String representations
    def __repr__(self) -> str:
        return self._tensor.__repr__()

    def __str__(self) -> str:
        return self._tensor.__str__()

    def __len__(self) -> int:
        return self._tensor.__len__()

    def __bool__(self) -> bool:
        return self._tensor.__bool__()

    # Indexing and slicing (simplified)
    def __getitem__(self, key):
        """Tensor indexing and slicing."""

        def _check_slice(k):
            if isinstance(k, slice):
                if k.step not in (None, 1):
                    raise IndexError("slice step must be 1")
            elif isinstance(k, tuple):
                for item in k:
                    _check_slice(item)

        _check_slice(key)
        result = Tensor.__new__(Tensor)
        result._tensor = self._tensor.__getitem__(key)
        return result

    def __setitem__(self, key, value):
        """Tensor item assignment."""
        if isinstance(value, Tensor):
            self._tensor.__setitem__(key, value._tensor)
        else:
            self._tensor.__setitem__(key, value)

    # Static tensor creation methods
    @staticmethod
    def zeros(
        *shape: Union[int, Sequence[int]],
        dtype: Optional[str] = None,
        device=None,
        requires_grad: bool = False,
    ) -> "Tensor":
        """Create a tensor filled with zeros."""
        if len(shape) == 1 and isinstance(shape[0], (list, tuple)):
            shape = shape[0]
        dtype = _resolve_dtype(dtype)
        result = Tensor.__new__(Tensor)
        result._tensor = _minitensor_core.Tensor.zeros(
            list(shape), dtype, device, requires_grad
        )
        return result

    @staticmethod
    def ones(
        *shape: Union[int, Sequence[int]],
        dtype: Optional[str] = None,
        device=None,
        requires_grad: bool = False,
    ) -> "Tensor":
        """Create a tensor filled with ones."""
        if len(shape) == 1 and isinstance(shape[0], (list, tuple)):
            shape = shape[0]
        dtype = _resolve_dtype(dtype)
        result = Tensor.__new__(Tensor)
        result._tensor = _minitensor_core.Tensor.ones(
            list(shape), dtype, device, requires_grad
        )
        return result

    @staticmethod
    def full(
        shape: Sequence[int],
        fill_value: float,
        dtype: Optional[str] = None,
        device=None,
        requires_grad: bool = False,
    ) -> "Tensor":
        """Create a tensor filled with a specific value."""
        dtype = _resolve_dtype(dtype)
        result = Tensor.__new__(Tensor)
        result._tensor = _minitensor_core.Tensor.full(
            list(shape), fill_value, dtype, device, requires_grad
        )
        return result

    @staticmethod
    def rand(
        *shape: Union[int, Sequence[int]],
        dtype: Optional[str] = None,
        device=None,
        requires_grad: bool = False,
    ) -> "Tensor":
        """Create a tensor with random values from uniform distribution [0, 1)."""
        if len(shape) == 1 and isinstance(shape[0], (list, tuple)):
            shape = shape[0]
        dtype = _resolve_dtype(dtype)
        result = Tensor.__new__(Tensor)
        result._tensor = _minitensor_core.Tensor.rand(
            list(shape), dtype, device, requires_grad
        )
        return result

    @staticmethod
    def randn(
        *shape: Union[int, Sequence[int]],
        dtype: Optional[str] = None,
        device=None,
        requires_grad: bool = False,
    ) -> "Tensor":
        """Create a tensor with random values from standard normal distribution."""
        if len(shape) == 1 and isinstance(shape[0], (list, tuple)):
            shape = shape[0]
        dtype = _resolve_dtype(dtype)
        result = Tensor.__new__(Tensor)
        result._tensor = _minitensor_core.Tensor.randn(
            list(shape), dtype, device, requires_grad
        )
        return result

    @staticmethod
    def eye(
        n: int,
        m: Optional[int] = None,
        dtype: Optional[str] = None,
        device=None,
        requires_grad: bool = False,
    ) -> "Tensor":
        """Create an identity matrix."""
        dtype = _resolve_dtype(dtype)
        result = Tensor.__new__(Tensor)
        result._tensor = _minitensor_core.Tensor.eye(n, m, dtype, device, requires_grad)
        return result

    @staticmethod
    def arange(
        start: float,
        end: Optional[float] = None,
        step: float = 1.0,
        dtype: Optional[str] = None,
        device=None,
        requires_grad: bool = False,
    ) -> "Tensor":
        """Create a tensor with evenly spaced values."""
        if end is None:
            end = start
            start = 0.0
        dtype = _resolve_dtype(dtype)
        result = Tensor.__new__(Tensor)
        result._tensor = _minitensor_core.Tensor.arange(
            start, end, step, dtype, device, requires_grad
        )
        return result

    @staticmethod
    def linspace(
        start: float,
        end: float,
        steps: int,
        dtype: Optional[str] = None,
        device=None,
        requires_grad: bool = False,
    ) -> "Tensor":
        """Create a tensor with linearly spaced values."""
        if steps <= 1:
            raise ValueError("Number of steps must be greater than 1")
        step = (end - start) / (steps - 1)
        dtype = _resolve_dtype(dtype)
        return Tensor.arange(start, end + step / 2, step, dtype, device, requires_grad)

    @staticmethod
    def logspace(
        start: float,
        end: float,
        steps: int,
        base: float = 10.0,
        dtype: Optional[str] = None,
        device=None,
        requires_grad: bool = False,
    ) -> "Tensor":
        """Create a tensor with logarithmically spaced values."""
        dtype = _resolve_dtype(dtype)
        linear = Tensor.linspace(start, end, steps, dtype, device, requires_grad)
        return Tensor(base) ** linear

    @staticmethod
    def from_numpy(array: np.ndarray, requires_grad: bool = False) -> "Tensor":
        """Create a tensor from a NumPy array."""
        result = Tensor.__new__(Tensor)
        result._tensor = _minitensor_core.Tensor.from_numpy(array, requires_grad)
        return result

    @staticmethod
    def from_numpy_shared(array: np.ndarray, requires_grad: bool = False) -> "Tensor":
        """Create a tensor from a NumPy array with zero-copy when possible."""
        result = Tensor.__new__(Tensor)
        result._tensor = _minitensor_core.Tensor.from_numpy_shared(array, requires_grad)
        return result


# Convenience functions for tensor creation (NumPy-style)
def tensor(
    data: Any, dtype: Optional[str] = None, device=None, requires_grad: bool = False
) -> Tensor:
    """Create a tensor from data."""
    return Tensor(data, requires_grad=requires_grad, dtype=dtype, device=device)


def zeros(
    *shape: Union[int, Sequence[int]],
    dtype: Optional[str] = None,
    device=None,
    requires_grad: bool = False,
) -> Tensor:
    """Create a tensor filled with zeros."""
    return Tensor.zeros(*shape, dtype=dtype, device=device, requires_grad=requires_grad)


def ones(
    *shape: Union[int, Sequence[int]],
    dtype: Optional[str] = None,
    device=None,
    requires_grad: bool = False,
) -> Tensor:
    """Create a tensor filled with ones."""
    return Tensor.ones(*shape, dtype=dtype, device=device, requires_grad=requires_grad)


def full(
    shape: Sequence[int],
    fill_value: float,
    dtype: Optional[str] = None,
    device=None,
    requires_grad: bool = False,
) -> Tensor:
    """Create a tensor filled with a specific value."""
    return Tensor.full(
        shape, fill_value, dtype=dtype, device=device, requires_grad=requires_grad
    )


def rand(
    *shape: Union[int, Sequence[int]],
    dtype: Optional[str] = None,
    device=None,
    requires_grad: bool = False,
) -> Tensor:
    """Create a tensor with random values from uniform distribution."""
    return Tensor.rand(*shape, dtype=dtype, device=device, requires_grad=requires_grad)


def randn(
    *shape: Union[int, Sequence[int]],
    dtype: Optional[str] = None,
    device=None,
    requires_grad: bool = False,
) -> Tensor:
    """Create a tensor with random values from normal distribution."""
    return Tensor.randn(*shape, dtype=dtype, device=device, requires_grad=requires_grad)


def eye(
    n: int,
    m: Optional[int] = None,
    dtype: Optional[str] = None,
    device=None,
    requires_grad: bool = False,
) -> Tensor:
    """Create an identity matrix."""
    return Tensor.eye(n, m, dtype=dtype, device=device, requires_grad=requires_grad)


def arange(
    start: float,
    end: Optional[float] = None,
    step: float = 1.0,
    dtype: Optional[str] = None,
    device=None,
    requires_grad: bool = False,
) -> Tensor:
    """Create a tensor with evenly spaced values."""
    return Tensor.arange(
        start, end, step, dtype=dtype, device=device, requires_grad=requires_grad
    )


def linspace(
    start: float,
    end: float,
    steps: int,
    dtype: Optional[str] = None,
    device=None,
    requires_grad: bool = False,
) -> Tensor:
    """Create a tensor with linearly spaced values."""
    return Tensor.linspace(
        start, end, steps, dtype=dtype, device=device, requires_grad=requires_grad
    )


def from_numpy(array: np.ndarray, requires_grad: bool = False) -> Tensor:
    """Create a tensor from a NumPy array."""
    return Tensor.from_numpy(array, requires_grad=requires_grad)


# Export all public symbols
__all__ = [
    "Tensor",
    "tensor",
    "zeros",
    "ones",
    "full",
    "rand",
    "randn",
    "eye",
    "arange",
    "linspace",
    "from_numpy",
    "set_default_dtype",
    "get_default_dtype",
]
