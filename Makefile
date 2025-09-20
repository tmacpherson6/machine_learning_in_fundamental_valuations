VENV   := $(HOME)/.venvs/milestoneII
PYTHON := $(VENV)/bin/python

.PHONY: all venv
all: datasets/Russell_3000_Fundamentals.csv

# Create virtual environment and install dependencies
venv: $(PYTHON)
$(PYTHON):
	python3 -m venv $(VENV)

$(VENV)/.deps: requirements.txt | $(PYTHON)
	"$(PYTHON)" -m pip install -U pip
	"$(PYTHON)" -m pip install -r requirements.txt
	touch $@

# Generate the dataset with fundamentals from the Base Stock Dataset
datasets/Russell_3000_Fundamentals.csv: datasets/Russell_3000.csv data_acquisition.py | datasets $(VENV)/.deps
	"$(PYTHON)" data_acquisition.py $< $@

# If the datasets directory does not exist, create it
datasets:
	mkdir -p $@