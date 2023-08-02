
quality_checks:
	# isort .
	black batch/
	pylint --recursive=y batch/

# Deploy the monthly scoring
batch-deploy:
	python batch/score_deploy.py

# Run the monthly scoring
batch-run:
	python batch/score.py