# CHANGELOG

## v1.6.1 (2025-09-19)

### Bug fixes

* **DataStore**: regression of handling of existing objects ([`28bd44c`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/28bd44cf019aea0203ad252fd434860f45a1e54a))

* **DataStore**: proper forwarding of spacePrefix for filtering relevant spaces ([`c4117f3`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/c4117f3b04b9f6237f6d8471bef2d76c379e6f11))

* **DataStore**: use the URL provided by constructor ([`fcc46fb`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/fcc46fb941006b489054dc492f433e62d77cb605))

## v1.6.0 (2025-09-19)

### Bug fixes

* **DataStore**: f-string syntax ([`9166382`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/916638264be58e75fdfba15d9c6a6584ace92199))

* **Tests**: pybis module required for collecting in new datastore module ([`ea6a21d`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/ea6a21df3656dcc5f926aa7ff67a7136806ded3b))

### Features

* **DataStore**: new module for managing objects in OpenBIS ([`cdf0a27`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/cdf0a27c0ae1412acd5329532ec8ec1fa7e6be94))

## v1.5.1 (2025-08-04)

### Bug fixes

* **readSSFZ**: split in two: ssfz2json for converting, ssfz_compare for diff-like compare ([`e8b24fe`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/e8b24fe796430bb4b09fa23dcd204e6162051f79))

## v1.5.0 (2025-08-04)

### Bug fixes

* **readSSFZ**: rename command readSSFZ -> ssfz2json for avoiding name collision with function in readdata module ([`dde1d10`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/dde1d109b70de0cd0cb712cfc4f19a3be2cbd880))

### Features

* **readdata**: jupyter_analysis_tools.readSSFZ cmdline tool to convert .SSFZ to .JSON and diff-compare .SSFZ files (their metadata) ([`46dc633`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/46dc6338052a9dd875326d2a38cc5b6621439270))

### Refactoring

* **utils**: formatting ([`b23f195`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/b23f1957149a9ae77a28f330eba3249d3fe3d2e5))

## v1.4.3 (2025-08-01)

### Bug fixes

* **utils**: makeNetworkdriveAbsolute() should return input path if no changes needed ([`2ec96d7`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/2ec96d7066a3473c6d27a6e6d01c640f6c142346))

## v1.4.2 (2025-08-01)

### Bug fixes

* **utils**: makeNetworkdriveAbsolute() with FQDN resolution ([`f4591fb`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/f4591fb46dcfeafbb1f63c4323efbb8aea302a92))

## v1.4.1 (2025-08-01)

### Bug fixes

* **utils**: networkdriveMapping() for Linux, with tests ([`3f4deeb`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/3f4deebdf57cc9162121c26d5d7d8484f1f0ec63))

### Testing

* **utils**: remove debug output, should work now ([`1117c89`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/1117c89d4206c6880373e3b8765dff6e48d3ccd5))

## v1.4.0 (2025-07-28)

### Continuous integration

* **dependencies**: removed unused requirements ([`592bfe1`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/592bfe1e592cf3776dc626d0df453d95e527f8b8))

### Documentation

* **readdata**: function docstrings and clearer function arguments/variables ([`365effa`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/365effa474e700beb5e9194a75f4ceb8eb9c9e7e))

* **Changelog&Readme**: updated by template ([`ab2efa8`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/ab2efa808b7c96b9bf63fdb333c09f070c19b754))

* **readme**: note on reapplying project template ([`a8d0176`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/a8d01764645c9996bb1e2af60ba6c2d1ee33363a))

* **readme**: .rst version not needed anymore ([`a59e9a8`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/a59e9a81b7165c67f6c02906d0266d93f7deaca3))

### Features

* **plotting**: plotPDH() plots a given .PDH file path with pandas with reasonable defaults for SAXS ([`d592638`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/d592638e613527eb471e06291bdbcd401f54c7b6))

* **Utils**: naturalKey() can be used as sort key for natural file sorting ([`a60f186`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/a60f1864a87c435a165cebc885f0b55de52db796))

* feat: readSSFZ() convenience function ([`c3e882b`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/c3e882bc1d26be578b41c60c1f6b0df94cd83025))

## v1.3.2 (2025-07-23)

### Bug fixes

* **Project**: let the template generate supported python versions ([`8acfa6d`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/8acfa6d337ea4b8b92f8ea623e961af1be9a0f17))

### Continuous integration

* **coverage**: revert config regression for coverage merging ([`dffe265`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/dffe265af9779253a698f241e725d0ea03ea2979))

### Documentation

* **readme**: additional fix for readme.md ([`795046f`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/795046f73ada0ae85b4eb050c8453cc096c43122))

