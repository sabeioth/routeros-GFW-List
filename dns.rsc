:global dnsserver "192.18.0.1"
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="ac.jiruan.net"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="research.jmsc.hku.hk"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="news.hk.msn.com"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="friendfeed-media.com"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="googlescholar.comUSA"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="phobos.apple.com"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="notify.dropboxapi.com"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="michaelanti.com"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="jav2be.com"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="washeng.net"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="cn.dayabook.com"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="thehots.info"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="thehousenews.com"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="newspeak.cc"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="memorybbs.com"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="meyul.com"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="weiboscope.jmsc.hku.hk"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="razyboard.com"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="wiki.moegirl.org"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="video.pbs.org"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="puuko.com"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="21pron.com"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="api.dropboxapi.com"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="goldjizz.com"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="wiki.esu.im"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="raremovie.net"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="jinroukong.com"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="esu.dog"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="sjum.cn"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="meyou.jp"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="news.now.com"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="jobso.tv"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="tweets.seraph.me"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="21join.com"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="x1949x.com"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="x365x.com"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="xda-developers.com"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="news.tvb.com"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="winwhispers.info"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="dbc.hk"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="bbs.hasi.wang"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="ja.wikipedia.org"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="raremovie.cc"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="thetinhat.com"]
/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="gongwt.com"]
/ip dns static
:local domainList {
    "airitilibrary.com";
    "vpnproxymaster.com";
    "wikibooks.org";
    "uscg.mil";
    "spreaker.com";
    "audacy.com";
    "hypothes.is";
    "500px.com";
    "pixivsketch.net";
    "kindle4rss.com";
    "deadhouse.org";
    "japanhdv.com";
    "ey.gov.tw";
    "nos.nl";
    "www.msn.com";
    "caoporn.us";
    "xfxssr.me";
    "vpl.bibliocommons.com";
    "toptoon.net";
    "91porny.com";
    "bestvpnforchina.net";
    "dropboxapi.com";
    "ask.com";
    "unwire.hk";
    "freezhihu.org";
    "thehindu.com";
    "main-ecnpaper-economist.content.pugpig.com";
    "patreonusercontent.com";
    "vrporn.com";
    "vpn.net";
    "blacked.com";
    "stitcher.com";
    "moneydj.com";
    "mlc.ai";
    "xn--noss43i.com";
    "hsex.men";
    "doourbest.org";
    "eastasiaforum.org";
    "6do.world";
    "500px.org";
    "kzaobao.com";
    "coinbase.com";
    "rocket.chat";
    "lih.kg";
    "chaos.social";
    "cdpuk.co.uk";
    "reabble.com";
    "thewirechina.com";
    "androidapksfree.com";
    "tiktokcdn-us.com";
    "qianglie.com";
    "waybig.com";
    "ua5v.com";
    "chinademocrats.org";
    "pkqjiasu.com";
    "fountmedia.io";
    "miraheze.org";
    "memes.tw";
    "sleazyfork.org";
    "githubcopilot.com";
    "blog.reimu.net";
    "yunomi.tokyo";
    "smn.news";
    "newsblur.com";
    "appadvice.com";
    "usercontent.goog";
    "jmsc.hku.hk";
    "inherit.live";
    "chanworld.org";
    "fish.audio";
    "judicial.gov.tw";
    "x3guide.com";
    "wikidata.org";
    "pigav.com";
    "wikiversity.org";
    "thirdmill.org";
    "legra.ph";
    "fireofliberty.info";
    "ppy.sh";
    "jinrizhiyi.news";
    "weebly.com";
    "caus.com";
    "megalodon.jp";
    "wmfusercontent.org";
    "spatial.io";
    "bmdru.com";
    "open.firstory.me";
    "zmedia.com.tw";
    "mangmang.run";
    "dma.mil";
    "ultravpn.com";
    "carousell.com.hk";
    "popai.pro";
    "googlescholar.com";
    "mikanani.me";
    "ly.gov.tw";
    "momoshop.com.tw";
    "dashlane.com";
    "good.news";
    "aiosearch.com";
    "cnbeta.com.tw";
    "exam.gov.tw";
    "ultrasurf.us";
    "diyin.org";
    "z-lib.io";
    "bookwalker.com.tw";
    "bbs.nyinfor.com";
    "inews-api.tvb.com";
    "character.ai";
    "goodnewsnetwork.org";
    "tingtalk.me";
    "abebooks.co.uk";
    "flowhongkong.net";
    "ishr.ch";
    "play-asia.com";
    "uujiasu.com";
    "speedcat.me";
    "s3-ap-southeast-1.amazonaws.com";
    "sosad.fun";
    "1point3acres.com";
    "sehuatang.net";
    "glarity.app";
    "copilot.microsoft.com";
    "moeshare.cc";
    "tiktokv.us";
    "frank2019.me";
    "b.hatena.ne.jp";
    "yasukuni.or.jp";
    "fullservicegame.com";
    "lilaoshibushinilaoshi.com";
    "pornstarbyface.com";
    "javfinder.ai";
    "wiktionary.org";
    "btguard.com";
    "kuaichedao.co";
    "southmongolia.org";
    "simpleswap.io";
    "tfc-taiwan.org.tw";
    "wikivoyage.org";
    "radio-en-ligne.fr";
}
:foreach domain in=$domainList do={
    /ip dns static add forward-to=$dnsserver type=FWD address-list=gfw_list match-subdomain=no regexp=$domain
}
/ip dns cache flush
