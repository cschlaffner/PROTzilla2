# Repository Coverage



| Name                                                                    |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|------------------------------------------------------------------------ | -------: | -------: | -------: | -------: | ------: | --------: |
| \_\_init\_\_.py                                                         |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/\_\_init\_\_.py                                               |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/constants/\_\_init\_\_.py                                     |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/constants/colors.py                                           |        2 |        0 |        0 |        0 |    100% |           |
| protzilla/constants/location\_mapping.py                                |        9 |        0 |        2 |        0 |    100% |           |
| protzilla/constants/logging.py                                          |        3 |        0 |        0 |        0 |    100% |           |
| protzilla/constants/paths.py                                            |        7 |        0 |        0 |        0 |    100% |           |
| protzilla/data\_analysis/clustering.py                                  |       20 |        1 |        6 |        1 |     92% |        76 |
| protzilla/data\_analysis/differential\_expression.py                    |        5 |        2 |        0 |        0 |     60% |       8-9 |
| protzilla/data\_analysis/differential\_expression\_anova.py             |       30 |        3 |        8 |        2 |     87% | 52-53, 87 |
| protzilla/data\_analysis/differential\_expression\_helper.py            |        7 |        1 |        2 |        1 |     78% |        22 |
| protzilla/data\_analysis/differential\_expression\_t\_test.py           |       57 |        0 |       18 |        0 |    100% |           |
| protzilla/data\_analysis/dimension\_reduction.py                        |       33 |        4 |       10 |        2 |     86% |62-67, 95, 163 |
| protzilla/data\_analysis/plots.py                                       |       75 |        2 |       34 |        3 |     95% |55, 64->66, 253 |
| protzilla/data\_integration/database\_query.py                          |       11 |        8 |        4 |        0 |     20% |      7-35 |
| protzilla/data\_integration/enrichment\_analysis.py                     |      226 |       60 |      114 |       13 |     70% |37->39, 132->138, 142->148, 149-151, 153, 204-207, 219-222, 244-245, 254->257, 274-334, 362, 364, 395, 431, 433, 437, 525-526 |
| protzilla/data\_preprocessing/\_\_init\_\_.py                           |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/data\_preprocessing/filter\_proteins.py                       |       15 |        2 |        4 |        1 |     74% |     55-56 |
| protzilla/data\_preprocessing/filter\_samples.py                        |       34 |        0 |        4 |        0 |    100% |           |
| protzilla/data\_preprocessing/imputation.py                             |       74 |        1 |       14 |        3 |     95% |140, 290->299, 309->315 |
| protzilla/data\_preprocessing/normalisation.py                          |       97 |        1 |       22 |        2 |     97% |244->255, 256 |
| protzilla/data\_preprocessing/outlier\_detection.py                     |       67 |        3 |       12 |        4 |     89% |172, 189, 244, 245->exit |
| protzilla/data\_preprocessing/peptide\_filter.py                        |       16 |        2 |        4 |        1 |     75% |     50-51 |
| protzilla/data\_preprocessing/plots.py                                  |       71 |        7 |        9 |        1 |     90% |176->191, 368-392 |
| protzilla/data\_preprocessing/transformation.py                         |       20 |        2 |        8 |        3 |     82% |31, 40->49, 50 |
| protzilla/history.py                                                    |      124 |        5 |       50 |        5 |     94% |33, 107, 114, 124, 210 |
| protzilla/importing/metadata\_import.py                                 |       31 |       11 |       14 |        1 |     56% |     20-35 |
| protzilla/importing/ms\_data\_import.py                                 |       35 |        4 |        8 |        2 |     86% |10-11, 52-53 |
| protzilla/importing/peptide\_import.py                                  |       21 |        2 |        2 |        0 |     91% |     15-16 |
| protzilla/run.py                                                        |      259 |       27 |       88 |        6 |     85% |46-52, 56-62, 145, 147, 164->162, 243-244, 273-276, 319, 352, 356-359, 364->363 |
| protzilla/run\_helper.py                                                |       38 |        4 |       28 |        1 |     86% |     36-39 |
| protzilla/runner.py                                                     |       89 |        4 |       38 |        3 |     94% |115, 124, 156-157 |
| protzilla/utilities/\_\_init\_\_.py                                     |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/utilities/clustergram.py                                      |      375 |       99 |      194 |       55 |     67% |69, 84, 86, 93, 137-138, 140, 142, 148->151, 151->158, 177, 192, 196, 200, 204, 214, 218-223, 228->230, 231, 233, 235, 239->241, 241->245, 246-257, 260, 262, 264-283, 302-305, 308->310, 315->317, 318, 370-371, 373-374, 389-390, 392-393, 461->467, 473, 490, 510, 513->536, 518->521, 555->561, 561->574, 649->654, 662->666, 683, 685, 715-722, 731-744, 754-758, 812->829, 829->849, 881->889, 889->898, 916-928, 931-943, 969-985, 999-1015 |
| protzilla/utilities/memory.py                                           |        5 |        2 |        0 |        0 |     60% |       7-8 |
| protzilla/utilities/random.py                                           |        4 |        0 |        0 |        0 |    100% |           |
| protzilla/utilities/transform\_dfs.py                                   |       13 |        0 |        0 |        0 |    100% |           |
| protzilla/workflow\_helper.py                                           |       53 |        0 |       36 |        0 |    100% |           |
| runner\_cli.py                                                          |       21 |        5 |        2 |        1 |     74% | 55-58, 62 |
| tests/\_\_init\_\_.py                                                   |        0 |        0 |        0 |        0 |    100% |           |
| tests/conftest.py                                                       |       54 |        3 |       10 |        1 |     94% | 18-19, 35 |
| tests/protzilla/\_\_init\_\_.py                                         |        0 |        0 |        0 |        0 |    100% |           |
| tests/protzilla/data\_analysis/test\_analysis\_plots.py                 |       21 |        2 |        4 |        2 |     84% |    78, 90 |
| tests/protzilla/data\_analysis/test\_clustering.py                      |       22 |        0 |        0 |        0 |    100% |           |
| tests/protzilla/data\_analysis/test\_differential\_expression.py        |       83 |        2 |       16 |        2 |     96% |   82, 306 |
| tests/protzilla/data\_analysis/test\_dimension\_reduction.py            |       45 |        8 |        0 |        0 |     82% |91-114, 119-143 |
| tests/protzilla/data\_analysis/test\_plots\_data\_analysis.py           |       66 |        5 |       22 |       11 |     82% |75, 82, 89, 96->exit, 102->exit, 112, 119, 126->exit, 131->exit, 157->exit, 179->exit |
| tests/protzilla/data\_integration/test\_enrichment\_analysis.py         |      198 |        0 |       26 |        0 |    100% |           |
| tests/protzilla/data\_preprocessing/\_\_init\_\_.py                     |        0 |        0 |        0 |        0 |    100% |           |
| tests/protzilla/data\_preprocessing/test\_filter\_proteins.py           |       16 |        1 |        2 |        1 |     89% |        48 |
| tests/protzilla/data\_preprocessing/test\_filter\_samples.py            |       42 |        3 |        6 |        3 |     88% |58, 88, 113 |
| tests/protzilla/data\_preprocessing/test\_imputation.py                 |       87 |       10 |       10 |        5 |     85% |154-155, 179-180, 204-205, 232-233, 258-259 |
| tests/protzilla/data\_preprocessing/test\_normalisation.py              |       67 |        4 |       12 |        4 |     90% |309, 325, 351, 377 |
| tests/protzilla/data\_preprocessing/test\_outlier\_detection.py         |       41 |        3 |        6 |        3 |     87% |65, 79, 95 |
| tests/protzilla/data\_preprocessing/test\_peptide\_preprocessing.py     |       24 |        1 |        2 |        1 |     92% |        47 |
| tests/protzilla/data\_preprocessing/test\_plots\_data\_preprocessing.py |       47 |        8 |       16 |        5 |     79% |20, 39, 56, 81, 117-120 |
| tests/protzilla/data\_preprocessing/test\_transformation.py             |       35 |        2 |        4 |        2 |     90% |  119, 140 |
| tests/protzilla/importing/test\_metadata\_import.py                     |       26 |        0 |        0 |        0 |    100% |           |
| tests/protzilla/importing/test\_ms\_data\_import.py                     |       16 |        0 |        0 |        0 |    100% |           |
| tests/protzilla/importing/test\_peptide\_import.py                      |       20 |        0 |        0 |        0 |    100% |           |
| tests/protzilla/test\_history.py                                        |      117 |        0 |        6 |        0 |    100% |           |
| tests/protzilla/test\_run.py                                            |      156 |        0 |       10 |        0 |    100% |           |
| tests/protzilla/test\_run\_helper.py                                    |       42 |        0 |        0 |        0 |    100% |           |
| tests/protzilla/test\_runner.py                                         |      100 |        0 |       10 |        0 |    100% |           |
| tests/protzilla/test\_runner\_cli.py                                    |       66 |        0 |        4 |        0 |    100% |           |
| tests/protzilla/test\_transform\_dfs.py                                 |       35 |        0 |        0 |        0 |    100% |           |
| tests/protzilla/test\_workflow\_helper.py                               |       60 |        0 |        4 |        0 |    100% |           |
| tests/ui/test\_views.py                                                 |       39 |        0 |        0 |        0 |    100% |           |
| tests/ui/test\_views\_helper.py                                         |       37 |        2 |        2 |        0 |     95% |     16-26 |
| ui/main/\_\_init\_\_.py                                                 |        0 |        0 |        0 |        0 |    100% |           |
| ui/main/settings.py                                                     |       25 |        0 |        2 |        1 |     96% |    22->30 |
| ui/runs/\_\_init\_\_.py                                                 |        0 |        0 |        0 |        0 |    100% |           |
| ui/runs/fields.py                                                       |       96 |       82 |       56 |        0 |      9% |13-31, 35-61, 72-74, 87-96, 100-105, 118-159, 163-171 |
| ui/runs/utilities/alert.py                                              |        2 |        1 |        0 |        0 |     50% |         2 |
| ui/runs/views.py                                                        |      192 |      145 |       48 |        0 |     20% |36, 48-54, 84-97, 115-162, 166-173, 177-179, 183-185, 189-191, 195-204, 208-215, 219-227, 231-258, 262-300, 304-306, 310-311, 333-335, 339-353 |
| ui/runs/views\_helper.py                                                |       51 |       10 |       22 |        2 |     75% |12->14, 18, 25-37 |
|                                                               **TOTAL** | **3875** |  **554** | **1035** |  **154** | **81%** |           |


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