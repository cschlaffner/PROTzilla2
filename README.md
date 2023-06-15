# Repository Coverage



| Name                                                                    |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|------------------------------------------------------------------------ | -------: | -------: | -------: | -------: | ------: | --------: |
| \_\_init\_\_.py                                                         |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/\_\_init\_\_.py                                               |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/constants/\_\_init\_\_.py                                     |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/constants/colors.py                                           |        2 |        0 |        0 |        0 |    100% |           |
| protzilla/constants/location\_mapping.py                                |        9 |        0 |        2 |        0 |    100% |           |
| protzilla/constants/logging.py                                          |       43 |       15 |       10 |        0 |     53% |38-40, 43-44, 47-48, 51-52, 55-56, 59-60, 63-64 |
| protzilla/constants/paths.py                                            |        8 |        0 |        0 |        0 |    100% |           |
| protzilla/data\_analysis/classification.py                              |       47 |        0 |        8 |        1 |     98% |  76->exit |
| protzilla/data\_analysis/classification\_helper.py                      |      111 |        8 |       42 |        5 |     86% |47->exit, 66->exit, 81-92, 138->exit, 171->exit |
| protzilla/data\_analysis/clustering.py                                  |       20 |        1 |        6 |        1 |     92% |        76 |
| protzilla/data\_analysis/differential\_expression.py                    |        7 |        3 |        0 |        0 |     57% |      9-11 |
| protzilla/data\_analysis/differential\_expression\_anova.py             |       30 |        1 |        8 |        1 |     95% |        87 |
| protzilla/data\_analysis/differential\_expression\_helper.py            |        7 |        1 |        2 |        1 |     78% |        22 |
| protzilla/data\_analysis/differential\_expression\_linear\_model.py     |       47 |        6 |       12 |        3 |     85% |52-53, 55-56, 81-83 |
| protzilla/data\_analysis/differential\_expression\_t\_test.py           |       57 |        0 |       18 |        0 |    100% |           |
| protzilla/data\_analysis/dimension\_reduction.py                        |       33 |        4 |       10 |        2 |     86% |61-66, 94, 165 |
| protzilla/data\_analysis/plots.py                                       |       77 |        3 |       36 |        4 |     94% |55, 64->66, 106, 255 |
| protzilla/data\_integration/database\_query.py                          |       30 |       21 |        6 |        0 |     25% |10-41, 45-46, 50-51, 55-63 |
| protzilla/data\_integration/di\_plots.py                                |       85 |       32 |       34 |        4 |     60% |69, 101->104, 105, 166-233 |
| protzilla/data\_integration/enrichment\_analysis.py                     |      307 |       91 |      160 |       24 |     68% |34->36, 153->159, 163->169, 170-172, 174, 201-205, 219-223, 254-311, 339->346, 346->353, 392-393, 458-468, 470->480, 472-473, 475-478, 480->485, 486, 491-492, 510, 567-568, 576-577, 579-580, 582-585, 589-590, 592-595, 678-679, 701-702, 714 |
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
| protzilla/importing/ms\_data\_import.py                                 |       35 |        4 |        8 |        2 |     86% |10-11, 52-53 |
| protzilla/importing/peptide\_import.py                                  |       21 |        2 |        2 |        0 |     91% |     15-16 |
| protzilla/run.py                                                        |      265 |       28 |       90 |        8 |     85% |46-52, 56-62, 120->131, 152, 154, 171->169, 208, 252-253, 282-285, 327, 360, 364-367, 372->371 |
| protzilla/run\_helper.py                                                |       43 |        8 |       34 |        3 |     75% |31-36, 42, 51 |
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
| tests/protzilla/data\_analysis/test\_classification.py                  |       25 |        3 |        0 |        0 |     88% |     62-76 |
| tests/protzilla/data\_analysis/test\_clustering.py                      |       22 |        0 |        0 |        0 |    100% |           |
| tests/protzilla/data\_analysis/test\_differential\_expression.py        |      105 |        3 |       22 |        3 |     95% |91, 135, 333 |
| tests/protzilla/data\_analysis/test\_dimension\_reduction.py            |       45 |        8 |        0 |        0 |     82% |91-114, 119-143 |
| tests/protzilla/data\_analysis/test\_plots\_data\_analysis.py           |       66 |        5 |       22 |       11 |     82% |75, 82, 89, 96->exit, 102->exit, 112, 119, 126->exit, 131->exit, 157->exit, 179->exit |
| tests/protzilla/data\_integration/test\_enrichment\_analysis.py         |      210 |        3 |       56 |        1 |     98% |   354-356 |
| tests/protzilla/data\_integration/test\_plots\_data\_integration.py     |       72 |        8 |        8 |        4 |     85% |16-19, 33, 43, 59, 169 |
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
| tests/protzilla/importing/test\_ms\_data\_import.py                     |       16 |        0 |        0 |        0 |    100% |           |
| tests/protzilla/importing/test\_peptide\_import.py                      |       20 |        0 |        0 |        0 |    100% |           |
| tests/protzilla/test\_history.py                                        |      117 |        0 |        6 |        0 |    100% |           |
| tests/protzilla/test\_run.py                                            |      157 |        0 |       10 |        0 |    100% |           |
| tests/protzilla/test\_run\_helper.py                                    |       42 |        0 |        0 |        0 |    100% |           |
| tests/protzilla/test\_runner.py                                         |      100 |        0 |       10 |        0 |    100% |           |
| tests/protzilla/test\_runner\_cli.py                                    |       66 |        0 |        4 |        0 |    100% |           |
| tests/protzilla/test\_transform\_dfs.py                                 |       35 |        0 |        0 |        0 |    100% |           |
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
| ui/runs/fields.py                                                       |      113 |       96 |       66 |        0 |      9% |15-26, 34-62, 73-83, 87-89, 102-113, 117-122, 135-205, 209-217 |
| ui/runs/migrations/\_\_init\_\_.py                                      |        0 |        0 |        0 |        0 |    100% |           |
| ui/runs/templatetags/\_\_init\_\_.py                                    |        0 |        0 |        0 |        0 |    100% |           |
| ui/runs/templatetags/id\_tags.py                                        |       10 |       10 |        2 |        0 |      0% |      1-13 |
| ui/runs/urls.py                                                         |        4 |        4 |        0 |        0 |      0% |       1-6 |
| ui/runs/utilities/alert.py                                              |        2 |        1 |        0 |        0 |     50% |         2 |
| ui/runs/views.py                                                        |      248 |      197 |       72 |        0 |     17% |37, 49-80, 107-123, 140-161, 172-245, 249-256, 260-262, 266-268, 272-274, 278-287, 291-298, 302-310, 314-341, 345-374, 378-380, 384-385, 407-409, 413-427, 435-456, 470-476 |
| ui/runs/views\_helper.py                                                |       52 |        9 |       22 |        4 |     80% |14->16, 20, 33, 36-42 |
|                                                               **TOTAL** | **4648** |  **848** | **1289** |  **192** | **78%** |           |


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