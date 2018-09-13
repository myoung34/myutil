test:
	flake8 myutil
	#PYTHONPATH=$(shell pwd) py.test tests
	py.test tests

install:
	python setup.py install

.PHONY: build push
