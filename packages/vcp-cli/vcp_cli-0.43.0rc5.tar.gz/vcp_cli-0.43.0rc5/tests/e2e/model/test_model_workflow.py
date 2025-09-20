import subprocess
import tempfile
import uuid
from pathlib import Path

import pytest
import requests

from tests.e2e.model.base_model_test import BaseModelTest


class TestModelWorkflowE2E(BaseModelTest):
    def setup_method(self):
        """Initialize instance variables for teardown."""
        self.model_name = None
        self.app_env = None

    def teardown_method(self):
        """Clean up GitHub repository created during test."""
        if not self.model_name or not self.app_env:
            return

        try:
            id_token = self.get_id_token(self.app_env)
            gh_token = self.get_github_contributions_token(self.app_env, id_token)
            repo_api = f"{self.GITHUB_REPOS_ENDPOINT}{self.CZ_MODEL_CONTRIBUTIONS}/{self.model_name}"

            resp = requests.delete(
                repo_api,
                headers={
                    "Authorization": f"Bearer {gh_token}",
                    "Accept": "application/vnd.github+json",
                },
                timeout=30,
            )

            if resp.status_code in (202, 204):
                print(
                    f"Teardown: Deleted test repo {self.CZ_MODEL_CONTRIBUTIONS}/{self.model_name}"
                )
            elif resp.status_code == 404:
                print(
                    f"Teardown: Repo not found (may not have been created): {self.CZ_MODEL_CONTRIBUTIONS}/{self.model_name}"
                )
            else:
                print(
                    f"Teardown: Failed to delete repo {self.CZ_MODEL_CONTRIBUTIONS}/{self.model_name}: {resp.status_code} {resp.text}"
                )
        except Exception as e:
            print(f"Teardown: Error during repo cleanup for {self.model_name}: {e}")

    @pytest.mark.e2e
    def test_model_workflow_end_to_end(self, session_auth):
        """
        Test the model workflow from initialization to submission and acceptance.
        This test covers the model workflow lifecycle, including:
        - Model initialization
        - Model status checks
          - Initialized
          - Submitted
          - Accepted
        - Model workflow steps
          - Metadata step
          - Copy weights step
          - Package model step
          - Submit model step

        VCP CLI commands used:
        - vcp model init
        - vcp model status
        - vcp model workflow
        - vcp model submit

        Model Hub API used:
        - /api/admin/submissions
        - /api/admin/submissions/{submission_id}/accept

        This test is designed to ensure that the model workflow is working as expected.
        The test uses the model hub api to accept the model submission.

        """
        app_env, temp_config = session_auth
        self.app_env = app_env

        with tempfile.TemporaryDirectory() as work_dir:
            work_path = Path(work_dir)

            unique = uuid.uuid4().hex[:8]
            model_name = f"test-e2e-workflow-model-{unique}"
            self.model_name = model_name
            model_version = "v1.0.0"

            # region Prepare git and template environment
            env_with_git, _template_dir, cleanup = self.prepare_git_and_template_env(
                app_env, Path(temp_config)
            )
            # endregion Prepare git and template environment

            # region Run model init
            try:
                init_cmd = [
                    "uv",
                    "run",
                    "vcp",
                    "model",
                    "init",
                    "--model-name",
                    model_name,
                    "--model-version",
                    model_version,
                    "--license-type",
                    "MIT",
                    "--work-dir",
                    work_dir,
                ]

                init_result = subprocess.run(
                    init_cmd,
                    env=env_with_git,
                    capture_output=True,
                    text=True,
                )

                print(init_result.stdout)
                print(init_result.stderr)

                assert (
                    init_result.returncode == 0
                ), f"init failed: {init_result.stderr}\n{init_result.stdout}"
                assert (
                    "Model initialization completed successfully!" in init_result.stdout
                )
                assert f"Work directory: {work_dir}" in init_result.stdout
            finally:
                cleanup()
            # endregion Run model init

            # region Run model status and assert initialized
            status_cmd = [
                "uv",
                "run",
                "vcp",
                "model",
                "status",
                "--format",
                "json",
            ]

            status_proc = subprocess.run(
                status_cmd,
                env=env_with_git,
                capture_output=True,
                text=True,
            )

            self.assert_successful_command(status_proc, "model status")
            model = self.get_model_status_json(
                status_proc.stdout, model_name, model_version
            )
            assert (
                model
            ), f"Could not parse JSON from model status output: {status_proc.stdout}"

            assert model, f"Model not found in payload: {model}"
            assert (
                model.get("status") == "initialized"
            ), f"Model status is not initialized: {model}"

            print(f"model: {model}")
            # endregion Run model status and assert initialized

            # region Prepare workflow environment
            (work_path / "copier.yml").write_text("min_version: '0.0.0'\n")
            (work_path / ".copier-answers.yml").write_text("{}\n")
            # endregion Prepare workflow environment

            # region Run workflow status and assert metadata step is next
            workflow_cmd = [
                "uv",
                "run",
                "vcp",
                "model",
                "workflow",
                "--work-dir",
                work_dir,
            ]

            workflow_result = subprocess.run(
                workflow_cmd,
                env=env_with_git,
                capture_output=True,
                text=True,
            )

            print(workflow_result.stdout)
            print(workflow_result.stderr)

            assert (
                workflow_result.returncode == 0
            ), f"workflow failed: {workflow_result.stderr}\n{workflow_result.stdout}"
            assert "VCP Model Workflow Status" in workflow_result.stdout
            assert "Next Step: Review Files" in workflow_result.stdout
            # endregion Run workflow status and assert metadata step is next

            # region Run workflow metadata and assert copy weights step is next
            # Edit metadata with required fields and mark files as recently modified
            metadata_path = work_path / "model_card_docs" / "model_card_metadata.yaml"
            metadata_content = (
                f"model_display_name: {model_name}\n"
                f"model_version: {model_version}\n"
                "model_description: E2E workflow test model description\n"
            )
            metadata_path.write_text(metadata_content)

            # Touch README to count as an edited key file
            (work_path / "README.md").write_text(
                f"# {model_name}\n\nUpdated by workflow e2e test\n"
            )

            # Check workflow again; next step should be Copy Weights
            workflow_result = subprocess.run(
                workflow_cmd,
                env=env_with_git,
                capture_output=True,
                text=True,
            )

            print(workflow_result.stdout)
            print(workflow_result.stderr)

            self.assert_successful_command(
                workflow_result, "model workflow (after metadata)"
            )
            assert "VCP Model Workflow Status" in workflow_result.stdout
            assert "Next Step: Copy Weights" in workflow_result.stdout
            # endregion Run workflow metadata and assert copy weights step is next

            # region Run workflow weights and assert package step is next
            # Create *_mlflow_pkg/model_data and add a non-gitkeep file
            mlflow_pkg = work_path / "example_mlflow_pkg"
            model_data_dir = mlflow_pkg / "model_data"
            model_data_dir.mkdir(parents=True, exist_ok=True)
            (model_data_dir / "weights.bin").write_bytes(b"dummy-weights\n")

            # Re-run workflow; next step should be Package Model
            workflow_result = subprocess.run(
                workflow_cmd,
                env=env_with_git,
                capture_output=True,
                text=True,
            )

            print(workflow_result.stdout)
            print(workflow_result.stderr)

            self.assert_successful_command(
                workflow_result, "model workflow (after weights)"
            )
            assert "VCP Model Workflow Status" in workflow_result.stdout
            assert "Next Step: Package Model" in workflow_result.stdout
            # endregion Run workflow weights and assert package step is next

            # region Run workflow package and assert submit step is next
            # Create mlflow package artifact directory with at least one file
            artifact_dir = work_path / "example_mlflow_pkg" / "mlflow_model_artifact"
            artifact_dir.mkdir(parents=True, exist_ok=True)
            (artifact_dir / "README.txt").write_text("artifact contents for e2e test\n")

            # Re-run workflow; next step should be Stage Files
            workflow_result = subprocess.run(
                workflow_cmd,
                env=env_with_git,
                capture_output=True,
                text=True,
            )

            print(workflow_result.stdout)
            print(workflow_result.stderr)

            self.assert_successful_command(
                workflow_result, "model workflow (after package)"
            )
            assert "VCP Model Workflow Status" in workflow_result.stdout
            assert "Next Step: Submit Model" in workflow_result.stdout
            # endregion Run workflow package and assert submit step is next

            # region Run workflow submit and assert success
            # Convert weights to staged pointers to satisfy submit validations
            # Replace non-.ptr file with a .ptr pointer file
            (model_data_dir / "weights.bin").unlink(missing_ok=True)
            (model_data_dir / "weights.bin.ptr").write_text("{}\n")

            # Ensure a git repo and commit exist to satisfy submit checks
            subprocess.run(["git", "init"], cwd=work_dir, env=env_with_git, check=False)

            # Set author identity
            subprocess.run(
                ["git", "config", "user.name", "E2E Test"],
                cwd=work_dir,
                env=env_with_git,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=work_dir,
                env=env_with_git,
                check=True,
            )

            subprocess.run(
                ["git", "add", "."], cwd=work_dir, env=env_with_git, check=False
            )
            subprocess.run(
                [
                    "git",
                    "-c",
                    "user.email=devnull@example.com",
                    "-c",
                    "user.name=E2E Workflow Test",
                    "commit",
                    "-m",
                    f"feat: model {model_name} initial files",
                ],
                cwd=work_dir,
                env=env_with_git,
                check=False,
            )

            submit_cmd = [
                "uv",
                "run",
                "vcp",
                "model",
                "submit",
                "--work-dir",
                work_dir,
            ]

            submit_result = subprocess.run(
                submit_cmd,
                env=env_with_git,
                capture_output=True,
                text=True,
            )

            print(submit_result.stdout)
            print(submit_result.stderr)

            assert (
                submit_result.returncode == 0
            ), f"submit failed: {submit_result.stderr}\n{submit_result.stdout}"
            assert "Starting model submission" in submit_result.stdout
            assert "✅ Init command validation passed" in submit_result.stdout
            assert "Validating stage command was run" in submit_result.stdout
            assert "Model data submitted successfully" in submit_result.stdout
            # endregion Run workflow submit and assert success

            # region Run workflow and assert "🎉 Workflow Successfully Completed!"
            workflow_cmd = [
                "uv",
                "run",
                "vcp",
                "model",
                "workflow",
                "--work-dir",
                work_dir,
            ]

            workflow_result = subprocess.run(
                workflow_cmd,
                env=env_with_git,
                capture_output=True,
                text=True,
            )

            print(workflow_result.stdout)
            print(workflow_result.stderr)

            assert "🎉 Workflow Successfully Completed!" in workflow_result.stdout
            # endregion Run workflow and assert "🎉 Workflow Successfully Completed!"

            # region Run model status and assert submitted
            status_cmd = [
                "uv",
                "run",
                "vcp",
                "model",
                "status",
                "--format",
                "json",
            ]

            status_proc = subprocess.run(
                status_cmd,
                env=env_with_git,
                capture_output=True,
                text=True,
            )

            self.assert_successful_command(status_proc, "model status")
            model = self.get_model_status_json(
                status_proc.stdout, model_name, model_version
            )
            assert (
                model
            ), f"Could not parse JSON from model status output: {status_proc.stdout}"

            assert model, f"Model not found in payload: {model}"
            assert (
                model.get("status") == "submitted"
            ), f"Model status is not submitted: {model}"

            assert (
                f"@github.com/{self.CZ_MODEL_CONTRIBUTIONS}/{model_name}"
                in model.get("pr_url")
            ), f"Model PR URL does not include @github.com/{self.CZ_MODEL_CONTRIBUTIONS}/{model_name}: {model}"

            print(f"model: {model}")
            # endregion Run model status and assert submitted

            # region Get the model submission id from the model hub api
            api_base = app_env["VCP_API_BASE_URL"].rstrip("/")
            id_token = self.get_id_token(app_env)

            resp = requests.get(
                f"{api_base}/api/admin/submissions",
                headers={"Authorization": f"Bearer {id_token}"},
                timeout=60,
            )
            assert (
                resp.status_code == 200
            ), f"/api/admin/submissions failed: {resp.status_code} {resp.text}"

            submissions = resp.json() or []
            matching = [
                s
                for s in submissions
                if s.get("model_name") == model_name
                and s.get("model_version") == model_version
            ]
            assert matching, (
                "No submission found for model/version in admin submissions list. "
                f"model={model_name} version={model_version}\nGot: {submissions[:3]}..."
            )
            submission_id = matching[0].get("submission_id")
            assert submission_id, f"submission_id missing in record: {matching[0]}"

            # Persist for debugging
            (work_path / "submission_id.txt").write_text(str(submission_id) + "\n")
            print(f"Submission ID (from API): {submission_id}")
            # endregion Get the model submission id from the model hub api

            # region Accept the model submission using model hub api
            accept_resp = requests.post(
                f"{api_base}/api/admin/submissions/{submission_id}/accept",
                headers={"Authorization": f"Bearer {id_token}"},
                timeout=60,
            )
            assert (
                accept_resp.status_code == 200
            ), f"Accept submission failed: {accept_resp.status_code} {accept_resp.text}"
            # endregion Accept the model submission using model hub api

            # region Run model status and assert accepted
            status_cmd = [
                "uv",
                "run",
                "vcp",
                "model",
                "status",
                "--format",
                "json",
            ]

            status_proc = subprocess.run(
                status_cmd,
                env=env_with_git,
                capture_output=True,
                text=True,
            )

            self.assert_successful_command(status_proc, "model status")
            model = self.get_model_status_json(
                status_proc.stdout, model_name, model_version
            )
            assert (
                model
            ), f"Could not parse JSON from model status output: {status_proc.stdout}"

            assert model, f"Model not found in payload: {model}"
            assert (
                model.get("status") == "accepted"
            ), f"Model status is not accepted: {model}"

            assert (
                f"@github.com/{self.CZ_MODEL_CONTRIBUTIONS}/{model_name}"
                in model.get("pr_url")
            ), f"Model PR URL does not include @github.com/{self.CZ_MODEL_CONTRIBUTIONS}/{model_name}: {model}"

            print(f"model: {model}")
            # endregion Run model status and assert accepted
