from baddns.lib import baddns as BadDNS

from .base import BaseModule


class baddns(BaseModule):
    watched_events = ["DNS_NAME", "DNS_NAME_UNRESOLVED"]
    produced_events = ["FINDING", "VULNERABILITY"]
    flags = ["active", "safe", "web-basic"]
    meta = {"description": "Check subdomains for for subdomain takeovers and other DNS tomfoolery"}
    max_event_handlers = 2
    deps_pip = ["baddns"]

    async def handle_event(self, event):
        baddns_cname = BadDNS.BadDNS_cname(event.data)
        if await baddns_cname.dispatch():
            r = baddns_cname.analyze()
            self.critical(r)
            if r:
                data = {
                    "severity": "MEDIUM",
                    "description": f"Probable Subdomain Takeover. CNAME: [{r['cname']}] Signature Name: [{r['signature_name']}] Matching Domain: [{r['matching_domain']}] Technique: [{r['technique']}]",
                    "host": str(event.host),
                }
                self.emit_event(data, "VULNERABILITY", event)