* **readme**: in markdown format for combining with changelog ([`eb6b904`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/eb6b904136697ddc2427369a605058e464d49351))

* **readme**: use markdown format to allow combining with changelog on PyPI ([`395b2c0`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/395b2c0c72232e9109ca50c5b84a7fce2d423df4))

## v1.3.1 (2025-07-23)

### Bug fixes

* **Project**: update manifest and flake8 config, reapplied template ([`c98c648`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/c98c6489423a45d8a195fda32396ea9d9d18b9eb))

### Code style

* **utils**: satisfy flake8 ([`2e3dc36`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/2e3dc36ef21e60f4fe7b8caea567411cc69967c0))

### Continuous integration

* **semantic-release**: replace .cookiecutterrc by .copier-answers.yml ([`2030c88`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/2030c88dfb0ca69ac332380e33b3baed9cb6cf44))

* **coverage**: coverage-report fix ([`1bd26b7`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/1bd26b71abcb090ef32cb2fbdd05b978bce5144c))

* **GitHub Workflows**: remove templates, rendered by *copier update* ([`8a637a5`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/8a637a5b34df4a3ec6a4e8cae97a9d3e24ad2e5c))

* **GitHub Workflow**: publish depends on all other job to be successful ([`efc1f22`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/efc1f223aa2da882d43b27406a2f20113c2c8879))

* **Template**: latest GitHub Workflow templates applied ([`7d87906`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/7d87906c852cb2b57704c45db0b19c7a1ae513a2))

* **coverage**: fix path name matching rules ([`37bd2d9`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/37bd2d93a8fe10a3355feee6779f45bd9161a88b))

### Documentation

* **Copyright years**: update ([`cee35e6`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/cee35e6fe92ae27575bd7fb4a7a2638cd1c931b2))

* **Contributions**: Authors update ([`dd5a5c4`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/dd5a5c4d81732821057bcc200f462159cffa760b))

### Refactoring

* **Project**: GitHub Workflow templates fixed ([`b346b28`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/b346b282332f0f7f81b724509a4004e6a69d7791))

* **Project**: GitHub Workflow templates updated ([`235c4d9`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/235c4d9c53997fdf4c08913361fb57167939cd7c))

* **Project**: switching to copier for project template with update mechanism ([`0d3064b`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/0d3064b8cef45667b0964aab248b583424946207))

## v1.3.0 (2025-07-16)

### Bug fixes

* **utils.extract7z**: informative info message ([`80d2f71`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/80d2f7134992d59f0bfd7f5e7bc27772f77cd452))

### Continuous integration

* **coverage**: fix coverage artifact name for multiple matrix.os ([`f471599`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/f471599b8c86e29fd20b78f7cbd9291c3a6dd98a))

* **testing**: test on Windows as well ([`4a83c39`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/4a83c3924bcb820ef0728af40b86a0f6622dfef2))

### Features

* **utils.makeNetworkdriveAbsolute**: new routines for translating a windows drive letter mount to its network location ([`823a6bf`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/823a6bfe126829381bc14d34578f342f4b9d3e8f))

## v1.2.2 (2025-07-15)

### Bug fixes

* **readPDHmeta**: use unique dict keys, the xmk *key* can occur in multiple groups in PDH ([`ef41c81`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/ef41c81d40d801b5baf86f56cf9012ca35d2ccde))

### Documentation

* **pyproject**: revert specify readme+changelog document types ([`1baa762`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/1baa762d441fe0a1b7b663b9d0589de857277426))

* **pyproject**: specify readme+changelog document types to render overview on pypi correctly ([`6e4d1e5`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/6e4d1e56640b604f971ddca8dabd8d1aff5c9bf1))

* **ghpages**: make sure .nojekyll exists after purging old html docs ([`4847845`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/4847845cc06884b6e589b26897e83411d649ef4d))

## v1.2.1 (2025-07-11)

### Bug fixes

* **readme**: trigger new version after style changes ([`8b2b5e9`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/8b2b5e93c0f24ae59afaa764abdc508e994946b4))

### Code style

* **__init__**: imports format ([`6f07790`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/6f07790a04e43736b1c0fbce0eac54d0b661a7cf))

* **utils**: satisfy flake8 ([`9657474`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/9657474e94a4d9887c4a6b653e0ffa403e666d02))

* **readdata**: satisfy flake8 ([`36bf6e8`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/36bf6e8be67a2ebd345c5557c2352710bcebed82))

### Continuous integration

* **workflow**: publish only if the docs are good ([`a663ed3`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/a663ed3d1fd87079a4fd7cf419132a129280a562))

### Testing

