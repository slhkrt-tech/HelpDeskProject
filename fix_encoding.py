from pathlib import Path
files=['.gitignore','requirements.txt']
for f in files:
    p=Path(f)
    if not p.exists():
        print(f'SKIP missing: {f}')
        continue
    data=None
    # try utf-8
    try:
        data=p.read_text(encoding='utf-8')
        print(f'{f}: read as utf-8')
    except Exception as e:
        try:
            data=p.read_text(encoding='utf-16')
            print(f'{f}: read as utf-16')
        except Exception as e2:
            try:
                data=p.read_text(encoding='utf-16-le')
                print(f'{f}: read as utf-16-le')
            except Exception as e3:
                try:
                    data=p.read_text(encoding='latin-1')
                    print(f'{f}: read as latin-1')
                except Exception as e4:
                    print(f'{f}: failed to read with common encodings')
                    continue
    # normalize line endings and write utf-8
    data = data.replace('\r\n','\n')
    p.write_text(data,encoding='utf-8')
    print(f'{f}: written as utf-8')
