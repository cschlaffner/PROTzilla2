# Repository Coverage



| Name                                                                    |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|------------------------------------------------------------------------ | -------: | -------: | -------: | -------: | ------: | --------: |
| \_\_init\_\_.py                                                         |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/\_\_init\_\_.py                                               |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/constants/\_\_init\_\_.py                                     |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/constants/colors.py                                           |        2 |        0 |        0 |        0 |    100% |           |
| protzilla/constants/location\_mapping.py                                |        9 |        0 |        2 |        0 |    100% |           |
| protzilla/constants/logging.py                                          |       43 |       10 |       10 |        0 |     62% |47-48, 51-52, 55-56, 59-60, 63-64 |
| protzilla/constants/paths.py                                            |        8 |        0 |        0 |        0 |    100% |           |
| protzilla/data\_analysis/\_\_init\_\_.py                                |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/data\_analysis/classification.py                              |       65 |       32 |       12 |        4 |     48% |33-52, 54, 56-66, 67->exit, 220-270 |
| protzilla/data\_analysis/classification\_helper.py                      |       67 |       24 |       34 |        5 |     57% |26, 29-33, 66-67, 88-99, 115, 136-145 |
| protzilla/data\_analysis/clustering.py                                  |       20 |        1 |        6 |        1 |     92% |        76 |
| protzilla/data\_analysis/differential\_expression.py                    |        7 |        3 |        0 |        0 |     57% |      9-11 |
| protzilla/data\_analysis/differential\_expression\_anova.py             |       30 |        1 |        8 |        1 |     95% |        87 |
| protzilla/data\_analysis/differential\_expression\_helper.py            |        7 |        1 |        2 |        1 |     78% |        22 |
| protzilla/data\_analysis/differential\_expression\_linear\_model.py     |       47 |        6 |       12 |        3 |     85% |52-53, 55-56, 81-83 |
| protzilla/data\_analysis/differential\_expression\_t\_test.py           |       59 |        0 |       18 |        0 |    100% |           |
| protzilla/data\_analysis/dimension\_reduction.py                        |       33 |        4 |       10 |        2 |     86% |61-66, 94, 165 |
| protzilla/data\_analysis/model\_evaluation.py                           |       10 |        0 |        0 |        0 |    100% |           |
| protzilla/data\_analysis/model\_evaluation\_plots.py                    |       18 |        0 |        0 |        0 |    100% |           |
| protzilla/data\_analysis/plots.py                                       |       77 |        3 |       36 |        4 |     94% |55, 64->66, 106, 255 |
| protzilla/data\_analysis/protein\_graphs.py                             |      382 |       28 |      190 |       13 |     92% |31-39, 87, 110-111, 123, 251-253, 262-264, 282-283, 334, 359-363, 407, 421, 487, 518, 525, 722 |
| protzilla/data\_integration/database\_integration.py                    |       48 |        1 |       30 |        1 |     97% |        59 |
| protzilla/data\_integration/database\_query.py                          |       91 |       18 |       40 |        6 |     79% |14, 44-45, 51-53, 57, 66-70, 88->87, 102-107, 108->115, 116-119 |
| protzilla/data\_integration/di\_plots.py                                |      124 |       36 |       58 |        8 |     69% |69, 101->104, 105, 166-233, 282-283, 286, 296->exit, 350 |
| protzilla/data\_integration/enrichment\_analysis.py                     |      291 |       66 |      138 |       28 |     76% |22-23, 45->47, 168->174, 178->184, 185-187, 189, 196, 212-216, 234-238, 283->290, 290->297, 349-351, 440, 456-460, 462, 478-488, 490->500, 492-493, 500->507, 508-512, 515-516, 534, 599-600, 611-612, 614-615, 617-620, 624-625, 627-630, 643, 662-665, 679-682, 687 |
| protzilla/data\_integration/enrichment\_analysis\_gsea.py               |      124 |        3 |       52 |        5 |     95% |149, 152, 215->219, 356, 429->433 |
| protzilla/data\_integration/enrichment\_analysis\_helper.py             |       46 |        0 |       30 |        0 |    100% |           |
| protzilla/data\_preprocessing/\_\_init\_\_.py                           |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/data\_preprocessing/filter\_proteins.py                       |       17 |        2 |        4 |        1 |     76% |     51-52 |
| protzilla/data\_preprocessing/filter\_samples.py                        |       34 |        0 |        4 |        0 |    100% |           |
| protzilla/data\_preprocessing/imputation.py                             |       74 |        1 |       14 |        3 |     95% |140, 290->299, 309->315 |
| protzilla/data\_preprocessing/normalisation.py                          |       97 |        1 |       22 |        2 |     97% |244->255, 256 |
| protzilla/data\_preprocessing/outlier\_detection.py                     |       67 |        3 |       12 |        4 |     89% |172, 189, 244, 245->exit |
| protzilla/data\_preprocessing/peptide\_filter.py                        |       16 |        2 |        4 |        1 |     75% |     50-51 |
| protzilla/data\_preprocessing/plots.py                                  |       71 |        7 |        9 |        1 |     90% |176->191, 368-392 |
| protzilla/data\_preprocessing/transformation.py                         |       20 |        2 |        8 |        3 |     82% |31, 40->49, 50 |
| protzilla/history.py                                                    |      134 |       11 |       54 |        7 |     90% |35, 109, 116, 126, 172-176, 218, 225 |
| protzilla/importing/metadata\_import.py                                 |       31 |       11 |       14 |        1 |     56% |     20-35 |
| protzilla/importing/ms\_data\_import.py                                 |       48 |        4 |        8 |        2 |     89% |12-13, 56-57 |
| protzilla/importing/peptide\_import.py                                  |       25 |        2 |        2 |        0 |     93% |     16-17 |
| protzilla/run.py                                                        |      268 |       29 |       92 |        9 |     84% |46-52, 56-62, 120->131, 152, 154, 171->169, 207, 210, 254-255, 284-287, 330, 363, 367-370, 375->374 |
| protzilla/run\_helper.py                                                |       60 |       22 |       44 |        4 |     60% |24, 35-56, 62, 71 |
| protzilla/runner.py                                                     |       89 |        4 |       38 |        3 |     94% |115, 124, 156-157 |
| protzilla/utilities/\_\_init\_\_.py                                     |        1 |        0 |        0 |        0 |    100% |           |
| protzilla/utilities/clustergram.py                                      |      375 |       99 |      194 |       55 |     67% |69, 84, 86, 93, 137-138, 140, 142, 148->151, 151->158, 177, 192, 196, 200, 204, 214, 218-223, 228->230, 231, 233, 235, 239->241, 241->245, 246-257, 260, 262, 264-283, 302-305, 308->310, 315->317, 318, 370-371, 373-374, 389-390, 392-393, 461->467, 473, 490, 510, 513->536, 518->521, 555->561, 561->574, 649->654, 662->666, 683, 685, 715-722, 731-744, 754-758, 812->829, 829->849, 881->889, 889->898, 916-928, 931-943, 969-985, 999-1015 |
| protzilla/utilities/transform\_dfs.py                                   |       24 |        0 |        9 |        0 |    100% |           |
| protzilla/utilities/utilities.py                                        |       26 |        2 |        4 |        0 |     93% |     25-26 |
| protzilla/workflow\_helper.py                                           |       53 |        0 |       36 |        0 |    100% |           |
| runner\_cli.py                                                          |       21 |        5 |        2 |        1 |     74% | 55-58, 62 |
| tests/\_\_init\_\_.py                                                   |        0 |        0 |        0 |        0 |    100% |           |
| tests/conftest.py                                                       |       92 |       15 |       10 |        1 |     84% |22-23, 39, 87-92, 106-110, 149-152 |
| tests/protzilla/\_\_init\_\_.py                                         |        0 |        0 |        0 |        0 |    100% |           |
| tests/protzilla/data\_analysis/test\_analysis\_plots.py                 |       21 |        2 |        4 |        2 |     84% |    78, 90 |
| tests/protzilla/data\_analysis/test\_classification.py                  |       37 |        5 |        2 |        1 |     85% |75-91, 142-143 |
| tests/protzilla/data\_analysis/test\_clustering.py                      |       22 |        0 |        0 |        0 |    100% |           |
| tests/protzilla/data\_analysis/test\_differential\_expression.py        |       96 |        3 |       22 |        3 |     95% |91, 135, 290 |
| tests/protzilla/data\_analysis/test\_dimension\_reduction.py            |       45 |        8 |        0 |        0 |     82% |91-114, 119-143 |
| tests/protzilla/data\_analysis/test\_plots\_data\_analysis.py           |       66 |        5 |       22 |       11 |     82% |75, 82, 89, 96->exit, 102->exit, 112, 119, 126->exit, 131->exit, 157->exit, 179->exit |
| tests/protzilla/data\_analysis/test\_protein\_graphs.py                 |      603 |        0 |       10 |        0 |    100% |           |
| tests/protzilla/data\_integration/test\_database\_integration.py        |       25 |        0 |        2 |        0 |    100% |           |
| tests/protzilla/data\_integration/test\_database\_query.py              |       48 |        0 |        4 |        0 |    100% |           |
| tests/protzilla/data\_integration/test\_enrichment\_analysis.py         |      429 |       25 |       84 |        1 |     94% |399-480, 491-493 |
| tests/protzilla/data\_integration/test\_plots\_data\_integration.py     |      128 |        9 |       30 |        9 |     89% |31, 41, 56, 162, 191, 208, 258, 268, 285 |
| tests/protzilla/data\_preprocessing/\_\_init\_\_.py                     |        0 |        0 |        0 |        0 |    100% |           |
| tests/protzilla/data\_preprocessing/test\_filter\_proteins.py           |       25 |        4 |        2 |        1 |     81% | 13-39, 84 |
| tests/protzilla/data\_preprocessing/test\_filter\_samples.py            |       42 |        3 |        6 |        3 |     88% |58, 87, 116 |
| tests/protzilla/data\_preprocessing/test\_imputation.py                 |       87 |       10 |       10 |        5 |     85% |154-155, 179-180, 204-205, 232-233, 258-259 |
| tests/protzilla/data\_preprocessing/test\_normalisation.py              |       67 |        4 |       12 |        4 |     90% |309, 325, 351, 377 |
| tests/protzilla/data\_preprocessing/test\_outlier\_detection.py         |       41 |        3 |        6 |        3 |     87% |65, 79, 95 |
| tests/protzilla/data\_preprocessing/test\_peptide\_preprocessing.py     |       24 |        1 |        2 |        1 |     92% |        47 |
| tests/protzilla/data\_preprocessing/test\_plots\_data\_preprocessing.py |       47 |        8 |       16 |        5 |     79% |20, 39, 56, 81, 117-120 |
| tests/protzilla/data\_preprocessing/test\_transformation.py             |       35 |        2 |        4 |        2 |     90% |  119, 140 |
| tests/protzilla/importing/test\_metadata\_import.py                     |       26 |        0 |        0 |        0 |    100% |           |
| tests/protzilla/importing/test\_ms\_data\_import.py                     |       21 |        0 |        2 |        0 |    100% |           |
| tests/protzilla/importing/test\_peptide\_import.py                      |       20 |        0 |        0 |        0 |    100% |           |
| tests/protzilla/test\_history.py                                        |      117 |        0 |        6 |        0 |    100% |           |
| tests/protzilla/test\_run.py                                            |      157 |        0 |       10 |        0 |    100% |           |
| tests/protzilla/test\_run\_helper.py                                    |       42 |        0 |        0 |        0 |    100% |           |
| tests/protzilla/test\_runner.py                                         |      100 |        0 |       10 |        0 |    100% |           |
| tests/protzilla/test\_runner\_cli.py                                    |       66 |        0 |        4 |        0 |    100% |           |
| tests/protzilla/test\_transform\_dfs.py                                 |       47 |        0 |        0 |        0 |    100% |           |
| tests/protzilla/test\_workflow\_helper.py                               |       62 |        0 |        4 |        0 |    100% |           |
| tests/ui/test\_views.py                                                 |       39 |        0 |        0 |        0 |    100% |           |
| tests/ui/test\_views\_helper.py                                         |       37 |        2 |        2 |        0 |     95% |     16-26 |
| ui/\_\_init\_\_.py                                                      |        0 |        0 |        0 |        0 |    100% |           |
| ui/\_\_main\_\_.py                                                      |       11 |       11 |        2 |        0 |      0% |      2-21 |
| ui/main/\_\_init\_\_.py                                                 |        0 |        0 |        0 |        0 |    100% |           |
| ui/main/asgi.py                                                         |        4 |        4 |        0 |        0 |      0% |     10-16 |
| ui/main/settings.py                                                     |       28 |        0 |        2 |        1 |     97% |    24->32 |
| ui/main/upload\_handler.py                                              |       37 |       37 |        2 |        0 |      0% |      1-68 |
| ui/main/urls.py                                                         |        4 |        4 |        0 |        0 |      0% |     16-21 |
| ui/main/views.py                                                        |        3 |        3 |        0 |        0 |      0% |       1-5 |
| ui/main/wsgi.py                                                         |        4 |        4 |        0 |        0 |      0% |     10-16 |
| ui/manage.py                                                            |       14 |       14 |        2 |        0 |      0% |      2-24 |
| ui/runs/\_\_init\_\_.py                                                 |        0 |        0 |        0 |        0 |    100% |           |
| ui/runs/apps.py                                                         |        4 |        4 |        0 |        0 |      0% |       1-6 |
| ui/runs/fields.py                                                       |      116 |       98 |       66 |        0 |     10% |16-27, 35-63, 74-84, 88-90, 103-114, 118-123, 136-214, 218-226 |
| ui/runs/migrations/\_\_init\_\_.py                                      |        0 |        0 |        0 |        0 |    100% |           |
| ui/runs/templatetags/\_\_init\_\_.py                                    |        0 |        0 |        0 |        0 |    100% |           |
| ui/runs/templatetags/id\_tags.py                                        |       10 |       10 |        2 |        0 |      0% |      1-13 |
| ui/runs/urls.py                                                         |        4 |        4 |        0 |        0 |      0% |       1-6 |
| ui/runs/utilities/alert.py                                              |        2 |        1 |        0 |        0 |     50% |         2 |
| ui/runs/views.py                                                        |      317 |      261 |      106 |        0 |     14% |46, 58-97, 125-141, 158-179, 185-313, 317-324, 328-330, 334-336, 340-342, 346-355, 359-366, 370-378, 382-409, 413-442, 446-448, 452-453, 475-477, 481-495, 503-533, 552-565, 571-607 |
| ui/runs/views\_helper.py                                                |       52 |        9 |       22 |        4 |     80% |14->16, 20, 33, 36-42 |
|                                                               **TOTAL** | **6483** | **1017** | **1752** |  **236** | **81%** |           |


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