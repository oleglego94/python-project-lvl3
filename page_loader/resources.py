import os
from bs4 import BeautifulSoup
from urllib import parse
from page_loader import io
from page_loader.saving import save
from page_loader.naming import make_name

RESOURCES = {
    "img": "src",
    "link": "href",
    "script": "src",
}


def get_local_resources(html_path, directory, url):
    domain = get_domain(url)
    soup = make_soup(html_path)
    for resource in RESOURCES.keys():
        attr = RESOURCES[resource]
        for tag in soup.find_all(resource):
            link = tag.get(attr)
            normal_link = normalize_link(link, domain)
            if not is_local(normal_link, domain):
                continue
            else:
                path, rel_path = make_file_path(normal_link, directory)
                save(normal_link, path)
                tag[attr] = rel_path

    new_html = soup.prettify(formatter="html5")
    io.write_file(new_html, html_path, "w")
    return


def get_domain(url):
    parsed_url = parse.urlparse(url)
    scheme = parsed_url.scheme
    host = parsed_url.netloc
    return "{}://{}".format(scheme, host)


def make_soup(doc_path):
    with open(doc_path) as fp:
        soup = BeautifulSoup(fp, "html.parser")
    return soup


def normalize_link(url, domain):
    parsed_url = parse.urlparse(url)
    if not parsed_url.scheme and not parsed_url.netloc:
        return parse.urljoin(domain, url)
    return url


def is_local(url, ref_domain):
    url_domain = get_domain(url)
    if url_domain == ref_domain:
        return True
    return False


def make_file_path(link, directory):
    path, ext = os.path.splitext(link)
    if not ext:
        ext = ".html"
    file_name = make_name(path, ext)
    path = os.path.join(directory, file_name)
    _, tail = os.path.split(directory)
    rel_path = os.path.join(tail, file_name)
    return path, rel_path
