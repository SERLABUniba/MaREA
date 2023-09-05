from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import json


def tuning_random_forest_model(X_train, y_train):
    """
    Performs the tuning phase.
    The GridSearchCV will be used

    Parameters
    ----------
    X_train: the train set or the dataframe without the label
    y_train: contains only the example label

    Returns
    -------

    """
    from sklearn.model_selection import GridSearchCV

    n_estimators = [9, 20, 50, 100]
    max_features = ['sqrt', 'log2', None]
    max_depth = [10, 15, 20, 25, 30, 40, None]
    min_samples_split = [2, 5, 10]
    min_samples_leaf = [1, 2, 4]

    random_grid = {'n_estimators': n_estimators,
                   'max_features': max_features,
                   'max_depth': max_depth,
                   'min_samples_split': min_samples_split,
                   'min_samples_leaf': min_samples_leaf,
                   }

    rf = RandomForestClassifier()

    gs = GridSearchCV(estimator=rf, param_grid=random_grid, cv=5, verbose=2)
    gs.fit(X_train, y_train)

    print(f"Param Grid: {gs.param_grid}")
    print(f"Best params: {gs.best_params_}")
    print(f"Best estimators: {gs.best_estimator_}")


def train_model(X_train, y_train):
    """
    Performs the training with parameters.
    These parameters, will take from the configuration.json
    Parameters
    ----------
    X_train: train dataset without the label
    y_train: the label

    Returns
    -------
    RandomForest model fitted
    """

    config_file = json.load(open('configuration.json', 'r'))
    if config_file['DATASETS']['SURVIVAL_ANALYSIS_AND_FABRICATION']:
        hyperparam_rf = config_file['RANDOM_FOREST_PARAMETERS_SURVIVAL_ANALYSIS_AND_FABRICATION']
    elif config_file['DATASETS']['CAR_HACKING']:
        hyperparam_rf = config_file['RANDOM_FOREST_PARAMETERS_CAR_HACKING']
    else:
        raise Exception("Not implement error!")

    max_depth = hyperparam_rf['max_depth']
    max_features = hyperparam_rf['max_features']
    min_samples_leaf = hyperparam_rf['min_samples_leaf']
    min_samples_split = hyperparam_rf['min_samples_split']
    n_estimators = hyperparam_rf['n_estimators']

    model = RandomForestClassifier(n_estimators=n_estimators,
                                   max_depth=max_depth,
                                   min_samples_split=min_samples_split,
                                   min_samples_leaf=min_samples_leaf,
                                   max_features=max_features,
                                   random_state=42)

    return model.fit(X_train, y_train)


def test_model(X_test, model: RandomForestClassifier):
    """
    Test the RandomForest model
    Parameters
    ----------
    X_test: the dataset with the test examples
    model: the RandomForest model fitted

    Returns
    -------
    y_pred: the prediction of the RandomForestClassifier

    """
    return model.predict(X_test)


def split_dataset(X, y):
    """
    Calls the train_test_split with train_size=0.70 and test_size=0.32.
    The random_state is 42 to reproduce the experiments
    Parameters
    ----------
    X: the dataframe without the label
    y: the labels with the examples

    Returns
    -------
    X_train, X_test, y_train, y_test
    """
    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.70,
                                                        test_size=0.30, random_state=42, stratify=y)

    return X_train, X_test, y_train, y_test


def scale_dataset(dataset, object_scaler=None):
    """
    Scale the data using the MinMaxScaler in the range [0, 1].
    If the object_scaler is not defined, the method perform the MinMaxScaler on the dataset specified
    and return the object. If the object is specified, perform the transform with this object on the
    dataset specified.
    Parameters
    ----------
    dataset : the dataset to be processed
    object_scaler : If None perform the MinMaxScaler else perform the transform

    Returns
    -------
    If object_scaler is None, returns the dataset processed with fit_transform and the object
    Else return the dataset scaled

    """
    from sklearn.preprocessing import MinMaxScaler

    if object_scaler is None:
        min_max_scaler = MinMaxScaler()
        data = min_max_scaler.fit_transform(dataset)
        return data, min_max_scaler
    else:
        data = object_scaler.transform(dataset)
        return data


def evaluation_results(y_test, y_pred, class_labels):
    """
    Evaluate the result using the Classification Report, save the results into results.txt and print the results.
    The path to save the results, is in the configuration.json
    Parameters
    ----------
    y_test : The label of the test dataset
    y_pred : The label predicted
    class_labels: the name of the label (Normal, Flooding, Fuzzy, Malfunction, Fabrication)

    Returns
    -------

    """

    import os

    path_save_results = json.load(open('configuration.json', 'r'))["PATH_SAVE_RESULTS"]

    report = classification_report(y_test,
                                   y_pred,
                                   target_names=class_labels,
                                   output_dict=True)

    print(report)

    with open(os.path.join(path_save_results, 'results.txt'), 'a') as f:
        json.dump(report, f)
        f.writelines('\n')
    f.close()


def x_y_split(dataset):
    """
    Split the dataset into X and y where X is the dataframe that contains only the examples without the label.
    Instead, y contains the labels
    Parameters
    ----------
    dataset: the dataset to split

    Returns
    -------
    X, y
    """
    cols = list(dataset.columns.values)
    independent_list = cols[0:dataset.shape[1] - 1]

    X = dataset.loc[:, independent_list]
    flag = dataset.columns[dataset.shape[1] - 1]  # Take the label from the dataset

    y = dataset[flag]

    return X, y
