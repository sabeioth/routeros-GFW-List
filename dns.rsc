:global dnsserver
/ip dns static remove [/ip dns static find name="phobos.apple.com"]
/ip dns static
:local domainList {
    "phobos.apple.com*";
}
:foreach domain in=$domainList do={
    /ip dns static add forward-to=$dnsserver type=FWD address-list=gfw_list match-subdomain=no name=$domain
}
/ip dns cache flush
