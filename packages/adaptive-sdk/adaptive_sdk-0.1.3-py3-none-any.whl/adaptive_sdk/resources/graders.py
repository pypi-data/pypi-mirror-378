from __future__ import annotations

from typing import Sequence, TYPE_CHECKING, Any, Literal

from adaptive_sdk.graphql_client import (
    GraderData,
    GraderCreateInput,
    CustomConfigInput,
    GraderConfigInput,
    GraderTypeEnum,
    JudgeConfigInput,
    PrebuiltConfigInput,
    RemoteConfigInput,
    PrebuiltCriteriaKey,
    MetricGetOrCreate,
    JudgeExampleInput,
    JudgeExampleInputTurnEntry,
    TestRemoteEnvTestRemoteEnvRemoteEnvTestOffline,
    TestRemoteEnvTestRemoteEnvRemoteEnvTestOnline,
    RemoteEnvCreate,
)
from adaptive_sdk import input_types

from .base_resource import SyncAPIResource, AsyncAPIResource, UseCaseResource

if TYPE_CHECKING:
    from adaptive_sdk.client import Adaptive, AsyncAdaptive


class GraderCreator(SyncAPIResource, UseCaseResource):  # type: ignore[misc]
    """Helper class for creating different types of graders with a clean API."""

    def __init__(self, client: Adaptive) -> None:
        SyncAPIResource.__init__(self, client)
        UseCaseResource.__init__(self, client)

    def binary_judge(
        self,
        *,
        key: str,
        criteria: str,
        judge_model: str,
        feedback_key: str,
        name: str | None = None,
        examples: list[input_types.JudgeExampleInput] | None = None,
        use_case: str | None = None,
    ) -> GraderData:
        """
        Creates a new judge-based grader.

        Args:
            key: Unique key for the grader.
            criteria: Natural-language explanation of what should be evaluated as a binary pass/fail.
            judge_model: Model key of the judge model.
            feedback_key: Key for the feedback this grader writes to.
            examples: List of annotated examples for few-shot prompting.
            name: Human-readable grader name. If omitted, derived from key.
            use_case: Explicit use-case key. Falls back to client.default_use_case.
        """
        # Parse examples if provided
        parsed_examples = []
        if examples:
            for ex in examples:
                if not all(k in ex for k in ("input", "output", "passes")):
                    raise ValueError("Each example must contain 'input', 'output', and 'passes' keys")
                input_turns = [JudgeExampleInputTurnEntry(role=t["role"], content=t["content"]) for t in ex["input"]]
                parsed_examples.append(
                    JudgeExampleInput(
                        input=input_turns,
                        output=ex["output"],
                        reasoning=ex.get("reasoning"),
                        **{"pass": bool(ex["passes"])},
                    )
                )

        # Create judge config
        judge_config = JudgeConfigInput(
            model=judge_model,
            criteria=criteria,
            examples=parsed_examples,
        )

        # Create grader config
        grader_config = GraderConfigInput(judge=judge_config)

        input_obj = GraderCreateInput(
            name=name or key,
            key=key,
            graderType=GraderTypeEnum.JUDGE,
            graderConfig=grader_config,
            metric=MetricGetOrCreate(existing=feedback_key),
        )

        return self._client._gql_client.create_grader(
            use_case=self.use_case_key(use_case), input=input_obj
        ).create_grader

    def prebuilt_judge(
        self,
        *,
        key: str,
        type: Literal["FAITHFULNESS"],
        judge_model: str,
        name: str | None = None,
        use_case: str | None = None,
    ) -> GraderData:
        """
        Creates a new prebuilt grader.

        Args:
            key: Unique key for the grader.
            type: Type of prebuild AI Judge Grader.
            judge_model: Model key of the judge model.
            name: Human-readable grader name. If omitted, derived from key.
            use_case: Explicit use-case key. Falls back to client.default_use_case.
        """
        # Create prebuilt config
        assert type == "FAITHFULNESS", "Only faithfulness prebuilt grader is supported for now"
        prebuilt_config = PrebuiltConfigInput(
            key=PrebuiltCriteriaKey(type),
            model=judge_model,
        )

        # Create grader config
        grader_config = GraderConfigInput(prebuilt=prebuilt_config)

        input_obj = GraderCreateInput(
            name=name or key,
            key=key,
            graderType=GraderTypeEnum.PREBUILT,
            graderConfig=grader_config,
            metric=None,
        )

        return self._client._gql_client.create_grader(
            use_case=self.use_case_key(use_case), input=input_obj
        ).create_grader

    def external_endpoint(
        self,
        *,
        key: str,
        url: str,
        feedback_key: str,
        name: str | None = None,
        use_case: str | None = None,
    ) -> GraderData:
        """
        Creates a new external feedback endpoint grader.

        Args:
            key: Unique key for the grader.
            url: URL of the remote grading service.
            feedback_key: Key for the feedback this grader writes to.
            name: Human-readable grader name. If omitted, derived from key.
            use_case: Explicit use-case key. Falls back to client.default_use_case.
        """
        # Create remote config
        remote_config = RemoteConfigInput(url=url)

        # Create grader config
        grader_config = GraderConfigInput(remote=remote_config)

        input_obj = GraderCreateInput(
            name=name or key,
            key=key,
            graderType=GraderTypeEnum.REMOTE,
            graderConfig=grader_config,
            metric=MetricGetOrCreate(existing=feedback_key),
        )

        return self._client._gql_client.create_grader(
            use_case=self.use_case_key(use_case), input=input_obj
        ).create_grader

    def custom(
        self,
        *,
        key: str,
        feedback_key: str,
        description: str | None = None,
        name: str | None = None,
        use_case: str | None = None,
    ) -> GraderData:
        """
        Creates a new custom grader.

        Args:
            key: Unique key for the grader.
            feedback_key: Key for the feedback this grader writes to.
            description: Description of what grader does.
            name: Human-readable grader name. If omitted, derived from key.
            use_case: Explicit use-case key. Falls back to client.default_use_case.
        """
        grader_config = GraderConfigInput(custom=CustomConfigInput(description=description))

        input_obj = GraderCreateInput(
            name=name or key,
            key=key,
            graderType=GraderTypeEnum.CUSTOM,
            graderConfig=grader_config,
            metric=MetricGetOrCreate(existing=feedback_key),
        )

        return self._client._gql_client.create_grader(
            use_case=self.use_case_key(use_case), input=input_obj
        ).create_grader


