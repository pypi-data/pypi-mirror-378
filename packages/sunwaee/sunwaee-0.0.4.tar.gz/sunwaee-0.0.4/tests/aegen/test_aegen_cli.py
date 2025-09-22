# standard
from unittest.mock import patch

# third party
from typer.testing import CliRunner

# custom
from sunwaee.aegen._cli._entrypoint import aegen_commands


class TestAegenCLI:
    def setup_method(self):
        self.runner = CliRunner()

    def test_aegen_list_models_integration(self):
        result = self.runner.invoke(aegen_commands, ["list", "models"])
        assert result.exit_code == 0

        output_lines = result.stdout.strip().split("\n")
        assert len(output_lines) > 0

        non_empty_lines = [line for line in output_lines if line.strip()]
        assert non_empty_lines == sorted(non_empty_lines)

        assert "gpt-5" in output_lines

    def test_aegen_list_providers_integration(self):
        result = self.runner.invoke(aegen_commands, ["list", "providers"])
        assert result.exit_code == 0

        output_lines = result.stdout.strip().split("\n")
        assert len(output_lines) > 0

        non_empty_lines = [line for line in output_lines if line.strip()]
        assert non_empty_lines == sorted(non_empty_lines)

        assert "openai" in output_lines

    def test_aegen_list_agents_integration(self):
        result = self.runner.invoke(aegen_commands, ["list", "agents"])
        assert result.exit_code == 0

        output_lines = result.stdout.strip().split("\n")
        assert len(output_lines) > 0

        non_empty_lines = [line for line in output_lines if line.strip()]
        assert non_empty_lines == sorted(non_empty_lines)

        assert "openai/gpt-5" in output_lines

    @patch("sunwaee.aegen._cli.serve.uvicorn.run")
    def test_serve_default_options(self, mock_uvicorn_run):
        self.runner.invoke(aegen_commands, ["serve"])

        mock_uvicorn_run.assert_called_once_with(
            "sunwaee.api:app",
            host="127.0.0.1",
            port=8000,
            reload=False,
            workers=None,
            log_level="info",
        )

    @patch("sunwaee.aegen._cli.serve.uvicorn.run")
    def test_serve_custom_options(self, mock_uvicorn_run):
        self.runner.invoke(
            aegen_commands,
            [
                "serve",
                "--host",
                "0.0.0.0",
                "--port",
                "8080",
                "--reload",
                "--log-level",
                "debug",
            ],
        )

        mock_uvicorn_run.assert_called_once_with(
            "sunwaee.api:app",
            host="0.0.0.0",
            port=8080,
            reload=True,
            workers=None,
            log_level="debug",
        )

    @patch("sunwaee.aegen._cli.serve.uvicorn.run")
    def test_serve_with_workers(self, mock_uvicorn_run):
        self.runner.invoke(aegen_commands, ["serve", "--workers", "4"])
        mock_uvicorn_run.assert_called_once_with(
            "sunwaee.api:app",
            host="127.0.0.1",
            port=8000,
            reload=False,
            workers=4,
            log_level="info",
        )

    @patch("sunwaee.aegen._cli.serve.uvicorn.run")
    def test_serve_workers_with_reload_conflict(self, mock_uvicorn_run):
        self.runner.invoke(aegen_commands, ["serve", "--workers", "4", "--reload"])
        mock_uvicorn_run.assert_called_once_with(
            "sunwaee.api:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            workers=None,
            log_level="info",
        )

    @patch("sunwaee.aegen._cli.serve.uvicorn.run")
    @patch("sys.exit")
    def test_serve_keyboard_interrupt(self, mock_sys_exit, mock_uvicorn_run):
        mock_uvicorn_run.side_effect = KeyboardInterrupt()
        self.runner.invoke(aegen_commands, ["serve"])
        calls = mock_sys_exit.call_args_list
        assert any(
            call[0][0] == 0 for call in calls
        ), f"Expected sys.exit(0) to be called, got calls: {calls}"

    @patch("sunwaee.aegen._cli.serve.uvicorn.run")
    @patch("sys.exit")
    def test_serve_exception_handling(self, mock_sys_exit, mock_uvicorn_run):
        mock_uvicorn_run.side_effect = Exception("Test exception")
        self.runner.invoke(aegen_commands, ["serve"])
        calls = mock_sys_exit.call_args_list
        assert any(
            call[0][0] == 1 for call in calls
        ), f"Expected sys.exit(1) to be called, got calls: {calls}"
