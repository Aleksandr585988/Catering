
.PHONY: run
run:
	python manage.py runserver



.PHONY: worker
worker:
	watchmedo auto-restart --pattern="*.py" --recursive -- cmd /c "celery -A config worker -l INFO --pool=solo"



.PHONY: infra
infra:
	docker compose up -d test_melange test_bueno test_uklon database cache broker mailing

.PHONY: bueno
bueno:
	uvicorn tests.providers.bueno:app --reload --port 8002

.PHONY: melange
melange:
	uvicorn tests.providers.melange:app --reload --port 8001

.PHONY: uber
uber:
	uvicorn tests.providers.uber:app --reload --port 8004

.PHONY: uklon
uklon:
	uvicorn tests.providers.uklon:app --reload --port 8003

# ==================================================
# CODE QUALITY
# ==================================================
.PHONY: check
check:
	black --check ./
	isort --check ./
	flake8 ./
	mypy ./


.PHONY: quality
quality:
	black ./
	isort ./