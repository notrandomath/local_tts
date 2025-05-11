# Local TTS App
## Installation Guide
Clone the repo
```bash
git clone git@github.com:notrandomath/local_tts.git
```
Create the environment (to install conda see [here](https://www.anaconda.com/docs/getting-started/miniconda/install#quickstart-install-instructions))
```bash
conda create -n local_tts python=3.9
conda activate local_tts
pip install -r requirements.txt
```
Run the app
```bash
python main.py
```
For better speed effects:
- `brew install rubberband` (mac)
- `sudo apt install rubberband-cli` (linux)
