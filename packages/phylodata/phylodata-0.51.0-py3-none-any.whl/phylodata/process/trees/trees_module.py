from io import BytesIO

import streamlit as st

from phylodata.data_types import Trees
from phylodata.errors import ValidationError
from phylodata.process.module import Module
from phylodata.process.trees.parse_trees import parse_trees


class TreesModule(Module[Trees | None]):
    def ui(self): ...

    def validate(self): ...

    def parse(
        self, beast2_trees: BytesIO | None, other_files: list[BytesIO]
    ) -> Trees | None:
        st.text("Processing the trees...")

        if beast2_trees:
            return parse_trees(beast2_trees)

        for file in other_files:
            try:
                return parse_trees(file)
            except ValidationError:
                pass
