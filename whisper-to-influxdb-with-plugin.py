import argparse
import multiprocessing
import os
import subprocess
import time

import graphitesend
from joblib import Parallel, delayed

WHISPER_DIR = '/opt/graphite/whisper/'

def search_whisper_files(whisper_folder):
    """
    Given a directory return all the whisper files in the directory.
    :param whisper_folder: The whisper root directory.
    :return: All .wsp files , full paths in all the sub directories.
    """
    for root, directories, files in os.walk(whisper_folder):
        for whisper_file in files:
            if whisper_file.endswith('.wsp'):
                yield os.path.join(root, whisper_file)


def get_metric_name(whisper_file):
    metric_name = whisper_file.split('/whisper/')[1].split('.wsp')[0].replace(
        '/', '.')

    return metric_name


def read_whisper_file(whisper_file, from_time, until_time):
    """
    Given a whisper path, read it and return the data within a given time.
    :param whisper_file: a given full path to a whisper file.
    :param from_time: from when to read the stored metrics (in unix epoch).
    :param until_time: upto when  to read the stored metrics (in unix epoch).
    :return: data in the whisper file within the specfied time range.
            the data is a dict with time_stamp as key and metric value as
            the value.
    """
    WHISPER_FETCH = 'whisper-fetch.py'  # The whisper fetch command

    command = [
        WHISPER_FETCH, '--until=' + until_time, '--from=' + from_time,
        whisper_file,
    ]
    run_command = subprocess.Popen(command, stdout=subprocess.PIPE)
    stdout = run_command.communicate()[0]

    data = {}
    for line in stdout.split('\n'):
        contents = line.split()
        try:
            time, value = contents[0], contents[1]
        except IndexError:
            continue
        if value != 'None':
            data[time] = float(value)

    return data


def send_metrics(whisper_file, time_stamp, value, args):
    """
    Send a given whisper file's data to InfluxDB
    :param whisper_file: The compelte path to the whisper file.
    :param time_stamp:  The time stamp for value in unix epoch
    :param value: The value of the metric at time timestamp
    :param args: the configparser object
    """
    metric = get_metric_name(whisper_file)
    system_name = metric.split('.', 1)[0]
    metric_name = metric.split('.', 1)[1]

    print metric_name
    g = graphitesend.init(
        prefix='',
        system_name=system_name,
        graphite_server=args.influxdb_host,
        graphite_port=int(args.influxdb_port)
    )
    g.send(metric=metric_name, value=value, timestamp=float(time_stamp))
    # Sleep for 50 millisecond, to give influxDB time to write the points
    time.sleep(0.02)


def get_args():
    """
    Get command line arguments and pass them on.
    :return: configparser object
    """
    parser = argparse.ArgumentParser(
        description='Whisper file to InfluxDB migration script, '
                    'using the graphite influxdb plugin. '
                    'Assumes that influxdb is running with graphite plugin '
                    'enabled')

    parser.add_argument('path', help='Path to the root whisper folder')
    parser.add_argument(
        '-influxdb_host',
        metavar='influxdb_host',
        help='InfluxDB address')
    parser.add_argument(
        '-influxdb_port',
        metavar='influxdb_port graphite port',
        help='Influxdb graphite port')
    parser.add_argument(
        '-fromwhen',
        metavar='from when in unix epoch',
        help='From when, to transfer data')
    parser.add_argument(
        '-until',
        metavar='until when in unix epoch',
        help='Upto when, to transfer data')

    return parser.parse_args()


def main():
    """
    Loop through a directory, get all the .wsp files,
    Do a whisper-fetch on them and return the data.
    Send the data using graphitesend with the directory path as the
    measurement.InfluxDB takes in the data as if it was graphite.
    """
    cpus = multiprocessing.cpu_count()
    parallel = Parallel(n_jobs=cpus)

    args = get_args()

    parallel(delayed(send_metrics)(whisper_file, time_stamp, value, args)
             for whisper_file in search_whisper_files(args.path)
             for time_stamp, value in
             read_whisper_file(whisper_file, args.fromwhen,
                               args.until).iteritems()
             )


if __name__ == "__main__":
    main()