* **utils**: fix imports ([`ddd5369`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/ddd5369b8037f583c6900aea25522a56126c9d32))

## v1.2.0 (2025-07-11)

### Features

* **readdata**: readSSF() renamed from readSession(), tests added with expected JSON output ([`e2197f6`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/e2197f6bcb032c1bc1a9a7435e024dda763228c4))

* **readPDHmeta**: routine for reading metadata part from .PDH and .SSF files ([`ea6a1d5`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/ea6a1d554f3763fc05022ae8e4e8909f0993cd43))

### Testing

* **readdata**: path separator depends on platform ([`1b2866f`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/1b2866f13307c2cf2dedc59f36d7372442ddbfd8))

* **readdata**: testdata files and testing, using pathlib instead of old os.path ([`aeacfa4`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/aeacfa4a949d7293f2cd3ce5e3004fddf20ecc02))

## v1.1.0 (2025-07-10)

### Bug fixes

* **packaging**: add dependencies for project and testing ([`2729a45`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/2729a45958893c9acd07af9463bbf7d657db626b))

### Documentation

* **utils**: reformat doc strings ([`1cf9b9b`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/1cf9b9b969e075a75a41e19bfb526378b68a0ed7))

### Features

* **utils**: addEnvScriptsToPATH() ([`a8c22e0`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/a8c22e0d37a5627d5955c1f7f7eebcb0bc99206e))

* **notebook_utils**: remove method for finding notebook file path currentNBpath() ([`13a5a60`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/13a5a60436c7926c478f2ab3f2c309a86b653218))

### Refactoring

* **utils**: appendToPATH() using pathlib, verifed test included ([`35f37fc`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/35f37fc19cdcf4b575dc0525400f3c0212bb0faf))

### Testing

* **readdata**: test data for reading PDH and SSFZ ([`9b919d2`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/9b919d24e1fa5679b49cebf576e471d6e4e9b655))

## v1.0.0 (2025-07-09)

### Bug fixes

* **packaging**: add required dependency packages to project config ([`43076e2`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/43076e2fd27e511545d8f1ec12752435cf5153c6))

## v0.1.8 (2025-01-30)

### Bug fixes

* **distrib**: scipy.integrate.simps does not exist in recent scipy versions ([`b59edc1`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/b59edc18a6df3bbee23a3ba6e8b8412c294c20d1))

### Continuous integration

* **changelog**: format commit by using their scope only, not repeating the tag ([`6b72fe7`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/6b72fe766d121d7ea38c452d093368f84760155e))

* **semver**: allow message tag *enh* for enhancements ([`0810b4f`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/0810b4fd58e1b2383313496b657a800078260c83))

### Documentation

* **Changelog**: use semantic-release detected scope if available, unchange summary otherwise ([`ca803e7`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/ca803e71d1a5915fc72a4a2feea55616533ff54e))

* **Changelog**: omit *empty* versions without relevant changes ([`87b7f23`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/87b7f2360c5224a6570f8687e8008e2293b81ddb))

* **index**: show link to github project on left sidebar ([`3fad5a8`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/3fad5a870801904a636a114d70ff418886c3f2a6))

* **Changelog**: don't show *chore* changes on automated build config (CI) ([`10c7ee3`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/10c7ee3190969322b3e19b5ff0ce5e1e911bff59))

* **Changelog**: exclude commit message body from changelog rendering ([`e37e82c`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/e37e82cef2fb27e33d3f0c14d3f38189b97c17d7))

## v0.1.7 (2024-03-26)

### Bug fixes

* **distrib**: Distribution.plotPeak() legend background more transparent ([`4a148f1`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/4a148f1d4ca4b0aa5335f8982c5f8348fb906e78))

### Refactoring

* **notebook_utils**: whitespace ([`30feb51`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/30feb51175fa55c694cc88995a94e7ff26303b9b))

## v0.1.6 (2024-03-25)

### Bug fixes

* **notebook_utils**: notebookapp import path changed ([`27266db`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/27266db0c62a1e35be8bfb90194b001f29d4534c))

## v0.1.6-dev.1 (2023-03-27)

### Documentation

* **analysis**: minor fix ([`601a6f7`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/601a6f7dbbf383810add39620748808c51af6fa3))

## v0.1.5 (2023-03-27)

### Bug fixes

* **reBin**: module renamed to binning, fixes name clashes with docs gen ([`ec959fb`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/ec959fb9e1b51d69cdceaf7784b27df22aa6f4d4))

### Code style

* **format**: fix whitespace and quotes with black ([`b0b7dba`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/b0b7dbaac59528ead6c663165c8d4dab3aabcdfe))

