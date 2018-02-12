# !/usr/bin/env python
# -*- coding: utf-8 -*-

import ntpath
import os
import shutil
import sys
import json
from argparse import ArgumentParser
import logging
from logging.handlers import RotatingFileHandler
import traceback
from torrent_client import UtorrentClient, QBittorrentClient

clients = {'utorrent': UtorrentClient,
           'qbittorrent': QBittorrentClient}


def filter_file(key):
    key_lower = key.lower()
    return key_lower.endswith(
        ('.dat', '.txt', '.nfo', '.sfv', '.jpg', '.png', '.gif', '.html')) or 'sample' in key_lower


def get_final_name(dst_dir, basename):
    head, tail = os.path.splitext(basename)
    dst_file = os.path.join(dst_dir, basename)
    # rename if necessary
    count = 0
    while os.path.exists(dst_file):
        count += 1
        dst_file = os.path.join(dst_dir, '%s-%d%s' % (head, count, tail))
    return dst_file


def setup_logging():
    global logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    # create the console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    # create a file handler
    handler = RotatingFileHandler('processor.log', maxBytes=20000000, backupCount=10)
    handler.setLevel(logging.INFO)
    # create a logging format
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(handler)
    logger.addHandler(ch)


def main():
    parser = ArgumentParser()

    # Add more options if you like
    parser.add_argument("-th", "--torrent-hash", dest="tor_api_torrent_hash",
                        help="Hash for the torrent to process", required=True)
    parser.add_argument("-k", "--client", dest="tor_client_type",
                        help="Torrent client type: utorrent | qbittorrent", required=True)
    parser.add_argument("-e", "--endpoint", dest="tor_api_endpoint",
                        help="Torrent API endpoint", required=True)
    parser.add_argument("-u", "--username", dest="tor_api_username",
                        help="Torrent API username", required=True)
    parser.add_argument("-p", "--password", dest="tor_api_password",
                        help="Torrent API password", required=True)
    parser.add_argument("-r", "--remove-torrent", dest="tor_api_remove_torrent",
                        help="Remove torrent from torrent client when done", required=False, action='store_true')
    parser.add_argument("-c", "--config-file", dest="config_file",
                        help="Configuration file to use for processing the torrent", required=False,
                        default='config.json')

    args = parser.parse_args()

    if not os.path.exists(args.config_file):
        logger.error("Configuration file doesn't exist. Please check your -c parameter")
        sys.exit(-1)

    with open(args.config_file) as config_file:
        config = json.load(config_file)

    api_client = clients[args.tor_client_type](args.tor_api_endpoint, args.tor_api_username, args.tor_api_password)

    torrent_hash = args.tor_api_torrent_hash

    torrent_info = api_client.get_torrent_info(torrent_hash)
    if not torrent_info.complete:
        logger.error("Torrent isn't done downloading.")
        sys.exit(-1)

    if not torrent_info.label or not config[torrent_info.label]:
        config_section = config['DEFAULT']
    else:
        config_section = config[torrent_info.label]

    if not config_section:
        logger.error("No action configured for this label and default doesn't exist.")
        sys.exit(-1)

    api_client.stop_torrent(torrent_hash)
    torrent_files = api_client.get_torrent_files(torrent_hash)

    clean_up = config_section['clean_up']
    keep_folders = config_section['keep_directory_structure']
    target_base_folder = config_section['move_to']

    for torrent_file in torrent_files:
        name = torrent_file.name

        source_path = torrent_info.base_folder + '\\' + name
        if not os.path.exists(source_path):
            logger.info("Filtering file '%s' since it wasn't downloaded" % source_path)
            continue

        if clean_up and filter_file(source_path):
            logger.info("Filtering file '%s' due to cleanup rules" % source_path)
            continue

        if keep_folders:
            target_path = get_final_name(target_base_folder, name)
        else:
            target_path = get_final_name(target_base_folder, ntpath.basename(source_path))

        logger.info("Moving file from '%s' to '%s'" % (source_path, target_path))
        if not os.path.exists(ntpath.dirname(target_path)):
            os.makedirs(ntpath.dirname(target_path))

        shutil.move(source_path, target_path)

    if args.tor_api_remove_torrent:
        logger.info("Deleting torrent info and source base folder '%s'" % torrent_info.base_folder)
        api_client.remove_torrent(torrent_hash)


if __name__ == "__main__":
    setup_logging()
    try:
        main()
    except:
        logger.error(traceback.format_exc())
