
# test:
# 	pytest tests/

quality_checks:
	isort .
	black .
	pylint --recursive=y .

preprocess: #quality_checks
	python -m src.preprocess

featurization:
	python -m src.featurization

clusters:
	python -m src.clustering 

scorecard:
	python -m src.scorecard 
