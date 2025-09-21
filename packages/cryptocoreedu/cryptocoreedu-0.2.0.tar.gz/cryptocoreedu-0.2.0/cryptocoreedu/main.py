# from cryptocoreedu.modes.ECBMode import ECBMode
from .modes.ECBMode import ECBMode
from pathlib import Path
import argparse

def main():

    parser = argparse.ArgumentParser(description='Crypto Tool')
    parser.add_argument('--algorithm', '-alg', choices=['aes'], required=True, help='Algorithm')
    parser.add_argument('--mode', '-m', choices=['ecb'], required=True, help='Mode')

    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--encrypt', '-enc', action='store_true',
                            help='Encrypt mode')
    mode_group.add_argument('--decrypt', '-dec', action='store_true',
                            help='Decrypt mode')

    parser.add_argument('--key', '-k', required=True, help='Encryption key')
    parser.add_argument('--input', '-i', type=Path, required=True, help='Input file path')
    parser.add_argument('--output', '-o', type=Path, required=True, help='Output file path')

    args = parser.parse_args()

    try:
        # Создаем шифратор
        if args.algorithm == 'aes' and args.mode == 'ecb':
            cipher = ECBMode(args.key.encode())

            if args.encrypt:
                cipher.encrypt_file(args.input, args.output)
                print(f"File encrypted: {args.input} -> {args.output}")
            else:
                cipher.decrypt_file(args.input, args.output)
                print(f"File decrypted: {args.input} -> {args.output}")

    except Exception as error:
        parser.error(f'Operation failed: {error}')

if __name__ == "__main__":
    main()