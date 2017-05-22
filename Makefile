run:
	echo "Hello"

install:
	pip install -r requirements.txt

venv:
	rm -rf env && mkdir env && virtualenv --system-site-packages env

.PHONY: install run venv