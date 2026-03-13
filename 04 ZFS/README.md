# ZFS — Betriebssysteme Übungsblatt 3

Uni Trier · Prof. Sturm · Winter 2025

## Voraussetzungen

- Ubuntu 24.04 VM (KVM)
- ZFS installiert (`zfs-2.2.2` / `zfs-kmod-2.3.4`)
- Root-Rechte (`sudo`)

## Ausführung

### 1. Virtuelle Disks erstellen

```bash
sudo bash shell/disks-up.sh
```

Erstellt 4 × 500 MB Sparse-Image-Dateien unter `/2025WEdition/`.

### 2. Aufgaben ausführen

```bash
sudo python3 aufgabe1.py   # Backup-Tool mit ZFS Snapshots & Retention
sudo python3 aufgabe2.py   # Datei-Inkonsistenzen trotz ZFS Snapshots
sudo python3 aufgabe3.py   # RAIDZ — Disk-Ausfall ohne Datenverlust
sudo python3 aufgabe4.py   # Benchmark ZFS vs ext4
```

> **Hinweis:** `aufgabe1.py` läuft in einer Endlosschleife — mit `Ctrl+C` beenden.

### 3. Aufräumen

```bash
sudo bash shell/disks-down.sh
```

Entfernt alle ZFS Pools, Loop-Devices, Image-Dateien und das `/2025WEdition/`-Verzeichnis.

## Projektstruktur

```
.
├── aufgabe1.py          # Backup-Tool (ZFS send/receive, Retention Policy)
├── aufgabe2.py          # Inkonsistenz-Experiment (Writer-Thread + Snapshot)
├── aufgabe3.py          # RAIDZ-Demo (Disk-Ausfall + Worker-Thread)
├── aufgabe4.py          # Benchmark ZFS vs ext4
├── config/
│   └── backup.yaml      # Backup-Konfiguration (Dataset, Ziel, Retention)
├── lib/
│   ├── ShellCommander.py
│   ├── ZFSDisk.py
│   ├── ZFSPool.py
│   ├── ZFSDataset.py
│   ├── ZFSSnapshot.py
│   ├── BackupManager.py
│   ├── Ext4Disk.py
│   └── Ext4Mount.py
├── shell/
│   ├── disks-up.sh      # Virtuelle Disks erstellen
│   └── disks-down.sh    # Virtuelle Disks entfernen
└── tests/
    ├── BenchmarkTest.py
    ├── SequentialWriteTest.py
    ├── SequentialReadTest.py
    ├── RandomWriteTest.py
    ├── RandomReadTest.py
    └── SmallFilesTest.py
```