# Packetframe v4

Packetframe has a new control plane! The old API, dashboard, and node orchestrator have been completely rewritten to improve the stability and feature set. (See the [api](https://github.com/packetframe/api), [web](https://github.com/packetframe/web), and [infra](https://github.com/packetframe/infra) repos for the full source)

The new version, dubbed "v4" is ready for beta testing!

**v4 is in early beta. If you're looking for stability, stick with the current system for now.**

### Using `pfmigrate`

`pfmigrate` is a simple tool that copies a zone to v4.

#### Quickstart

```bash
git clone https://github.com/packetframe/pfmigrate
cd pfmigrate
pip3 install -r requirements.txt
python3 pfmigrate.py
```

The tool will ask for two logins: first, your current credentials, then your new creds for v4. Enter both, then use the arrow keys to select a zone for migration.

#### < 1 min asciicast

[![asciicast](https://asciinema.org/a/452135.svg)](https://asciinema.org/a/452135)

**Don't forget to update your nameservers to ns1v4.packetframe.com and ns2v4.packetframe.com!**

### About the new nameserver hostnames

We want to allow every user to choose when is the right time to migrate to v4. This presents a problem with cleanly migrating zones at different times between two completely different systems.

The v4 edge nodes currently use ns1v4.packetframe.com and ns2v4.packetframe.com as nameserver hostnames, while ns1.packetframe.com and ns2.packetframe.com continue with the current system as they always have.

The v4 nameserver hostnames will be removed at the end of the beta and ns1/ns2.packetframe.com will be pointed to v4; just keep in mind that you'll have to update your nameservers again after the beta is complete.
