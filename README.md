# Repository Coverage



| Name                                                                |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|-------------------------------------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| \_\_init\_\_.py                                                     |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/\_\_init\_\_.py                                           |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/constants/\_\_init\_\_.py                                 |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/constants/colors.py                                       |        2 |        0 |        0 |        0 |    100% |           |
| protzilla/constants/location\_mapping.py                            |        7 |        0 |        2 |        0 |    100% |           |
| protzilla/constants/paths.py                                        |        8 |        0 |        0 |        0 |    100% |           |
| protzilla/constants/protzilla\_logging.py                           |       42 |       10 |       10 |        0 |     62% |46-47, 50-51, 54-55, 58-59, 62-63 |
| protzilla/data\_analysis/\_\_init\_\_.py                            |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/data\_analysis/classification.py                          |       65 |       32 |       12 |        4 |     48% |33-52, 54, 56-66, 67->exit, 263-313 |
| protzilla/data\_analysis/classification\_helper.py                  |       80 |       15 |       40 |        5 |     73% |41, 81-82, 103-114, 131, 166-169 |
| protzilla/data\_analysis/clustering.py                              |       69 |       11 |        6 |        2 |     83% |141, 365-380, 384-388 |
| protzilla/data\_analysis/differential\_expression.py                |        7 |        3 |        0 |        0 |     57% |      9-11 |
| protzilla/data\_analysis/differential\_expression\_anova.py         |       58 |       14 |       30 |        7 |     69% |70-72, 78->91, 81-87, 102-107, 110, 127-128, 139 |
| protzilla/data\_analysis/differential\_expression\_helper.py        |       27 |        2 |       10 |        2 |     89% |    43, 60 |
| protzilla/data\_analysis/differential\_expression\_linear\_model.py |       66 |       15 |       24 |        6 |     70% |56-57, 64-65, 83-89, 92, 132-138 |
| protzilla/data\_analysis/differential\_expression\_t\_test.py       |       64 |        2 |       24 |        2 |     95% |21, 76->80, 107 |
| protzilla/data\_analysis/dimension\_reduction.py                    |       33 |        4 |       10 |        2 |     86% |67-72, 100, 179 |
| protzilla/data\_analysis/model\_evaluation.py                       |       10 |        0 |        0 |        0 |    100% |           |
| protzilla/data\_analysis/model\_evaluation\_plots.py                |       18 |        0 |        0 |        0 |    100% |           |
| protzilla/data\_analysis/plots.py                                   |      131 |       41 |       64 |        5 |     63% |75, 84->86, 137, 282, 312-319, 325-461 |
| protzilla/data\_analysis/protein\_graphs.py                         |      409 |       46 |      196 |       15 |     89% |32-40, 63-92, 148, 173-174, 188, 319-321, 330-332, 350-351, 400, 425-429, 473, 487, 556, 587, 594, 795, 853->852, 857-860 |
| protzilla/data\_integration/\_\_init\_\_.py                         |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/data\_integration/database\_download.py                   |       63 |       63 |       28 |        0 |      0% |     1-116 |
| protzilla/data\_integration/database\_integration.py                |       58 |       10 |       32 |        1 |     86% |73, 101-113 |
| protzilla/data\_integration/database\_query.py                      |       99 |       44 |       46 |       17 |     44% |26-70, 74-76, 80, 86-93, 119->118, 127->151, 131-136, 142->exit, 143, 146, 151->152, 151->154, 169-173, 193->194, 193->196, 194->193, 201->exit, 202->exit, 203, 207->200, 208-209 |
| protzilla/data\_integration/di\_plots.py                            |      124 |       21 |       58 |       11 |     82% |77, 106->109, 110, 176-177, 180-181, 183, 186-187, 215-217, 237-242, 295-296, 299, 373 |
| protzilla/data\_integration/enrichment\_analysis.py                 |      327 |       87 |      158 |       38 |     72% |23-24, 48->50, 177-178, 193->199, 203->209, 210-212, 214, 221, 250-254, 276-280, 328, 391-394, 409-410, 425-426, 530-533, 542-544, 548->562, 553, 555, 568-569, 581-591, 593->603, 595-596, 598-601, 603->616, 613-614, 617-627, 630-631, 647, 728-729, 738-739, 752-753, 755-756, 758-761, 765-766, 768-771, 784, 802-803, 815-816, 819-820, 830-833 |
| protzilla/data\_integration/enrichment\_analysis\_gsea.py           |      132 |        4 |       54 |        6 |     95% |155, 158, 220->224, 385, 388, 457->461 |
| protzilla/data\_integration/enrichment\_analysis\_helper.py         |       73 |        6 |       42 |        2 |     93% |137-139, 145, 150-151 |
| protzilla/data\_preprocessing/\_\_init\_\_.py                       |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/data\_preprocessing/filter\_proteins.py                   |       18 |        2 |        4 |        1 |     77% |     53-54 |
| protzilla/data\_preprocessing/filter\_samples.py                    |       35 |        0 |        4 |        0 |    100% |           |
| protzilla/data\_preprocessing/imputation.py                         |      131 |        3 |       30 |        4 |     96% |47-53, 180, 517->530, 541->547 |
| protzilla/data\_preprocessing/normalisation.py                      |       98 |        1 |       22 |        2 |     98% |248->259, 260 |
| protzilla/data\_preprocessing/outlier\_detection.py                 |       67 |        3 |       12 |        4 |     89% |176, 193, 248, 249->exit |
| protzilla/data\_preprocessing/peptide\_filter.py                    |       16 |        2 |        4 |        1 |     75% |     50-51 |
| protzilla/data\_preprocessing/plots.py                              |       97 |       11 |       21 |        4 |     87% |165->180, 249-250, 283, 294, 394-418 |
| protzilla/data\_preprocessing/plots\_helper.py                      |       17 |       13 |        6 |        0 |     17% |15-24, 38-47 |
| protzilla/data\_preprocessing/transformation.py                     |       21 |        2 |        8 |        3 |     83% |33, 42->52, 53 |
| protzilla/history.py                                                |      135 |       10 |       60 |        6 |     92% |39, 123, 133, 179-183, 226, 233 |
| protzilla/importing/\_\_init\_\_.py                                 |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/importing/metadata\_import.py                             |       64 |       15 |       28 |        7 |     76% |29, 31, 45-47, 91-98, 113, 124, 129-138, 168-169 |
| protzilla/importing/ms\_data\_import.py                             |      115 |       22 |       48 |        1 |     79% |28-29, 88-90, 117-119, 231-249 |
| protzilla/importing/peptide\_import.py                              |       22 |        2 |        2 |        0 |     92% |     15-16 |
| protzilla/run.py                                                    |      329 |       61 |      125 |       18 |     75% |75-81, 85-91, 151->162, 183, 185, 193-196, 202-205, 253-259, 263, 266, 325-326, 411, 425->444, 436, 440, 443, 448->451, 449-450, 453-457, 462->491, 468, 471, 474-476, 479-488, 489->462, 490, 502 |
| protzilla/run\_helper.py                                            |       95 |       34 |       74 |       15 |     60% |25, 28-45, 48-55, 66, 73, 83, 85, 87, 89-94, 96-98, 101-103, 104->107, 120, 158->exit, 170 |
| protzilla/runner.py                                                 |       89 |        4 |       38 |        4 |     94% |115, 124, 142->140, 156-157 |
| protzilla/utilities/\_\_init\_\_.py                                 |        1 |        0 |        0 |        0 |    100% |           |
| protzilla/utilities/clustergram.py                                  |      375 |       99 |      194 |       55 |     67% |82, 97, 99, 106, 150-151, 153, 155, 161->164, 164->171, 190, 205, 209, 213, 217, 227, 231-236, 241->243, 244, 246, 248, 252->254, 254->258, 259-270, 273, 275, 277-296, 315-318, 321->323, 328->330, 331, 383-384, 386-387, 402-403, 405-406, 474->480, 486, 503, 523, 526->549, 531->534, 568->574, 574->587, 662->667, 675->679, 696, 698, 728-735, 744-757, 767-771, 825->842, 842->862, 894->902, 902->911, 929-941, 944-956, 982-998, 1012-1028 |
| protzilla/utilities/dunn\_score.py                                  |       10 |        6 |        6 |        0 |     25% | 25, 41-48 |
| protzilla/utilities/transform\_dfs.py                               |       25 |        0 |        9 |        0 |    100% |           |
| protzilla/utilities/utilities.py                                    |       42 |        4 |       12 |        2 |     89% |27-28, 69, 80 |
| protzilla/workflow\_helper.py                                       |       58 |       14 |       36 |       20 |     62% |26-28, 37, 41, 46, 50->exit, 50->exit, 57, 65->66, 65->67, 67->70, 68, 71, 76-88, 94, 96->102, 106, 112->111, 113->112, 115->112, 118->115, 119->120, 123 |
| runner\_cli.py                                                      |       21 |        5 |        2 |        1 |     74% | 55-58, 62 |
| ui/\_\_init\_\_.py                                                  |        0 |        0 |        0 |        0 |    100% |           |
| ui/\_\_main\_\_.py                                                  |       11 |       11 |        2 |        0 |      0% |      2-21 |
| ui/main/\_\_init\_\_.py                                             |        0 |        0 |        0 |        0 |    100% |           |
| ui/main/asgi.py                                                     |        4 |        4 |        0 |        0 |      0% |     10-16 |
| ui/main/settings.py                                                 |       28 |        0 |        2 |        1 |     97% |    24->32 |
| ui/main/upload\_handler.py                                          |       37 |       37 |        2 |        0 |      0% |      1-73 |
| ui/main/urls.py                                                     |        4 |        4 |        0 |        0 |      0% |     16-21 |
| ui/main/views.py                                                    |       76 |       76 |       32 |        0 |      0% |     1-115 |
| ui/main/wsgi.py                                                     |        4 |        4 |        0 |        0 |      0% |     10-16 |
| ui/manage.py                                                        |       14 |       14 |        2 |        0 |      0% |      2-24 |
| ui/runs/\_\_init\_\_.py                                             |        0 |        0 |        0 |        0 |    100% |           |
| ui/runs/apps.py                                                     |        4 |        4 |        0 |        0 |      0% |       1-6 |
| ui/runs/fields.py                                                   |      128 |      108 |       76 |        0 |     10% |35-46, 64-97, 122-132, 145-147, 172-183, 197-202, 223-303, 320-345 |
| ui/runs/migrations/\_\_init\_\_.py                                  |        0 |        0 |        0 |        0 |    100% |           |
| ui/runs/templatetags/\_\_init\_\_.py                                |        0 |        0 |        0 |        0 |    100% |           |
| ui/runs/templatetags/id\_tags.py                                    |       10 |       10 |        4 |        0 |      0% |      1-13 |
| ui/runs/urls.py                                                     |        4 |        4 |        0 |        0 |      0% |       1-6 |
| ui/runs/utilities/\_\_init\_\_.py                                   |        0 |        0 |        0 |        0 |    100% |           |
| ui/runs/utilities/alert.py                                          |        2 |        1 |        0 |        0 |     50% |         2 |
| ui/runs/views.py                                                    |      344 |      309 |      134 |        2 |      7% |59, 84-124, 166-182, 213-234, 254-655, 677, 680, 683-862 |
| ui/runs/views\_helper.py                                            |       63 |       14 |       26 |        4 |     75% |16->18, 22, 35, 38-44, 116-124, 138-139 |
|                                                           **TOTAL** | **4586** | **1343** | **1871** |  **280** | **67%** |           |


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