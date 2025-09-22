r"""Spectral transform implementations for neural networks.

This module provides implementations of spectral transforms used in
spectral transformer architectures. All transforms implement consistent interfaces
through the base classes, enabling easy substitution and experimentation with different
spectral methods. The transforms support both real and complex inputs, batch processing,
and multi-dimensional operations where applicable.

Modules
-------
base
    Base classes and interfaces for spectral transforms.
cosine
    Discrete Cosine and Sine Transform implementations.
fourier
    Fast Fourier Transform implementations.
hadamard
    Hadamard and related orthogonal transforms.
wavelet
    Discrete Wavelet Transform implementations.

Classes
-------
AdaptiveTransform
    Transform with learnable parameters for adaptation.
DCT
    Discrete Cosine Transform implementation.
DCT2D
    2D Discrete Cosine Transform for image-like data.
DST
    Discrete Sine Transform implementation.
DWT1D
    1D Discrete Wavelet Transform.
DWT2D
    2D Discrete Wavelet Transform.
FFT1D
    1D Fast Fourier Transform with real/complex support.
FFT2D
    2D Fast Fourier Transform for AFNO-style operations.
HadamardTransform
    Fast Hadamard Transform implementation.
HadamardTransform2D
    2D Hadamard Transform implementation.
MDCT
    Modified Discrete Cosine Transform for audio processing.
MultiResolutionTransform
    Base class for multi-resolution decompositions.
NeuralSpectralTransform
    Transform with neural network components.
OrthogonalTransform
    Base class for orthogonal transforms (DCT, DST, Hadamard).
RFFT
    Real-input Fast Fourier Transform.
RFFT2D
    2D Real-input Fast Fourier Transform.
SequencyHadamardTransform
    Sequency-ordered Hadamard transform.
SlantTransform
    Slant transform implementation.
SpectralPooling
    Spectral pooling operation in frequency domain.
SpectralTransform
    Base class for simple 1D spectral transforms.
UnitaryTransform
    Base class for unitary transforms (FFT).

Examples
--------
Using Fourier transforms:

>>> from spectrans.transforms import FFT1D, RFFT
>>> # Complex-input FFT
>>> fft = FFT1D()
>>> complex_output = fft.transform(complex_input)
>>> reconstructed = fft.inverse_transform(complex_output)
>>>
>>> # Real-input FFT
>>> rfft = RFFT()
>>> freq_domain = rfft.transform(real_input)

Using orthogonal transforms:

>>> from spectrans.transforms import DCT, HadamardTransform
>>> # Discrete Cosine Transform
>>> dct = DCT(normalized=True)
>>> dct_coeffs = dct.transform(signal)
>>>
>>> # Fast Hadamard Transform
>>> hadamard = HadamardTransform()
>>> hadamard_coeffs = hadamard.transform(signal, dim=-1)

Using wavelet transforms:

>>> from spectrans.transforms import DWT1D
>>> dwt = DWT1D(wavelet='db4', levels=3)
>>> approx_coeffs, detail_coeffs = dwt.decompose(signal)
>>> reconstructed = dwt.reconstruct((approx_coeffs, detail_coeffs))

Notes
-----
Mathematical Properties:

The transforms maintain important mathematical properties:

1. **Orthogonal Transforms** (DCT, DST, Hadamard):
   - Preserve inner products: $\langle \mathbf{x}, \mathbf{y} \rangle = \langle \mathcal{T}(\mathbf{x}), \mathcal{T}(\mathbf{y}) \rangle$
   - Perfect reconstruction: $\mathcal{T}^{-1}(\mathcal{T}(\mathbf{x})) = \mathbf{x}$
   - Energy conservation (Parseval's theorem)

2. **Unitary Transforms** (FFT):
   - Complex inner product preservation
   - Norm conservation: $||\mathcal{T}(\mathbf{x})||_2 = ||\mathbf{x}||_2$
   - Hermitian symmetry for real inputs

3. **Multi-Resolution Transforms** (DWT):
   - Perfect reconstruction from coefficients
   - Localization in both time and frequency
   - Compact support for finite-length wavelets

Implementation Details:

- All transforms support batch processing with proper broadcasting
- Complex number operations use the spectrans.utils.complex module
- Numerical stability is ensured through proper scaling and normalization
- GPU acceleration through PyTorch's native FFT operations
- In-place operations used where possible

Performance Characteristics:

- FFT: $O(n \log n)$ time complexity
- DCT/DST: $O(n \log n)$ via FFT-based algorithms
- Hadamard: $O(n \log n)$ fast transform algorithms
- DWT: $O(n)$ time complexity with compact support wavelets

See Also
--------
[`spectrans.transforms.base`][] : Base classes and interfaces.
[`spectrans.utils.complex`][] : Complex tensor operations.
[`spectrans.core.registry`][] : Component registration for transforms.
"""

from .base import (
    AdaptiveTransform,
    MultiResolutionTransform,
    NeuralSpectralTransform,
    OrthogonalTransform,
    SpectralTransform,
    UnitaryTransform,
)
from .cosine import DCT, DCT2D, DST, MDCT
from .fourier import FFT1D, FFT2D, RFFT, RFFT2D, SpectralPooling
from .hadamard import (
    HadamardTransform,
    HadamardTransform2D,
    SequencyHadamardTransform,
    SlantTransform,
)
from .wavelet import DWT1D, DWT2D

__all__ = [
    "DCT",
    "DCT2D",
    "DST",
    "DWT1D",
    "DWT2D",
    "FFT1D",
    "FFT2D",
    "MDCT",
    "RFFT",
    "RFFT2D",
    "AdaptiveTransform",
    "HadamardTransform",
    "HadamardTransform2D",
    "MultiResolutionTransform",
    "NeuralSpectralTransform",
    "OrthogonalTransform",
    "SequencyHadamardTransform",
    "SlantTransform",
    "SpectralPooling",
    "SpectralTransform",
    "UnitaryTransform",
]
