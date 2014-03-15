tar czvf sleepy.tar.gz sleepy_worker.py
cocaine-tool app stop -n sleepy
cocaine-tool app upload --name sleepy --manifest manifest.json --package sleepy.tar.gz
cocaine-tool app start -n sleepy -r TestProfile