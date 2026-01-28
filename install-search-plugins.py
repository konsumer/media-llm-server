#!/usr/bin/env python3
"""
Download qBittorrent search plugins from official and unofficial sources.
Usage: python3 install-search-plugins.py [--official] [--unofficial] [--all]
"""

import argparse
import json
import os
import re
import sys
import urllib.request
from pathlib import Path
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup

# Configuration
PLUGINS_DIR_DEFAULT = "./config/qbittorrent/qBittorrent/nova3/engines"

# these are pulled from
# https://github.com/qbittorrent/search-plugins/tree/master/nova3/engines
# https://github.com/qbittorrent/search-plugins/wiki/Unofficial-search-plugins
# there were some dead, so I tried to find them

plugins = {
  "official": {
    "eztv": "https://raw.githubusercontent.com/qbittorrent/search-plugins/master/nova3/engines/eztv.py",
    "jackett": "https://raw.githubusercontent.com/qbittorrent/search-plugins/master/nova3/engines/jackett.py",
    "limetorrents": "https://raw.githubusercontent.com/qbittorrent/search-plugins/master/nova3/engines/limetorrents.py",
    "piratebay": "https://raw.githubusercontent.com/qbittorrent/search-plugins/master/nova3/engines/piratebay.py",
    "solidtorrents": "https://raw.githubusercontent.com/qbittorrent/search-plugins/master/nova3/engines/solidtorrents.py",
    "torlock": "https://raw.githubusercontent.com/qbittorrent/search-plugins/master/nova3/engines/torlock.py",
    "torrentproject": "https://raw.githubusercontent.com/qbittorrent/search-plugins/master/nova3/engines/torrentproject.py",
    "torrentscsv": "https://raw.githubusercontent.com/qbittorrent/search-plugins/master/nova3/engines/torrentscsv.py"
  },
  "unofficial": {
    "academictorrents": "https://raw.githubusercontent.com/LightDestory/qBittorrent-Search-Plugins/master/src/engines/academictorrents.py",
    "acgrip": "https://raw.githubusercontent.com/Cc050511/qBit-search-plugins/main/acgrip.py",
    "ali213": "https://raw.githubusercontent.com/hannsen/qbittorrent_search_plugins/master/ali213.py",
    "anidex": "https://raw.githubusercontent.com/nindogo/qbtSearchScripts/master/anidex.py",
    "animetosho": "https://raw.githubusercontent.com/AlaaBrahim/qBitTorrent-animetosho-search-plugin/main/animetosho.py",
    "audiobookbay": "https://raw.githubusercontent.com/nklido/qBittorrent_search_engines/master/engines/audiobookbay.py",
    "bitsearch": "https://raw.githubusercontent.com/BurningMop/qBittorrent-Search-Plugins/refs/heads/main/bitsearch.py",
    "bt4gprx": "https://raw.githubusercontent.com/TuckerWarlock/qbittorrent-search-plugins/main/bt4gprx.com/bt4gprx.py",
    "btdig": "https://raw.githubusercontent.com/galaris/BTDigg-qBittorrent-plugin/main/btdig.py",
    "calidadtorrent": "https://raw.githubusercontent.com/BurningMop/qBittorrent-Search-Plugins/refs/heads/main/calidadtorrent.py",
    "cloudtorrents": "https://raw.githubusercontent.com/elazar/qbittorrent-search-plugins/refs/heads/add-cloudtorrents-plugin/nova3/engines/cloudtorrents.py",
    "cpasbien": "https://raw.githubusercontent.com/MarcBresson/cpasbien/master/src/cpasbien.py",
    "darklibria": "https://raw.githubusercontent.com/bugsbringer/qbit-plugins/master/darklibria.py",
    "divxtotal": "https://raw.githubusercontent.com/BurningMop/qBittorrent-Search-Plugins/refs/heads/main/divxtotal.py",
    "dmhy": "https://raw.githubusercontent.com/ZH1637/dmhy/main/dmhy.py",
    "dodi_repacks": "https://raw.githubusercontent.com/Bioux1/qbtSearchPlugins/main/dodi_repacks.py",
    "dontorrent": "https://raw.githubusercontent.com/dangar16/dontorrent-plugin/main/dontorrent.py",
    "elitetorrent": "https://raw.githubusercontent.com/iordic/qbittorrent-search-plugins/master/engines/elitetorrent.py",
    "esmeraldatorrent": "https://raw.githubusercontent.com/BurningMop/qBittorrent-Search-Plugins/refs/heads/main/esmeraldatorrent.py",
    "fitgirl_repacks": "https://raw.githubusercontent.com/Bioux1/qbtSearchPlugins/main/fitgirl_repacks.py",
    "glotorrents": "https://raw.githubusercontent.com/LightDestory/qBittorrent-Search-Plugins/master/src/engines/glotorrents.py",
    "kickasstorrents": "https://raw.githubusercontent.com/LightDestory/qBittorrent-Search-Plugins/master/src/engines/kickasstorrents.py",
    "linuxtracker": "https://raw.githubusercontent.com/MadeOfMagicAndWires/qBit-plugins/6074a7cccb90dfd5c81b7eaddd3138adec7f3377/engines/linuxtracker.py",
    "magnetdl": "https://raw.githubusercontent.com/nindogo/qbtSearchScripts/master/magnetdl.py",
    "maxitorrent": "https://raw.githubusercontent.com/joseeloren/search-plugins/master/nova3/engines/maxitorrent.py",
    "mejortorrent": "https://raw.githubusercontent.com/iordic/qbittorrent-search-plugins/master/engines/mejortorrent.py",
    "mikan": "https://raw.githubusercontent.com/Cycloctane/qBittorrent-plugins/master/engines/mikan.py",
    "mikanani": "https://raw.githubusercontent.com/Cc050511/qBit-search-plugins/main/mikanani.py",
    "mypornclub": "https://raw.githubusercontent.com/BurningMop/qBittorrent-Search-Plugins/refs/heads/main/mypornclub.py",
    "naranjatorrent": "https://raw.githubusercontent.com/BurningMop/qBittorrent-Search-Plugins/refs/heads/main/naranjatorrent.py",
    # "pantsu": "https://raw.githubusercontent.com/libellula/qbt-plugins/main/pantsu.py",
    "nyaapantsu": "https://raw.githubusercontent.com/MadeOfMagicAndWires/qBit-plugins/refs/heads/main/engines/nyaapantsu.py",
    "nyaasi": "https://raw.githubusercontent.com/MadeOfMagicAndWires/qBit-plugins/master/engines/nyaasi.py",
    "onlinefix": "https://raw.githubusercontent.com/caiocinel/onlinefix-qbittorrent-plugin/main/onlinefix.py",
    "pediatorrent": "https://raw.githubusercontent.com/dangar16/pediatorrent-plugin/refs/heads/main/pediatorrent.py",
    "pirateiro": "https://raw.githubusercontent.com/LightDestory/qBittorrent-Search-Plugins/master/src/engines/pirateiro.py",
    "rockbox": "https://raw.githubusercontent.com/LightDestory/qBittorrent-Search-Plugins/master/src/engines/rockbox.py",
    "rutor": "https://raw.githubusercontent.com/imDMG/qBt_SE/master/engines/rutor.py",
    "sktorrent": "https://raw.githubusercontent.com/Ashalda/sktorrent-qbt/refs/heads/main/sktorrent.py",
    "smallgames": "https://raw.githubusercontent.com/hannsen/qbittorrent_search_plugins/master/smallgames.py",
    "snowfl": "https://raw.githubusercontent.com/LightDestory/qBittorrent-Search-Plugins/master/src/engines/snowfl.py",
    "solidtorrents": "https://raw.githubusercontent.com/BurningMop/qBittorrent-Search-Plugins/refs/heads/main/solidtorrents.py",
    "subsplease": "https://raw.githubusercontent.com/kli885/qBittorent-SubsPlease-Search-Plugin/main/subsplease.py",
    "sukebeisi": "https://github.com/vt-idiot/qBit-SukebeiNyaa-plugin/raw/master/engines/sukebeisi.py",
    "nyaa": "https://raw.githubusercontent.com/phuongtailtranminh/qBittorrent-Nyaa-Search-Plugin/master/nyaa.py",
    # "sukebei": "https://raw.githubusercontent.com/libellula/qbt-plugins/main/sukebei.py",
    "thepiratebay": "https://raw.githubusercontent.com/LightDestory/qBittorrent-Search-Plugins/master/src/engines/thepiratebay.py",
    "therarbg": "https://raw.githubusercontent.com/BurningMop/qBittorrent-Search-Plugins/refs/heads/main/therarbg.py",
    "tomadivx": "https://raw.githubusercontent.com/BurningMop/qBittorrent-Search-Plugins/refs/heads/main/tomadivx.py",
    # "tokyotoshokan": "https://raw.githubusercontent.com/BrunoReX/qBittorrent-Search-Plugin-TokyoToshokan/master/tokyotoshokan.py",
    "torrent9": "https://raw.githubusercontent.com/menegop/qbfrench/master/torrent9.py",
    "torrentdownload": "https://raw.githubusercontent.com/LightDestory/qBittorrent-Search-Plugins/master/src/engines/torrentdownload.py",
    "torrentdownloads": "https://raw.githubusercontent.com/BurningMop/qBittorrent-Search-Plugins/refs/heads/main/torrentdownloads.py",
    # "torrenflix": "https://raw.githubusercontent.com/BurningMop/qBittorrent-Search-Plugins/refs/heads/main/torrenflix.py",
    "torrentgalaxy": "https://raw.githubusercontent.com/nindogo/qbtSearchScripts/master/torrentgalaxy.py",
    "traht": "https://raw.githubusercontent.com/BurningMop/qBittorrent-Search-Plugins/refs/heads/main/traht.py",
    "uniondht": "https://raw.githubusercontent.com/msagca/qbittorrent-plugins/main/uniondht.py",
    "xxxclubto": "https://raw.githubusercontent.com/BurningMop/qBittorrent-Search-Plugins/refs/heads/main/xxxclubto.py",
    "yourbittorrent": "https://raw.githubusercontent.com/LightDestory/qBittorrent-Search-Plugins/master/src/engines/yourbittorrent.py",
    "yggtracker": "https://raw.githubusercontent.com/YGGverse/qbittorrent-yggtracker-search-plugin/main/yggtracker.py",
    "zooqle": "https://raw.githubusercontent.com/444995/qbit-search-plugins/main/engines/zooqle.py"
  },
  "private": {
    "bakabt": "https://raw.githubusercontent.com/MadeOfMagicAndWires/qBit-plugins/master/engines/bakabt.py",
    "danishbytes": "https://raw.githubusercontent.com/444995/qbit-search-plugins/main/engines/danishbytes.py",
    "filelist": "https://raw.githubusercontent.com/PricopeStefan/Filelist-QBitTorrent-Plugin/refs/heads/main/filelist.py",
    "gazellegames": "https://raw.githubusercontent.com/Ooggle/qbittorrent-search-plugins/master/engines/gazellegames.py",
    "iptorrents": "https://raw.githubusercontent.com/txtsd/qB-IPT/master/iptorrents.py",
    "kinozal": "https://raw.githubusercontent.com/imDMG/qBt_SE/master/engines/kinozal.py",
    "lostfilm": "https://raw.githubusercontent.com/bugsbringer/qbit-plugins/master/lostfilm.py",
    "ncore": "https://raw.githubusercontent.com/darktohka/qbittorrent-plugins/master/ncore.py",
    "nnmclub": "https://raw.githubusercontent.com/imDMG/qBt_SE/master/engines/nnmclub.py",
    "pornolab": "https://raw.githubusercontent.com/TainakaDrums/qbPornolab/master/pornolab.py",
    "redacted_ch": "https://raw.githubusercontent.com/evyd13/search-plugins/master/nova3/engines/redacted_ch.py",
    "rutracker": "https://raw.githubusercontent.com/imDMG/qBt_SE/master/engines/rutracker.py",
    "torrentleech": "https://raw.githubusercontent.com/444995/qbit-search-plugins/main/engines/torrentleech.py",
    "prowlarr": "https://raw.githubusercontent.com/swannie-eire/prowlarr-qbittorrent-plugins/main/prowlarr.py",
    "speedapp": "https://raw.githubusercontent.com/miIiano/SpeedApp.io-qBittorent-search-plugin/main/speedapp.py",
    "tapochek": "https://raw.githubusercontent.com/MjKey/qBT-SE/refs/heads/master/enigines/tapochek.py",
    "toloka_to": "https://raw.githubusercontent.com/playday3008/qBittorrent-plugins/refs/heads/main/plugins/search/toloka_to.py",
    "yggtorrent": "https://raw.githubusercontent.com/CravateRouge/qBittorrentSearchPlugins/master/yggtorrent.py"
  }
}

