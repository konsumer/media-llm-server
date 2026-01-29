# Media Server Setup

Docker-based media server with VPN-protected torrents, Plex, AI tools, and more.

> [!WARNING]
> It is assumed this is running on your LAN, behind a firewall. Everything is lacking authentication (but you can add it) so you probably don't want to deploy this as-is, if your network is not secured.

It is intended to be a central media-server setup that supports my [AI media MCPs](https://github.com/konsumer/aitorrent):

---
🎉 I've successfully added all 3 episodes of **Star Trek: Starfleet Academy** to your download queue!

## **✅ Downloads Started:**

**Star Trek: Starfleet Academy - Season 1**
- **Episode 1** - "Kids These Days" (1.1 GB, 1468 seeders) - x265 HEVC
- **Episode 2** - "Beta Test" (4.1 GB, 4882 seeders) - h264
- **Episode 3** - "Vitus Reflux" (858 MB, 4288 seeders) - x265 HEVC

**Download Location:** `/media/video/tv/Star Trek Starfleet Academy/Season 1`

All torrents have excellent seeder counts, so they should download quickly! Once they're done, Plex should automatically detect them.

**Note:** Episode 4 airs **tomorrow (January 29, 2026)**, so you can download that once it's available. New episodes air every Wednesday through March 12.

Would you like me to set up an RSS auto-download rule so new episodes automatically download as they air?
---

## usage

Some things you should setup, first:

- Get a VPN. Most will work fine, look for "WireGuard" configuration, and use it to set the `WIREGAURD_` variables
- Install docker
- If you want GPU acceleration, and have an Nvidia card, install [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)

In the directions below:

- `/mnt/MEDIA/server/config` - defined as `$CONFIG` in `.env`. This is where dockers will store their settings.
- `/mnt/MEDIA` - defined as `$ROOT` in `.env`. This is where all your media-files go.

You can set the variables to whatever location you want.

To get started copy the example config, and adjust everything:

```sh
cp -R config-example config
cp .env.example .env
```

Actually look at `.env`, since they have some config to fill in.

## Nvidia

In order for some of the containers to work as they are (ollama/plex) you should install [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) and have an NVIDIA GPU. This part is optional, just remove this kind of stuff from docker-compose:

```yml
deploy:
  resources:
    reservations:
      devices:
        - count: 1
          driver: nvidia
          capabilities: [gpu]
```

## Services

- **[qBittorrent](https://www.qbittorrent.org/) + [VueTorrent](https://github.com/VueTorrent/VueTorrent)**: Modern torrent client with VPN protection
- **[Gluetun](https://github.com/qdm12/gluetun)**: VPN container (WireGuard) - automatically wraps any service you connect to it, so your IP is not exposed.
- **[Plex](https://plex.tv)**: Media server
- **[Ollama](https://ollama.com/) + [LLMs](https://llmspy.org/)**: Self-hosted AI
- **[Samba](https://www.samba.org/)**: Network file sharing
- **[Nginx](https://nginx.org/)**: Web server (for frontend)

## Running things

It's all using docker-compose, so it's easy to manage:

```sh
# run it all
docker compose up -d

# watch the logs
docker compose logs -f

# list what is running
docker compose ps

# restart everyting
docker compose restart

# restart 1 thing
docker compose restart qbittorrent

# run a shell in 1 thing, to look around
docker compose exec qbittorrent sh

# stop it
docker compose down
```

You wil see a lot of warnings like this:

```
WARN[0000] The "CEREBRAS_API_KEY" variable is not set. Defaulting to a blank string.
```

You can either ignore these, or remove them from `docker-compose.yml`. Adding all of them to `.env` is also an option, but you probably won't actually use them all.

## Accessing Services

### Direct Access (via ports)

- **qBittorrent (VueTorrent)**: http://localhost:8080
- **Plex**: http://localhost:32400/web
- **Ollama**: http://localhost:11434
- **LLMs Frontend**: http://localhost:8000

### Adding More qBittorrent Search Plugins

#### Automatic Installation (Recommended)

Use the included Python script to download all available plugins:

```bash
# Install dependencies first (if needed)
pip install -r requirements.txt

# Download ALL plugins (official + public unofficial)
python3 install-search-plugins.py

# Download including private trackers (requires account)
python3 install-search-plugins.py --private

# Download only official plugins
python3 install-search-plugins.py --official

# List available plugins without downloading
python3 install-search-plugins.py --list
```

Then restart qBittorrent:

```bash
docker compose restart qbittorrent
```

The new plugins will appear in VueTorrent's search dropdown.

#### Manual Installation

1. **Find plugins** at:
   - Official: https://github.com/qbittorrent/search-plugins/tree/master/nova3/engines
   - Unofficial: https://github.com/qbittorrent/search-plugins/wiki/Unofficial-search-plugins

2. **Download the .py file** to:

   ```bash
   config/qbittorrent/qBittorrent/nova3/engines/
   ```

3. **Example:**

   ```bash
   wget https://raw.githubusercontent.com/qbittorrent/search-plugins/master/nova3/engines/PLUGINNAME.py \
     -O config/qbittorrent/qBittorrent/nova3/engines/PLUGINNAME.py
   ```

4. **Restart qBittorrent:**
   ```bash
   docker compose restart qbittorrent
   ```

#### Popular Plugins

- **eztv.py** - TV shows
- **solidtorrents.py** - Meta-search across multiple sites
- **jackett.py** - Integrates with Jackett (requires configuration, and you might want to run jackett in your docker-compose)
- **torrentscsv.py** - CSV-based torrent search

## VPN Configuration

All torrent traffic routes through Gluetun VPN.

### VPN Settings

Located in `.env` file:

```
VPN_ENDPOINT_IP=<YOURS>
VPN_ENDPOINT_PORT=<YOURS>
WIREGUARD_PUBLIC_KEY=<YOURS>
WIREGUARD_PRIVATE_KEY=<YOURS>
```

### Verify VPN is Working

```bash
docker compose exec qbittorrent curl ifconfig.me/all

# Should show the VPN IP, not your real IP:

ip_addr: <YOUR_IP>
remote_host: unavailable
user_agent: curl/8.18.0
port: 39852
language:
referer:
connection:
keep_alive:
method: GET
encoding:
mime: */*
charset:
via: 1.1 google
forwarded: <YOUR_IP>,<ANOTHER>
```

You can also try [a magent link from here](https://torguard.net/check-my-torrent-ip-address/), to verify your torrent client does not show your real IP. You can just add it to your torrent client (`+` button) at `http://localhost:8080`.

## Local Network Access

You might need to adjust the concept of "local" IP. On my network, that is `192.168.86.X`. The ` 172.X` addresses here are for docker.

qBittorrent WebUI is accessible without password from:

- 192.168.86.0/24
- 172.17.0.0/24
- 172.18.0.0/24

## Directory Structure

```
/mnt/MEDIA/server/
├── config/
│   ├── qbittorrent/     # qBittorrent + VueTorrent config
│   ├── gluetun/         # VPN config
│   ├── plex/            # Plex database
│   └── ...
└── docker-compose.yml
```

## Setup

There is a bit of setup to do after this. Go to each link on [your local page](http://localhost) to configure each thing. Specifically, you will want to login/claim/configure plex, and probably also want to setup some basic stuff on your torrent client.

## Troubleshooting

### "Firewalled" Status in qBittorrent

This is **normal** when using a VPN. You can still download and upload torrents, but won't accept incoming connections. This may be slightly slower on some torrents but works fine.

### Adding Search Plugins Not Working

1. Make sure the .py file is in the correct directory
2. Check file permissions: `chmod 644 /path/to/plugin.py`
3. Restart qBittorrent: `docker-compose restart qbittorrent`
4. Check logs: `docker logs qbittorrent`

### VPN Not Connecting

1. Check Gluetun logs: `docker compose logs gluetun`
2. Verify WireGuard config (`WIREGAURD_` variables) in .env file
