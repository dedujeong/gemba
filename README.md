# Gemba

Claude plugins that take software from an idea or a client request to a released version, with every decision traced back to where it was made.

_Gemba_ (現場) is Japanese for "the actual place": where the work really happens. It comes with a principle from the Toyota Production System, _genchi genbutsu_ (現地現物), "go and see for yourself": understand a problem at the place where it happens instead of deciding from reports. These plugins work the same way. They ask about what has actually happened, read what already exists, and keep the record in the tools where the work lives.

## Install

Gemba is a Claude Code plugin marketplace hosted on GitHub. Add it once:

```bash
/plugin marketplace add dedujeong/gemba
```

Then install any plugin of the family from it with `/plugin install <plugin>@gemba`.

## Update

Refresh the marketplace listing:

```bash
/plugin marketplace update gemba
```

This refreshes the listing only and leaves installed plugins at their current versions. To update an installed plugin, run `claude plugin update <plugin>@gemba` in your shell, or choose **Update marketplace** on the **Marketplaces** tab of `/plugin`.

## License

[Apache License 2.0](LICENSE). If you redistribute Gemba or a derivative work, keep, among other conditions, the copyright notice and the [NOTICE](NOTICE) file with the attribution to the author.

Copyright 2026 [Daniel Efraín Domínguez Urbina](https://github.com/dedujeong).
