def protection(url):
    import requests
    protections_dict = {
    "Cloudflare": {
        "indicators": [
            "cloudflare.com",
            "__cf_bm",
            "__cfduid",
            "cf-ray",
            "cf-chl",
            "cf_clearance",
            "Rocket Loader",
            "/cdn-cgi/",
            "cloudflare-ray-id",
            "Server: cloudflare"
        ]
    },
    "reCAPTCHA v2": {
        "indicators": [
            "www.google.com/recaptcha/api.js",
            "g-recaptcha",
            "recaptcha-token",
            "data-sitekey",
            "recaptcha-checkbox"
        ]
    },
    "reCAPTCHA v3": {
        "indicators": [
            "grecaptcha.execute",
            "recaptcha/api.js?render=",
            "data-sitekey",
            "grecaptcha.ready"
        ]
    },
    "hCaptcha": {
        "indicators": [
            "hcaptcha.com/1/api.js",
            "data-sitekey",
            "h-captcha",
            "hcaptcha-checkbox"
        ]
    },
    "Datadome": {
        "indicators": [
            "datadome.co",
            "__ddjs",
            "datadome-js",
            "/js/datadome",
            "captcha.datadome.co",
            "x-datadome-clientid"
        ]
    },
    "Akamai Bot Manager": {
        "indicators": [
            "akamai.net",
            "abck",
            "bm_sv",
            "ak_bmsc",
            "akamai-error",
            "akamai-bot"
        ]
    },
    "PerimeterX": {
        "indicators": [
            "px-captcha",
            "perimeterx.net",
            "_px",
            "client.px-cdn.net",
            "px_vid",
            "px3"
        ]
    },
    "Imperva Incapsula": {
        "indicators": [
            "incapsula",
            "visid_incap",
            "incap_ses",
            "X-Iinfo",
            "X-CDN",
            "incapsula incident id"
        ]
    },
    "AWS WAF / Shield": {
        "indicators": [
            "AWSShield",
            "AWSWAF",
            "wafv2",
            "x-amzn-waf",
            "x-amz-cf-id"
        ]
    },
    "Sucuri": {
        "indicators": [
            "sucuri.net",
            "Access Denied - Sucuri Website Firewall",
            "sucuri_cloudproxy_js",
            "x-sucuri-id"
        ]
    },
    "F5 BIG-IP": {
        "indicators": [
            "BIGipServer",
            "F5 Networks",
            "TS01",
            "f5-waf",
            "f5_bigip"
        ]
    },
    "Radware Bot Manager": {
        "indicators": [
            "radware.com",
            "radware-bot-manager",
            "rdwr"
        ]
    },
    "ArvanCloud": {
        "indicators": [
            "arvancloud.com",
            "Server: ArvanCloud",
            "ar-bot-protection"
        ]
    },
    "StackPath": {
        "indicators": [
            "stackpathdns.net",
            "stackpathcdn",
            "Server: StackPath"
        ]
    },
    "Fortinet WAF": {
        "indicators": [
            "fortinet",
            "fortiwaf",
            "fortiguard",
            "fortigate"
        ]
    },
    "Barracuda WAF": {
        "indicators": [
            "barracuda",
            "barra-counter",
            "barra-captcha"
        ]
    },
    "Wordfence": {
        "indicators": [
            "wordfence",
            "wf-captcha",
            "wordfence_verify",
            "wordfence_firewall"
        ]
    },
    "SiteGround WAF": {
        "indicators": [
            "siteground",
            "sg-security",
            "x-sg-protection"
        ]
    },
    "360 Web Application Firewall": {
        "indicators": [
            "360.cn",
            "waf.360",
            "360wzws"
        ]
    },
    "ModSecurity (Generic)": {
        "indicators": [
            "mod_security",
            "modsecurity",
            "X-Mod-Security",
            "Access denied by security policy"
        ]
    },
    "NAXSI": {
        "indicators": [
            "naxsi",
            "learning mode",
            "naxsi_block"
        ]
    }
}
    def protection(hldata):
        detected = []
        for name, data in protections_dict.items():
            for indicator in data["indicators"]:
                if indicator.lower() in hldata.lower():
                    detected.append(name)
                    break 
        return detected
     
    response = requests.get(url)
    if response.status_code != 200:
        print(response.text)
        return 'Bad req'
    else:
        protectsh = protection(response.text)
        protectsc = protection(str(response.headers))
        protects = protectsc + protectsh
        return protects


def database(url):
    import requests    
    db_dict = {
        "Microsoft SQL Server": {
            "indicators": [
                "Microsoft SQL Server",
                "System.Data.SqlClient",
                "Unclosed quotation mark after the character string",
                "SqlException",
                ".aspx",
                "ASP.NET_SessionId"
            ]
        },
        "MySQL / MariaDB": {
            "indicators": [
                "MySQLSyntaxErrorException",
                "mysql_fetch",
                "mysqli_query",
                "MariaDB server",
                "You have an error in your SQL syntax",
                ".php"
            ]
        },
        "PostgreSQL": {
            "indicators": [
                "PostgreSQL",
                "pg_query",
                "org.postgresql.util.PSQLException",
                "ERROR: syntax error at or near"
            ]
        },
        "Oracle": {
            "indicators": [
                "ORA-00933",
                "ORA-00936",
                "ORA-01756",
                "Oracle error"
            ]
        },
        "MongoDB": {
            "indicators": [
                "MongoDB",
                "MongoException",
                "errmsg",
                "E11000 duplicate key error collection"
            ]
        },
        "SQLite": {
            "indicators": [
                "SQLite3::SQLException",
                "SQLite error",
                "SQLITE_ERROR"
            ]
        }
    }

    def detect(hldata):
        detected = []
        for name, data in db_dict.items():
            for indicator in data["indicators"]:
                if indicator.lower() in hldata.lower():
                    detected.append(name)
                    break
        return detected
    
    try:
        response = requests.get(url, timeout=10)
    except Exception as e:
        return f"Request failed: {e}"
    
    if response.status_code != 200:
        return f"Bad req: {response.status_code}"
    else:
        found = detect(response.text) + detect(str(response.headers))
        return found if found else ["Unknown / No DB indicators found"]
        
def urls(url):
    import requests
    import re
    from urllib.parse import urljoin
    def grab(url):
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return []
    
        links = re.findall(r'https?://[^\s"\'>]+', response.text)
        links = list(set(links))
        
        return links
    
    def getrobots(url):
        try:
            urlmain = f"https://{url.split('/')[2]}"
        except:
            if len(url.split('/')) < 3:
                urlmain = f"https://{url.split('/')[-1]}"
                if '?' in urlmain:
                    urlmain = urlmain.split('?')[0]
    
        urlsset = set()
        try:
            response = requests.get(urlmain + "/robots.txt", timeout=10)
            lines = response.text.splitlines()
            for line in lines:
                line = line.strip()
                if line.lower().startswith(("disallow:", "allow:")):
                    path = line.split(":", 1)[1].strip()
                    if path:
                        fullurl = urljoin(urlmain, path)
                        urlsset.add(fullurl)
                elif line.lower().startswith("sitemap:"):
                    sitemapurl = line.split(":", 1)[1].strip()
                    urlsset.add(sitemapurl)
        except:
            pass
    
        return list(urlsset)
    
    htmlurls = grab(url)
    robotsurls = getrobots(url)
    
    return list(htmlurls + robotsurls)