* **binning**: fix quoting by using black formatter ([`61603f7`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/61603f7de8640437ccd277faefc2d31fa1e1e232))

### Documentation

* **cleanup**: removed obsolete module doc, replaced by autosummary generated files ([`c0d4256`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/c0d4256a5bcbb83a9a9c0ca0dd3001b9d111cb4b))

* **format**: fix formatting with black ([`5de80d4`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/5de80d4d528bfb2bf106fa38d2cd8f30f6421f19))

## v0.1.5-dev.1 (2023-03-27)

### Code style

* **config**: string normalization, double quotes ([`e8edbc4`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/e8edbc437b3c6876fae1ff72ad24edbcbe82a8f8))

### Documentation

* **General**: config updated by cookiecutter ([`6c9ddfb`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/6c9ddfb9777cb344378f5a0d86e204dc016a2068))

## v0.1.4 (2023-03-03)

### Bug fixes

* **readme**: license link ([`f98f736`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/f98f7362dd0278210894f138dd7646c8bc92cc9f))

## v0.1.3 (2023-03-03)

### Bug fixes

* **tox**: clean env ([`0135426`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/013542651eb2bd9a7e2d3b2e8ef837c38501b578))

* **Package**: cookiecutterrc updated ([`7b29a17`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/7b29a1764f972379086abb51194604423c9714f2))

* **tox**: cleanup env removed pckg build files ([`ecd8648`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/ecd86485ec0fe67f646d06ca134fe97310f7a3f5))

* **GitHubAction**: migrate to pathlib.Path in template rendering ([`d3ae5db`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/d3ae5db8f657e929f4139bb17bb746f7b03961d3))

### Code style

* **pyproject.toml**: use double quotes ([`8f902a2`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/8f902a25b0578babc6e2ad3b72cc7adff94361e2))

### Documentation

* **readme**: adjust version numbers in readme as well ([`5700694`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/57006942e6625faf9f36dca1bac0719706b4d000))

* **readme**: using test.pypi.org links ([`240e58c`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/240e58c87ef0cf0dc3d195f237a09c8e8a717e75))

* **Package**: update project description ([`704a0b5`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/704a0b50a727ef36f685d27ce068103ffa60ca99))

* **comments**: add some, remove obsolete ([`efe2689`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/efe2689707f410a18cce331f9cd3732fa2190640))

### Refactoring

* **docs**: config adjusted by cookiecutter ([`84e00f0`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/84e00f061bc5780a0b3457ec95847b266dcfa2cc))

* **metadata**: update project meta data ([`9d6982c`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/9d6982c960fef68b4c155d05162491f2b6e8b4d0))

### Testing

* **tox**: find sys Python version when generating files if not specified explicitly ([`e690193`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/e690193e2a7f3f34dd8457b459c82ec1b9643e0e))

## v0.1.2 (2023-02-24)

### Bug fixes

* **Documentation**: doctest format in *distrib* ([`5942972`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/59429724fd41e62c7717fa185e7f5c5c1e5b50d9))

### Documentation

* **distrib**: generate entries of submodule *distrib* ([`c8055c6`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/c8055c65ac1d49a757ee30f9cd34fc18e8445944))

## v0.1.2-dev.1 (2023-02-24)

### Documentation

* **utils**: generate entries of submodule *utils* ([`762a548`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/762a548a967cf54aed7a58f9d84e4cf6e98e25f7))

### Unknown Scope

* v0.1.1 ([`738fdd4`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/738fdd44b27881360f51f540f28cda4aed2e9005))

## v0.1.1 (2023-02-24)

### Bug fixes

* **docs**: allow markdown format in changelog ([`593356b`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/593356bb0fb6ea7a6c028b99032ed9742708cb6b))

## v0.1.1-dev.4 (2023-02-23)

### Documentation

* **readme**: updated links and badges ([`2e0329d`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/2e0329d510bb5c090d093818c0536993c6292a8a))

## v0.1.1-dev.1 (2023-02-23)

### Bug fixes

* **tox**: removed tox-wheel settings ([`cacbfe3`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/cacbfe36af39f613efc4651bed4c8875c80c60c5))

### Documentation

* **config**: clean up version definition ([`c18c67f`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/c18c67fae8852f2acdd79ffe3bcb89aa5821c797))

* docs: removed disabled config ([`3059ff9`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/3059ff9fba6a17b845441cd283c0f498c05beab2))

* docs: disabled incompatible sidebar config with furo theme ([`61959be`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/61959be18f26e304042c21872f50dda23635caae))

### Unknown Scope

* added tox-wheel to ci required packages ([`7eae72c`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/7eae72c4a2e977c3efc56b5d9c8da76d67d44536))

