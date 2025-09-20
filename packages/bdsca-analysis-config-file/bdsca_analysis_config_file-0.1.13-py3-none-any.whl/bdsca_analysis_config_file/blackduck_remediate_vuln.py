import sys
from typing import Any, Optional


class BlackDuckRemediator:
    last_error: Optional[str]
    _purl_cache: dict[str, Any]
    _purl_component_cache: dict[str, tuple[str, str, str]]
    _nv_component_cache: dict[tuple[str, str, str], tuple[str, str, str]]

    def __init__(
        self,
        log_level: int = 10,
        *,
        hub: Optional[Any] = None,
        base_url: Optional[str] = None,
        api_token: Optional[str] = None,
        insecure: bool = False,
        session: Optional[Any] = None,
        output_level: str = "info",
    ) -> None:
        # Logging was replaced with print statements; preserving parameter for compatibility
        lvl = (output_level or "info").lower()
        self._level = "debug" if lvl == "debug" else "info"

        def _make_debug() -> Any:
            if self._level == "debug":
                return lambda *a, **k: print("[DEBUG]", *a, **k)
            return lambda *a, **k: None

        self._debug = _make_debug()
        self._info = lambda *a, **k: print("[INFO]", *a, **k)
        self._error = lambda *a, **k: print("[ERROR]", *a, file=sys.stderr, **k)

        # Session dependency (requests-like)
        if session is None:
            try:
                import requests as _requests  # type: ignore
            except Exception as ex:  # pragma: no cover
                raise RuntimeError("Provide a session or install 'requests'") from ex
            self.session = _requests
        else:
            self.session = session

        # Hub dependency
        if hub is not None:
            self.hub = hub
        else:
            if not base_url or not api_token:
                raise ValueError("base_url and api_token are required when no hub is provided")
            # Normalize base_url, remove trailing slash
            url = base_url[:-1] if base_url.endswith("/") else base_url
            # Lazy import to avoid hard dependency during tests
            try:
                from blackduck.HubRestApi import HubInstance  # type: ignore
            except Exception as ex:  # pragma: no cover
                raise RuntimeError("Black Duck SDK not installed; pass a 'hub' instance instead") from ex
            self.hub = HubInstance(url, api_token=api_token, insecure=insecure)

        # Detailed failure reason (for CLI display)
        self.last_error = None
        # Simple in-memory caches
        self._purl_cache = {}
        self._purl_component_cache = {}
        self._nv_component_cache = {}

    def get_project_and_version_ids(self, project_name: str, project_version_name: str) -> Optional[tuple[str, str]]:
        """
        Find project and version IDs for given names using the Black Duck hub.
        Returns (project_id, project_version_id) or None if not found.
        """
        parameters = {"q": f"name:{project_name}"}
        projects = self.hub.get_projects(limit=1, parameters=parameters)
        if not projects or not projects.get("items"):
            self.last_error = f"Project not found: {project_name}"
            return None
        project = projects["items"][0]
        versions = self.__get_project_versions(project, project_version_name)
        if not versions or not versions.get("items"):
            self.last_error = f"Version not found: {project_version_name} (project {project_name})"
            return None
        version = versions["items"][0]
        project_id = project.get("_meta", {}).get("href", "").split("/")[-1]
        version_id = version.get("_meta", {}).get("href", "").split("/")[-1]
        if not project_id or not version_id:
            self.last_error = f"Could not extract project/version IDs for {project_name}/{project_version_name}"
            return None
        return (project_id, version_id)

    def check_component_exists_in_bom(
        self,
        project_name: str,
        project_version_name: str,
        component_name: str,
        component_version_name: str,
    ) -> bool:
        """
        Check if a component with the given name exists in the BOM of the specified project and version.
        Returns True if found, False otherwise. Sets last_error on failure.
        """
        ids = self.get_project_and_version_ids(project_name, project_version_name)
        if not ids:
            self._error(f"Could not resolve project/version IDs for {project_name}/{project_version_name}: {self.last_error}")
            return False
        project_id, project_version_id = ids
        base = None
        if hasattr(self.hub, "base_url") and self.hub.base_url:
            base = self.hub.base_url.rstrip("/")
        elif isinstance(getattr(self.hub, "config", None), dict):
            cfg = self.hub.config
            base = (cfg.get("baseurl") or cfg.get("url") or "").rstrip("/")
        url = f"{base}/api/projects/{project_id}/versions/{project_version_id}/components"
        headers = self.hub.get_headers()
        headers["Accept"] = "application/vnd.blackducksoftware.bill-of-materials-6+json"
        self._info("Fetching BOM components", {"url": url})
        response = self.session.get(
            url,
            headers=headers,
            verify=not self.hub.config["insecure"],
        )
        if response.status_code == 200:
            try:
                bom_data = response.json()
                for item in bom_data.get("items", []):
                    if item.get("componentName") == component_name and item.get("componentVersion") == component_version_name:
                        return True
                return False
            except Exception:
                self.last_error = "Failed to parse BOM components response JSON"
                return False
        body = getattr(response, "text", "") or getattr(response, "content", b"")
        self.last_error = f"Fetch BOM components failed ({response.status_code}): {body}"
        self._error(self.last_error)
        return False

    def add_missing_components_from_config(
        self,
        project_name: str,
        project_version_name: str,
        component_additions: list[dict],
    ) -> list[dict]:
        """
        For each component in component_additions, add to BOM if not already present.
        Resolves project and version IDs internally.
        Returns a list of results for each attempted addition.
        """
        ids = self.get_project_and_version_ids(project_name, project_version_name)
        if not ids:
            self._error(f"Could not resolve project/version IDs for {project_name}/{project_version_name}: {self.last_error}")
            return []
        project_id, project_version_id = ids
        results = []
        for entry in component_additions:
            component = entry.get("component", {})
            purl = component.get("purl")
            already_exists = False
            if purl:
                existing = self.get_component_by_purl(purl)
                print(existing)
                if existing and "items" in existing and isinstance(existing["items"], list) and len(existing["items"]) > 0:
                    existing_in_bom = self.check_component_exists_in_bom(
                        project_name, project_version_name, existing["items"][0]["componentName"], existing["items"][0]["versionName"]
                    )
                    if existing_in_bom:
                        self._info(f"Component with purl {purl} already exists in BOM, skipping.")
                        already_exists = True
            # Optionally, add more checks for name/version if needed

            if not already_exists:
                if existing and "items" in existing and isinstance(existing["items"], list) and len(existing["items"]) > 0:
                    version = existing["items"][0].get("version", "")
                else:
                    version = ""
                component_payload = {"component": version, "componentModification": "add"}
                result = self.add_component_to_bom(project_id, project_version_id, component_payload)
                results.append({"component": component, "added": bool(result), "result": result})
            else:
                results.append({"component": component, "added": False, "result": None})
        return results

    def add_component_to_bom(
        self,
        project_id: str,
        project_version_id: str,
        component_payload: dict,
    ) -> Optional[dict]:
        """
        Add a component to the BOM for a given project version.

        The payload can contain:
        {
            "component": "https://.../components/{componentId}",
            "componentPurpose": "purpose",
            "componentModified": true,
            "componentModification": "modification",
            "license": "https://.../licenses/{licenseId}"
        }

        POST /api/projects/{projectId}/versions/{projectVersionId}/components
        Content-Type: application/vnd.blackducksoftware.bill-of-materials-6+json

        Returns the response JSON on success, or None and sets last_error on failure.
        """
        base = None
        if hasattr(self.hub, "base_url") and self.hub.base_url:
            base = self.hub.base_url.rstrip("/")
        elif isinstance(getattr(self.hub, "config", None), dict):
            cfg = self.hub.config
            base = (cfg.get("baseurl") or cfg.get("url") or "").rstrip("/")
        url = f"{base}/api/projects/{project_id}/versions/{project_version_id}/components"
        headers = self.hub.get_headers()
        headers["Content-Type"] = "application/vnd.blackducksoftware.bill-of-materials-6+json"
        self._info("Adding component to BOM", {"url": url, "payload": component_payload})
        response = self.session.post(
            url,
            headers=headers,
            json=component_payload,
            verify=not self.hub.config["insecure"],
        )
        if response.status_code in (200, 201, 202):
            return {"status": "OK"}
        else:
            print(response.json())
            body = getattr(response, "text", "") or getattr(response, "content", b"")
            self.last_error = f"Add component to BOM failed ({response.status_code}): {body}"
            self._error(self.last_error)
            return None

    """
    Remediate Black Duck specific component version issue from given project and project version.
    :param projectName: Black Duck project name
    :param projectVersionName: Black Duck project version name
    :param componentName: Black Duck component name
    :param componentVersionName: Black Duck component version name
    :param componentOriginID: The ID of the component origin
    :param vulnerabilityName: Black Duckvulnerability name
    :param remediatedBy: Name who remediated vulnerability
    :param dismissStatus: Dismiss status (Original status from tool)
    :param remediationStatus: Remediation status (Changed status for Black Duck)
    :param remediationComment: Remediation comment
    """

    def __remediate(
        self,
        projectName: str,
        projectVersionName: str,
        componentName: str,
        componentVersionName: str,
        componentOriginID: Optional[str],
        vulnerabilityName: str,
        remediatedBy: str,
        dismissStatus: str,
        remediationStatus: str,
        remediationComment: str,
        *,
        dryrun: bool = False,
    ) -> bool:
        self._debug(
            "remediate with params:",
            projectName,
            projectVersionName,
            componentName,
            componentVersionName,
            vulnerabilityName,
            remediationStatus,
            remediationComment,
        )
        parameters = {"q": f"name:{projectName}"}
        projects = self.hub.get_projects(limit=1, parameters=parameters)
        if not projects or not projects.get("items"):
            self.last_error = f"Project not found: {projectName}"
            return False
        for project in projects["items"]:
            versions = self.__get_project_versions(project, projectVersionName)
            if not versions or not versions.get("items"):
                self.last_error = f"Version not found: {projectVersionName} (project {projectName})"
                continue
            for version in versions["items"]:
                headers = self.hub.get_headers()
                headers["Accept"] = "application/vnd.blackducksoftware.bill-of-materials-6+json"
                parameters = {"q": f"componentName:{componentName},vulnerabilityName:{vulnerabilityName}"}
                url = version["_meta"]["href"] + "/vulnerable-bom-components" + self.hub._get_parameter_string(parameters)
                response = self.session.get(
                    url,
                    headers=headers,
                    verify=not self.hub.config["insecure"],
                )
                if response.status_code == 200:
                    vulnComps = response.json()
                    if vulnComps["totalCount"] > 0:
                        matched = False
                        for vulnComp in vulnComps["items"]:
                            self._debug("vulnComp:", vulnComp)
                            if vulnComp["componentName"] == componentName and vulnComp["componentVersionName"] == componentVersionName:
                                # Check if component origin ID match if it is given
                                # There might be same component and same version of it from
                                # different origins
                                self._debug(f"vulnComponent: {vulnComp}")
                                if componentOriginID and vulnComp["componentVersionOriginId"] == componentOriginID:
                                    url = vulnComp["_meta"]["href"]
                                elif not componentOriginID:
                                    url = vulnComp["_meta"]["href"]
                                else:
                                    continue
                                matched = True
                                if url:
                                    response = self.session.get(
                                        url,
                                        headers=headers,
                                        verify=not self.hub.config["insecure"],
                                    )
                                    if response.status_code == 200:
                                        current: dict[str, Any] = {}
                                        try:
                                            current = response.json() or {}
                                        except Exception:
                                            current = {}
                                        # Prepare desired payload
                                        remediationData = {}
                                        remediationData["comment"] = self.__createComment(dismissStatus, remediationComment, remediatedBy)
                                        remediationData["remediationStatus"] = remediationStatus
                                        self._debug("vulnComponent:", vulnComp)

                                        if dryrun:
                                            # Print current vs new values and skip the PUT
                                            cur_status = current.get("remediationStatus", "<unknown>")
                                            cur_comment = current.get("comment", "<none>")
                                            new_status = remediationData["remediationStatus"]
                                            new_comment = remediationData["comment"]

                                            status_changed = cur_status != new_status
                                            comment_changed = cur_comment != new_comment

                                            lines = [
                                                "DRY-RUN: Would update remediation",
                                                f"  Project:     {projectName}",
                                                f"  Version:     {projectVersionName}",
                                                (f"  Component:   {componentName} " f"({componentVersionName})"),
                                                f"  Vulnerability: {vulnerabilityName}",
                                                "  Current:",
                                                f"    - status:  {cur_status}",
                                                f"    - comment: {cur_comment}",
                                                "  New:",
                                                f"    - status:  {new_status}",
                                                f"    - comment: {new_comment}",
                                            ]
                                            if not status_changed and not comment_changed:
                                                lines.append("  Note: No change needed (already up-to-date).")
                                            self._info("\n".join(lines))
                                            return True

                                        self._info(
                                            "Updating remediation status",
                                            {
                                                "project": projectName,
                                                "version": projectVersionName,
                                                "component": componentName,
                                                "componentVersion": componentVersionName,
                                                "vulnerability": vulnerabilityName,
                                                "status": remediationStatus,
                                            },
                                        )
                                        response = self.session.put(
                                            url,
                                            headers=headers,
                                            json=remediationData,
                                            verify=not self.hub.config["insecure"],
                                        )
                                        if response.status_code == 202:
                                            self._info(
                                                "Remediation succeeded",
                                                {
                                                    "component": componentName,
                                                    "componentVersion": componentVersionName,
                                                    "vulnerability": vulnerabilityName,
                                                },
                                            )
                                            return True
                                        else:
                                            body = getattr(response, "text", "") or getattr(response, "content", b"")
                                            msg = "Remediation status update failed " f"({response.status_code}): {body}"
                                            self._error(msg)
                                            self.last_error = msg
                                    else:
                                        msg = "Failed to fetch vulnerable BOM item " f"({response.status_code})"
                                        self._error(msg)
                                        self.last_error = msg
                        if not matched:
                            self.last_error = "No matching vulnerable component found with the specified " "name, version, and origin"
                    else:
                        msg = f"No vulnerable component found with name: {componentName} " f"and vulnerability: {vulnerabilityName}"
                        self._error(msg)
                        self.last_error = msg
                else:
                    self.last_error = f"Query vulnerable components failed ({response.status_code})"
        return False

    def __createComment(self, reason: str, comment: str, dismissedBy: str) -> str:
        policyComment = ""
        if reason:
            policyComment = f"Reason to dismiss: {reason}\n"
        if comment:
            policyComment = f"{policyComment}Comments:\n{comment}\n"
        if dismissedBy:
            policyComment = f"{policyComment}Changed by: {dismissedBy}"
        return policyComment

    def __get_project_versions(self, project: dict, projectVersionName: str) -> dict[str, Any]:
        parameters = {"q": f"versionName:{projectVersionName}", "limit": "1"}
        url = project["_meta"]["href"] + "/versions" + self.hub._get_parameter_string(parameters)
        headers = self.hub.get_headers()
        headers["Accept"] = "application/vnd.blackducksoftware.internal-1+json"
        response = self.session.get(url, headers=headers, verify=not self.hub.config["insecure"])
        jsondata = response.json()
        if isinstance(jsondata, dict):
            return jsondata
        return {}

    def get_component_by_purl(self, purl: str) -> Optional[dict[str, Any]]:
        """Fetch a component by purl using Black Duck search endpoint.

        GET /api/search/kb-purl-component
        Accept: application/vnd.blackducksoftware.component-detail-5+json

        Returns the parsed JSON on success, or None on failure and sets last_error.
        """
        if not purl:
            self.last_error = "purl must be provided"
            return None

        # Determine API root from hub configuration
        base = None
        if hasattr(self.hub, "base_url") and self.hub.base_url:
            base = self.hub.base_url.rstrip("/")
        elif isinstance(getattr(self.hub, "config", None), dict):
            cfg = self.hub.config
            base = (cfg.get("baseurl") or cfg.get("url") or "").rstrip("/")
        if not base:
            self.last_error = "Could not determine Black Duck base URL from hub"
            return None

        endpoint = f"{base}/api/search/kb-purl-component"
        # Build query string
        params = {"purl": purl}
        if hasattr(self.hub, "_get_parameter_string"):
            endpoint = endpoint + self.hub._get_parameter_string(params)
        else:
            from urllib.parse import urlencode

            endpoint = endpoint + "?" + urlencode(params)

        headers = self.hub.get_headers()
        headers["Accept"] = "application/vnd.blackducksoftware.component-detail-5+json"

        self._info("Fetching component by purl", {"purl": purl})
        resp = self.session.get(endpoint, headers=headers, verify=not self.hub.config["insecure"])
        if resp.status_code == 200:
            self._debug("Component lookup response OK")
            try:
                result = resp.json()
                if isinstance(result, dict):
                    return result
                return None
            except Exception:
                self.last_error = "Failed to parse component response JSON"
                return None
        if resp.status_code == 404:
            self.last_error = f"Component not found for purl: {purl}"
            return None
        self.last_error = f"Component lookup failed ({resp.status_code}): " f"{getattr(resp, 'text', '') or getattr(resp, 'content', b'')}"
        self._error(self.last_error)
        return None

    def _extract_component_from_purl_payload(self, payload: Any) -> tuple[str, str, str]:
        """Best-effort extraction of (name, version, originId) from PURL search payload.

        The Black Duck component detail payloads may vary by version. We try a few
        common key paths and fall back to empty strings if not found.
        """
        d = payload or {}
        if isinstance(d, dict) and d.get("items") and isinstance(d["items"], list):
            # Take first match
            d = d["items"][0] or {}

        def first(*keys: str) -> str:
            for k in keys:
                v = d.get(k)
                if isinstance(v, str) and v:
                    return v
            # Nested common shapes
            comp = d.get("component") or {}
            if isinstance(comp, dict):
                for k in keys:
                    v = comp.get(k)
                    if isinstance(v, str) and v:
                        return v
            compver = d.get("componentVersion") or {}
            if isinstance(compver, dict):
                for k in keys:
                    v = compver.get(k)
                    if isinstance(v, str) and v:
                        return v
            return ""

        name = first("componentName", "name")
        version = first("componentVersionName", "versionName", "name")

        origin = first("componentVersionOriginId", "originId")
        # Try origins array
        if not origin:
            origins = d.get("origins")
            if isinstance(origins, list) and origins:
                o0 = origins[0]
                if isinstance(o0, dict):
                    origin = o0.get("originId") or o0.get("componentVersionOriginId") or ""

        return (str(name or ""), str(version or ""), str(origin or ""))

    def remediate_component_vulnerabilities(
        self,
        project_name: str,
        project_version: str,
        component: dict,
        triages: list[dict],
        *,
        changed_by: str = "bdsca-cli",
        dryrun: bool = False,
    ) -> bool:
        """Remediate vulnerabilities for a single component (optionally via purl).

        - Resolves name/version/origin via get_component_by_purl when
          component["purl"] exists.
        - Applies remediation per triage so each vulnerability can carry its own
          resolution and comment.
        - Returns True only if all triages are successfully remediated.
        """
        self.last_error = None
        if not project_name or not project_version:
            self.last_error = "Project name/version required"
            return False
        if not isinstance(component, dict):
            self.last_error = "Component must be a dict"
            return False
        if not triages:
            self._info("No triages to remediate for component", component)
            return True

        comp_name = component.get("name") or ""
        comp_version = component.get("version") or ""
        comp_origin = component.get("origin") or ""

        purl = component.get("purl")
        # Compute a stable cache key for the component identity
        if purl:
            cached_ident = self._purl_component_cache.get(purl)
            if cached_ident:
                self._debug("Using cached PURL component identity", {"purl": purl})
                comp_name, comp_version, comp_origin = cached_ident
            else:
                # Use cache to avoid repeated searches across projects
                payload = self._purl_cache.get(purl)
                if payload is None:
                    payload = self.get_component_by_purl(purl)
                    if payload is not None:
                        self._purl_cache[purl] = payload
                if payload:
                    name, ver, origin = self._extract_component_from_purl_payload(payload)
                    comp_name = name or comp_name
                    comp_version = ver or comp_version
                    comp_origin = origin or comp_origin
                else:
                    self._info(
                        "PURL lookup failed; falling back to provided component fields",
                        {"purl": purl},
                    )
                self._purl_component_cache[purl] = (str(comp_name), str(comp_version), str(comp_origin))
        else:
            nv_key = (str(comp_name), str(comp_version), str(comp_origin))
            cached_ident = self._nv_component_cache.get(nv_key)
            if cached_ident:
                self._debug("Using cached NV component identity", {"key": nv_key})
                comp_name, comp_version, comp_origin = cached_ident
            else:
                self._nv_component_cache[nv_key] = (str(comp_name), str(comp_version), str(comp_origin))

        if not comp_name or not comp_version:
            self.last_error = "Component name/version could not be determined"
            return False

        overall = True
        for t in triages:
            if not isinstance(t, dict):
                continue
            vuln = t.get("cve") or t.get("bdsa")
            if not vuln:
                continue
            resolution = t.get("resolution") or ""
            comment = t.get("comment") or ""
            ok = self.__remediate(
                project_name,
                project_version,
                comp_name,
                comp_version,
                comp_origin,
                vuln,
                changed_by,
                resolution,
                resolution,
                comment,
                dryrun=dryrun,
            )
            if not ok:
                overall = False

        return overall
