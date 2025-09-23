from typing import Any, Tuple, Optional, List
import re

from certbot.plugins import dns_common
from certbot.plugins.dns_common import CredentialsConfiguration
from certbot import errors

from ._internal.abion_client import AbionClient

def _to_fqdn(name: str) -> str:
    return name if name.endswith(".") else name + "."

def _strip_trailing_dot(name: str) -> str:
    return name[:-1] if name.endswith(".") else name

class Authenticator(dns_common.DNSAuthenticator):
    """DNS Authenticator for Abion"""

    description = "Obtain certificates using a DNS TXT record (if you are using Abion for DNS)."
    ttl = None

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._client = None  # type: Optional[AbionClient]
        self._zone_cache = {}  # fqdn -> (zone, relative_label)

    @classmethod
    def add_parser_arguments(cls, add: Any) -> None:
        super().add_parser_arguments(add)
        add('credentials', help='Path to INI file containing Abion API credentials')
        add('propagation-seconds', default=60, type=int,
            help='Estimated time for DNS to propagate changes (default: 60 seconds)')

    def more_info(self) -> str:
        return "This plugin create and remove TXT records using the official Abion API."

    def _setup_credentials(self) -> None:
        self.credentials = self._configure_credentials(
            "credentials",
            "INI File containing for example :\n"
            "dns_abion_api_key=...\n"
            "dns_abion_api_url=https://api.abion.com/\n"
            "dns_abion_dns_ttl=60",
            {
                "api_key": "API key Abion (dns_abion_api_key)",
                "api_url": "Base URL API (dns_abion_api_url, optional)",
                "dns_ttl": "TTL (dns_abion_dns_ttl, optional)",
            },
        )

        api_key = self.credentials.conf("api_key", default=None) or self.credentials.conf("dns_abion_api_key", default=None)
        if not api_key:
            raise errors.PluginError("dns_abion_api_key missing in the credentials INI file")

        api_url = self.credentials.conf("api_url", default=None) or self.credentials.conf("dns_abion_api_url", default="https://api.abion.com/")
        ttl = self.credentials.conf("dns_ttl", default=None) or self.credentials.conf("dns_abion_dns_ttl", default=None)
        self.ttl = int(ttl) if ttl else None

        self._client = AbionClient(api_key=api_key, base_url=api_url)

    def _perform(self, domain: str, validation_name: str, validation: str) -> None:
        zone, rel = self._find_zone_and_relative(validation_name)
        txt_rr = {"rdata": validation}
        if self.ttl:
            txt_rr["ttl"] = self.ttl

        payload = {
            "data": {
                "type": "zone",
                "id": zone,
                "attributes": {
                    "records": {
                        rel: {
                            "TXT": [txt_rr]
                        }
                    }
                }
            }
        }

        self._client.patch_zone_records(zone, payload)

    def _cleanup(self, domain: str, validation_name: str, validation: str) -> None:
        zone, rel = self._find_zone_and_relative(validation_name)

        payload = {
            "data": {
                "type": "zone",
                "id": zone,
                "attributes": {
                    "records": {
                        rel: {
                            "TXT": None
                        }
                    }
                }
            }
        }

        try:
            self._client.patch_zone_records(zone, payload)
        except Exception as e:
            # Do not fail on cleanup
            raise

    def _find_zone_and_relative(self, fqdn: str) -> Tuple[str, str]:
        fqdn = _strip_trailing_dot(fqdn)
        if fqdn in self._zone_cache:
            return self._zone_cache[fqdn]

        labels = fqdn.split(".")
        # Trying from the most specific to the least specific
        for i in range(len(labels)-1):
            candidate = ".".join(labels[i:])
            z = self._client.get_zone(candidate)
            if z is not None:
                zone = candidate
                relative = fqdn[:-len(zone)].rstrip(".")
                if relative == "":
                    relative = "@"
                self._zone_cache[fqdn] = (zone, relative)
                return zone, relative

        # Last resort, try the FQDN as zone (for single-label zones)
        z = self._client.get_zone(fqdn)
        if z is not None:
            self._zone_cache[fqdn] = (fqdn, "@")
            return fqdn, "@"
        raise errors.PluginError(f"Zone not found in Abion for : {fqdn}")
