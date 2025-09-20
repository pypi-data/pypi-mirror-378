# DistaLs

DistaLs is a database and toolkit that can be used to obtain distances
between languages. 

An online interface is available on: [https://distals.streamlit.app/](https://distals.streamlit.app/)

A short introduction video to DistaLs can be viewed on: https://www.youtube.com/watch?v=SSk9xbssY2o

More information about the toolkit and its features can be found in the [paper](distals_paper.pdf)

## Installation
#### Direct use from the repository
First install the required packages: `pip3 install -r requirements.txt`, 
and then you can run DistaLs directly from the src folder: `python3 src/distals/distals.py`.

#### Install
You can install DistaLs from pip: `pip3 install distals`, or from the 
repository: 
```
python3 setup.py  sdist bdist_wheel
pip3 install dist/distals-0.0.9.1-py3-none-any.whl --break-system-packages --force-reinstall
```

After distals has been installed, you can directly call it from the command
line using `distals`, or import it in python.

## Usage
#### command line
The main usage is through the --langs parameter. It takes a list of languages as input, which
can be either iso639-3 codes or full names of languages. 
We first try to parse the input as an ISO code, and treat it as a language name only if this is not successful.
It first prints information from the
databases for each language, followed by the distances between the languages. If you provide
only one language, you just get the database information. If you provide two languages, you 
get a list of distances, and if you provide more, you get confusion matrices. An example output
with two languages is shown below:

```
> distals --langs danish fry
database_path not defined, searching for database in:
current folder
loading from: ./distals-db.pickle.gz
7856 languages loaded
========================================
Information for Danish (dan)
wiki_size: 308,911
nlp_state: 3. The Rising Stars
speakers: 5,510,600
AES: 5. not endangered
loc: (9.36284, 54.8655)
lang2vec: [1.0, 0.0, 0.0, ..., '--', '--', '--']
lang2vec_knn: [1.0, 0.0, 0.0, ..., 1.0, 0.0, 0.0]
phoible: ['0061', '0062+0325', '0062+0325+02B0', ..., '0281+031E', '028B', '028C']
grambank: {'GB020': 1, 'GB021': 1, 'GB022': 1, ..., 'GB520': 0, 'GB521': 0, 'GB522': 0}
glot_tree: ["'Danish [dani1285][dan]-l-'", "'South Scandinavian [sout3248]'", "'North Germanic [nort3160]'", "'Northwest Germanic [nort3152]'", "'Germanic [germ1287]'", "'Classical Indo-European [clas1257]'", "'Indo-European [indo1319]'"]
scripts: {'latn'}
asjp: [['1', 'yoy'], ['2', 'du'], ['3', 'vi'], ..., ['98', 'ron7'], ['99', 'tE7a'], ['100', 'now7n']]
whitespace: 0.156298
punctuation: 0.028514
char_JSD: {' ': 0.1563, 'e': 0.1249, 'r': 0.0675, ..., 'Y': 0.0000, 'Á': 0.0000, 'Q': 0.0000}
textcat: [' ', 'e', 'r', ..., 'lle ', 'J', 'e de']

========================================
Information for Western Frisian (fry)
wiki_size: 57,027
nlp_state: 1. The Scraping-Bys
speakers: 740,000
AES: 5. not endangered
loc: (5.86091, 53.143)
lang2vec: [1.0, 1.0, 0.0, ..., '--', '--', '--']
lang2vec_knn: [1.0, 1.0, 0.0, ..., 1.0, 0.0, 0.0]
phoible: ['0061', '0061+0069', '0061+0075', ..., '026A+0259', '0275', '0275+0259']
grambank: {'GB020': 1, 'GB021': 1, 'GB022': 1, ..., 'GB520': 0, 'GB521': 0, 'GB522': 0}
glot_tree: ["'Western Frisian [west2354][fry]-l-'", "'Westlauwers-Terschelling Frisian [west2902]'", "'Modern West Frisian [mode1264]'", ..., "'Germanic [germ1287]'", "'Classical Indo-European [clas1257]'", "'Indo-European [indo1319]'"]
scripts: {'latn'}
asjp: [['1', 'ik'], ['2', 'do, yo'], ['3', 'vEi'], ..., ['95', 'fol'], ['96', 'nEy, nEi'], ['100', 'nam3']]
whitespace: 0.160835
punctuation: 0.031726
char_JSD: {' ': 0.1608, 'e': 0.1195, 'n': 0.0754, ..., 'ɾ': 0.0000, 'õ': 0.0000, 'ß': 0.0000}
textcat: [' ', 'e', 'n', ..., 'ing ', ' dat ', 'n.']

========================================
Distances between Danish (dan) and Western Frisian (fry), -1 if the feature is not available for both
METADATA
wiki_size: 0.8154
nlp_state: 0.4000
speakers: 0.8657
AES: 0.0000
loc: 0.0149
average: 0.4219

TYPOLOGY
lang2vec: 0.1598
lang2vec_knn: 0.1204
phoible: 0.8148
grambank: 0.3841
gb_clause: 0.3742
gb_nominal_domain: 0.3482
gb_numeral: 0.5000
gb_pronoun: 0.0000
gb_verbal_domain: 0.4644
glot_tree: 0.5325
scripts: 0.0000
average: 0.5995

WORDLISTS
asjp: 0.3397
concepts: 0.0400
average: 0.1898

TEXTBASED
whitespace: 0.0282
punctuation: 0.1012
char_JSD: 0.1979
textcat: 0.5859
average: 0.5859

```

The code is dependent on a database file. If it is not specified, it will search in the current folder and in `~/.cache/distals/`. If it is not found, it will automatically download a recent version of the database to the `.cache` folder and use that.

To rebuild or update the database, you first need to scrape the relevant data sources, this can be done with the `scripts/0.update.sh` script, and `0.get_text_data.sh` for the textbased features (note that this takes very long to download). After this has been done, you can run distals with the `--database_path` option, and one of the three update commands: `--update_langnames` for language lookup information, `--update_textbased` for updating the textbased features, and `--update_databases` for all other features.

#### python
First load a DistaLs models based on a database:
```
>>> from distals import distals
>>> model = distals.Distals('distals-db.pickle.gz')
```

Now you can query the model for distances between two languages with the `get_dists()` function:

```
>>> model.get_dists('nld', 'cmn')
{'metadata': {'AES': 0.0,
              'average': 0.39377015597113374,
              'loc': 0.39121043192100247,
              'nlp_state': 0.2,
              'speakers': 0.9813104679134012,
              'wiki_size': 0.9937779949135439},
 'textbased': {'average': 0.87235,
               'char_JSD': 0.5440088529474519,
               'punctuation': 0.6785480160817546,
               'textcat': 0.87235,
               'whitespace': 0.2124426381618435},
 'typology': {'average': 0.8025219634870027,
              'gb_clause': 0.5547001962252291,
              'gb_nominal_domain': 0.5976143046671968,
              'gb_numeral': 0.0,
              'gb_pronoun': 0.6454972243679029,
              'gb_verbal_domain': 0.6030226891555274,
              'glot_tree': 1.0,
              'grambank': 0.584781080334426,
              'lang2vec': 0.3165422989941302,
              'lang2vec_knn': 0.33795071460896176,
              'phoible': 0.8227848101265822,
              'scripts': 0.6666666666666667},
 'wordlists': {'asjp': 0.49635837471403577,
               'average': 0.28817918735701786,
               'concepts': 0.07999999999999996}}
```

By default, it returns the features as a hierarchy of dictionaries, including the averages over selected features.
If you set `aslist` to `True`, you will get the features as a list (without averages). If you want to align them 
to the feature names you can obtain those from `distals.classes`:
```
>>> model.get_dists('nld', 'cmn', aslist=True)
([0.9937790230796005, 0.2, 0.9813104679134012, 0.0, 0.39121043192100247, 0.3165422989941302, 0.33795071460896176, 0.8227848101265822, 0.584781080334426, 0.5547001962252291, 0.5976143046671968, 0.0, 0.6454972243679029, 0.6030226891555274, 1.0, 0.6666666666666667, 0.4968771719863224, 0.07999999999999996, 0.2124426381618435, 0.6785480160817546, 0.5440088529474518, 0.87235], [0.5437723727482504, 0.7037829452305041, 0.2884385859931612, 0.7081794264737259])
>>> [x[1] for x in distals.classes]
['wiki_size', 'nlp_state', 'speakers', 'AES', 'loc', 'lang2vec', 'lang2vec_knn', 'phoible', 'grambank', 'gb_clause', 'gb_nominal_domain', 'gb_numeral', 'gb_pronoun', 'gb_verbal_domain', 'glot_tree', 'scripts', 'asjp', 'concepts', 'whitespace', 'punctuation', 'char_JSD', 'textcat']
```

For the distance measures based on ASJP, lang2vec and Grambank, DistaLs uses a threshold: distances are only calculated if at least 25% of the features have values for both languages. You can change this threshold with the `threshold` argument:

```
[TODO: insert example here]
```

Using only the name to iso639-3 conversion functionality is also possible:
```
>>> print(model.langname_utils.toISO('nederlands'))
nld
```

If you want direct access to the features of a language you can use `model.all_data`, it is a dictionary with languages as keys, and all their information stored in their values (also as a dictionary). Note that they are in a variety of formats.


#### Data
You can also use the precalculated distance metrics directly from csv files,
but the files are quite large (as the matrices can be 7856x7856). You can
download the csv files from
https://itu.dk/people/robv/data/distals-precalculated.tar.gz


## References
Please provide the correct citations when using any of these metrics. People
have spend a lot of their valuable time providing us with this data. If you
use all of them, please use:

```
We used DistaLs~\cite{van-der-goot-etal-2025-distals,ritchie-etal-2024-linguameta,kargaran-etal-2024-glotscript-resource,joshi-etal-2020-state,glottolog,littell-etal-2017-uriel,skirgardGrambankRevealsImportance2023,glottolog,phoible,ASJP,liu-etal-2023-crosslingual,brown-2014-non}
```

with the bib data in `data/papers.bib` in this repository.

* **Wikipedia**
You can use the source URL for referencing: https://en.wikipedia.org/wiki/List_of_Wikipedias

* **LinguaMeta**

```
@inproceedings{ritchie-etal-2024-linguameta,
    title = "{L}ingua{M}eta: Unified Metadata for Thousands of Languages",
    author = "Ritchie, Sandy  and
      van Esch, Daan  and
      Okonkwo, Uche  and
      Vashishth, Shikhar  and
      Drummond, Emily",
    editor = "Calzolari, Nicoletta  and
      Kan, Min-Yen  and
      Hoste, Veronique  and
      Lenci, Alessandro  and
      Sakti, Sakriani  and
      Xue, Nianwen",
    booktitle = "Proceedings of the 2024 Joint International Conference on Computational Linguistics, Language Resources and Evaluation (LREC-COLING 2024)",
    month = may,
    year = "2024",
    address = "Torino, Italia",
    publisher = "ELRA and ICCL",
    url = "https://aclanthology.org/2024.lrec-main.921/",
    pages = "10530--10538",
}

```
Complemented with script information from:

```
@inproceedings{kargaran-etal-2024-glotscript-resource,
    title = "{G}lot{S}cript: A Resource and Tool for Low Resource Writing System Identification",
    author = {Kargaran, Amir Hossein  and
      Yvon, Fran{\c{c}}ois  and
      Sch{\"u}tze, Hinrich},
    editor = "Calzolari, Nicoletta  and
      Kan, Min-Yen  and
      Hoste, Veronique  and
      Lenci, Alessandro  and
      Sakti, Sakriani  and
      Xue, Nianwen",
    booktitle = "Proceedings of the 2024 Joint International Conference on Computational Linguistics, Language Resources and Evaluation (LREC-COLING 2024)",
    month = may,
    year = "2024",
    address = "Torino, Italia",
    publisher = "ELRA and ICCL",
    url = "https://aclanthology.org/2024.lrec-main.687",
    pages = "7774--7784"
}
```

* **State and Fate**
```
@inproceedings{joshi-etal-2020-state,
    title = "The State and Fate of Linguistic Diversity and Inclusion in the {NLP} World",
    author = "Joshi, Pratik  and
      Santy, Sebastin  and
      Budhiraja, Amar  and
      Bali, Kalika  and
      Choudhury, Monojit",
    editor = "Jurafsky, Dan  and
      Chai, Joyce  and
      Schluter, Natalie  and
      Tetreault, Joel",
    booktitle = "Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics",
    month = jul,
    year = "2020",
    address = "Online",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2020.acl-main.560",
    doi = "10.18653/v1/2020.acl-main.560",
    pages = "6282--6293"
}
```

* **Glottolog**
```
@misc{glottolog,
    title = "Glottolog 5.0.",
    author = "Hammarström, Harald and Forkel, Robert and Haspelmath, Martin and Bank, Sebastian",
    year = 2024,
    url = "https://doi.org/10.5281/zenodo.10804357",
    publisher = "Leipzig: Max Planck Institute for Evolutionary Anthropology",
    misc = "Available online at http://glottolog.org, Accessed on 2024-04-24."
}
```

* **lang2vec**: 
```
@inproceedings{littell-etal-2017-uriel,
    title = "{URIEL} and lang2vec: Representing languages as typological, geographical, and phylogenetic vectors",
    author = "Littell, Patrick  and
      Mortensen, David R.  and
      Lin, Ke  and
      Kairis, Katherine  and
      Turner, Carlisle  and
      Levin, Lori",
    editor = "Lapata, Mirella  and
      Blunsom, Phil  and
      Koller, Alexander",
    booktitle = "Proceedings of the 15th Conference of the {E}uropean Chapter of the Association for Computational Linguistics: Volume 2, Short Papers",
    month = apr,
    year = "2017",
    address = "Valencia, Spain",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/E17-2002",
    pages = "8--14"
}
```

* **Grambank**
```
@article{skirgardGrambankRevealsImportance2023,
  title = {Grambank reveals the importance of genealogical constraints on linguistic diversity and highlights the impact of language loss},
  author = {Skirgård, Hedvig and Haynie, Hannah J. and Blasi, Damián E. and Hammarström, Harald and Collins, Jeremy and Latarche, Jay J. and Lesage, Jakob and Weber, Tobias and Witzlack-Makarevich, Alena and Passmore, Sam and Chira, Angela and Maurits, Luke and Dinnage, Russell and Dunn, Michael and Reesink, Ger and Singer, Ruth and Bowern, Claire and Epps, Patience and Hill, Jane and Vesakoski, Outi and Robbeets, Martine and Abbas, Noor Karolin and Auer, Daniel and Bakker, Nancy A. and Barbos, Giulia and Borges, Robert D. and Danielsen, Swintha and Dorenbusch, Luise and Dorn, Ella and Elliott, John and Falcone, Giada and Fischer, Jana and Ghanggo Ate, Yustinus and Gibson, Hannah and Göbel, Hans-Philipp and Goodall, Jemima A. and Gruner, Victoria and Harvey, Andrew and Hayes, Rebekah and Heer, Leonard and Herrera Miranda, Roberto E. and Hübler, Nataliia and Huntington-Rainey, Biu and Ivani, Jessica K. and Johns, Marilen and Just, Erika and Kashima, Eri and Kipf, Carolina and Klingenberg, 
    Janina V. and König, Nikita and Koti, Aikaterina and Kowalik, Richard G. A. and Krasnoukhova, Olga and Lindvall, Nora L.M. and Lorenzen, Mandy and Lutzenberger, Hannah and Martins, Tônia R.A. and Mata German, Celia and van der Meer, Suzanne and Montoya Samamé, Jaime and Müller, Michael and Muradoglu, Saliha and Neely, Kelsey and Nickel, Johanna and Norvik, Miina and Oluoch, Cheryl Akinyi and Peacock, Jesse and Pearey, India O.C. and Peck, Naomi and Petit, Stephanie and Pieper, Sören and Poblete, Mariana and Prestipino, Daniel and Raabe, Linda and Raja, Amna and Reimringer, Janis and Rey, Sydney C. and Rizaew, Julia and Ruppert, Eloisa and Salmon, Kim K. and Sammet, Jill and Schembri, Rhiannon and Schlabbach, Lars and Schmidt, Frederick W.P. and Skilton, Amalia and Smith, Wikaliler Daniel and de Sousa, Hilário and Sverredal, Kristin and Valle, Daniel and Vera, Javier and Voß, Judith and Witte, Tim and Wu, Henry and Yam, Stephanie and Ye 葉婧婷, Jingting and Yong, Maisie and Yuditha, Tessa and Zariquiey, Roberto and Forkel, Robert and Evans, Nicholas and Levinson, Stephen C. and Haspelmath, Martin and Greenhill, Simon J. and Atkinson, Quentin D. and Gray, Russell D.},
  journal = {Science Advances},
  volume = {9},
  number = {16},
  doi = {10.1126/sciadv.adg6175},
  year = {2023}
}
```

* **Glottolog**: 
```
@misc{glottolog,
    title = "Glottolog 5.0.",
    author = "Hammarström, Harald and Forkel, Robert and Haspelmath, Martin and Bank, Sebastian",
    year = 2024,
    url = "https://doi.org/10.5281/zenodo.10804357",
    publisher = "Leipzig: Max Planck Institute for Evolutionary Anthropology",
    misc = "Available online at http://glottolog.org, Accessed on 2024-04-24."
}
```

* **PHOIBLE**
```
@book{phoible,
  address   = {Jena},
  editor    = {Steven Moran and Daniel McCloy},
  publisher = {Max Planck Institute for the Science of Human History},
  title     = {PHOIBLE 2.0},
  url       = {https://phoible.org/},
  year      = {2019}
}
```

* **asjp_lev_dist**: 
```
@misc{ASJP,
author = {Wichmann and Søren and Holman, Eric W. and Brown, Cecil H.},
year = {2022},
title = {The {ASJP} Database (version 20)}
}
```

* **Conceptualizer**
```
@inproceedings{liu-etal-2023-crosslingual,
    title = "A Crosslingual Investigation of Conceptualization in 1335 Languages",
    author = {Liu, Yihong  and
      Ye, Haotian  and
      Weissweiler, Leonie  and
      Wicke, Philipp  and
      Pei, Renhao  and
      Zangenfeind, Robert  and
      Sch{\"u}tze, Hinrich},
    editor = "Rogers, Anna  and
      Boyd-Graber, Jordan  and
      Okazaki, Naoaki",
    booktitle = "Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)",
    month = jul,
    year = "2023",
    address = "Toronto, Canada",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2023.acl-long.726/",
    doi = "10.18653/v1/2023.acl-long.726",
    pages = "12969--13000"
}
```

* **Text-based**
```
@inproceedings{brown-2014-non,
    title = "Non-linear Mapping for Improved Identification of 1300+ Languages",
    author = "Brown, Ralf",
    editor = "Moschitti, Alessandro  and
      Pang, Bo  and
      Daelemans, Walter",
    booktitle = "Proceedings of the 2014 Conference on Empirical Methods in Natural Language Processing ({EMNLP})",
    month = oct,
    year = "2014",
    address = "Doha, Qatar",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/D14-1069/",
    doi = "10.3115/v1/D14-1069",
    pages = "627--632"
}
```

* **DistaLs**
```
@inproceedings{van-der-goot-etal-2025-distals,
    title= "{DistaLs}: a Comprehensive Collection of Language Distance Measures",
    author = "van der Goot, Rob and Ploeger, Esther and Blaschke, Verena and Samardzic, Tanja"
    year = "2025",
    booktitle = {Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing: System Demonstrations}
}
```

## How to reproduce the paper
We follow the reproducability strategy proposed on: https://robvanderg.github.io/evaluation/repro/ . This means that we have a scripts folder that contains the code for all experiments. The experiments are numbered, and the exact commands to run to reproduce all results can be found in `scripts/runall.sh`. Note that these steps take very long, so I would discourage you to run `runall.sh` directly, but instead parallelize some steps. If you want to run the scripts, you need to install the dependencies from `requirements-dev.txt`. 

## How to add new languages
By design, DistaLs focuses only on ISO639-3 languages. The information from ISO639-3 is simply collected from the file `data/data/iso-639-3.tab`, so if you use a file in the same format you could also add other languages. However, most data sources use ISO639-3, so you will not be able to automatically extract the features. If you would just like to update a feature(set) for a language, this can be done through the original sources (and running `scripts/0.update.sh`), editing the downloaded files in the `data/` folder, or directly editing the python dictionary that contains the database.

## How to add new features
- You can add the commands to download the new data source to the data folder in `scripts/0.update.sh`
- You have to create a new python file for each new data source that you include.
- In this file there have to be two functions: `collect` and `distance_metric`. The first one converts the raw data into the DistaLs database, the 2nd one uses this data to calculate a distance metric. Below we'll describe how they can/should be made:

collect: there is an `all_data` variable, which is a dictionary containing all metadata per language. So for each language, you should first find the language in the `all_data` dictionary, then add the new information with a new, unique name. Note that you can (and probably should) use the functions `langname_utils.name_to_iso` or `langname_utiles.toISO` to ensure that names and language codes are converted into valid ISO639-3 codes (or None if not available). Finally, the all_data dictionary should be returned.

distance_metric: This will receive the data that was stored in the collect function for 2 languages. This data can then be used to calculate a distance metric which should be returned.

- You can see many examples of how features are implemented in `src/distals/`. We would recommend to look at `src/distals/state_and_fate.py`, as the data collection is relatively straightforward.
- Import the file in `src/distal/distals.py` (twice)
- Add to the classes variable in `src/distals/distals.py`, note that the string with the name should exactly match the one used in the `collect` function to store the data in the database.


## How to update DistaLs (for devs)
- generate a new database
- push/upload database
- update link to db in src/distals/distals.py
- push code
- update version number in setup.py
- add to pip:
```
rm dist/*
python3 setup.py  sdist bdist_wheel
pip3 install dist/distals-0.1-py3-none-any.whl  --break-system-packages --force-reinstall
twine upload dist/*
```
