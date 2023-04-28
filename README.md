# Repository Coverage



| Name                                                                    |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|------------------------------------------------------------------------ | -------: | -------: | -------: | -------: | ------: | --------: |
| \_\_init\_\_.py                                                         |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/\_\_init\_\_.py                                               |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/constants/\_\_init\_\_.py                                     |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/constants/colors.py                                           |        2 |        0 |        0 |        0 |    100% |           |
| protzilla/constants/location\_mapping.py                                |        8 |        0 |        4 |        1 |     92% |  22->exit |
| protzilla/constants/logging.py                                          |        3 |        0 |        0 |        0 |    100% |           |
| protzilla/constants/paths.py                                            |        6 |        0 |        0 |        0 |    100% |           |
| protzilla/data\_analysis/clustering.py                                  |       20 |        1 |        6 |        1 |     92% |        76 |
| protzilla/data\_analysis/differential\_expression.py                    |        5 |        2 |        0 |        0 |     60% |       8-9 |
| protzilla/data\_analysis/differential\_expression\_anova.py             |       28 |        2 |        8 |        2 |     89% |50-51, 93->96 |
| protzilla/data\_analysis/differential\_expression\_helper.py            |        7 |        1 |        2 |        1 |     78% |        22 |
| protzilla/data\_analysis/differential\_expression\_t\_test.py           |       40 |        0 |       10 |        0 |    100% |           |
| protzilla/data\_analysis/dimension\_reduction.py                        |       33 |        6 |       10 |        2 |     81% |62-67, 95, 150-155, 164 |
| protzilla/data\_analysis/plots.py                                       |       36 |        1 |       12 |        2 |     94% |53, 62->64 |
| protzilla/data\_preprocessing/\_\_init\_\_.py                           |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/data\_preprocessing/filter\_proteins.py                       |       15 |        2 |        4 |        1 |     74% |     55-56 |
| protzilla/data\_preprocessing/filter\_samples.py                        |       26 |        1 |        4 |        2 |     90% |56->65, 66 |
| protzilla/data\_preprocessing/imputation.py                             |       74 |        1 |       14 |        3 |     95% |140, 290->299, 309->315 |
| protzilla/data\_preprocessing/normalisation.py                          |       99 |        1 |       22 |        2 |     98% |243->254, 255 |
| protzilla/data\_preprocessing/outlier\_detection.py                     |       67 |        3 |       12 |        4 |     89% |172, 189, 244, 245->exit |
| protzilla/data\_preprocessing/plots.py                                  |       71 |        7 |        9 |        1 |     90% |176->191, 368-392 |
| protzilla/data\_preprocessing/transformation.py                         |       20 |        2 |        8 |        3 |     82% |31, 40->49, 50 |
| protzilla/history.py                                                    |      122 |        7 |       48 |        7 |     92% |33, 109, 116, 120, 126, 192, 207 |
| protzilla/importing/metadata\_import.py                                 |       26 |        7 |       12 |        1 |     63% |     19-26 |
| protzilla/importing/ms\_data\_import.py                                 |       30 |        0 |        4 |        0 |    100% |           |
| protzilla/run.py                                                        |      206 |       42 |       62 |        7 |     75% |38-44, 48-54, 103-104, 133, 140-141, 153->151, 164-175, 178, 183-188, 220-221, 239-242, 280->exit, 303, 311->310, 313 |
| protzilla/run\_helper.py                                                |       30 |        4 |       22 |        5 |     83% |10, 15, 21, 24->28, 29 |
| protzilla/runner.py                                                     |       76 |        6 |       30 |        4 |     91% |109, 112, 118->121, 126-127, 140-141 |
| protzilla/utilities/\_\_init\_\_.py                                     |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/utilities/random.py                                           |        4 |        0 |        0 |        0 |    100% |           |
| protzilla/utilities/transform\_dfs.py                                   |       13 |        0 |        0 |        0 |    100% |           |
| protzilla/workflow\_helper.py                                           |       45 |        7 |       32 |        0 |     88% |22-27, 31, 35, 39 |
| runner\_cli.py                                                          |       20 |        5 |        2 |        1 |     73% | 52-55, 59 |
| tests/\_\_init\_\_.py                                                   |        0 |        0 |        0 |        0 |    100% |           |
| tests/conftest.py                                                       |       38 |        0 |        6 |        0 |    100% |           |
| tests/protzilla/\_\_init\_\_.py                                         |        0 |        0 |        0 |        0 |    100% |           |
| tests/protzilla/data\_analysis/test\_clustering.py                      |       22 |        0 |        0 |        0 |    100% |           |
| tests/protzilla/data\_analysis/test\_differential\_expression.py        |       70 |        2 |       14 |        2 |     95% |   74, 230 |
| tests/protzilla/data\_analysis/test\_dimension\_reduction.py            |       45 |        8 |        0 |        0 |     82% |91-114, 119-143 |
| tests/protzilla/data\_analysis/test\_plots\_data\_analysis.py           |       39 |        3 |       10 |        5 |     84% |75, 82, 89, 96->exit, 102->exit |
| tests/protzilla/data\_preprocessing/test\_filter\_proteins.py           |       16 |        1 |        2 |        1 |     89% |        48 |
| tests/protzilla/data\_preprocessing/test\_filter\_samples.py            |       29 |        2 |        4 |        2 |     88% |    74, 99 |
| tests/protzilla/data\_preprocessing/test\_imputation.py                 |       87 |       10 |       10 |        5 |     85% |154-155, 179-180, 204-205, 232-233, 258-259 |
| tests/protzilla/data\_preprocessing/test\_normalisation.py              |       67 |        4 |       12 |        4 |     90% |309, 325, 351, 377 |
| tests/protzilla/data\_preprocessing/test\_outlier\_detection.py         |       41 |        3 |        6 |        3 |     87% |65, 79, 95 |
| tests/protzilla/data\_preprocessing/test\_plots\_data\_preprocessing.py |       47 |        8 |       16 |        5 |     79% |20, 39, 56, 81, 117-120 |
| tests/protzilla/data\_preprocessing/test\_transformation.py             |       35 |        2 |        4 |        2 |     90% |  119, 140 |
| tests/protzilla/importing/test\_metadata\_import.py                     |       23 |        0 |        0 |        0 |    100% |           |
| tests/protzilla/importing/test\_ms\_data\_import.py                     |       16 |        0 |        0 |        0 |    100% |           |
| tests/protzilla/test\_history.py                                        |      116 |        0 |        6 |        0 |    100% |           |
| tests/protzilla/test\_run.py                                            |      108 |        8 |        2 |        0 |     93% |   144-162 |
| tests/protzilla/test\_run\_helper.py                                    |       42 |        0 |        0 |        0 |    100% |           |
| tests/protzilla/test\_runner.py                                         |       89 |        0 |       10 |        0 |    100% |           |
| tests/protzilla/test\_runner\_cli.py                                    |       66 |        0 |        4 |        0 |    100% |           |
| tests/protzilla/test\_transform\_dfs.py                                 |       35 |        0 |        0 |        0 |    100% |           |
| tests/protzilla/test\_workflow\_helper.py                               |       55 |        0 |        4 |        0 |    100% |           |
| ui/main/\_\_init\_\_.py                                                 |        0 |        0 |        0 |        0 |    100% |           |
|                                                               **TOTAL** | **2218** |  **159** |  **447** |   **79** | **90%** |           |


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