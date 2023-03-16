# Repository Coverage



| Name                                                            |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|---------------------------------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| \_\_init\_\_.py                                                 |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/\_\_init\_\_.py                                       |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/constants/\_\_init\_\_.py                             |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/constants/constants.py                                |        6 |        0 |        0 |        0 |    100% |           |
| protzilla/constants/location\_mapping.py                        |        6 |        0 |        0 |        0 |    100% |           |
| protzilla/constants/paths.py                                    |        5 |        0 |        0 |        0 |    100% |           |
| protzilla/data\_preprocessing/\_\_init\_\_.py                   |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/data\_preprocessing/filter\_proteins.py               |       15 |        2 |        4 |        1 |     74% |     54-55 |
| protzilla/data\_preprocessing/filter\_samples.py                |       26 |        1 |        4 |        2 |     90% |55->64, 65 |
| protzilla/data\_preprocessing/imputation.py                     |       74 |        1 |       14 |        1 |     98% |       138 |
| protzilla/data\_preprocessing/normalisation.py                  |       93 |        1 |       22 |        2 |     97% |239->250, 251 |
| protzilla/data\_preprocessing/outlier\_detection.py             |       56 |        4 |       16 |        6 |     83% |151, 156->165, 169-178, 182->198, 219, 220->exit |
| protzilla/data\_preprocessing/plots.py                          |       71 |        7 |        9 |        1 |     90% |176->191, 368-392 |
| protzilla/data\_preprocessing/transformation.py                 |       20 |        2 |        8 |        3 |     82% |31, 43->52, 53 |
| protzilla/history.py                                            |       64 |        2 |       22 |        2 |     95% |   32, 133 |
| protzilla/importing/ms\_data\_import.py                         |       16 |        1 |        2 |        0 |     94% |        32 |
| protzilla/run.py                                                |       86 |       20 |       22 |        0 |     69% |12-18, 64-70, 81-82, 85, 119-125 |
| protzilla/run\_manager.py                                       |       19 |       19 |        4 |        0 |      0% |      1-27 |
| protzilla/utilities/\_\_init\_\_.py                             |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/utilities/transform\_dfs.py                           |       11 |        0 |        0 |        0 |    100% |           |
| protzilla/workflow\_manager.py                                  |        7 |        7 |        2 |        0 |      0% |       1-9 |
| tests/conftest.py                                               |        6 |        0 |        0 |        0 |    100% |           |
| tests/protzilla/data\_preprocessing/test\_filter\_proteins.py   |       16 |        1 |        2 |        1 |     89% |        48 |
| tests/protzilla/data\_preprocessing/test\_filter\_samples.py    |       29 |        2 |        4 |        2 |     88% |    73, 98 |
| tests/protzilla/data\_preprocessing/test\_imputation.py         |       87 |       27 |       10 |       10 |     62% |140-141, 145, 153->158, 154-155, 165-166, 170, 178->183, 179-180, 190-191, 195, 203->208, 204-205, 216, 220, 231->232, 231->236, 233, 244-246, 257->262, 258-259, 277-282 |
| tests/protzilla/data\_preprocessing/test\_normalisation.py      |       60 |        4 |        8 |        4 |     88% |309, 325, 342, 366 |
| tests/protzilla/data\_preprocessing/test\_outlier\_detection.py |       23 |        3 |        6 |        3 |     79% |43, 52, 59 |
| tests/protzilla/data\_preprocessing/test\_plots.py              |       47 |        8 |       16 |        5 |     79% |21, 40, 57, 82, 117-120 |
| tests/protzilla/data\_preprocessing/test\_transformation.py     |       35 |        2 |        4 |        2 |     90% |  122, 137 |
| tests/protzilla/test\_history.py                                |       53 |        0 |        0 |        0 |    100% |           |
| tests/protzilla/test\_run.py                                    |       38 |        0 |        0 |        0 |    100% |           |
| tests/protzilla/test\_transform\_dfs.py                         |        0 |        0 |        0 |        0 |    100% |           |
|                                                       **TOTAL** |  **969** |  **114** |  **179** |   **45** | **84%** |           |


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