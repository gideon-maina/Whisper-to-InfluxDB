Whisper-to-InfluxDB
===================

The script searches for all whisper files, reads them and creates datapoints in InfluxDB.

How it works
============
InfluxDB supports the graphite input protocol and can be enabled in the InfluxDB config.
Here is a section of the influxdb.conf, showing how graphite input can be accepted
```bash
...
[[graphite]]
  enabled = true
  database = "graphite"
  bind-address = ":2003"
  protocol = "tcp"
  consistency-level = "one"
 ...
 ```

If the influxDB service is running with the above graphite input enabled, then this script will work.

Requirements
============
* You have InfluxDB running with graphite plugin enabled.
* Access to the InfluxDB server

Usage
=====
Expects to called in the command prompt with the correct arguments and the whisper directory path.


```bash
python whisper-to-influxdb-with-plugin.py
usage: whisper-to-influxdb-with-plugin.py [-h] [-influxdb_host influxdb_host]
                                          [-influxdb_port influxdb_port graphite port]
                                          [-fromwhen from when in unix epoch]
                                          [-untilwhen until when in unix epoch]
                                          path
```
                              
The script will go through the given path recursively and search for all whisper files.

The found whisper files are read and None values are omitted.

Then path of the whisper file is 'split' to build a similar long name to be used as the 
measurement in InfluxDB.

The metric is then sent to the InfluxDB server.

Example Output
==============
Directory path and contents
```bash
	/home/user/whisper/
		── whisper
	│   ├── host1
	│   │   └── cpuload
	│   │       ├── avg1.wsp
	│   │       ├── avg15.wsp
	│   │       └── avg5.wsp
```

Output from the script (Also sends the data to InfluxDB)
```bash
	host1.cpuload.avg1
	host1.cpuload.avg15
	host1.cpuload.avg5
```

TODO
====
* Improve on performance.
* Test on large whisper data sets.

