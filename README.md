# Repository Coverage



| Name                                                                |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|-------------------------------------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| \_\_init\_\_.py                                                     |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/\_\_init\_\_.py                                           |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/constants/\_\_init\_\_.py                                 |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/constants/colors.py                                       |        2 |        0 |        0 |        0 |    100% |           |
| protzilla/constants/location\_mapping.py                            |        7 |        0 |        0 |        0 |    100% |           |
| protzilla/constants/paths.py                                        |        8 |        0 |        0 |        0 |    100% |           |
| protzilla/constants/protzilla\_logging.py                           |       42 |       10 |       10 |        0 |     62% |46-47, 50-51, 54-55, 58-59, 62-63 |
| protzilla/data\_analysis/\_\_init\_\_.py                            |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/data\_analysis/classification.py                          |       65 |       32 |        8 |        4 |     51% |33-52, 54, 56-66, 67->exit, 263-313 |
| protzilla/data\_analysis/classification\_helper.py                  |       82 |       15 |       32 |        5 |     72% |41, 81-82, 104-115, 132, 167-170 |
| protzilla/data\_analysis/clustering.py                              |       69 |       11 |        6 |        2 |     83% |141, 365-380, 384-388 |
| protzilla/data\_analysis/differential\_expression.py                |        7 |        3 |        0 |        0 |     57% |      9-11 |
| protzilla/data\_analysis/differential\_expression\_anova.py         |       58 |       14 |       26 |        7 |     70% |70-72, 78->91, 81-87, 102-107, 110, 127-128, 139 |
| protzilla/data\_analysis/differential\_expression\_helper.py        |       27 |        3 |       10 |        3 |     84% |43, 63, 71 |
| protzilla/data\_analysis/differential\_expression\_linear\_model.py |       66 |       15 |       22 |        6 |     69% |56-57, 64-65, 83-89, 92, 132-138 |
| protzilla/data\_analysis/differential\_expression\_t\_test.py       |       66 |        2 |       24 |        3 |     94% |21, 77->81, 100->103, 108 |
| protzilla/data\_analysis/dimension\_reduction.py                    |       33 |        4 |       10 |        2 |     86% |67-72, 100, 179 |
| protzilla/data\_analysis/model\_evaluation.py                       |       10 |        0 |        0 |        0 |    100% |           |
| protzilla/data\_analysis/model\_evaluation\_plots.py                |       19 |        0 |        0 |        0 |    100% |           |
| protzilla/data\_analysis/plots.py                                   |      135 |        9 |       56 |        9 |     90% |79, 88->90, 141, 294, 325, 331, 377, 385-386, 401 |
| protzilla/data\_analysis/protein\_graphs.py                         |      412 |       37 |      208 |       18 |     90% |32-40, 157, 163-166, 169-172, 177, 209-210, 224, 297-299, 308-310, 328-329, 378, 404-408, 452, 466, 535, 566, 573, 774, 832->831, 836-839 |
| protzilla/data\_integration/\_\_init\_\_.py                         |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/data\_integration/database\_download.py                   |       63 |       63 |       26 |        0 |      0% |     1-116 |
| protzilla/data\_integration/database\_integration.py                |       62 |       14 |       28 |        1 |     81% |73, 102-137 |
| protzilla/data\_integration/database\_query.py                      |      115 |       44 |       52 |        7 |     59% |27-80, 84-86, 90, 103->exit, 104->103, 107->104, 111-112, 116-123, 149->148, 161-166, 167->176, 177-180 |
| protzilla/data\_integration/di\_plots.py                            |      124 |       21 |       58 |       11 |     82% |77, 106->109, 110, 176-177, 180-181, 183, 186-187, 215-217, 237-242, 295-296, 299, 373 |
| protzilla/data\_integration/enrichment\_analysis.py                 |      342 |       91 |      168 |       37 |     72% |24-25, 182-183, 198->204, 208->214, 215-217, 219, 226, 281-285, 333, 396-399, 414-415, 430-431, 537-540, 549-550, 555-557, 561->582, 566, 569-575, 588-589, 601-611, 613->623, 615-616, 618-621, 623->636, 633-634, 637-647, 650-651, 667, 748-749, 758-759, 772-773, 775-776, 778-781, 785-786, 788-791, 804, 822-823, 835-836, 839-840, 850-853 |
| protzilla/data\_integration/enrichment\_analysis\_gsea.py           |      132 |        4 |       54 |        6 |     95% |155, 158, 222->226, 387, 390, 461->465 |
| protzilla/data\_integration/enrichment\_analysis\_helper.py         |       73 |        6 |       34 |        2 |     93% |137-139, 145, 150-151 |
| protzilla/data\_preprocessing/\_\_init\_\_.py                       |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/data\_preprocessing/filter\_proteins.py                   |       18 |        2 |        4 |        1 |     77% |     53-54 |
| protzilla/data\_preprocessing/filter\_samples.py                    |       35 |        0 |        4 |        0 |    100% |           |
| protzilla/data\_preprocessing/imputation.py                         |      131 |        3 |       30 |        4 |     96% |47-53, 180, 517->530, 541->547 |
| protzilla/data\_preprocessing/normalisation.py                      |       98 |        1 |       22 |        2 |     98% |250->261, 262 |
| protzilla/data\_preprocessing/outlier\_detection.py                 |       67 |        3 |        8 |        4 |     91% |176, 193, 248, 249->exit |
| protzilla/data\_preprocessing/peptide\_filter.py                    |       16 |        2 |        4 |        1 |     75% |     50-51 |
| protzilla/data\_preprocessing/plots.py                              |      101 |       11 |       23 |        4 |     88% |164->179, 248-249, 283, 294, 394-418 |
| protzilla/data\_preprocessing/plots\_helper.py                      |       17 |       13 |        6 |        0 |     17% |15-24, 38-47 |
| protzilla/data\_preprocessing/transformation.py                     |       21 |        2 |        8 |        3 |     83% |33, 42->52, 53 |
| protzilla/history.py                                                |      135 |       10 |       60 |        6 |     92% |40, 124, 134, 180-184, 227, 234 |
| protzilla/importing/\_\_init\_\_.py                                 |        0 |        0 |        0 |        0 |    100% |           |
| protzilla/importing/metadata\_import.py                             |       64 |       15 |       28 |        7 |     76% |29, 31, 45-47, 91-98, 113, 124, 129-138, 168-169 |
| protzilla/importing/ms\_data\_import.py                             |      115 |       22 |       40 |        1 |     77% |28-29, 89-91, 119-121, 233-251 |
| protzilla/importing/peptide\_import.py                              |       22 |        2 |        0 |        0 |     91% |     15-16 |
| protzilla/run.py                                                    |      360 |       54 |      140 |       11 |     83% |77-83, 87-93, 171->182, 203, 205, 240-244, 293-299, 309, 324-337, 376-377, 414-417, 449->exit, 495, 535, 539-544, 548-551, 570, 582->555 |
| protzilla/run\_helper.py                                            |      100 |       24 |       74 |       15 |     73% |28, 47-48, 53, 58, 69, 75, 81, 88, 92-97, 99-101, 104-106, 111, 126, 141-143, 171->exit, 184 |
| protzilla/runner.py                                                 |       93 |        4 |       36 |        4 |     94% |121, 130, 148->146, 162-163 |
| protzilla/utilities/\_\_init\_\_.py                                 |        1 |        0 |        0 |        0 |    100% |           |
| protzilla/utilities/clustergram.py                                  |      375 |       99 |      168 |       55 |     67% |82, 97, 99, 106, 150-151, 153, 155, 161->164, 164->171, 190, 205, 209, 213, 217, 227, 231-236, 241->243, 244, 246, 248, 252->254, 254->258, 259-270, 273, 275, 277-296, 315-318, 321->323, 328->330, 331, 383-384, 386-387, 402-403, 405-406, 474->480, 486, 503, 523, 526->549, 531->534, 568->574, 574->587, 662->667, 675->679, 696, 698, 728-735, 744-757, 767-771, 825->842, 842->862, 894->902, 902->911, 929-941, 944-956, 982-998, 1012-1028 |
| protzilla/utilities/dunn\_score.py                                  |       10 |        6 |        0 |        0 |     40% | 25, 41-48 |
| protzilla/utilities/transform\_dfs.py                               |       25 |        0 |        9 |        0 |    100% |           |
| protzilla/utilities/utilities.py                                    |       44 |        4 |       10 |        2 |     89% |27-28, 69, 80 |
| protzilla/workflow\_helper.py                                       |       65 |        0 |       36 |        0 |    100% |           |
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
| ui/runs/fields.py                                                   |      128 |      108 |       74 |        0 |     10% |35-46, 64-97, 122-132, 145-147, 172-183, 197-202, 223-303, 320-345 |
| ui/runs/migrations/\_\_init\_\_.py                                  |        0 |        0 |        0 |        0 |    100% |           |
| ui/runs/templatetags/\_\_init\_\_.py                                |        0 |        0 |        0 |        0 |    100% |           |
| ui/runs/templatetags/id\_tags.py                                    |       10 |       10 |        4 |        0 |      0% |      1-13 |
| ui/runs/urls.py                                                     |        4 |        4 |        0 |        0 |      0% |       1-6 |
| ui/runs/utilities/\_\_init\_\_.py                                   |        0 |        0 |        0 |        0 |    100% |           |
| ui/runs/utilities/alert.py                                          |        2 |        1 |        0 |        0 |     50% |         2 |
| ui/runs/views.py                                                    |      348 |      289 |      124 |        1 |     13% |59, 84-131, 173-189, 220-241, 261-407, 420-427, 441-444, 459-463, 478-480, 492-494, 509-518, 533-540, 555-563, 579-588, 606-615, 631-633, 646-650, 666-667, 714-716, 732-747, 755-785, 804-819, 825-877 |
| ui/runs/views\_helper.py                                            |       70 |       20 |       28 |        4 |     67% |16->18, 22, 35, 38-44, 116-130, 145-146, 155-158 |
|                                                           **TOTAL** | **4697** | **1266** | **1814** |  **250** | **70%** |           |


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