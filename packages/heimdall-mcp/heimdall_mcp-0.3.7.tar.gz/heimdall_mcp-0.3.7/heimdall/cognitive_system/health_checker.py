"""
Comprehensive health checking system for cognitive memory components.

This module provides systematic verification of all system dependencies,
configuration, and runtime health of the cognitive memory system.
"""

import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import psutil
import requests
from rich.console import Console

from .service_manager import QdrantManager, ServiceStatus


class HealthResult(Enum):
    """Health check result status."""

    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class HealthCheck:
    """Individual health check result."""

    name: str
    status: HealthResult
    message: str
    details: dict[str, Any] | None = None
    fix_attempted: bool = False
    fix_successful: bool = False


@dataclass
class HealthCheckResults:
    """Complete health check results."""

    overall_status: HealthResult
    checks: list[HealthCheck] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


class HealthChecker:
    """
    Comprehensive health checker for cognitive memory system.

    Performs systematic verification of:
    - System dependencies and environment
    - Service availability and health
    - Configuration validity
    - Resource availability
    - Runtime performance
    """

    def __init__(self, config_path: str | None = None):
        """
        Initialize health checker.

        Args:
            config_path: Optional path to configuration file
        """
        self.config_path = config_path
        self.console = Console()
        self.qdrant_manager = QdrantManager()
        self._is_container = self._detect_container_environment()

    def _detect_container_environment(self) -> bool:
        """Detect if running inside a container."""
        # Check for common container indicators
        container_indicators = [
            os.path.exists("/.dockerenv"),
            os.path.exists("/proc/1/cgroup")
            and "docker" in open("/proc/1/cgroup").read(),
            os.environ.get("CONTAINER") is not None,
            os.environ.get("PROJECT_ID") is not None,  # Our container sets this
        ]
        return any(container_indicators)

    def run_all_checks(
        self,
        verbose: bool = False,
        fix_issues: bool = False,
    ) -> HealthCheckResults:
        """
        Run comprehensive health checks.

        Args:
            verbose: Include detailed diagnostic information
            fix_issues: Attempt to fix detected issues

        Returns:
            HealthCheckResults: Complete health check results
        """
        results = HealthCheckResults(overall_status=HealthResult.HEALTHY)

        # Run all health checks
        check_methods = [
            self._check_python_environment,
            self._check_dependencies,
            self._check_system_resources,
            self._check_docker_availability,
            self._check_qdrant_service,
            self._check_monitoring_service,
            self._check_data_directories,
            self._check_configuration,
            self._check_model_availability,
            self._check_network_connectivity,
            self._check_performance_baseline,
        ]

        for check_method in check_methods:
            try:
                check_result = check_method(verbose=verbose, fix_issues=fix_issues)
                results.checks.append(check_result)

                # Update overall status
                if check_result.status == HealthResult.CRITICAL:
                    results.overall_status = HealthResult.CRITICAL
                elif (
                    check_result.status == HealthResult.WARNING
                    and results.overall_status != HealthResult.CRITICAL
                ):
                    results.overall_status = HealthResult.WARNING

            except Exception as e:
                # Add error as critical check failure
                error_check = HealthCheck(
                    name=check_method.__name__,
                    status=HealthResult.CRITICAL,
                    message=f"Check failed with error: {str(e)}",
                    details={"exception": str(e)},
                )
                results.checks.append(error_check)
                results.overall_status = HealthResult.CRITICAL

        # Generate recommendations
        results.recommendations = self._generate_recommendations(results.checks)

        return results

    def _check_python_environment(
        self,
        verbose: bool = False,
        fix_issues: bool = False,
    ) -> HealthCheck:
        """Check Python environment and version."""
        try:
            python_version = sys.version_info
            required_version = (3, 13)

            if python_version >= required_version:
                details = None
                if verbose:
                    details = {
                        "python_version": f"{python_version.major}.{python_version.minor}.{python_version.micro}",
                        "executable": sys.executable,
                        "platform": sys.platform,
                    }

                return HealthCheck(
                    name="Python Environment",
                    status=HealthResult.HEALTHY,
                    message=f"Python {python_version.major}.{python_version.minor} is compatible",
                    details=details,
                )
            else:
                return HealthCheck(
                    name="Python Environment",
                    status=HealthResult.CRITICAL,
                    message=f"Python {required_version[0]}.{required_version[1]}+ required, found {python_version.major}.{python_version.minor}",
                    details={
                        "required": f"{required_version[0]}.{required_version[1]}+",
                        "found": f"{python_version.major}.{python_version.minor}.{python_version.micro}",
                    },
                )

        except Exception as e:
            return HealthCheck(
                name="Python Environment",
                status=HealthResult.CRITICAL,
                message=f"Failed to check Python environment: {str(e)}",
            )

    def _check_dependencies(
        self,
        verbose: bool = False,
        fix_issues: bool = False,
    ) -> HealthCheck:
        """Check required Python packages."""
        required_packages = [
            "onnxruntime",
            "tokenizers",
            "qdrant_client",
            "numpy",
            "loguru",
            "dotenv",  # python-dotenv package imports as 'dotenv'
            "pydantic",
            "typer",
            "rich",
            "docker",
        ]

        missing_packages = []
        installed_versions = {}

        for package in required_packages:
            try:
                module = __import__(package.replace("-", "_"))
                if hasattr(module, "__version__"):
                    installed_versions[package] = module.__version__
                else:
                    installed_versions[package] = "unknown"
            except ImportError:
                missing_packages.append(package)

        if missing_packages:
            message = f"Missing packages: {', '.join(missing_packages)}"

            if fix_issues:
                # Attempt to install missing packages
                import subprocess

                try:
                    subprocess.check_call(
                        [sys.executable, "-m", "pip", "install"] + missing_packages
                    )

                    return HealthCheck(
                        name="Dependencies",
                        status=HealthResult.HEALTHY,
                        message="Fixed: Installed missing packages",
                        fix_attempted=True,
                        fix_successful=True,
                    )
                except subprocess.CalledProcessError:
                    return HealthCheck(
                        name="Dependencies",
                        status=HealthResult.CRITICAL,
                        message=f"Failed to install missing packages: {', '.join(missing_packages)}",
                        fix_attempted=True,
                        fix_successful=False,
                    )
            else:
                return HealthCheck(
                    name="Dependencies",
                    status=HealthResult.CRITICAL,
                    message=message,
                    details={"missing": missing_packages},
                )

        details = None
        if verbose:
            details = {"installed_versions": installed_versions}

        return HealthCheck(
            name="Dependencies",
            status=HealthResult.HEALTHY,
            message="All required packages are installed",
            details=details,
        )

    def _check_system_resources(
        self,
        verbose: bool = False,
        fix_issues: bool = False,
    ) -> HealthCheck:
        """Check system resources (memory, disk, CPU)."""
        try:
            # Check memory
            memory = psutil.virtual_memory()
            memory_gb = memory.total / (1024**3)
            memory_available_gb = memory.available / (1024**3)

            # Check disk space
            disk = psutil.disk_usage(".")
            disk_free_gb = disk.free / (1024**3)

            # Check CPU
            cpu_count = psutil.cpu_count()

            warnings = []
            critical_issues = []

            # Memory checks
            if memory_gb < 4:
                critical_issues.append(
                    f"Low system memory: {memory_gb:.1f}GB (4GB+ recommended)"
                )
            elif memory_available_gb < 2:
                warnings.append(f"Low available memory: {memory_available_gb:.1f}GB")

            # Disk checks
            if disk_free_gb < 5:
                critical_issues.append(
                    f"Low disk space: {disk_free_gb:.1f}GB (5GB+ recommended)"
                )
            elif disk_free_gb < 10:
                warnings.append(f"Low disk space: {disk_free_gb:.1f}GB")

            # CPU checks
            if cpu_count < 2:
                warnings.append(f"Low CPU cores: {cpu_count} (2+ recommended)")

            details = None
            if verbose:
                details = {
                    "memory_total_gb": round(memory_gb, 1),
                    "memory_available_gb": round(memory_available_gb, 1),
                    "disk_free_gb": round(disk_free_gb, 1),
                    "cpu_cores": cpu_count,
                }

            if critical_issues:
                return HealthCheck(
                    name="System Resources",
                    status=HealthResult.CRITICAL,
                    message="; ".join(critical_issues),
                    details=details,
                )
            elif warnings:
                return HealthCheck(
                    name="System Resources",
                    status=HealthResult.WARNING,
                    message="; ".join(warnings),
                    details=details,
                )
            else:
                return HealthCheck(
                    name="System Resources",
                    status=HealthResult.HEALTHY,
                    message="System resources are adequate",
                    details=details,
                )

        except Exception as e:
            return HealthCheck(
                name="System Resources",
                status=HealthResult.CRITICAL,
                message=f"Failed to check system resources: {str(e)}",
            )

    def _check_docker_availability(
        self,
        verbose: bool = False,
        fix_issues: bool = False,
    ) -> HealthCheck:
        """Check Docker availability and status."""
        try:
            import docker

            try:
                client = docker.from_env()
                client.ping()

                details = None
                if verbose:
                    info = client.info()
                    details = {
                        "docker_version": info.get("ServerVersion", "unknown"),
                        "containers_running": info.get("ContainersRunning", 0),
                        "images": info.get("Images", 0),
                    }

                return HealthCheck(
                    name="Docker Availability",
                    status=HealthResult.HEALTHY,
                    message="Docker is available and accessible",
                    details=details,
                )

            except Exception as docker_error:
                # In container environments, Docker unavailability is expected
                status = (
                    HealthResult.HEALTHY if self._is_container else HealthResult.WARNING
                )
                message = (
                    "Docker unavailable in container (expected)"
                    if self._is_container
                    else f"Docker unavailable: {str(docker_error)} (will use local binary fallback)"
                )
                return HealthCheck(
                    name="Docker Availability",
                    status=status,
                    message=message,
                    details={
                        "error": str(docker_error),
                        "container_env": self._is_container,
                    },
                )

        except ImportError:
            # In container environments, Docker client not being installed is expected
            status = (
                HealthResult.HEALTHY if self._is_container else HealthResult.WARNING
            )
            message = (
                "Docker client not installed in container (expected)"
                if self._is_container
                else "Docker client not installed (will use local binary fallback)"
            )
            return HealthCheck(
                name="Docker Availability",
                status=status,
                message=message,
                details={"container_env": self._is_container},
            )

    def _check_qdrant_service(
        self,
        verbose: bool = False,
        fix_issues: bool = False,
    ) -> HealthCheck:
        """Check Qdrant service status and health."""
        try:
            status = self.qdrant_manager.get_status()

            if status.status == ServiceStatus.RUNNING:
                # Service is running, check health
                if status.health_status == "healthy":
                    details = None
                    if verbose:
                        details = {
                            "port": status.port,
                            "pid": status.pid,
                            "container_id": status.container_id,
                            "uptime_seconds": status.uptime_seconds,
                        }

                    return HealthCheck(
                        name="Qdrant Service",
                        status=HealthResult.HEALTHY,
                        message=f"Qdrant is running and healthy on port {status.port}",
                        details=details,
                    )
                else:
                    return HealthCheck(
                        name="Qdrant Service",
                        status=HealthResult.WARNING,
                        message=f"Qdrant is running but unhealthy on port {status.port}",
                        details={
                            "status": status.status.value,
                            "port": status.port,
                            "pid": status.pid,
                            "container_id": status.container_id,
                            "uptime_seconds": status.uptime_seconds,
                            "health_status": status.health_status,
                            "error": status.error,
                        },
                    )

            elif status.status == ServiceStatus.STOPPED:
                if fix_issues:
                    # Attempt to start Qdrant
                    try:
                        success = self.qdrant_manager.start(wait_timeout=15)
                        if success:
                            return HealthCheck(
                                name="Qdrant Service",
                                status=HealthResult.HEALTHY,
                                message="Fixed: Started Qdrant service",
                                fix_attempted=True,
                                fix_successful=True,
                            )
                        else:
                            return HealthCheck(
                                name="Qdrant Service",
                                status=HealthResult.CRITICAL,
                                message="Failed to start Qdrant service",
                                fix_attempted=True,
                                fix_successful=False,
                            )
                    except Exception as start_error:
                        return HealthCheck(
                            name="Qdrant Service",
                            status=HealthResult.CRITICAL,
                            message=f"Failed to start Qdrant: {str(start_error)}",
                            fix_attempted=True,
                            fix_successful=False,
                        )
                else:
                    # In container environments, not finding local Qdrant is expected
                    if self._is_container:
                        return HealthCheck(
                            name="Qdrant Service",
                            status=HealthResult.HEALTHY,
                            message="Qdrant runs in separate container (expected)",
                            details={"container_env": self._is_container},
                        )
                    else:
                        return HealthCheck(
                            name="Qdrant Service",
                            status=HealthResult.WARNING,
                            message="Qdrant service is not running (run 'memory_system qdrant start')",
                        )

            else:
                return HealthCheck(
                    name="Qdrant Service",
                    status=HealthResult.CRITICAL,
                    message=f"Qdrant service status unknown: {status.error or 'unknown error'}",
                    details={
                        "status": status.status.value,
                        "port": status.port,
                        "pid": status.pid,
                        "container_id": status.container_id,
                        "uptime_seconds": status.uptime_seconds,
                        "health_status": status.health_status,
                        "error": status.error,
                    },
                )

        except Exception as e:
            return HealthCheck(
                name="Qdrant Service",
                status=HealthResult.CRITICAL,
                message=f"Failed to check Qdrant service: {str(e)}",
            )

    def _check_monitoring_service(
        self,
        verbose: bool = False,
        fix_issues: bool = False,
    ) -> HealthCheck:
        """Check monitoring service status and health."""
        try:
            # Use the same health check logic as the monitor_health command
            from heimdall.cognitive_system.monitoring_service import (
                MonitoringService,
                MonitoringServiceError,
            )

            service = MonitoringService()
            health = service.health_check()

            if health["status"] == "healthy":
                details = None
                if verbose:
                    details = {
                        "health_checks": len(health["checks"]),
                        "checks": health["checks"],
                    }

                return HealthCheck(
                    name="Monitoring Service",
                    status=HealthResult.HEALTHY,
                    message="Monitoring service is healthy",
                    details=details,
                )

            elif health["status"] == "warning":
                failed_checks = [
                    check["name"]
                    for check in health["checks"]
                    if check["status"] == "warn"
                ]
                return HealthCheck(
                    name="Monitoring Service",
                    status=HealthResult.WARNING,
                    message=f"Monitoring service has warnings: {', '.join(failed_checks)}",
                    details=health["checks"] if verbose else None,
                )

            else:  # unhealthy
                failed_checks = [
                    check["name"]
                    for check in health["checks"]
                    if check["status"] == "fail"
                ]

                if fix_issues:
                    # Attempt to restart monitoring service
                    try:
                        success = service.restart()

                        if success:
                            return HealthCheck(
                                name="Monitoring Service",
                                status=HealthResult.HEALTHY,
                                message="Fixed: Restarted monitoring service",
                                fix_attempted=True,
                                fix_successful=True,
                            )
                        else:
                            return HealthCheck(
                                name="Monitoring Service",
                                status=HealthResult.CRITICAL,
                                message=f"Failed to restart monitoring service: {', '.join(failed_checks)}",
                                fix_attempted=True,
                                fix_successful=False,
                            )
                    except Exception as restart_error:
                        return HealthCheck(
                            name="Monitoring Service",
                            status=HealthResult.CRITICAL,
                            message=f"Failed to restart monitoring: {str(restart_error)}",
                            fix_attempted=True,
                            fix_successful=False,
                        )
                else:
                    return HealthCheck(
                        name="Monitoring Service",
                        status=HealthResult.CRITICAL,
                        message=f"Monitoring service is unhealthy: {', '.join(failed_checks)}",
                        details=health["checks"] if verbose else None,
                    )

        except MonitoringServiceError as e:
            return HealthCheck(
                name="Monitoring Service",
                status=HealthResult.WARNING,
                message=f"Monitoring service error: {str(e)}",
                details={"error": str(e)},
            )
        except ImportError:
            return HealthCheck(
                name="Monitoring Service",
                status=HealthResult.WARNING,
                message="Monitoring service components not available",
                details={"import_error": "monitoring_service"},
            )
        except Exception as e:
            return HealthCheck(
                name="Monitoring Service",
                status=HealthResult.WARNING,
                message=f"Failed to check monitoring service: {str(e)}",
                details={"error": str(e)},
            )

    def _check_data_directories(
        self,
        verbose: bool = False,
        fix_issues: bool = False,
    ) -> HealthCheck:
        """Check shared data directories and permissions."""
        try:
            from heimdall.cognitive_system.data_dirs import (
                get_heimdall_data_dir,
                get_logs_data_dir,
                get_models_data_dir,
                get_qdrant_data_dir,
            )

            # Use shared data directories
            required_dirs = [
                get_heimdall_data_dir(),
                get_qdrant_data_dir(),
                get_models_data_dir(),
                get_logs_data_dir(),
            ]

            dir_names = [
                "heimdall data",
                "qdrant data",
                "models cache",
                "logs",
            ]

        except ImportError:
            # Fallback to legacy directories if shared data module unavailable
            required_dirs = [
                Path("./data"),
                Path("./data/qdrant"),
                Path("./data/models"),
            ]
            dir_names = ["data", "qdrant", "models"]

        issues = []
        created_dirs = []

        for dir_path, dir_name in zip(required_dirs, dir_names, strict=False):
            if not dir_path.exists():
                if fix_issues:
                    try:
                        dir_path.mkdir(parents=True, exist_ok=True)
                        created_dirs.append(f"{dir_name} ({dir_path})")
                    except Exception as e:
                        issues.append(f"Cannot create {dir_name} directory: {str(e)}")
                else:
                    issues.append(f"Missing {dir_name} directory: {dir_path}")
            elif not os.access(dir_path, os.W_OK):
                issues.append(f"No write permission for {dir_name}: {dir_path}")

        if issues:
            status = HealthResult.CRITICAL if not fix_issues else HealthResult.WARNING
            return HealthCheck(
                name="Data Directories",
                status=status,
                message="; ".join(issues),
                details={"issues": issues},
            )

        message = "All data directories are accessible"
        if created_dirs:
            message = f"Fixed: Created {', '.join(created_dirs)}"

        details = None
        if verbose:
            details = {
                "directories": [
                    (name, str(path))
                    for name, path in zip(dir_names, required_dirs, strict=False)
                ],
                "created": created_dirs,
            }

        return HealthCheck(
            name="Data Directories",
            status=HealthResult.HEALTHY,
            message=message,
            details=details,
            fix_attempted=bool(created_dirs),
            fix_successful=bool(created_dirs),
        )

    def _check_configuration(
        self,
        verbose: bool = False,
        fix_issues: bool = False,
    ) -> HealthCheck:
        """Check configuration files and environment variables."""
        try:
            issues: list[str] = []

            # Check required environment variables
            from cognitive_memory.core.config import SystemConfig

            try:
                config = SystemConfig.from_env()

                details = None
                if verbose:
                    details = {
                        "qdrant_url": config.qdrant.url,
                        "sentence_bert_model": config.embedding.model_name,
                        "activation_threshold": config.cognitive.activation_threshold,
                    }

                if issues:
                    return HealthCheck(
                        name="Configuration",
                        status=HealthResult.WARNING,
                        message="; ".join(issues),
                        details=details,
                    )
                else:
                    return HealthCheck(
                        name="Configuration",
                        status=HealthResult.HEALTHY,
                        message="Configuration is valid",
                        details=details,
                    )

            except Exception as config_error:
                return HealthCheck(
                    name="Configuration",
                    status=HealthResult.CRITICAL,
                    message=f"Configuration error: {str(config_error)}",
                )

        except Exception as e:
            return HealthCheck(
                name="Configuration",
                status=HealthResult.CRITICAL,
                message=f"Failed to check configuration: {str(e)}",
            )

    def _check_model_availability(
        self,
        verbose: bool = False,
        fix_issues: bool = False,
    ) -> HealthCheck:
        """Check ONNX model availability and functionality."""
        try:
            from cognitive_memory.encoding.onnx_provider import ONNXEmbeddingProvider
            from heimdall.cognitive_system.data_dirs import get_models_data_dir

            # First check if shared models directory is empty
            models_dir = get_models_data_dir()
            critical_files = [
                models_dir / "all-MiniLM-L6-v2.onnx",
                models_dir / "tokenizer" / "tokenizer.json",
                models_dir / "model_config.json",
            ]

            missing_files = [f for f in critical_files if not f.exists()]

            if missing_files:
                if fix_issues:
                    try:
                        from heimdall.cognitive_system.data_dirs import (
                            ensure_models_available,
                        )

                        print("Models missing from shared directory, downloading...")
                        ensure_models_available()

                        return HealthCheck(
                            name="Model Availability",
                            status=HealthResult.HEALTHY,
                            message="Models downloaded to shared directory and working",
                            fix_attempted=True,
                            fix_successful=True,
                            details={"models_dir": str(models_dir)}
                            if verbose
                            else None,
                        )
                    except Exception as download_error:
                        return HealthCheck(
                            name="Model Availability",
                            status=HealthResult.CRITICAL,
                            message=f"Model download failed: {str(download_error)}",
                            fix_attempted=True,
                            fix_successful=False,
                        )
                else:
                    missing_names = [f.name for f in missing_files]
                    return HealthCheck(
                        name="Model Availability",
                        status=HealthResult.CRITICAL,
                        message=f"Models missing from shared directory: {', '.join(missing_names)}. Run 'heimdall doctor --fix' to download.",
                        details={
                            "models_dir": str(models_dir),
                            "missing_files": missing_names,
                        }
                        if verbose
                        else None,
                    )

            try:
                # Try to load the ONNX model
                provider = ONNXEmbeddingProvider()

                # Test encoding
                test_encoding = provider.encode("test sentence")

                details = None
                if verbose:
                    details = {
                        "model_name": "all-MiniLM-L6-v2",
                        "embedding_dimension": len(test_encoding),
                        "model_format": "ONNX",
                        "model_path": str(provider.model_path),
                    }

                return HealthCheck(
                    name="Model Availability",
                    status=HealthResult.HEALTHY,
                    message="ONNX model is available and working",
                    details=details,
                )

            except Exception as model_error:
                return HealthCheck(
                    name="Model Availability",
                    status=HealthResult.CRITICAL,
                    message=f"ONNX model loading failed: {str(model_error)}",
                )

        except ImportError as import_error:
            return HealthCheck(
                name="Model Availability",
                status=HealthResult.CRITICAL,
                message=f"ONNX provider not available: {str(import_error)}",
            )

    def _check_network_connectivity(
        self,
        verbose: bool = False,
        fix_issues: bool = False,
    ) -> HealthCheck:
        """Check network connectivity for model downloads."""
        try:
            # Test HuggingFace Hub connectivity
            test_urls = [
                "https://huggingface.co",
                "https://pypi.org",
            ]

            connectivity_results = {}

            for url in test_urls:
                try:
                    response = requests.get(url, timeout=10)
                    connectivity_results[url] = response.status_code == 200
                except Exception:
                    connectivity_results[url] = False

            failed_connections = [
                url for url, success in connectivity_results.items() if not success
            ]

            if failed_connections:
                return HealthCheck(
                    name="Network Connectivity",
                    status=HealthResult.WARNING,
                    message=f"Limited connectivity: {', '.join(failed_connections)}",
                    details=connectivity_results if verbose else None,
                )
            else:
                return HealthCheck(
                    name="Network Connectivity",
                    status=HealthResult.HEALTHY,
                    message="Network connectivity is good",
                    details=connectivity_results if verbose else None,
                )

        except Exception as e:
            return HealthCheck(
                name="Network Connectivity",
                status=HealthResult.WARNING,
                message=f"Cannot check connectivity: {str(e)}",
            )

    def _check_performance_baseline(
        self,
        verbose: bool = False,
        fix_issues: bool = False,
    ) -> HealthCheck:
        """Check basic performance baseline using ONNX provider."""
        try:
            start_time = time.time()

            # Simple performance test: encoding speed with ONNX
            from cognitive_memory.encoding.onnx_provider import ONNXEmbeddingProvider

            provider = ONNXEmbeddingProvider()
            test_texts = ["test sentence"] * 10

            encoding_start = time.time()
            embeddings = provider.encode_batch(test_texts)
            encoding_time = time.time() - encoding_start

            total_time = time.time() - start_time

            # Performance thresholds (ONNX should be faster)
            if encoding_time > 3.0:
                status = HealthResult.WARNING
                message = f"Slow ONNX encoding performance: {encoding_time:.2f}s for 10 sentences"
            elif encoding_time > 8.0:
                status = HealthResult.CRITICAL
                message = f"Very slow ONNX encoding performance: {encoding_time:.2f}s for 10 sentences"
            else:
                status = HealthResult.HEALTHY
                message = f"Good ONNX encoding performance: {encoding_time:.2f}s for 10 sentences"

            details = None
            if verbose:
                details = {
                    "encoding_time_seconds": round(encoding_time, 3),
                    "total_time_seconds": round(total_time, 3),
                    "sentences_per_second": round(10 / encoding_time, 1),
                    "embedding_shape": list(embeddings.shape),
                    "provider": "ONNX",
                }

            return HealthCheck(
                name="Performance Baseline",
                status=status,
                message=message,
                details=details,
            )

        except Exception as e:
            return HealthCheck(
                name="Performance Baseline",
                status=HealthResult.WARNING,
                message=f"Cannot run ONNX performance test: {str(e)}",
            )

    def _generate_recommendations(self, checks: list[HealthCheck]) -> list[str]:
        """Generate recommendations based on health check results."""
        recommendations = []

        for check in checks:
            if check.status == HealthResult.CRITICAL:
                if "Python" in check.name:
                    recommendations.append("Upgrade to Python 3.13 or higher")
                elif "Dependencies" in check.name:
                    recommendations.append(
                        "Install missing packages with: pip install -r requirements.txt"
                    )
                elif "Qdrant" in check.name:
                    recommendations.append(
                        "Start Qdrant service with: memory_system qdrant start"
                    )
                elif "Data Directories" in check.name:
                    recommendations.append(
                        "Create required directories or check permissions"
                    )
                elif "Configuration" in check.name:
                    recommendations.append("Check .env file and configuration settings")

            elif check.status == HealthResult.WARNING:
                if "System Resources" in check.name:
                    recommendations.append(
                        "Consider upgrading system resources for better performance"
                    )
                elif "Docker" in check.name:
                    recommendations.append(
                        "Install Docker for easier service management"
                    )
                elif "Network" in check.name:
                    recommendations.append(
                        "Check internet connection for model downloads"
                    )

        return recommendations
