from rekuest_next.structures.default import (
    get_default_structure_registry,
    id_shrink,
)
from rekuest_next.widgets import SearchWidget
from mikro_next.api.schema import (
    Image,
    Snapshot,
    ROI,
    Stage,
    Dataset,
    File,
    RGBContext,
    Mesh,
    Table,
    TableCell,
    TableRow,
    RGBView,
    aget_rgb_view,
    aget_image,
    aget_snapshot,
    aget_roi,
    aget_stage,
    aget_dataset,
    aget_file,
    aget_rgb_context,
    aget_mesh,
    aget_table,
    aget_table_cell,
    aget_table_row,
    SearchRGBViewsQuery,
    SearchImagesQuery,
    SearchSnapshotsQuery,
    SearchRoisQuery,
    SearchStagesQuery,
    SearchDatasetsQuery,
    SearchFilesQuery,
    SearchMeshesQuery,
    SearchTablesQuery,
    SearchTableCellsQuery,
    SearchTableRowsQuery,
)


structure_reg = get_default_structure_registry()

structure_reg.register_as_structure(
    Image,
    identifier="@mikro/image",
    aexpand=aget_image,
    ashrink=id_shrink,
    default_widget=SearchWidget(query=SearchImagesQuery.Meta.document, ward="mikro"),
)
structure_reg.register_as_structure(
    Snapshot,
    identifier="@mikro/snapshot",
    aexpand=aget_snapshot,
    ashrink=id_shrink,
    default_widget=SearchWidget(query=SearchSnapshotsQuery.Meta.document, ward="mikro"),
)

structure_reg.register_as_structure(
    ROI,
    identifier="@mikro/roi",
    aexpand=aget_roi,
    ashrink=id_shrink,
    default_widget=SearchWidget(query=SearchRoisQuery.Meta.document, ward="mikro"),
)
structure_reg.register_as_structure(
    Stage,
    identifier="@mikro/stage",
    aexpand=aget_stage,
    ashrink=id_shrink,
    default_widget=SearchWidget(query=SearchStagesQuery.Meta.document, ward="mikro"),
)
structure_reg.register_as_structure(
    RGBView,
    identifier="@mikro/rgbview",
    aexpand=aget_rgb_view,
    ashrink=id_shrink,
    default_widget=SearchWidget(query=SearchRGBViewsQuery.Meta.document, ward="mikro"),
)


structure_reg.register_as_structure(
    Stage,
    identifier="@mikro/stage",
    aexpand=aget_stage,
    ashrink=id_shrink,
    default_widget=SearchWidget(query=SearchStagesQuery.Meta.document, ward="mikro"),
)
structure_reg.register_as_structure(
    Dataset,
    identifier="@mikro/dataset",
    aexpand=aget_dataset,
    ashrink=id_shrink,
    default_widget=SearchWidget(query=SearchDatasetsQuery.Meta.document, ward="mikro"),
)
structure_reg.register_as_structure(
    File,
    identifier="@mikro/file",
    aexpand=aget_file,
    ashrink=id_shrink,
    default_widget=SearchWidget(query=SearchFilesQuery.Meta.document, ward="mikro"),
)
structure_reg.register_as_structure(
    RGBContext,
    identifier="@mikro/rbgcontext",
    aexpand=aget_rgb_context,
    ashrink=id_shrink,
)


structure_reg.register_as_structure(
    Mesh,
    identifier="@mikro/mesh",
    aexpand=aget_mesh,
    ashrink=id_shrink,
    default_widget=SearchWidget(query=SearchMeshesQuery.Meta.document, ward="mikro"),
)

structure_reg.register_as_structure(
    Table,
    identifier="@mikro/table",
    aexpand=aget_table,
    ashrink=id_shrink,
    default_widget=SearchWidget(query=SearchTablesQuery.Meta.document, ward="mikro"),
)

structure_reg.register_as_structure(
    TableCell,
    identifier="@mikro/tablecell",
    aexpand=aget_table_cell,
    ashrink=id_shrink,
    default_widget=SearchWidget(
        query=SearchTableCellsQuery.Meta.document, ward="mikro"
    ),
)

structure_reg.register_as_structure(
    TableRow,
    identifier="@mikro/tablerow",
    aexpand=aget_table_row,
    ashrink=id_shrink,
    default_widget=SearchWidget(query=SearchTableRowsQuery.Meta.document, ward="mikro"),
)
