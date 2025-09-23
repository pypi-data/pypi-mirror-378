import json
import subprocess
import tempfile
import time
from pathlib import Path

import pytest
from faker import Faker

from tests.e2e.model.base_model_test import BaseModelTest


class TestModelSubmit(BaseModelTest):
    @pytest.mark.e2e
    def test_model_submit(self, session_auth):
        app_env, _ = session_auth

        fake = Faker()
        unique_suffix = fake.bothify(text="????-####").lower()
        model_display_name = f"example-model-{unique_suffix}"
        model_version = "v1.0.0"

        with tempfile.TemporaryDirectory() as work_dir:
            work_path = Path(work_dir)

            # region 1) Create .model-metadata
            output_path = work_path / "output"
            branch_name = f"test-model-branch-{unique_suffix}"
            metadata = {
                "model_name": model_display_name,
                "model_version": model_version,
                "output_path": str(output_path),
                "branch_name": branch_name,
            }
            (work_path / ".model-metadata").write_text(json.dumps(metadata))
            # endregion 1) Create .model-metadata

            # region 2) Create mlflow_pkg/model_data with .ptr files
            mlflow_pkg = output_path / "mlflow_pkg" / "model_data"
            mlflow_pkg.mkdir(parents=True, exist_ok=True)
            # Pointer file indicating successful upload
            ptr = {
                "file_size": 123,
                "upload_successful": True,
                "checksum": "sha256:d41d8cd98f00b204e9800998ecf8427e",
                "last_modified": "2024-01-01T00:00:00Z",
            }
            (mlflow_pkg / "artifact.ptr").write_text(json.dumps(ptr))
            # endregion 2) Create mlflow_pkg/model_data with .ptr files

            # region 3) Create model_card_docs/model_card_metadata.yaml
            mcd = work_path / "model_card_docs"
            mcd.mkdir(parents=True, exist_ok=True)
            mcd_yaml = (
                f"model_display_name: {model_display_name}\n"
                f"model_version: {model_version}\n"
                "licenses:\n  - type: MIT\n"
                "repository_link: https://github.com/example/example-model\n"
                "authors:\n  - name: Test User\n"
                "model_description: Example model for E2E submit test\n"
            )
            (mcd / "model_card_metadata.yaml").write_text(mcd_yaml)
            # endregion 3) Create model_card_docs/model_card_metadata.yaml

            # region 4) Run the submit command with skip-git
            cmd = [
                "uv",
                "run",
                "vcp",
                "model",
                "submit",
                "--skip-git",
                "--work-dir",
                str(work_path),
            ]
            result = subprocess.run(
                cmd,
                env=app_env,
                capture_output=True,
                text=True,
            )
            print(result.stdout)
            print(result.stderr)
            # endregion 4) Run the submit command with skip-git

            # region Assert the command ran successfully
            self.validate_model_submit_success(
                result, model_display_name, model_version, str(output_path)
            )
            # endregion Assert the command ran successfully

    @pytest.mark.e2e
    def test_model_submit_with_config_option(self, session_auth):
        app_env, temp_config = session_auth

        fake = Faker()
        unique_suffix = fake.bothify(text="????-####").lower()
        model_display_name = f"example-model-{unique_suffix}"
        model_version = "v1.0.0"

        with tempfile.TemporaryDirectory() as work_dir:
            work_path = Path(work_dir)

            # region 1) Create .model-metadata
            output_path = work_path / "output"
            branch_name = f"test-model-branch-{unique_suffix}"
            metadata = {
                "model_name": model_display_name,
                "model_version": model_version,
                "output_path": str(output_path),
                "branch_name": branch_name,
            }
            (work_path / ".model-metadata").write_text(json.dumps(metadata))
            # endregion 1) Create .model-metadata

            # region 2) Create mlflow_pkg/model_data with .ptr files
            mlflow_pkg = output_path / "mlflow_pkg" / "model_data"
            mlflow_pkg.mkdir(parents=True, exist_ok=True)
            # Pointer file indicating successful upload
            ptr = {
                "file_size": 123,
                "upload_successful": True,
                "checksum": "sha256:d41d8cd98f00b204e9800998ecf8427e",
                "last_modified": "2024-01-01T00:00:00Z",
            }
            (mlflow_pkg / "artifact.ptr").write_text(json.dumps(ptr))
            # endregion 2) Create mlflow_pkg/model_data with .ptr files

            # region 3) Create model_card_docs/model_card_metadata.yaml
            mcd = work_path / "model_card_docs"
            mcd.mkdir(parents=True, exist_ok=True)
            mcd_yaml = (
                f"model_display_name: {model_display_name}\n"
                f"model_version: {model_version}\n"
                "licenses:\n  - type: MIT\n"
                "repository_link: https://github.com/example/example-model\n"
                "authors:\n  - name: Test User\n"
                "model_description: Example model for E2E submit test\n"
            )
            (mcd / "model_card_metadata.yaml").write_text(mcd_yaml)
            # endregion 3) Create model_card_docs/model_card_metadata.yaml

            # region 4) Run the submit command with skip-git
            cmd = [
                "uv",
                "run",
                "vcp",
                "model",
                "submit",
                "--skip-git",
                "--work-dir",
                str(work_path),
                "--config",
                str(temp_config),
            ]
            result = subprocess.run(
                cmd,
                env=app_env,
                capture_output=True,
                text=True,
            )
            print(result.stdout)
            print(result.stderr)
            # endregion 4) Run the submit command with skip-git

            # region Assert the command ran successfully
            self.validate_model_submit_success(
                result, model_display_name, model_version, str(output_path)
            )
            # endregion Assert the command ran successfully

    @pytest.mark.e2e
    def test_model_submit_with_verbose_option(self, session_auth):
        app_env, _ = session_auth

        fake = Faker()
        unique_suffix = fake.bothify(text="????-####").lower()
        model_display_name = f"example-model-{unique_suffix}"
        model_version = "v1.0.0"

        with tempfile.TemporaryDirectory() as work_dir:
            work_path = Path(work_dir)

            # region 1) Create .model-metadata
            output_path = work_path / "output"
            branch_name = f"test-model-branch-{unique_suffix}"
            metadata = {
                "model_name": model_display_name,
                "model_version": model_version,
                "output_path": str(output_path),
                "branch_name": branch_name,
            }
            (work_path / ".model-metadata").write_text(json.dumps(metadata))
            # endregion 1) Create .model-metadata

            # region 2) Create mlflow_pkg/model_data with .ptr files
            mlflow_pkg = output_path / "mlflow_pkg" / "model_data"
            mlflow_pkg.mkdir(parents=True, exist_ok=True)
            # Pointer file indicating successful upload
            ptr = {
                "file_size": 123,
                "upload_successful": True,
                "checksum": "sha256:d41d8cd98f00b204e9800998ecf8427e",
                "last_modified": "2024-01-01T00:00:00Z",
            }
            (mlflow_pkg / "artifact.ptr").write_text(json.dumps(ptr))
            # endregion 2) Create mlflow_pkg/model_data with .ptr files

            # region 3) Create model_card_docs/model_card_metadata.yaml
            mcd = work_path / "model_card_docs"
            mcd.mkdir(parents=True, exist_ok=True)
            mcd_yaml = (
                f"model_display_name: {model_display_name}\n"
                f"model_version: {model_version}\n"
                "licenses:\n  - type: MIT\n"
                "repository_link: https://github.com/example/example-model\n"
                "authors:\n  - name: Test User\n"
                "model_description: Example model for E2E submit test\n"
            )
            (mcd / "model_card_metadata.yaml").write_text(mcd_yaml)
            # endregion 3) Create model_card_docs/model_card_metadata.yaml

            # region 4) Run the submit command with skip-git
            cmd = [
                "uv",
                "run",
                "vcp",
                "model",
                "submit",
                "--skip-git",
                "--work-dir",
                str(work_path),
                "--verbose",
            ]
            result = subprocess.run(
                cmd,
                env=app_env,
                capture_output=True,
                text=True,
            )
            print(result.stdout)
            print(result.stderr)
            # endregion 4) Run the submit command with skip-git

            # region Assert the command ran successfully
            self.validate_model_submit_success(
                result, model_display_name, model_version, str(output_path)
            )
            # endregion Assert the command ran successfully

    @pytest.mark.e2e
    def test_model_submit_with_duplicate_model_name(self, session_auth):
        app_env, temp_config = session_auth

        fake = Faker()
        unique_suffix = fake.bothify(text="????-####").lower()
        model_display_name = f"example-model-{unique_suffix}"
        model_version = "v1.0.0"

        with tempfile.TemporaryDirectory() as work_dir:
            work_path = Path(work_dir)

            # region 1) Create .model-metadata
            output_path = work_path / "output"
            branch_name = f"test-model-branch-{unique_suffix}"
            metadata = {
                "model_name": model_display_name,
                "model_version": model_version,
                "output_path": str(output_path),
                "branch_name": branch_name,
            }
            (work_path / ".model-metadata").write_text(json.dumps(metadata))
            # endregion 1) Create .model-metadata

            # region 2) Create mlflow_pkg/model_data with .ptr files
            mlflow_pkg = output_path / "mlflow_pkg" / "model_data"
            mlflow_pkg.mkdir(parents=True, exist_ok=True)
            # Pointer file indicating successful upload
            ptr = {
                "file_size": 123,
                "upload_successful": True,
                "checksum": "sha256:d41d8cd98f00b204e9800998ecf8427e",
                "last_modified": "2024-01-01T00:00:00Z",
            }
            (mlflow_pkg / "artifact.ptr").write_text(json.dumps(ptr))
            # endregion 2) Create mlflow_pkg/model_data with .ptr files

            # region 3) Create model_card_docs/model_card_metadata.yaml
            mcd = work_path / "model_card_docs"
            mcd.mkdir(parents=True, exist_ok=True)
            mcd_yaml = (
                f"model_display_name: {model_display_name}\n"
                f"model_version: {model_version}\n"
                "licenses:\n  - type: MIT\n"
                "repository_link: https://github.com/example/example-model\n"
                "authors:\n  - name: Test User\n"
                "model_description: Example model for E2E submit test\n"
            )
            (mcd / "model_card_metadata.yaml").write_text(mcd_yaml)
            # endregion 3) Create model_card_docs/model_card_metadata.yaml

            # region 4) Run the submit command with skip-git
            cmd = [
                "uv",
                "run",
                "vcp",
                "model",
                "submit",
                "--skip-git",
                "--work-dir",
                str(work_path),
                "--config",
                str(temp_config),
            ]
            submission_1_result = subprocess.run(
                cmd,
                env=app_env,
                capture_output=True,
                text=True,
            )
            print(submission_1_result.stdout)
            print(submission_1_result.stderr)
            assert "Model data submitted successfully" in submission_1_result.stdout
            # endregion 4) Run the submit command with skip-git

            # region 5) Make changes to the model
            updated_mcd_yaml = (
                f"model_display_name: {model_display_name}\n"
                f"model_version: {model_version}\n"
                "licenses:\n  - type: MIT\n"
                "repository_link: https://github.com/example/example-model\n"
                "authors:\n  - name: Test User\n"
                f"model_description: Updated model for E2E submit test - version 2\n"  # updated description
            )
            (mcd / "model_card_metadata.yaml").write_text(updated_mcd_yaml)
            updated_ptr = {
                "file_size": 456,  # updated file size
                "upload_successful": True,
                "checksum": "sha256:updated_checksum_for_second_submission",
                "last_modified": "2024-01-02T00:00:00Z",  # updated timestamp
            }
            (mlflow_pkg / "artifact.ptr").write_text(json.dumps(updated_ptr))
            # endregion 5) Make changes to the model

            # region 6) Submit the updated model again
            time.sleep(1)  # Pause before second submission

            submission_2_result = subprocess.run(
                cmd,
                env=app_env,
                capture_output=True,
                text=True,
            )
            print(submission_2_result.stdout)
            print(submission_2_result.stderr)
            # endregion 6) Submit the updated model again

            # region Assert the updated model was submitted successfully
            print("=== First Submission ===")
            print(submission_1_result.stdout)
            print("\n=== Second Submission (Updated Model) ===")
            print(submission_2_result.stdout)
            assert "Model data submitted successfully" in submission_2_result.stdout
            # endregion Assert the updated model was submitted successfully

    @pytest.mark.e2e
    def test_version_format_normalization(self, session_auth):
        app_env, temp_config = session_auth

        fake = Faker()
        unique_suffix = fake.bothify(text="????-####").lower()
        model_display_name = f"example-model-{unique_suffix}"
        version_without_v_prefix = "1.0.0"  # Missing 'v' prefix

        with tempfile.TemporaryDirectory() as work_dir:
            work_path = Path(work_dir)

            # region 1) Create .model-metadata with invalid version
            output_path = work_path / "output"
            branch_name = f"test-model-branch-{unique_suffix}"
            metadata = {
                "model_name": model_display_name,
                "model_version": version_without_v_prefix,
                "output_path": str(output_path),
                "branch_name": branch_name,
            }
            (work_path / ".model-metadata").write_text(json.dumps(metadata))
            # endregion 1) Create .model-metadata with invalid version

            # region 2) Create mlflow_pkg/model_data with .ptr files
            mlflow_pkg = output_path / "mlflow_pkg" / "model_data"
            mlflow_pkg.mkdir(parents=True, exist_ok=True)
            ptr = {
                "file_size": 123,
                "upload_successful": True,
                "checksum": "sha256:d41d8cd98f00b204e9800998ecf8427e",
                "last_modified": "2024-01-01T00:00:00Z",
            }
            (mlflow_pkg / "artifact.ptr").write_text(json.dumps(ptr))
            # endregion 2) Create mlflow_pkg/model_data with .ptr files

            # region 3) Create model_card_docs/model_card_metadata.yaml with invalid version
            mcd = work_path / "model_card_docs"
            mcd.mkdir(parents=True, exist_ok=True)
            mcd_yaml = (
                f"model_display_name: {model_display_name}\n"
                f"model_version: {version_without_v_prefix}\n"  # Invalid version format
                "licenses:\n  - type: MIT\n"
                "repository_link: https://github.com/example/example-model\n"
                "authors:\n  - name: Test User\n"
                "model_description: Example model for E2E invalid version test\n"
            )
            (mcd / "model_card_metadata.yaml").write_text(mcd_yaml)
            # endregion 3) Create model_card_docs/model_card_metadata.yaml with invalid version

            # region 4) Run the submit command with skip-git
            cmd = [
                "uv",
                "run",
                "vcp",
                "model",
                "submit",
                "--skip-git",
                "--work-dir",
                str(work_path),
                "--config",
                str(temp_config),
                "--verbose",
            ]
            result = subprocess.run(
                cmd,
                env=app_env,
                capture_output=True,
                text=True,
            )
            print(result.stdout)
            print(result.stderr)
            # endregion 4) Run the submit command with skip-git

            # region Assert the v was automatically added to the version in the Submission Data

            # Assert the v was automatically added to the version
            expected_submission_data = f'"version": "v{version_without_v_prefix}"'
            assert (
                expected_submission_data in result.stdout
            ), f"Expected v prefix automatically added to the version Submission Data, got: {result.stdout}"
            # endregion Assert the v was automatically added to the version in the Submission Data
