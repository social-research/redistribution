# Code and data for "Social networks affect redistribution decisions and polarization"

The repository contains code for agent based models, simulation data, experimental data, analysis code, and outputs for the paper:

* Tsvetkova, M., Olsson, H., & Galesic, M. (2024). Social networks affect redistribution decisions and polarization. https://doi.org/10.31219/osf.io/bw7ux

The folders and files are structured as follows:

* Nelogo code for agent-based model
  * `redistribution_model.nlogo` – generic model for a large population with realistic and adjustable wealth distribution and networks
  * `redistribution_experiment.nlogo` – simplified model for the fixed group size and network structures used in the experiment
* Jupyter notebooks with Python code for main data analysis
  * `model_analysis.ipynb` – analysis of the results from the generic agent-based model
  * `model_exp_analysis.ipynb` – analysis of the predictions from the simplified agent-based model
  * `exp_analysis.ipynb` – analysis of the experimental results
  * helping functions in `modules` folder
  * outputted plots for paper in `plots` folder
* R code for supplementary statistical analyses of experimental data
  * `exp_analysis_behavioir.R`
  * `exp_analysis_dropouts.R`
  * `exp_analysis_groups.R` 
* Data from agent-based model
  * Simulated data from agent-based model in folder `sim-data`
  * Anonymized data from experiments with human subjects in folder `exp-data`
