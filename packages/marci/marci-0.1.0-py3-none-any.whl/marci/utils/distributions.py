from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Final

import numpy as np


class Distribution(ABC):
	def __init__(self, mean: float, cv: float) -> None:
		self.mean: Final[float] = float(mean)
		self.cv: Final[float] = float(cv)

	@abstractmethod
	def generate(self, size: int) -> np.ndarray:
		"""Generate random samples from the distribution.

		Args:
			size: Number of samples to generate. Must be a positive integer.

		Returns:
			A 1D numpy array of random samples.
		"""
		raise NotImplementedError

	def __repr__(self) -> str:
		return f"{self.__class__.__name__}(mean={self.mean}, cv={self.cv})"


class Lognormal(Distribution):
	def __init__(self, mean: float, cv: float) -> None:
		super().__init__(mean, cv)

		self.sigma: Final[float] = float(np.sqrt(np.log(1.0 + self.cv**2)))
		self.mu: Final[float] = float(np.log(self.mean) - 0.5 * self.sigma**2)

	def generate(self, size: int) -> np.ndarray:
		if not isinstance(size, int) or size <= 0:
			raise ValueError("size must be a positive integer")
		return np.random.lognormal(self.mu, self.sigma, size)
