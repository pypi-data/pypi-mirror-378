import importlib.metadata
import importlib.util
import io
import json
import os
import pkgutil
import uuid
from http import HTTPStatus
from pathlib import Path
from typing import Any

import aiofiles
import aiohttp
import nbformat
import tornado
import tornado.web
from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
from nbconvert import PythonExporter

from trainwave_jupyter.io import create_tarball


class TrainwaveConfig:
    """Configuration for Trainwave API endpoints"""

    def __init__(self):
        # Get API endpoint from environment or use default
        self.api_endpoint = os.getenv(
            "TRAINWAVE_API_ENDPOINT", "https://backend.trainwave.ai"
        )
        self.api_endpoint = self.api_endpoint.rstrip("/")

        # Check if we should use mock mode (for development/testing)
        self.use_mock = os.getenv("TRAINWAVE_USE_MOCK", "false").lower() == "true"

        # API endpoints
        self.create_session_url = f"{self.api_endpoint}/api/v1/cli/create_session/"
        self.session_status_url = f"{self.api_endpoint}/api/v1/cli/session_status/"


class RouteHandler(APIHandler):
    # The following decorator should be present on all verb methods (head, get, post,
    # patch, put, delete, options) to ensure only authorized user can request the
    # Jupyter server
    @tornado.web.authenticated
    def get(self):
        self.finish(
            json.dumps({"data": "This is /trainwave-jupyter/get-example endpoint!"})
        )


