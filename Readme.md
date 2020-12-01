**AXA Assignment**

Fill Allocation System: 

##Description:
```
    Each server in this application is independently deployable and hence application is cloud native 
    and is implemented a combination of 4 microsevices:
    - 1 AUM Server: Provide account allocation every 10 seconds
    - X Fill Server: Provide stock ticks at random intervals.
        NOTE: You can change number of fill servers by: 
            _If running on local machine: modifying instances in `run.bat`
            If running in container: modify replicas in `docker-compose.yml`_
    - 1 Position Server : Displays positions every 30 seconds
    - 1 Controller : Act as manager / observer 
```
##Usage :
````
    1. run.bat (if you want to run on local machine)
    2. docker-compose.yml run (if deploying in container)
````
##Architecture : 
                                
                                  AUM SERVER
                                      |
                                     [MQ]
                                      |                            
    FILL SERVER----->[MQ]---|         |
                            |         V
    FILL SERVER----->[MQ]---|---->CONTROLLER-----[MQ]-----> POSITION SERVER
                            | 
    FILL SERVER----->[MQ]---|
