import abc
import logging
from utorrentapi import UTorrentAPI
from qbittorrent import Client

logger = logging.getLogger(__name__)


class TorrentClient(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, endpoint, username, password):
        pass

    @abc.abstractmethod
    def get_torrent_info(self, torrent_hash):
        pass

    @abc.abstractmethod
    def remove_torrent(self, torrent_hash):
        pass

    @abc.abstractmethod
    def stop_torrent(self, torrent_hash):
        pass

    @abc.abstractmethod
    def get_torrent_files(self, torrent_hash):
        pass


class Torrent(object):
    def __init__(self, hash, complete, label, base_folder):
        self._hash = hash
        self._complete = complete
        self._label = label
        self._base_folder = base_folder

    @property
    def hash(self):
        return self._hash

    @property
    def complete(self):
        return self._complete

    @property
    def label(self):
        return self._label

    @property
    def base_folder(self):
        return self._base_folder


class TorrentFile(object):
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name


class UtorrentClient(TorrentClient):
    def __init__(self, endpoint, username, password):
        self._api_client = UTorrentAPI(endpoint, username, password)
        if not self._api_client:
            message = "Unable to connect to uTorrent Web API. Please check your -e, -u and -p arguments."
            logger.error(message)
            raise Exception(message)

    def get_torrent_info(self, torrent_hash):
        torrents = self._api_client.get_list()

        for torrent in torrents['torrents']:
            if torrent[0] == torrent_hash:
                return Torrent(torrent_hash, torrent[4], torrent[11], torrent[26], torrent[2])

        return None

    def remove_torrent(self, torrent_hash):
        self._api_client.removedata(torrent_hash)

    def stop_torrent(self, torrent_hash):
        self._api_client.stop(torrent_hash)

    def get_torrent_files(self, torrent_hash):
        return self._api_client.get_files(torrent_hash)


class QBittorrentClient(TorrentClient):
    def __init__(self, endpoint, username, password):
        self._api_client = Client(endpoint)
        self._api_client.login(username, password)
        if not self._api_client:
            message = "Unable to connect to qBittorrent API. Please check your -e, -u and -p arguments."
            logger.error(message)
            raise Exception(message)

    def get_torrent_info(self, torrent_hash):
        torrents = self._api_client.torrents()

        for torrent in torrents:
            if torrent['hash'] == torrent_hash:
                return Torrent(torrent_hash, torrent['progress'] == 1, torrent['category'], torrent['save_path'])

        return None

    def remove_torrent(self, torrent_hash):
        self._api_client.delete_permanently(torrent_hash)

    def stop_torrent(self, torrent_hash):
        self._api_client.pause(torrent_hash)

    def get_torrent_files(self, torrent_hash):
        files = self._api_client.get_torrent_files(torrent_hash)
        parsed_files = []
        for file in files:
            if ".unwanted" not in file['name']:
                parsed_files.append(TorrentFile(file['name']))

        return parsed_files
