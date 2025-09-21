[![penterepTools](https://www.penterep.com/external/penterepToolsLogo.png)](https://www.penterep.com/)


## PTMULTIVIEWS - Apache Multiviews Detection & Enumeration Tool

## Installation
```
pip install ptmultiviews
```

## Adding to PATH
If you're unable to invoke the script from your terminal, it's likely because it's not included in your PATH. You can resolve this issue by executing the following commands, depending on the shell you're using:

For Bash Users
```bash
echo "export PATH=\"`python3 -m site --user-base`/bin:\$PATH\"" >> ~/.bashrc
source ~/.bashrc
```

For ZSH Users
```bash
echo "export PATH=\"`python3 -m site --user-base`/bin:\$PATH\"" >> ~/.zshrc
source ~/.zshrc
```

## Usage examples

```
ptmultiviews -u https://www.example.com/                          # Test single URL for MultiViews vulnerability and retrieve alternatives
ptmultiviews -u https://www.example.com/ -co                      # Test single URL for MultiViews vulnerability without enumeration
ptmultiviews -u https://www.example.com/index.php -o output.txt   # Saves enumerated files to output.txt
ptmultiviews -f urlList.txt                                       # Enumerate all files from urlList
```


### Options:

```
-u   --url                 <url>           Connect to URL
-f   --file                <file>          Load list of URLs / filepaths
-df  --domain-file         <domain-file>   Load list of domains to mass scan (defaults to favicon.ico)
-co  --check-only                          Check for multiviews without enumerating
-wr  --with-requested-url                  Include requested source among enumerated results
-wd  --without-domain                      Enumerated files will be printed without domain
-t   --threads             <threads>       Set number of threads (default 20)
-p   --proxy               <proxy>         Set proxy (e.g. http://127.0.0.1:8080)
-T   --timeout             <timeout>       Set timeout (default 10)
-a   --user-agent          <agent>         Set User-Agent
-c   --cookie              <cookie>        Set Cookie(s)
-H   --headers             <header:value>  Set Header(s)
-o   --output              <output>        Save output to file
-r   --redirects                           Follow redirects (default False)
-C   --cache                               Cache HTTP communication (load from tmp in future)
-v   --version                             Show script version and exit
-h   --help                                Show this help message and exit
-j   --json                                Output in JSON format
```

## Dependencies

```
ptlibs
```


## License

Copyright (c) 2024 Penterep Security s.r.o.

ptmultiviews is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

ptmultiviews is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with ptmultiviews. If not, see https://www.gnu.org/licenses/.

## Warning

You are only allowed to run the tool against the websites which
you have been given permission to pentest. We do not accept any
responsibility for any damage/harm that this application causes to your
computer, or your network. Penterep is not responsible for any illegal
or malicious use of this code. Be Ethical!
