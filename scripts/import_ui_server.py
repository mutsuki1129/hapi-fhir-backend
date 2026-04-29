import argparse
import base64
import csv
import json
import os
import re
import socket
import subprocess
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _safe_json_loads(text: str):
    try:
        return json.loads(text)
    except Exception:
        return None


def _parse_fhir_error_legacy(raw_text: str, status_code: int):
    obj = _safe_json_loads(raw_text or "")
    issue = None
    if isinstance(obj, dict):
        issues = obj.get("issue")
        if isinstance(issues, list) and issues:
            issue = issues[0]

    diagnostics = ""
    issue_code = ""
    if isinstance(issue, dict):
        diagnostics = str(issue.get("diagnostics", "") or "")
        issue_code = str(issue.get("code", "") or "")

    message = diagnostics or "FHIR operation failed."
    code = "UNKNOWN_ERROR"

    if status_code == 401:
        code = "UNAUTHORIZED"
        message = "未授權，請先登入或提供有效 Token。"
    elif status_code == 403:
        code = "FORBIDDEN"
        message = "沒有權限存取此資源。"
    elif status_code == 404:
        if "Patient/" in diagnostics:
            code = "PATIENT_NOT_FOUND"
            message = "找不到指定病患資料。"
        else:
            code = "RESOURCE_NOT_FOUND"
            message = "找不到指定資源。"
    elif status_code == 400:
        if issue_code in ("invalid", "structure", "value", "processing"):
            code = "VALIDATION_ERROR"
            message = "資料格式或欄位驗證失敗。"
        else:
            code = "BAD_REQUEST"
            message = "請求格式錯誤。"
    elif status_code >= 500:
        code = "SERVER_ERROR"
        message = "後端服務錯誤，請稍後再試。"

    # HAPI specific not-found style
    if "HAPI-2001" in diagnostics and "not known" in diagnostics:
        if "Patient/" in diagnostics:
            code = "PATIENT_NOT_FOUND"
            message = "找不到指定病患資料。"
        else:
            code = "RESOURCE_NOT_FOUND"
            message = "找不到指定資源。"

    return {
        "code": code,
        "message": message,
        "httpStatus": status_code,
        "fhirIssueCode": issue_code or None,
        "diagnostics": diagnostics or None,
        "rawOperationOutcome": obj,
    }


def _fhir_request_legacy(method: str, url: str, data=None, token: str = ""):
    headers = {
        "Accept": "application/fhir+json",
    }
    if data is not None:
        headers["Content-Type"] = "application/fhir+json"
    if token:
        headers["Authorization"] = f"Bearer {token}"

    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")

    req = urllib.request.Request(url=url, method=method, headers=headers, data=body)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            parsed = _safe_json_loads(raw)
            return resp.status, parsed if parsed is not None else raw
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        return e.code, raw
    except Exception as e:
        return 0, str(e)


def _parse_fhir_error(raw_text: str, status_code: int):
    obj = _safe_json_loads(raw_text or "")
    issue = None
    if isinstance(obj, dict):
        issues = obj.get("issue")
        if isinstance(issues, list) and issues:
            issue = issues[0]

    diagnostics = ""
    issue_code = ""
    if isinstance(issue, dict):
        diagnostics = str(issue.get("diagnostics", "") or "")
        issue_code = str(issue.get("code", "") or "")

    raw_message = str(raw_text or "")
    message = diagnostics or "FHIR operation failed."
    code = "UNKNOWN_ERROR"

    if status_code == 0:
        lower = raw_message.lower()
        if "timed out" in lower or "timeout" in lower:
            code = "TIMEOUT"
            message = "FHIR request timed out. Please try again."
            status_code = 504
        else:
            code = "NETWORK_ERROR"
            message = "FHIR server is unreachable. Please check the backend connection."
            status_code = 503
    elif status_code == 401:
        code = "UNAUTHORIZED"
        message = "Authentication is required. Please sign in again."
    elif status_code == 403:
        code = "FORBIDDEN"
        message = "You do not have permission to perform this action."
    elif status_code == 404:
        if "Patient/" in diagnostics:
            code = "PATIENT_NOT_FOUND"
            message = "Patient was not found."
        elif "Observation/" in diagnostics:
            code = "OBSERVATION_NOT_FOUND"
            message = "Observation was not found."
        elif "Condition/" in diagnostics:
            code = "CONDITION_NOT_FOUND"
            message = "Condition was not found."
        elif "Media/" in diagnostics:
            code = "MEDIA_NOT_FOUND"
            message = "Media was not found."
        elif "DocumentReference/" in diagnostics:
            code = "DOCUMENTREFERENCE_NOT_FOUND"
            message = "DocumentReference was not found."
        elif "Practitioner/" in diagnostics:
            code = "PRACTITIONER_NOT_FOUND"
            message = "Practitioner was not found."
        else:
            code = "RESOURCE_NOT_FOUND"
            message = "Requested resource was not found."
    elif status_code == 400:
        if issue_code in ("invalid", "structure", "value", "processing"):
            code = "VALIDATION_ERROR"
            message = "Submitted data is invalid. Please review the request."
        else:
            code = "BAD_REQUEST"
            message = "Request could not be processed."
    elif status_code >= 500:
        code = "SERVER_ERROR"
        message = "Server error. Please try again later."

    if "HAPI-2001" in diagnostics and "not known" in diagnostics:
        if "Patient/" in diagnostics:
            code = "PATIENT_NOT_FOUND"
            message = "Patient was not found."
        elif "Observation/" in diagnostics:
            code = "OBSERVATION_NOT_FOUND"
            message = "Observation was not found."
        elif "Condition/" in diagnostics:
            code = "CONDITION_NOT_FOUND"
            message = "Condition was not found."
        elif "Media/" in diagnostics:
            code = "MEDIA_NOT_FOUND"
            message = "Media was not found."
        elif "DocumentReference/" in diagnostics:
            code = "DOCUMENTREFERENCE_NOT_FOUND"
            message = "DocumentReference was not found."
        elif "Practitioner/" in diagnostics:
            code = "PRACTITIONER_NOT_FOUND"
            message = "Practitioner was not found."
        else:
            code = "RESOURCE_NOT_FOUND"
            message = "Requested resource was not found."

    return {
        "code": code,
        "message": message,
        "httpStatus": status_code,
        "fhirIssueCode": issue_code or None,
        "diagnostics": diagnostics or raw_message or None,
        "rawOperationOutcome": obj,
    }


def _fhir_request(method: str, url: str, data=None, token: str = "", timeout_seconds: int = 30):
    headers = {
        "Accept": "application/fhir+json",
    }
    if data is not None:
        headers["Content-Type"] = "application/fhir+json"
    if token:
        headers["Authorization"] = f"Bearer {token}"

    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")

    req = urllib.request.Request(url=url, method=method, headers=headers, data=body)
    try:
        with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            parsed = _safe_json_loads(raw)
            return resp.status, parsed if parsed is not None else raw
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        return e.code, raw
    except (TimeoutError, socket.timeout) as e:
        return 0, f"Timeout while calling FHIR server: {e}"
    except urllib.error.URLError as e:
        return 0, f"Network error while calling FHIR server: {e.reason}"
    except Exception as e:
        return 0, str(e)