* readme: updated badge for docs ([`6e78a50`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/6e78a50e5b9b7c47498cdb7bc3c4a493a1cacfe3))

* comments added ([`af59a8a`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/af59a8a01d7891a35a2c1b9a76f303b5dfb1139a))

* readme: fixed link to coverage report page ([`1e173dc`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/1e173dc08abec18fb231dc56432bab3b1244b614))

* docs env needs toml module for reading values from pyproject.toml ([`6a2d755`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/6a2d7555ce44ff820f3375dca9cd0714a2e54c49))

* applying isort config ([`02c6bbc`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/02c6bbc9cd0cd06375bd263efb072d9f0116ac69))

* updated isort config ([`78e38e9`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/78e38e9d298bc384695c9104195f749cdcc6a52d))

* docs config: using urls defined in pyproject.toml ([`33d5f23`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/33d5f2338e3a95212c21396d9007bac1495f30a8))

* moving isort config to separate file, not picked up from pyproject in a pre-commit hook ([`bfaf1e0`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/bfaf1e0ab5be225e5e4c34ffc8b1ea8bedb59688))

* pre-commit uses pycqa repo for isort ([`4b4a31c`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/4b4a31c15e9a07455fe9796e17ddbce5f23456ed))

* updated pre-commit hook versions ([`4fdec5c`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/4fdec5c7bab285cb53665d23d063c3ef117ce077))

* docs switching theme to furo ([`ceab414`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/ceab4148b9fbac53f5ffd936da15f39bedfad968))

* moved project meta data from setup.py to pyproject.toml ([`a73f9a7`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/a73f9a7c52df781bffcf388a2e5932573bbc51a7))

* removed obsolete dependency from github action template ([`0d071bc`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/0d071bc80d627395a569d007f05ba26e880ad28b))

* tox: removed coverage combine for single runner, useless ([`831fa6b`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/831fa6b16ac6053dfff570ca3098e4610709b039))

* tox: updated bootstrap template for github actions ([`47528b8`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/47528b8c2705a4f80339561d877f14038ab19691))

* tox: build env for package building ([`91969bb`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/91969bbe7bf7e69f006e439166db2d7ff62a063e))

* tox.docs: generating placeholder for github pages; ([`bcaaa54`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/bcaaa5448d764b7969f1885740b4914df74ed965))

* tox: coverage combine command added ([`bc45701`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/bc45701fc9cf656aa191b2b61df60d10f448be4f))

* readme: removed unused table def ([`9665ccf`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/9665ccf5f5f3d753135dcdf477c09f9212f512eb))

* readme: coverage badge added (from report) ([`6570cf1`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/6570cf1a6c7036a8998536740867819a52ed084b))

* tox config format fixes ([`210b5e3`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/210b5e39a37ecdf1abaf083379e05fa8d5e6726a))

* readme: download numbers from pypi ([`7082226`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/7082226643aef7bcdd4d42d3109653e77fde230c))

* readme: minor formatting edit ([`645e0f8`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/645e0f8f87965e5e42e807bbbb573b861ab7f1c9))

* readme: adjusted badges ([`343dc81`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/343dc812104a84eea4fe028656edb4befaefb8e5))

* fixed broken link ([`e41268d`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/e41268d735e8ad78692db43b8581975993946782))

* removed missing tbump.toml from manifest ([`1a54907`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/1a549076017a9608d33b428e750216db8d135ead))

* Dependabot config ([`4578709`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/4578709355e0d4ad839b61f42ff2af01c85ee7ff))

## v0.1.0 (2022-11-10)

### Documentation

* docs: let sphinx use numpy directly instead of mockup ([`9b6ec6d`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/9b6ec6d3f4123b8bfb0934cdb2e8a0df0933daee))

* docs: sphinx extlinks syntax updated ([`0866ee7`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/0866ee71cbfa5b8f1134858a44fe8e360707faec))

* docs: URL updated ([`146039c`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/146039cc13670cfc62ca295935567e14ba38d738))

* docs: fix docs gh workflow spec ([`49d7e93`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/49d7e9305987cb918e3ea3c812c7aeac2fe36c56))

* docs: fix gh workflow spec ([`b977751`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/b97775186b5554a9bf260c6ad34ed63481571eae))

* docs: fix gh workflow spec ([`e23c22c`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/e23c22cae9045a75c7ff41ddffdd44c93fd027da))

* docs: fix gh workflow spec ([`024295d`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/024295d797da7274071cf54085d614a2f8e96a53))

* docs: fix gh workflow spec ([`12adda9`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/12adda94ad39ce9c4e61687cdbf829c196ff81ed))

