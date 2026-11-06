import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

class BatchInstaller(unittest.TestCase):
    @unittest.skipUnless(os.name == 'nt', 'requires Windows cmd.exe')
    def test_batch_installer_downloads_local_archive_and_passes_arguments(self):
        import shutil
        import sys
        import zipfile
        with tempfile.TemporaryDirectory(prefix='vivarc batch ') as temporary:
            root = Path(temporary)
            batch = root / 'installer & files' / 'install.bat'
            batch.parent.mkdir()
            shutil.copy2(Path(__file__).parents[1] / 'install.bat', batch)
            archive = root / 'release.zip'
            with zipfile.ZipFile(archive, 'w') as package:
                package.writestr('release/vivarc.py', 'import json,sys; from pathlib import Path; Path(__file__).with_name("called.json").write_text(json.dumps(sys.argv[1:]))')
                package.writestr('release/install.ps1', '')
                package.writestr('release/install.bat', batch.read_text(encoding='utf8'))
            home = root / 'user home'
            env = {**os.environ, 'USERPROFILE': str(home), 'VIVARC_PYTHON': sys.executable, 'VIVARC_ZIP_URL': archive.as_uri()}
            comspec = os.environ.get('COMSPEC', 'cmd.exe')
            command = f'"{comspec}" /d /s /c ""{batch}" --no-peek"'
            result = subprocess.run(command, env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads((home / '.vivarc/app/called.json').read_text()), ['install', '--no-peek'])
            self.assertTrue((home / '.vivarc/app/install.bat').is_file())
