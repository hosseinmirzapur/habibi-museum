activate:
	@source bookstore_env/bin/activate

clean:
	@rm -rf ./scraped_data/*

v1:
	@python scrapper_v1.py
v2:
	@python scrapper_v2.py
v3:
	@python scrapper_v3.py

.PHONY: activate clean v1 v2 v3