* docs: fix gh workflow spec ([`f062d12`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/f062d12d3f2cb430c643228573cf76aef31dfee6))

* docs: updated urls and gh workflow spec ([`66a0704`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/66a07049567a524a82633547c8006ed1630238c1))

### Unknown Scope

* tbump config updated ([`e17de91`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/e17de9111659992b9419efc7e07c58172737e285))

* package classifiers and readme updated ([`4cafdca`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/4cafdca402cb8171b7ab32de4c93feeb94e00af4))

* tox: removed passenv=*, more strictness ([`818ffa1`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/818ffa1a590e42aa2599679755ffaeea794d346f))

* moved tbump config into pyproject file ([`b8b9881`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/b8b9881fec80199ec5e730d33fbb5a427acfd9c1))

* isort excludes .ipynb_checkpoints ([`db90f62`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/db90f62015abc54088eae146419863ff9a1c38ac))

* flake8 config updated ([`20a46bc`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/20a46bc9ca8d09f79795d10b91ee759042045f08))

* reformatting according to pre-commit config ([`54fd524`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/54fd524c6791ec3ac6a7f95a153bf739c35bf8d1))

* tox:check: let check-manifest ignore macOS meta files ([`d301bd2`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/d301bd2d02d5030e7c50071187bb6f4ea895c63e))

* gh: removed obsolete testing.yml ([`1ce898d`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/1ce898dfc5c547bbef27e159cc377478f26d39d5))

* readme: updated badges ([`790bf44`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/790bf44e76f1f25959672536cbe6c588efe2ac17))

* readme: updated badges ([`99ddde2`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/99ddde2155dab5bbda3b632d58576a85f3dbf701))

* readme: updated badges ([`f18418c`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/f18418cc52850c6622c4cc0ab6ceb01f4e4839eb))

* readme: fixed badges, renamed testing -> tests ([`3efb28f`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/3efb28fdfbef47fd6a776fada5a7f0b8804a4fa7))

* removed pypy test environment from github actions ([`17f8515`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/17f8515fda7746b6c43e4e2ff94fedce95e9a2ae))

* removed pypy test environment ([`e2cfa0a`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/e2cfa0adbfdf3b3d927949a5f43e37ae1367911a))

* conda_environment.yml not needed anymore ([`b28806f`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/b28806f0f8aa7faa60b6162b05a84386e72e4f1c))

* tested testing config, enabled doctests ([`a273d9d`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/a273d9d218ca151f19623fd7b978557e23a55ea2))

* generate github testing workflow with tox ([`f04bb7b`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/f04bb7bae96a417d56d545be61423930a210fa4a))

* tox:bootstrap: don't fail for macOS .DS_Store files ([`0445011`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/0445011ea7721471aa6caee06565062d041a6110))

* tox setup added and works partially ([`4956d25`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/4956d2573999ed7fd5aeb5dc8f22b99ef5e6c6da))

* moved implementation to src subfolder ([`a917c30`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/a917c30fbfabd5f14666b36305484f3d8dee8cd6))

* updated gitignore ([`2499639`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/24996396b32b4991cfb9450e028f0d73b3fff138))

* readme: updated docs gh workflow badge ([`3bb0b40`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/3bb0b40ffd5c95869151efa5274e1b4e9bc5ec60))

* documentation setup ([`fa494d0`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/fa494d05c78ec8ccd6d98caedd0c67479bc301bb))

* editorconfig added ([`61299aa`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/61299aa1904401865aa169112acdada96d29f5fe))

* pre-commit config added, running reformatter, import sort and flake8 linter for the first time ([`0537b68`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/0537b68cc3e139911e7b65b2bb4d72ca9d85dac9))

* let git ignore macOS meta data files ([`6e35aa3`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/6e35aa33bbacb4bf3a2dc041c59aee17ae793f13))

* distrib: removed radius-specific scale factors when converting (LogNorm) distribution parameters ([`bf7bcca`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/bf7bcca230d1d3aeb0c3aea41035b71180d33a01))

* distrib.Distribution.xlabel added ([`30ad6c1`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/30ad6c138545afb08f1c68466405f8dd09d0cfab))

* indicate python raw string to protect LaTeX commands ([`4483cb5`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/4483cb525b50aa04a5f9105a1910e333880e3110))

* utils.setPackage() prepend local module search path ([`247973a`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/247973af69237825dd8f4def2accef20b2941c47))

* distrib: handling logNorm params *distrPar* as dict now, doctests added ([`0aad717`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/0aad7179132ec90f715badd0f89e99adb86e7016))

