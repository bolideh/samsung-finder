# 📡 Samsung Device Finder

> Scan your local network and automatically detect **Samsung devices** using ARP, ping sweep, and MAC OUI (vendor) lookup — no third-party libraries required.

![Python](https://img.shields.io/badge/Python-3.7%2B-blue?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)
![No dependencies](https://img.shields.io/badge/Dependencies-None-brightgreen)

---

## ✨ Features

- 🔍 **Ping sweep** — fast multi-threaded scan of your entire /24 subnet (254 hosts in ~5s)
- 🏷️ **MAC OUI lookup** — identifies Samsung devices from 100+ known Samsung MAC prefixes
- 🖥️ **Device type guessing** — detects Smart TVs, Galaxy phones, printers, appliances, watches
- 🌐 **Reverse DNS** — resolves hostnames for cleaner results
- 🎨 **Colored terminal output** — easy to read at a glance
- ⚡ **Zero dependencies** — uses only Python's standard library

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/samsung-finder.git
cd samsung-finder
```

### 2. Run the scanner

```bash
# Auto-detect your network and scan
python src/scanner.py

# Or specify a custom subnet
python src/scanner.py 192.168.0.0/24
```

> **Note:** On Linux/macOS you may need `sudo` for ARP access:
> ```bash
> sudo python src/scanner.py
> ```

---

## 📸 Example Output

```
 ███████╗ █████╗ ███╗   ███╗███████╗██╗   ██╗███╗   ██╗  ██████╗
 ...
          Samsung Device Finder — Local Network Scanner

  Network range : 192.168.1.0/24
  Your IP       : 192.168.1.10

  [14:32:01] Pinging 254 hosts...
  ✓ Found 8 alive host(s)

  ✅  Found 3 Samsung device(s):

  IP Address         MAC Address          Type                      Hostname
  ------------------ -------------------- ------------------------- --------------------
  192.168.1.42       a0:07:98:xx:xx:xx    📺  Smart TV              Samsung-SmartTV
  192.168.1.55       f4:7b:5e:xx:xx:xx    📱  Galaxy Phone/Tablet   android-1234
  192.168.1.61       d8:57:ef:xx:xx:xx    📡  Samsung Device        unknown

  Scan completed in 4.8s
```

---

## 🧠 How It Works

```
┌─────────────────────────────────────────────────────┐
│                  Your Machine                        │
│                                                      │
│  1. Detect local IP  →  e.g. 192.168.1.10           │
│  2. Derive subnet    →  192.168.1.0/24               │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│              Ping Sweep (threaded)                   │
│   Send ICMP ping to all 254 hosts simultaneously    │
│   Collect list of "alive" IPs                       │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│              ARP Cache Lookup                        │
│   Read system ARP table (arp -a)                    │
│   Map each alive IP → MAC address                   │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│           Samsung OUI Matching                       │
│   Compare MAC prefix (first 3 bytes)                │
│   Against 100+ Samsung-registered OUI prefixes      │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│          Device Classification                       │
│   Reverse DNS lookup for hostname                   │
│   Keyword match → TV / Phone / Printer / etc.       │
└─────────────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```
samsung-finder/
├── src/
│   └── scanner.py       # Main scanner script
├── requirements.txt     # No dependencies (stdlib only)
├── .gitignore
└── README.md
```

---

## ⚙️ Configuration

You can pass a custom subnet as a command-line argument:

```bash
python src/scanner.py 10.0.0.0/24
python src/scanner.py 172.16.0.0/24
```

The script auto-detects your subnet by default — no configuration needed.

---

## 🔬 What is MAC OUI?

Every network device has a **MAC address** (e.g. `a0:07:98:12:34:56`).

The **first 3 bytes** (`a0:07:98`) are called the **OUI (Organizationally Unique Identifier)** — they identify the device manufacturer. Samsung has registered over 100 OUI prefixes with the IEEE.

This tool checks every live device's MAC prefix against the known Samsung OUI list to identify Samsung devices — no cloud service or API needed.

---

## 🛡️ Permissions

| OS | Requirement |
|----|------------|
| Linux | `sudo` recommended for full ARP access |
| macOS | `sudo` recommended |
| Windows | Run as Administrator for best results |

---

## 🐛 Troubleshooting

**No devices found?**
- Make sure your Samsung device is **on the same Wi-Fi/LAN** as your computer
- Try running with `sudo` (Linux/macOS) or as Administrator (Windows)
- Some devices block ICMP pings — try waking them up first

**ARP table is empty?**
- The ping sweep must complete first to populate the ARP cache
- On Windows, try running `arp -a` manually to verify ARP is working

**Wrong subnet detected?**
- Pass the correct subnet manually: `python src/scanner.py 192.168.0.0/24`

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 🤝 Contributing

Pull requests are welcome! Ideas for improvement:
- [ ] mDNS/Bonjour device discovery
- [ ] SSDP/UPnP Samsung device detection
- [ ] Export results to JSON/CSV
- [ ] GUI with tkinter
- [ ] Continuous monitoring mode

---

*Built with ❤️ using Python's standard library only.*