class AsyncGraderCreator(AsyncAPIResource, UseCaseResource):  # type: ignore[misc]
    """Async helper class for creating different types of graders with a clean API."""

    def __init__(self, client: AsyncAdaptive) -> None:
        AsyncAPIResource.__init__(self, client)
        UseCaseResource.__init__(self, client)

    async def binary_judge(
        self,
        *,
        key: str,
        criteria: str,
        judge_model: str,
        feedback_key: str,
        name: str | None = None,
        examples: list[input_types.JudgeExampleInput] | None = None,
        use_case: str | None = None,
    ) -> GraderData:
        """
        Creates a new judge-based grader.

        Args:
            key: Unique key for the grader.
            criteria: Natural-language explanation of what should be evaluated as a binary pass/fail.
            judge_model: Model key of the judge model.
            feedback_key: Key for the feedback this grader writes to.
            examples: List of annotated examples for few-shot prompting.
            name: Human-readable grader name. If omitted, derived from key.
            use_case: Explicit use-case key. Falls back to client.default_use_case.
        """
        # Parse examples if provided
        parsed_examples = []
        if examples:
            for ex in examples:
                if not all(k in ex for k in ("input", "output", "passes")):
                    raise ValueError("Each example must contain 'input', 'output', and 'passes' keys")
                input_turns = [JudgeExampleInputTurnEntry(role=t["role"], content=t["content"]) for t in ex["input"]]
                parsed_examples.append(
                    JudgeExampleInput(
                        input=input_turns,
                        output=ex["output"],
                        reasoning=ex.get("reasoning"),
                        **{"pass": bool(ex["passes"])},
                    )
                )

        # Create judge config
        judge_config = JudgeConfigInput(
            model=judge_model,
            criteria=criteria,
            examples=parsed_examples,
        )

        # Create grader config
        grader_config = GraderConfigInput(judge=judge_config)

        input_obj = GraderCreateInput(
            name=name or key,
            key=key,
            graderType=GraderTypeEnum.JUDGE,
            graderConfig=grader_config,
            metric=MetricGetOrCreate(existing=feedback_key),
        )

        return (
            await self._client._gql_client.create_grader(use_case=self.use_case_key(use_case), input=input_obj)
        ).create_grader

    async def prebuilt_judge(
        self,
        *,
        key: str,
        type: Literal["FAITHFULNESS"],
        judge_model: str,
        name: str | None = None,
        use_case: str | None = None,
    ) -> GraderData:
        """
        Creates a new prebuilt grader.

        Args:
            key: Unique key for the grader.
            type: Type of prebuild AI Judge Grader.
            judge_model: Model key of the judge model.
            name: Human-readable grader name. If omitted, derived from key.
            use_case: Explicit use-case key. Falls back to client.default_use_case.
        """
        # Create prebuilt config
        assert type == "FAITHFULNESS", "Only faithfulness prebuilt grader is supported for now"
        prebuilt_config = PrebuiltConfigInput(
            key=PrebuiltCriteriaKey(type),
            model=judge_model,
        )

        # Create grader config
        grader_config = GraderConfigInput(prebuilt=prebuilt_config)

        input_obj = GraderCreateInput(
            name=name or key,
            key=key,
            graderType=GraderTypeEnum.PREBUILT,
            graderConfig=grader_config,
            metric=None,
        )

        return (
            await self._client._gql_client.create_grader(use_case=self.use_case_key(use_case), input=input_obj)
        ).create_grader

    async def external_endpoint(
        self,
        *,
        key: str,
        url: str,
        feedback_key: str,
        name: str | None = None,
        use_case: str | None = None,
    ) -> GraderData:
        """
        Creates a new external feedback endpoint grader.

        Args:
            key: Unique key for the grader.
            url: URL of the remote grading service.
            feedback_key: Existing key for the feedback this grader writes to.
            name: Human-readable grader name. If omitted, derived from key.
            use_case: Explicit use-case key. Falls back to client.default_use_case.
        """
        # Create remote config
        remote_config = RemoteConfigInput(url=url)

        # Create grader config
        grader_config = GraderConfigInput(remote=remote_config)

        input_obj = GraderCreateInput(
            name=name or key,
            key=key,
            graderType=GraderTypeEnum.REMOTE,
            graderConfig=grader_config,
            metric=MetricGetOrCreate(existing=feedback_key),
        )

        return (
            await self._client._gql_client.create_grader(use_case=self.use_case_key(use_case), input=input_obj)
        ).create_grader

    async def custom(
        self,
        *,
        key: str,
        feedback_key: str,
        description: str | None = None,
        name: str | None = None,
        use_case: str | None = None,
    ) -> GraderData:
        """
        Creates a new custom grader.

        Args:
            key: Unique key for the grader.
            feedback_key: Key for the feedback this grader writes to.
            description: Description of what grader does.
            name: Human-readable grader name. If omitted, derived from key.
            use_case: Explicit use-case key. Falls back to client.default_use_case.
        """
        grader_config = GraderConfigInput(custom=CustomConfigInput(description=description))

        input_obj = GraderCreateInput(
            name=name or key,
            key=key,
            graderType=GraderTypeEnum.CUSTOM,
            graderConfig=grader_config,
            metric=MetricGetOrCreate(existing=feedback_key),
        )

        return (
            await self._client._gql_client.create_grader(use_case=self.use_case_key(use_case), input=input_obj)
        ).create_grader


