import numpy as np
from sklearn.metrics import pairwise_distances


# courtesy from validclust package
def _get_clust_pairs(clusters):
    return [(i, j) for i in clusters for j in clusters if i > j]


def dunn_score(X, labels=None):
    dist = pairwise_distances(X)
    clusters = set(labels)
    inter_dists = [
        dist[np.ix_(labels == i, labels == j)].min()
        for i, j in _get_clust_pairs(clusters)
    ]
    intra_dists = [dist[np.ix_(labels == i, labels == i)].max() for i in clusters]
    return min(inter_dists) / max(intra_dists)
