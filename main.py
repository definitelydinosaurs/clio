import http.client
import sys
from urllib.parse import urlparse, urljoin
import html.parser
import re
import os

class AssetParser(html.parser.HTMLParser):
    def __init__(self, base_url):
        super().__init__()
        self.assets = set()
        self.base_url = base_url

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        if tag in ['img', 'video', 'audio', 'source'] and "src" in attr_dict:
            self.assets.add(attr_dict['src'] if url_is_absolute(attr_dict['src']) else urljoin(self.base_url, attr_dict['src']))

    def get_assets(self):
        return self.assets

def save_file(content, path, mode='w'):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, mode) as f:
            f.write(content)
    except Exception as e:
        print(f"Error saving {path}: {e}")

def sanitize_filename(url):
    parsed = urlparse(url)
    domain = parsed.netloc.replace('.', '_')
    path = parsed.path.strip('/')
    if not path:
        path = "index.html"
    path = re.sub(r'[<>:"|?*]', '_', path)
    if '.' not in os.path.basename(path):
        path += '.html'
    return os.path.join(domain, path)

def url_is_absolute(url):
    return bool(urlparse(url).netloc)

def is_url_reachable(proposed_path=None):
    if not proposed_path:
        print("No URL provided.")
        return False

    parsed = urlparse(proposed_path)
    conn_class = http.client.HTTPSConnection if parsed.scheme == "https" else http.client.HTTPConnection
    conn = conn_class(parsed.netloc)

    try:
        path = parsed.path or "/"
        if parsed.query:
            path += "?" + parsed.query
        conn.request("HEAD", path)
        response = conn.getresponse()
        return response.status != 404
    except Exception as e:
        print("Error:", e)
        return False
    finally:
        conn.close()

def get_root_url(proposed_path):
    if not proposed_path:
        print("No URL provided.")
        return None

    parsed = urlparse(proposed_path)
    conn_class = http.client.HTTPSConnection if parsed.scheme == "https" else http.client.HTTPConnection
    conn = conn_class(parsed.netloc)

    try:
        path = parsed.path or "/"
        if parsed.query:
            path += "?" + parsed.query
        conn.request("HEAD", path)
        response = conn.getresponse()

        # Handle 3xx redirects
        if 300 <= response.status < 400:
            location = response.getheader('Location')
            if location:
                return get_root_url(location)  # Recursively follow redirect

        return parsed._replace(path="/").geturl()
    except Exception as e:
        print("Error:", e)
        return None
    finally:
        conn.close()

def get_page(url, binary=False):
    try:
        parsed = urlparse(url)
        conn_class = http.client.HTTPSConnection if parsed.scheme == "https" else http.client.HTTPConnection
        conn = conn_class(parsed.netloc)

        path = parsed.path or "/"
        if parsed.query:
            path += "?" + parsed.query

        conn.request("GET", path)
        response = conn.getresponse()

        if response.status == 200:
            content = response.read()
            if binary:
                return content  # Return raw bytes for binary files
            else:
                return content.decode('utf-8', errors='ignore')  # Decode for text files
        else:
            print(f"Failed to get content: HTTP {response.status}")
            return None

    except Exception as e:
        print(f"Error getting content: {e}")
        return None
    finally:
        conn.close()

def get_page_assets(root_url, page_content):
    parser = AssetParser(root_url)
    parser.feed(page_content)
    return parser.get_assets()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        root_url = get_root_url(sys.argv[1])
        if is_url_reachable(root_url):
            base_page = get_page(root_url)
            save_file(base_page, sanitize_filename(root_url))
            # print(base_page)
            assets = get_page_assets(root_url, base_page)
            print("Assets found:")
            for asset in assets:
                print(" -", sanitize_filename(asset))
        else:
            print(f"URL {sys.argv[1]} is not reachable.")
    else:
        print("Please provide a URL as an argument.")
