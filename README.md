
# SA-Hacking Dataset: Synthetic Automotive Hacking Dataset

Authors:
_Vita Santa Barletta, Danilo Caivano, and Mirko De Vincentiis_

## References

_MaREA: Multi-class Random Forest for Automotive Intrusion Detection_

```
@InProceedings{Caivano2024MaREA,
author="Caivano, Danilo
and Catalano, Christian
and De Vincentiis, Mirko
and Lako, Alfred
and Pagano, Alessandro",
editor="Kadgien, Regine
and Jedlitschka, Andreas
and Janes, Andrea
and Lenarduzzi, Valentina
and Li, Xiaozhou",
title="MaREA: Multi-class Random Forest for Automotive Intrusion Detection",
booktitle="Product-Focused Software Process Improvement",
year="2024",
publisher="Springer Nature Switzerland",
address="Cham",
pages="23--34",
isbn="978-3-031-49269-3"
}
```

_Machine Learning for Automotive Security in Technology Transfer_

```
@InProceedings{Barletta2024TechTransfer,
author="Barletta, Vita Santa
and Caivano, Danilo
and Catalano, Christian
and De Vincentiis, Mirko
and Pal, Anibrata",
editor="Rocha, Alvaro
and Adeli, Hojjat
and Dzemyda, Gintautas
and Moreira, Fernando
and Colla, Valentina",
title="Machine Learning for Automotive Security in Technology Transfer",
booktitle="Information Systems and Technologies",
year="2024",
publisher="Springer Nature Switzerland",
address="Cham",
pages="341--350",
isbn="978-3-031-45651-0"
}
```

## Code requirements
The code relies on the following python3.7+ libs.
Packages with the version used are:
* [Pandas 1.5.0](https://pandas.pydata.org/)
* [Numpy 1.23.3](https://numpy.org/)
* [scikit-learn 1.0.2](https://scikit-learn.org/stable/)

## Data
The [Car-Hacking Dataset](https://ocslab.hksecurity.net/Datasets/car-hacking-dataset), the [Survival Analysis Dataset](https://ocslab.hksecurity.net/Datasets/survival-ids), and the Synthetic Automotive Dataset have used. For the Survivial Analysis only the KIA Soul were considered. The files for this dataset are trasformed from .txt to .csv.
The Synthetic Automotive Dataset dataset is contained into the RandomForest\datasets

Corresponding labels for the Car-Hacking Dataset:
* 0: Normal
* 1: DoS
* 2: Fuzzy
* 3: Gear Spoofing
* 4: RPM Spoofing

Corresponding labels for the concantenated dataset (Survival Analysis Dataset and Synthetic Automotive Hacking Dataset):
* 0: Normal
* 1: Flooding
* 2: Fuzzy
* 3: Malfunction
* 4: Fabrication

## How to use

The repository contains the following scripts:
RandomForest\
* main.py:  script to execute the different phases
* preprocessing.py: script that contains the preprocessing phases (load dataset, padding, conversion, ...).
* classification.py: script that contains the classification phases (model evaluation, split dataset, train and test, results evaluation)

generated_dataset\
* Fabrication.py: script that generate the normal and fabrication attacks using a virtual CAN interface 

## Replicate the experiments

Use the **configuration.json** to configure the different paths in which the datasets are contained. Use the label "true" or "false" to select the dataset that you want to use. Then, run **main.py** script.
The configuration.json contains also the best parameters founded for the Random Forest.
