# Connecting to ZKTeco devices

First, go to the `ZKTeco` directory.

### For add a device:
`python main.py add_device --ip IP [--port PORT] [--timeout TIMEOUT] [--password PASSWORD] --location LOCATION
`

### For show all devices:
`python main.py show_devices`


### For show delete a device:
`python main.py delete_device --id ID`


### For all attendances which are related to a device:
`python main.py get_attendances [--id ID]`
