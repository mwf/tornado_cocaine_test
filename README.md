Tornado + Cocaine
============

Test Tornado behavior with Yandex [cocaine-framework-python](https://github.com/cocaine/cocaine-framework-python)

Requirements
---------------

Cocaine core and framework must be installed.


Installation
---------------

1. Install requirements

2. Deploy cocaine workers:

	```
	./initial_deploy.sh
	./deploy_all.sh
	```

3. Run Tornado HTTP Proxy service

	```
	python http_proxy/manager.py
	```

4. Test service with ```ab``` tool using test_data

	```
	ab -T 'application/json' -p ./test_data/10s_verbose.json -n 100 -c 10 http://localhost:8888/sleepy/
	```
	
	Or using ```curl```
	
	```
	curl -N -H "Content-Type: application/json" --data @/test_data/10s_verbose.json http://localhost:8888/sleepy/
	```
