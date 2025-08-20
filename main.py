import http.client
import sys
from urllib.parse import urlparse
import html.parser

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

        # Handle 3xx redirects
        if 300 <= response.status < 400:
            location = response.getheader('Location')
            if location:
                return is_url_reachable(location)  # Recursively follow redirect

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

def get_base_page(url):
    """Get the HTML content of a page"""
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
            content = response.read().decode('utf-8', errors='ignore')
            return content
        else:
            print(f"Failed to get page content: HTTP {response.status}")
            return None

    except Exception as e:
        print(f"Error getting page content: {e}")
        return None
    finally:
        conn.close()

def get_page_assets(page_content):
    assets = set()
    parser = html.parser.HTMLParser()
    temp_assets = parser.feed(page_content)
    return assets

if __name__ == "__main__":
    if len(sys.argv) > 1:
        root_url = get_root_url(sys.argv[1])
        if is_url_reachable(root_url):
            base_page = get_base_page(root_url)
            print(base_page)
        else:
            print(f"URL {sys.argv[1]} is not reachable.")
    else:
        print("Please provide a URL as an argument.")
