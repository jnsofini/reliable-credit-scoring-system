
# test:
# 	pytest tests/

quality_checks:
	# isort .
	black src/
	pylint --recursive=y src/

preprocess: #quality_checks
	python -m src.preprocess

featurization:
	python -m src.featurization

clusters:
	python -m src.clustering 

scorecard:
	python -m src.scorecard 

data-reduction: preprocess featurization clusters

model-pipeline: data-reduction scorecard

tests: quality_checks
	pytest
