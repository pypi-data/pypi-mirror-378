"""Contains the main class to represent maps with sequences."""

import itertools
import logging
import warnings
from functools import reduce
from operator import and_
from typing import Literal, Optional

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
import spm1d
import tqdm
from scipy import spatial
from sklearn import neighbors

from .data import amino_acids
from .dataframes import CoordDf, SeqDf
from .helper import is_not_amino_acid
from .munging import handle_duplicate_sequences
from .plotting import (
    add_ellipses,
    amino_acid_colors,
    combination_label,
    make_ax_a_map,
    set_ax_limits,
)


class MapSeq(object):
    def __init__(self, seq_df, coord_df, map=None):
        """An antigenic map with sequence data.

        Args:
            seq_df (pd.DataFrame): Indexes are strains. Columns are amino acid
                positions.
            coord_df (pd.DataFrame): Indexes are strains. Columns are "x" and
                "y" coordinates.
            map (int): 2009 or 2017. Optional. Specify a known map to configure
                plotting boundaries.

        Attributes:
            sequence_df (pd.DataFrame): Columns are sites. Rows are strains.
                Cells contain amino acids.
            coord_df (pd.DataFrame): Columns are coordinate dimensions. rows
                are strains. Cells contain numbers.
            strains_with_seq (set): Strains that have a sequence.
            strains_with_coords (set): Strains that have antigenic coordinates.
            strains_with_both (set): Strains that have both antigenic
                coordinates and a sequence.
            strains_with_only_coords (set): Strains that have coordinates, but
                don't have a sequence.
            seq_in_both (pd.DataFrame): Like self.sequence_df, but only for
                strains that have a sequence and coordinates.
            coords_in_both (pd.DataFrame): Like self.coord_df, but only for
                strains that have a sequence and coordinates.
            variant_positions (set): Column names in sequence_df that contain
                more than one unique element.
            map (int): Optional. Integer encoding which antigenic map this is.
        """
        if len(seq_df.index) != len(set(seq_df.index)):
            vc = seq_df.index.value_counts()
            warnings.warn(f"seq_df index contains duplicates:\n{vc[vc > 1]}")

        if len(coord_df.index) != len(set(coord_df.index)):
            vc = coord_df.index.value_counts()
            warnings.warn(f"coord_df index contains duplicates:\n{vc[vc > 1]}")

        self.sequence_df = handle_duplicate_sequences(seq_df)
        self.coord_df = coord_df.copy()
        self.map = map

        # Replace any unknown amino acids with NaN
        cond = self.sequence_df.map(lambda x: x not in amino_acids)
        self.sequence_df.mask(cond, inplace=True)

        # Remove any rows that contain NaN coords
        mask = self.coord_df.notnull().any(axis=1)
        self.coord_df = self.coord_df.loc[mask, :]

        # Strains in the sequences and coordinates dataframes
        self.strains_with_seq = set(self.sequence_df.index)
        self.strains_with_coords = set(self.coord_df.index)

        # Strains in both sequence and coordinate dataframes
        self.strains_with_both = self.strains_with_seq & self.strains_with_coords

        # Strains that only have coordinates
        self.strains_with_only_coords = self.strains_with_coords - self.strains_with_seq

        # Coordinates and sequences of strains in both
        self.seq_in_both = self.sequence_df.loc[sorted(self.strains_with_both), :]
        self.coords_in_both = self.coord_df.loc[sorted(self.strains_with_both), :]

        self.coords_of_strains_without_sequence = self.coord_df.loc[
            sorted(self.strains_with_only_coords)
        ]

    @property
    def variant_positions(self):
        """Positions that have different amino acids."""
        variant_positions = set()
        for p in self.seq_in_both.columns:
            if len(self.seq_in_both.loc[:, p].unique()) != 1:
                variant_positions.add(p)
        return variant_positions

    def plot_with_without(self, ax=None, **kwds):
        """Plot indicating which antigens do and do not have sequences.

        Args:
            ax (matplotlib ax): Optional matplotlib ax.
            **kwds passed to pd.DataFrame.plot.scatter.
        """
        ax = plt.gca() if ax is None else ax
        kwds = dict(ax=ax, x="x", y="y")
        n_without_sequence = self.coords_of_strains_without_sequence.shape[0]
        if n_without_sequence:
            self.coords_of_strains_without_sequence.plot.scatter(
                color="darkgrey",
                label="Without sequence ({})".format(n_without_sequence),
                **kwds,
            )
        n_with_sequence = self.coords_in_both.shape[0]
        if n_with_sequence:
            self.coords_in_both.plot.scatter(
                color="#b72467",
                label="With sequence ({})".format(n_with_sequence),
                **kwds,
            )
        set_ax_limits(map=self.map)
        make_ax_a_map()
        return ax

    def variant_proportions(self, p):
        """Of antigens with sequences, compute the proportion of amino acids
        at each position, p.

        Args:
            p (int): HA position

        Returns:
            pd.Series
        """
        series = self.seq_in_both.loc[:, p]
        value_counts = series.value_counts()
        return (value_counts / value_counts.sum()).sort_values()

    def plot_amino_acids_at_site(
        self,
        p,
        ellipses=True,
        title=True,
        ax=None,
        zorder_behaviour: Literal["random", "default"] = "default",
        **kwds,
    ):
        """Plot map colored by amino acids at site p.

        Args:
            p (int): HA site.
            ellipses (bool): Demark clusters with ellipses.
            title (bool): Add a title to the figure.
            ax (matplotlib ax): Plot figure on this ax.
            zorder_behaviour (str): "random" gives points random sites in z. This is slower because
                marks have to plotted individually.
            **kwds passed to ax.scatter for the colored strains.

        Returns:
            (matplotlib ax)
        """
        ax = ax or plt.gca()

        if kwds.get("zorder") == "random":
            warnings.warn(
                "You probably want zorder_behaviour='random', not zorder='random'"
            )

        if kwds.get("zorder") == "default":
            warnings.warn(
                "You probably want zorder_behaviour='default', not zorder='default'"
            )

        # Antigens without a known sequence
        if not self.coords_of_strains_without_sequence.empty:
            self.coords_of_strains_without_sequence.plot.scatter(
                ax=ax, x="x", y="y", s=5, color="darkgrey", label="Unknown sequence"
            )

        # Antigens with a known sequence
        kwds = dict(
            lw=kwds.pop("lw", 0.5), edgecolor="white", s=kwds.pop("s", 5), **kwds
        )

        proportions = self.variant_proportions(p=p) * 100

        if zorder_behaviour == "default":
            for amino_acid, seq_group in self.seq_in_both.groupby(p):
                coord_group = self.coords_in_both.loc[seq_group.index, :]

                # Get a colour for this amino acid. Get the default color if it's not
                # a known amino acid
                kwds["color"] = amino_acid_colors.get(
                    amino_acid, amino_acid_colors["X"]
                )

                label = f"{amino_acid} {proportions[amino_acid]:.1f}%"

                coord_group.plot.scatter(label=label, x="x", y="y", ax=ax, **kwds)

        elif zorder_behaviour == "random":

            # Can't pass an array of zorders to scatter, so plot all points at the same time, but
            # sort them in random order to achieve a random zorder
            idx = np.argsort(np.random.rand(self.coords_in_both.shape[0]))
            x = self.coords_in_both["x"].values[idx]
            y = self.coords_in_both["y"].values[idx]
            kwds["color"] = np.array(
                [
                    amino_acid_colors.get(amino_acid, amino_acid_colors["X"])
                    for amino_acid in self.seq_in_both[p]
                ]
            )[idx]

            ax.scatter(x=x, y=y, **kwds)

            # Now plot one labeled point for each amino acid for the legend.

            # Remove color from kwds because it is set individually for each point in
            # the loop below
            kwds.pop("color")

            groups = {
                amino_acid: seq_group
                for amino_acid, seq_group in self.seq_in_both.groupby(p)
            }

            amino_acids_sorted_by_proportion = (
                self.seq_in_both.groupby(p).size().sort_values(ascending=False)
            ).index

            for amino_acid in amino_acids_sorted_by_proportion:
                seq_group = groups[amino_acid]
                row = self.coords_in_both.loc[seq_group.index, :].iloc[0, :]
                ax.scatter(
                    x=row["x"],
                    y=row["y"],
                    label=f"{amino_acid} {proportions[amino_acid]:.1f}%",
                    color=amino_acid_colors.get(amino_acid, amino_acid_colors["X"]),
                    **kwds,
                )

        if ellipses and self.map is not None:
            add_ellipses(self.map)

        set_ax_limits(self.map)

        ax.legend()
        if title:
            ax.text(
                x=0.5,
                y=1,
                s=p,
                fontsize=25,
                va="top",
                transform=ax.transAxes,
                ha="center",
            )

        make_ax_a_map(ax)
        return ax

    def plot_single_substitution(
        self,
        sub,
        ellipses=True,
        connecting_lines=True,
        max_cols=4,
        axsize=(4, 4),
        hotellings=True,
        subplots_kwds={},
        **kwds,
    ):
        """Showing strains that differ only by the given substitution.

        Args:
            sub (tuple): Substitution. E.g. ("N", 145, "K")
            ellipses (bool): Demark clusters with ellipses.
            connecting_lines (bool): Plot lines between each points that
                differ by the substitution.
            axsize (tuple): Approximate size for a single ax. (x, y)
            hotellings (bool): Compute Hotelling's T-squared statistic on the
                two samples, and report the results.
            subplots_kwds (dict): Passed to plt.subplots.

            **kwds passed to self.single_substitutions. Use to restrict
                to particular sites.
        """
        # Strains that differ by only the substitution sub
        combinations = self.single_substitutions(sub, **kwds)

        label = "".join(map(str, sub))

        if not combinations:
            raise ValueError("No pairs of strains with {}".format(label))

        # Collect x, y of points to plot, and lines between
        aas = sub[0], sub[2]

        n_combinations = len(combinations)
        if n_combinations <= max_cols:
            nrows = 1
            ncols = n_combinations
        else:
            nrows = (n_combinations // max_cols) + 1
            ncols = max_cols

        fig, _ = plt.subplots(
            nrows=nrows,
            ncols=ncols,
            figsize=(axsize[0] * ncols, axsize[1] * nrows),
            **subplots_kwds,
        )
        axes = iter(fig.axes)

        for i, pairs in enumerate(combinations):

            ax = next(axes)

            # Antigens without a known sequence
            if not self.coords_of_strains_without_sequence.empty:
                self.coords_of_strains_without_sequence.plot.scatter(
                    ax=ax,
                    x="x",
                    y="y",
                    s=5,
                    color="lightgrey",
                    label="Unknown sequence",
                )

            # Antigens with a known sequence
            if not self.coords_in_both.empty:
                self.coords_in_both.plot.scatter(
                    ax=ax, x="x", y="y", s=10, color="darkgrey", label="Known sequence"
                )

            # More transparent lines when there are more points
            alpha = 0.95 ** len(pairs)
            alpha = 0.3 if alpha < 0.3 else alpha

            # Plot strains that have aa0 and aa1
            samples = [None, None]

            for j in range(2):
                strains = set(pair[j] for pair in pairs)
                samples[j] = self.coords_in_both.loc[strains, :]

            # Plot the group with more samples first
            # Prevents over plotting
            if len(samples[1]) > len(samples[0]):
                samples = list(reversed(samples))
                aas = list(reversed(aas))

            for aa, sample in zip(aas, samples):
                sample.plot.scatter(
                    x="x",
                    y="y",
                    s=75,
                    c=amino_acid_colors[aa],
                    edgecolor="white",
                    linewidth=1,
                    zorder=20,
                    ax=ax,
                    label="{}{}".format(aa, sub[1]),
                )

            # Plot both means above the rest of the data
            for aa, sample in zip(aas, samples):
                mean_x, mean_y = sample.mean()
                ax.scatter(
                    mean_x,
                    mean_y,
                    s=150,
                    c=amino_acid_colors[aa],
                    zorder=20,
                    marker="X",
                    lw=1.5,
                    edgecolor="white",
                )

            if hotellings:
                if len(samples[0]) > 1 and len(samples[1]) > 1:
                    h = spm1d.stats.hotellings2(*samples)
                    h_report = "p = {:.2E}\nz = {:.3f}\ndf = {:d}, {:d}".format(
                        h.inference().p, h.z, *list(map(int, h.df))
                    )
                else:
                    h_report = "[Insufficient data]"

                ax.text(
                    x=0,
                    y=1,
                    ha="left",
                    va="top",
                    transform=ax.transAxes,
                    s=r"2 sample Hotelling's T$^2$" + "\n" + h_report,
                )

            if connecting_lines:
                for pair in pairs:
                    # May be multiple strains with the same name that have
                    # different coordinates. Plot lines between all
                    # combinations
                    pair_coords = self.coords_in_both.loc[pair, :]

                    segments = []

                    if pair_coords.shape[0] > 2:
                        # Some strains are repeated in the map
                        # Look for all combinations of groups of strains
                        groups = [
                            group
                            for name, group in pair_coords.groupby(pair_coords.index)
                        ]

                        for idx, series_1 in groups[0].iterrows():
                            for idx, series_2 in groups[1].iterrows():
                                segments.append((series_1.values, series_2.values))

                    elif pair_coords.shape[0] == 2:
                        segments.append(pair_coords.values)

                    else:
                        raise ValueError(
                            "This 'pair' indexes less that 2 "
                            "strains\n{}".format(pair)
                        )

                    ax.add_collection(
                        mpl.collections.LineCollection(
                            segments=segments,
                            lw=1,
                            color="black",
                            alpha=alpha,
                            zorder=10,
                            label="",
                        )
                    )

            if ellipses:
                add_ellipses(self.map)

            make_ax_a_map(ax)
            set_ax_limits(self.map)
            ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))
            title = f"{label} ({i + 1})"
            ax.set_title(title)
            make_ax_a_map(ax)

        # Turn remaining axes off
        for ax in axes:
            ax.set_axis_off()

    def plot_variant_positions_colored_by_amino_acid(self, filename, **kwds):
        """Call plot_amino_acids_at_site for all variant positions

        Args:
            filename (str): A format string with one field to fill in. Each
                position will be substituted in. E.g.:
                "img/melb-h3-2009-coloured-by-pos/{}.png"

            **kwds: Keyword arguments passed to plot_amino_acids_at_site
        """
        # Save text file containing html of the variant positions. 1 sorted by
        # primary structure the second by most common variant
        sorted_primary = sorted(self.variant_positions)
        sorted_most_common = self.variant_positions_sorted_by_most_common_variant()

        img_tag = '<img src="{}" class="map" />\n'

        with open(".by_primary.txt", "w") as fobj:
            for p in sorted_primary:
                fobj.write(img_tag.format(filename.format(p)))

        with open(".by_most_common.txt", "w") as fobj:
            for p in sorted_most_common:
                fobj.write(img_tag.format(filename.format(p)))

        logging.info("Wrote .by_primary.txt and .by_most_common.txt.")
        logging.info(
            "There are {} variant positions.".format(len(self.variant_positions))
        )
        logging.info("Doing:", end=" ")

        for p in self.variant_positions:
            logging.info("{}".format(p), end=" ")

            plt.subplots()
            self.scatter_colored_by_amino_acid(p, **kwds)
            make_ax_a_map()
            plt.tight_layout()
            plt.savefig(filename.format(p), bbox_inches="tight")
            plt.close()

    @property
    def variant_positions_sorted_by_most_common_variant(self):
        """Lookup variant positions.

        Returns:
            tuple. Contains variant positions, sorted by most common variant.
        """
        proportions_all_variants = list(
            map(self.variant_proportions, self.variant_positions)
        )
        proportions_all_variants_sorted = sorted(
            proportions_all_variants, key=lambda x: x[-1]
        )
        return tuple(p.name for p in proportions_all_variants_sorted)

    def strains_with_combinations(self, combinations, without=False):
        """Lookup strains that have combinations of amino acids at particular
        positions.

        Args:
            combinations (dict): Keys are positions, values are amino
                acids:  E.g. {145: "N", 189: "S"}
            without (bool): Lookup strains without the combination.

        Returns:
            pd.DataFrame. Contains strains with the amino acid combinations.
        """
        for k in list(combinations.keys()):
            if k not in self.seq_in_both.columns:
                raise ValueError("Position {} is unknown.")

        masks = (self.seq_in_both.loc[:, k] == v for k, v in combinations.items())

        mask = reduce(and_, masks)

        if without:
            mask = ~mask

        df = self.seq_in_both[mask]

        if df.empty:
            label = "+".join(
                sorted("{}{}".format(k, v) for k, v in combinations.items())
            )

            warnings.warn("No strains with {}".format(label))

        return df

    def duplicate_sequences(self, **kwds):
        """Find groups of duplicate sequences.

        Any element in self.seq_in_both that is not one of the standard 20
        1-letter amino acid abbreviations is ignored. (It is treated as NaN,
        see: http://pandas.pydata.org/pandas-docs/stable/
        missing_data.html#na-values-in-groupby)

        Args:
            positions (iterable of ints). Optional. Lookup groups of sequences
                identical at these positions. Default is all positions.

        Returns:
            pd.GroupBy
        """
        positions = kwds.pop("positions", self.seq_in_both.columns.tolist())
        df = self.seq_in_both
        return df.mask(df.map(is_not_amino_acid)).groupby(positions)

    def plot_strains_with_combinations(
        self, combinations, without=False, plot_other=True, ax=None, **kwds
    ):
        """Plot a map highlighting strains with combinations of amino acids
        at particular positions.

        Args:
            combinations (dict): Keys are positions, values are amino
                acids:  E.g. {145: "N", 189: "S"}.
            without (bool): Plot strains without the combination.
            plot_other (bool): Plot other antigens (those without the
                combinations).
            ax (matplotlib ax): Optional.
            **kwds passed to the plt.scatter.

        Returns:
            (matplotlib ax)
        """
        ax = plt.gca() if ax is None else ax
        df = self.strains_with_combinations(combinations, without=without)

        label = "+".join(sorted("{}{}".format(k, v) for k, v in combinations.items()))
        label = "Without {}".format(label) if without else label

        if df.empty:
            raise ValueError("No strains with {}".format(label))

        else:
            strains = df.index

            if plot_other:
                other = set(self.coord_df.index) - set(strains)
                self.coord_df.loc[list(other), :].plot.scatter(
                    x="x", y="y", s=10, color="darkgrey", ax=ax
                )

            ax.scatter(
                self.coord_df.loc[strains, "x"],
                self.coord_df.loc[strains, "y"],
                label=label,
                **kwds,
            )
            ax.legend()

            if self.map:
                add_ellipses(self.map)
                set_ax_limits(self.map)

            make_ax_a_map(ax)
            return ax

    def plot_strains_with_combinations_kde(
        self,
        combinations,
        c=0.9,
        color="black",
        ax=None,
        label=False,
        clabel_kwds=dict(),
        **kwds,
    ):
        """Plot a contour that contains c percent of the density of a KDE of
        strains with combinations of AAPs specified in combinations.

        Args:
            combinations (dict): Dictionary specifying combinations. E.g.:
                {145: "N", 133: "D"}
            c (number): Range 0-1. The contour contains c percent of the KDE
                density.
            color (matplotlib colour): Colour to plot the contour line
            ax (matplotlib ax): Optional.
            label (bool): Label the contour.
            clabel_kwds (dict): Optional kwds for ax.clabel if label is True.
            **kwds passed to plt.contour.

        Returns:
            (matplotlib ax)
        """
        ax = plt.gca() if ax is None else ax
        df = self.strains_with_combinations(combinations)
        strains = df.index

        dataset = self.coord_df.loc[strains, :]

        grid = sklearn.model_selection.GridSearchCV(
            estimator=neighbors.KernelDensity(kernel="gaussian"),
            param_grid=dict(bandwidth=np.linspace(0.01, 2, 20)),
            cv=3,
        )

        kde = grid.fit(dataset).best_estimator_

        xmin, ymin = dataset.min() - 2
        xmax, ymax = dataset.max() + 2

        xnum = (xmax - xmin) * 5
        ynum = (ymax - ymin) * 5

        Xgrid, Ygrid = np.meshgrid(
            np.linspace(xmin, xmax, num=xnum), np.linspace(ymin, ymax, num=ynum)
        )

        Z = np.exp(kde.score_samples(np.vstack([Xgrid.ravel(), Ygrid.ravel()]).T))

        zsort = np.sort(Z)[::-1]
        dens = zsort[np.argmax(np.cumsum(zsort) > Z.sum() * c)]

        contour_set = ax.contour(
            Xgrid,
            Ygrid,
            Z.reshape(Xgrid.shape),
            levels=[dens],
            colors=color,
            **kwds,
        )

        if label:
            # fmt arg of clabel can be dict mapping level value to str
            fmt = {contour_set.levels[0]: combination_label(combinations)}
            ax.clabel(
                contour_set, fmt=fmt, inline=True, use_clabeltext=True, **clabel_kwds
            )

        make_ax_a_map(ax)

        return ax

    def differ_by_n(self, n):
        """Lookup pairs of strains that differ by n positions.

        Args:
            n (int)

        Returns:
            set containing 2-tuples
        """
        keep = set()
        for a, b in itertools.combinations(self.seq_in_both.index, 2):
            df = self.seq_in_both
            if (df.loc[a, :] != df.loc[b, :]).sum() == n:
                keep.add((a, b))
        return keep

    def single_substitutions_one_random_aa(self, p, aa):
        """Find pairs of strains that differ only at position p, and where one
        has the amino acid aa at that position.

        Args:
            p (int): Position
            aa (str): Amino acid. Must be in amino_acids.

        Returns:
            list of pd.Series containing the amino acids
                and corresponding strain names.
        """
        keep = list()
        differ_by_1 = self.differ_by_n(1)
        for pair in differ_by_1:
            aas = self.seq_in_both.loc[pair, p]
            different = aas.unique().shape[0] > 1
            aa_present = (aa == aas).sum()
            nan_absent = aas.isnull().sum() < 1
            if different and aa_present and nan_absent:
                keep.append(aas)
        return keep

    def single_substitutions(
        self, sub: tuple[str, int, str], exclude: Optional[list] = None
    ) -> set[tuple[tuple[str, str], ...]]:
        """Find pairs of strains that differ by only the substitution 'sub'.

        Args:
            sub (tuple): ("N", 145, "K") like. First and last elements are
                strings referring to amino acids. Middle element is int.
            exclude (list). Optional. Don't consider positions in this list when looking for
            identical sequences.

        Returns:
            (set): Set containing tuples of 2-tuples.
        """
        aa0, pos, aa1 = sub
        assert aa0 in amino_acids
        assert aa1 in amino_acids
        assert pos in self.seq_in_both.columns

        # Drop unwanted positions
        df = (
            self.seq_in_both.drop(exclude, axis=1)
            if exclude is not None
            else self.seq_in_both
        )

        # Drop the position of the substitution.
        # (Going to groupby columns not including this site, and then look for strains that have
        # the aa0 / aa1 of interest in the groups.)
        if pos in df.columns:
            df = df.drop(pos, axis=1)

        # Groupby all columns to get groups with the same sequence
        grouped = df.groupby(df.columns.tolist())

        # In each group find all combinations of sequences that differ by
        # aa0-aa1 at pos
        pairs = set()

        for _, group in grouped:

            # Only consider groups that contain more than one sequence
            if len(group) < 2:
                continue

            # Lookup amino acid for the group at pos
            group_pos = self.seq_in_both.loc[group.index, pos]

            # These sequences have aa0 / aa1 at pos
            strains_with_pos_aa0 = group_pos[group_pos == aa0].index
            strains_with_pos_aa1 = group_pos[group_pos == aa1].index

            if strains_with_pos_aa0.any() and strains_with_pos_aa1.any():
                pairs.add(
                    tuple(itertools.product(strains_with_pos_aa0, strains_with_pos_aa1))
                )

        return pairs

    def identical_sequences(self, positions=None):
        """Lookup strains with identical sequences.

        Args:
            positions (list containing ints). Only consider these positions.
                The default, None, considers all positions.

        Returns:
            (pd.DataFrame) containing the identical sequences.
        """
        identical = []
        if positions is None:
            positions = self.seq_in_both.columns.tolist()
        groupby = self.seq_in_both.groupby(positions)
        for _, strains in groupby.groups.items():
            if len(strains) > 1:
                identical.append(strains)
        return identical

    def error(self, positions=None):
        """
        Assuming in a perfect system (sequencing, laboratory, cartography)
        genetically identical strains should be in an identical position in the
        map. This method returns the distribution of pairwise distances between
        genetically identical strains.

        Some groups of genetically identical strains are larger than others.
        E.g. some groups can have ~30 strains, whilst lots of others have 2-5.
        This methods computes the mean and median pairwise distance for each
        group, so that one group does not dominate the distribution.

        (There are (30^2-30)/2 = 435 pairwise distances between 30 points,
        compared to (5^2-5)/2 = 10 for 10 points).

        Args:
            positions (list containing ints) Only consider these positions when
                looking for genetically identical strains. Default, None, uses
                all positions.

        Returns:
            (dict) containing mean and median distances.
        """
        identical_sequences = self.identical_sequences(positions=positions)
        n = len(identical_sequences)
        means, medians = np.empty(n), np.empty(n)
        for i, names in enumerate(identical_sequences):
            # Each i is a list containing the indexes of identical sequences
            coords = self.coords_in_both.loc[names, :].values
            distances = spatial.distance.pdist(X=coords, metric="euclidean", p=2)
            means[i] = np.mean(distances)
            medians[i] = np.median(distances)
        return {"means": means, "medians": medians}

    def plot_error(self, positions=None):
        """Plot the distribution of means and median pairwise antigenic
        distances between genetically strains, calculated by self.error()

        Args:
            positions (list of ints). Only consider these positions when
                looking for genetically identical strains. Default, None, uses
                all positions.

        Returns:
            (matplotlib ax)
        """
        error = self.error(positions=positions)
        max_error = max(list(map(max, list(error.values()))))
        step = 0.5
        bins = np.arange(0, np.ceil(max_error) + step, step)

        _, ax = plt.subplots(
            nrows=2, ncols=1, figsize=(7, 10), sharex=True, sharey=True
        )

        ax[0].hist(error["means"], bins=bins, ec="white")
        ax[0].set_title("Means")
        ax[0].set_ylabel("Frequency")

        ax[1].hist(error["medians"], bins=bins, ec="white")
        ax[1].set_title("Medians")
        ax[1].set_ylabel("Frequency")

        ax[1].set_xlabel("Antigenic distance (AU)")

        return ax

    def find_single_substitutions(self, cluster_diff_df, filename=None, **kwds):
        """
        Find strains that differ by one substitution out of the combinations
        defined in cluster_combinations

        Args:
            cluster_diff_df (pd.DataFrame): Specifies cluster difference
                substitutions. E.g.:

                        ==== ==== ====
                        Site CA04 FU02
                        ==== ==== ====
                        145  N    K
                        159  F    Y
                        189  N    S
                        226  I    V
                        227  P    S
                        ==== ==== ====

            filename (str or None): If not None, save a plot with filename.
                Should be a format string with room to substitute in a label
                describing the substitutions found.

            **kwds passed to plot_strains_with_combinations.
        """
        clusters = cluster_diff_df.columns
        positions = cluster_diff_df.index

        for c0, c1 in itertools.permutations(clusters, 2):
            for p in positions:
                # Base combinations on c0
                combinations = cluster_diff_df.loc[:, c0].to_dict()

                # Alter position p to be c1-like
                combinations[p] = cluster_diff_df.loc[p, c1]

                # Find strains that have this combination of amino acids
                # and plot them
                if self.plot_strains_with_combinations(combinations, **kwds):
                    # The c1 amino acid
                    label = "{}-like_{}{}".format(c1, str(p), combinations[p])

                    # The c0 amino acids
                    combinations.pop(p, None)
                    c0_aas = combination_label(combinations)
                    label += ",_{}-like_{}".format(c0, c0_aas)

                    plt.title(label.replace("_", " "))
                    plt.tight_layout()
                    plt.savefig(filename.format(label).replace(",", "_"))
                    plt.close()

        # Finally, plot the viruses with the full combinations of each cluster
        for c in clusters:
            combinations = cluster_diff_df.loc[:, c].to_dict()
            aas = combination_label(combinations)
            if self.plot_strains_with_combinations(combinations, **kwds):
                label = "{}-like_{}".format(c, aas)
                plt.title(label.replace("_", " "))
                plt.tight_layout()
                plt.savefig(filename.format(label))
                plt.close()

    def plot(self, ax=None, **kwds):
        """Plot the map.

        Args:
            ax (matplotlib ax): Optional.
            **kwds passed to ax.scatter

        Returns:
            (matplotlib ax)
        """
        ax = plt.gca() if ax is None else ax
        x = self.coord_df.iloc[:, 0]
        y = self.coord_df.iloc[:, 1]
        ax.scatter(x, y, **kwds)
        make_ax_a_map(ax)
        return ax

    def find_double_substitutions(self, cluster_diff_df, filename=None, **kwds):
        """Find strains that differ by two substitutions out of the
        combinations defined in cluster_combinations.

        Args:
            cluster_diff_df (pd.DataFrame): Contains cluster difference
                substitutions. E.g.:

                        ==== ==== ====
                        Site CA04 FU02
                        ==== ==== ====
                        145  N    K
                        159  F    Y
                        189  N    S
                        226  I    V
                        ==== ==== ====

            filename (str or None): If not None, save a plot with filename.
                Should be a format string with room to substitute in a label
                describing the substitutions found.
            **kwds passed to plot_strains_with_combinations.
        """
        clusters = cluster_diff_df.columns
        positions = cluster_diff_df.index

        for c0, c1 in itertools.permutations(clusters, 2):
            for p0, p1 in itertools.combinations(positions, 2):
                # Base combinations on c0
                combinations = cluster_diff_df.loc[:, c0].to_dict()

                # Alter positions to be c1-like
                for p in p0, p1:
                    combinations[p] = cluster_diff_df.loc[p, c1]

                # Find strains that have this combination of amino acids
                # and plot them
                if self.plot_strains_with_combinations(combinations, **kwds):
                    # Label
                    subs = "+".join(
                        sorted("{}{}".format(str(p), combinations[p]) for p in (p0, p1))
                    )
                    label = "Double_{}-like_{}".format(c1, subs)
                    plt.title(label.replace("_", " "))
                    plt.tight_layout()
                    plt.savefig(filename.format(label))
                    plt.close()


