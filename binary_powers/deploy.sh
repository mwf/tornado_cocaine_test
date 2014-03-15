tar czvf powers.tar.gz powers_worker.py
cocaine-tool app stop -n powers
cocaine-tool app upload --name powers --manifest manifest.json --package powers.tar.gz
cocaine-tool app start -n powers -r TestProfile