## 1.30.8 - 2025-09-23
### Extractors
#### Additions
- [chevereto] support `imglike.com` ([#5179](https://github.com/mikf/gallery-dl/issues/5179))
- [chevereto] add `category` extractor ([#5179](https://github.com/mikf/gallery-dl/issues/5179))
- [Danbooru] add `random` extractor ([#8270](https://github.com/mikf/gallery-dl/issues/8270))
- [hdoujin] add support ([#6810](https://github.com/mikf/gallery-dl/issues/6810))
- [imgpile] add support ([#5044](https://github.com/mikf/gallery-dl/issues/5044))
- [mangadex] add `covers` extractor ([#4994](https://github.com/mikf/gallery-dl/issues/4994))
- [mangataro] add support ([#8237](https://github.com/mikf/gallery-dl/issues/8237))
- [thehentaiworld] add support ([#274](https://github.com/mikf/gallery-dl/issues/274) [#8237](https://github.com/mikf/gallery-dl/issues/8237))
#### Fixes
- [4archive] fix `TypeError` ([#8217](https://github.com/mikf/gallery-dl/issues/8217))
- [bellazon] fix video attachments ([#8239](https://github.com/mikf/gallery-dl/issues/8239))
- [bunkr] fix `JSONDecodeError` for files with URL slugs containing apostrophes `'` ([#8150](https://github.com/mikf/gallery-dl/issues/8150))
- [instagram] ensure manifest data exists before attempting a DASH download ([#8267](https://github.com/mikf/gallery-dl/issues/8267))
- [schalenetwork] fix extraction ([#6948](https://github.com/mikf/gallery-dl/issues/6948) [#7391](https://github.com/mikf/gallery-dl/issues/7391) [#7728](https://github.com/mikf/gallery-dl/issues/7728))
- [twitter] fix quoted Tweets being marked as `deleted` ([#8225](https://github.com/mikf/gallery-dl/issues/8225))
#### Improvements
- [2ch] update domain to `2ch.su`, support `2ch.life` URLs ([#8216](https://github.com/mikf/gallery-dl/issues/8216))
- [bellazon][simpcity][vipergirls] process threads in descending order ([#8248](https://github.com/mikf/gallery-dl/issues/8248))
- [bellazon] extract `inline` images (##8247)
- [bellazon] support video embeds ([#8239](https://github.com/mikf/gallery-dl/issues/8239))
- [bellazon] support `#comment-12345` post links ([#8239](https://github.com/mikf/gallery-dl/issues/8239))
- [lensdump] support new direct file URL pattern ([#8251](https://github.com/mikf/gallery-dl/issues/8251))
- [simpcity] extract URLs of `<iframe>` embeds ([#8214](https://github.com/mikf/gallery-dl/issues/8214) [#8256](https://github.com/mikf/gallery-dl/issues/8256))
- [simpcity] improve post content extraction ([#8214](https://github.com/mikf/gallery-dl/issues/8214))
#### Metadata
- [facebook] extract `biography` metadata ([#8233](https://github.com/mikf/gallery-dl/issues/8233))
- [instagram:tagged] provide full `tagged_…` metadata when using `id:…` URLs ([#8263](https://github.com/mikf/gallery-dl/issues/8263))
- [iwara] extract more metadata ([#6582](https://github.com/mikf/gallery-dl/issues/6582))
- [iwara] make `type` available for directories ([#8245](https://github.com/mikf/gallery-dl/issues/8245))
- [reddit] provide `comment` metadata for all media files ([#8228](https://github.com/mikf/gallery-dl/issues/8228))
#### Options
- [bellazon] add `quoted` option ([#8247](https://github.com/mikf/gallery-dl/issues/8247))
- [bellazon] implement `order-posts` option ([#8248](https://github.com/mikf/gallery-dl/issues/8248))
- [kemono:discord] implement `order-posts` option ([#8241](https://github.com/mikf/gallery-dl/issues/8241))
- [simpcity] implement `order-posts` option ([#8248](https://github.com/mikf/gallery-dl/issues/8248))
- [vipergirls] implement `order-posts` option ([#8248](https://github.com/mikf/gallery-dl/issues/8248))
### Downloaders
- [ytdl] fix errors caused by deprecated options removal
### Post Processors
- [metadata] add `"mode": "print"` ([#2691](https://github.com/mikf/gallery-dl/issues/2691))
- [python] add `"mode": "eval"`
- close archive database connections ([#8243](https://github.com/mikf/gallery-dl/issues/8243))
### Miscellaneous
- [util] define `__enter__` & `__exit__` methods for `NullResponse` objects ([#8227](https://github.com/mikf/gallery-dl/issues/8227))
- [util] extend list of ISO 639 language codes
