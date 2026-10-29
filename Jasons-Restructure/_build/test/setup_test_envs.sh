#!/bin/zsh
# Creates the two test environments (pandas 2.2 = what Colab has shipped, pandas 3 = newest)
# and a Jupyter kernel for each, all inside one folder you choose (e.g. a scratch folder).
# usage: setup_test_envs.sh <folder>
set -e
T=${1:?give a folder}; mkdir -p $T
uv venv -q $T/venv22 --python 3.12
uv pip install -q --python $T/venv22/bin/python "pandas==2.2.2" "numpy<2.1" scikit-learn matplotlib statsmodels nbconvert nbformat ipykernel
uv venv -q $T/venvlatest --python 3.12
uv pip install -q --python $T/venvlatest/bin/python pandas numpy scikit-learn matplotlib statsmodels nbconvert nbformat ipykernel markdown pillow pypdf defusedxml lxml python-pptx
for env in venv22 venvlatest; do
  $T/$env/bin/python -m ipykernel install --prefix $T/kernels_$env --name ts-$env >/dev/null
done
echo "ready: $T/venv22 (pandas $($T/venv22/bin/python -c 'import pandas;print(pandas.__version__)')), $T/venvlatest (pandas $($T/venvlatest/bin/python -c 'import pandas;print(pandas.__version__)'))"
