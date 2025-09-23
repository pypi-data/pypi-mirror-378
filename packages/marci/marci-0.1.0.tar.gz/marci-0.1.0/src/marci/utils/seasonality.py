from __future__ import annotations

import numpy as np
import pandas as pd


class Seasonality:
    # fixed, internal anchor — not a parameter
    _ANCHOR = pd.Timestamp("2000-01-01")

    def __init__(
        self,
        weekly_harmonics=4,
        monthly_harmonics=1,
        annual_harmonics=5,
        weekly_prominance=1.5,
        monthly_prominance=1.5,
        annual_prominance=4,
        seed=None,
        month_days=30.4375,
        year_days=365.2425,
    ):
        self.Kw, self.Km, self.Ky = map(
            int, (weekly_harmonics, monthly_harmonics, annual_harmonics)
        )
        self.ww, self.wm, self.wy = (
            float(weekly_prominance),
            float(monthly_prominance),
            float(annual_prominance),
        )
        self.W, self.M, self.Y = 7.0, float(month_days), float(year_days)
        self.rng = np.random.default_rng(seed)

        def ab(K):
            if K <= 0:
                return None, None
            k = np.arange(1, K + 1, dtype=float)
            s = 1 / np.sqrt(k)  # softer higher harmonics
            return self.rng.normal(0, s), self.rng.normal(0, s)

        self.aw, self.bw = ab(self.Kw)
        self.am, self.bm = ab(self.Km)
        self.ay, self.by = ab(self.Ky)

    def _fourier(self, t, period, K, a, b, weight):
        if (K is None) or (K <= 0) or (weight == 0):
            return np.zeros_like(t, dtype=float)
        k = np.arange(1, K + 1, dtype=float)  # (K,)
        omega = 2 * np.pi * k / period  # (K,)
        C = np.cos(t[:, None] * omega[None, :])  # (N,K)
        S = np.sin(t[:, None] * omega[None, :])  # (N,K)
        return weight * (C @ a + S @ b)  # (N,)

    def _raw(self, index: pd.DatetimeIndex) -> np.ndarray:
        # GLOBAL phase anchored to fixed epoch
        t = ((index - self._ANCHOR) / pd.Timedelta(days=1)).to_numpy(dtype=float)
        y = (
            self._fourier(t, self.W, self.Kw, self.aw, self.bw, self.ww)
            + self._fourier(t, self.M, self.Km, self.am, self.bm, self.wm)
            + self._fourier(t, self.Y, self.Ky, self.ay, self.by, self.wy)
        )
        return y

    def values(self, index: pd.DatetimeIndex, cv=0.1) -> pd.Series:
        if not isinstance(index, pd.DatetimeIndex):
            raise TypeError("index must be a pandas.DatetimeIndex")

        y = self._raw(index)

        if cv == 0:
            return pd.Series(np.ones(len(index)), index=index)

        # local normalization (z-scores)
        mu = float(y.mean())
        sd = float(y.std(ddof=0)) or 1.0
        z = (y - mu) / sd

        # lognormal mapping
        s = np.sqrt(np.log1p(cv**2))
        out = np.exp(z * s - 0.5 * s**2)

        # enforce exact mean=1 (rescale multiplicatively)
        out /= out.mean()

        return pd.Series(out, index=index)

    def raw_standardized(self, index: pd.DatetimeIndex) -> pd.Series:
        """Optional helper: window-local z-scored raw trend (mean 0, std 1)."""
        y = self._raw(index)
        sd = float(y.std(ddof=0)) or 1.0
        return pd.Series((y - float(y.mean())) / sd, index=index)
