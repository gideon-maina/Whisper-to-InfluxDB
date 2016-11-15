Whisper-to-InfluxDB
===================

### script searches whisper files, reads them and creates datapoints in influxDB.

the script is a early proof of concept and might be using bulk commits or threading in the future.
the performance is __not mindblowing__ at the moment.


```bash
usage: whisper-to-influxdb-with-plugin.py [-h] [-graphite_host graphite_host]
                                          [-graphite_port graphite_port]
                                          [-fromwhen from when in unix epoch]
                                          [-untilwhen until when in unix epoch]
                                          path
```
                              
the script will parse the given path recursively and search for whisper files.
the found whisper files are being read and None values are omitted.

