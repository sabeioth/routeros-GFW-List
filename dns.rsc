:global dnsserver "192.168.0.98"
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="192.18.0.1"]
/ip dns static
:local domainList {
    "192.168.0.98";
}
:foreach domain in=$domainList do={
    /ip dns static add forward-to=$dnsserver type=FWD address-list=gfw_list match-subdomain=no regexp=$domain
}
/ip dns cache flush
