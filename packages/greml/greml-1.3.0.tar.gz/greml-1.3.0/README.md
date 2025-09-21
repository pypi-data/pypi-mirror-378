# Greml

Make HTML greppable!

A simple tool to allow you to *gre*p HT*ML*. 

## Installation

The recommended way to install is to use `pipx`:

`pipx install greml`

## Usage

Specify a HTML document, either piped as stdin, or a file or HTTP request and a [selector (provided by Soup Sieve)](https://facelessuser.github.io/soupsieve/). 

The output may be the text of the elements, a JSON representation of the element (including all attributes) that may be parsed further using `jq` or the value of specific attributes. 

```
%   greml --help

 Usage: greml [OPTIONS] [INPUT_PATH] [SELECTOR]

╭─ Arguments ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│   input_path      [INPUT_PATH]  Input file path or URL. If not specified uses stdin. [default: (stdin)]                                                           │
│   selector        [SELECTOR]    HTML selector [default: None]                                                                                                     │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --display                                          TEXT                             How to display, either 'text', 'json' or 'attr.ATTR' [default: text]          │
│ --follow-redirects        --no-follow-redirects                                     [default: follow-redirects]                                                   │
│ --user-agent                                       TEXT                             Custom User-Agent header for HTTP requests [default: None]                    │
│ --user-agent-random                                                                 Use a random User-Agent header                                                │
│ --header                                           TEXT                             Custom HTTP header in 'Header-Name: value' format [default: None]            │
│ --ajax                -a                                                            Add X-Requested-With header to simulate Ajax requests                         │
│ --timeout                                          INTEGER                          Timeout in seconds for HTTP requests [default: 30]                            │
│ --version             -v                                                                                                                                          │
│ --install-completion                               [bash|zsh|fish|powershell|pwsh]  Install completion for the specified shell. [default: None]                   │
│ --show-completion                                  [bash|zsh|fish|powershell|pwsh]  Show completion for the specified shell, to copy it or customize the          │
│                                                                                     installation.                                                                 │
│                                                                                     [default: None]                                                               │
│ --help                                                                              Show this message and exit.                                                   │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## Exampless

```
% greml https://www.yourlifedoncaster.co.uk/trees-and-woodlands '#treeCounter'
108,000
```

```
% greml https://github.com/adamckay 'img[alt^="Achievement: "]' --display attr.alt | sort | uniq
Achievement: Arctic Code Vault Contributor
Achievement: Pull Shark
Achievement: Quickdraw
Achievement: YOLO
```

### Custom Headers

Add custom HTTP headers to your requests using the `--header` option. You can specify multiple headers by repeating the option:

```
% greml https://api.example.com/data 'div.content' --header "Authorization: Bearer your-token"
% greml https://api.example.com/data 'div.content' --header "X-API-Key: abc123" --header "Content-Type: application/json"
```

### Ajax Requests

Use the `--ajax` (or `-a`) option to simulate Ajax/XMLHttpRequest requests by automatically adding the `X-Requested-With: XMLHttpRequest` header:

```
% greml https://api.example.com/endpoint 'div.response' --ajax
% greml https://api.example.com/endpoint 'div.response' -a --header "Authorization: Bearer token"
```

This is useful when accessing APIs or web pages that behave differently for Ajax requests versus regular browser requests.