* readdata: fixed imports, allow disabling info output by *print_filename* arg ([`aa1cf22`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/aa1cf22f9af49db58a43be7feaf76206d6a84af5))

* readPDH replaced by a pandas.read_csv wrapper ([`9d3c6a4`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/9d3c6a45b5875e45289d6678695b2cc3d387cbfb))

* fixed __init__ ([`55e9d20`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/55e9d20dc75fad8e73c459a96d351043ace693f4))

* readPDH: detection of XML section updated ([`096521f`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/096521f678ca4c8e42161b2b59550a0f8cc636e3))

* updated GitHub Action ([`7844e90`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/7844e90b2457dea869fa96cdd9b1d1e5f341439f))

* utils: moved jupyter notebook related helper to separate file/module ([`4bbee4e`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/4bbee4ef4dde0a8591215afdd527f74f9b44d303))

* testing workflow runs doctest on utils module ([`6d19fd4`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/6d19fd4a2bf9dd1250707bc5b02f8d375865aff3))

* utils.isList(): doctest added ([`f27855d`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/f27855dff40990b98a901d0f8d0f7981deae3332))

* testing workflow: fixed python versions ([`a71e60e`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/a71e60ea8173d0549b8f8bfd3e9d03d93dab52e8))

* defined new github action for running tests ([`3589299`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/3589299bd25d5c9e7822fb96a9f73badb43d39f1))

* Distribution.uncertRatioMedian() added ([`8a2ef2d`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/8a2ef2d44237c33c617cad02ce16309b1984f648))

* distrib.getLargestPeaks: fixed sort order of largest peaks ([`9cca28f`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/9cca28f442a75bba1097c670ab3c3c10d6578fa2))

* show LogNorm params for each peak ([`64b60e7`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/64b60e7094ff980dd8eba0a12e83fa1dd5f4ef4c))

* introduced distrib.Distribution for finding and plotting peaks ([`6beadf3`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/6beadf3ae55330ec5ec362263f2afef449fa0080))

* analysis.getModZScore() calculates the modified z-score of some data arrays ([`2250a59`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/2250a59f4aca728ccf79b041b5e148835afb3182))

* distrib.findLocalMinima: skip peaks with less than 5 points ([`712d590`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/712d5904218beb9e129d30fb7f6dedb84e050175))

* distrib.findLocalMinima() fail gracefully on single peak ranges ([`45eb76b`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/45eb76b5ab67ad0d190c88ff4e6846e16e446994))

* plotting.GenericResult with x-axis label ([`1a14688`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/1a1468808a0fb0458a6b8a06051ec6dcb7434edd))

* missing numpy import ([`8c01e86`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/8c01e86c26f0c1a500ad21174189fba1ffb08836))

* added plotting.GenericResult ([`96cf6c8`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/96cf6c8f7062fce9b83404e3f86658d6a9e73bc4))

* distrib.normalizeDistrib: convert pandas.Series to numpy.ndarray first ([`a50f78e`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/a50f78eded5f12f3204a25046b3b6f4ed6164562))

* distrib.findLocalMinima() added ([`0ac94c7`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/0ac94c760f93bfa53bc823d1ccec8901eb5af306))

* distrib.findPeakRanges() filters monotonously increasing/decreasing 'peaks' (artefacts) ([`7b967c0`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/7b967c00772bea6adce2e735d9c4f54bc1e70d18))

* distrib.distrParFromPeakRanges: convert pandas.Series to numpy.ndarray at the beginning ([`bb19270`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/bb192703cece3027d5766f66c8c5a9c27f61df32))

* distrib.test: fixed indents, replaced tabs by spaces ([`da8f402`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/da8f40236fd5906bbc8c28a36ce8eadd1f2b8c36))

* plotting: increases limit for warning about many plots ([`ef8a6fd`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/ef8a6fd7ff86941eef5f45af38d644a1a048bfef))

* plotting.plotVertBar() now with kwargs being forwarded to matplotlib ([`35dbce1`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/35dbce14a89472aa121483ab96078bcd9270d9f7))

* utils.updatedDict() added ([`03fe42c`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/03fe42c0702efb7a49493c96f4d5768f72c8e86f))

* isList() moved to utils ([`4367a6c`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/4367a6c2c1245a5c3cfb071afd3bccdd96591cb3))

* datalocations.getDataFiles() argument handling lists and non-lists ([`4ee348a`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/4ee348a8f5caebac6f4c4009e5f999abe05237a0))

* datalocations: filtering file names with in-/exclude patterns ([`d65efff`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/d65efffa2df938033443ba54fa09570eaf4afbc3))

* datalocations.getDataFiles() with filename pattern argument ([`7d10c9c`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/7d10c9c237f8b48a9c6b8ced05a7bb92c2016ec8))

