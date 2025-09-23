# certbot-dns-abion

A **Certbot DNS plugin** to perform DNS-01 challenges using the **Abion DNS API**.  
This allows you to obtain and renew Let's Encrypt (or other ACME) certificates automatically with Abion-managed domains.

---

## Disclaimer

This project is **community-maintained** and **not affiliated with Abion AB**.
Abion is a trademark of its respective owner.

---

## Installation

From PyPI :

```bash
pip install certbot-dns-abion
```
---

## Usage

1. Create a credentials file, e.g. ```/etc/letsencrypt/abion.ini```:

```bash
dns_abion_api_key = <your_api_key>
dns_abion_api_url = https://api.abion.com/   # optional, defaults to this URL
dns_abion_dns_ttl = 60                       # optional
```

Make sure this file is readable only by root:
```bash
chmod 600 /etc/letsencrypt/abion.ini
```
2. Run certbot with the plugin :

```bash
certbot certonly \
  --non-interactive --agree-tos --email you@example.com \
  --authenticator dns-abion \
  --dns-abion-credentials /etc/letsencrypt/abion.ini \
  -d example.com -d *.example.com
```
---
### Licence

This project is licensed under the Apache 2.0 License
