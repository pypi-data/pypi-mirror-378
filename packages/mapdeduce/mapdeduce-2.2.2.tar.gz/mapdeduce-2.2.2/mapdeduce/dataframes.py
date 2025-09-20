"""Classes for handling DataFrames containing coordinates and sequences."""

from collections import defaultdict
from itertools import combinations
import logging

from scipy.spatial.distance import euclidean
from sklearn.decomposition import PCA
from sklearn.preprocessing import quantile_transform
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn

from .helper import expand_sequences, site_consensus
from .munging import df_from_fasta


class CoordDf:

    def __init__(self, df):
        """Coordinate data.

        Args:
            df (pd.DataFrame): Must contain x and y columns.
        """
        self.df = df

    def __repr__(self):
        return "CoordDf with {} samples and {} dimensions:\n{}".format(
            *self.df.shape, repr(self.df)
        )

    def rotate(self, a, inplace=True):
        """Rotate points a degrees around the origin anticlockwise.

        Args:
            a (Number): Arc degrees to rotate the dataframe by.
            inplace (bool): Rotate the data inplace, or return a rotated
                copy of the data.
        """
        theta = np.radians(a)
        c, s = np.cos(theta), np.sin(theta)
        R = np.array(((c, -s), (s, c)))
        arr = np.matmul(self.df, R)
        df = pd.DataFrame(arr, index=self.df.index, columns=self.df.columns)

        if inplace:
            self.df = df
        else:
            return CoordDf(df=df)

    def points_in_patch(self, patch):
        """Points in sel.df contained in a matplotlib patch.

        Args:
            patch (matplotlib.patches.Patch)

        Returns:
            Strains in patch.
        """
        _, ax = plt.subplots()
        self.df.plot.scatter(x="x", y="y", ax=ax)
        ax.add_artist(patch)
        path = patch.get_transform().transform_path(patch.get_path())
        mask = path.contains_points(ax.transData.transform(self.df))
        plt.close()
        return mask

    def pca_rotate(self, inplace=True, keep_dim_names=False):
        """Rotate coordinates along first and second principal components.

        Args:
            inplace (bool): Rotate the data inplace, or return a rotated
                copy of the data.
            keep_colnames (bool): Keep the existing names of the columns. Otherwise replaced by
                "PC1", "PC2" etc...
        """
        n_components = self.df.shape[1]

        df_rotated = pd.DataFrame(
            PCA(n_components=n_components).fit(self.df).transform(self.df),
            index=self.df.index,
            columns=(
                self.df.columns
                if keep_dim_names
                else [f"PC{i}" for i in range(1, n_components + 1)]
            ),
        )

        if inplace:
            self.df = df_rotated
        else:
            return CoordDf(df=df_rotated)

    def quantile_transform(self, inplace=True):
        """Transform features using quantile information.

        Notes:
            http://scikit-learn.org/stable/modules/generated/
            sklearn.preprocessing.quantile_transform.html#sklearn.
                preprocessing.quantile_transform

        Args:
            inplace (bool)
        """
        arr = quantile_transform(self.df, output_distribution="normal")
        df = pd.DataFrame(arr, index=self.df.index, columns=self.df.columns)

        if inplace:
            self.df = df
        else:
            return CoordDf(df=df)

    def paired_distances(self, other):
        """Compute euclidean distances between points in self.df and paired
        points in another dataframe. The other dataframe must have the same
        dimensions as self.df

        Args:
            other (pd.DataFrame)

        Returns:
            (ndarray): Euclidean distances.
        """
        if self.df.index.shape != other.index.shape:
            raise ValueError("Index lengths mismatched.")

        if self.df.columns.shape != other.columns.shape:
            raise ValueError("Column lengths mismatched.")

        n = self.df.shape[0]

        distances = np.empty(n)

        for i in range(n):
            try:
                distances[i] = euclidean(u=self.df.iloc[i, :], v=other.iloc[i, :])

            except ValueError:
                distances[i] = np.nan

        return distances


