# Repository Coverage



| Name                                                             |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|----------------------------------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| \_\_init\_\_.py                                                  |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/\_\_init\_\_.py                                        |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/constants/\_\_init\_\_.py                              |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/constants/colors.py                                    |        2 |        0 |        0 |        0 |    100% |           |
| protzilla/constants/location\_mapping.py                         |        8 |        0 |        4 |        1 |     92% |  17->exit |
| protzilla/constants/logging.py                                   |        3 |        0 |        0 |        0 |    100% |           |
| protzilla/constants/paths.py                                     |        6 |        0 |        0 |        0 |    100% |           |
| protzilla/data\_analysis/differential\_expression.py             |        5 |        2 |        0 |        0 |     60% |       8-9 |
| protzilla/data\_analysis/differential\_expression\_anova.py      |       22 |        0 |        6 |        1 |     96% |    82->85 |
| protzilla/data\_analysis/differential\_expression\_helper.py     |        7 |        1 |        2 |        1 |     78% |        22 |
| protzilla/data\_analysis/differential\_expression\_t\_test.py    |       40 |        0 |       10 |        0 |    100% |           |
| protzilla/data\_preprocessing/\_\_init\_\_.py                    |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/data\_preprocessing/filter\_proteins.py                |       15 |        2 |        4 |        1 |     74% |     55-56 |
| protzilla/data\_preprocessing/filter\_samples.py                 |       26 |        1 |        4 |        2 |     90% |56->65, 66 |
| protzilla/data\_preprocessing/imputation.py                      |       74 |        1 |       14 |        3 |     95% |140, 290->299, 309->315 |
| protzilla/data\_preprocessing/normalisation.py                   |       99 |        1 |       22 |        2 |     98% |243->254, 255 |
| protzilla/data\_preprocessing/outlier\_detection.py              |       67 |        3 |       12 |        4 |     89% |172, 189, 244, 245->exit |
| protzilla/data\_preprocessing/plots.py                           |       71 |        7 |        9 |        1 |     90% |176->191, 368-392 |
| protzilla/data\_preprocessing/transformation.py                  |       20 |        2 |        8 |        3 |     82% |31, 40->49, 50 |
| protzilla/history.py                                             |      119 |        6 |       46 |        6 |     93% |33, 109, 116, 124, 189, 203 |
| protzilla/importing/metadata\_import.py                          |       27 |        7 |       12 |        1 |     64% |     19-26 |
| protzilla/importing/ms\_data\_import.py                          |       16 |        0 |        2 |        0 |    100% |           |
| protzilla/run.py                                                 |      175 |       38 |       50 |        7 |     74% |36-42, 46-52, 58, 83->82, 85, 114-115, 126-127, 134-135, 145, 149, 157->155, 168-175, 178-182, 219-222, 234-235 |
| protzilla/utilities/\_\_init\_\_.py                              |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/utilities/random.py                                    |        4 |        0 |        0 |        0 |    100% |           |
| protzilla/utilities/transform\_dfs.py                            |       11 |        0 |        0 |        0 |    100% |           |
| protzilla/workflow\_helper.py                                    |       33 |        0 |       30 |        1 |     98% |    20->19 |
| tests/\_\_init\_\_.py                                            |        0 |        0 |        0 |        0 |    100% |           |
| tests/conftest.py                                                |        6 |        0 |        0 |        0 |    100% |           |
| tests/protzilla/\_\_init\_\_.py                                  |        0 |        0 |        0 |        0 |    100% |           |
| tests/protzilla/data\_analysis/test\_differential\_expression.py |       63 |        0 |       10 |        0 |    100% |           |
| tests/protzilla/data\_preprocessing/test\_filter\_proteins.py    |       16 |        1 |        2 |        1 |     89% |        48 |
| tests/protzilla/data\_preprocessing/test\_filter\_samples.py     |       29 |        2 |        4 |        2 |     88% |    74, 99 |
| tests/protzilla/data\_preprocessing/test\_imputation.py          |       87 |       10 |       10 |        5 |     85% |154-155, 179-180, 204-205, 232-233, 258-259 |
| tests/protzilla/data\_preprocessing/test\_normalisation.py       |       67 |        4 |       12 |        4 |     90% |309, 325, 351, 377 |
| tests/protzilla/data\_preprocessing/test\_outlier\_detection.py  |       41 |        3 |        6 |        3 |     87% |65, 79, 95 |
| tests/protzilla/data\_preprocessing/test\_plots.py               |       47 |        8 |       16 |        5 |     79% |20, 39, 56, 81, 117-120 |
| tests/protzilla/data\_preprocessing/test\_transformation.py      |       35 |        2 |        4 |        2 |     90% |  119, 140 |
| tests/protzilla/importing/test\_metadata\_import.py              |       23 |        0 |        0 |        0 |    100% |           |
| tests/protzilla/test\_history.py                                 |      116 |        0 |        6 |        0 |    100% |           |
| tests/protzilla/test\_run.py                                     |       78 |        8 |        2 |        0 |     90% |   107-125 |
| tests/protzilla/test\_transform\_dfs.py                          |       32 |        0 |        0 |        0 |    100% |           |
| tests/protzilla/test\_workflow\_helper.py                        |       62 |        0 |       10 |        0 |    100% |           |
| ui/main/\_\_init\_\_.py                                          |        0 |        0 |        0 |        0 |    100% |           |
|                                                        **TOTAL** | **1552** |  **109** |  **317** |   **56** | **90%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://github.com/antonneubauer/PROTzilla2/raw/python-coverage-comment-action-data/badge.svg)](https://github.com/antonneubauer/PROTzilla2/tree/python-coverage-comment-action-data)

This is the one to use if your repository is private or if you don't want to customize anything.



## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.