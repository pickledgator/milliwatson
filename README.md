# milliwatson
The newest pint-sized trivia super star

# To set up:
Linux:
```bash
sudo apt-get install tesseract -y
pip3 install -r requirements.txt
```

MacOS:
```bash
brew install tesseract
pip3 install -r requirements.txt
```

# Running
* Connect iPhone to mac via USB
* Open Quicktime, select File->New Movie Recording
* Down arrow next to record button, select Camera: iPhone
* Left snap quick time window to left side of desktop
* Run script: ```python3 ./milliwatson.py```
* Use ```c``` to capture

TODO:
  * Implement a video stream method
    * screencap polling method?
  * Auto detect the question screen
  * Better text detection via thresholding
