# milliwatson
The newest pint-sized HQTrivia super star

## Issue Tracking / Feature Requests
<a href="https://waffle.io/pickledgator/milliwatson" target="_blank">https://waffle.io/pickledgator/milliwatson</a>

## Setup
Linux:
* Install bazel (https://docs.bazel.build/versions/master/install-ubuntu.html)
```bash
pip3 install virtualenv
virtualenv -p python3 env
source env/bin/activate
sudo apt-get install tesseract -y
bazel build milliwatson
```

MacOS:
```bash
brew install tesseract bazel
pip3 install virtualenv
virtualenv -p python3 env
source env/bin/activate
bazel build milliwatson
```

## Running
* Connect iPhone to mac via USB
* Open Quicktime, select File->New Movie Recording
* Down arrow next to record button, select Camera: iPhone
* Left snap quick time window to left side of desktop
* Run:
  * Linux: ```./bazel-out/k8-py3-fastbuild/bin/milliwatson/milliwatson```
  * Mac: ```./bazel-out/darwin-py3-fastbuild/bin/milliwatson/milliwatson```
* Use ```c``` to capture

## TODO:
  * Implement a video stream method
    * screencap polling method?
  * Auto detect the question screen
  * Better text detection via thresholding

## Troubleshooting
### Xcode version must be specified to use an Apple CROSSTOOL
```shell
bazel clean --expunge
sudo xcode-select -s /Applications/Xcode.app/Contents/Developer
sudo xcodebuild -license
bazel clean --expunge
```
