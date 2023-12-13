# Copyright 2018 Christopher Crew Baker
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import numpy as np
from sklearn.metrics import pairwise_distances


def _get_clust_pairs(clusters):
    return [(i, j) for i in clusters for j in clusters if i > j]


def dunn_score(X, labels=None):
    """
    The Dunn index is an internal clustering validation metric. It evaluates how
    compact and how well separated from each other clusters are.

    :param X: The dataframe that should be clustered in wide or long format
    :type X: pd.DataFrame
    :param labels: the predicted labels/classes by the clustering algorithm
    :type labels: pd.DataFrame

    :returns: the dunn index for the clusters found for a given data set X
    :rtype: float
    """
    dist = pairwise_distances(X)
    clusters = set(labels)
    inter_dists = [
        dist[np.ix_(labels == i, labels == j)].min()
        for i, j in _get_clust_pairs(clusters)
    ]
    intra_dists = [dist[np.ix_(labels == i, labels == i)].max() for i in clusters]
    return min(inter_dists) / max(intra_dists)
