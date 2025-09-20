
git clone https://github.com/machamp-nlp/machamp.git
cd machamp
pip3 install -r requirements.txt
cd ..

cd data
# UD
if [ ! -d "ud-treebanks-v2.15" ];then
    wget https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-5787/ud-treebanks-v2.15.tgz
    tar -zxvf ud-treebanks-v2.15.tgz
fi
cd ../


python3 machamp/scripts/misc/cleanconl.py data/ud-treebanks-v2.15/*/*conllu
