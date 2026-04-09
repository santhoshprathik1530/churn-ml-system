.PHONY: install train mlflow api test

install:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

train:
	. .venv/bin/activate && python -m pipeline.training_pipeline

mlflow:
	./scripts/start_mlflow_ui.sh

api:
	./scripts/start_api.sh

test:
	. .venv/bin/activate && pytest
