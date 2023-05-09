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
| protzilla/data\_analysis/differential\_expression\_anova.py             |       27 |        0 |        8 |        1 |     97% |    92->95 |
| protzilla/data\_analysis/differential\_expression\_helper.py            |        7 |        1 |        2 |        1 |     78% |        22 |
| protzilla/data\_analysis/differential\_expression\_t\_test.py           |       48 |        0 |       14 |        0 |    100% |           |
| protzilla/data\_analysis/dimension\_reduction.py                        |       33 |        6 |       10 |        2 |     81% |62-67, 95, 148-153, 162 |
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
| protzilla/run.py                                                        |      226 |       31 |       72 |        7 |     83% |45-51, 55-61, 110-111, 160->158, 173, 181-182, 190-195, 227-228, 235->239, 250-253, 291->exit, 324, 329->328 |
| protzilla/run\_helper.py                                                |       30 |        1 |       22 |        2 |     94% |10, 24->28 |
| protzilla/runner.py                                                     |       76 |        5 |       30 |        4 |     92% |109, 118->121, 126-127, 140-141 |
| protzilla/utilities/\_\_init\_\_.py                                     |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/utilities/random.py                                           |        4 |        0 |        0 |        0 |    100% |           |
| protzilla/utilities/transform\_dfs.py                                   |       13 |        0 |        0 |        0 |    100% |           |
| protzilla/workflow\_helper.py                                           |       49 |        0 |       36 |        0 |    100% |           |
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
| tests/protzilla/test\_run.py                                            |      117 |        0 |        8 |        0 |    100% |           |
| tests/protzilla/test\_run\_helper.py                                    |       42 |        0 |        0 |        0 |    100% |           |
| tests/protzilla/test\_runner.py                                         |       95 |        0 |       10 |        0 |    100% |           |
| tests/protzilla/test\_runner\_cli.py                                    |       66 |        0 |        4 |        0 |    100% |           |
| tests/protzilla/test\_transform\_dfs.py                                 |       35 |        0 |        0 |        0 |    100% |           |
| tests/protzilla/test\_workflow\_helper.py                               |       55 |        0 |        4 |        0 |    100% |           |
| tests/ui/test\_views.py                                                 |       38 |        0 |        0 |        0 |    100% |           |
| tests/ui/test\_views\_helper.py                                         |       37 |        2 |        2 |        0 |     95% |     16-26 |
| ui/main/\_\_init\_\_.py                                                 |        0 |        0 |        0 |        0 |    100% |           |
| ui/main/settings.py                                                     |       25 |        0 |        2 |        1 |     96% |    22->30 |
| ui/runs/\_\_init\_\_.py                                                 |        0 |        0 |        0 |        0 |    100% |           |
| ui/runs/fields.py                                                       |       76 |       62 |       38 |        0 |     12% |13-29, 33-49, 60-62, 75-82, 86-89, 102-139, 143-149 |
| ui/runs/utilities/alert.py                                              |        2 |        1 |        0 |        0 |     50% |         2 |
| ui/runs/views.py                                                        |      167 |      123 |       34 |        0 |     23% |32, 44-51, 80-93, 111-133, 137-144, 148-150, 154-156, 160-162, 166-175, 179-186, 190-198, 202-230, 234-261, 265-267, 271-272, 294-296, 300-314 |
| ui/runs/views\_helper.py                                                |       39 |        1 |       16 |        2 |     95% |12->14, 18 |
|                                                               **TOTAL** | **2648** |  **316** |  **563** |   **78** | **85%** |           |


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