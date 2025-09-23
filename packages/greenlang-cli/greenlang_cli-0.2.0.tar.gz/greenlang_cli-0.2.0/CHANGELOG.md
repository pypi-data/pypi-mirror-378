### Added Features

- Allow source type input via CLI flag (not scheme) [[#1783](https://github.com/anchore/syft/issues/1783) [#2610](https://github.com/anchore/syft/pull/2610) @kzantow]

### Bug Fixes

- OpenSSL binary matcher fails to properly detect letter releases [[#2681](https://github.com/anchore/syft/issues/2681) [#2682](https://github.com/anchore/syft/pull/2682) @harmw]
- TUI package count does not match package count in default table output [[#2672](https://github.com/anchore/syft/issues/2672) [#2679](https://github.com/anchore/syft/pull/2679) @wagoodman]
- .NET NuGet - dotnet-deps cataloger not working with syft v0.94.0 [[#2264](https://github.com/anchore/syft/issues/2264) [#2674](https://github.com/anchore/syft/pull/2674) @willmurphyscode]
- New path filtering logic excluding large number of unintended paths [[#2667](https://github.com/anchore/syft/issues/2667) [#2675](https://github.com/anchore/syft/pull/2675) @wagoodman]
- Syft TUI can hang when using license fetching from go modules [[#2653](https://github.com/anchore/syft/issues/2653) [#2673](https://github.com/anchore/syft/pull/2673) @willmurphyscode]

**[(Full Changelog)](https://github.com/anchore/syft/compare/v0.105.1...v1.0.0)**
