# Repository Coverage



| Name                                                                |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|-------------------------------------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| \_\_init\_\_.py                                                     |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/\_\_init\_\_.py                                           |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/constants/\_\_init\_\_.py                                 |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/constants/colors.py                                       |        2 |        0 |        0 |        0 |    100% |           |
| protzilla/constants/location\_mapping.py                            |        9 |        0 |        2 |        0 |    100% |           |
| protzilla/constants/logging.py                                      |       43 |       10 |       10 |        0 |     62% |47-48, 51-52, 55-56, 59-60, 63-64 |
| protzilla/constants/paths.py                                        |        8 |        0 |        0 |        0 |    100% |           |
| protzilla/data\_analysis/\_\_init\_\_.py                            |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/data\_analysis/classification.py                          |       65 |       32 |       12 |        4 |     48% |33-52, 54, 56-66, 67->exit, 220-270 |
| protzilla/data\_analysis/classification\_helper.py                  |       80 |       15 |       40 |        5 |     73% |41, 81-82, 103-114, 131, 166-169 |
| protzilla/data\_analysis/clustering.py                              |       69 |       11 |        6 |        2 |     83% |140, 362-377, 381-385 |
| protzilla/data\_analysis/differential\_expression.py                |        7 |        3 |        0 |        0 |     57% |      9-11 |
| protzilla/data\_analysis/differential\_expression\_anova.py         |       30 |        1 |        8 |        1 |     95% |        87 |
| protzilla/data\_analysis/differential\_expression\_helper.py        |        7 |        1 |        2 |        1 |     78% |        22 |
| protzilla/data\_analysis/differential\_expression\_linear\_model.py |       47 |        6 |       12 |        3 |     85% |52-53, 55-56, 81-83 |
| protzilla/data\_analysis/differential\_expression\_t\_test.py       |       59 |        0 |       18 |        0 |    100% |           |
| protzilla/data\_analysis/dimension\_reduction.py                    |       33 |        4 |       10 |        2 |     86% |61-66, 94, 165 |
| protzilla/data\_analysis/model\_evaluation.py                       |       10 |        0 |        0 |        0 |    100% |           |
| protzilla/data\_analysis/model\_evaluation\_plots.py                |       18 |        0 |        0 |        0 |    100% |           |
| protzilla/data\_analysis/plots.py                                   |       77 |        3 |       36 |        4 |     94% |55, 64->66, 106, 255 |
| protzilla/data\_analysis/protein\_graphs.py                         |      392 |       30 |      194 |       15 |     92% |32-40, 148, 173-174, 188, 261-263, 272-274, 292-293, 342, 367-371, 415, 429, 497, 528, 535, 734, 792->791, 796-799 |
| protzilla/data\_integration/database\_integration.py                |       58 |       10 |       32 |        1 |     86% | 59, 71-83 |
| protzilla/data\_integration/database\_query.py                      |       99 |       38 |       46 |        4 |     60% |13-57, 61-63, 67, 73-80, 101->100, 113-118, 119->126, 127-130 |
| protzilla/data\_integration/di\_plots.py                            |      124 |       21 |       58 |       11 |     82% |75, 104->107, 108, 173-174, 177-178, 180, 183-184, 212-214, 234-239, 291-292, 295, 368 |
| protzilla/data\_integration/enrichment\_analysis.py                 |      327 |       87 |      158 |       38 |     72% |23-24, 46->48, 173-174, 189->195, 199->205, 206-208, 210, 217, 246-250, 272-276, 323, 385-388, 403-404, 419-420, 523-526, 535-537, 541->555, 546, 548, 561-562, 574-584, 586->596, 588-589, 591-594, 596->609, 606-607, 610-620, 623-624, 640, 720-721, 730-731, 744-745, 747-748, 750-753, 757-758, 760-763, 776, 794-795, 807-808, 811-812, 822-825 |
| protzilla/data\_integration/enrichment\_analysis\_gsea.py           |      131 |        4 |       54 |        6 |     95% |151, 154, 216->220, 379, 382, 451->455 |
| protzilla/data\_integration/enrichment\_analysis\_helper.py         |       73 |        6 |       42 |        2 |     93% |132-134, 140, 145-146 |
| protzilla/data\_preprocessing/\_\_init\_\_.py                       |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/data\_preprocessing/filter\_proteins.py                   |       17 |        2 |        4 |        1 |     76% |     51-52 |
| protzilla/data\_preprocessing/filter\_samples.py                    |       34 |        0 |        4 |        0 |    100% |           |
| protzilla/data\_preprocessing/imputation.py                         |      110 |        1 |       20 |        3 |     97% |140, 401->410, 420->426 |
| protzilla/data\_preprocessing/normalisation.py                      |       97 |        1 |       22 |        2 |     97% |244->255, 256 |
| protzilla/data\_preprocessing/outlier\_detection.py                 |       67 |        3 |       12 |        4 |     89% |172, 189, 244, 245->exit |
| protzilla/data\_preprocessing/peptide\_filter.py                    |       16 |        2 |        4 |        1 |     75% |     50-51 |
| protzilla/data\_preprocessing/plots.py                              |       71 |        7 |        9 |        1 |     90% |176->191, 368-392 |
| protzilla/data\_preprocessing/transformation.py                     |       20 |        2 |        8 |        3 |     82% |31, 40->49, 50 |
| protzilla/history.py                                                |      134 |       11 |       60 |        7 |     91% |35, 109, 116, 126, 172-176, 218, 225 |
| protzilla/importing/metadata\_import.py                             |       64 |       21 |       28 |        7 |     63% |28-38, 45-47, 61, 88-95, 110, 118, 123-132, 162-163 |
| protzilla/importing/ms\_data\_import.py                             |      110 |       22 |       52 |        4 |     77% |17-18, 32-33, 56-57, 90-91, 221-239 |
| protzilla/importing/peptide\_import.py                              |       22 |        2 |        2 |        0 |     92% |     15-16 |
| protzilla/run.py                                                    |      282 |       30 |      114 |       10 |     85% |47-53, 57-63, 121->132, 153, 155, 172->170, 208, 211, 255-256, 288-291, 334, 367, 371-374, 393, 405->378 |
| protzilla/run\_helper.py                                            |       64 |       24 |       50 |        6 |     58% |24, 35, 42, 51-72, 78, 87 |
| protzilla/runner.py                                                 |       89 |        4 |       38 |        3 |     94% |115, 124, 156-157 |
| protzilla/utilities/\_\_init\_\_.py                                 |        1 |        0 |        0 |        0 |    100% |           |
| protzilla/utilities/clustergram.py                                  |      375 |       99 |      194 |       55 |     67% |69, 84, 86, 93, 137-138, 140, 142, 148->151, 151->158, 177, 192, 196, 200, 204, 214, 218-223, 228->230, 231, 233, 235, 239->241, 241->245, 246-257, 260, 262, 264-283, 302-305, 308->310, 315->317, 318, 370-371, 373-374, 389-390, 392-393, 461->467, 473, 490, 510, 513->536, 518->521, 555->561, 561->574, 649->654, 662->666, 683, 685, 715-722, 731-744, 754-758, 812->829, 829->849, 881->889, 889->898, 916-928, 931-943, 969-985, 999-1015 |
| protzilla/utilities/dunn\_score.py                                  |       10 |        6 |        6 |        0 |     25% | 25, 40-47 |
| protzilla/utilities/transform\_dfs.py                               |       24 |        0 |        9 |        0 |    100% |           |
| protzilla/utilities/utilities.py                                    |       26 |        2 |        4 |        0 |     93% |     25-26 |
| protzilla/workflow\_helper.py                                       |       52 |        0 |       34 |        0 |    100% |           |
| runner\_cli.py                                                      |       21 |        5 |        2 |        1 |     74% | 55-58, 62 |
| ui/\_\_init\_\_.py                                                  |        0 |        0 |        0 |        0 |    100% |           |
| ui/\_\_main\_\_.py                                                  |       11 |       11 |        2 |        0 |      0% |      2-21 |
| ui/main/\_\_init\_\_.py                                             |        0 |        0 |        0 |        0 |    100% |           |
| ui/main/asgi.py                                                     |        4 |        4 |        0 |        0 |      0% |     10-16 |
| ui/main/settings.py                                                 |       28 |        0 |        2 |        1 |     97% |    24->32 |
| ui/main/upload\_handler.py                                          |       37 |       37 |        2 |        0 |      0% |      1-69 |
| ui/main/urls.py                                                     |        4 |        4 |        0 |        0 |      0% |     16-21 |
| ui/main/views.py                                                    |       76 |       76 |       32 |        0 |      0% |     1-115 |
| ui/main/wsgi.py                                                     |        4 |        4 |        0 |        0 |      0% |     10-16 |
| ui/manage.py                                                        |       14 |       14 |        2 |        0 |      0% |      2-24 |
| ui/runs/\_\_init\_\_.py                                             |        0 |        0 |        0 |        0 |    100% |           |
| ui/runs/apps.py                                                     |        4 |        4 |        0 |        0 |      0% |       1-6 |
| ui/runs/fields.py                                                   |      116 |       98 |       66 |        0 |     10% |16-27, 35-63, 74-84, 88-90, 103-114, 118-123, 136-214, 218-229 |
| ui/runs/migrations/\_\_init\_\_.py                                  |        0 |        0 |        0 |        0 |    100% |           |
| ui/runs/templatetags/\_\_init\_\_.py                                |        0 |        0 |        0 |        0 |    100% |           |
| ui/runs/templatetags/id\_tags.py                                    |       10 |       10 |        4 |        0 |      0% |      1-13 |
| ui/runs/urls.py                                                     |        4 |        4 |        0 |        0 |      0% |       1-6 |
| ui/runs/utilities/alert.py                                          |        2 |        1 |        0 |        0 |     50% |         2 |
| ui/runs/views.py                                                    |      320 |      264 |      112 |        0 |     13% |46, 57-96, 124-140, 156-177, 181-309, 313-320, 324-326, 330-332, 336-338, 342-351, 355-362, 366-374, 378-405, 409-438, 442-444, 448-449, 471-473, 477-492, 500-530, 549-564, 570-606 |
| ui/runs/views\_helper.py                                            |       52 |        9 |       22 |        4 |     80% |14->16, 20, 33, 36-42 |
|                                                           **TOTAL** | **4160** | **1066** | **1660** |  **212** | **72%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://github.com/cschlaffner/PROTzilla2/raw/python-coverage-comment-action-data/badge.svg)](https://github.com/cschlaffner/PROTzilla2/tree/python-coverage-comment-action-data)

This is the one to use if your repository is private or if you don't want to customize anything.



## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.