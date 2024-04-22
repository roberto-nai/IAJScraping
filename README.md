# Giustizia Amministrativa verdicts downloader

![PyPI - Python Version](https://img.shields.io/badge/python-3.12-3776AB?logo=python)

Download the verdicts from Italian Administrative Justice website (TAR and CDS)[https://www.giustizia-amministrativa.it](https://www.giustizia-amministrativa.it).

### > Directories

#### config
Configuration directory with ```config.yml```

#### court
Courts list.

#### verdicts
Index of verdicts to be downloaded.

#### verdicts/<year>
Files of the verdicts.

#### utility_manager
Utility functions.

### > Files

#### ```log.py```
Class useful to the script ```01_scraper.py```.

#### ```sentence.py```
Class useful to the script ```01_scraper.py```.

### > Running the program
- Execute ```01_scraper.py '<query>' <year>``` to generate the list (index) of the verdicts to be downloaded (index file in csv format saved in "verdicts" folder); e.g: ```01_scraper.py 'appalt*' 2022```.
- Execute ```02_downloader.py <year>``` to download the files indexed by ```01_scraper.py``` (using files csv saved in ```verdicts``` folder); e.g: ```01_scraper.py 2022```.
- Execute ```03_analyzer.py``` to get stats about the downloaded data (it analyze the ```verdicts``` directory and save stats in ```verdicts_stats```).

### > Reference
If you use this script, please cite:  

```
@article{NAI2023105887,
title = {Public tenders, complaints, machine learning and recommender systems: a case study in public administration},
journal = {Computer Law & Security Review},
volume = {51},
pages = {105887},
year = {2023},
issn = {0267-3649},
doi = {https://doi.org/10.1016/j.clsr.2023.105887},
url = {https://www.sciencedirect.com/science/article/pii/S0267364923000973},
author = {Roberto Nai and Rosa Meo and Gabriele Morina and Paolo Pasteris},
keywords = {Public procurement, Legal prediction, Complaint detection, Knowledge discovery, Natural language processing, Machine learning, Recommender system},
}
```