class Graders(SyncAPIResource, UseCaseResource):  # type: ignore[misc]
    """Resource to interact with grader definitions used to evaluate model completions."""

    def __init__(self, client: Adaptive) -> None:
        SyncAPIResource.__init__(self, client)
        UseCaseResource.__init__(self, client)

        # Nested creator for clean API
        self.create = GraderCreator(client)

    def delete(self, *, grader_key: str, use_case: str | None = None) -> bool:
        """Delete a grader. Returns True on success."""
        result = self._gql_client.delete_grader(use_case=self.use_case_key(use_case), id=grader_key).delete_grader
        return result.success

    def lock(self, *, grader_key: str, locked: bool, use_case: str | None = None) -> GraderData:
        """Lock or unlock a grader.

        Args:
            grader_key: ID or key of the grader.
            locked: Whether to lock (True) or unlock (False) the grader.
            use_case: Explicit use-case key. Falls back to client.default_use_case.
        """
        return self._gql_client.lock_grader(
            use_case=self.use_case_key(use_case), id=grader_key, locked=locked
        ).lock_grader

    def list(self, *, use_case: str | None = None) -> Sequence[GraderData]:
        """List all graders for the given use case."""
        return self._gql_client.list_graders(use_case=self.use_case_key(use_case)).graders

    def get(self, *, grader_key: str, use_case: str | None = None) -> GraderData | None:
        """Retrieve a specific grader by ID or key."""
        return self._gql_client.get_grader(id=grader_key, use_case=self.use_case_key(use_case)).grader

    def test_external_endpoint(
        self, url: str
    ) -> TestRemoteEnvTestRemoteEnvRemoteEnvTestOnline | TestRemoteEnvTestRemoteEnvRemoteEnvTestOffline:
        """Test external endpoint to check if it is reachable from Adaptive and returns a valid response."""
        return self._gql_client.test_remote_env(RemoteEnvCreate(url=url)).test_remote_env


