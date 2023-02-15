# This is a sample Python script.
import fileinput
import re
import os
import json
import sys
import logging
from queue import PriorityQueue

logging.basicConfig(level=logging.INFO)


class AccessLogParser:

    def __init__(self, pattern, input_file, output_file, max_ips, max_paths):
        self.pattern = pattern
        self.input_file = input_file
        self.output_file = output_file
        self.max_ips = max_ips
        self.freq_heap = PriorityQueue(self.max_ips)
        self.max_paths = max_paths
        self.sum_heap = PriorityQueue(self.max_paths)
        self.ip_frequency_map = {}
        self.path_summation_map = {}
        self.processed_lines = 0
        self.unprocessed_lines = 0

    def parse(self, ):
        track_frequency_of_req_paths = {}
        for line in fileinput.input([self.input_file]):
            access_log = AccessLog()
            result = re.search(self.pattern, line)
            if result is not None:
                logging.debug("Processing line success --> " + line)
                self.processed_lines += 1
                match_count = 0
                for m in result.groups():
                    if match_count == 0:
                        access_log.ip_address = m
                    elif match_count == 1:
                        access_log.datetime = m
                    elif match_count == 2:
                        access_log.method = m
                    elif match_count == 3:
                        access_log.requested_path = m
                    elif match_count == 4:
                        access_log.status = m
                    elif match_count == 5:
                        access_log.bandwidth = m
                    elif match_count == 6:
                        access_log.referrer = m
                    elif match_count == 7:
                        access_log.user_agent = m
                    match_count += 1

                if access_log.ip_address in self.ip_frequency_map:
                    curr_frequency = self.ip_frequency_map[access_log.ip_address]
                    self.ip_frequency_map[access_log.ip_address] = curr_frequency + 1
                else:
                    self.ip_frequency_map[access_log.ip_address] = 1

                if access_log.requested_path in self.path_summation_map:
                    curr_latency_sum = self.path_summation_map[access_log.requested_path]
                    track_frequency_of_req_paths[access_log.requested_path] = int(track_frequency_of_req_paths[access_log.requested_path]) + 1
                    self.path_summation_map[access_log.requested_path] = (int(curr_latency_sum) + int(access_log.bandwidth))/track_frequency_of_req_paths[access_log.requested_path]
                else:
                    self.path_summation_map[access_log.requested_path] = access_log.bandwidth
                    track_frequency_of_req_paths[access_log.requested_path] = 1
            else:
                logging.info("Could not process line --> " + line)
                self.unprocessed_lines += 1

    def arrange(self, ):
        for key in self.ip_frequency_map:
            if len(self.freq_heap.queue) >= self.max_ips:
                self.freq_heap.get(True)
                self.put_in_freq_heap(key)
            else:
                self.put_in_freq_heap(key)
        for key in self.path_summation_map:
            key_ = int(self.path_summation_map[key])
            if len(self.sum_heap.queue) >= self.max_paths:
                self.sum_heap.get(True)
                self.put_in_sum_heap(key, key_)
            else:
                self.put_in_sum_heap(key, key_)

    def put_in_sum_heap(self, key, key_):
        try:
            self.sum_heap.put((+1 * key_, key))
        except KeyError as e:
            logging.info("Exception in `put_in_sum_heap` for key '" + key + "': " + repr(e))
        except TypeError as e:
            logging.info("Exception in `put_in_sum_heap` for key '" + key + "': " + repr(e))

    def put_in_freq_heap(self, key):
        try:
            self.freq_heap.put((+1 * self.ip_frequency_map[key], key))
        except KeyError as e:
            logging.info("Exception in `put_in_freq_heap` for key '" + key + "': " + repr(e))
            pass

    def display(self, ):
        display_ips = {}
        while len(self.freq_heap.queue) > 0:
            get = self.freq_heap.get(False)
            tuple_parts = str(get[1]) + ": " + str(get[0])
            display_ips[str(get[1])] = str(+1 * get[0])

        sum_paths = {}
        while len(self.sum_heap.queue) > 0:
            get = self.sum_heap.get(False)
            tuple_parts = str(get[1]) + ": " + str(get[0])
            sum_paths[str(get[1])] = str(+1 * get[0])

        total_number_of_lines = self.processed_lines + self.unprocessed_lines
        display = {
            "total_number_of_lines_processed": str(total_number_of_lines),
            "total_number_of_lines_ok": str(self.processed_lines),
            "total_number_of_lines_failed": str(self.unprocessed_lines),
            "top_client_ips": display_ips,
            "top_path_avg_seconds": sum_paths,
        }

        logging.debug(json.dumps(display, indent=4))
        results = open(self.output_file, "w")
        results.write(json.dumps(display, indent=4))


class AccessLog:

    def __init__(self, ):
        self.ip_address = ""
        self.datetime = ""
        self.method = ""
        self.requested_path = ""
        self.status = ""
        self.bandwidth = 0
        self.referrer = ""
        self.user_agent = ""

    def set_ip_address(self, ip_address):
        self.ip_address = ip_address

    def set_requested_path(self, requested_path):
        self.requested_path = requested_path

    def set_bandwidth(self, bandwidth):
        self.bandwidth = bandwidth


if __name__ == '__main__':
    nginx_access_logs_pattern = re.compile(r''
                         '(\d+.\d+.\d+.\d+)\s-\s-\s'  # IP address
                           '\[(.+)\]\s'  # datetime
                           '"(GET|POST|PUT|PATCH|DELETE|HEAD)\s(.+)\s\w+/.+"\s'  # requested file
                           '(\d+)\s'  # status
                           '(\d+)\s'  # bandwidth
                           '"(.+)"\s'  # referrer
                           '"(.+)"'  # user agent
                           )

    if os.getenv('input_file') is None or os.getenv('output_file') is None:
        logging.info("Usage ")
        logging.info("\tinput_file and output_file are required arguments and has the form <filename.log> which must be supplied on container mount")
        logging.info("\tCommand : docker run -v $(pwd)/input.log:/opt/input.log -e input_file=input.log -v $(pwd):/opt:Z -e output_file=results.json <image>")
        logging.info("program exiting ... ")
        sys.exit(-1)

    input_file = os.environ.get('input_file')
    output_file = os.environ.get('output_file')
    max_ips = 10 if os.environ.get('max_ips') is None else os.environ.get('max_ips')
    max_paths = 10 if os.environ.get('max_paths') is None else os.environ.get('max_paths')

    accessLogParser = AccessLogParser(nginx_access_logs_pattern, input_file, output_file, max_ips, max_paths)
    accessLogParser.parse()
    accessLogParser.arrange()
    accessLogParser.display()

