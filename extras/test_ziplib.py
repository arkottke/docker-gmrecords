import ziplib
# cloudburst framework - Bruce Hearn 2021 bruce.hearn@gmail.com
# tests ziplib. These are manual tests, i.e. no conditions are checked, but results must
# be observed. In future we will use a known test data set and add verification code

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.joinpath("scripts")))

ziplib.compress('/tmp/logz.7z', 'logs/*')
ziplib.expand('/tmp/logz.7z', 'logs/x/')

