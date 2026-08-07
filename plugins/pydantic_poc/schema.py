from pydantic import BaseModel, DirectoryPath, Field, field_validator
from typing import Literal, Annotated
from annotated_types import Gt, Lt, Le, Ge


class SchemaPOCSettings(BaseModel):
    test_directory: DirectoryPath = Field(
        title="Test Directory",
        description="Directory containing the measurement files.",
    )

    test_integer: Annotated[int, Gt(0), Lt(100)] = Field(
        default=10,
        title="Iterations",
        description="Number of optimization iterations.",
        examples=[25],
    )

    test_float: Annotated[float, Ge(0.0), Le(1.0)] = Field(
        default=2,
        title="Threshold",
        description="Threshold used during optimization.",
    )

    test_string: str = Field(
        default="plhl",
        title="Sample Name",
        description="Name used for the generated output.",
    )

    test_enum: Literal["option1", "option2", "option3"] = Field(
        default="option2",
        title="Algorithm",
        description="Optimization algorithm to use.",
    )