class AuthHandler(APIHandler):
    """Handler for CLI-style authentication operations"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trainwave_config = TrainwaveConfig()

    @tornado.web.authenticated
    async def post(self):
        """Handle authentication session creation and status checking"""
        try:
            data = json.loads(self.request.body.decode("utf-8"))
            path = self.request.path

            if path.endswith("/create_session"):
                # Create CLI authentication session
                name = data.get("name", "jupyter-extension")
                session_data = await self._create_cli_auth_session(name)
                self.finish(json.dumps(session_data))

            elif path.endswith("/session_status"):
                # Check CLI authentication session status
                token = data.get("token")
                if not token:
                    self.set_status(400)
                    self.finish(json.dumps({"error": "Missing token parameter"}))
                    return

                status_data = await self._check_cli_auth_session_status(token)
                self.finish(json.dumps(status_data))

            else:
                self.set_status(404)
                self.finish(json.dumps({"error": "Endpoint not found"}))

        except json.JSONDecodeError:
            self.set_status(400)
            self.finish(json.dumps({"error": "Invalid JSON in request body"}))
        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps({"error": f"Internal server error: {str(e)}"}))

    async def _create_cli_auth_session(self, name: str) -> dict[str, Any]:
        """Create a CLI authentication session by calling Trainwave API"""
        # If mock mode is enabled, use mock implementation
        if self.trainwave_config.use_mock:
            return self._create_mock_auth_session(name)

        try:
            async with aiohttp.ClientSession() as session:
                payload = {"name": f"Jupyter: {name}"}
                async with session.post(
                    self.trainwave_config.create_session_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {"url": data.get("url"), "token": data.get("token")}
                    else:
                        error_text = await response.text()
                        raise Exception(
                            f"API request failed with status {response.status}: {error_text}"
                        )
        except aiohttp.ClientError as e:
            # Fallback to mock mode if API is not available
            print(
                f"Warning: Trainwave API not available ({e}), falling back to mock mode"
            )
            return self._create_mock_auth_session(name)
        except Exception as e:
            # Fallback to mock mode on any other error
            print(
                f"Warning: Error calling Trainwave API ({e}), falling back to mock mode"
            )
            return self._create_mock_auth_session(name)

    async def _check_cli_auth_session_status(self, token: str) -> dict[str, Any]:
        """Check CLI authentication session status by calling Trainwave API"""
        # If mock mode is enabled, use mock implementation
        if self.trainwave_config.use_mock:
            return self._check_mock_auth_session_status(token)

        try:
            async with aiohttp.ClientSession() as session:
                payload = {"token": token}
                async with session.post(
                    self.trainwave_config.session_status_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    # Handle HTTP status codes exactly like the Django endpoint
                    if response.status == HTTPStatus.ACCEPTED.value:  # 202
                        # 202 Accepted means authentication is still pending
                        # Django returns empty body with 202 status
                        return {"status": "NOT_COMPLETED"}
                    elif response.status == HTTPStatus.OK.value:  # 200
                        # 200 OK means authentication completed successfully
                        # Django returns {"api_token": "uuid"} with 200 status
                        data = await response.json()
                        api_token = data.get("api_token")
                        return {
                            "status": "SUCCESS",
                            "api_token": api_token,
                        }
                    elif response.status == HTTPStatus.NOT_FOUND.value:  # 404
                        # 404 Not Found means session doesn't exist
                        # Django returns empty body with 404 status
                        return {"status": "NOT_FOUND"}
                    else:
                        # Any other status code is an error
                        error_text = await response.text()
                        raise Exception(
                            f"API request failed with status {response.status}: {error_text}"
                        )
        except aiohttp.ClientError as e:
            # Fallback to mock mode if API is not available
            print(
                f"Warning: Trainwave API not available ({e}), falling back to mock mode"
            )
            return self._check_mock_auth_session_status(token)
        except Exception as e:
            # Fallback to mock mode on any other error
            print(
                f"Warning: Error calling Trainwave API ({e}), falling back to mock mode"
            )
            return self._check_mock_auth_session_status(token)

    def _create_mock_auth_session(self, name: str) -> dict[str, Any]:
        """Create a mock CLI authentication session for development/testing"""
        session_token = str(uuid.uuid4())
        session_url = f"https://trainwave.ai/auth/cli?token={session_token}&name={name}"
        return {"url": session_url, "token": session_token}

    def _check_mock_auth_session_status(self, token: str) -> dict[str, Any]:
        """Check mock CLI authentication session status for development/testing"""
        # Simulate different states based on token for testing
        if token.endswith("_completed"):
            # Simulate successful authentication
            api_token = f"api_token_{token[:8]}"
            return {"status": "SUCCESS", "api_token": api_token}
        elif token.endswith("_not_found"):
            # Simulate session not found
            return {"status": "NOT_FOUND"}
        else:
            # Simulate pending authentication (most common case)
            return {"status": "NOT_COMPLETED"}


class TrainwaveAPIHandler(APIHandler):
    """Handler for Trainwave API endpoints"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trainwave_config = TrainwaveConfig()

    @tornado.web.authenticated
    async def get(self):
        """Handle GET requests to API endpoints"""
        try:
            path = self.request.path

            if path.endswith("/api/users/me"):
                # Get current user information
                api_key = self.request.headers.get("X-Api-Key")
                if not api_key:
                    self.set_status(401)
                    self.finish(json.dumps({"error": "API key required"}))
                    return

                user_data = await self._get_user_info(api_key)
                self.finish(json.dumps(user_data))

            elif path.endswith("/api/organizations"):
                # List organizations
                api_key = self.request.headers.get("X-Api-Key")
                if not api_key:
                    self.set_status(401)
                    self.finish(json.dumps({"error": "API key required"}))
                    return

                orgs_data = await self._list_organizations(api_key)
                self.finish(json.dumps({"results": orgs_data}))

            elif path.endswith("/api/projects"):
                api_key = self.request.headers.get("X-Api-Key")
                if not api_key:
                    self.set_status(401)
                    self.finish(json.dumps({"error": "API key required"}))
                    return

                if self.request.method == "GET":
                    # List projects
                    projects_data = await self._list_projects(api_key)
                    self.finish(json.dumps({"results": projects_data}))
                elif self.request.method == "POST":
                    # Create project
                    try:
                        project_data = json.loads(self.request.body.decode("utf-8"))
                        created_project = await self._create_project(
                            api_key, project_data
                        )
                        self.finish(json.dumps(created_project))
                    except json.JSONDecodeError:
                        self.set_status(400)
                        self.finish(json.dumps({"error": "Invalid JSON"}))
                    except Exception as e:
                        self.set_status(500)
                        self.finish(json.dumps({"error": str(e)}))
                else:
                    self.set_status(405)
                    self.finish(json.dumps({"error": "Method not allowed"}))

            elif path.startswith("/trainwave-jupyter/api/jobs"):
                # List jobs
                api_key = self.request.headers.get("X-Api-Key")
                if not api_key:
                    self.set_status(401)
                    self.finish(json.dumps({"error": "API key required"}))
                    return

                # Extract organization ID and project ID from query parameters
                org_id = self.get_argument("org", None)
                project_id = self.get_argument("project", None)
                jobs_data = await self._list_jobs(api_key, org_id, project_id)
                self.finish(json.dumps(jobs_data))

            elif path.endswith("/api/offers"):
                # List GPU offers
                api_key = self.request.headers.get("X-Api-Key")
                if not api_key:
                    self.set_status(401)
                    self.finish(json.dumps({"error": "API key required"}))
                    return

                offers_data = await self._fetch_offers(api_key)
                self.finish(json.dumps(offers_data))

            else:
                self.set_status(404)
                self.finish(json.dumps({"error": "API endpoint not found"}))

        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps({"error": f"Internal server error: {str(e)}"}))

    async def post(self):
        """Handle POST requests to API endpoints"""
        try:
            path = self.request.path

            if path.endswith("/api/projects"):
                api_key = self.request.headers.get("X-Api-Key")
                if not api_key:
                    self.set_status(401)
                    self.finish(json.dumps({"error": "API key required"}))
                    return

                # Create project
                try:
                    project_data = json.loads(self.request.body.decode("utf-8"))
                    created_project = await self._create_project(api_key, project_data)
                    self.finish(json.dumps(created_project))
                except json.JSONDecodeError:
                    self.set_status(400)
                    self.finish(json.dumps({"error": "Invalid JSON"}))
                except Exception as e:
                    self.set_status(500)
                    self.finish(json.dumps({"error": str(e)}))
            else:
                self.set_status(404)
                self.finish(json.dumps({"error": "API endpoint not found"}))

        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps({"error": f"Internal server error: {str(e)}"}))

    async def _get_user_info(self, api_key: str) -> dict[str, Any]:
        """Get user information from Trainwave API"""
        if self.trainwave_config.use_mock:
            return self._get_mock_user_info(api_key)

        try:
            async with aiohttp.ClientSession() as session:
                headers = {"X-Api-Key": api_key}
                async with session.get(
                    f"{self.trainwave_config.api_endpoint}/api/v1/users/me/",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        raise Exception(
                            f"API request failed with status {response.status}: {error_text}"
                        )
        except Exception as e:
            print(
                f"Warning: Error calling Trainwave API ({e}), falling back to mock mode"
            )
            return self._get_mock_user_info(api_key)

    async def _list_organizations(self, api_key: str) -> list[dict[str, Any]]:
        """List organizations from Trainwave API"""
        if self.trainwave_config.use_mock:
            return self._get_mock_organizations()

        try:
            async with aiohttp.ClientSession() as session:
                headers = {"X-Api-Key": api_key}
                async with session.get(
                    f"{self.trainwave_config.api_endpoint}/api/v1/organizations/",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("results", [])
                    else:
                        error_text = await response.text()
                        raise Exception(
                            f"API request failed with status {response.status}: {error_text}"
                        )
        except Exception as e:
            print(
                f"Warning: Error calling Trainwave API ({e}), falling back to mock mode"
            )
            return self._get_mock_organizations()

    async def _list_projects(self, api_key: str) -> list[dict[str, Any]]:
        """List projects from Trainwave API"""
        if self.trainwave_config.use_mock:
            return self._get_mock_projects()

        try:
            async with aiohttp.ClientSession() as session:
                headers = {"X-Api-Key": api_key}
                async with session.get(
                    f"{self.trainwave_config.api_endpoint}/api/v1/projects/",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("results", [])
                    else:
                        error_text = await response.text()
                        raise Exception(
                            f"API request failed with status {response.status}: {error_text}"
                        )
        except Exception as e:
            print(
                f"Warning: Error calling Trainwave API ({e}), falling back to mock mode"
            )
            return self._get_mock_projects()

    async def _create_project(self, api_key: str, project_data: dict) -> dict[str, Any]:
        """Create a new project via Trainwave API"""
        if self.trainwave_config.use_mock:
            return self._get_mock_created_project(project_data)

        try:
            async with aiohttp.ClientSession() as session:
                headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}
                async with session.post(
                    f"{self.trainwave_config.api_endpoint}/api/v1/projects/",
                    headers=headers,
                    json=project_data,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    if response.status in [200, 201]:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        raise Exception(
                            f"API request failed with status {response.status}: {error_text}"
                        )
        except Exception as e:
            print(
                f"Warning: Error calling Trainwave API ({e}), falling back to mock mode"
            )
            return self._get_mock_created_project(project_data)

    def _get_mock_user_info(self, api_key: str) -> dict[str, Any]:
        """Get mock user information"""
        return {
            "id": "mock-user-id",
            "rid": "mock-user-rid",
            "email": "user@example.com",
            "first_name": "Jupyter",
            "last_name": "User",
        }

    def _get_mock_organizations(self) -> list[dict[str, Any]]:
        """Get mock organizations"""
        return [
            {
                "id": "org-1",
                "rid": "org-rid-1",
                "name": "Default Organization",
                "computed_credit_balance": 1000,
            }
        ]

    def _get_mock_projects(self) -> list[dict[str, Any]]:
        """Get mock projects"""
        return [{"id": "proj-1", "rid": "proj-rid-1", "name": "My First Project"}]

    def _get_mock_created_project(self, project_data: dict) -> dict[str, Any]:
        """Get mock created project response"""
        import uuid

        project_id = str(uuid.uuid4())
        return {
            "id": project_id,
            "rid": f"proj-{project_id[:8]}",
            "name": project_data.get("name", "New Project"),
            "active_job_count": 0,
            "total_job_count": 0,
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            "organization": project_data.get("organization", ""),
            "users": [],
        }

    async def _list_jobs(
        self, api_key: str, organization_id: str = None, project_id: str = None
    ) -> dict[str, Any]:
        """List jobs for the organization"""
        if self.trainwave_config.use_mock:
            return self._get_mock_jobs()

        try:
            async with aiohttp.ClientSession() as session:
                headers = {"X-Api-Key": api_key}
                path = f"{self.trainwave_config.api_endpoint}/api/v1/jobs/"

                params = {}
                if organization_id:
                    params["org"] = organization_id
                if project_id:
                    params["project"] = project_id

                if params:
                    path += f"?{'&'.join([f'{k}={v}' for k, v in params.items()])}"

                print("DANCE")
                print(f"PATH: {path}")

                async with session.get(
                    path,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        raise Exception(
                            f"API request failed with status {response.status}: {error_text}"
                        )
        except Exception as e:
            print(
                f"Warning: Error calling Trainwave API ({e}), falling back to mock mode"
            )
            return self._get_mock_jobs()

    def _get_mock_jobs(self) -> dict[str, Any]:
        """Get mock jobs data"""
        return {
            "results": [
                {
                    "id": "job-1",
                    "rid": "rid-1",
                    "state": "RUNNING",
                    "s3_url": "s3://bucket/job-1",
                    "project": {
                        "id": "proj-1",
                        "rid": "proj-rid-1",
                        "name": "Test Project",
                    },
                    "cloud_offer": {
                        "cpus": 4,
                        "memory_mb": 8192,
                        "compliance_soc2": True,
                        "gpu_type": "A100",
                        "gpu_memory_mb": 40960,
                        "gpus": 1,
                    },
                    "cost_per_hour": 2.50,
                    "config": {
                        "id": "config-1",
                        "rid": "config-rid-1",
                        "name": "BERT Fine-tuning",
                        "expires_at": -1,
                        "cpus": 4,
                        "gpus": 1,
                        "gpu_type": "A100",
                    },
                    "created_at": "2024-01-15T10:30:00Z",
                    "total_cost": 125,
                    "upload_url": "",
                    "url": "https://job-1.trainwave.ai",
                },
                {
                    "id": "job-2",
                    "rid": "rid-2",
                    "state": "SUCCESS",
                    "s3_url": "s3://bucket/job-2",
                    "project": {
                        "id": "proj-1",
                        "rid": "proj-rid-1",
                        "name": "Test Project",
                    },
                    "cloud_offer": {
                        "cpus": 2,
                        "memory_mb": 4096,
                        "compliance_soc2": True,
                        "gpu_type": "V100",
                        "gpu_memory_mb": 16384,
                        "gpus": 1,
                    },
                    "cost_per_hour": 1.25,
                    "config": {
                        "id": "config-2",
                        "rid": "config-rid-2",
                        "name": "Image Classification",
                        "expires_at": -1,
                        "cpus": 2,
                        "gpus": 1,
                        "gpu_type": "V100",
                    },
                    "created_at": "2024-01-15T08:15:00Z",
                    "total_cost": 45,
                    "upload_url": "",
                    "url": None,
                },
            ]
        }

    async def _fetch_offers(self, api_key: str) -> dict[str, Any]:
        """Fetch GPU offers from Trainwave API"""
        if self.trainwave_config.use_mock:
            return self._get_mock_offers()

        try:
            async with aiohttp.ClientSession() as session:
                headers = {"X-Api-Key": api_key}
                path = f"{self.trainwave_config.api_endpoint}/api/v1/offers/"

                async with session.get(
                    path,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    if response.status == 200:
                        return {"results": await response.json()}
                    else:
                        error_text = await response.text()
                        raise Exception(
                            f"API request failed with status {response.status}: {error_text}"
                        )
        except Exception as e:
            print(
                f"Warning: Error calling Trainwave API ({e}), falling back to mock mode"
            )
            return self._get_mock_offers()

    def _get_mock_offers(self) -> dict[str, Any]:
        """Get mock offers data"""
        return {
            "results": [
                {
                    "id": "offer-1",
                    "offer": 2.3,
                    "cpus": 28,
                    "memory_mb": 184320,
                    "gpus": 1,
                    "gpu_type": "NVIDIA-A100-80GB",
                    "gpu_memory_mb": 81920,
                    "compliance_soc2": True,
                    "tflops": 312.0,
                    "grade": "ENTERPRISE",
                },
                {
                    "id": "offer-2",
                    "offer": 3.1,
                    "cpus": 28,
                    "memory_mb": 184320,
                    "gpus": 1,
                    "gpu_type": "NVIDIA-H100-80GB",
                    "gpu_memory_mb": 81920,
                    "compliance_soc2": True,
                    "tflops": 1979.0,
                    "grade": "ENTERPRISE",
                },
                {
                    "id": "offer-3",
                    "offer": 0.5,
                    "cpus": 24,
                    "memory_mb": 16384,
                    "gpus": 1,
                    "gpu_type": "NVIDIA-V100-16GB",
                    "gpu_memory_mb": 16384,
                    "compliance_soc2": False,
                    "tflops": 14.0,
                    "grade": "ENTERPRISE",
                },
            ]
        }


class LaunchJobHandler(APIHandler):
    """Handler for launching training jobs from notebook content"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trainwave_config = TrainwaveConfig()

    @tornado.web.authenticated
    async def post(self):
        """Handle launch job requests"""
        try:
            # Parse request body to get notebook path, project_id, and settings
            data = json.loads(self.request.body.decode("utf-8"))
            notebook_path = data.get("notebook_path")
            project_id = data.get("project_id", "default")
            gpu_type = data.get("gpu_type", "CPU")
            gpu_count = data.get("gpu_count", 1)
            job_name = data.get("job_name")

            print(f"NOTEBOOK PATH: {notebook_path}")
            print(f"GPU TYPE: {gpu_type}")
            print(f"GPU COUNT: {gpu_count}")

            # Get the current notebook content
            notebook_content = await self._get_current_notebook_content(notebook_path)

            # Get installed packages
            installed_packages = await self._get_installed_packages()

            if not any(package.startswith("ipython") for package in installed_packages):
                installed_packages.append("ipython")

            print(f"INSTALLED PACKAGES: {installed_packages}")

            notebook_name = await self._get_notebook_name(notebook_path)
            print(f"NOTEBOOK NAME: {notebook_name}")
            print(f"JOB NAME: {job_name}")

            # Use provided job name or fallback to notebook-based name
            final_job_name = job_name if job_name else f"Jupyter - {notebook_name}"

            tarball = None
            requirements_file = f"{uuid.uuid4()}_requirements.txt"
            setup_script = f"{uuid.uuid4()}_setup.sh"
            run_script = f"{uuid.uuid4()}_run.sh"
            temp_code_file = f"{uuid.uuid4()}_code.ipy"

            # Configure job based on user settings
            if "cpu" in gpu_type.lower():
                # CPU-only configuration
                job_cpus = gpu_count  # Use gpu_count as CPU count for CPU jobs
                job_gpus = 0
                job_gpu_type = ""
            else:
                # GPU configuration
                job_cpus = 1  # Default CPU count for GPU jobs
                job_gpus = gpu_count
                job_gpu_type = gpu_type

            job_config = {
                "name": final_job_name,
                "image": "trainwave/pytorch:2.3.1",
                "setup_command": f"bash {setup_script}",
                "run_command": f"bash {run_script}",
                "hdd_size_mb": 2048,
                "memory_mb": 0,
                "cpus": job_cpus,
                "gpus": job_gpus,
                "gpu_type": job_gpu_type,
                "env_vars": {},
            }
            print(f"JOB CONFIG: {job_config}")
            try:
                print(f"Using project ID: {project_id}")

                job = await self._create_job(job_config, project_id)
                print(f"✅ Job created successfully: {job.get('id', 'Unknown ID')}")

                in_memory_files = [
                    (
                        requirements_file,
                        io.BytesIO("\n".join(installed_packages).encode("utf-8")),
                    ),
                    (
                        setup_script,
                        io.BytesIO(f"pip install -r {requirements_file}".encode()),
                    ),
                    (
                        run_script,
                        io.BytesIO(f"ipython {temp_code_file}".encode()),
                    ),
                    (temp_code_file, io.BytesIO(notebook_content.encode("utf-8"))),
                ]
                print(f"In memory files: {in_memory_files}")

                tarball = create_tarball(
                    Path().cwd(),
                    exclude_gitignore=True,
                    exclude_regex=None,
                    show_progress_bar=False,
                    in_memory_files=in_memory_files,
                )

                await self._upload_code(Path(tarball.name), job["upload_url"])
                await self._code_submission(job["id"])

                return self.finish(
                    json.dumps(
                        {
                            "status": "success",
                            "message": "Job launched successfully",
                            "job": job,
                        }
                    )
                )
            except Exception as e:
                print(f"❌ Failed to create job: {str(e)}")
                # Continue with the rest of the process even if job creation fails
            finally:
                if tarball:
                    tarball.close()
        except Exception as e:
            print(f"Error in launch job handler: {str(e)}")
            self.set_status(500)
            self.finish(json.dumps({"error": f"Failed to launch job: {str(e)}"}))

        return self.finish(json.dumps({"error": "Failed to launch job"}))

    async def _get_current_notebook_content(self, notebook_path: str = None) -> str:
        """Extract all code from the current notebook as a single Python script"""
        try:
            if not notebook_path:
                return self._get_placeholder_code()

            # Convert notebook to Python using nbconvert
            python_code = self._convert_notebook_to_python(notebook_path)
            print(
                f"Successfully converted notebook to Python: {len(python_code)} characters"
            )
            return python_code

        except Exception as e:
            print(f"Error getting notebook content: {str(e)}")
            return self._get_placeholder_code()

    def _get_placeholder_code(self) -> str:
        """Return placeholder code when notebook path is not available"""
        return """# This would be the combined code from all notebook cells
# In a real implementation, this would extract:
# 1. All code cells from the current notebook
# 2. Remove markdown cells and outputs
# 3. Combine imports at the top
# 4. Maintain execution order

# Example of what the extracted code might look like:
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Cell 1: Data loading
data = pd.read_csv('data.csv')

# Cell 2: Data preprocessing
data_clean = data.dropna()

# Cell 3: Model training
from sklearn.linear_model import LinearRegression
model = LinearRegression()
model.fit(data_clean[['feature1', 'feature2']], data_clean['target'])

# Cell 4: Predictions
predictions = model.predict(data_clean[['feature1', 'feature2']])

# Cell 5: Visualization
plt.figure(figsize=(10, 6))
plt.scatter(data_clean['target'], predictions)
plt.xlabel('Actual')
plt.ylabel('Predicted')
plt.title('Model Performance')
plt.show()

print("Training completed successfully!")
"""

    async def _get_notebook_name(self, notebook_path: str) -> str:
        """Get the name of the notebook"""
        return os.path.basename(notebook_path).replace(".ipynb", "")

    def _convert_notebook_to_python(self, notebook_path: str) -> str:
        """Convert notebook to Python code using nbconvert"""
        try:
            # Resolve the notebook path
            resolved_path = self._resolve_notebook_path(notebook_path)
            if not resolved_path:
                return f"# Error: Could not find notebook at {notebook_path}"

            # Read the notebook using nbformat
            nb = nbformat.read(resolved_path, as_version=4)

            # Convert to Python using nbconvert
            exporter = PythonExporter(exclude_markdown=True)
            py_code, _ = exporter.from_notebook_node(nb)

            return py_code

        except Exception as e:
            return f"# Error converting notebook to Python: {str(e)}"

    def _resolve_notebook_path(self, notebook_path: str) -> str | None:
        """Resolve the notebook path to an absolute path"""
        try:
            # Get the Jupyter server root directory
            server_root = self.settings.get("server_root_dir", ".")
            print(f"Server root directory: {server_root}")
            print(f"Original notebook path: {notebook_path}")

            # Handle different path formats
            if notebook_path.startswith("/"):
                # Absolute path
                full_path = notebook_path
            elif notebook_path.startswith("~/"):
                # Home directory path
                full_path = os.path.expanduser(notebook_path)
            else:
                # Relative path - join with server root
                full_path = os.path.join(server_root, notebook_path)

            # Normalize the path
            full_path = os.path.normpath(full_path)
            print(f"Resolved notebook path: {full_path}")

            # Check if file exists
            if not os.path.exists(full_path):
                print(f"Notebook file not found: {full_path}")
                # Try alternative locations
                alternative_paths = [
                    os.path.join(
                        os.getcwd(), notebook_path
                    ),  # Current working directory
                    os.path.join(server_root, notebook_path),  # Server root
                    notebook_path,  # As-is
                ]

                for alt_path in alternative_paths:
                    alt_path = os.path.normpath(alt_path)
                    print(f"Trying alternative path: {alt_path}")
                    if os.path.exists(alt_path):
                        full_path = alt_path
                        print(f"Found notebook at alternative path: {full_path}")
                        break
                else:
                    print("Notebook not found in any location")
                    return None

            print(f"Successfully resolved notebook path: {full_path}")
            return full_path

        except Exception as e:
            print(f"Error resolving notebook path {notebook_path}: {str(e)}")
            return None

    async def _build_setup_script(
        self, installed_packages: list[str]
    ) -> tuple[str, str]:
        """Build a setup script for the installed packages"""
        temp_file = f"{uuid.uuid4()}_requirements.txt"
        setup_script = f"""#!/bin/bash
pip install -r {temp_file}
        """
        return setup_script, temp_file

    async def _upload_code(self, tarball: Path, presigned_url: str) -> None:
        """Upload code tarball to presigned URL"""
        try:
            size = tarball.stat().st_size
            print(f"Uploading tarball of size: {size} bytes")

            async def file_chunk_iterator(filename):
                async with aiofiles.open(filename, "rb") as file:
                    while True:
                        chunk = await file.read(64 * 1024)
                        if not chunk:
                            break
                        yield chunk

            async with aiohttp.ClientSession() as session:
                headers = {
                    "Content-Type": "application/gzip",
                    "Content-Length": str(size),
                }
                response = await session.put(
                    presigned_url, headers=headers, data=file_chunk_iterator(tarball)
                )
                response.raise_for_status()
                print("✅ Code uploaded successfully")

        except Exception as e:
            print(f"❌ Failed to upload code: {str(e)}")
            raise e

    async def _code_submission(self, job_id: str) -> None:
        """Submit code for the job"""
        try:
            # Get API key from request headers
            api_key = self.request.headers.get("X-Api-Key")
            if not api_key:
                raise Exception("API key required for code submission")

            # Make the API request to submit code
            async with aiohttp.ClientSession() as session:
                headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}

                url = f"{self.trainwave_config.api_endpoint}/api/v1/jobs/{job_id}/code_submission/"

                async with session.post(
                    url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    if response.status == 200 or response.status == 201:
                        result = await response.json()
                        print(f"✅ Code submitted successfully for job {job_id}")
                        return result
                    else:
                        error_text = await response.text()
                        raise Exception(
                            f"Failed to submit code. Status: {response.status}, Error: {error_text}"
                        )

        except Exception as e:
            print(f"❌ Failed to submit code: {str(e)}")
            raise e

    async def _create_job(self, job_config: dict, project_id: str) -> dict:
        """Create a job on Trainwave API"""
        try:
            # Get API key from request headers
            api_key = self.request.headers.get("X-Api-Key")
            if not api_key:
                raise Exception("API key required for job creation")

            # Prepare the request payload
            payload = {
                "project": project_id,
                "config": job_config,
            }

            print(f"Creating job with config: {job_config}")

            # Make the API request
            async with aiohttp.ClientSession() as session:
                headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}

                url = f"{self.trainwave_config.api_endpoint}/api/v1/jobs/"

                async with session.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    if response.status == 200 or response.status == 201:
                        job_data = await response.json()
                        print(f"Job created successfully: {job_data}")
                        return job_data
                    else:
                        error_text = await response.text()
                        raise Exception(
                            f"Failed to create job. Status: {response.status}, Error: {error_text}"
                        )

        except Exception as e:
            print(f"Error creating job: {str(e)}")
            raise e

    async def _get_installed_packages(self) -> list[str]:
        packages = []

        # Get all modules that can be imported
        for _importer, modname, _ispkg in pkgutil.iter_modules():
            try:
                spec = importlib.util.find_spec(modname)
                if spec is not None:
                    version = "unknown"
                    try:
                        # Try to get version using importlib.metadata
                        version = importlib.metadata.version(modname)
                    except (importlib.metadata.PackageNotFoundError, Exception):
                        # Try alternative module names or skip version
                        pass
                    packages.append((modname, version))
            except (ImportError, ValueError, ModuleNotFoundError):
                # Skip modules that can't be imported
                continue

        # Only care about non-system packages (i.e. not in the standard library)
        return [
            f"{package}=={version}"
            for package, version in packages
            if version != "unknown"
            and package not in ("trainwave", "trainwave-jupyter")
        ]


def setup_handlers(web_app):
    host_pattern = ".*$"

    base_url = web_app.settings["base_url"]

    # Original example route
    route_pattern = url_path_join(base_url, "trainwave-jupyter", "get-example")

    # Auth routes
    auth_create_session_pattern = url_path_join(
        base_url, "trainwave-jupyter", "auth", "create_session"
    )
    auth_session_status_pattern = url_path_join(
        base_url, "trainwave-jupyter", "auth", "session_status"
    )

    # API routes
    api_users_me_pattern = url_path_join(
        base_url, "trainwave-jupyter", "api", "users", "me"
    )
    api_organizations_pattern = url_path_join(
        base_url, "trainwave-jupyter", "api", "organizations"
    )
    api_projects_pattern = url_path_join(
        base_url, "trainwave-jupyter", "api", "projects"
    )
    api_jobs_pattern = url_path_join(base_url, "trainwave-jupyter", "api", "jobs")
    api_offers_pattern = url_path_join(base_url, "trainwave-jupyter", "api", "offers")

    # Launch job route
    launch_job_pattern = url_path_join(base_url, "trainwave-jupyter", "launch-job")

    handlers = [
        (route_pattern, RouteHandler),
        (auth_create_session_pattern, AuthHandler),
        (auth_session_status_pattern, AuthHandler),
        (api_users_me_pattern, TrainwaveAPIHandler),
        (api_organizations_pattern, TrainwaveAPIHandler),
        (api_projects_pattern, TrainwaveAPIHandler),
        (api_jobs_pattern, TrainwaveAPIHandler),
        (api_offers_pattern, TrainwaveAPIHandler),
        (launch_job_pattern, LaunchJobHandler),
    ]
    web_app.add_handlers(host_pattern, handlers)
