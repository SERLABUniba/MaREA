from classification import *
from preprocessing import *
import sys
import json


def main():
    configuration = json.load(open('configuration.json', 'r'))

    if configuration["DATASETS"]["SURVIVAL_ANALYSIS_AND_FABRICATION"]:
        labels = ['Normal', 'Flooding', 'Fuzzy', 'Malfunction', 'Fabrication']
    elif configuration["DATASETS"]["CAR_HACKING"]:
        labels = ['Normal', 'DoS', 'Fuzzy', 'Gear Spoofing', 'RPM Spoofing']
    else:
        raise Exception("The dataset is not implemented or at least one of the two datasets must be selected.")

    if configuration['DO_PREPROCESSING']:
        dataframe = init_preprocessing()
        print(f'[+] Pre processing done!')
    else:
        import os
        path_dataset = os.path.join(configuration['DIRECTORY_DATASET'], configuration['NAME_DATASET_TO_SAVED'])
        dataframe = pd.read_csv(path_dataset)

    # random_state for reproducibility
    dataframe = dataframe.sample(frac=1, random_state=42).reset_index(drop=True)

    print(f'[+] Splitting into X, y')
    X, y = x_y_split(dataframe)

    if configuration['TUNING']:
        X, scaler = scale_dataset(X)
        tuning_random_forest_model(X, y)
        print("[+] Tuning DONE!")
        sys.exit(-1)

    print(f'[+] Splitting dataset')
    X_train, X_test, y_train, y_test = split_dataset(X, y)

    print(f'[+] Scaling dataset')
    X_train, scaler = scale_dataset(X_train)
    X_test = scale_dataset(X_test, scaler)

    print(f'[+] Training the model')
    model = train_model(X_train, y_train)

    print(f'[+] Testing the model')
    y_pred = test_model(X_test, model)

    evaluation_results(y_test, y_pred, labels)


if __name__ == '__main__':
    main()
