import os
import platform
import sys
import zipfile
import hashlib
import struct
import subprocess

import update_metadata_pb2

BRILLO_MAJOR_PAYLOAD_VERSION = 2
BLOCK_SIZE = 4096
PROGRAMS = ["bzcat", "xzcat"]


class PayloadError(Exception):
    pass


class Payload:
    class _PayloadHeader:
        _MAGIC = b"CrAU"

        def __init__(self):
            self.version = None
            self.manifest_len = None
            self.metadata_signature_len = None
            self.size = None

        def ReadFromPayload(self, payload_file):
            magic = payload_file.read(4)
            if magic != self._MAGIC:
                raise PayloadError("Invalid payload magic: %s" % magic)
            self.version = struct.unpack(">Q", payload_file.read(8))[0]
            self.manifest_len = struct.unpack(">Q", payload_file.read(8))[0]
            self.size = 20
            self.metadata_signature_len = 0
            if self.version != BRILLO_MAJOR_PAYLOAD_VERSION:
                raise PayloadError("Unsupported payload version (%d)" % self.version)
            self.size += 4
            self.metadata_signature_len = struct.unpack(">I", payload_file.read(4))[0]

    def __init__(self, payload_file):
        self.payload_file = payload_file
        self.header = None
        self.manifest = None
        self.data_offset = None
        self.metadata_signature = None
        self.metadata_size = None

    def _ReadManifest(self):
        return self.payload_file.read(self.header.manifest_len)

    def _ReadMetadataSignature(self):
        self.payload_file.seek(self.header.size + self.header.manifest_len)
        return self.payload_file.read(self.header.metadata_signature_len)

    def ReadDataBlob(self, offset, length):
        self.payload_file.seek(self.data_offset + offset)
        return self.payload_file.read(length)

    def Init(self):
        self.header = self._PayloadHeader()
        self.header.ReadFromPayload(self.payload_file)
        manifest_raw = self._ReadManifest()
        self.manifest = update_metadata_pb2.DeltaArchiveManifest()
        self.manifest.ParseFromString(manifest_raw)
        metadata_signature_raw = self._ReadMetadataSignature()
        if metadata_signature_raw:
            self.metadata_signature = update_metadata_pb2.Signatures()
            self.metadata_signature.ParseFromString(metadata_signature_raw)
        self.metadata_size = self.header.size + self.header.manifest_len
        self.data_offset = self.metadata_size + self.header.metadata_signature_len


def decompress_payload(command, data, size, hash):
    """Декомпрессия данных / Decompress data"""

    system = platform.system()

    if command == "xzcat":
        if system == "Darwin":
            command = ["tar", "-xf", "-"]
        else:
            command = ["tar", "-xJf", "-"]

    elif command == "bzcat":
        if system == "Windows":
            command = ["tar", "-xjf", "-"]
        else:
            command = "bzcat"

    p = subprocess.Popen([command, "-"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    r = p.communicate(data)[0]
    if len(r) != size:
        print("Unexpected size %d %d" % (len(r), size))
    elif hashlib.sha256(data).digest() != hash:
        print("Hash mismatch")
    return r


def parse_payload(payload_f, partition, out_f, progress_callback, log_message, lang):
    """Разбирает payload и обновляет прогресс / Parses payload and updates progress"""
    total_operations = len(partition.operations)
    # log_message(lang["log_processing_partition"].format(partition=partition.partition_name))

    for i, operation in enumerate(partition.operations):
        e = operation.dst_extents[0]
        data = payload_f.ReadDataBlob(operation.data_offset, operation.data_length)
        out_f.seek(e.start_block * BLOCK_SIZE)

        # log_message(f"Processing operation {i + 1}/{total_operations}")

        if operation.type == update_metadata_pb2.InstallOperation.REPLACE:
            out_f.write(data)
        elif operation.type == update_metadata_pb2.InstallOperation.REPLACE_XZ:
            # log_message("Decompressing XZ data...")
            r = decompress_payload(
                "xzcat", data, e.num_blocks * BLOCK_SIZE, operation.data_sha256_hash
            )
            out_f.write(r)
        elif operation.type == update_metadata_pb2.InstallOperation.REPLACE_BZ:
            # log_message("Decompressing BZ2 data...")
            r = decompress_payload(
                "bzcat", data, e.num_blocks * BLOCK_SIZE, operation.data_sha256_hash
            )
            out_f.write(r)
        elif operation.type == update_metadata_pb2.InstallOperation.ZERO:
            # log_message("Writing zeroed blocks...")
            out_f.write(b"\x00" * (e.num_blocks * BLOCK_SIZE))
        else:
            log_message(
                lang["log_extraction_failed"].format(
                    error=f"Unhandled operation type ({operation.type})"
                )
            )
            raise PayloadError(f"Unhandled operation type ({operation.type})")

        progress_callback(i / total_operations)  # Обновляем прогресс / Update progress


def extract_ota(filename, output_dir, progress_callback, log_message, lang):
    """Функция для обработки OTA-файла с прогресс-баром
    Function for processing an OTA file with a progress bar"""

    os.makedirs(output_dir, exist_ok=True)
    log_message(lang["log_creating_output_dir"].format(dir=output_dir))

    if filename.endswith(".zip"):
        ota_zf = zipfile.ZipFile(filename)
        log_message(lang["log_extracting"].format(file=filename, folder=output_dir))
        payload_file = open(ota_zf.extract("payload.bin", output_dir), "rb")
    else:
        log_message(lang["log_opening_payload"])
        payload_file = open(filename, "rb")

    payload = Payload(payload_file)
    payload.Init()
    log_message("Payload initialized.")

    for p in payload.manifest.partitions:
        name = p.partition_name + ".img"
        fname = os.path.join(output_dir, name)
        log_message(lang["log_processing_partition"].format(partition=p.partition_name))
        with open(fname, "wb") as out_f:
            try:
                parse_payload(payload, p, out_f, progress_callback, log_message, lang)
            except PayloadError as e:
                log_message(lang["log_extraction_failed"].format(error=str(e)))
                os.unlink(fname)