class AsyncGraders(AsyncAPIResource, UseCaseResource):  # type: ignore[misc]
    """Asynchronous resource to interact with grader definitions used to evaluate model completions."""

    def __init__(self, client: AsyncAdaptive) -> None:
        AsyncAPIResource.__init__(self, client)
        UseCaseResource.__init__(self, client)

        # Nested creator for clean API
        self.create = AsyncGraderCreator(client)

    async def delete(self, *, grader_key: str, use_case: str | None = None) -> bool:
        """Delete a grader. Returns True on success."""
        result = (
            await self._gql_client.delete_grader(use_case=self.use_case_key(use_case), id=grader_key)
        ).delete_grader
        return result.success

    async def lock(self, *, grader_key: str, locked: bool, use_case: str | None = None) -> GraderData:
        """Lock or unlock a grader."""
        return (
            await self._gql_client.lock_grader(use_case=self.use_case_key(use_case), id=grader_key, locked=locked)
        ).lock_grader

    async def list(self, *, use_case: str | None = None) -> Sequence[GraderData]:
        """List all graders for the given use case."""
        return (await self._gql_client.list_graders(use_case=self.use_case_key(use_case))).graders

    async def get(self, *, grader_key: str, use_case: str | None = None) -> GraderData | None:
        """Retrieve a specific grader by ID or key."""
        return (await self._gql_client.get_grader(id=grader_key, use_case=self.use_case_key(use_case))).grader

    async def test_external_endpoint(
        self, url: str
    ) -> TestRemoteEnvTestRemoteEnvRemoteEnvTestOnline | TestRemoteEnvTestRemoteEnvRemoteEnvTestOffline:
        """Test external endpoint to check if it is reachable from Adaptive and returns a valid response."""
        return (await self._gql_client.test_remote_env(RemoteEnvCreate(url=url))).test_remote_env
