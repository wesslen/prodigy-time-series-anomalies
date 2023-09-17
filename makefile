preprocess:
	python scripts/preprocessing.py "./data/MSFT.csv" "data/output_files" 176

get-images:
	python scripts/generate_plots.py "data/output_files/statistics.jsonl" 0.1 "data/output_files" "data/output_images"

prodigy-images:
	PRODIGY_LOGGING=verbose python -m prodigy classify-images data_anomaly ./data/output_images -F scripts/recipe.py

clean:
	rm -rf data/output_images
	rm -rf data/output_files
	python -m prodigy drop data_anomaly