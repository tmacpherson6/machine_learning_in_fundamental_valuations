.PHONY: all
all: datasets/Russell_3000_Fundamentals.csv

datasets/Russell_3000_Fundamentals.csv: data_acquisition.py datasets/Russell_3000.csv | datasets
	python data_acquisition.py datasets/Russell_3000.csv datasets/Russell_3000_Fundamentals.csv