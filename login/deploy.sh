tar czvf login.tar.gz login_worker.py
cocaine-tool app stop -n login
cocaine-tool app upload --name login --manifest manifest.json --package login.tar.gz
cocaine-tool app start -n login -r TestProfile