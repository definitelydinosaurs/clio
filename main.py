import http.client
import sys
from urllib.parse import urlparse

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

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if is_url_reachable(sys.argv[1]):
            print(f"URL {sys.argv[1]} is reachable.")
        else:
            print(f"URL {sys.argv[1]} is not reachable.")
    else:
        print("Please provide a URL as an argument.")
