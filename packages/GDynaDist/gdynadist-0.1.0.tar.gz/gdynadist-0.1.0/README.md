# G-DynaDist

### Dall'Amico, Cattuto, Belliardo - *An embedding-based distance for temporal graphs*

| **[Documentation]()** 
| **[Paper](https://www.nature.com/articles/s41467-024-54280-4)** | 

```bash
pip install 
```


## Summary

These codes implement our definition of distance between temporal graphs as defined in [Dall'Amico, Cattuto, Barrat *An embedding-based distance for temporal graphs*](https://www.nature.com/articles/s41467-024-54280-4). We consider the problem of comparing pairs of temporal graphs, *i.e* relational datasets in which the interaction between node pairs $i, j$ are time-stamped.

We define two metrics for `matched` and `unmatched` graphs, respectively. We say two graphs are *matched* if there exists a known bijective relationship between the nodes of the two graphs and they *unmatched* otherwise. Matched graphs have the same number of nodes and represent different instances of the same graph, while unmatched graphs may have a different number of nodes.

To compute the distance, we first obtain a node embedding of the temporal graphs, and then we compute the distances in the embedded space. The embedding is obtained using the [EDRep](https://github.com/lorenzodallamico/EDRep) Python package. The figure below summarizes the pipeline adopted to compute the distance.

![](Fig/pipeline.png)

## V2 release

In this release we improved the user interface (but left the core code untouched) and we introduced a new [documentation]() to ease the use of our package. We invite the user to check it out to find several examples and comments on how to eeasily compute temporal graph distances using our package.

## V1 release
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.13880695.svg)](https://doi.org/10.5281/zenodo.13880695)

This is the original release of the article, which correasponds to the DOI indicated above. These codes can be used to reproduce the results of the paper. We remark that, while the distance function is called in a different way, the core definition is unchanged from V1 to V2.

> ℹ️ **Note:** In the V1 version, we used greek letters $\tau$ and $\eta$ to indicate the edge weight and the learning rate, respectively. In the V2 version, these have been turned into `tau` and `eta`. Especially the use of `eta` instead of $\eta$ can cause problems when calling the `EDRep` package, but that is easily fixed by applying by hand the modification just described to the parameters names.


## Citation

If you make use of these codes, please reference the following articles

```
@article{dallamico2024embeddingbased,
   title={An embedding-based distance for temporal graphs},
   volume={15},
   ISSN={2041-1723},
   url={http://dx.doi.org/10.1038/s41467-024-54280-4},
   DOI={10.1038/s41467-024-54280-4},
   number={1},
   journal={Nature Communications},
   publisher={Springer Science and Business Media LLC},
   author={Dall’Amico, Lorenzo and Barrat, Alain and Cattuto, Ciro},
   year={2024},
   month=nov }
```

```
@article{
dallamico2025learning,
title={Learning distributed representations with efficient SoftMax normalization},
author={Lorenzo Dall'Amico and Enrico Maria Belliardo},
journal={Transactions on Machine Learning Research},
issn={2835-8856},
year={2025},
url={https://openreview.net/forum?id=9M4NKMZOPu},
note={}
}
```
    
## Author

[Lorenzo Dall'Amico](https://lorenzodallamico.github.io/) - lorenzo.dallamico@isi.it

## Licence

This software is released under the GNU AFFERO GENERAL PUBLIC LICENSE (see included file LICENSE)
