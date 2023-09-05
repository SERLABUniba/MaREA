import pandas as pd
import os
import json
import numpy as np


def load_dataset(path, d_name):
    """
    Load the dataframe using Pandas read_csv
    Parameters
    ----------
    path: The path of the dataset
    d_name: the dataset name

    Returns
    -------
    The dataframe loaded with the attributes
    """

    if d_name == 'Fabrication':
        type_names = {
            'Timestamp': float,
            'CAN_ID': str,
            'DLC': int,
            'DATA[0]': str,
            'DATA[1]': str,
            'DATA[2]': str,
            'DATA[3]': str,
            'DATA[4]': str,
            'DATA[5]': str,
            'DATA[6]': str,
            'DATA[7]': str,
        }
        dataframe = pd.read_csv(path,
                                names=['Timestamp', 'CAN_ID', 'DLC', 'DATA[0]', 'DATA[1]', 'DATA[2]',
                                       'DATA[3]', 'DATA[4]', 'DATA[5]', 'DATA[6]', 'DATA[7]', 'Flag'],
                                header=None,
                                dtype=type_names
                                )

    else:
        type_names = {
            'Timestamp': float,
            'CAN_ID': str,
            'DLC': int,
            'DATA[0]': str,
            'DATA[1]': str,
            'DATA[2]': str,
            'DATA[3]': str,
            'DATA[4]': str,
            'DATA[5]': str,
            'DATA[6]': str,
            'DATA[7]': str,
            'Flag': str
        }

        dataframe = pd.read_csv(path,
                                names=['Timestamp', 'CAN_ID', 'DLC', 'DATA[0]', 'DATA[1]', 'DATA[2]',
                                       'DATA[3]', 'DATA[4]', 'DATA[5]', 'DATA[6]', 'DATA[7]', 'Flag'],
                                header=None,
                                dtype=type_names
                                )
    return dataframe


def clear_dataset(dataframe):
    """
    Clear the CAN ID "01E5" became "1E5".
    Parameters
    ----------
    dataframe pandas.DataFrame
    name_dataset the name of processing dataset

    Returns
    -------
    """

    dataframe['CAN_ID'] = dataframe['CAN_ID'].str[1:]

    return dataframe


def drop_features(dataframe):
    """
    Drop the Timestamp, CAN_ID, and DLC features
    Parameters
    ----------
    dataframe the dataframe to be processed

    Returns
    -------
    The dataframe
    """
    dataframe.drop('Timestamp', inplace=True, axis=1)
    dataframe.drop('CAN_ID', inplace=True, axis=1)
    dataframe.drop('DLC', inplace=True, axis=1)

    return dataframe


def convert_data_features(dataframe):
    """
    Convert the DATA into a decimal form
    Parameters
    ----------
    dataframe the dataframe to be processed

    Returns
    -------
    The dataframe with the converted DATA
    """

    for i in range(0, 8):
        dataframe['DATA[' + str(i) + ']'] = dataframe['DATA[' + str(i) + ']'].apply(int, base=16)

    return dataframe


def convert_can_id_to_binary(row):
    """
    Convert the CAN ID into a binary form.
    Parameters
    ----------
    row the processing dataset row

    Returns
    -------
    The converted ID
    """
    bin_st = bin(int(row.CAN_ID, 16))[2:].zfill(11)

    return bin_st[0], bin_st[1], bin_st[2], bin_st[3], bin_st[4], bin_st[5], bin_st[6], bin_st[7], bin_st[8], \
        bin_st[9], bin_st[10]


def padding_data_payload(dataframe, label=None):
    """
    Perform the padding in the DATA attributes.
    If the DLC in < 8, the algorithm add '00' in the remain attributes.

    Parameters
    ----------
    dataframe: the dataframe to be processed
    label: the label name

    Returns
    -------
    The converted dataframe
    """

    where_are = np.where(dataframe['DLC'] < 8)

    for i in where_are[0]:
        dlc = dataframe.loc[i]['DLC']
        get_flag = dataframe.loc[i][
            'DATA[' + str(dlc) + ']']
        dataframe.loc.__setitem__((i, label), get_flag)
        dataframe.loc.__setitem__((i, 'DATA[' + str(dlc) + ']'), str('00'))
        dataframe.loc[i] = dataframe.loc[i].fillna(str('00'))

    del where_are

    return dataframe