* plotting.createFigure(): fixed argument ([`ba6ae3b`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/ba6ae3bc2e1ddde3fdda9b9e0bc02b58dcf2ed6b))

* added modules for plotting and distribution helpers ([`3472db8`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/3472db8e9217c9ae0fa1bb3a078e0af04d3328cb))

* utils.fmtErr() ([`56457ae`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/56457ae8a37ff474165c2c9959e115f8c341c48c))

* utils.grouper() ([`a5ad6aa`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/a5ad6aaf80c1dc6be417fd20c22c84c93046dd88))

* utils.setPackage() added ([`969aae8`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/969aae82848b53a0d6257877011dc89e3eb10852))

* datalocations module added ([`f4fb7ff`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/f4fb7ffd0dcc2eab2319e257d0c8dca5be1d6d75))

* utils: OS helpers and for 7-zip added ([`629c0fa`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/629c0fab2e2a9012b76e069ed199107ab6e2e179))

* utils.setLocaleUTF8() added ([`8dc76f3`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/8dc76f3be20b754df2631a6655fc5918ceed72d3))

* minor: line endings converted to UNIX style ([`45d3535`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/45d353595dcbfdc864a02225475532c4d7825d22))

* reBin: removed unnecessary whitespace ([`65e622b`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/65e622bae6f73eef4f4d3f946ec038c33e97d50c))

* reBin: show help when called without arguments or files ([`1c8244c`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/1c8244cbfbbfd1373254069bb04062f3e6baeee0))

* reBin: fixed python3 compat. ([`05468c0`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/05468c0784d33fc8e8ecea686f06d0216e7f7aa7))

* disabled nbstripout checks ([`8835ff0`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/8835ff05cf91c42c470c7f572da8af179a9b8866))

* license added ([`10bb685`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/10bb68573b9b2dd66370bd8bf277d0aa9e354724))

* git: check if installed at all ([`80e7328`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/80e73289d376d18ca7ae135e4ae3d0249a724bf2))

* handle exception if git submodule is moved out of parent repository ([`fb382bd`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/fb382bd3508c8c35aa796b89e765220280cec6c1))

* added showBoolStatus() to pretty print the value of a boolean variable ([`b00316c`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/b00316c60cd5036750104961e7c10337df5a451a))

* added PathSelector in *widgets* module ([`189b56e`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/189b56e1a0af30876013bf676577c2bd4d9e1183))

* git: using full python path for running nbstripout during checkRepo ([`1fbe3cc`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/1fbe3cc93f778f69dc34e569fc54d0906268357a))

* set git status text always transparent ([`9e5943f`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/9e5943fac800ff3385cc2ebb058d3c95608533a0))

* git: partial transparent git status if repo is clean ([`b2fc0e9`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/b2fc0e9e1020c1fcd36cb2a35ab3edd6cc50feb3))

* fixed git module: using subprocess instead of ipython syntax '!' ([`95e7851`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/95e78510aaba7ceeab4515b226f8aad486140424))

* functions for git repo status added ([`4c1f620`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/4c1f6201707e3bb5591614eae102b8e63abf4972))

* fixed encoding header info ([`8375642`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/83756420fab8f3851ce881f54744a2caba20e19d))

* use proper boolean operator ([`94fc592`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/94fc59229261b4acf8e6f32027a4649f133291ad))

* diff.textconv and filters for IPYNB and XLS files ([`ec97ca4`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/ec97ca423a0353c0d82c4c77b141f3a14602e8c8))

* added pycache to gitignore ([`7650b60`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/7650b60079190303a1570caaa3c8016ecd74dd92))

* fixed module path ([`e7f866a`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/e7f866a13044a5b064f3b94bfa8cb15159ea9af3))

* removed Jupyter startup scripts, not needed here ([`c0e07b0`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/c0e07b0675efe51dff549f7526371947b76e8bff))

* init file to make up a proper python module ([`7b984da`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/7b984da192d03a586941374755514f5b11515bf2))

* small-angle scattering data rebinning routine by Brian Pauw ([`eae62d8`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/eae62d8f317b19d3b3022ba6285df0df4ecd1f9b))

* code for parsing a PDH file ([`af59678`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/af59678ff824dfade45b8c18b83ee390b1f14413))

* Jupyter shortcuts added ([`85a8b9b`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/85a8b9b6c85065fa1d4491efbf479973e4c8e238))

* Initial Commit ([`645ef06`](https://github.com/BAMresearch/jupyter-analysis-tools/commit/645ef06938f90d3219c17f74c23d9e610c5a1753))
