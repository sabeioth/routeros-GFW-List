:global dnsserver "192.18.0.1"
/ip dns static
:local domainList {
    "192.18.0.1";
}
:foreach domain in=$domainList do={
    /ip dns static add forward-to=$dnsserver type=FWD address-list=gfw_list match-subdomain=no regexp=$domain
}
/ip dns cache flush
