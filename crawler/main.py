import urllib2
import re
import sys
import threading
import httplib
import pickle


class LinkFetcher:

    def getContent(self, page):
        content = page.read()
        return content

    def getLinks(self, content):
        links = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
        return links

    def getHeaders(self, page):
        headers = page.info()
        return headers

    def getCode(self, page):
        return page.getcode()


class Config:
    sites_processed = []
    sites_queue = ["http://www.microsoft.com"]
    max_workers = 100
    current_workers = 0
    db_file = "../data/dbFile.txt"
    sites_file = "../data/sites.txt"
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}

lf = LinkFetcher()
config = Config()


def processSite(site, verbose):
    if verbose == 1:
        print "Fetching: "+site
    if verbose == 2:
        print ":]",
    req = urllib2.Request(site, headers=config.hdr)
    try:
        page = urllib2.urlopen(req, timeout=1)
        if verbose == 1:
            print lf.getCode(page)
        if verbose == 2:
            print str(lf.getCode(page))+"",
        if lf.getCode(page):
            content = lf.getContent(page)
            links = lf.getLinks(content)
            headers = lf.getHeaders(page)
            for link in links:
                link = strip_tags(link)
                if link in config.sites_queue:
                    if verbose == 1:
                        print "duplicate ignored - "+link
                    if verbose == 2:
                        print ":(",
                else:
                    if link in config.sites_processed:
                        if verbose == 1:
                            print "already processed ignored - "+link
                        if verbose == 2:
                            print ":|",
                    else:
                        config.sites_queue.append(link)

            if site not in config.sites_processed:
                config.sites_processed.append(site)
                addSite(site, content, headers, links)

            if verbose == 1:
                print "Found: "+str(len(links))+" links"
            if verbose == 2:
                print ":D "+str(len(links))+" links",

    except urllib2.HTTPError, e:
        if verbose == 2:
            print "httperr",
        else:
            print 'HTTPError = ' + str(e.code)
    except urllib2.URLError, e:
        if verbose == 2:
            print "urlerr",
        else:
            print 'URLError = ' + str(e.reason)
    except httplib.HTTPException, e:
        if verbose == 2:
            print "httpex",
        else:
            print 'HTTPException'
    except Exception:
        import traceback
        if verbose == 2:
            print "genex",
        else:
            print 'generic exception: ' + traceback.format_exc()
    

def strip_tags(input):
    return re.compile(r'<[^<]*?/?>').sub('', input)


def addSite(url, content, headers, links):

    d = {"url":url,"content":content,"headers":headers,"links":links}

    with open(config.db_file, 'a') as f:
        f.write(str(d)+"\n")

    with open(config.sites_file, 'a') as f:
        f.write(str(url)+"\n")


def runner(i):
    while True:
        #config.current_workers += 1
        #print "!"+str(config.current_workers)
        #print str(len(config.sites_queue))
        if len(config.sites_queue) > 0:
            nextSite = config.sites_queue.pop()
            if nextSite != "":
                if nextSite not in config.sites_processed:
                    processSite(str(nextSite), 2)
        #config.current_workers -= 1


def main():
    threads = []
    #while True:
        #runner(1)

    #if config.current_workers < config.max_workers:
        #total_workers_needed = config.max_workers-config.current_workers

    try:
        for i in range(100):
            t = threading.Thread(target=runner, args=(i,))
            threads.append(t)

        for i in range(len(threads)):
            threads[i].start()

        for i in range(len(threads)):
            threads[i].join()

    except RuntimeError:
        print "runtimeerror"
        sys.exit(0)

if __name__ == "__main__":main()
