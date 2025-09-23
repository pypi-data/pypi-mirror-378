# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""End-to-end tests for the toolbox SDK interacting with the toolbox server.

This file covers the following use cases:

1. Loading a tool.
2. Loading a specific toolset.
3. Loading the default toolset (contains all tools).
4. Running a tool with
    a. Missing params.
    b. Wrong param type.
5. Running a tool with no required auth, with auth provided.
6. Running a tool with required auth:
    a. No auth provided.
    b. Wrong auth provided: The tool requires a different authentication
                            than the one provided.
    c. Correct auth provided.
7. Running a tool with a parameter that requires auth:
    a. No auth provided.
    b. Correct auth provided.
    c. Auth provided does not contain the required claim.
"""

import pytest
import pytest_asyncio
from pydantic import ValidationError

from toolbox_llamaindex.client import ToolboxClient


@pytest.mark.asyncio
@pytest.mark.usefixtures("toolbox_server")
class TestE2EClientAsync:
    @pytest.fixture(scope="function")
    def toolbox(self):
        """Provides a ToolboxClient instance for each test."""
        toolbox = ToolboxClient("http://localhost:5000")
        return toolbox

    @pytest_asyncio.fixture(scope="function")
    async def get_n_rows_tool(self, toolbox):
        tool = await toolbox.aload_tool("get-n-rows")
        assert tool._ToolboxTool__core_tool.__name__ == "get-n-rows"
        return tool

    #### Basic e2e tests
    @pytest.mark.parametrize(
        "toolset_name, expected_length, expected_tools",
        [
            ("my-toolset", 1, ["get-row-by-id"]),
            ("my-toolset-2", 2, ["get-n-rows", "get-row-by-id"]),
        ],
    )
    async def test_aload_toolset_specific(
        self, toolbox, toolset_name, expected_length, expected_tools
    ):
        toolset = await toolbox.aload_toolset(toolset_name)
        assert len(toolset) == expected_length
        for tool in toolset:
            name = tool._ToolboxTool__core_tool.__name__
            assert name in expected_tools

    async def test_aload_toolset_all(self, toolbox):
        toolset = await toolbox.aload_toolset()
        assert len(toolset) == 7
        tool_names = [
            "get-n-rows",
            "get-row-by-id",
            "get-row-by-id-auth",
            "get-row-by-email-auth",
            "get-row-by-content-auth",
            "search-rows",
            "process-data",
        ]
        for tool in toolset:
            name = tool._ToolboxTool__core_tool.__name__
            assert name in tool_names

    async def test_run_tool_async(self, get_n_rows_tool):
        response = await get_n_rows_tool.acall(num_rows="2")

        assert "row1" in response.content
        assert "row2" in response.content
        assert "row3" not in response.content

    async def test_run_tool_sync(self, get_n_rows_tool):
        response = get_n_rows_tool.call(num_rows="2")

        assert "row1" in response.content
        assert "row2" in response.content
        assert "row3" not in response.content

    async def test_run_tool_missing_params(self, get_n_rows_tool):
        with pytest.raises(TypeError, match="missing a required argument: 'num_rows'"):
            await get_n_rows_tool.acall()

    async def test_run_tool_wrong_param_type(self, get_n_rows_tool):
        with pytest.raises(ValidationError, match="Input should be a valid string"):
            await get_n_rows_tool.acall(num_rows=2)

    ##### Auth tests
    @pytest.mark.asyncio
    async def test_run_tool_unauth_with_auth(self, toolbox, auth_token2):
        """Tests running a tool that doesn't require auth, with auth provided."""
        with pytest.raises(
            ValueError,
            match="Validation failed for tool 'get-row-by-id': unused auth tokens: my-test-auth.",
        ):
            await toolbox.aload_tool(
                "get-row-by-id",
                auth_token_getters={"my-test-auth": lambda: auth_token2},
            )

    async def test_run_tool_no_auth(self, toolbox):
        """Tests running a tool requiring auth without providing auth."""
        tool = await toolbox.aload_tool(
            "get-row-by-id-auth",
        )
        with pytest.raises(
            PermissionError,
            match="One or more of the following authn services are required to invoke this tool: my-test-auth",
        ):
            await tool.acall(id="2")

    async def test_run_tool_wrong_auth(self, toolbox, auth_token2):
        """Tests running a tool with incorrect auth."""
        tool = await toolbox.aload_tool(
            "get-row-by-id-auth",
        )
        auth_tool = tool.add_auth_token_getter("my-test-auth", lambda: auth_token2)
        with pytest.raises(
            Exception,
            match="tool invocation not authorized. Please make sure your specify correct auth headers",
        ):
            await auth_tool.acall(id="2")

    async def test_run_tool_auth(self, toolbox, auth_token1):
        """Tests running a tool with correct auth."""
        tool = await toolbox.aload_tool(
            "get-row-by-id-auth",
        )
        auth_tool = tool.add_auth_token_getter("my-test-auth", lambda: auth_token1)
        response = await auth_tool.acall(id="2")
        assert "row2" in response.content

    async def test_run_tool_param_auth_no_auth(self, toolbox):
        """Tests running a tool with a param requiring auth, without auth."""
        tool = await toolbox.aload_tool("get-row-by-email-auth")
        with pytest.raises(
            PermissionError,
            match="One or more of the following authn services are required to invoke this tool: my-test-auth",
        ):
            await tool.acall(email="")

    async def test_run_tool_param_auth(self, toolbox, auth_token1):
        """Tests running a tool with a param requiring auth, with correct auth."""
        tool = await toolbox.aload_tool(
            "get-row-by-email-auth",
            auth_token_getters={"my-test-auth": lambda: auth_token1},
        )
        response = await tool.acall()
        assert "row4" in response.content
        assert "row5" in response.content
        assert "row6" in response.content

    async def test_run_tool_param_auth_no_field(self, toolbox, auth_token1):
        """Tests running a tool with a param requiring auth, with insufficient auth."""
        tool = await toolbox.aload_tool(
            "get-row-by-content-auth",
            auth_token_getters={"my-test-auth": lambda: auth_token1},
        )
        with pytest.raises(
            Exception,
            match='provided parameters were invalid: error parsing authenticated parameter "data": no field named row_data in claims',
        ):
            await tool.acall()


