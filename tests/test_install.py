"""Exercise installation only inside isolated temporary directories."""
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import release


class InstallerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.archive = release.build()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="fangdatong-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.unpack = self.root / "分享包 with spaces"
        with zipfile.ZipFile(self.archive) as archive:
            archive.extractall(self.unpack)
        self.package = self.unpack / "fangdatong-codex-pets"
        self.target = self.root / "Codex 数据" / "pets"

    def install(self, *args):
        return subprocess.run(
            ["/bin/bash", str(self.package / "安装到Codex.command"), "--pet-dir", str(self.target), *args],
            cwd=self.root, text=True, capture_output=True,
        )

    def assert_installed(self):
        for pet in release.PET_IDS:
            for name in ("pet.json", "spritesheet.webp"):
                self.assertEqual(release.digest(self.target / pet / name), release.digest(self.package / pet / name))

    def test_fresh_install_preserves_other_pets(self):
        other = self.target / "existing-pet" / "keep.txt"
        other.parent.mkdir(parents=True)
        other.write_text("keep this pet")
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assert_installed()
        self.assertEqual(other.read_text(), "keep this pet")

    def test_reinstall_backs_up_same_name(self):
        old = self.target / release.PET_IDS[0]
        old.mkdir(parents=True)
        (old / "pet.json").write_text('{"old":"configuration"}')
        (old / "custom-note.txt").write_text("personal note")
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        backups = list((self.package / "安装前备份").glob(f"backup.*/{release.PET_IDS[0]}"))
        self.assertEqual(len(backups), 1)
        self.assertEqual((backups[0] / "pet.json").read_text(), '{"old":"configuration"}')
        self.assertEqual((backups[0] / "custom-note.txt").read_text(), "personal note")
        self.assert_installed()

    def test_changed_payload_stops_before_installing(self):
        with (self.package / release.PET_IDS[0] / "spritesheet.webp").open("ab") as file:
            file.write(b"damaged")
        self.assertNotEqual(self.install().returncode, 0)
        self.assertFalse(self.target.exists())

    def test_missing_asset_stops_before_installing(self):
        (self.package / release.PET_IDS[1] / "pet.json").unlink()
        self.assertNotEqual(self.install().returncode, 0)
        self.assertFalse(self.target.exists())

    def test_verify_only_does_not_install(self):
        result = self.install("--verify-only")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(self.target.exists())

    def test_download_zip_contains_exact_payload_and_executable_installer(self):
        with zipfile.ZipFile(self.archive) as archive:
            expected = {f"fangdatong-codex-pets/{p}" for p in release.PAYLOAD + ["SHA256SUMS"]}
            self.assertEqual(set(archive.namelist()), expected)
            info = archive.getinfo("fangdatong-codex-pets/安装到Codex.command")
            self.assertEqual((info.external_attr >> 16) & 0o777, 0o755)
        self.assertTrue(release.verify(self.package)["ok"])


if __name__ == "__main__":
    unittest.main()
