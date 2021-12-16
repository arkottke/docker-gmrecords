import ziplib

ziplib.compress('/tmp/logz.7z', 'logs/*')
ziplib.expand('/tmp/logz.7z', 'logs/x/')