@pytest.mark.usefixtures("toolbox_server")
class TestE2EClientSync:
    @pytest.fixture(scope="session")
    def toolbox(self):
        """Provides a ToolboxClient instance for each test."""
        toolbox = ToolboxClient("http://localhost:5000")
        return toolbox

    @pytest.fixture(scope="function")
    def get_n_rows_tool(self, toolbox):
        tool = toolbox.load_tool("get-n-rows")
        assert tool._ToolboxTool__core_tool.__name__ == "get-n-rows"
        return tool

    #### Basic e2e tests
    @pytest.mark.parametrize(
        "toolset_name, expected_length, expected_tools",
        [
            ("my-toolset", 1, ["get-row-by-id"]),
            ("my-toolset-2", 2, ["get-n-rows", "get-row-by-id"]),
        ],
    )
    def test_load_toolset_specific(
        self, toolbox, toolset_name, expected_length, expected_tools
    ):
        toolset = toolbox.load_toolset(toolset_name)
        assert len(toolset) == expected_length
        for tool in toolset:
            name = tool._ToolboxTool__core_tool.__name__
            assert name in expected_tools

    def test_aload_toolset_all(self, toolbox):
        toolset = toolbox.load_toolset()
        assert len(toolset) == 7
        tool_names = [
            "get-n-rows",
            "get-row-by-id",
            "get-row-by-id-auth",
            "get-row-by-email-auth",
            "get-row-by-content-auth",
            "search-rows",
            "process-data",
        ]
        for tool in toolset:
            name = tool._ToolboxTool__core_tool.__name__
            assert name in tool_names

    @pytest.mark.asyncio
    async def test_run_tool_async(self, get_n_rows_tool):
        response = await get_n_rows_tool.acall(num_rows="2")

        assert "row1" in response.content
        assert "row2" in response.content
        assert "row3" not in response.content

    def test_run_tool_sync(self, get_n_rows_tool):
        response = get_n_rows_tool.call(num_rows="2")

        assert "row1" in response.content
        assert "row2" in response.content
        assert "row3" not in response.content

    def test_run_tool_missing_params(self, get_n_rows_tool):
        with pytest.raises(TypeError, match="missing a required argument: 'num_rows'"):
            get_n_rows_tool.call()

    def test_run_tool_wrong_param_type(self, get_n_rows_tool):
        with pytest.raises(ValidationError, match="Input should be a valid string"):
            get_n_rows_tool.call(num_rows=2)

    #### Auth tests
    def test_run_tool_unauth_with_auth(self, toolbox, auth_token2):
        """Tests running a tool that doesn't require auth, with auth provided."""
        with pytest.raises(
            ValueError,
            match="Validation failed for tool 'get-row-by-id': unused auth tokens: my-test-auth.",
        ):
            toolbox.load_tool(
                "get-row-by-id",
                auth_token_getters={"my-test-auth": lambda: auth_token2},
            )

    def test_run_tool_no_auth(self, toolbox):
        """Tests running a tool requiring auth without providing auth."""
        tool = toolbox.load_tool(
            "get-row-by-id-auth",
        )
        with pytest.raises(
            PermissionError,
            match="One or more of the following authn services are required to invoke this tool: my-test-auth",
        ):
            tool.call(id="2")

    def test_run_tool_wrong_auth(self, toolbox, auth_token2):
        """Tests running a tool with incorrect auth."""
        tool = toolbox.load_tool(
            "get-row-by-id-auth",
        )
        auth_tool = tool.add_auth_token_getter("my-test-auth", lambda: auth_token2)
        with pytest.raises(
            Exception,
            match="tool invocation not authorized. Please make sure your specify correct auth headers",
        ):
            auth_tool.call(id="2")

    def test_run_tool_auth(self, toolbox, auth_token1):
        """Tests running a tool with correct auth."""
        tool = toolbox.load_tool(
            "get-row-by-id-auth",
        )
        auth_tool = tool.add_auth_token_getter("my-test-auth", lambda: auth_token1)
        response = auth_tool.call(id="2")
        assert "row2" in response.content

    def test_run_tool_param_auth_no_auth(self, toolbox):
        """Tests running a tool with a param requiring auth, without auth."""
        tool = toolbox.load_tool("get-row-by-email-auth")
        with pytest.raises(
            PermissionError,
            match="One or more of the following authn services are required to invoke this tool: my-test-auth",
        ):
            tool.call(email="")

    def test_run_tool_param_auth(self, toolbox, auth_token1):
        """Tests running a tool with a param requiring auth, with correct auth."""
        tool = toolbox.load_tool(
            "get-row-by-email-auth",
            auth_token_getters={"my-test-auth": lambda: auth_token1},
        )
        response = tool.call()
        assert "row4" in response.content
        assert "row5" in response.content
        assert "row6" in response.content

    def test_run_tool_param_auth_no_field(self, toolbox, auth_token1):
        """Tests running a tool with a param requiring auth, with insufficient auth."""
        tool = toolbox.load_tool(
            "get-row-by-content-auth",
            auth_token_getters={"my-test-auth": lambda: auth_token1},
        )
        with pytest.raises(
            Exception,
            match='provided parameters were invalid: error parsing authenticated parameter "data": no field named row_data in claims',
        ):
            tool.call()
