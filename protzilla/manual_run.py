from protzilla.importing.ms_data_import import max_quant_import


def start():
    print(max_quant_import("",**{'intensity_name': 'iBAQ',
                      'file_path': 'C:\\Users\\Dell\\Documents\\Übungen\\BP\\ExampleData\\MaxQuant_BA39_INSOLUBLE\\proteinGroups.txt'}))
