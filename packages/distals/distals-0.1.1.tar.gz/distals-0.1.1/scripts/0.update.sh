# For context, references, and licenses see `data/README.md`.

cd data

wget https://en.wikipedia.org/wiki/List_of_Wikipedias -O List_of_Wikipedias.htm
wget https://iso639-3.sil.org/sites/iso639-3/files/downloads/iso-639-3.tab -O iso-639-3.tab
wget https://iso639-3.sil.org/sites/iso639-3/files/downloads/iso-639-3_Retirements.tab -O iso-639-3_Retirements.tab
wget https://cdstar.eva.mpg.de//bitstreams/EAEA0-2198-D710-AA36-0/tree_glottolog_newick.txt -O tree_glottolog_newick.txt 
wget https://microsoft.github.io/linguisticdiversity/assets/lang2tax.txt -O lang2tax.txt
wget https://github.com/cisnlp/GlotScript/raw/main/metadata/GlotScript.tsv -O GlotScript.tsv
wget https://raw.githubusercontent.com/google-research/url-nlp/refs/heads/main/linguameta/linguameta.tsv -O linguameta.tsv
wget https://raw.githubusercontent.com/yihongL1U/conceptualizer/refs/heads/main/4_similarity_eva/sim_matrix.csv -O sim_matrix.csv
wget https://github.com/grambank/grambank/raw/refs/heads/master/cldf/values.csv -O values.csv
wget https://github.com/phoible/dev/raw/refs/heads/master/data/phoible.csv -O phoible.csv
wget https://raw.githubusercontent.com/grambank/grambank/refs/heads/master/docs/feature_groupings/feature_grouping_for_analysis.csv -O feature_grouping_for_analysis.csv

# ASJP
wget https://zenodo.org/records/16736409/files/lexibank/asjp-v21.zip -O asjp-v21.zip
unzip asjp-v21.zip
cp lexibank-asjp-0127953/raw/lists.txt .
rm -rf lexibank-asjp-0127953/ asjp-v21.zip

# Glottolog
if [ ! -d "glottolog" ]; then
    git clone https://github.com/glottolog/glottolog.git
fi
cd glottolog 
git pull

# WALS
if [ ! -d "wals" ]; then
    git clone https://github.com/cldf-datasets/wals.git
fi
cd wals
git pull

cd ../