class SeqDf:

    def __init__(self, df):
        """DataFrames containing amino acid sequences.

        Args:
            df (pd.DataFrame): Columns are amino acid positions, rows are
                samples, cells contain amino acids.
        """
        self.df = df.copy()

    def __repr__(self):
        return "SeqDf with {} samples and {} sites\n{}:".format(
            *self.df.shape, repr(self.df)
        )

    def __str__(self):
        return str(self.df)

    @classmethod
    def from_fasta(cls, path):
        """Make a SeqDf from a fasta file.

        Args:
            path (str): Path to fasta file.

        Returns:
            (SeqDf)
        """
        return cls(df_from_fasta(path=path, positions="infer"))

    @classmethod
    def from_series(cls, series):
        """Make SeqDf from a series.

        Args:
            series (pd.Series): Each element in series is a string. See
                mapdeduce.helper.expand_sequences for more details.

        Returns:
            (SeqDf)
        """
        return cls(expand_sequences(series))

    def remove_invariant(self) -> "SeqDf":
        """Remove positions (columns) that contain only one amino acid."""
        mask = self.df.apply(lambda x: pd.unique(x).shape[0] > 1)
        logging.info(f"Removed {(~mask).sum()} invariant sequence positions")
        return SeqDf(self.df.loc[:, self.df.columns[mask]])

    def get_dummies(self) -> None:
        """Get dummy representation of the sequences.

        Attaches a `dummies` attribute.
        """
        self.dummies = pd.get_dummies(self.df, prefix_sep="").astype(float)

    def shuffle_dummies(self, n_shuffles, c):
        """Return a DataFrame containing n shuffles of the data in column c

        Args:
            n_shuffles (int): Number of shuffles.
            c (str): Must be column in self.dummies.

        Returns:
            (ndarray): Shape [N, n_shuffles].
        """
        values = self.dummies.loc[:, c].values
        arr = np.empty((values.shape[0], n_shuffles))
        for i in range(n_shuffles):
            arr[:, i] = sklearn.utils.shuffle(values)
        return arr

    def get_dummies_at_positions(self, positions):
        """Return set of dummy variable names at HA positions.

        Notes:
            Dummy variable names are either singles (e.g. 135K), or compound
            (e.g. 7D|135K|265E). For compound dummy variable names return the
            entire compound name if any constituent AAP is in positions.

        Args:
            positions (iterable) containing positions.

        Returns:
            (set) containing dummy variable names.
        """
        dummies = set()
        add = dummies.add

        for dummy in self.dummies.columns:
            for c in dummy.split("|"):
                pos = int(c[:-1])

                if pos in positions:
                    add(dummy)
                    break

        return dummies

    def merge_duplicate_dummies(self):
        """
        Merge AAPs that are identical in all strains, then remove any AAPs that are exactly
        inverses of any other AAP. Updates the `dummies` attribute.
        """
        grouped = self.dummies.T.groupby(by=self.dummies.index.tolist())
        dummies = pd.DataFrame(
            data={"|".join(g.index): n for n, g in grouped}, index=self.dummies.index
        )
        self.dummies, self.inverse_dummies = remove_inverse_profiles(dummies)

    def consensus(self):
        """Compute the consensus sequence.

        Returns:
            (pd.Series)
        """
        return self.df.apply(site_consensus, axis=0)

    def merge_duplicate_strains(self, inplace=False):
        """Replace all strains that have the same index with a single
        consensus strain.

        Args:
            inplace (bool).

        Returns:
            (mapdeduce.dataframes.SeqDf) if inplace=False.
        """
        vc = self.df.index.value_counts()
        dupes = (vc[vc > 1]).index
        data = {d: SeqDf(self.df.loc[d]).consensus() for d in dupes}
        cons = pd.DataFrame.from_dict(data, orient="index")
        df = pd.concat([self.df.drop(dupes, axis=0), cons])

        if inplace:
            self.df = df
        else:
            return SeqDf(df)

    def to_fasta(self, path):
        """Write the sequences in fasta format.

        Args:
            path (str): Path to write file.
        """
        if not path.lower().endswith(".fasta"):
            path += ".fasta"
        with open(path, "w") as handle:
            for row in self.df.iterrows():
                handle.write(">{}\n".format(row.name))
                handle.write("{}\n".format("".join(row)))

    def groupby_amino_acid_at_site(self, p):
        """Lookup groups of strains that have the same amino acid at site p.

        Args:
            p (int): Site. Must be a column in self.df.

        Returns:
            (dict): Maps amino acid -> set containing strain names.
        """
        if p not in self.df.columns:
            raise ValueError("{} not in self.df.columns".format(p))
        return {
            amino_acid: set(group.index)
            for amino_acid, group in self.df.groupby(self.df.loc[:, p])
        }

    def substitutions_at_site(self, p, min_strains=0):
        """Find substitutions that occur at site p.

        Args:
            p (int). Must be in self.df.
            min_strains (int). Minimum number of strains that must posses a
                given amino acid to be included. Default=0 to include all
                strains.

        Returns:
            (dict): Maps substitution -> pd.Series containing profile of
                substitution. Strains with 0 have the aa0. Strains with 1 have
                the aa1.
        """
        groups = self.groupby_amino_acid_at_site(p)
        rv = {}
        for aa0, aa1 in combinations(groups, 2):
            aa0, aa1 = sorted((aa0, aa1))
            if len(groups[aa0]) < min_strains:
                continue
            elif len(groups[aa1]) < min_strains:
                continue
            else:
                data = [0.0] * len(groups[aa0]) + [1.0] * len(groups[aa1])
                index = list(groups[aa0]) + list(groups[aa1])
                series = pd.Series(data=data, index=index)
                series.name = "{}{}{}".format(aa0, str(p), aa1)
                rv[str(series.name)] = series
        return rv


def remove_inverse_profiles(dummies: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    AAPs might have profiles: 000111 and 111000.

    The same information is encoded in both cases, just with different uses of 0/1. Importantly the
    effect sizes of two AAPs with these profiles would be the same, but one multiplied by a factor
    of -1 relative to the other.

    This function searches for situations like this in a DataFrame containing AAP profiles (or
    'dummies'), and returns a DataFrame with the inverse profiles removed. It also returns a
    dictionary where keys are dummies in the returned DataFrame and values are lists of dummy names
    that were inverses of the key.
    """
    # Store unique profiles
    seen = {}

    # This dictionary keeps track of which dummies are the inverse of another dummy
    inverse_dummies = defaultdict(list)

    # Iterate over each dummy variable, testing if any profiles already seen are exactly equal
    # to one minus the profile (i.e. the 'inverse')
    for dummy in dummies:

        profile = dummies[dummy].values
        inverse = 1 - profile

        # Check if this inverse profile has been seen before
        for seen_dummy, seen_value in seen.items():
            if all(inverse == seen_value):
                inverse_dummies[seen_dummy].append(dummy)
                break
        else:
            seen[dummy] = profile

    return pd.DataFrame(seen), inverse_dummies