def list_plugins(official, unofficial, private):
    for header in plugins:
        print(header) 
        if not len(plugins[header]):
            print("  NONE")
        else:
            for plugin in plugins[header]:
                print(f"  {plugin}")
        print("")

def download_plugins(dir, official, unofficial, private):
    for category in plugins:
        for name, url in plugins[category].items():
            try:
                response = urllib.request.urlopen(url)
                content = response.read()
                filepath = dir / f"{name}.py"
                filepath.write_bytes(content)
            except Exception as e:
                print(f"  Error downloading {name}: {e}", file=sys.stderr)



def main():
    parser = argparse.ArgumentParser(
        description="Download qBittorrent search plugins"
    )
    parser.add_argument(
        "--official",
        action="store_true",
        help="Download/list official plugins",
    )
    parser.add_argument(
        "--unofficial",
        action="store_true",
        help="Download/list unofficial plugins",
    )
    parser.add_argument(
        "--private",
        action="store_true",
        help="Download/list private tracker unooficial plugins (requires login/account)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Download/list both official and unofficial plugins",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available plugins without downloading",
    )
    parser.add_argument(
        '--dir',
        help="Output dir for plugins",
        default=PLUGINS_DIR_DEFAULT
    )

    args = parser.parse_args()

    # Default to --all if no flags specified (or if only --list is specified)
    if not (args.official or args.unofficial or args.all):
        args.all = True

    # set all to true for all
    if args.all:
        args.official = True
        args.unofficial = True

    if (args.list):
        list_plugins(args.official, args.unofficial, args.private)
    else:
        dirPlugins = Path(args.dir)
        dirPlugins.mkdir(parents=True, exist_ok=True)
        download_plugins(dirPlugins, args.official, args.unofficial, args.private)


if __name__ == "__main__":
    sys.exit(main())