def pad_dataset(dataset, name_dataset=None, save_path=None):
    """
    Call the padding_data_payload and create a new dataset padded.
    Parameters
    ----------
    dataset: dataset to be processed
    name_dataset: the dataset name
    save_path: PATH where the dataset will be saved

    Returns
    -------
    dataframe padded

    """

    print("[+] Padding dataset. It may take several minutes...")
    dataframe = padding_data_payload(dataset, 'Flag')

    if save_path is not None:
        print("[+] Saving dataset padded...")
        if name_dataset is None:
            raise ValueError('Name dataset is mandatory!')
        else:
            to_csv_dataframe = name_dataset + '_PADDED.csv'
            create_path = os.path.join(save_path, to_csv_dataframe)
            dataframe.to_csv(create_path, index=False)
    return dataframe


def init_preprocessing():
    """
    Perform the preprocessing phase

    Returns
    -------
    The concatenated dataframe
    """

    configuration = json.load(open('configuration.json', 'r'))

    concatenated_dataset = None
    i = 1

    if configuration["DATASETS"]["SURVIVAL_ANALYSIS_AND_FABRICATION"]:
        list_datasets = ['Flooding_dataset_KIA', 'Fuzzy_dataset_KIA', 'Malfunction153_dataset_KIA', 'Fabrication']
    elif configuration["DATASETS"]["CAR_HACKING"]:
        list_datasets = ['DoS_dataset', 'Fuzzy_dataset', 'gear_dataset', 'RPM_dataset']
    else:
        raise Exception("The dataset is not implemented or at least one of the two datasets must be selected.")

    for df in list_datasets:

        print(f'[+] Processing dataset: {df}')

        dataset_path = os.path.join(configuration['DIRECTORY_DATASET'], df + '.csv')

        dataframe = load_dataset(dataset_path, df)

        if df != 'Fabrication':
            dataframe = clear_dataset(dataframe)

        dataframe = pad_dataset(dataframe, df.split('_')[0] + '_dataset',
                                configuration["DIRECTORY_SAVED_DATASET_PADDED"])

        dataframe = convert_data_features(dataframe)

        dataframe[['CAN_ID_0', 'CAN_ID_1', 'CAN_ID_2', 'CAN_ID_3', 'CAN_ID_4',
                   'CAN_ID_5', 'CAN_ID_6', 'CAN_ID_7', 'CAN_ID_8', 'CAN_ID_9', 'CAN_ID_10'
                   ]] = dataframe.apply(convert_can_id_to_binary, axis=1, result_type='expand')

        dataframe = drop_features(dataframe)
        
        cols_at_end = dataframe.pop('Flag')

        dataframe.insert(len(dataframe.columns), 'Flag', cols_at_end)

        if df != 'Fabrication':
            dataframe['Flag'] = dataframe['Flag'].map({'R': 0, 'T': int(i)})
        else:
            dataframe['Flag'] = [i if x == 1 else 0 for x in dataframe['Flag'].values]

        dataframe = dataframe.iloc[:, [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 0, 1, 2, 3, 4, 5, 6, 7, 19]]

        #  get the majority class and then remove random sample to balance the dataset
        get_number_non_attack_class = len(dataframe.index[dataframe['Flag'] == 0].tolist())
        get_number_attack_class = len(dataframe.index[dataframe['Flag'] == i].tolist())

        if get_number_non_attack_class > get_number_attack_class:
            majority = 0
            remove_elements = get_number_non_attack_class - get_number_attack_class
        else:
            majority = i
            remove_elements = get_number_attack_class - get_number_non_attack_class

        # random_state to reproduce the experiments
        dataframe.drop(dataframe[dataframe['Flag'] == majority].sample(n=remove_elements, random_state=42).index,
                       inplace=True)

        if concatenated_dataset is None:
            concatenated_dataset = pd.concat([dataframe], axis=0)
        else:
            concatenated_dataset = pd.concat([concatenated_dataset, dataframe], axis=0)
        i += 1

    concatenated_dataset.reset_index(drop=True, inplace=True)

    if configuration['SAVE_DATASET']:
        path_save = os.path.join(configuration['DIRECTORY_DATASET'], configuration['NAME_DATASET_TO_SAVE'])
        concatenated_dataset.to_csv(path_save, index=False)

    return concatenated_dataset
