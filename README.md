# Repository Coverage



| Name                                                            |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|---------------------------------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| \_\_init\_\_.py                                                 |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/\_\_init\_\_.py                                       |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/constants/\_\_init\_\_.py                             |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/constants/colors.py                                   |        2 |        0 |        0 |        0 |    100% |           |
| protzilla/constants/location\_mapping.py                        |        6 |        0 |        2 |        1 |     88% |  16->exit |
| protzilla/constants/paths.py                                    |        5 |        0 |        0 |        0 |    100% |           |
| protzilla/data\_preprocessing/\_\_init\_\_.py                   |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/data\_preprocessing/filter\_proteins.py               |       15 |        2 |        4 |        1 |     74% |     55-56 |
| protzilla/data\_preprocessing/filter\_samples.py                |       26 |        1 |        4 |        2 |     90% |56->65, 66 |
| protzilla/data\_preprocessing/imputation.py                     |       74 |        1 |       14 |        1 |     98% |       140 |
| protzilla/data\_preprocessing/normalisation.py                  |       98 |        1 |       22 |        2 |     98% |244->255, 256 |
| protzilla/data\_preprocessing/outlier\_detection.py             |       57 |        4 |       16 |        6 |     84% |152, 157->166, 170-179, 183->199, 222, 223->exit |
| protzilla/data\_preprocessing/plots.py                          |       71 |        7 |        9 |        1 |     90% |176->191, 368-392 |
| protzilla/data\_preprocessing/transformation.py                 |       20 |        2 |        8 |        3 |     82% |31, 43->52, 53 |
| protzilla/history.py                                            |       81 |        3 |       26 |        3 |     94% |33, 135, 149 |
| protzilla/importing/ms\_data\_import.py                         |       16 |        1 |        2 |        0 |     94% |        32 |
| protzilla/run.py                                                |       87 |       19 |       20 |        1 |     72% |13-19, 25, 64-66, 77-78, 81, 115-119 |
| protzilla/run\_manager.py                                       |       19 |       19 |        4 |        0 |      0% |      1-27 |
| protzilla/utilities/\_\_init\_\_.py                             |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/utilities/random.py                                   |        4 |        0 |        0 |        0 |    100% |           |
| protzilla/utilities/transform\_dfs.py                           |       11 |        0 |        0 |        0 |    100% |           |
| protzilla/workflow\_manager.py                                  |        7 |        7 |        2 |        0 |      0% |       1-9 |
| tests/conftest.py                                               |        6 |        0 |        0 |        0 |    100% |           |
| tests/protzilla/data\_preprocessing/test\_filter\_proteins.py   |       16 |        1 |        2 |        1 |     89% |        48 |
| tests/protzilla/data\_preprocessing/test\_filter\_samples.py    |       29 |        2 |        4 |        2 |     88% |    74, 99 |
| tests/protzilla/data\_preprocessing/test\_imputation.py         |       87 |       10 |       10 |        5 |     85% |154-155, 179-180, 204-205, 232-233, 258-259 |
| tests/protzilla/data\_preprocessing/test\_normalisation.py      |       67 |        4 |       12 |        4 |     90% |309, 325, 351, 377 |
| tests/protzilla/data\_preprocessing/test\_outlier\_detection.py |       23 |        3 |        6 |        3 |     79% |42, 51, 58 |
| tests/protzilla/data\_preprocessing/test\_plots.py              |       47 |        8 |       16 |        5 |     79% |20, 39, 56, 81, 116-119 |
| tests/protzilla/data\_preprocessing/test\_transformation.py     |       35 |        2 |        4 |        2 |     90% |  119, 134 |
| tests/protzilla/test\_history.py                                |       61 |        0 |        0 |        0 |    100% |           |
| tests/protzilla/test\_run.py                                    |       35 |        0 |        0 |        0 |    100% |           |
| tests/protzilla/test\_transform\_dfs.py                         |        0 |        0 |        0 |        0 |    100% |           |
|                                                       **TOTAL** | **1005** |   **97** |  **187** |   **43** | **87%** |           |


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