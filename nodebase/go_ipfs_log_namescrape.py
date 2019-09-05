import json

import requests
import ipfsapi

from go_ipfs_log_scraper import many, key_if_present, LOG_URL


ipfs_client = ipfsapi.Client()


def get_agent(name):
    try:
        return ipfs_client.id(name)['AgentVersion']
    except ipfsapi.exceptions.ErrorResponse:
        return None


datafile = 'data/agents.json'
with open(datafile, 'rt') as f:
    agents = json.load(f)


def add_name(name):
    if name in agents:
        return
    agents[name] = get_agent(name)
    with open(datafile, 'wt') as f:
        json.dump(agents, f, indent=2, sort_keys=True)
    print(f'{len(agents)} nodes')


def message(msg):
    if ('message' in msg) and (msg['message'].get('type') == 'FIND_NODE'):
        add_name(msg['message'].get('key'))


if __name__ == '__main__':
    for peer in ipfs_client.swarm_peers()['Peers']:
        add_name(peer['Peer'])

    handler = many([
        key_if_present('peerID', add_name),
        key_if_present('peer', add_name),
        key_if_present("localPeer", add_name),
        key_if_present("remotePeer", add_name),
        message,
    ])

    for line in requests.get(LOG_URL, stream=True).iter_lines():
        handler(json.loads(line))
