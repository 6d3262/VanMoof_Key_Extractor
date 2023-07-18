# VanMoof Key Extractor

This Python script queries the Vanmoof API to retrieve details about your bike. It can also parse a local JSON file containing the bike details.

The script fetches the following details:
- Bike Type
- Frame Number
- MAC Address
- Encryption Key
- Passcode

All the data is also saved to a JSON file named `VanMoof_{bike_type}_{frame_number}.json` in your Downloads directory.

## Usage

There are two ways to use this script:

1. Query the Vanmoof API:

    ```sh
    python3 VanMoof_key_extractor.py -u username@example.com -p yourpassword
    ```

    If the `-u` (username) or `-p` (password) argument is omitted, the script will prompt you for the missing information.

2. Parse a local JSON file:

    ```sh
    python3 VanMoof_key_extractor.py -j /path/to/your/file.json
    ```


After running the script, you will see the bike details printed in your terminal.

## Dependencies

You will need the following Python packages to run this script:

- `requests`
- `json`
- `logging`
- `argparse`
- `getpass`
- `base64`
- `os`

You can install these packages using pip:

```sh
pip install requests
```

## Contributing

Contributions are welcome. Please open an issue or submit a pull request if you have any improvements or suggestions.

## License

This project is licensed under the MIT License
