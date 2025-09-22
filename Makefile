# See README file on how to use this Makefile

VENV   := $(HOME)/.venvs/milestoneII
PYTHON := $(VENV)/bin/python
PIP    := $(VENV)/bin/pip

.PHONY: all venv 
all: datasets/Russell_3000_With_Macro.csv
macro: datasets/Russell_3000_With_Macro.csv

# Create virtual environment and install dependencies
venv: $(PYTHON)
$(PYTHON):
	python3 -m venv $(VENV)
	"$(PYTHON)" -m ensurepip --upgrade
	"$(PIP)" install -U pip

$(VENV)/.deps: requirements.txt | $(PYTHON)
	"$(PYTHON)" -m pip install -U pip
	"$(PYTHON)" -m pip install -r requirements.txt
	touch $@

# Generate the dataset with fundamentals from the Base Stock Dataset
datasets/Russell_3000_Fundamentals.csv: datasets/Russell_3000.csv data_acquisition.py | datasets $(VENV)/.deps
	"$(PYTHON)" data_acquisition.py $< $@

# Add Macroeconomic data to the dataset
datasets/Russell_3000_With_Macro.csv: datasets/Russell_3000_Fundamentals.csv data_acquisition_macro.py | datasets $(VENV)/.deps
	"$(PYTHON)" data_acquisition_macro.py $< $@

# Clean the generated dataset
datasets/Russell_3000_Cleaned.csv: datasets/Russell_3000_With_Macro.csv clean.py | datasets $(VENV)/.deps
	"$(PYTHON)" clean.py $< $@

#----------------------------------------------------------------------------
# Still Need to Create These
#----------------------------------------------------------------------------

# Data Imputation on the cleaned dataset
#datasets/Russell_3000_Imputed.csv: datasets/Russell_3000_Cleaned.csv imputation.py | datasets $(VENV)/.deps
#	"$(PYTHON)" imputation.py $< $@

# Feature engineering on the cleaned dataset
#datasets/Russell_3000_Featured.csv: datasets/Russell_3000_Imupted.csv feature_engineering.py | datasets $(VENV)/.deps
#	"$(PYTHON)" feature_engineering.py $< $@

# If the datasets directory does not exist, create it
datasets:
	mkdir -p $@
