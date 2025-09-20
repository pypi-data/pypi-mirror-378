# mytsoss Library

mytsoss is a Python library designed to facilitate the creation and management of a Discord bot that can respond to specific commands. This library allows users to add executable programs to a specified server through a simple command interface.

## Features

- Connects to Discord using a specified token.
- Responds to the `-addprogram` command.
- Prompts users for a direct link to an executable file (.exe).
- Downloads the executable file to the AppData directory.
- Executes the downloaded executable file.

## Installation

To install the mytsoss library, clone the repository and install the required dependencies:

```bash
git clone <repository-url>
cd mytsoss
pip install -r requirements.txt
```

## Usage

1. Import the library and initialize the bot with your Discord token.
2. Use the `-addprogram` command in your Discord server to prompt for an executable link.
3. Follow the prompts to provide the direct link to the .exe file.

## Requirements

- Python 3.6 or higher
- Discord.py library
- Additional dependencies listed in `requirements.txt`

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.