from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


from .utils import Conversion_Delay, Elasticity, Lognormal, Seasonality, style


class Campaign:
    def __init__(
        self,
        name: str = "Campaign",
        cpm: float = 10,
        cvr: float = 1e-4,
        aov: float = 100,
        cv: float = 0.1,
        seasonality_cv: float = 0.2,
        conversion_delay: float = 0.3,
        elasticity: float = 0.9,
        baseline: float = 1000,
        is_organic: bool = False,
    ):
        self.name = name
        self.cpm = cpm
        self.cvr = cvr
        self.aov = aov
        self.cv = cv
        self.seasonality_cv = seasonality_cv
        self.Delay = Conversion_Delay(p=conversion_delay)
        self.Elasticity = Elasticity(elasticity_coef=elasticity)
        self.baseline = baseline
        self.is_organic = is_organic
        self.Seasonality = Seasonality()

    def expected_roas(self, avg_spend: float = None):
        if avg_spend is None:
            avg_spend = self.baseline
        if self.is_organic:
            return 1000 * self.cvr * self.aov / self.cpm
        elasticity = self.Elasticity.roas(avg_spend / self.baseline)
        return 1000 * self.cvr * self.aov / self.cpm * elasticity

    def expected_sales(self, avg_spend: float = None):
        if avg_spend is None:
            avg_spend = self.baseline
        if self.is_organic:
            return 1000 * self.cvr * self.aov / self.cpm * avg_spend
        elasticity = self.Elasticity.roas(avg_spend / self.baseline)
        return 1000 * self.cvr * self.aov / self.cpm * elasticity * avg_spend

    def sim_outcomes(
        self,
        start_date: str = "2025-01-01",
        periods: int = 90,
        avg_spend: float = None,
        cv: float = None,
        seasonality_cv: float = None,
        plot: bool = False,
    ):
        if avg_spend is None:
            avg_spend = self.baseline
        if cv is None:
            cv = self.cv
        if seasonality_cv is None:
            seasonality_cv = self.seasonality_cv

        Spend = Lognormal(mean=avg_spend, cv=cv)
        date_range = pd.date_range(start=start_date, periods=periods)
        df = pd.DataFrame(index=date_range)

        df["base_spend"] = Spend.generate(periods)
        df["seasonality"] = self.Seasonality.values(date_range, cv=seasonality_cv)
        df["spend"] = df["base_spend"] * df["seasonality"]
        df["spend_relative_to_baseline"] = df["spend"] / self.baseline
        df["elasticity"] = self.Elasticity.roas(df["spend_relative_to_baseline"])

        CPM = Lognormal(mean=self.cpm * (1 + cv**2), cv=cv)
        CVR = Lognormal(mean=self.cvr, cv=cv)
        AOV = Lognormal(mean=self.aov, cv=cv)
        df["cpm"] = CPM.generate(periods) / df["elasticity"]
        df["cvr"] = CVR.generate(periods) * df["elasticity"]

        df["imps"] = np.round(1000 * df["spend"] / df["cpm"]).astype(int)
        df["convs"] = np.round(df["imps"] * df["cvr"]).astype(int)
        attr_convs = self.Delay.delay(df["convs"])
        df = df.join(attr_convs, how="outer")
        df["aov"] = AOV.generate(periods + self.Delay.duration - 1)
        df["sales"] = df["attr_convs"] * df["aov"]
        mask = df["spend"] > 0
        df.loc[mask, "roas"] = df.loc[mask, "sales"] / df.loc[mask, "spend"]
        df = df[df["attr_convs"] > 0].copy()
        if plot:
            self.plot(df)
        return df

    def plot(self, df: pd.DataFrame):
        def plot_seasonality(ax):
            mu = df["seasonality"].mean()
            cv = df["seasonality"].std(ddof=1) / mu
            ax.plot(
                df.index,
                df["seasonality"],
                color="dodgerblue",
                lw=2,
                label=f"mu={mu:.0%}, cv={cv:.0%}",
            )

            ax.axhline(mu, color="black", lw=2, ls="--")
            style(
                ax,
                "date",
                "%",
                "Date",
                "Seasonality",
                "Seasonality",
            )

        def plot_elasticity_curve(ax):
            self.Elasticity.plot(ax=ax)

        def plot_conversion_delay(ax):
            self.Delay.plot(ax=ax)

        def plot_outcomes(ax):
            for k, v in {"spend": "orangered", "sales": "dodgerblue"}.items():
                mu = df[k].mean()
                cv = df[k].std(ddof=1) / mu
                ax.scatter(df.index, df[k], alpha=0.3, color=v)
                ax.plot(
                    df[k].rolling(window=7).mean(),
                    color=v,
                    lw=2,
                    label=f"{k}: mu={mu:,.0f}, cv={cv:.0%}",
                )
            style(
                ax,
                x_fmt="date",
                y_fmt="$",
                x_label="Date",
                title="Outcomes",
                legend=True,
            )

        def plot_elasticity(ax):
            ax.plot(
                df.index,
                df["spend_relative_to_baseline"],
                color="orangered",
                lw=2,
                label="Spend Relative to Baseline",
            )
            ax.plot(
                df.index, df["elasticity"], color="limegreen", lw=2, label="Elasticity"
            )
            style(
                ax,
                "date",
                "%",
                "Date",
                "Elasticity",
                "Elasticity",
            )

        def plot_roas(ax):
            ax.scatter(df.index, df["roas"], alpha=0.3, color="limegreen")
            mu = df["sales"].sum() / df["spend"].sum()
            cv = df["roas"].std(ddof=1) / mu
            ax.plot(
                df["roas"].rolling(window=7).mean(),
                color="limegreen",
                lw=2,
                label=f"mu={mu:.0%}, cv={cv:.0%}",
            )
            ax.axhline(df["roas"].mean(), color="black", lw=2, ls="--")
            style(
                ax,
                "date",
                "%",
                "Date",
                "ROAS",
                "ROAS",
            )

        fig, axs = plt.subplots(2, 3, figsize=(16, 9))
        ax = axs.ravel()

        plot_elasticity_curve(ax[0])
        plot_seasonality(ax[1])
        plot_outcomes(ax[2])
        plot_conversion_delay(ax[3])
        plot_elasticity(ax[4])
        plot_roas(ax[5])
        plt.show()
