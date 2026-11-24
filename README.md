# 24 November 2026 — The World in One Day

[![entry](https://img.shields.io/badge/make.fun-news--image--20261124-blue)](https://make.fun/c/news-image-20261124)
[![license](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![python](https://img.shields.io/badge/python-3.13%20stdlib%20only-yellow)](main.py)

A make.fun bounty entry for **news-image-20261124**: *"Sum up 24 November's
world news in one image"*. The program draws a one-page newspaper front page
— masthead dated **24 November 2026**, six illustrated stories, and an
"also in the news" strip — and writes it to `entry.png`.

## The day's stories (all reported 24 Nov 2026)

| Story | What happened |
|---|---|
| Gaza | Israeli airstrike kills at least 3 near Khan Younis; five wounded (Reuters) |
| South Korea | Russian aircraft enters airspace; evacuation warning for Ulleung island (Reuters) |
| Iran / shipping | US probes Iran link in cyberattacks on up to 50 tankers (WSJ via Reuters) |
| India–Nepal | Modi and Shah flag off the Saryu–Kamala Express; eight pacts signed |
| Chess | World Chess Championship opens in Geneva: Gukesh defends vs Sindarov |
| Vanuatu | Magnitude 6.5 earthquake; no tsunami threat |

Also in the news: Nvidia shares soar after Huang's return, COP31 blame game
after the collapse, Indonesia confirms 24 dead in the factory fire, US states
sue SpaceX over Grok AI images.

## How it works

`main.py` is **pure Python 3.13 standard library** (`math`, `os`, `struct`,
`zlib`) — no third-party packages, no network. It draws every pixel itself
with a tiny built-in 5×7 bitmap font and its own PNG encoder, so both grader
runs write byte-identical output.

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png (1024x1024, ~22 KB)
```

## License

MIT — see [LICENSE](LICENSE).
