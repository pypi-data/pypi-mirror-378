"""Generate JSON schema for EditablePaperWithExperiment data type."""

import msgspec

from phylodata.data_types import (
    EditablePaperWithExperiment,
    NonEditablePaperWithExperiment,
)

editable_schema = msgspec.json.schema(EditablePaperWithExperiment)
with open("../website/src/lib/schema/editableSchema.json", "wb") as f:
    f.write(msgspec.json.format(msgspec.json.encode(editable_schema)))
with open("../java/src/main/resources/schemas/editableSchema.json", "wb") as f:
    f.write(msgspec.json.format(msgspec.json.encode(editable_schema)))

non_editable_schema = msgspec.json.schema(NonEditablePaperWithExperiment)
with open("../website/src/lib/schema/nonEditableSchema.json", "wb") as f:
    f.write(msgspec.json.format(msgspec.json.encode(non_editable_schema)))
with open("../java/src/main/resources/schemas/nonEditableSchema.json", "wb") as f:
    # org.jsonschema2pojo does not like anyof references for nullable fields,
    # hence we manually set the trees to non-nullable. it will still work
    # cause they can just be null in Java
    schema = msgspec.json.format(msgspec.json.encode(non_editable_schema))
    schema = schema.replace(
        b""""trees": {
          "anyOf": [
            {
              "type": "null"
            },
            {
              "$ref": "#/$defs/Trees"
            }
          ]""",
        b""""trees": {
          "$ref": "#/$defs/Trees"
""",
    )
    f.write(schema)
