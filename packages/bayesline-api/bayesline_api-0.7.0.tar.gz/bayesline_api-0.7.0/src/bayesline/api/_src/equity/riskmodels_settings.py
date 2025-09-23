import datetime as dt
import os
from itertools import zip_longest
from typing import Annotated, Any, Literal

from pydantic import BaseModel, BeforeValidator, Field, PositiveInt

from bayesline.api._src.equity.exposure_settings import ExposureSettings
from bayesline.api._src.equity.modelconstruction_settings import (
    ModelConstructionSettings,
)
from bayesline.api._src.equity.universe_settings import UniverseSettings
from bayesline.api._src.registry import Settings, SettingsMenu, SettingsTypeMetaData

GetModelMode = Literal[
    "compute",
    "compute-and-persist",
    "get-or-compute",
    "get-or-compute-and-persist",
    "get-or-fail",
]


class FactorRiskModelMetadata(BaseModel):
    """Metadata for a factor risk model.

    Contains information about the model's configuration, status, and update history.
    """

    name: str
    id: int
    risk_dataset: str | None

    settings_created_on: dt.datetime
    settings_last_updated_on: dt.datetime

    model_last_updated_on: dt.datetime | None
    model_data_date: dt.date | None
    model_risk_dataset_digest: str | None

    can_update: bool
    current_data_date: dt.date | None
    current_risk_dataset_digest: str | None


def _ensure_list(value: Any) -> Any:
    if isinstance(value, list | tuple):
        return value
    return [value]


class FactorRiskModelSettings(Settings):
    """Define all settings needed to build a factor risk model."""

    universe: Annotated[
        list[str | int | UniverseSettings],
        BeforeValidator(_ensure_list),
        Field(
            description="The universe to build the factor risk model on.",
            min_length=1,
            max_length=1,
        ),
        SettingsTypeMetaData[list[str | int | UniverseSettings]](
            references=UniverseSettings,
            extractor=lambda x: [r for r in x if not isinstance(r, UniverseSettings)],
        ),
    ]

    exposures: Annotated[
        list[str | int | ExposureSettings],
        BeforeValidator(_ensure_list),
        Field(
            description="The exposures to build the factor risk model on.",
            min_length=1,
        ),
        SettingsTypeMetaData[str | int | ExposureSettings](
            references=ExposureSettings,
            extractor=lambda x: [r for r in x if not isinstance(r, ExposureSettings)],
        ),
    ] = [ExposureSettings()]

    modelconstruction: Annotated[
        list[str | int | ModelConstructionSettings],
        BeforeValidator(_ensure_list),
        Field(
            description="The model construction settings to use for the factor risk model.",
            min_length=1,
        ),
        SettingsTypeMetaData[str | int | ModelConstructionSettings](
            references=ModelConstructionSettings,
            extractor=lambda x: [
                r for r in x if not isinstance(r, ModelConstructionSettings)
            ],
        ),
    ] = [ModelConstructionSettings()]
    halflife_idio_vra: PositiveInt | None = Field(
        None,
        description=(
            "The half-life for the idio adjustment. "
            "If None, no adjustment is applied."
        ),
    )


class FactorRiskModelSettingsMenu(SettingsMenu, frozen=True, extra="forbid"):
    """Define available settings to build a factor risk model."""

    def describe(self, settings: FactorRiskModelSettings | None = None) -> str:
        """Describe the settings in a human-readable format.

        Parameters
        ----------
        settings : FactorRiskModelSettings | None, default=None
            The settings to describe. If None, returns a generic description.

        Returns
        -------
        str
            A human-readable description of the settings.
        """
        if settings:
            n_stages = len(settings.exposures)
            if n_stages == 1:
                result = [
                    "Universe: " + str(settings.universe[0]),
                    "Exposures: " + str(settings.exposures[0]),
                    "Model Construction: " + str(settings.modelconstruction[0]),
                ]
                return os.linesep.join(result)
            else:
                result = []
                for i, (universe, exposures, modelconstruction) in enumerate(
                    zip_longest(
                        settings.universe,
                        settings.exposures,
                        settings.modelconstruction,
                        fillvalue="same as previous stage",
                    )
                ):
                    result.append(f"Stage {i + 1}:")
                    result.append("  Universe: " + str(universe))
                    result.append("  Exposures: " + str(exposures))
                    result.append("  Model Construction: " + str(modelconstruction))
                return os.linesep.join(result)
        else:
            return "This settings menu has no description."

    def validate_settings(self, settings: FactorRiskModelSettings) -> None:
        """Validate that the settings are consistent.

        Checks that the universe, exposures and model construction settings line up
        properly across all stages.

        Parameters
        ----------
        settings : FactorRiskModelSettings
            The settings to validate.

        Raises
        ------
        ValueError
            If the settings are inconsistent.
        """
        # check that the universe, exposures and model construction settings line up
        n_stages = len(settings.exposures)
        if len(settings.universe) not in (n_stages, 1):
            raise ValueError(
                f"Universe settings must be either one or {n_stages} settings."
            )
        if len(settings.modelconstruction) not in (n_stages, 1):
            raise ValueError(
                f"Model construction settings must be either one or {n_stages} settings."
            )
