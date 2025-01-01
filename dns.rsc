:global dnsserver "192.18.0.1"
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="hacg.in"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="hacg.me"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="hacg.li"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="hacg.club"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="bt2mag.com"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="hacg.red"]
/ip dns static
:local domainList {
    "slides.new";
    "vrchat.com";
    "docs.new";
    "whats.new";
    "herokuapp.com";
    "pcgamestorrents.com";
    "haijiao.com";
    "sheets.new";
    "deepai.org";
    "hpjav.com";
    "ground.news";
    "snapseed.com";
    "iavian.net";
    "bsky.social";
    "bsky.app";
}
:foreach domain in=$domainList do={
    /ip dns static add forward-to=$dnsserver type=FWD address-list=gfw_list match-subdomain=no regexp=$domain
}
/ip dns cache flush
