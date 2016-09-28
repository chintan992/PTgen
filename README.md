# PTgen

Create and evaluate probabilistic transcriptions (PT's) of speech recordings
generated by *mismatched crowdsourcing:* by many people
who don't speak the recordings' language.

The technique is described in this [ICASSP paper](http://www.isle.illinois.edu/sst/pubs/2016/liu16icassp.pdf),
this [AAAI paper](http://www.ifp.illinois.edu/~pjyothi/files/AAAI2015.pdf),
and without jargon in this [Technograph article](Technograph.md).
<!-- (http://dailyillini.com/special-sections/2016/04/10/researchers-developing-an-automatic-speech-recognition-software-for-under-resourced-languages/) -->

# How to build on Ubuntu

Install [OpenFST](http://www.openfst.org/), [Carmel](http://www.isi.edu/licensed-sw/carmel), and at least the `compute-wer` executable of [Kaldi](https://github.com/kaldi-asr/kaldi).

```
git clone https://github.com/ws15code/PTgen
cd src
make
```

The first time you `make`, you'll be asked to enter the directory of OpenFST's file `fst/compat.h`.
This is usually `/usr/local/include`.  If that fails, `rm config.mk; make`, and instead try a result from the command `locate fst/compat.h`.

# How to create and evaluate PT's

Edit the settings file, e.g. `test/ws15/settings_full`.
- Ensure that the required files within that file's `$DATA` exist,
or can be downloaded from that file's `$DATA_URL`.

`run.sh settings_full`

If `run.sh` can't find the executable programs of OpenFST, Carmel, or Kaldi, it prompts you for their locations,
and caches your answers in a new file `config.sh`, for future runs.

If you encounter errors and fix them, you can save time by starting `run.sh` partway through:
in your settings file, set `startstage` to one past the last successfully completed stage.

# How to run prebuilt tests

`cd test/ws15` (or any other test directory).

`../../run.sh settings-foo`

The settings file in each of these tests includes
a `$DATA_URL` for downloading the test's data,
which is too unwieldy to store on github.

If `../../run.sh` prompts you again for the locations of exes, you can just abort it with `ctrl+C`, retrieve those settings with `cp ../../config.sh .`, and retry.
