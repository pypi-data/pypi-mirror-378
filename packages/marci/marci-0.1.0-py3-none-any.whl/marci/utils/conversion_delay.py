from __future__ import annotations

import matplotlib.pyplot as plt
from typing import Union

import numpy as np
import pandas as pd

from .math_utils import antidiag_sums
from .plot_utils import style


class Conversion_Delay:
    def __init__(self, p: float = 0.3, duration: int = 7):
        """
        p: probability that a conversion is delayed beyond day 1 (0..1)
        duration: number of days in the attribution window (>=1)
        """
        if not (0 <= p <= 1):
            raise ValueError("p must be in [0, 1].")
        if duration < 1:
            raise ValueError("duration must be >= 1.")
        self.p = float(p)
        self.duration = int(duration)

    @property
    def probs(self) -> np.ndarray:
        # Single-day window: all conversions on day 1
        if self.duration == 1:
            return np.array([1.0], dtype=float)

        p = np.zeros(self.duration, dtype=float)
        p[0] = 1 - self.p  # day 1 share is 1 - delayed probability

        # Distribute delayed mass over days 2..duration
        rem = self.p
        k = np.arange(1, self.duration)  # days 2..D
        # Stretched-exponential weights; power tied to p for continuity with your draft
        power = min(self.p, 1 - self.p) if self.p not in (0.0, 1.0) else 1.0
        u = np.exp(-(k**power))

        # Normalize tail to sum to 'rem'
        tail = rem * (u / u.sum())
        p[1:] = tail

        # Guard against tiny FP drift; force exact sum to 1
        p[-1] += 1.0 - p.sum()
        return p

    def delay(
        self, convs: Union[pd.Series, np.ndarray, list[int], list[float]]
    ) -> pd.Series:
        """
        x: array-like of totals (integers). Returns (N, duration) aggregated along antidiagonals.
        """
        x = np.asarray(convs)
        if x.ndim != 1:
            x = x.ravel()
        if np.any(x < 0):
            raise ValueError("x must be non-negative.")
        probs = self.probs  # compute once
        attr_convs = np.empty((len(x), self.duration), dtype=int)
        for i, n in enumerate(x):
            attr_convs[i] = np.random.multinomial(int(n), probs)
        attr_convs = antidiag_sums(attr_convs).astype(int)

        # Build date index: if convs is a Series use its index, else start today
        if isinstance(convs, pd.Series) and len(convs.index) > 0:
            start = convs.index.min()
        else:
            start = pd.Timestamp.today().normalize()
        date_range = pd.date_range(
            start=start, periods=len(x) + self.duration - 1, freq="D"
        )
        return pd.Series(attr_convs, index=date_range, name="attr_convs")

    def plot(self, ax=None, bar_width=0.8):
        """Plot the conversion delay distribution as a bar chart."""
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 5))

        probs = self.probs
        days = np.arange(1, self.duration + 1)

        ax.bar(
            days,
            probs,
            width=bar_width,
            alpha=0.7,
            color="dodgerblue",
        )

        # Add value labels on top of bars
        for i, (day, prob) in enumerate(zip(days, probs)):
            ax.text(
                day, prob + 0.01, f"{prob:.2%}", ha="center", va="bottom", fontsize=9
            )
        style(
            ax,
            y_fmt="%",
            x_label="Day",
            y_label="Probability",
            title="Conversion Delay",
            legend=False,
        )

        return ax
