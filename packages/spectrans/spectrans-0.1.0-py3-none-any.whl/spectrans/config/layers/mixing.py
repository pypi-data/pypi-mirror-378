"""Configuration models for mixing layer components.

This module provides Pydantic models for validating and typing configuration
data used to construct mixing layers in spectrans.

Classes
-------
WaveletMixingConfig
    Configuration for WaveletMixing layer.
WaveletMixing2DConfig
    Configuration for WaveletMixing2D layer.
FourierMixingConfig
    Configuration for Fourier mixing layers.
GlobalFilterMixingConfig
    Configuration for global filter mixing layers.

Notes
-----
All configuration models use Pydantic v2 BaseModel for validation and type safety.
Mixing layer configurations inherit from base layer configuration classes in the
parent models module.

Examples
--------
>>> from spectrans.config.layers.mixing import WaveletMixingConfig
>>> config = WaveletMixingConfig(hidden_dim=768, wavelet="db4", levels=3)
>>> print(config.wavelet)
'db4'
"""

from typing import Literal

from pydantic import BaseModel, Field, field_validator

from ...core.types import ActivationType, WaveletType
from ..core import BaseLayerConfig, FilterLayerConfig, UnitaryLayerConfig


class WaveletMixingConfig(BaseLayerConfig):
    """Configuration model for WaveletMixing layer.

    Attributes
    ----------
    wavelet : WaveletType
        Wavelet family name, defaults to "db4".
    levels : int
        Number of decomposition levels, must be between 1 and 6, defaults to 3.
    mixing_mode : Literal["pointwise", "subband"]
        Mixing operation mode, defaults to "pointwise".
    """

    wavelet: WaveletType = Field(default="db4", description="Wavelet family name")
    levels: int = Field(default=3, ge=1, le=6, description="Number of decomposition levels")
    mixing_mode: Literal["pointwise", "subband"] = Field(
        default="pointwise", description="Mixing operation mode"
    )

    @field_validator("wavelet")
    @classmethod
    def validate_wavelet(cls, v: WaveletType) -> WaveletType:
        """Validate that wavelet name is supported."""
        if not v:
            raise ValueError("Wavelet name cannot be empty")
        return v


class WaveletMixing2DConfig(BaseModel):
    """Configuration model for WaveletMixing2D layer.

    Attributes
    ----------
    channels : int
        Number of input channels, must be positive.
    wavelet : WaveletType
        Wavelet family name, defaults to "db4".
    levels : int
        Number of decomposition levels, must be between 1 and 6, defaults to 2.
    mixing_mode : Literal["subband", "channel"]
        2D mixing operation mode, defaults to "subband".
    """

    channels: int = Field(gt=0, description="Number of input channels")
    wavelet: WaveletType = Field(default="db4", description="Wavelet family name")
    levels: int = Field(default=2, ge=1, le=6, description="Number of decomposition levels")
    mixing_mode: Literal["subband", "channel"] = Field(
        default="subband", description="2D mixing operation mode"
    )

    @field_validator("wavelet")
    @classmethod
    def validate_wavelet(cls, v: WaveletType) -> WaveletType:
        """Validate that wavelet name is supported."""
        if not v:
            raise ValueError("Wavelet name cannot be empty")
        return v


class FourierMixingConfig(UnitaryLayerConfig):
    """Configuration for standard Fourier mixing layers.

    Attributes
    ----------
    keep_complex : bool
        If True, keeps complex values from FFT. If False (default),
        takes only the real part as in original FNet.
    """

    keep_complex: bool = Field(
        default=False,
        description="Keep complex values from FFT (True) or extract real part only (False)",
    )


class GlobalFilterMixingConfig(FilterLayerConfig):
    """Configuration for global filter mixing layers.

    Attributes
    ----------
    activation : ActivationType
        Activation function for filters, defaults to "sigmoid".
    """

    activation: ActivationType = Field(default="sigmoid", description="Filter activation function")


class AFNOMixingConfig(BaseLayerConfig):
    """Configuration for Adaptive Fourier Neural Operator mixing layers.

    Attributes
    ----------
    max_sequence_length : int
        Maximum sequence length for mode truncation, must be positive.
    modes_seq : int | None
        Number of Fourier modes in sequence dimension, defaults to max_sequence_length // 2.
    modes_hidden : int | None
        Number of Fourier modes in hidden dimension, defaults to hidden_dim // 2.
    mlp_ratio : float
        MLP expansion ratio in frequency domain, defaults to 2.0.
    activation : ActivationType
        Activation function for MLP, defaults to "gelu".
    """

    max_sequence_length: int = Field(gt=0, description="Maximum sequence length")
    modes_seq: int | None = Field(
        default=None, ge=1, description="Fourier modes in sequence dimension"
    )
    modes_hidden: int | None = Field(
        default=None, ge=1, description="Fourier modes in hidden dimension"
    )
    mlp_ratio: float = Field(default=2.0, gt=0.0, description="MLP expansion ratio")
    activation: ActivationType = Field(default="gelu", description="MLP activation function")
