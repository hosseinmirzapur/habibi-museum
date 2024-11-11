activate:
	source bookstore_env/bin/activate

v1:
	python scrapper_v1.py
v2:
	python scrapper_v2.py

.PHONY: activate v1 v2