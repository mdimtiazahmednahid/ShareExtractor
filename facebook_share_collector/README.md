# Facebook Share Collector

A robust, production-quality Python automation application to collect publicly visible profiles/pages from Facebook's "Shares" list using an Android device, Appium 2, and UiAutomator2, all managed via a PySide6 GUI.

## Prerequisites
- **Python 3.12+**
- **Android Device** connected via USB with Developer Options and **USB Debugging** enabled.
- **Node.js** (for installing Appium 2)
- **ADB (Android Debug Bridge)** installed and added to your system PATH.

## Environment Setup

### 1. Install Appium 2 and UiAutomator2 Driver
```bash
npm install -g appium
appium driver install uiautomator2
```

### 2. Set Up Python Virtual Environment
**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Start Appium Server
Open a separate terminal and run:
```bash
appium
```

### 5. Verify Connected Device
Run `adb devices` in the terminal to verify your Android device is listed and marked as `device` (not `unauthorized`).

## Running the Application
```bash
python run.py
```

## Workflow
1. Connect your Android phone to the computer.
2. Ensure the Appium server is running.
3. Launch the application (`python run.py`).
4. Manually open Facebook on your phone and navigate to the desired post's "Shares" list.
5. In the application GUI, click **Inspect UI** to verify the UI hierarchy and then **Start Collection** to begin collecting profiles.
6. Once completed or stopped, you can export the collected data to CSV, JSON, or XLSX.

## Limitations & Privacy
- This application does **NOT** bypass Facebook privacy settings.
- It will only collect publicly/visibly exposed information from the Share list.
- It operates strictly via UI automation, interacting only with what is visible on the screen.
