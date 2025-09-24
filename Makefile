# See README file on how to use this Makefile

VENV   := $(HOME)/.venvs/milestoneII
PYTHON := $(VENV)/bin/python
PIP    := $(VENV)/bin/pip

# --- Train/Test split configuration ---
SPLIT_SCRIPT := train_test_split.py
TARGET_TAG   := _2025Q2
SPLIT_DIR    := datasets
X_TRAIN := $(SPLIT_DIR)/X_train.csv
Y_TRAIN := $(SPLIT_DIR)/y_train.csv
X_TEST  := $(SPLIT_DIR)/X_test.csv
Y_TEST  := $(SPLIT_DIR)/y_test.csv
SPLIT_STAMP := $(SPLIT_DIR)/.train_test.split

.PHONY: all venv macro cleaned split clean-split
all: $(X_TRAIN) $(Y_TRAIN) $(X_TEST) $(Y_TEST)
macro: datasets/Russell_3000_With_Macro.csv
cleaned: datasets/Russell_3000_Cleaned.csv
split: $(X_TRAIN) $(Y_TRAIN) $(X_TEST) $(Y_TEST)

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

# --- Train/Test split: produce all four outputs via a stamp ---
$(SPLIT_STAMP): datasets/Russell_3000_Cleaned.csv $(SPLIT_SCRIPT) | datasets $(VENV)/.deps
	cd $(SPLIT_DIR) && "$(PYTHON)" "../$(SPLIT_SCRIPT)" "Russell_3000_Cleaned.csv" "$(TARGET_TAG)"
	touch $@

$(X_TRAIN) $(Y_TRAIN) $(X_TEST) $(Y_TEST): $(SPLIT_STAMP)

clean-split:
	rm -f $(X_TRAIN) $(Y_TRAIN) $(X_TEST) $(Y_TEST) $(SPLIT_STAMP)

#----------------------------------------------------------------------------
# Create X_train_ready.csv from imputation script
datasets/X_train_ready.csv: Missing_value_fillin.ipynb datasets/X_train.csv
	jupyter nbconvert --to notebook --execute Missing_value_fillin.ipynb --output tmp_out.ipynb
#----------------------------------------------------------------------------

# Data Imputation on the cleaned dataset
#datasets/Russell_3000_Imputed.csv: datasets/Russell_3000_Cleaned.csv imputation.py | datasets $(VENV)/.deps
#	"$(PYTHON)" imputation.py $< $@

# Feature engineering on the cleaned dataset
#datasets/Russell_3000_Featured.csv: datasets/Russell_3000_Imputed.csv feature_engineering.py | datasets $(VENV)/.deps
#	"$(PYTHON)" feature_engineering.py $< $@

# If the datasets directory does not exist, create it
datasets:
	mkdir -p $@