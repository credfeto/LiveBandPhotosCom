import os
import pathlib
from urllib.request import Request, urlopen

root = pathlib.Path(__file__).parent.resolve()

if __name__ == "__main__":
  url = 'http://admin.livebandphotos.co.uk/transfergigsonly.php'

  request = Request(url)
  request.add_header('Accepts', 'application/json')
  request.add_header('Accept-Encoding', 'deflate, gzip')

  print("Requesting...")
  response = urlopen(request, timeout=240)  

  print("Downloading Content...")
  content = response.read()

  gigs = root / "gigs.xml"
  gigs.open("w").write(content.decode("utf-8"))