class ImportUIHandler(BaseHTTPRequestHandler):
    project_root: Path = Path(".")
    ui_file: Path = Path("ui/import-ui.html")
    import_script: Path = Path("scripts/import-patient-intake-csv.ps1")
    create_script: Path = Path("scripts/create-patient-intake.ps1")
    update_script: Path = Path("scripts/update-patient-intake.ps1")
    cors_allow_origin: str = "*"

    def _send_headers(self, status: int, content_type: str, content_len: int):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(content_len))
        self.send_header("Access-Control-Allow-Origin", self.cors_allow_origin)
        self.send_header("Access-Control-Allow-Methods", "GET,POST,PATCH,DELETE,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def _write_json(self, obj, status=200):
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self._send_headers(status, "application/json; charset=utf-8", len(data))
        self.wfile.write(data)

    def _write_html(self, html: str, status=200):
        data = html.encode("utf-8")
        self._send_headers(status, "text/html; charset=utf-8", len(data))
        self.wfile.write(data)

    def _read_json_body(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        return json.loads(body)

    def _resolve_base_url(self, mode: str, explicit_base_url: str) -> str:
        if explicit_base_url:
            return explicit_base_url.rstrip("/")
        if mode == "auth":
            return "http://localhost:8090"
        return "http://localhost:8091"

    def _build_smart_configuration(self):
        issuer = os.getenv("SMART_ISSUER", "http://localhost:8080/realms/fhir")
        authorization_endpoint = os.getenv("SMART_AUTHORIZATION_ENDPOINT", issuer.rstrip("/") + "/protocol/openid-connect/auth")
        token_endpoint = os.getenv("SMART_TOKEN_ENDPOINT", issuer.rstrip("/") + "/protocol/openid-connect/token")
        registration_endpoint = os.getenv("SMART_REGISTRATION_ENDPOINT", "")
        introspection_endpoint = os.getenv("SMART_INTROSPECTION_ENDPOINT", issuer.rstrip("/") + "/protocol/openid-connect/token/introspect")
        scopes_csv = os.getenv(
            "SMART_SCOPES_SUPPORTED",
            "openid,profile,launch/patient,patient/*.read,patient/*.write,patient/Patient.read,patient/Observation.read",
        )
        scopes_supported = [x.strip() for x in scopes_csv.split(",") if x.strip()]
        capability_csv = os.getenv(
            "SMART_CAPABILITIES",
            "sso-openid-connect,launch-ehr-client,client-public,permission-patient,permission-user",
        )
        capabilities = [x.strip() for x in capability_csv.split(",") if x.strip()]
        return {
            "issuer": issuer,
            "authorization_endpoint": authorization_endpoint,
            "token_endpoint": token_endpoint,
            "registration_endpoint": registration_endpoint or None,
            "introspection_endpoint": introspection_endpoint,
            "response_types_supported": ["code"],
            "grant_types_supported": ["authorization_code", "refresh_token", "client_credentials"],
            "token_endpoint_auth_methods_supported": ["client_secret_basic", "client_secret_post", "none"],
            "capabilities": capabilities,
            "scopes_supported": scopes_supported,
            "code_challenge_methods_supported": ["S256"],
        }

    def _is_scope_enforcement_enabled(self) -> bool:
        return str(os.getenv("SMART_SCOPE_ENFORCEMENT", "1")).strip().lower() not in ("0", "false", "off", "no")

    def _get_bearer_token(self) -> str:
        auth = str(self.headers.get("Authorization", "") or "").strip()
        if not auth.lower().startswith("bearer "):
            return ""
        token = auth[7:].strip()
        return token

    def _decode_jwt_payload(self, token: str):
        parts = token.split(".")
        if len(parts) < 2:
            return None
        payload_b64 = parts[1]
        pad_len = (4 - (len(payload_b64) % 4)) % 4
        payload_b64 += "=" * pad_len
        try:
            payload_bytes = base64.urlsafe_b64decode(payload_b64.encode("utf-8"))
            return _safe_json_loads(payload_bytes.decode("utf-8", errors="replace"))
        except Exception:
            return None

    def _extract_token_scopes(self, token: str):
        payload = self._decode_jwt_payload(token)
        if not isinstance(payload, dict):
            return None
        scopes = []
        scope_raw = payload.get("scope")
        if isinstance(scope_raw, str):
            scopes.extend([x.strip() for x in scope_raw.split(" ") if x.strip()])
        scp_raw = payload.get("scp")
        if isinstance(scp_raw, list):
            scopes.extend([str(x).strip() for x in scp_raw if str(x).strip()])
        elif isinstance(scp_raw, str):
            scopes.extend([x.strip() for x in scp_raw.split(" ") if x.strip()])
        return sorted(set(scopes))

    def _extract_request_scopes(self, token: str):
        allow_header = str(os.getenv("SMART_ALLOW_SCOPE_HEADER", "1")).strip().lower() not in ("0", "false", "off", "no")
        if allow_header:
            header_scopes = str(self.headers.get("X-SMART-Scopes", "") or "").strip()
            if header_scopes:
                return sorted(set([x.strip() for x in header_scopes.replace(",", " ").split(" ") if x.strip()]))
        return self._extract_token_scopes(token)

    def _require_scopes_any(self, required_any):
        if not self._is_scope_enforcement_enabled():
            return True, "", []
        token = self._get_bearer_token()
        if not token:
            self._write_json(
                {"ok": False, "error": {"code": "UNAUTHORIZED", "message": "Authentication is required. Please sign in again.", "httpStatus": 401}},
                status=401,
            )
            return False, "", []
        scopes = self._extract_request_scopes(token)
        if not isinstance(scopes, list):
            self._write_json(
                {"ok": False, "error": {"code": "UNAUTHORIZED", "message": "Bearer token is invalid or unreadable.", "httpStatus": 401}},
                status=401,
            )
            return False, token, []
        granted = any(scope in scopes for scope in required_any)
        if not granted:
            self._write_json(
                {
                    "ok": False,
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "You do not have permission to perform this action.",
                        "httpStatus": 403,
                        "requiredScopes": required_any,
                    },
                },
                status=403,
            )
            return False, token, scopes
        return True, token, scopes

    def _require_patient_observation_read_scopes(self):
        allowed, token, scopes = self._require_scopes_any(["patient/*.read", "patient/Patient.read", "patient/Observation.read"])
        if not allowed:
            return False, token, scopes
        # If wildcard scope exists, treat as fully granted.
        if "patient/*.read" in scopes:
            return True, token, scopes
        # Require both Patient.read and Observation.read when wildcard is absent.
        need = {"patient/Patient.read", "patient/Observation.read"}
        if not need.issubset(set(scopes)):
            self._write_json(
                {
                    "ok": False,
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "You do not have permission to perform this action.",
                        "httpStatus": 403,
                        "requiredScopes": sorted(list(need)),
                    },
                },
                status=403,
            )
            return False, token, scopes
        return True, token, scopes

    def _require_condition_read_scopes(self):
        allowed, token, scopes = self._require_scopes_any(["patient/*.read", "patient/Condition.read"])
        if not allowed:
            return False, token, scopes
        return True, token, scopes

    def _run_ps(self, args):
        proc = subprocess.run(
            args,
            cwd=str(self.project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        logs = (proc.stdout or "") + (("\n" + proc.stderr) if proc.stderr else "")
        return proc.returncode, logs

    def _validate_attachment_payload(self, payload: dict):
        # Contract: JSON mode uses payload.contentType + payload.url, with optional payload.sizeBytes/payload.contentBase64.
        allowed_csv = os.getenv(
            "ATTACHMENT_ALLOWED_CONTENT_TYPES",
            "image/png,image/jpeg,image/webp,application/pdf,text/plain",
        )
        allowed_types = {x.strip().lower() for x in allowed_csv.split(",") if x.strip()}
        max_bytes = int(str(os.getenv("ATTACHMENT_MAX_BYTES", "10485760")).strip() or "10485760")

        content_type = str(payload.get("contentType", "")).strip().lower()
        url = str(payload.get("url", "")).strip()
        if not content_type or not url:
            return {
                "ok": False,
                "status": 400,
                "error": {"code": "VALIDATION_ERROR", "message": "payload.contentType and payload.url are required.", "httpStatus": 400},
            }

        if content_type not in allowed_types:
            return {
                "ok": False,
                "status": 415,
                "error": {
                    "code": "UNSUPPORTED_MEDIA_TYPE",
                    "message": "payload.contentType is not allowed.",
                    "httpStatus": 415,
                    "allowedContentTypes": sorted(list(allowed_types)),
                },
            }

        size_bytes = payload.get("sizeBytes", None)
        if size_bytes is None and isinstance(payload.get("contentBase64"), str):
            b64 = str(payload.get("contentBase64")).strip()
            try:
                # base64 payload (no data URL header)
                size_bytes = len(base64.b64decode(b64.encode("utf-8"), validate=False))
            except Exception:
                return {
                    "ok": False,
                    "status": 400,
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "payload.contentBase64 is invalid base64.",
                        "httpStatus": 400,
                    },
                }
        if size_bytes is not None:
            try:
                size_int = int(size_bytes)
            except Exception:
                return {
                    "ok": False,
                    "status": 400,
                    "error": {"code": "VALIDATION_ERROR", "message": "payload.sizeBytes must be an integer.", "httpStatus": 400},
                }
            if size_int < 0:
                return {
                    "ok": False,
                    "status": 400,
                    "error": {"code": "VALIDATION_ERROR", "message": "payload.sizeBytes must be >= 0.", "httpStatus": 400},
                }
            if size_int > max_bytes:
                return {
                    "ok": False,
                    "status": 413,
                    "error": {
                        "code": "PAYLOAD_TOO_LARGE",
                        "message": "Attachment exceeds allowed size limit.",
                        "httpStatus": 413,
                        "maxBytes": max_bytes,
                    },
                }

        return {"ok": True, "contentType": content_type, "url": url}

    def _collect_intake_summary(self, base_url: str, patient_id: str, token: str = ""):
        status, patient_obj = _fhir_request("GET", f"{base_url}/fhir/Patient/{patient_id}", token=token)
        if status >= 400 or status == 0:
            return status, patient_obj

        status_obs, obs_obj = _fhir_request("GET", f"{base_url}/fhir/Observation?subject=Patient/{patient_id}&_count=200", token=token)
        if status_obs >= 400 or status_obs == 0:
            return status_obs, obs_obj

        status_ct, ct_obj = _fhir_request("GET", f"{base_url}/fhir/CareTeam?subject=Patient/{patient_id}&_count=50", token=token)
        if status_ct >= 400 or status_ct == 0:
            return status_ct, ct_obj

        practitioners = []
        refs = set()
        gp = patient_obj.get("generalPractitioner", []) if isinstance(patient_obj, dict) else []
        for x in gp:
            ref = x.get("reference", "")
            if isinstance(ref, str) and ref.startswith("Practitioner/"):
                refs.add(ref.split("/", 1)[1])

        if isinstance(ct_obj, dict):
            for ent in ct_obj.get("entry", []) or []:
                res = ent.get("resource", {})
                for p in res.get("participant", []) or []:
                    mem = p.get("member", {})
                    ref = mem.get("reference", "")
                    if isinstance(ref, str) and ref.startswith("Practitioner/"):
                        refs.add(ref.split("/", 1)[1])

        for pid in sorted(refs):
            s, po = _fhir_request("GET", f"{base_url}/fhir/Practitioner/{pid}", token=token)
            if s < 400 and isinstance(po, dict):
                practitioners.append(po)

        observations = []
        if isinstance(obs_obj, dict):
            for ent in obs_obj.get("entry", []) or []:
                res = ent.get("resource")
                if isinstance(res, dict):
                    observations.append(res)

        care_teams = []
        if isinstance(ct_obj, dict):
            for ent in ct_obj.get("entry", []) or []:
                res = ent.get("resource")
                if isinstance(res, dict):
                    care_teams.append(res)

        return 200, {
            "patient": patient_obj,
            "observations": observations,
            "careTeams": care_teams,
            "practitioners": practitioners,
            "summary": {
                "patientId": patient_id,
                "observationCount": len(observations),
                "careTeamCount": len(care_teams),
                "practitionerCount": len(practitioners),
            },
        }

    def _collect_patient_conditions(self, base_url: str, patient_id: str, token: str = ""):
        status, patient_obj = _fhir_request("GET", f"{base_url}/fhir/Patient/{patient_id}", token=token)
        if status >= 400 or status == 0:
            return status, patient_obj

        status_cond, cond_obj = _fhir_request("GET", f"{base_url}/fhir/Condition?subject=Patient/{patient_id}&_count=200", token=token)
        if status_cond >= 400 or status_cond == 0:
            return status_cond, cond_obj

        conditions = []
        if isinstance(cond_obj, dict):
            for ent in cond_obj.get("entry", []) or []:
                res = ent.get("resource")
                if isinstance(res, dict):
                    conditions.append(res)

        return 200, {
            "patientId": patient_id,
            "conditions": conditions,
            "summary": {
                "conditionCount": len(conditions),
            },
        }

    def _collect_patient_media(self, base_url: str, patient_id: str, token: str = ""):
        status, patient_obj = _fhir_request("GET", f"{base_url}/fhir/Patient/{patient_id}", token=token)
        if status >= 400 or status == 0:
            return status, patient_obj

        status_media, media_obj = _fhir_request("GET", f"{base_url}/fhir/Media?patient={patient_id}&_count=200", token=token)
        if status_media >= 400 or status_media == 0:
            return status_media, media_obj

        items = []
        if isinstance(media_obj, dict):
            for ent in media_obj.get("entry", []) or []:
                res = ent.get("resource")
                if isinstance(res, dict):
                    items.append(res)

        return 200, {
            "patientId": patient_id,
            "items": items,
            "summary": {
                "mediaCount": len(items),
            },
        }

    def _collect_patient_documents(self, base_url: str, patient_id: str, token: str = ""):
        status, patient_obj = _fhir_request("GET", f"{base_url}/fhir/Patient/{patient_id}", token=token)
        if status >= 400 or status == 0:
            return status, patient_obj

        status_doc, doc_obj = _fhir_request("GET", f"{base_url}/fhir/DocumentReference?patient={patient_id}&_count=200", token=token)
        if status_doc >= 400 or status_doc == 0:
            return status_doc, doc_obj

        items = []
        if isinstance(doc_obj, dict):
            for ent in doc_obj.get("entry", []) or []:
                res = ent.get("resource")
                if isinstance(res, dict):
                    items.append(res)

        return 200, {
            "patientId": patient_id,
            "items": items,
            "summary": {
                "documentReferenceCount": len(items),
            },
        }

    def _collect_practitioners(self, base_url: str, query_name: str = "", token: str = ""):
        search_query = "_count=200"
        if query_name:
            search_query += "&name=" + urllib.parse.quote(query_name)
        status, pr_obj = _fhir_request("GET", f"{base_url}/fhir/Practitioner?{search_query}", token=token)
        if status >= 400 or status == 0:
            return status, pr_obj

        items = []
        if isinstance(pr_obj, dict):
            for ent in pr_obj.get("entry", []) or []:
                res = ent.get("resource")
                if isinstance(res, dict):
                    items.append(res)

        # Fallback: some environments may return empty result for name search even when a match exists.
        if query_name and not items:
            status_all, all_obj = _fhir_request("GET", f"{base_url}/fhir/Practitioner?_count=200", token=token)
            if status_all >= 400 or status_all == 0:
                return status_all, all_obj
            if isinstance(all_obj, dict):
                needle = query_name.lower()
                for ent in all_obj.get("entry", []) or []:
                    res = ent.get("resource")
                    if not isinstance(res, dict):
                        continue
                    names = res.get("name", []) or []
                    family = ""
                    given = ""
                    if names and isinstance(names[0], dict):
                        family = str(names[0].get("family", "")).lower()
                        given_list = names[0].get("given", []) or []
                        given = " ".join([str(x).lower() for x in given_list if x is not None])
                    if needle in family or needle in given:
                        items.append(res)

        return 200, {
            "items": items,
            "summary": {
                "count": len(items),
            },
        }

    def do_OPTIONS(self):
        self._send_headers(204, "text/plain; charset=utf-8", 0)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._write_html(load_text(self.ui_file), status=200)
            return

        if self.path == "/health":
            self._write_json({"status": "UP", "service": "phase1-backend"}, status=200)
            return

        if self.path == "/.well-known/smart-configuration":
            self._write_json(self._build_smart_configuration(), status=200)
            return

        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)

        m = re.match(r"^/api/patients/([^/]+)/intake-summary$", path)
        if m:
            patient_id = urllib.parse.unquote(m.group(1))
            mode = (qs.get("mode", ["dev"])[0] or "dev").strip()
            token = ""
            if mode == "auth":
                allowed, token, scopes = self._require_patient_observation_read_scopes()
                if not allowed:
                    return
            base_url = self._resolve_base_url(mode, (qs.get("baseUrl", [""])[0] or "").strip())
            status, payload = self._collect_intake_summary(base_url=base_url, patient_id=patient_id, token=token)
            if status != 200:
                err = _parse_fhir_error(payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False), status)
                self._write_json({"ok": False, "error": err}, status=err["httpStatus"] if err["httpStatus"] > 0 else 500)
                return

            self._write_json(
                {
                    "ok": True,
                    "data": payload,
                    "source": {
                        "mode": mode,
                        "baseUrl": base_url,
                        "resourceType": ["Patient", "Observation", "CareTeam", "Practitioner"],
                        "smartScopeCheck": "enabled" if mode == "auth" and self._is_scope_enforcement_enabled() else "disabled",
                        "linkage": {
                            "model": "patient-latest",
                            "patient": "explicit",
                            "observation": "explicit",
                            "careTeam": "explicit_or_fallback",
                            "practitioner": "explicit_or_fallback",
                        },
                    },
                },
                status=200,
            )
            return

        m = re.match(r"^/api/patients/([^/]+)/conditions$", path)
        if m:
            patient_id = urllib.parse.unquote(m.group(1))
            mode = (qs.get("mode", ["dev"])[0] or "dev").strip()
            if mode not in ("dev", "auth"):
                self._write_json({"ok": False, "error": {"code": "INVALID_MODE", "message": "mode must be dev or auth."}}, status=400)
                return
            if mode == "auth":
                allowed, _, _ = self._require_condition_read_scopes()
                if not allowed:
                    return
            base_url = self._resolve_base_url(mode, (qs.get("baseUrl", [""])[0] or "").strip())
            status, payload = self._collect_patient_conditions(base_url=base_url, patient_id=patient_id)
            if status != 200:
                err = _parse_fhir_error(payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False), status)
                self._write_json({"ok": False, "error": err}, status=err["httpStatus"] if err["httpStatus"] > 0 else 500)
                return

            self._write_json(
                {
                    "ok": True,
                    "data": payload,
                    "source": {
                        "mode": mode,
                        "baseUrl": base_url,
                        "resourceType": ["Condition"],
                        "linkage": {
                            "model": "patient-latest",
                            "condition": "explicit",
                        },
                    },
                },
                status=200,
            )
            return

        m = re.match(r"^/api/conditions/([^/]+)$", path)
        if m:
            condition_id = urllib.parse.unquote(m.group(1))
            mode = (qs.get("mode", ["dev"])[0] or "dev").strip()
            if mode not in ("dev", "auth"):
                self._write_json({"ok": False, "error": {"code": "INVALID_MODE", "message": "mode must be dev or auth."}}, status=400)
                return
            if mode == "auth":
                allowed, _, _ = self._require_condition_read_scopes()
                if not allowed:
                    return
            base_url = self._resolve_base_url(mode, (qs.get("baseUrl", [""])[0] or "").strip())
            status, payload = _fhir_request("GET", f"{base_url}/fhir/Condition/{condition_id}")
            if status >= 400 or status == 0:
                err = _parse_fhir_error(payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False), status)
                self._write_json({"ok": False, "error": err}, status=err["httpStatus"] if err["httpStatus"] > 0 else 500)
                return

            self._write_json(
                {
                    "ok": True,
                    "data": payload,
                    "source": {
                        "mode": mode,
                        "baseUrl": base_url,
                        "resourceType": ["Condition"],
                        "linkage": {
                            "model": "direct-by-id",
                            "condition": "explicit",
                        },
                    },
                },
                status=200,
            )
            return

        m = re.match(r"^/api/patients/([^/]+)/media$", path)
        if m:
            patient_id = urllib.parse.unquote(m.group(1))
            mode = (qs.get("mode", ["dev"])[0] or "dev").strip()
            if mode not in ("dev", "auth"):
                self._write_json({"ok": False, "error": {"code": "INVALID_MODE", "message": "mode must be dev or auth."}}, status=400)
                return
            base_url = self._resolve_base_url(mode, (qs.get("baseUrl", [""])[0] or "").strip())
            status, payload = self._collect_patient_media(base_url=base_url, patient_id=patient_id)
            if status != 200:
                err = _parse_fhir_error(payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False), status)
                self._write_json({"ok": False, "error": err}, status=err["httpStatus"] if err["httpStatus"] > 0 else 500)
                return
            self._write_json({"ok": True, "data": payload, "source": {"mode": mode, "baseUrl": base_url, "resourceType": ["Media"]}}, status=200)
            return

        m = re.match(r"^/api/patients/([^/]+)/documents$", path)
        if m:
            patient_id = urllib.parse.unquote(m.group(1))
            mode = (qs.get("mode", ["dev"])[0] or "dev").strip()
            if mode not in ("dev", "auth"):
                self._write_json({"ok": False, "error": {"code": "INVALID_MODE", "message": "mode must be dev or auth."}}, status=400)
                return
            base_url = self._resolve_base_url(mode, (qs.get("baseUrl", [""])[0] or "").strip())
            status, payload = self._collect_patient_documents(base_url=base_url, patient_id=patient_id)
            if status != 200:
                err = _parse_fhir_error(payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False), status)
                self._write_json({"ok": False, "error": err}, status=err["httpStatus"] if err["httpStatus"] > 0 else 500)
                return
            self._write_json({"ok": True, "data": payload, "source": {"mode": mode, "baseUrl": base_url, "resourceType": ["DocumentReference"]}}, status=200)
            return

        if path == "/api/practitioners":
            mode = (qs.get("mode", ["dev"])[0] or "dev").strip()
            if mode not in ("dev", "auth"):
                self._write_json({"ok": False, "error": {"code": "INVALID_MODE", "message": "mode must be dev or auth."}}, status=400)
                return
            base_url = self._resolve_base_url(mode, (qs.get("baseUrl", [""])[0] or "").strip())
            query_name = (qs.get("name", [""])[0] or "").strip()
            status, payload = self._collect_practitioners(base_url=base_url, query_name=query_name)
            if status != 200:
                err = _parse_fhir_error(payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False), status)
                self._write_json({"ok": False, "error": err}, status=err["httpStatus"] if err["httpStatus"] > 0 else 500)
                return
            self._write_json({"ok": True, "data": payload, "source": {"mode": mode, "baseUrl": base_url, "resourceType": ["Practitioner"]}}, status=200)
            return

        self._write_json({"ok": False, "error": {"code": "NOT_FOUND", "message": "Not Found"}}, status=404)

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path

        if path == "/api/process":
            # Keep existing import UI API.
            self._handle_import_ui_api()
            return

        if path == "/api/patients/intake":
            self._handle_create_intake()
            return

        m = re.match(r"^/api/patients/([^/]+)/conditions$", path)
        if m:
            patient_id = urllib.parse.unquote(m.group(1))
            self._handle_create_condition(patient_id)
            return

        m = re.match(r"^/api/patients/([^/]+)/media$", path)
        if m:
            patient_id = urllib.parse.unquote(m.group(1))
            self._handle_create_media(patient_id)
            return

        m = re.match(r"^/api/patients/([^/]+)/documents$", path)
        if m:
            patient_id = urllib.parse.unquote(m.group(1))
            self._handle_create_document_reference(patient_id)
            return

        if path == "/api/practitioners":
            self._handle_create_practitioner()
            return

        self._write_json({"ok": False, "error": {"code": "NOT_FOUND", "message": "Not Found"}}, status=404)

    def do_PATCH(self):
        path = urllib.parse.urlparse(self.path).path
        m = re.match(r"^/api/patients/([^/]+)/intake$", path)
        if m:
            patient_id = urllib.parse.unquote(m.group(1))
            self._handle_patch_intake(patient_id)
            return

        m = re.match(r"^/api/practitioners/([^/]+)$", path)
        if m:
            practitioner_id = urllib.parse.unquote(m.group(1))
            self._handle_patch_practitioner(practitioner_id)
            return

        self._write_json({"ok": False, "error": {"code": "NOT_FOUND", "message": "Not Found"}}, status=404)

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        m = re.match(r"^/api/patients/([^/]+)/intake$", parsed.path)
        if not m:
            self._write_json({"ok": False, "error": {"code": "NOT_FOUND", "message": "Not Found"}}, status=404)
            return

        patient_id = urllib.parse.unquote(m.group(1))
        qs = urllib.parse.parse_qs(parsed.query)
        mode = (qs.get("mode", ["dev"])[0] or "dev").strip()
        if mode not in ("dev", "auth"):
            self._write_json({"ok": False, "error": {"code": "INVALID_MODE", "message": "mode must be dev or auth."}}, status=400)
            return
        base_url = self._resolve_base_url(mode, (qs.get("baseUrl", [""])[0] or "").strip())
        self._handle_delete_intake_observations(patient_id=patient_id, mode=mode, base_url=base_url)

    def _handle_import_ui_api(self):
        temp_csv = None
        validation_report = None
        result_json = None
        try:
            body = self._read_json_body()
            csv_text = str(body.get("csvText", ""))
            if not csv_text.strip():
                self._write_json({"ok": False, "error": {"code": "CSV_REQUIRED", "message": "csvText is required."}}, status=400)
                return

            mode = str(body.get("mode", "dev")).strip() or "dev"
            if mode not in ("dev", "auth"):
                self._write_json({"ok": False, "error": {"code": "INVALID_MODE", "message": "mode must be dev or auth."}}, status=400)
                return

            base_url = str(body.get("baseUrl", "")).strip()
            validate_only = bool(body.get("validateOnly", False))
            continue_on_validation_error = bool(body.get("continueOnValidationError", False))

            with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8", newline="") as f:
                f.write(csv_text)
                temp_csv = f.name
            with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8") as f:
                validation_report = f.name
            with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
                result_json = f.name

            args = [
                "powershell",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(self.import_script),
                "-Mode",
                mode,
                "-CsvFile",
                temp_csv,
                "-ValidationReportPath",
                validation_report,
                "-ImportResultJsonPath",
                result_json,
            ]
            if base_url:
                args.extend(["-BaseUrl", base_url])
            if validate_only:
                args.append("-ValidateOnly")
            if continue_on_validation_error:
                args.append("-ContinueOnValidationError")

            exit_code, logs = self._run_ps(args)

            validation_issues = []
            if validation_report and os.path.exists(validation_report):
                with open(validation_report, "r", encoding="utf-8", newline="") as f:
                    validation_issues = list(csv.DictReader(f))

            result_obj = None
            if result_json and os.path.exists(result_json):
                text = Path(result_json).read_text(encoding="utf-8").strip()
                if text:
                    result_obj = json.loads(text)

            ok = exit_code == 0
            status = 200 if ok else 500
            self._write_json(
                {
                    "ok": ok,
                    "exitCode": exit_code,
                    "logs": logs,
                    "validationIssues": validation_issues,
                    "result": result_obj,
                },
                status=status,
            )
        except Exception as e:
            self._write_json({"ok": False, "error": {"code": "INTERNAL_ERROR", "message": str(e)}}, status=500)
        finally:
            for p in (temp_csv, validation_report, result_json):
                if p and os.path.exists(p):
                    try:
                        os.remove(p)
                    except OSError:
                        pass

    def _handle_create_intake(self):
        temp_json = None
        temp_out = None
        try:
            body = self._read_json_body()
            mode = str(body.get("mode", "dev")).strip() or "dev"
            if mode not in ("dev", "auth"):
                self._write_json({"ok": False, "error": {"code": "INVALID_MODE", "message": "mode must be dev or auth."}}, status=400)
                return

            base_url = self._resolve_base_url(mode, str(body.get("baseUrl", "")).strip())
            payload = body.get("payload")
            if not isinstance(payload, dict):
                self._write_json({"ok": False, "error": {"code": "INVALID_PAYLOAD", "message": "payload (object) is required."}}, status=400)
                return

            with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False)
                temp_json = f.name
            with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
                temp_out = f.name

            args = [
                "powershell",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(self.create_script),
                "-Mode",
                mode,
                "-BaseUrl",
                base_url,
                "-InputFile",
                temp_json,
                "-OutFile",
                temp_out,
            ]
            exit_code, logs = self._run_ps(args)
            if exit_code != 0:
                err = _parse_fhir_error(logs, 400)
                self._write_json({"ok": False, "error": err, "logs": logs}, status=400)
                return

            patient = payload.get("patient", {})
            patient_id = str(patient.get("id", "")).strip()
            if patient_id:
                s, summary = self._collect_intake_summary(base_url=base_url, patient_id=patient_id)
                if s == 200:
                    self._write_json({"ok": True, "data": summary, "logs": logs}, status=200)
                    return

            self._write_json({"ok": True, "message": "Intake created.", "logs": logs}, status=200)
        except Exception as e:
            self._write_json({"ok": False, "error": {"code": "INTERNAL_ERROR", "message": str(e)}}, status=500)
        finally:
            for p in (temp_json, temp_out):
                if p and os.path.exists(p):
                    try:
                        os.remove(p)
                    except OSError:
                        pass

    def _handle_patch_intake(self, patient_id: str):
        try:
            body = self._read_json_body()
            mode = str(body.get("mode", "dev")).strip() or "dev"
            if mode not in ("dev", "auth"):
                self._write_json({"ok": False, "error": {"code": "INVALID_MODE", "message": "mode must be dev or auth."}}, status=400)
                return

            base_url = self._resolve_base_url(mode, str(body.get("baseUrl", "")).strip())
            payload = body.get("payload")
            if not isinstance(payload, dict):
                self._write_json({"ok": False, "error": {"code": "INVALID_PAYLOAD", "message": "payload (object) is required."}}, status=400)
                return

            key_map = {
                "nameFamily": "NameFamily",
                "nameGiven": "NameGiven",
                "gender": "Gender",
                "birthDate": "BirthDate",
                "newNationalId": "NewNationalId",
                "nhiCardNo": "NhiCardNo",
                "educationLevel": "EducationLevel",
                "occupation": "Occupation",
                "monthlyIncome": "MonthlyIncome",
                "monthlyExpense": "MonthlyExpense",
                "hobby": "Hobby",
                "psychologicalTraits": "PsychologicalTraits",
                "behaviorPattern": "BehaviorPattern",
                "biomarkerCode": "BiomarkerCode",
                "biomarkerDisplay": "BiomarkerDisplay",
                "biomarkerValue": "BiomarkerValue",
                "biomarkerUnit": "BiomarkerUnit",
                "doctorPractitionerId": "DoctorPractitionerId",
                "doctorFamily": "DoctorFamily",
                "doctorGiven": "DoctorGiven",
            }

            args = [
                "powershell",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(self.update_script),
                "-Mode",
                mode,
                "-BaseUrl",
                base_url,
                "-PatientId",
                patient_id,
            ]

            for in_key, ps_key in key_map.items():
                if in_key not in payload:
                    continue
                v = payload.get(in_key)
                if v is None:
                    continue
                if isinstance(v, str) and v.strip() == "":
                    continue
                args.extend([f"-{ps_key}", str(v)])

            exit_code, logs = self._run_ps(args)
            if exit_code != 0:
                err = _parse_fhir_error(logs, 400)
                self._write_json({"ok": False, "error": err, "logs": logs}, status=400)
                return

            s, summary = self._collect_intake_summary(base_url=base_url, patient_id=patient_id)
            if s != 200:
                err = _parse_fhir_error(summary if isinstance(summary, str) else json.dumps(summary, ensure_ascii=False), s)
                self._write_json({"ok": False, "error": err, "logs": logs}, status=err["httpStatus"] if err["httpStatus"] > 0 else 500)
                return

            self._write_json({"ok": True, "data": summary, "logs": logs}, status=200)
        except Exception as e:
            self._write_json({"ok": False, "error": {"code": "INTERNAL_ERROR", "message": str(e)}}, status=500)

    def _handle_delete_intake_observations(self, patient_id: str, mode: str, base_url: str):
        try:
            # Guardrail: we first confirm patient existence and only delete Observation resources.
            status_patient, patient_obj = _fhir_request("GET", f"{base_url}/fhir/Patient/{patient_id}")
            if status_patient >= 400 or status_patient == 0:
                err = _parse_fhir_error(
                    patient_obj if isinstance(patient_obj, str) else json.dumps(patient_obj, ensure_ascii=False),
                    status_patient,
                )
                self._write_json({"ok": False, "error": err}, status=err["httpStatus"] if err["httpStatus"] > 0 else 500)
                return

            status_obs, obs_obj = _fhir_request("GET", f"{base_url}/fhir/Observation?subject=Patient/{patient_id}&_count=200")
            if status_obs >= 400 or status_obs == 0:
                err = _parse_fhir_error(
                    obs_obj if isinstance(obs_obj, str) else json.dumps(obs_obj, ensure_ascii=False),
                    status_obs,
                )
                self._write_json({"ok": False, "error": err}, status=err["httpStatus"] if err["httpStatus"] > 0 else 500)
                return

            observation_ids = []
            if isinstance(obs_obj, dict):
                for ent in obs_obj.get("entry", []) or []:
                    res = ent.get("resource")
                    if isinstance(res, dict):
                        obs_id = str(res.get("id", "")).strip()
                        if obs_id:
                            observation_ids.append(obs_id)

            deleted_ids = []
            failed = []
            for obs_id in observation_ids:
                status_del, del_obj = _fhir_request("DELETE", f"{base_url}/fhir/Observation/{obs_id}")
                if 200 <= status_del < 300:
                    deleted_ids.append(obs_id)
                else:
                    failed.append(
                        {
                            "id": obs_id,
                            "status": status_del,
                            "payload": del_obj,
                        }
                    )

            if failed:
                first = failed[0]
                err = _parse_fhir_error(
                    first["payload"] if isinstance(first["payload"], str) else json.dumps(first["payload"], ensure_ascii=False),
                    first["status"],
                )
                if err.get("code") == "UNKNOWN_ERROR":
                    err["code"] = "DELETE_FAILED"
                    err["message"] = "Failed to delete one or more observations."
                self._write_json(
                    {
                        "ok": False,
                        "error": err,
                        "data": {
                            "patientId": patient_id,
                            "deletedObservationCount": len(deleted_ids),
                            "deletedObservationIds": deleted_ids,
                            "failedObservationIds": [x["id"] for x in failed],
                            "patientDeleted": False,
                        },
                    },
                    status=err["httpStatus"] if err["httpStatus"] > 0 else 500,
                )
                return

            self._write_json(
                {
                    "ok": True,
                    "data": {
                        "patientId": patient_id,
                        "deletedObservationCount": len(deleted_ids),
                        "deletedObservationIds": deleted_ids,
                        "patientDeleted": False,
                    },
                    "source": {
                        "mode": mode,
                        "baseUrl": base_url,
                        "resourceType": ["Observation"],
                    },
                },
                status=200,
            )
        except Exception as e:
            self._write_json({"ok": False, "error": {"code": "INTERNAL_ERROR", "message": str(e)}}, status=500)

    def _handle_create_condition(self, patient_id: str):
        try:
            body = self._read_json_body()
            mode = str(body.get("mode", "dev")).strip() or "dev"
            if mode not in ("dev", "auth"):
                self._write_json({"ok": False, "error": {"code": "INVALID_MODE", "message": "mode must be dev or auth."}}, status=400)
                return

            base_url = self._resolve_base_url(mode, str(body.get("baseUrl", "")).strip())
            payload = body.get("payload")
            if not isinstance(payload, dict):
                self._write_json({"ok": False, "error": {"code": "INVALID_PAYLOAD", "message": "payload (object) is required."}}, status=400)
                return

            status_patient, patient_obj = _fhir_request("GET", f"{base_url}/fhir/Patient/{patient_id}")
            if status_patient >= 400 or status_patient == 0:
                err = _parse_fhir_error(
                    patient_obj if isinstance(patient_obj, str) else json.dumps(patient_obj, ensure_ascii=False),
                    status_patient,
                )
                self._write_json({"ok": False, "error": err}, status=err["httpStatus"] if err["httpStatus"] > 0 else 500)
                return

            code_payload = payload.get("code")
            code_text = str(payload.get("codeText", "")).strip()
            clinical_status = str(payload.get("clinicalStatus", "")).strip()
            allowed_clinical_status = {"active", "recurrence", "relapse", "inactive", "remission", "resolved"}

            validation_issues = []
            if not clinical_status:
                validation_issues.append("payload.clinicalStatus is required.")
            elif clinical_status not in allowed_clinical_status:
                validation_issues.append("payload.clinicalStatus must be one of: active, recurrence, relapse, inactive, remission, resolved.")

            if not code_text and not isinstance(code_payload, dict):
                validation_issues.append("Either payload.codeText (string) or payload.code (object) is required.")

            if isinstance(code_payload, dict):
                code_system = str(code_payload.get("system", "")).strip()
                code_value = str(code_payload.get("code", "")).strip()
                if not code_system:
                    validation_issues.append("payload.code.system is required when payload.code is provided.")
                if not code_value:
                    validation_issues.append("payload.code.code is required when payload.code is provided.")

            if validation_issues:
                self._write_json(
                    {
                        "ok": False,
                        "error": {
                            "code": "VALIDATION_ERROR",
                            "message": "Condition payload validation failed.",
                            "httpStatus": 400,
                            "details": validation_issues,
                        },
                    },
                    status=400,
                )
                return

            condition_resource = {
                "resourceType": "Condition",
                "subject": {
                    "reference": f"Patient/{patient_id}",
                },
                "clinicalStatus": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                            "code": clinical_status,
                        }
                    ]
                },
                "verificationStatus": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                            "code": str(payload.get("verificationStatus", "confirmed")),
                        }
                    ]
                },
                "category": [
                    {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/condition-category",
                                "code": str(payload.get("categoryCode", "problem-list-item")),
                            }
                        ],
                        "text": str(payload.get("categoryText", "Problem List Item")),
                    }
                ],
            }

            if isinstance(code_payload, dict):
                coding = {}
                if str(code_payload.get("system", "")).strip():
                    coding["system"] = str(code_payload.get("system")).strip()
                if str(code_payload.get("code", "")).strip():
                    coding["code"] = str(code_payload.get("code")).strip()
                if str(code_payload.get("display", "")).strip():
                    coding["display"] = str(code_payload.get("display")).strip()

                condition_code = {}
                if coding:
                    condition_code["coding"] = [coding]
                if code_text:
                    condition_code["text"] = code_text
                elif str(code_payload.get("display", "")).strip():
                    condition_code["text"] = str(code_payload.get("display")).strip()
                else:
                    condition_code["text"] = "Condition"
                condition_resource["code"] = condition_code
            else:
                condition_resource["code"] = {"text": code_text}

            onset_date_time = str(payload.get("onsetDateTime", "")).strip()
            if onset_date_time:
                condition_resource["onsetDateTime"] = onset_date_time

            recorded_date = str(payload.get("recordedDate", "")).strip()
            if recorded_date:
                condition_resource["recordedDate"] = recorded_date

            note_text = str(payload.get("note", "")).strip()
            if note_text:
                condition_resource["note"] = [{"text": note_text}]

            asserter_practitioner_id = str(payload.get("asserterPractitionerId", "")).strip()
            if asserter_practitioner_id:
                status_pr, pr_obj = _fhir_request("GET", f"{base_url}/fhir/Practitioner/{asserter_practitioner_id}")
                if status_pr >= 400 or status_pr == 0:
                    err = _parse_fhir_error(
                        pr_obj if isinstance(pr_obj, str) else json.dumps(pr_obj, ensure_ascii=False),
                        status_pr,
                    )
                    self._write_json({"ok": False, "error": err}, status=err["httpStatus"] if err["httpStatus"] > 0 else 500)
                    return
                condition_resource["asserter"] = {"reference": f"Practitioner/{asserter_practitioner_id}"}

            status_create, created_obj = _fhir_request("POST", f"{base_url}/fhir/Condition", data=condition_resource)
            if status_create >= 400 or status_create == 0:
                err = _parse_fhir_error(
                    created_obj if isinstance(created_obj, str) else json.dumps(created_obj, ensure_ascii=False),
                    status_create,
                )
                self._write_json({"ok": False, "error": err}, status=err["httpStatus"] if err["httpStatus"] > 0 else 500)
                return

            self._write_json(
                {
                    "ok": True,
                    "data": {
                        "patientId": patient_id,
                        "condition": created_obj,
                    },
                    "source": {
                        "mode": mode,
                        "baseUrl": base_url,
                        "resourceType": ["Condition"],
                    },
                },
                status=201,
            )
        except Exception as e:
            self._write_json({"ok": False, "error": {"code": "INTERNAL_ERROR", "message": str(e)}}, status=500)

    def _handle_create_media(self, patient_id: str):
        try:
            body = self._read_json_body()
            mode = str(body.get("mode", "dev")).strip() or "dev"
            if mode not in ("dev", "auth"):
                self._write_json({"ok": False, "error": {"code": "INVALID_MODE", "message": "mode must be dev or auth."}}, status=400)
                return
            base_url = self._resolve_base_url(mode, str(body.get("baseUrl", "")).strip())
            payload = body.get("payload")
            if not isinstance(payload, dict):
                self._write_json({"ok": False, "error": {"code": "INVALID_PAYLOAD", "message": "payload (object) is required."}}, status=400)
                return

            status_patient, patient_obj = _fhir_request("GET", f"{base_url}/fhir/Patient/{patient_id}")
            if status_patient >= 400 or status_patient == 0:
                err = _parse_fhir_error(patient_obj if isinstance(patient_obj, str) else json.dumps(patient_obj, ensure_ascii=False), status_patient)
                self._write_json({"ok": False, "error": err}, status=err["httpStatus"] if err["httpStatus"] > 0 else 500)
                return

            validation = self._validate_attachment_payload(payload)
            if not validation.get("ok"):
                self._write_json({"ok": False, "error": validation.get("error")}, status=int(validation.get("status", 400)))
                return
            content_type = str(validation.get("contentType"))
            url = str(validation.get("url"))

            media = {
                "resourceType": "Media",
                "status": str(payload.get("status", "completed")),
                "subject": {"reference": f"Patient/{patient_id}"},
                "content": {
                    "contentType": content_type,
                    "url": url,
                },
            }
            title = str(payload.get("title", "")).strip()
            if title:
                media["content"]["title"] = title
            creation = str(payload.get("creation", "")).strip()
            if creation:
                media["content"]["creation"] = creation
            note = str(payload.get("note", "")).strip()
            if note:
                media["note"] = [{"text": note}]
            operator_id = str(payload.get("operatorPractitionerId", "")).strip()
            if operator_id:
                media["operator"] = {"reference": f"Practitioner/{operator_id}"}

            status_create, created_obj = _fhir_request("POST", f"{base_url}/fhir/Media", data=media)
            if status_create >= 400 or status_create == 0:
                err = _parse_fhir_error(created_obj if isinstance(created_obj, str) else json.dumps(created_obj, ensure_ascii=False), status_create)
                self._write_json({"ok": False, "error": err}, status=err["httpStatus"] if err["httpStatus"] > 0 else 500)
                return

            self._write_json(
                {"ok": True, "data": {"patientId": patient_id, "media": created_obj}, "source": {"mode": mode, "baseUrl": base_url, "resourceType": ["Media"]}},
                status=201,
            )
        except Exception as e:
            self._write_json({"ok": False, "error": {"code": "INTERNAL_ERROR", "message": str(e)}}, status=500)

    def _handle_create_document_reference(self, patient_id: str):
        try:
            body = self._read_json_body()
            mode = str(body.get("mode", "dev")).strip() or "dev"
            if mode not in ("dev", "auth"):
                self._write_json({"ok": False, "error": {"code": "INVALID_MODE", "message": "mode must be dev or auth."}}, status=400)
                return
            base_url = self._resolve_base_url(mode, str(body.get("baseUrl", "")).strip())
            payload = body.get("payload")
            if not isinstance(payload, dict):
                self._write_json({"ok": False, "error": {"code": "INVALID_PAYLOAD", "message": "payload (object) is required."}}, status=400)
                return

            status_patient, patient_obj = _fhir_request("GET", f"{base_url}/fhir/Patient/{patient_id}")
            if status_patient >= 400 or status_patient == 0:
                err = _parse_fhir_error(patient_obj if isinstance(patient_obj, str) else json.dumps(patient_obj, ensure_ascii=False), status_patient)
                self._write_json({"ok": False, "error": err}, status=err["httpStatus"] if err["httpStatus"] > 0 else 500)
                return

            validation = self._validate_attachment_payload(payload)
            if not validation.get("ok"):
                self._write_json({"ok": False, "error": validation.get("error")}, status=int(validation.get("status", 400)))
                return
            content_type = str(validation.get("contentType"))
            url = str(validation.get("url"))

            doc = {
                "resourceType": "DocumentReference",
                "status": str(payload.get("status", "current")),
                "subject": {"reference": f"Patient/{patient_id}"},
                "content": [
                    {
                        "attachment": {
                            "contentType": content_type,
                            "url": url,
                        }
                    }
                ],
            }
            description = str(payload.get("description", "")).strip()
            if description:
                doc["description"] = description
            title = str(payload.get("title", "")).strip()
            if title:
                doc["content"][0]["attachment"]["title"] = title
            date_value = str(payload.get("date", "")).strip()
            if date_value:
                doc["date"] = date_value

            status_create, created_obj = _fhir_request("POST", f"{base_url}/fhir/DocumentReference", data=doc)
            if status_create >= 400 or status_create == 0:
                err = _parse_fhir_error(created_obj if isinstance(created_obj, str) else json.dumps(created_obj, ensure_ascii=False), status_create)
                self._write_json({"ok": False, "error": err}, status=err["httpStatus"] if err["httpStatus"] > 0 else 500)
                return

            self._write_json(
                {"ok": True, "data": {"patientId": patient_id, "documentReference": created_obj}, "source": {"mode": mode, "baseUrl": base_url, "resourceType": ["DocumentReference"]}},
                status=201,
            )
        except Exception as e:
            self._write_json({"ok": False, "error": {"code": "INTERNAL_ERROR", "message": str(e)}}, status=500)

    def _handle_create_practitioner(self):
        try:
            body = self._read_json_body()
            mode = str(body.get("mode", "dev")).strip() or "dev"
            if mode not in ("dev", "auth"):
                self._write_json({"ok": False, "error": {"code": "INVALID_MODE", "message": "mode must be dev or auth."}}, status=400)
                return
            base_url = self._resolve_base_url(mode, str(body.get("baseUrl", "")).strip())
            payload = body.get("payload")
            if not isinstance(payload, dict):
                self._write_json({"ok": False, "error": {"code": "INVALID_PAYLOAD", "message": "payload (object) is required."}}, status=400)
                return

            family = str(payload.get("family", "")).strip()
            given = str(payload.get("given", "")).strip()
            if not family and not given:
                self._write_json({"ok": False, "error": {"code": "VALIDATION_ERROR", "message": "payload.family or payload.given is required.", "httpStatus": 400}}, status=400)
                return

            practitioner = {
                "resourceType": "Practitioner",
                "active": bool(payload.get("active", True)),
                "name": [
                    {
                        "family": family if family else "Unknown",
                        "given": [given if given else "Doctor"],
                    }
                ],
            }
            identifier_system = str(payload.get("identifierSystem", "")).strip()
            identifier_value = str(payload.get("identifierValue", "")).strip()
            if identifier_system and identifier_value:
                practitioner["identifier"] = [{"system": identifier_system, "value": identifier_value}]

            status_create, created_obj = _fhir_request("POST", f"{base_url}/fhir/Practitioner", data=practitioner)
            if status_create >= 400 or status_create == 0:
                err = _parse_fhir_error(created_obj if isinstance(created_obj, str) else json.dumps(created_obj, ensure_ascii=False), status_create)
                self._write_json({"ok": False, "error": err}, status=err["httpStatus"] if err["httpStatus"] > 0 else 500)
                return

            self._write_json(
                {"ok": True, "data": {"practitioner": created_obj}, "source": {"mode": mode, "baseUrl": base_url, "resourceType": ["Practitioner"]}},
                status=201,
            )
        except Exception as e:
            self._write_json({"ok": False, "error": {"code": "INTERNAL_ERROR", "message": str(e)}}, status=500)

    def _handle_patch_practitioner(self, practitioner_id: str):
        try:
            body = self._read_json_body()
            mode = str(body.get("mode", "dev")).strip() or "dev"
            if mode not in ("dev", "auth"):
                self._write_json({"ok": False, "error": {"code": "INVALID_MODE", "message": "mode must be dev or auth."}}, status=400)
                return
            base_url = self._resolve_base_url(mode, str(body.get("baseUrl", "")).strip())
            payload = body.get("payload")
            if not isinstance(payload, dict):
                self._write_json({"ok": False, "error": {"code": "INVALID_PAYLOAD", "message": "payload (object) is required."}}, status=400)
                return

            status_get, practitioner = _fhir_request("GET", f"{base_url}/fhir/Practitioner/{practitioner_id}")
            if status_get >= 400 or status_get == 0:
                err = _parse_fhir_error(practitioner if isinstance(practitioner, str) else json.dumps(practitioner, ensure_ascii=False), status_get)
                self._write_json({"ok": False, "error": err}, status=err["httpStatus"] if err["httpStatus"] > 0 else 500)
                return
            if not isinstance(practitioner, dict):
                self._write_json({"ok": False, "error": {"code": "BAD_REQUEST", "message": "Unexpected practitioner payload.", "httpStatus": 400}}, status=400)
                return

            family = str(payload.get("family", "")).strip()
            given = str(payload.get("given", "")).strip()
            active = payload.get("active", None)
            identifier_system = str(payload.get("identifierSystem", "")).strip()
            identifier_value = str(payload.get("identifierValue", "")).strip()

            if family or given:
                if not isinstance(practitioner.get("name"), list) or not practitioner.get("name"):
                    practitioner["name"] = [{"family": "Unknown", "given": ["Doctor"]}]
                name0 = practitioner["name"][0]
                if family:
                    name0["family"] = family
                if given:
                    name0["given"] = [given]
                practitioner["name"][0] = name0
            if active is not None:
                practitioner["active"] = bool(active)
            if identifier_system and identifier_value:
                practitioner["identifier"] = [{"system": identifier_system, "value": identifier_value}]

            status_put, updated_obj = _fhir_request("PUT", f"{base_url}/fhir/Practitioner/{practitioner_id}", data=practitioner)
            if status_put >= 400 or status_put == 0:
                err = _parse_fhir_error(updated_obj if isinstance(updated_obj, str) else json.dumps(updated_obj, ensure_ascii=False), status_put)
                self._write_json({"ok": False, "error": err}, status=err["httpStatus"] if err["httpStatus"] > 0 else 500)
                return

            self._write_json(
                {"ok": True, "data": {"practitioner": updated_obj}, "source": {"mode": mode, "baseUrl": base_url, "resourceType": ["Practitioner"]}},
                status=200,
            )
        except Exception as e:
            self._write_json({"ok": False, "error": {"code": "INTERNAL_ERROR", "message": str(e)}}, status=500)

    def log_message(self, format, *args):
        return


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8092)
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--cors-origin", default="*")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    ui_file = root / "ui" / "import-ui.html"
    import_script = root / "scripts" / "import-patient-intake-csv.ps1"
    create_script = root / "scripts" / "create-patient-intake.ps1"
    update_script = root / "scripts" / "update-patient-intake.ps1"

    for p, title in [
        (ui_file, "UI file"),
        (import_script, "Import script"),
        (create_script, "Create script"),
        (update_script, "Update script"),
    ]:
        if not p.exists():
            raise FileNotFoundError(f"{title} not found: {p}")

    ImportUIHandler.project_root = root
    ImportUIHandler.ui_file = ui_file
    ImportUIHandler.import_script = import_script
    ImportUIHandler.create_script = create_script
    ImportUIHandler.update_script = update_script
    ImportUIHandler.cors_allow_origin = args.cors_origin

    server = ThreadingHTTPServer((args.host, args.port), ImportUIHandler)
    print(f"Phase1 backend started at http://{args.host}:{args.port}/")
    print(f"CORS allow-origin: {args.cors_origin}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
