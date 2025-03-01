:global dnsserver "192.18.0.1"
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="usinfo.state.gov"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="student.tw"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="www.americorps.gov"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="nps.gov"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="gobet.cc"]
/ip dns static
:local domainList {
    "americorps.gov";
    "cofacts.tw";
    "news1.kr";
    "bsky.network";
    "ccfd.org.tw";
    "greasyfork.org";
    "pacom.mil";
    "picuki.com";
    "nodeseek.com";
    "ipdefenseforum.com";
    "611study.icu";
    "grok.com";
}
:foreach domain in=$domainList do={
    /ip dns static add forward-to=$dnsserver type=FWD address-list=gfw_list match-subdomain=no regexp=$domain
}
/ip dns cache flush
