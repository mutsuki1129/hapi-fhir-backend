import argparse
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

    def do_OPTIONS(self):
        self._send_headers(204, "text/plain; charset=utf-8", 0)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._write_html(load_text(self.ui_file), status=200)
            return

        if self.path == "/health":
            self._write_json({"status": "UP", "service": "phase1-backend"}, status=200)
            return

        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)

        m = re.match(r"^/api/patients/([^/]+)/intake-summary$", path)
        if m:
            patient_id = urllib.parse.unquote(m.group(1))
            mode = (qs.get("mode", ["dev"])[0] or "dev").strip()
            base_url = self._resolve_base_url(mode, (qs.get("baseUrl", [""])[0] or "").strip())
            status, payload = self._collect_intake_summary(base_url=base_url, patient_id=patient_id)
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
                    },
                },
                status=200,
            )
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

        self._write_json({"ok": False, "error": {"code": "NOT_FOUND", "message": "Not Found"}}, status=404)

    def do_PATCH(self):
        m = re.match(r"^/api/patients/([^/]+)/intake$", urllib.parse.urlparse(self.path).path)
        if not m:
            self._write_json({"ok": False, "error": {"code": "NOT_FOUND", "message": "Not Found"}}, status=404)
            return
        patient_id = urllib.parse.unquote(m.group(1))
        self._handle_patch_intake(patient_id)

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
            if not isinstance(code_payload, dict) and not code_text:
                self._write_json(
                    {"ok": False, "error": {"code": "VALIDATION_ERROR", "message": "Either payload.code (object) or payload.codeText (string) is required."}},
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
                            "code": str(payload.get("clinicalStatus", "active")),
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
