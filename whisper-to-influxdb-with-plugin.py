import whisper
import argparse
import os
import time
import subprocess
import time
import graphitesend


WHISPER_DIR = '/opt/graphite/whisper/'
WHISPER_INFO = '//anaconda/bin/whisper-fetch.py'
#WHISPER_INFO = 'whisper-fetch' # the whisper info command
FROM = '1478093280'
UNTIL = '1478094280'

GRAPHITE_SERVER = 'localhost'
GRAPHITE_PORT = 2013


def search_whisper_files(whisper_folder):
    """
    Given a directory return all the whisper files in the directory.
    :param directory:
    :return:
    """
    whisper_files = []
    for root, directories, files in os.walk(whisper_folder):
        for a_file in files:
            if a_file.endswith('.wsp'):
                whisper_files.append(os.path.join(root, a_file))

    return whisper_files


def read_whisper_file(whisper_file, from_time, until_time):
    """
    Given a whisper path, read it and return the data within a given time.
    :param whisper_file:
    :return:
    """
    command = [
        WHISPER_INFO, '--until='+until_time, '--from='+from_time,
        whisper_file,
    ]
    run_command = subprocess.Popen(command, stdout=subprocess.PIPE)
    stdout = run_command.communicate()[0]

    data = {}
    for line in stdout.split('\n'):
        try:
            time, value = line.split()[0], line.split()[1]
        except:
            continue
        if value != 'None':
            data[time] = float(value)

    return data


def main():
    """
    Loop through a directory, get all the .wsp files,
    Do a whisper-info on them
    Send the data using graphitesend with the directory path as the
    measurement. InfluxDB takes in the data as if it was graphite.
    """
    parser = argparse.ArgumentParser(
        description='Whisper file to InfluxDB migration script, '
                    'using the graphite influxdb plugin.'
                    'assumes that influxdb is running with graphite plugin '
                    'enabled')

    parser.add_argument('path', help='Path to the root whisper folder')
    parser.add_argument(
        '-graphite_host',
        default=GRAPHITE_SERVER,
        metavar='graphite_host',
        help='Graphite address')
    parser.add_argument(
        '-graphite_port',
        default=GRAPHITE_PORT,
        metavar='graphite_port',
        help='Graphite port')
    parser.add_argument(
        '-fromwhen',
        default=FROM,
        metavar='from when in unix epoch',
        help='From when, to transfer data')
    parser.add_argument(
        '-untilwhen',
        default=UNTIL,
        metavar='until when in unix epoch',
        help='Upto when, to transfer data')

    args = parser.parse_args()

    g = graphitesend.init(
        prefix='migrated',
        system_name='',
        graphite_server=args.graphite_host,
        graphite_port=int(args.graphite_port)
    )

    for whisper_file in search_whisper_files(args.path):
        metric = whisper_file.split('/whisper/')[1].split('.wsp')[0].replace(
            '/', '.')
        data = read_whisper_file(whisper_file, args.fromwhen, args.untilwhen)
        for time_stamo, value in data.iteritems():
            g.send(metric=metric, value=value, timestamp=float(time_stamo))
            # Sleep for 1 second, to give influxDB time to write the points
            time.sleep(1)


if __name__ == "__main__":
    main()
