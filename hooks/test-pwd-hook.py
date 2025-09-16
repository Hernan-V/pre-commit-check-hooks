#!/usr/bin/env python3

import os
import sys

def main():
    print("=== PWD Test Hook ===", file=sys.stderr)
    print(f"Directorio actual (os.getcwd()): {os.getcwd()}", file=sys.stderr)
    print(f"PWD desde variable de entorno: {os.environ.get('PWD', 'No disponible')}", file=sys.stderr)
    print(f"Argumentos recibidos: {sys.argv[1:]}", file=sys.stderr)
    print(f"Archivos pasados como argumentos:", file=sys.stderr)

    for arg in sys.argv[1:]:
        if os.path.isfile(arg):
            abs_path = os.path.abspath(arg)
            print(f"  - {arg} -> {abs_path}", file=sys.stderr)
            print(f"    Directorio del archivo: {os.path.dirname(abs_path)}", file=sys.stderr)
        else:
            print(f"  - {arg} (no es un archivo)", file=sys.stderr)

    # También mostrar algunas variables de entorno relevantes
    print("Variables de entorno relevantes:", file=sys.stderr)
    for env_var in ['GIT_DIR', 'GIT_WORK_TREE', 'PRE_COMMIT_HOME']:
        value = os.environ.get(env_var)
        if value:
            print(f"  {env_var}: {value}", file=sys.stderr)

    return 0

if __name__ == "__main__":
    sys.exit(main())