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
| protzilla/data\_analysis/differential\_expression\_anova.py         |       31 |        1 |        8 |        1 |     95% |        92 |
| protzilla/data\_analysis/differential\_expression\_helper.py        |        7 |        1 |        2 |        1 |     78% |        22 |
| protzilla/data\_analysis/differential\_expression\_linear\_model.py |       47 |        6 |       12 |        3 |     85% |56-57, 59-60, 85-87 |
| protzilla/data\_analysis/differential\_expression\_t\_test.py       |       59 |        0 |       18 |        0 |    100% |           |
| protzilla/data\_analysis/dimension\_reduction.py                    |       33 |        4 |       10 |        2 |     86% |67-72, 100, 179 |
| protzilla/data\_analysis/model\_evaluation.py                       |       10 |        0 |        0 |        0 |    100% |           |
| protzilla/data\_analysis/model\_evaluation\_plots.py                |       18 |        0 |        0 |        0 |    100% |           |
| protzilla/data\_analysis/plots.py                                   |      131 |       41 |       64 |        5 |     63% |75, 84->86, 131, 276, 306-313, 319-455 |
| protzilla/data\_analysis/protein\_graphs.py                         |      409 |       46 |      196 |       15 |     89% |32-40, 63-92, 148, 173-174, 188, 319-321, 330-332, 350-351, 400, 425-429, 473, 487, 556, 587, 594, 795, 853->852, 857-860 |
| protzilla/data\_integration/\_\_init\_\_.py                         |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/data\_integration/database\_download.py                   |       63 |       63 |       28 |        0 |      0% |     1-116 |
| protzilla/data\_integration/database\_integration.py                |       58 |       10 |       32 |        1 |     86% |73, 101-113 |
| protzilla/data\_integration/database\_query.py                      |       99 |       38 |       46 |        4 |     60% |26-70, 74-76, 80, 86-93, 119->118, 131-136, 137->144, 145-148 |
| protzilla/data\_integration/di\_plots.py                            |      124 |       21 |       58 |       11 |     82% |77, 106->109, 110, 176-177, 180-181, 183, 186-187, 215-217, 237-242, 295-296, 299, 373 |
| protzilla/data\_integration/enrichment\_analysis.py                 |      327 |       87 |      158 |       38 |     72% |23-24, 48->50, 177-178, 193->199, 203->209, 210-212, 214, 221, 250-254, 276-280, 328, 391-394, 409-410, 425-426, 530-533, 542-544, 548->562, 553, 555, 568-569, 581-591, 593->603, 595-596, 598-601, 603->616, 613-614, 617-627, 630-631, 647, 728-729, 738-739, 752-753, 755-756, 758-761, 765-766, 768-771, 784, 802-803, 815-816, 819-820, 830-833 |
| protzilla/data\_integration/enrichment\_analysis\_gsea.py           |      132 |        4 |       54 |        6 |     95% |155, 158, 220->224, 385, 388, 457->461 |
| protzilla/data\_integration/enrichment\_analysis\_helper.py         |       73 |        6 |       42 |        2 |     93% |137-139, 145, 150-151 |
| protzilla/data\_preprocessing/\_\_init\_\_.py                       |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/data\_preprocessing/filter\_proteins.py                   |       18 |        2 |        4 |        1 |     77% |     53-54 |
| protzilla/data\_preprocessing/filter\_samples.py                    |       35 |        0 |        4 |        0 |    100% |           |
| protzilla/data\_preprocessing/imputation.py                         |      115 |        1 |       22 |        3 |     97% |144, 493->506, 517->523 |
| protzilla/data\_preprocessing/normalisation.py                      |       98 |        1 |       22 |        2 |     98% |248->259, 260 |
| protzilla/data\_preprocessing/outlier\_detection.py                 |       67 |        3 |       12 |        4 |     89% |176, 193, 248, 249->exit |
| protzilla/data\_preprocessing/peptide\_filter.py                    |       16 |        2 |        4 |        1 |     75% |     50-51 |
| protzilla/data\_preprocessing/plots.py                              |      100 |       11 |       21 |        4 |     88% |165->180, 249-250, 286, 297, 397-421 |
| protzilla/data\_preprocessing/plots\_helper.py                      |       17 |       13 |        6 |        0 |     17% |15-24, 38-47 |
| protzilla/data\_preprocessing/transformation.py                     |       21 |        2 |        8 |        3 |     83% |33, 42->52, 53 |
| protzilla/history.py                                                |      134 |       11 |       60 |        7 |     91% |39, 113, 120, 130, 176-180, 222, 229 |
| protzilla/importing/\_\_init\_\_.py                                 |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/importing/metadata\_import.py                             |       64 |       21 |       28 |        7 |     63% |28-38, 45-47, 61, 88-95, 110, 118, 123-132, 162-163 |
| protzilla/importing/ms\_data\_import.py                             |      112 |       22 |       46 |        1 |     78% |28-29, 84-86, 113-115, 227-245 |
| protzilla/importing/peptide\_import.py                              |       22 |        2 |        2 |        0 |     92% |     15-16 |
| protzilla/run.py                                                    |      282 |       30 |      114 |       10 |     85% |75-81, 85-91, 149->160, 181, 183, 200->198, 236, 239, 283-284, 316-319, 362, 395, 399-402, 421, 433->406 |
| protzilla/run\_helper.py                                            |       66 |       18 |       52 |       12 |     69% |24, 35, 42, 52, 54, 56, 58-63, 65-67, 70-72, 73->76, 80, 89 |
| protzilla/runner.py                                                 |       89 |        4 |       38 |        3 |     94% |115, 124, 156-157 |
| protzilla/utilities/\_\_init\_\_.py                                 |        1 |        0 |        0 |        0 |    100% |           |
| protzilla/utilities/clustergram.py                                  |      375 |       99 |      194 |       55 |     67% |82, 97, 99, 106, 150-151, 153, 155, 161->164, 164->171, 190, 205, 209, 213, 217, 227, 231-236, 241->243, 244, 246, 248, 252->254, 254->258, 259-270, 273, 275, 277-296, 315-318, 321->323, 328->330, 331, 383-384, 386-387, 402-403, 405-406, 474->480, 486, 503, 523, 526->549, 531->534, 568->574, 574->587, 662->667, 675->679, 696, 698, 728-735, 744-757, 767-771, 825->842, 842->862, 894->902, 902->911, 929-941, 944-956, 982-998, 1012-1028 |
| protzilla/utilities/dunn\_score.py                                  |       10 |        6 |        6 |        0 |     25% | 25, 41-48 |
| protzilla/utilities/transform\_dfs.py                               |       25 |        0 |        9 |        0 |    100% |           |
| protzilla/utilities/utilities.py                                    |       40 |        4 |       10 |        2 |     88% |27-28, 69, 80 |
| protzilla/workflow\_helper.py                                       |       48 |        0 |       34 |        0 |    100% |           |
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
| ui/runs/fields.py                                                   |      118 |       98 |       66 |        0 |     11% |32-43, 61-89, 114-124, 137-139, 164-175, 189-194, 215-295, 312-323 |
| ui/runs/migrations/\_\_init\_\_.py                                  |        0 |        0 |        0 |        0 |    100% |           |
| ui/runs/templatetags/\_\_init\_\_.py                                |        0 |        0 |        0 |        0 |    100% |           |
| ui/runs/templatetags/id\_tags.py                                    |       10 |       10 |        4 |        0 |      0% |      1-13 |
| ui/runs/urls.py                                                     |        4 |        4 |        0 |        0 |      0% |       1-6 |
| ui/runs/utilities/\_\_init\_\_.py                                   |        0 |        0 |        0 |        0 |    100% |           |
| ui/runs/utilities/alert.py                                          |        2 |        1 |        0 |        0 |     50% |         2 |
| ui/runs/views.py                                                    |      332 |      276 |      118 |        0 |     13% |60, 85-125, 166-182, 213-234, 254-382, 395-402, 416-418, 433-435, 450-452, 467-476, 491-498, 513-521, 537-564, 582-611, 627-629, 645-646, 693-695, 711-726, 734-764, 783-798, 804-856 |
| ui/runs/views\_helper.py                                            |       53 |        9 |       22 |        4 |     80% |13->15, 19, 32, 35-41 |
|                                                           **TOTAL** | **4378** | **1208** | **1746** |  **221** | **70%** |           |


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