class OrderedMapSeq(MapSeq):
    def __init__(self, seq_df, coord_df):
        """Like MapSeq, but the order of the indexes of the dataframes
        containing the coordinates and sequences are identical.

        Notes:
            Positions with no amino acid diversity are removed.

        Args:
            seq_df (pd.DataFrame): Indexes are strains. Columns are amino acid
                positions.
            coord_df (pd.DataFrame): Indexes are strains. Columns are "x" and
                "y" coordinates.

        Attributes:
            coord (mapdeduce.dataframes.CoordDf): Contains coordinates.
            seq (mapdeduce.dataframes.SeqDf): Contains sequences.
        """
        super().__init__(seq_df, coord_df)

        # Join the two dataframes, so they share indexes
        if shared := set(self.coords_in_both) & set(self.seq_in_both):
            raise ValueError(f"seq_df and coord_df share column names: {shared}")
        else:
            combined = self.coords_in_both.join(self.seq_in_both)

        # Remove strains that have any NaN entries
        mask = combined.notnull().any(axis=1)
        n_with_nan = (~mask).sum()
        if n_with_nan:
            tqdm.write("Removed {} strains with NaN values".format(n_with_nan))
            combined = combined[mask]

        phenotypes = self.coords_in_both.columns

        self.coord = CoordDf(combined.loc[:, phenotypes])
        self.seqs = SeqDf(combined.drop(phenotypes, axis=1))

    @classmethod
    def from_dataframe(
        cls,
        df: pd.DataFrame,
        map_coords: list[str],
        sequence: str,
        sites: Optional[tuple[int]] = None,
    ) -> "OrderedMapSeq":
        """
        Instantiate directly from a single DataFrame that has columns containing sequences and map
        coordinates.

        Args:
            df: DataFrame.
            map_coords: List containing column names of map sequences.
            sequence: Name of column containing sequences.
            sites: 2-tuple containing first and last sequence position to include (1-indexed). By
                default include all sequence positions.
        """
        coord_df = df[map_coords].copy()
        seq_df = df[sequence].str.split("", expand=True)

        if sites is not None:

            try:
                start, end = sites
            except ValueError:
                raise ValueError("sites should contain 2 ints")

            seq_df = seq_df.loc[:, list(range(start, end + 1))].copy()

        return cls(seq_df=seq_df, coord_df=coord_df)

    def filter(
        self,
        patch=None,
        plot=True,
        remove_invariant=True,
        get_dummies=True,
        merge_duplicate_dummies=False,
        rename_idx=False,
    ) -> "OrderedMapSeq":
        """Remove data where the x y coordinates are outside a matplotlib
        patch.

        Notes:
            Updates self.coord and self.seq inplace.

        Args:
            patch (matplotlib.patches.Patch): Remove strains not contained
                in patch.
            plot (bool): Show points that have been included / excluded
                and the patch. (Only if a patch is specified).
            remove_invariant (bool): Remove sequence positions that only
                contain a single amino acid.
            get_dummies (bool): Attach dummy variable representation of the
                sequences.
            merge_duplicate_dummies (bool): Merge dummy variables that have
                the same profile (identical for all strains).
            rename_idx (bool): Rename strains in the format strain-X where X
                is an integer. This is necessary for merging duplicate dummies
                if there are duplicate strain names (which can occur if a
                strain was titrated multiple times). Attaches a strain_names
                attribute to self which is a dict containing the new name to
                old name mapping.

        Returns:
            (matplotlib ax)
        """
        # Strain removal operations first
        if patch is not None:
            if plot:
                ax = self.coord.df.plot.scatter(
                    x="x", y="y", label="All points", c="black", s=5
                )

            mask = self.coord.points_in_patch(patch=patch)

            self.coord.df = self.coord.df[mask]
            self.seqs.df = self.seqs.df[mask]

        if remove_invariant:
            self.seqs = self.seqs.remove_invariant()

        if rename_idx:
            old_idx = self.coord.df.index
            new_idx = ["strain-{}".format(i) for i in range(old_idx.shape[0])]
            self.strain_names = dict(list(zip(new_idx, old_idx)))
            self.coord.df.index = new_idx
            self.seqs.df.index = new_idx

        if get_dummies:
            self.seqs.get_dummies()

        if merge_duplicate_dummies:
            self.seqs.merge_duplicate_dummies()

        if plot and patch is not None:
            self.coord.df.plot.scatter(x="x", y="y", label="Included", ax=ax)
            make_ax_a_map(ax)
            return ax

        return self
