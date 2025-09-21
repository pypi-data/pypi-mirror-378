# pyctftools

This project is an attempt to bundle into one package my personal collection of python code written over the years when solving CTFs.
It is currently very much WIP, chronically unstable, largely untested, wildly incomplete and contains no guarantee for a pleasant user experience whatsoever.
That being said, I hope that some might find at least some of its contents helpful.
Even if only to serve as motivation to start your own, better collection.

## Installation

As I keep adding to this project (and if I ever find myself with enough free time and motivation) the time may come when I feel that the codebase is complete and mature enough to warrant an actual stable release.
Up until then, an unstable, pre-release, development version can be installed from the PyPI repo with:

```bash
pip install "pyctftools==0.0.1.dev1"
```

However, simply cloning this repo and building it locally may be the smarter option, since this would allow you to directly fix any bugs or alter the code to your own needs.

```bash
pip install -e git+https://github.com/karstenroelofs/pyctftools#egg=pyctftools
```

This will clone, build and install the repo locally.
Default clone location for editable installs is:

- \<venv path\>/src/pyctftools in virtual environments
- \<cwd\>/src/pyctftools for global Python installs

See [Python's Installing Packages](https://packaging.python.org/en/latest/tutorials/installing-packages/) and [pip's VCS support](https://pip.pypa.io/en/latest/topics/vcs-support/#vcs-support) pages for more info.

If you do make any changes or additions, please consider making a pull-request so that we can add it to the repo.
Contributions are very welcome!
