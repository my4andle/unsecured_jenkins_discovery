#!/usr/bin/python3
"""
Usage:
  jenkins_unsecured_instance_discovery.py -h | --help
  jenkins_unsecured_instance_discovery.py (--rhosts=<rhosts>)
 
Options:
  --rhosts=<rhosts> targets to test
"""

import json
import requests
import concurrent.futures

from docopt import docopt


def generate_list_from_file(data_file):
    """
    Generate a list from a given file containing a single line of desired data, intended for IPv4 and passwords.

    Args:
        file: A file containing a single password or IPv4 address per line

    Returns:
        A list of passwords, IPv4
    """
    print("Generating set from: {}".format(data_file))
    data_list = []
    with open(data_file, 'r') as my_file:
        for line in my_file:
            data_list.append(line.strip('\n').strip(' '))
    return set(data_list)

def test_url(ip, port=8080):
    """Check url for unsecured configure"""
    url = "http://{}:{}/configure".format(ip, str(port))
    print("Testing url: {}".format(url))
    try:
        req = requests.get(url, timeout=5)
        if req.status_code == 200:
            print("unsecure jenkins instance: {}".format(url))
            return ip
    except:
        pass

def test_url_concurrent(rhosts: list):
    """
    Test all given Jenkins servers for a response at the configure url path without authentication

    Args:
        rhosts: List of target IP addresses

    Returns:
        A list of dictionaries with the url results of all unsecured jenkins instances.
    """
    print("Entering concurrent url test")
    results_list = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=50) as pool:
        results = {pool.submit(test_url, ip): ip for ip in rhosts}
        for future in concurrent.futures.as_completed(results):
            if future.result():
                results_list.append(future.result())
    return results_list

def main():
    """Run it"""
    opts = docopt(__doc__)
    rhosts_set = generate_list_from_file(opts['--rhosts'])
    unsecured_jenkins = test_url_concurrent(rhosts_set)
    secured_jenkins = [x for x in rhosts_set if x not in unsecured_jenkins]
    print("Secured instances of Jenkins: {}".format(len(secured_jenkins)))
    print("Unsecured instances of jenkins: {}".format(len(unsecured_jenkins)))
    final_results = {"Unsecured Jenkins": unsecured_jenkins, "Secured Jenkins": secured_jenkins}
    print(json.dumps(final_results,sort_keys=True, indent=4))

if __name__ == '__main__':
    main()
