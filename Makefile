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
X_TRAIN_FILLED := $(SPLIT_DIR)/X_train_filled.csv
X_TRAIN_FILLED_KPIS := $(SPLIT_DIR)/X_train_filled_KPIs.csv
X_TEST_FILLED_KPIS := $(SPLIT_DIR)/X_test_filled_KPIs.csv
X_TEST_FILLED := $(SPLIT_DIR)/X_test_filled.csv
SPLIT_STAMP := $(SPLIT_DIR)/.train_test.split

.PHONY: all venv macro cleaned split clean-split
all: $(X_TRAIN) $(Y_TRAIN) $(X_TEST) $(Y_TEST) $(X_TRAIN_FILLED) $(X_TRAIN_FILLED_KPIS) $(X_TRAIN_FILLED_KPIS_QOQ) $(X_TEST_FILLED) $(X_TEST_FILLED_KPIS) $(X_TEST_FILLED_KPIS_QOQ)
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

# Train/Test split: produce all four outputs via a stamp file (this means it will only be done once not four times)
$(SPLIT_STAMP): datasets/Russell_3000_Cleaned.csv $(SPLIT_SCRIPT) | datasets $(VENV)/.deps
	cd $(SPLIT_DIR) && "$(PYTHON)" "../$(SPLIT_SCRIPT)" "Russell_3000_Cleaned.csv" "$(TARGET_TAG)"
	touch $@

$(X_TRAIN) $(Y_TRAIN) $(X_TEST) $(Y_TEST): $(SPLIT_STAMP)

clean-split:
	rm -f $(X_TRAIN) $(Y_TRAIN) $(X_TEST) $(Y_TEST) $(SPLIT_STAMP)

# Fill in the missing values for X_train and X_test
datasets/X_train_filled.csv datasets/X_test_filled.csv: \
        datasets/X_train.csv datasets/X_test.csv X_train_X_test_filled.py | datasets $(VENV)/.deps
	"$(PYTHON)" X_train_X_test_filled.py "datasets/X_train.csv" "datasets/X_test.csv" \
	    "datasets/X_train_filled.csv" "datasets/X_test_filled.csv"


# Add KPI for X_train_filled
datasets/X_train_filled_KPIs.csv: datasets/X_train_filled.csv make_KPIs.py | datasets $(VENV)/.deps
	"$(PYTHON)" make_KPIs.py $< $@

# Add KPI for X_test_filled
datasets/X_test_filled_KPIs.csv: datasets/X_test_filled.csv make_KPIs.py | datasets $(VENV)/.deps
	"$(PYTHON)" make_KPIs.py $< $@

# Add QoQ features for X_train_filled
datasets/X_train_filled_KPIs_QoQ.csv: datasets/X_train_filled_KPIs.csv make_QoQ.py | datasets $(VENV)/.deps
	"$(PYTHON)" make_QoQ.py $< $@

# Add QoQ features for X_test_filled
datasets/X_test_filled_KPIs_QoQ.csv: datasets/X_test_filled_KPIs.csv make_QoQ.py | datasets $(VENV)/.deps
	"$(PYTHON)" make_QoQ.py $< $@

# If the datasets directory does not exist, create it
datasets:
	mkdir -p $@