<h1 align="center">
A simple GUI based ping tester, good when looking for spikes
</h1>



<div align="center">

![pl_logo](https://raw.githubusercontent.com/fivepandasna/Ping-Poller/main/assets/icons/icon-80.png)

[![Discord](https://img.shields.io/badge/Discord-FivePandas-9089DA?logo=discord&style=for-the-badge)](https://discord.com/users/628709323068932125)
[![Downloads](https://img.shields.io/github/downloads/fivepandasna/Ping-Poller/total?label=downloads&color=208a19&logo=github&style=for-the-badge)](https://github.com/fivepandasna/Ping-Poller/releases)
</div>

## What is this? How is it useful?

This is a pretty simple program that uses ICMP echo requests to measure latency with a targeted host. It records the round-trip time for each ping and aggregates a variety of statistics. 

This isn't a super accurate measurement of long term latency due to using ICMP and a few other things, however it's useful for detecting packet loss and ping especially spikes (use lower intervals like 0.1s for this). 

## Todo

- [x] Create a myproject.toml or requirements.txt
- [x] Create an installer
- [x] Add different graph display settings (like follow last 30s of data)
- [x] Add a settings page?
- [ ] Modularize code
- [ ] Improve performance and stop storing data in memory for long tests
- [ ] Improve error handling and reporting
- [ ] Add support for a light ui
- [ ] Reduce duplicate code and logic
- [ ] Use constants for colours ;-;
- [ ] Add option in settings to change graph update interval to reduce some load
- [ ] Add even more documentation
- [ ] Add data importing
 
