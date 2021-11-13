#!/bin/bash
#SBATCH --job-name=deuparl
#SBATCH --output=/storage/nllg/compute-share/bodensohn/deuparl/DeuParl/logs/6_slice_bundestag.txt
#SBATCH --partition=ukp
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=15GB
#SBATCH --gres=gpu:1

echo "Activate Virtual Environment!"

source ../venv/bin/activate
module purge
module load cuda/11.1

echo "Start Python Script!"
python 6_slice_bundestag.py