pycfurlscannercli
=========

Description
-----------
A simple Python script to interact with Cloudflare Radar URL scanner APIs from CLI.


Usage
-----
```
$ pip install pycfurlscannercli

$ pycfurlscannercli -h
usage: pycfurlscannercli [-h] [-k API_KEY] [-c ACCOUNT_ID] [-a {scan}] [-i INPUT_FILE] [-p {http,http_and_https,https}]

version: 1.0

optional arguments:
  -h, --help            show this help message and exit

Mandatory parameters:
  -k API_KEY, --api-key API_KEY
                        Cloudflare API key (could either be provided in the "SECRET_CF_API_KEY" env var)
  -c ACCOUNT_ID, --account-id ACCOUNT_ID
                        Cloudflare Account ID key (could either be provided in the "SECRET_CF_ACCOUNT_ID" env var)
  -a {scan}, --action {scan}
                        Action to perform (default 'scan')

'scan' action parameters:
  -i INPUT_FILE, --input-file INPUT_FILE
                        Input file as a list of newline-separated FQDN or URL
  -p {http,http_and_https,https}, --protocol {http,http_and_https,https}
                        Protocol to use for each entry when not specified (default 'http_and_https')
```
  

Changelog
---------
* version 1.0 - 2025-09-21: First commit


Copyright and license
---------------------

All trademarks, service marks, trade names and product names appearing on this repository are the property of their respective owners

pycfurlscannercli is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

pycfurlscannercli is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  

See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU General Public License along with pycfurlscannercli. 
If not, see http://www.gnu.org/licenses/.

Contact
-------
* Thomas Debize < tdebize at mail d0t com >