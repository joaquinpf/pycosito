# pycosito
Un cosito. Very simple torrent downloads post processor for qbittorrent. uTorrent support no longer maintained and may not work :)

## Dependencies
Run pip install -r requirements.txt

## Config
[See sample config.json](../master/config.json)

## Usage
```
usage: pycosito.py [-h] -th TOR_API_TORRENT_HASH -k TOR_CLIENT_TYPE -e
                   TOR_API_ENDPOINT -u TOR_API_USERNAME -p TOR_API_PASSWORD
                   [-r] [-c CONFIG_FILE]

optional arguments:
  -h, --help            show this help message and exit
  -th TOR_API_TORRENT_HASH, --torrent-hash TOR_API_TORRENT_HASH
                        Hash for the torrent to process
  -k TOR_CLIENT_TYPE, --client TOR_CLIENT_TYPE
                        Torrent client type: utorrent | qbittorrent
  -e TOR_API_ENDPOINT, --endpoint TOR_API_ENDPOINT
                        Torrent API endpoint
  -u TOR_API_USERNAME, --username TOR_API_USERNAME
                        Torrent API username
  -p TOR_API_PASSWORD, --password TOR_API_PASSWORD
                        Torrent API password
  -r, --remove-torrent  Remove torrent from torrent client when done
  -c CONFIG_FILE, --config-file CONFIG_FILE
                        Configuration file to use for processing the torrent
```