# Changelog

## [0.43.0](https://github.com/chanzuckerberg/vcp-cli/compare/v0.42.0...v0.43.0) (2025-09-18)


### Features

* add `data summary` command, facet datasets by field ([#115](https://github.com/chanzuckerberg/vcp-cli/issues/115)) ([5bb45a4](https://github.com/chanzuckerberg/vcp-cli/commit/5bb45a45a71ca008859a09dd614ed73ceeee26dd))
* add license and doi to vcp data search --full ([#114](https://github.com/chanzuckerberg/vcp-cli/issues/114)) ([0a54c29](https://github.com/chanzuckerberg/vcp-cli/commit/0a54c29cd4afaa9a1ea29bef9dea7f55f96e948a))
* add user-agent header and centralized HTTP utilities ([#93](https://github.com/chanzuckerberg/vcp-cli/issues/93)) ([6649919](https://github.com/chanzuckerberg/vcp-cli/commit/664991981a5bec8574850845443cb274d601ad29))
* Centralize GitHub authentication across all model commands ([#110](https://github.com/chanzuckerberg/vcp-cli/issues/110)) ([0d1cade](https://github.com/chanzuckerberg/vcp-cli/commit/0d1cadef247aaac8edf46ebf26d0a2a7c2edccbc))
* Enabling exact match for search ([#112](https://github.com/chanzuckerberg/vcp-cli/issues/112)) ([ba2b091](https://github.com/chanzuckerberg/vcp-cli/commit/ba2b0918e192dd5e611b743a728e472b796cdbde))
* extend `data search --help` with searchable field explanations ([#121](https://github.com/chanzuckerberg/vcp-cli/issues/121)) ([5c89091](https://github.com/chanzuckerberg/vcp-cli/commit/5c89091bb224e1986c0ed81ac6436cbbe94dec9b))
* Feature flags to disable model and data commands ([#111](https://github.com/chanzuckerberg/vcp-cli/issues/111)) ([22f6ce8](https://github.com/chanzuckerberg/vcp-cli/commit/22f6ce841a7b571bd62527615eee57ffdb5ec8f0))
* Fix workflow validation for mlflow_pkg naming conventions ([#124](https://github.com/chanzuckerberg/vcp-cli/issues/124)) ([d7b69a7](https://github.com/chanzuckerberg/vcp-cli/commit/d7b69a7d93698caf1dc082151777ba2229543c97))
* improve error handling for vcp data describe &lt;invalid-id&gt; ([#116](https://github.com/chanzuckerberg/vcp-cli/issues/116)) ([5ac776b](https://github.com/chanzuckerberg/vcp-cli/commit/5ac776baf7fb488a4a9b6df91d81efb88334f889))
* improved downloads ([#81](https://github.com/chanzuckerberg/vcp-cli/issues/81)) ([48912c3](https://github.com/chanzuckerberg/vcp-cli/commit/48912c3df5d5cdf165ed870a836d57a44ee19e70))
* passing user dataset to model adapter ([#95](https://github.com/chanzuckerberg/vcp-cli/issues/95)) ([786037e](https://github.com/chanzuckerberg/vcp-cli/commit/786037e266b89aa4956e918f7f27168ac2878d09))
* review comments fixed ([#97](https://github.com/chanzuckerberg/vcp-cli/issues/97)) ([944f794](https://github.com/chanzuckerberg/vcp-cli/commit/944f794caf3acc0d2de4bd663ac4f07a4e518be1))
* vcp data describe should include XMS in tabular format ([#101](https://github.com/chanzuckerberg/vcp-cli/issues/101)) ([f50c957](https://github.com/chanzuckerberg/vcp-cli/commit/f50c9572f3f209814bbef4e0664620bda4ea96bf))


### Bug Fixes

* benchmark run user dataset option ([#109](https://github.com/chanzuckerberg/vcp-cli/issues/109)) ([34ef1bf](https://github.com/chanzuckerberg/vcp-cli/commit/34ef1bfbaaa157fea515797673072754cd9efc95))
* benchmarks version, change model dir ([#117](https://github.com/chanzuckerberg/vcp-cli/issues/117)) ([e75ffae](https://github.com/chanzuckerberg/vcp-cli/commit/e75ffaed0aa6d53e233802a607122238bca83d4e))
* get the publish to pypi action working ([#119](https://github.com/chanzuckerberg/vcp-cli/issues/119)) ([0162a05](https://github.com/chanzuckerberg/vcp-cli/commit/0162a05bc39a16ba0d01406eefc46bcb430a0c6b))
* resolve authentication issue and add verbose logging to model init ([#96](https://github.com/chanzuckerberg/vcp-cli/issues/96)) ([ced6724](https://github.com/chanzuckerberg/vcp-cli/commit/ced6724e77340849358d29fb2fe420d0c59ba431))
* resubmission workflow validation for stage command ([#106](https://github.com/chanzuckerberg/vcp-cli/issues/106)) ([a2d897b](https://github.com/chanzuckerberg/vcp-cli/commit/a2d897bdc3609301e10a1db0c182836776665df0))
* unbound TokenManager ([#100](https://github.com/chanzuckerberg/vcp-cli/issues/100)) ([4c2ae41](https://github.com/chanzuckerberg/vcp-cli/commit/4c2ae41fafa58ab340b354fbfaa00a2cfe50dec6))
* Warn user for unsupported dataset and task ([#102](https://github.com/chanzuckerberg/vcp-cli/issues/102)) ([b5c0cde](https://github.com/chanzuckerberg/vcp-cli/commit/b5c0cde606704a989253949b8f46e2d896c929ec))


### Documentation

* add basic documentation for VCP CLI (VCP-3228) ([#105](https://github.com/chanzuckerberg/vcp-cli/issues/105)) ([cf2374a](https://github.com/chanzuckerberg/vcp-cli/commit/cf2374af536736b4f014fe40522c2a828e7366b5))

## [0.42.0](https://github.com/chanzuckerberg/vcp-cli/compare/v0.41.0...v0.42.0) (2025-09-09)


### Features

* add model status command and workflow functionality ([#92](https://github.com/chanzuckerberg/vcp-cli/issues/92)) ([a2da84f](https://github.com/chanzuckerberg/vcp-cli/commit/a2da84fe5da96d7ac5011bacc04627f804c65fb5))
* implement refresh_token flow ([#88](https://github.com/chanzuckerberg/vcp-cli/issues/88)) ([fcf2b98](https://github.com/chanzuckerberg/vcp-cli/commit/fcf2b98444dcfb568cadbdc02c2a3a759942a5d2))
* improve data search table UI with Rich tables and dynamic pagination ([#83](https://github.com/chanzuckerberg/vcp-cli/issues/83)) ([1159df6](https://github.com/chanzuckerberg/vcp-cli/commit/1159df67316958467ad0fdb5cb25469987e5e84e))
* improve model init command ([#90](https://github.com/chanzuckerberg/vcp-cli/issues/90)) ([7534ec0](https://github.com/chanzuckerberg/vcp-cli/commit/7534ec0601d007f1c287ef71c033533561a976df))
* search - show total matches and paginated progress ([#87](https://github.com/chanzuckerberg/vcp-cli/issues/87)) ([a4af991](https://github.com/chanzuckerberg/vcp-cli/commit/a4af991037e099d3614dc97afb1b5350d08d7f49))
* VC-4055 uptake benchmark api in vcp cli ([#84](https://github.com/chanzuckerberg/vcp-cli/issues/84)) ([f69a01b](https://github.com/chanzuckerberg/vcp-cli/commit/f69a01ba1a73ba39e93e2daf27bf6406f2fdb617))

## [0.41.0](https://github.com/chanzuckerberg/vcp-cli/compare/v0.40.0...v0.41.0) (2025-09-04)


### Features

* add conditional scopes column to dataset search results ([#53](https://github.com/chanzuckerberg/vcp-cli/issues/53)) ([4eb95f0](https://github.com/chanzuckerberg/vcp-cli/commit/4eb95f0ea28b1a6bc2718143fcf07e5dd27554b1))
* Add initial docs pages ([#68](https://github.com/chanzuckerberg/vcp-cli/issues/68)) ([abd8cfe](https://github.com/chanzuckerberg/vcp-cli/commit/abd8cfe766bb150cb853e6369ce3181c57423f7c))
* add model stage command with batch upload functionality ([#75](https://github.com/chanzuckerberg/vcp-cli/issues/75)) ([e3db8fe](https://github.com/chanzuckerberg/vcp-cli/commit/e3db8fea73ea47b7e08bc8c5b1668eaaa42c07a6))
* Add Neuroglancer data preview command ([#80](https://github.com/chanzuckerberg/vcp-cli/issues/80)) ([a58d285](https://github.com/chanzuckerberg/vcp-cli/commit/a58d285a6729623dd3f4ef48866fc83255393b2f))
* **auth:** refactor logout to use Cognito token invalidation ([#61](https://github.com/chanzuckerberg/vcp-cli/issues/61)) ([8899e60](https://github.com/chanzuckerberg/vcp-cli/commit/8899e6040f680a314fbdc1a18a675f34ead888b2))
* benchmark list, run, get commands ([#71](https://github.com/chanzuckerberg/vcp-cli/issues/71)) ([bbba9f5](https://github.com/chanzuckerberg/vcp-cli/commit/bbba9f5cb805a196d501fe0530625bc0b81a048e))
* refactor model download to use presigned S3 URLs ([#69](https://github.com/chanzuckerberg/vcp-cli/issues/69)) ([f3c6c48](https://github.com/chanzuckerberg/vcp-cli/commit/f3c6c488fb31ac9e1e4471c82d5ea6720886150b))


### Bug Fixes

* get build and tests working again ([#76](https://github.com/chanzuckerberg/vcp-cli/issues/76)) ([4d2033c](https://github.com/chanzuckerberg/vcp-cli/commit/4d2033c7e8bdcfe974e1b603a47a287310ea4835))
* make workflow manually runnable ([#67](https://github.com/chanzuckerberg/vcp-cli/issues/67)) ([1ae6098](https://github.com/chanzuckerberg/vcp-cli/commit/1ae60986a09b568e0d3883cb5a3d1b54208f8238))
* resolve model staging authentication and update configuration structure ([#82](https://github.com/chanzuckerberg/vcp-cli/issues/82)) ([944d2a3](https://github.com/chanzuckerberg/vcp-cli/commit/944d2a3c07e7574c96859d333c5599ffeb5f7bdb))


### Documentation

* add github action for publishing docs to pages (VC-3228) ([#66](https://github.com/chanzuckerberg/vcp-cli/issues/66)) ([84c95f3](https://github.com/chanzuckerberg/vcp-cli/commit/84c95f3a8e68a0ce1d7ff605abfa2320f73de91c))
* fix repo urls in readme ([#63](https://github.com/chanzuckerberg/vcp-cli/issues/63)) ([03b55d9](https://github.com/chanzuckerberg/vcp-cli/commit/03b55d9f3a92448154198a909fe5952d07afe51e))

## [0.40.0](https://github.com/chanzuckerberg/vcp-cli/compare/v0.39.0...v0.40.0) (2025-08-25)


### Features

* testing release-please ([7e63e56](https://github.com/chanzuckerberg/vcp-cli/commit/7e63e56d6c73c74f595a6de2893be2c3bb3507a6))
