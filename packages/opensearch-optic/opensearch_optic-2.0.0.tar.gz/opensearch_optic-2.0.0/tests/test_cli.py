import click
import pytest
from click.testing import CliRunner

from optic.cli import alias, cli, cluster, get_default_from_optic_settings, index, init


@pytest.fixture
def ctx_obj(optic_settings_file_path, optic_settings):
    optic_settings["optic_settings_file_path"] = optic_settings_file_path
    yield {"optic_settings": optic_settings}


@pytest.fixture
def runner():
    return CliRunner(echo_stdin=False)


@pytest.fixture
def mock_exit(mocker):
    # mock 'exit' to prevent tests from exiting
    mock_exit = mocker.patch("builtins.exit", side_effect=SystemExit(1))
    yield mock_exit


class TestCli:
    @pytest.mark.parametrize("command", [cli, init, cluster, index, alias])
    def test_commands_help(self, runner, command):
        result = runner.invoke(command, ["--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.output

    def test_alias_info_tool_missing_cluster_config_file(
        self, runner, optic_settings_file_path, mock_exit
    ):
        runner.invoke(
            cli,
            [
                "--settings",
                optic_settings_file_path,
                "alias",
                "info",
                "--cluster-config",
                "dummy.yml",
            ],
        )
        mock_exit.assert_called_once_with(1)

    def test_alias_info_tool_missing_both_yaml_files(self, runner, mock_exit):
        runner.invoke(
            cli,
            [
                "--settings",
                "non-existing-settings.yaml",
                "alias",
                "info",
                "--cluster-config",
                "dummy.yml",
            ],
        )
        mock_exit.assert_called_once_with(1)

    def test_init_command_success(self, mocker, runner):
        mock_initialize_optic = mocker.patch("optic.cli.initialize_optic")
        runner.invoke(cli, ["init"])
        mock_initialize_optic.assert_called_once()

    def test_cluster_info_tool_missing_both_yaml_files(self, runner, mock_exit):
        runner.invoke(
            cli,
            [
                "--settings",
                "non-existing-settings.yaml",
                "cluster",
                "info",
                "--cluster-config",
                "dummy.yml",
            ],
        )
        mock_exit.assert_called_once_with(1)

    def test_cluster_info_tool_missing_cluster_config_file(
        self, mocker, runner, optic_settings_file_path, mock_exit
    ):
        runner.invoke(
            cli,
            [
                "--settings",
                optic_settings_file_path,
                "cluster",
                "info",
                "--cluster-config",
                "dummy.yml",
            ],
        )
        mock_exit.assert_called_once_with(1)

    def test_cluster_info_command_success(
        self, mocker, runner, optic_settings_file_path, optic_settings, cluster_config
    ):
        mock_get_selected_clusters = mocker.patch("optic.cli.get_selected_clusters")
        mock_get_cluster_info = mocker.patch("optic.cli.get_cluster_info")

        runner.invoke(
            cli,
            [
                "--settings",
                optic_settings_file_path,
                "cluster",
                "info",
                "--cluster",
                "cluster_1",
            ],
        )
        mock_get_selected_clusters.assert_called_once()
        mock_get_cluster_info.assert_called_once()

    def test_alias_tool_usage_display(self, ctx_obj, runner):
        result = runner.invoke(cli, ["alias"], obj=ctx_obj)
        assert result.exit_code == 0
        assert "alias: actions related to OpenSearch aliases" in result.output

    def test_alias_info_command_success(
        self,
        mocker,
        runner,
        optic_settings_file_path,
        optic_settings_file,
        cluster_config_file,
    ):
        mock_get_selected_clusters = mocker.patch("optic.cli.get_selected_clusters")
        mock_get_alias_info = mocker.patch("optic.cli.get_alias_info")

        runner.invoke(
            cli,
            [
                "--settings",
                optic_settings_file_path,
                "alias",
                "info",
                "--cluster",
                "cluster_1",
            ],
        )
        mock_get_selected_clusters.assert_called_once()
        mock_get_alias_info.assert_called_once()

    def test_alias_info_tool_missing_both_yaml_files(self, runner, mock_exit):
        runner.invoke(
            cli,
            [
                "--settings",
                "non-existing-settings.yaml",
                "index",
                "info",
                "--cluster-config",
                "dummy.yml",
            ],
        )
        mock_exit.assert_called_once_with(1)

    def test_alias_info_tool_missing_cluster_config_file(
        self,
        mocker,
        runner,
        optic_settings_file_path,
        optic_settings_file,
        mock_exit,
    ):
        runner.invoke(
            cli,
            [
                "--settings",
                optic_settings_file_path,
                "index",
                "info",
                "--cluster-config",
                "dummy.yml",
            ],
        )
        mock_exit.assert_called_once_with(1)

    def test_index_info_command_success(
        self,
        mocker,
        runner,
        optic_settings_file_path,
        optic_settings_file,
        cluster_config_file,
    ):
        mock_configure_cluster = mocker.patch("optic.cli.configure_cluster")
        mock_get_index_info = mocker.patch("optic.cli.get_index_info")
        mock_print_index_info = mocker.patch("optic.cli.print_index_info")

        runner.invoke(
            cli,
            [
                "--settings",
                optic_settings_file_path,
                "index",
                "info",
                "--cluster",
                "cluster_1",
                "--cluster",
                "cluster_2",
            ],
        )
        assert mock_configure_cluster.call_count == 2
        mock_get_index_info.assert_called_once()
        mock_print_index_info.assert_called_once()

    def test_option_get_default_from_optic_settings_absent(self, ctx_obj):
        context = click.Context(cli.commands["alias"].commands["info"], obj=ctx_obj)
        option_class = get_default_from_optic_settings("example_setting")
        option = option_class(["--example"], required=False)
        with pytest.raises(SystemExit) as e:
            option.get_default(context)
        assert e.type == SystemExit
        assert e.value.code == 1

    def test_option_get_default_from_optic_settings_no_obj(self):
        context = click.Context(cli.commands["alias"].commands["info"], obj=None)
        option_class = get_default_from_optic_settings("example_setting")
        option = option_class(["--example"], required=False)
        default_value = option.get_default(context)
        assert default_value is None

    def test_option_get_default_from_optic_settings_present(self):
        mock_settings = {"optic_settings": {"example_setting": "test_value"}}
        context = click.Context(
            cli.commands["alias"].commands["info"], obj=mock_settings
        )
        option_class = get_default_from_optic_settings("example_setting")
        option = option_class(["--example"], required=False)
        default_value = option.get_default(context)
        assert default_value == "test_value"
