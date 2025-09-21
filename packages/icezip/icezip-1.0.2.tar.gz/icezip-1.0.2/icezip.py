#!/usr/bin/env python3
import zipfile, argparse, json, io, sys
from pathlib import Path

class ICEZip:
    MAGIC = b'ICEZIP'
    VERSION = 1

    def __init__(self, path):
        self.path = Path(path)

    def create(self, files_dict, manifest=None):
        buf = io.BytesIO()
        if manifest is None:
            manifest = {"files": list(files_dict.keys())}
        files_dict['manifest.json'] = json.dumps(manifest).encode('utf-8')
        with zipfile.ZipFile(buf, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            for fname, data in files_dict.items():
                zf.writestr(fname, data)
        with open(self.path, 'wb') as f:
            f.write(self.MAGIC)
            f.write(bytes([self.VERSION]))
            f.write(buf.getvalue())

    def read(self):
        with open(self.path, 'rb') as f:
            header = f.read(len(self.MAGIC))
            if header != self.MAGIC:
                raise ValueError("Not a valid ICEZIP file")
            version = f.read(1)[0]
            buf = f.read()
        with zipfile.ZipFile(io.BytesIO(buf)) as zf:
            return {name: zf.read(name) for name in zf.namelist()}

    def list_files(self):
        data = self.read()
        return list(data.keys())

    def extract_all(self, output_dir):
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        data = self.read()
        for name, content in data.items():
            if name == "manifest.json":
                continue
            out_path = output_dir / name
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with open(out_path, 'wb') as f:
                f.write(content)

    def add_files(self, files_dict):
        current = self.read()
        manifest = json.loads(current.get('manifest.json', b'{}').decode())
        for fname, data in files_dict.items():
            current[fname] = data
            manifest.setdefault("files",[]).append(fname)
        self.create(current, manifest)

    def remove_files(self, file_list):
        current = self.read()
        manifest = json.loads(current.get('manifest.json', b'{}').decode())
        for fname in file_list:
            current.pop(fname, None)
            if "files" in manifest and fname in manifest["files"]:
                manifest["files"].remove(fname)
        self.create(current, manifest)

def main():
    parser = argparse.ArgumentParser(description="ICEZIP Advanced Tool")
    sp = parser.add_subparsers(dest="cmd")

    c = sp.add_parser("create")
    c.add_argument("file")
    c.add_argument("src", nargs="+")
    r = sp.add_parser("read")
    r.add_argument("file")
    l = sp.add_parser("list")
    l.add_argument("file")
    e = sp.add_parser("extract")
    e.add_argument("file")
    e.add_argument("out")
    a = sp.add_parser("add")
    a.add_argument("file")
    a.add_argument("src", nargs="+")
    rm = sp.add_parser("remove")
    rm.add_argument("file")
    rm.add_argument("names", nargs="+")

    args = parser.parse_args()
    ice = ICEZip(args.file)

    if args.cmd == "create":
        files = {Path(f).name: Path(f).read_bytes() for f in args.src if Path(f).is_file()}
        ice.create(files)
    elif args.cmd == "read":
        data = ice.read()
        for n, content in data.items():
            if n != "manifest.json":
                sys.stdout.buffer.write(b"===%s===\n"%n.encode())
                sys.stdout.buffer.write(content+b"\n")
    elif args.cmd == "list":
        files = ice.list_files()
        for f in files:
            print(f)
    elif args.cmd == "extract":
        ice.extract_all(args.out)
    elif args.cmd == "add":
        files = {Path(f).name: Path(f).read_bytes() for f in args.src if Path(f).is_file()}
        ice.add_files(files)
    elif args.cmd == "remove":
        ice.remove_files(args.names)

if __name__ == "__main__":
    main()
