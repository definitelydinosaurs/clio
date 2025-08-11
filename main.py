import http.client
import sys
from urllib.parse import urlparse

def main(proposed_path=None):
    if not proposed_path:
        print("No URL provided.")
        return False
    parsed = urlparse(proposed_path if proposed_path else "")
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

if __name__ == "__main__":
    main()
