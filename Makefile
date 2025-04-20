
.PHONY: run
run:
	python manage.py runserver



.PHONY: worker
worker:
	watchmedo auto-restart --pattern="*.py" --recursive -- cmd /c "celery -A config worker -l INFO --pool=solo"



.PHONY: infra
infra:
	docker compose up -d test_melange test_bueno test_uklon database cache broker mailing

