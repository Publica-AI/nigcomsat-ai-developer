#!/bin/zsh
# Runs a day's notebooks top to bottom on BOTH pandas versions and prints the score lines.
# usage: TS_TEST_DIR=<folder from setup_test_envs.sh> run_day.sh <TAG> <notebook.ipynb> [more.ipynb]
# Works offline: the download cache is pre-filled from the local original data files.
T=${TS_TEST_DIR:?set TS_TEST_DIR}
HERE=${0:A:h}; REPO=${HERE:h:h:h}
TAG=$1; shift
for env in venv22 venvlatest; do
  dir=$T/nbrun_${TAG}_$env; rm -rf $dir; mkdir -p $dir
  for w in week-03 week-04 week-05 week-06; do mkdir -p $dir/course_data/$w; cp $REPO/Time-series/$w/data/*.csv $dir/course_data/$w/; done
  for nb in "$@"; do
    cp "$nb" $dir/
    (cd $dir && JUPYTER_PATH=$T/kernels_$env/share/jupyter $T/$env/bin/python -m jupyter nbconvert --to notebook --execute --allow-errors \
      --ExecutePreprocessor.timeout=600 --ExecutePreprocessor.kernel_name=ts-$env "$(basename $nb)" --output "out-$(basename $nb)" >/dev/null 2>&1)
    echo "=== $env $(basename $nb)"; $T/venvlatest/bin/python $HERE/nbtest.py "$dir/out-$(basename $nb)" | grep -E "Ready|You have|ERRORS|ticks|❌"
  done
done
