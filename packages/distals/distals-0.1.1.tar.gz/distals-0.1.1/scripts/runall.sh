./scripts/0.update.sh
./scripts/0.get_text_data.sh
python3 scripts/0.clean_text_data.py

# Get the precalculated matrix
python3 scripts/1.gen_commands.py > 1.cmds.sh
chmod +x 1.cmds.sh
./1.cmds.sh
python3 scripts/1.merge.py

python3 scripts/2.correlation.py > 2.out
python3 scripts/2.correlation.graph.py
python3 scripts/2.coverage.py
python3 scripts/2.ranges.py

./scripts/3.machamp.prep.sh

python3 scripts/3.machamp.train.py > 3.train.sh
chmod +x 3.train.sh
./3.train.sh

python3 scripts/3.machamp.pred.py > 3.pred.sh
chmod +x 3.pred.sh
./3.pred.sh

python3 scripts/3.machamp.eval.py

python3 scripts/4.casestudy-correlation.py

