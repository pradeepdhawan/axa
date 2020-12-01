start /B python.exe FillServer\FillServer.py tcp://*:8080
start /B python.exe FillServer\FillServer.py tcp://*:8081
start /B python.exe AUMServer\AUMServer.py tcp://*:7777
start /B python.exe PositionServer\PositionServer.py tcp://localhost:9999
python.exe Controller\Controller.py tcp://*:9999 tcp://localhost:7777 tcp://localhost:8080 tcp://localhost:8081
pause