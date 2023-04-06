# Connecting to ZKTeco devices

First, go to the `ZKTeco` directory.

### For add a device:

`python main.py add-device --ip IP [--port PORT] [--timeout TIMEOUT] [--password PASSWORD] --comment LOCATION
`

### For show all devices:

`python main.py list-devices`

### For delete a device:

`python main.py delete-device --id ID`

### For all attendances which are related to a device:

`python main.py get-attendances [--id ID]`

### To Upload attendances to Odoo:

`python main.py get-attendances [--id ID]`

# Setup:

Device List:

| IP            | Serial Number | Comment    | Odoo Endpoint Address                      |
|:--------------|:-------------:|:-----------|:-------------------------------------------|
| 192.168.5.206 | BRM9203760786 | DyBuG      | https://dybug.ir/iclock/upload-attendances |
| 192.168.5.207 | ADWZ184560363 | Scarf Bank |                                            |
| 192.168.6.207 | BRM9203760463 | Factory    |                                            |

1. you need to define your devices:

   ```shell
   ./odoo-zkteco-agent.py --database /opt/odoo-zkteco-agent/zkteco.sqlite3 add-device --ip 192.168.5.206 --sn BRM9203760786 --odoo-endpoint "https://dybug.ir/iclock/upload-attendances" --comment "DyBuG"
   ./odoo-zkteco-agent.py --database /opt/odoo-zkteco-agent/zkteco.sqlite3 add-device --ip 192.168.5.207 --sn ADWZ184560363 --comment "Scarf Bank"
   ./odoo-zkteco-agent.py --database /opt/odoo-zkteco-agent/zkteco.sqlite3 add-device --ip 192.168.6.207 --sn BRM9203760463 --comment "Factory" --timeout 30
   ```

2. Fetch all attendances

   ```shell
   ./odoo-zkteco-agent.py --database /opt/odoo-zkteco-agent/zkteco.sqlite3 get-attendances
   ```

3. Mark all old attendances that you don't want to be loaded to odoo as Uploaded:

  ```sqlite
  UPDATE attendances
  SET is_sent = TRUE
      -- 2023-03-21 is 1402-01-01
  where date(day_time) < date('2023-03-21')
    and device_id = 1;

  UPDATE attendances
  SET is_sent = TRUE
  where is_sent = False
    and device_id = 1
    and user_id in (72, 1, 56, 71);
   ```

4. Create a cron job for fetching new attendances and uploading them to Odoo

   ```shell
   30 */4 * * * /opt/odoo-zkteco-agent/odoo-zkteco-agent.py --database /opt/odoo-zkteco-agent/zkteco.sqlite3 get-attendances; /opt/odoo-zkteco-agent/odoo-zkteco-agent.py --database /opt/odoo-zkteco-agent/zkteco.sqlite3 upload --id 1;
   ```
5. 