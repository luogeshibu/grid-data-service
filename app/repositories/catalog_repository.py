from __future__ import annotations

from typing import Any

from app.db.registry import DatabaseRegistry
from app.models.profile import ProfileConfig


class CatalogRepository:
    """Read-only Oracle repository for the D5000 power equipment model.

    All table names in this module are static allow-listed identifiers. User input
    is passed only as bind variables; no user-controlled SQL is constructed.
    """

    _SPECS: dict[str, dict[str, Any]] = {
        "substation": {
            "table": "SUBSTATION",
            "station": "NULL",
            "bay": "NULL",
            "voltage": "NULL",
            "base_voltage": "bv_id",
            "status": "status",
            "run_state": "NULL",
            "parent": "NULL",
            "parent_type": "NULL",
            "attributes": ["subarea_id", "zone_no", "region_id", "latitude", "longitude"],
        },
        "voltage_level": {
            "table": "VOLTAGELEVEL",
            "station": "st_id",
            "bay": "NULL",
            "voltage": "id",
            "base_voltage": "bv_id",
            "status": "NULL",
            "run_state": "NULL",
            "parent": "st_id",
            "parent_type": "substation",
            "attributes": ["st_id", "bv_id"],
        },
        "bay": {
            "table": "BAY",
            "station": "st_id",
            "bay": "id",
            "voltage": "vl_id",
            "base_voltage": "bv_id",
            "status": "bay_state",
            "run_state": "NULL",
            "parent": "CASE WHEN vl_id IS NOT NULL THEN vl_id ELSE st_id END",
            "parent_type": "CASE WHEN vl_id IS NOT NULL THEN 'voltage_level' ELSE 'substation' END",
            "attributes": ["st_id", "vl_id", "bv_id", "bay_type", "bay_config", "bay_dev_state"],
        },
        "breaker": {
            "table": "BREAKER",
            "station": "st_id",
            "bay": "bay_id",
            "voltage": "vl_id",
            "base_voltage": "bv_id",
            "status": "status",
            "run_state": "run_state",
            "parent": "bay_id",
            "parent_type": "bay",
            "attributes": ["brk_type", "nom_state", "ind", "jnd", "amprating", "inom", "vnom"],
        },
        "disconnector": {
            "table": "DISCONNECTOR",
            "station": "st_id",
            "bay": "bay_id",
            "voltage": "vl_id",
            "base_voltage": "bv_id",
            "status": "status",
            "run_state": "run_state",
            "parent": "bay_id",
            "parent_type": "bay",
            "attributes": ["discr_type", "nom_state", "funtype", "ind", "jnd"],
        },
        "ground_disconnector": {
            "table": "GROUNDDISCONNECTOR",
            "station": "st_id",
            "bay": "bay_id",
            "voltage": "vl_id",
            "base_voltage": "bv_id",
            "status": "status",
            "run_state": "run_state",
            "parent": "bay_id",
            "parent_type": "bay",
            "attributes": ["gddiscr_type", "nom_state", "nd"],
        },
        "power_transformer": {
            "table": "POWERTRANSFORMER",
            "station": "st_id",
            "bay": "bay_id",
            "voltage": "NULL",
            "base_voltage": "bv_id",
            "status": "status",
            "run_state": "run_state",
            "parent": "st_id",
            "parent_type": "substation",
            "attributes": ["tr_type", "wind_type", "term", "pb", "qb", "p_loss", "q_loss"],
        },
        "transformer_winding": {
            "table": "TRANSFORMERWINDING",
            "station": "st_id",
            "bay": "bay_id",
            "voltage": "vl_id",
            "base_voltage": "bv_id",
            "status": "status",
            "run_state": "run_state",
            "parent": "tr_id",
            "parent_type": "power_transformer",
            "attributes": [
                "tr_id",
                "wind_type",
                "kvnom",
                "mvanom",
                "amprating",
                "tap",
                "p",
                "q",
                "i",
            ],
        },
        "busbar_section": {
            "table": "BUSBARSECTION",
            "station": "st_id",
            "bay": "bay_id",
            "voltage": "vl_id",
            "base_voltage": "bv_id",
            "status": "status",
            "run_state": "run_state",
            "parent": "bay_id",
            "parent_type": "bay",
            "attributes": ["nd", "pos_type", "v", "p_load", "q_load"],
        },
        "energy_consumer": {
            "table": "ENERGYCONSUMER",
            "station": "st_id",
            "bay": "bay_id",
            "voltage": "vl_id",
            "base_voltage": "bv_id",
            "status": "status",
            "run_state": "run_state",
            "parent": "bay_id",
            "parent_type": "bay",
            "attributes": ["ld_type", "pnom", "qnom", "inom", "pmax", "qmax"],
        },
        "single_terminal": {
            "table": "SINGLETERM",
            "station": "st_id",
            "bay": "bay_id",
            "voltage": "vl_id",
            "base_voltage": "bv_id",
            "status": "status",
            "run_state": "run_state",
            "parent": "bay_id",
            "parent_type": "bay",
            "attributes": ["term_type", "nd"],
        },
        "ac_line_segment": {
            "table": "ACLINESEGMENT",
            "station": "NULL",
            "bay": "NULL",
            "voltage": "NULL",
            "base_voltage": "bv_id",
            "status": "status",
            "run_state": "run_state",
            "parent": "NULL",
            "parent_type": "NULL",
            "attributes": ["acline_id", "ist_id", "jst_id", "r", "x", "bch"],
        },
        "ac_line_end": {
            "table": "ACLINEEND",
            "station": "st_id",
            "bay": "bay_id",
            "voltage": "vl_id",
            "base_voltage": "bv_id",
            "status": "status",
            "run_state": "run_state",
            "parent": "bay_id",
            "parent_type": "bay",
            "attributes": ["aclnseg_id", "nd", "v_term", "open_flag", "send_flag"],
        },
        "feeder": {
            "table": "DMS_FEEDER_DEVICE",
            "station": "st_id",
            "bay": "NULL",
            "voltage": "NULL",
            "base_voltage": "NULL",
            "status": "status",
            "run_state": "run_state",
            "parent": "st_id",
            "parent_type": "substation",
            "description": "discribe",
            "attributes": [
                "type",
                "resp_area",
                "load_rate",
                "tr_id",
                "dms_area_id",
                "graph_name",
            ],
        },
    }

    _COMMON_COLUMNS = {
        "id",
        "entity_type",
        "source_id",
        "code",
        "name",
        "description",
        "station_id",
        "bay_id",
        "voltage_level_id",
        "base_voltage_id",
        "status",
        "run_state",
        "rdf_id",
    }
    _EQUIPMENT_TYPES = (
        "breaker",
        "disconnector",
        "ground_disconnector",
        "power_transformer",
        "transformer_winding",
        "energy_consumer",
        "single_terminal",
        "ac_line_segment",
        "ac_line_end",
    )

    @classmethod
    def supported_entity_types(cls) -> tuple[str, ...]:
        return tuple(sorted(cls._SPECS))

    def __init__(self, registry: DatabaseRegistry, profiles: dict[str, ProfileConfig]):
        self.registry = registry
        self.profiles = profiles

    async def _db(self, profile_id: str):
        profile = self.profiles[profile_id]
        return await self.registry.get(profile_id, profile.catalog.source)

    @staticmethod
    def _page_params(offset: int, limit: int) -> dict[str, int]:
        return {"offset": offset, "upper_bound": offset + limit + 1}

    @staticmethod
    def _paged_node_sql(inner_sql: str, order_by: str) -> str:
        fields = (
            "id, parent_id, node_type, entity_type, source_id, code, name, "
            'description, "level", sort_order, has_children, status, run_state'
        )
        return f"""
        SELECT {fields}
        FROM (
            SELECT ordered_rows.*, ROWNUM AS row_number
            FROM (
                {inner_sql}
                ORDER BY {order_by}
            ) ordered_rows
            WHERE ROWNUM <= :upper_bound
        )
        WHERE row_number > :offset
        """

    @staticmethod
    def _paged_directory_sql(inner_sql: str, order_by: str) -> str:
        fields = (
            "id, parent_id, node_type, entity_type, source_id, code, name, description, "
            '"level", sort_order, has_children, status, run_state, type, voltage, area, '
            "substation, bay, feeder, equipment, total_count"
        )
        return f"""
        SELECT {fields}
        FROM (
            SELECT ordered_rows.*, ROWNUM AS row_number
            FROM (
                {inner_sql}
                ORDER BY {order_by}
            ) ordered_rows
            WHERE ROWNUM <= :upper_bound
        )
        WHERE row_number > :offset
        """

    async def roots(self, profile_id: str, offset: int, limit: int) -> list[dict[str, Any]]:
        inner_sql = """
        SELECT
            'substation:' || TO_CHAR(s.id) AS id,
            CAST(NULL AS VARCHAR2(128)) AS parent_id,
            'substation' AS node_type,
            'substation' AS entity_type,
            TO_CHAR(s.id) AS source_id,
            NVL(s.code, TO_CHAR(s.id)) AS code,
            s.name AS name,
            s.describe AS description,
            0 AS "level",
            s.id AS sort_order,
            CASE WHEN EXISTS (SELECT 1 FROM voltagelevel vl WHERE vl.st_id = s.id)
                    OR EXISTS (SELECT 1 FROM bay b WHERE b.st_id = s.id)
                    OR EXISTS (SELECT 1 FROM powertransformer pt WHERE pt.st_id = s.id)
                    OR EXISTS (SELECT 1 FROM dms_feeder_device f WHERE f.st_id = s.id)
                 THEN 1 ELSE 0 END AS has_children,
            s.status AS status,
            CAST(NULL AS NUMBER) AS run_state
        FROM substation s
        """
        sql = self._paged_node_sql(inner_sql, "UPPER(name), sort_order")
        db = await self._db(profile_id)
        return await db.execute(sql, self._page_params(offset, limit))

    async def children(
        self,
        profile_id: str,
        parent_type: str,
        parent_source_id: int,
        offset: int,
        limit: int,
    ) -> list[dict[str, Any]]:
        inner_sql = """
        SELECT * FROM (
            SELECT
                'voltage_level:' || TO_CHAR(vl.id) AS id,
                'substation:' || TO_CHAR(vl.st_id) AS parent_id,
                'voltage_level' AS node_type, 'voltage_level' AS entity_type,
                TO_CHAR(vl.id) AS source_id, NVL(vl.code, TO_CHAR(vl.id)) AS code,
                vl.name AS name, vl.describe AS description, 1 AS "level", vl.id AS sort_order,
                1 AS has_children, CAST(NULL AS NUMBER) AS status, CAST(NULL AS NUMBER) AS run_state
            FROM voltagelevel vl
            WHERE :parent_type = 'substation' AND vl.st_id = :parent_source_id

            UNION ALL
            SELECT
                'bay:' || TO_CHAR(b.id),
                CASE WHEN b.vl_id IS NULL THEN 'substation:' || TO_CHAR(b.st_id)
                     ELSE 'voltage_level:' || TO_CHAR(b.vl_id) END,
                'bay', 'bay', TO_CHAR(b.id), NVL(b.code, TO_CHAR(b.id)), b.name, b.describe,
                CASE WHEN b.vl_id IS NULL THEN 1 ELSE 2 END, b.id,
                CASE WHEN b.dev_num > 0 OR b.brk_num > 0 OR b.disc_num > 0 THEN 1 ELSE 0 END,
                b.bay_state, CAST(NULL AS NUMBER)
            FROM bay b
            WHERE (:parent_type = 'voltage_level' AND b.vl_id = :parent_source_id)
               OR (:parent_type = 'substation' AND b.st_id = :parent_source_id AND b.vl_id IS NULL)

            UNION ALL
            SELECT
                'power_transformer:' || TO_CHAR(pt.id), 'substation:' || TO_CHAR(pt.st_id),
                'power_transformer', 'power_transformer', TO_CHAR(pt.id),
                NVL(pt.code, TO_CHAR(pt.id)),
                pt.name, pt.describe, 1, pt.id,
                CASE WHEN EXISTS (SELECT 1 FROM transformerwinding tw WHERE tw.tr_id = pt.id)
                     THEN 1 ELSE 0 END, pt.status, pt.run_state
            FROM powertransformer pt
            WHERE :parent_type = 'substation' AND pt.st_id = :parent_source_id

            UNION ALL
            SELECT
                'feeder:' || TO_CHAR(f.id), 'substation:' || TO_CHAR(f.st_id),
                'feeder', 'feeder', TO_CHAR(f.id), NVL(f.code, TO_CHAR(f.id)),
                f.name, f.discribe, 1, f.id, 0, f.status, f.run_state
            FROM dms_feeder_device f
            WHERE :parent_type = 'substation' AND f.st_id = :parent_source_id

            UNION ALL
            SELECT
                'transformer_winding:' || TO_CHAR(tw.id), 'power_transformer:' || TO_CHAR(tw.tr_id),
                'transformer_winding', 'transformer_winding', TO_CHAR(tw.id),
                NVL(tw.code, TO_CHAR(tw.id)),
                tw.name, tw.describe, 2, tw.id, 0, tw.status, tw.run_state
            FROM transformerwinding tw
            WHERE :parent_type = 'power_transformer' AND tw.tr_id = :parent_source_id

            UNION ALL
            SELECT
                'breaker:' || TO_CHAR(d.id), 'bay:' || TO_CHAR(d.bay_id),
                'breaker', 'breaker', TO_CHAR(d.id), NVL(d.code, TO_CHAR(d.id)), d.name, d.describe,
                3, d.id, 0, d.status, d.run_state
            FROM breaker d
            WHERE :parent_type = 'bay' AND d.bay_id = :parent_source_id

            UNION ALL
            SELECT
                'disconnector:' || TO_CHAR(d.id), 'bay:' || TO_CHAR(d.bay_id),
                'disconnector', 'disconnector', TO_CHAR(d.id), NVL(d.code, TO_CHAR(d.id)),
                d.name, d.describe,
                3, d.id, 0, d.status, d.run_state
            FROM disconnector d
            WHERE :parent_type = 'bay' AND d.bay_id = :parent_source_id

            UNION ALL
            SELECT
                'ground_disconnector:' || TO_CHAR(d.id), 'bay:' || TO_CHAR(d.bay_id),
                'ground_disconnector', 'ground_disconnector', TO_CHAR(d.id),
                NVL(d.code, TO_CHAR(d.id)), d.name, d.describe,
                3, d.id, 0, d.status, d.run_state
            FROM grounddisconnector d
            WHERE :parent_type = 'bay' AND d.bay_id = :parent_source_id

            UNION ALL
            SELECT
                'busbar_section:' || TO_CHAR(d.id), 'bay:' || TO_CHAR(d.bay_id),
                'busbar_section', 'busbar_section', TO_CHAR(d.id), NVL(d.code, TO_CHAR(d.id)),
                d.name, d.describe,
                3, d.id, 0, d.status, d.run_state
            FROM busbarsection d
            WHERE :parent_type = 'bay' AND d.bay_id = :parent_source_id

            UNION ALL
            SELECT
                'energy_consumer:' || TO_CHAR(d.id), 'bay:' || TO_CHAR(d.bay_id),
                'energy_consumer', 'energy_consumer', TO_CHAR(d.id), NVL(d.code, TO_CHAR(d.id)),
                d.name, d.describe,
                3, d.id, 0, d.status, d.run_state
            FROM energyconsumer d
            WHERE :parent_type = 'bay' AND d.bay_id = :parent_source_id

            UNION ALL
            SELECT
                'single_terminal:' || TO_CHAR(d.id), 'bay:' || TO_CHAR(d.bay_id),
                'single_terminal', 'single_terminal', TO_CHAR(d.id), NVL(d.code, TO_CHAR(d.id)),
                d.name, d.describe,
                3, d.id, 0, d.status, d.run_state
            FROM singleterm d
            WHERE :parent_type = 'bay' AND d.bay_id = :parent_source_id

            UNION ALL
            SELECT
                'ac_line_end:' || TO_CHAR(d.id), 'bay:' || TO_CHAR(d.bay_id),
                'ac_line_end', 'ac_line_end', TO_CHAR(d.id), NVL(d.code, TO_CHAR(d.id)),
                d.name, d.describe,
                3, d.id, 0, d.status, d.run_state
            FROM aclineend d
            WHERE :parent_type = 'bay' AND d.bay_id = :parent_source_id
        )
        """
        sql = self._paged_node_sql(inner_sql, '"level", UPPER(name), sort_order')
        params = {
            "parent_type": parent_type,
            "parent_source_id": parent_source_id,
            **self._page_params(offset, limit),
        }
        db = await self._db(profile_id)
        return await db.execute(sql, params)

    async def detail(
        self,
        profile_id: str,
        entity_type: str,
        source_id: int,
    ) -> dict[str, Any] | None:
        spec = self._SPECS.get(entity_type)
        if spec is None:
            raise KeyError(f"Unsupported entity type: {entity_type}")

        attribute_sql = ", ".join(
            f"{column.replace(' ', '_')} AS attr_{column.replace(' ', '_')}"
            for column in spec["attributes"]
            if " " not in column
        )
        if attribute_sql:
            attribute_sql = ", " + attribute_sql

        sql = f"""
        SELECT
            '{entity_type}' AS entity_type,
            TO_CHAR(id) AS source_id,
            NVL(code, TO_CHAR(id)) AS code,
            name,
            {spec.get("description", "describe")} AS description,
            TO_CHAR({spec["station"]}) AS station_id,
            TO_CHAR({spec["bay"]}) AS bay_id,
            TO_CHAR({spec["voltage"]}) AS voltage_level_id,
            TO_CHAR({spec["base_voltage"]}) AS base_voltage_id,
            {spec["status"]} AS status,
            {spec["run_state"]} AS run_state,
            rdf_id{attribute_sql}
        FROM {spec["table"]}
        WHERE id = :source_id
        """
        db = await self._db(profile_id)
        row = await db.execute(sql, {"source_id": source_id}, result="one")
        if row is None:
            return None
        return row

    @classmethod
    def equipment_types(cls) -> tuple[str, ...]:
        return cls._EQUIPMENT_TYPES

    @staticmethod
    def _node_level(entity_type: str) -> str:
        return {
            "substation": "0",
            "voltage_level": "1",
            "power_transformer": "1",
            "feeder": "1",
            "bay": "2",
            "transformer_winding": "2",
        }.get(entity_type, "3")

    @staticmethod
    def _node_parent_expression(entity_type: str, spec: dict[str, Any], alias: str = "t") -> str:
        if entity_type == "bay":
            return (
                f"CASE WHEN {alias}.vl_id IS NOT NULL THEN "
                f"'voltage_level:' || TO_CHAR({alias}.vl_id) "
                f"WHEN {alias}.st_id IS NOT NULL THEN 'substation:' || TO_CHAR({alias}.st_id) END"
            )
        parent_id = spec["parent"]
        if parent_id == "NULL":
            return "CAST(NULL AS VARCHAR2(128))"
        return (
            f"CASE WHEN {alias}.{parent_id} IS NULL THEN NULL ELSE "
            f"'{spec['parent_type']}:' || TO_CHAR({alias}.{parent_id}) END"
        )

    @staticmethod
    def _node_has_children_expression(entity_type: str, alias: str = "t") -> str:
        return {
            "substation": (
                f"CASE WHEN EXISTS (SELECT 1 FROM voltagelevel x WHERE x.st_id = {alias}.id) "
                f"OR EXISTS (SELECT 1 FROM bay x WHERE x.st_id = {alias}.id) "
                f"OR EXISTS (SELECT 1 FROM powertransformer x WHERE x.st_id = {alias}.id) "
                f"OR EXISTS (SELECT 1 FROM dms_feeder_device x WHERE x.st_id = {alias}.id) "
                "THEN 1 ELSE 0 END"
            ),
            "voltage_level": (
                f"CASE WHEN EXISTS (SELECT 1 FROM bay x WHERE x.vl_id = {alias}.id) "
                "THEN 1 ELSE 0 END"
            ),
            "bay": (
                f"CASE WHEN NVL({alias}.dev_num, 0) > 0 OR NVL({alias}.brk_num, 0) > 0 "
                f"OR NVL({alias}.disc_num, 0) > 0 OR NVL({alias}.gdisc_num, 0) > 0 "
                "THEN 1 ELSE 0 END"
            ),
            "power_transformer": (
                f"CASE WHEN EXISTS (SELECT 1 FROM transformerwinding x "
                f"WHERE x.tr_id = {alias}.id) THEN 1 ELSE 0 END"
            ),
        }.get(entity_type, "0")

    @classmethod
    def _directory_context(
        cls, entity_type: str, spec: dict[str, Any], alias: str = "t"
    ) -> dict[str, str]:
        joins: list[str] = []
        if entity_type == "substation":
            joins.extend(
                [
                    f"LEFT JOIN basevoltage bv ON bv.id = {alias}.bv_id",
                    f"LEFT JOIN subcontrolarea sca ON sca.id = {alias}.subarea_id",
                ]
            )
            return {
                "joins": " ".join(joins),
                "type": "CAST(NULL AS VARCHAR2(128))",
                "voltage": "bv.name",
                "area": f"NVL(sca.name, NVL(sca.code, TO_CHAR({alias}.subarea_id)))",
                "substation": "CAST(NULL AS VARCHAR2(128))",
                "bay": "CAST(NULL AS VARCHAR2(128))",
            }

        if entity_type == "feeder":
            joins.extend(
                [
                    f"LEFT JOIN substation s ON s.id = {alias}.st_id",
                    f"LEFT JOIN bay b ON b.st_id = {alias}.st_id "
                    f"AND UPPER(b.name) = UPPER({alias}.name)",
                    "LEFT JOIN voltagelevel vl ON vl.id = b.vl_id",
                    "LEFT JOIN basevoltage bv ON bv.id = b.bv_id",
                ]
            )
            return {
                "joins": " ".join(joins),
                "type": "CAST(NULL AS VARCHAR2(128))",
                "voltage": "REGEXP_SUBSTR(NVL(vl.name, bv.name), '[^/]+$')",
                "area": "CAST(NULL AS VARCHAR2(128))",
                "substation": "s.name",
                "bay": "b.name",
            }

        station_expression = "CAST(NULL AS VARCHAR2(128))"
        bay_expression = "CAST(NULL AS VARCHAR2(128))"
        voltage_expression = "CAST(NULL AS VARCHAR2(128))"
        if spec["station"] != "NULL":
            joins.append(f"LEFT JOIN substation s ON s.id = {alias}.{spec['station']}")
            station_expression = "s.name"
        if spec["bay"] != "NULL":
            joins.append(f"LEFT JOIN bay b ON b.id = {alias}.{spec['bay']}")
            bay_expression = "b.name"
        if spec["voltage"] != "NULL":
            joins.append(f"LEFT JOIN voltagelevel vl ON vl.id = {alias}.{spec['voltage']}")
            voltage_expression = "vl.name"
        if spec["base_voltage"] != "NULL":
            joins.append(f"LEFT JOIN basevoltage bv ON bv.id = {alias}.{spec['base_voltage']}")
            voltage_expression = f"NVL({voltage_expression}, bv.name)"
        elif spec["bay"] != "NULL":
            joins.append("LEFT JOIN voltagelevel vl_bay ON vl_bay.id = b.vl_id")
            voltage_expression = "vl_bay.name"
        if voltage_expression != "CAST(NULL AS VARCHAR2(128))":
            voltage_expression = f"REGEXP_SUBSTR({voltage_expression}, '[^/]+$')"
        type_expression = {
            "bay": f"TO_CHAR({alias}.bay_type)",
            "busbar_section": f"TO_CHAR({alias}.pos_type)",
        }.get(entity_type, "CAST(NULL AS VARCHAR2(128))")
        return {
            "joins": " ".join(joins),
            "type": type_expression,
            "voltage": voltage_expression,
            "area": "CAST(NULL AS VARCHAR2(128))",
            "substation": station_expression,
            "bay": bay_expression,
        }

    async def list_nodes(
        self,
        profile_id: str,
        entity_type: str,
        station_id: int | None,
        bay_id: int | None,
        query: str | None,
        offset: int,
        limit: int,
    ) -> list[dict[str, Any]]:
        spec = self._SPECS.get(entity_type)
        if spec is None:
            raise KeyError(f"Unsupported entity type: {entity_type}")

        conditions = ["1 = 1"]
        params: dict[str, Any] = {}
        station_column = spec["station"]
        bay_column = spec["bay"]
        if station_id is not None:
            if station_column == "NULL":
                conditions.append("1 = 0")
            else:
                conditions.append(f"t.{station_column} = :station_id")
                params["station_id"] = station_id
        if bay_id is not None:
            if bay_column == "NULL":
                conditions.append("1 = 0")
            else:
                conditions.append(f"t.{bay_column} = :bay_id")
                params["bay_id"] = bay_id
        if query:
            conditions.append(
                "(UPPER(t.name) LIKE :node_pattern "
                "OR UPPER(NVL(t.code, '')) LIKE :node_pattern)"
            )
            params["node_pattern"] = f"%{query.upper()}%"

        description_column = spec.get("description", "describe")
        context = self._directory_context(entity_type, spec)
        parent_expression = self._node_parent_expression(entity_type, spec)
        status_expression = (
            "CAST(NULL AS NUMBER)" if spec["status"] == "NULL" else f"t.{spec['status']}"
        )
        run_state_expression = (
            "CAST(NULL AS NUMBER)"
            if spec["run_state"] == "NULL"
            else f"t.{spec['run_state']}"
        )
        inner_sql = f"""
        SELECT
            '{entity_type}:' || TO_CHAR(t.id) AS id,
            {parent_expression} AS parent_id,
            '{entity_type}' AS node_type,
            '{entity_type}' AS entity_type,
            TO_CHAR(t.id) AS source_id,
            NVL(t.code, TO_CHAR(t.id)) AS code,
            t.name AS name,
            t.{description_column} AS description,
            {self._node_level(entity_type)} AS "level",
            t.id AS sort_order,
            {self._node_has_children_expression(entity_type)} AS has_children,
            {status_expression} AS status,
            {run_state_expression} AS run_state,
            {context['type']} AS type,
            {context['voltage']} AS voltage,
            {context['area']} AS area,
            {context['substation']} AS substation,
            {context['bay']} AS bay,
            CAST(NULL AS VARCHAR2(128)) AS feeder,
            CAST(NULL AS VARCHAR2(128)) AS equipment,
            COUNT(*) OVER() AS total_count
        FROM {spec['table']} t
        {context['joins']}
        WHERE {' AND '.join(conditions)}
        """
        sql = self._paged_directory_sql(inner_sql, '"level", UPPER(t.name), t.id')
        db = await self._db(profile_id)
        return await db.execute(sql, {**params, **self._page_params(offset, limit)})

    async def list_equipment(
        self,
        profile_id: str,
        entity_type: str | None,
        station_id: int | None,
        bay_id: int | None,
        query: str | None,
        offset: int,
        limit: int,
    ) -> list[dict[str, Any]]:
        types = (entity_type,) if entity_type else self._EQUIPMENT_TYPES
        branches: list[str] = []
        params: dict[str, Any] = {}
        for kind in types:
            spec = self._SPECS[kind]
            conditions = ["1 = 1"]
            if station_id is not None:
                if spec["station"] == "NULL":
                    conditions.append("1 = 0")
                else:
                    conditions.append(f"t.{spec['station']} = :station_id")
                    params["station_id"] = station_id
            if bay_id is not None:
                if spec["bay"] == "NULL":
                    conditions.append("1 = 0")
                else:
                    conditions.append(f"t.{spec['bay']} = :bay_id")
                    params["bay_id"] = bay_id
            if query:
                conditions.append(
                    "(UPPER(t.name) LIKE :equipment_pattern "
                    "OR UPPER(NVL(t.code, '')) LIKE :equipment_pattern)"
                )
                params["equipment_pattern"] = f"%{query.upper()}%"
            description_column = spec.get("description", "describe")
            context = self._directory_context(kind, spec)
            parent_expression = self._node_parent_expression(kind, spec)
            status_expression = (
                "CAST(NULL AS NUMBER)" if spec["status"] == "NULL" else f"t.{spec['status']}"
            )
            run_state_expression = (
                "CAST(NULL AS NUMBER)"
                if spec["run_state"] == "NULL"
                else f"t.{spec['run_state']}"
            )
            branches.append(
                f"""
                SELECT
                    '{kind}:' || TO_CHAR(t.id) AS id,
                    {parent_expression} AS parent_id,
                    '{kind}' AS node_type,
                    '{kind}' AS entity_type,
                    TO_CHAR(t.id) AS source_id,
                    NVL(t.code, TO_CHAR(t.id)) AS code,
                    t.name AS name,
                    t.{description_column} AS description,
                    {self._node_level(kind)} AS "level",
                    t.id AS sort_order,
                    {self._node_has_children_expression(kind)} AS has_children,
                    {status_expression} AS status,
                    {run_state_expression} AS run_state,
                    '{kind}' AS type,
                    {context['voltage']} AS voltage,
                    {context['area']} AS area,
                    {context['substation']} AS substation,
                    {context['bay']} AS bay,
                    CAST(NULL AS VARCHAR2(128)) AS feeder,
                    CAST(NULL AS VARCHAR2(128)) AS equipment,
                    CAST(NULL AS NUMBER) AS total_count
                FROM {spec['table']} t
                {context['joins']}
                WHERE {' AND '.join(conditions)}
                """
            )
        inner_sql = (
            "SELECT id, parent_id, node_type, entity_type, source_id, code, name, description, "
            '"level", sort_order, has_children, status, run_state, type, voltage, area, '
            "substation, bay, feeder, equipment, COUNT(*) OVER() AS total_count "
            "FROM ("
            + " UNION ALL ".join(branches)
            + ") equipment_rows"
        )
        sql = self._paged_directory_sql(inner_sql, '"level", UPPER(name), sort_order')
        db = await self._db(profile_id)
        return await db.execute(sql, {**params, **self._page_params(offset, limit)})

    async def search(
        self,
        profile_id: str,
        text: str,
        entity_type: str | None,
        offset: int,
        limit: int,
    ) -> list[dict[str, Any]]:
        branches = []
        for kind, spec in self._SPECS.items():
            if kind == "bay":
                parent_expression = (
                    "CASE WHEN t.vl_id IS NOT NULL THEN 'voltage_level:' || TO_CHAR(t.vl_id) "
                    "WHEN t.st_id IS NOT NULL THEN 'substation:' || TO_CHAR(t.st_id) END"
                )
            else:
                parent_id = spec["parent"]
                parent_type = spec["parent_type"]
                parent_expression = (
                    f"CASE WHEN {parent_id} IS NULL THEN NULL "
                    f"ELSE '{parent_type}:' || TO_CHAR({parent_id}) END"
                )
            level_expression = {
                "substation": "0",
                "voltage_level": "1",
                "bay": "2",
                "power_transformer": "1",
                "transformer_winding": "2",
                "feeder": "1",
            }.get(kind, "3")
            has_children_expression = {
                "substation": (
                    "CASE WHEN EXISTS (SELECT 1 FROM voltagelevel x WHERE x.st_id = t.id) "
                    "OR EXISTS (SELECT 1 FROM bay x WHERE x.st_id = t.id) "
                    "OR EXISTS (SELECT 1 FROM powertransformer x WHERE x.st_id = t.id) "
                    "THEN 1 ELSE 0 END"
                ),
                "voltage_level": (
                    "CASE WHEN EXISTS (SELECT 1 FROM bay x WHERE x.vl_id = t.id) "
                    "THEN 1 ELSE 0 END"
                ),
                "bay": (
                    "CASE WHEN NVL(t.dev_num, 0) > 0 OR NVL(t.brk_num, 0) > 0 "
                    "OR NVL(t.disc_num, 0) > 0 OR NVL(t.gdisc_num, 0) > 0 "
                    "THEN 1 ELSE 0 END"
                ),
                "power_transformer": (
                    "CASE WHEN EXISTS (SELECT 1 FROM transformerwinding x WHERE x.tr_id = t.id) "
                    "THEN 1 ELSE 0 END"
                ),
                "feeder": "0",
            }.get(kind, "0")
            description_column = spec.get("description", "describe")
            branches.append(
                f"""
                SELECT '{kind}' AS node_type, '{kind}' AS entity_type, TO_CHAR(t.id) AS source_id,
                       '{kind}:' || TO_CHAR(t.id) AS id,
                       NVL(t.code, TO_CHAR(t.id)) AS code, t.name AS name,
                       t.{description_column} AS description,
                       {parent_expression} AS parent_id,
                       {level_expression} AS "level",
                       t.id AS sort_order,
                       {has_children_expression} AS has_children,
                       {spec["status"]} AS status, {spec["run_state"]} AS run_state
                FROM {spec["table"]} t
                WHERE (:entity_type IS NULL OR :entity_type = '{kind}')
                  AND (UPPER(t.name) LIKE :pattern OR UPPER(NVL(t.code, '')) LIKE :pattern)
                """
            )
        inner_sql = "SELECT * FROM (" + " UNION ALL ".join(branches) + ")"
        sql = self._paged_node_sql(inner_sql, "UPPER(name), sort_order")
        db = await self._db(profile_id)
        return await db.execute(
            sql,
            {
                "entity_type": entity_type,
                "pattern": f"%{text.upper()}%",
                **self._page_params(offset, limit),
            },
        )

    async def signals(
        self,
        profile_id: str,
        entity_type: str,
        source_id: int,
        limit: int,
    ) -> list[dict[str, Any]]:
        spec = self._SPECS.get(entity_type)
        if spec is None:
            raise KeyError(f"Unsupported entity type: {entity_type}")
        sql = f"""
        SELECT * FROM (
            SELECT 'digital' AS signal_type, TO_CHAR(mp.id) AS id, TO_CHAR(mp.id) AS source_id,
                   NVL(mp.code, TO_CHAR(mp.id)) AS code, mp.name,
                   mp.datatype AS data_type, mp.value, mp.qual AS quality,
                   TO_CHAR(mp.chg_time) AS changed_at
            FROM measpoint mp
            JOIN {spec["table"]} d ON d.id = :source_id
            WHERE mp.st_id = d.st_id
              AND UPPER(mp.name) LIKE UPPER(d.name) || '/%'
            UNION ALL
            SELECT 'analog', TO_CHAR(ma.id), TO_CHAR(ma.id), NVL(ma.code, TO_CHAR(ma.id)), ma.name,
                   ma.datatype, ma.value, ma.qual, TO_CHAR(ma.chg_time)
            FROM measanalog ma
            JOIN {spec["table"]} d ON d.id = :source_id
            WHERE ma.st_id = d.st_id
              AND UPPER(ma.name) LIKE UPPER(d.name) || '/%'
        )
        ORDER BY UPPER(name), source_id
        FETCH FIRST :limit ROWS ONLY
        """
        db = await self._db(profile_id)
        return await db.execute(sql, {"source_id": source_id, "limit": limit})

    async def signal_list(
        self,
        profile_id: str,
        station_id: int | None,
        entity_type: str | None,
        entity_id: int | None,
        query: str | None,
        offset: int,
        limit: int,
    ) -> list[dict[str, Any]]:
        join_parts: list[str] = []
        conditions: list[str] = []
        params: dict[str, Any] = {}
        if entity_type is not None:
            spec = self._SPECS[entity_type]
            join_parts.append(f"JOIN {spec['table']} d ON d.id = :entity_id")
            conditions.extend(
                [
                    "mp.st_id = d.st_id",
                    "UPPER(mp.name) LIKE UPPER(d.name) || '/%'",
                ]
            )
            params["entity_id"] = entity_id
        if station_id is not None:
            conditions.append("mp.st_id = :signal_station_id")
            params["signal_station_id"] = station_id
        if query:
            conditions.append("UPPER(mp.name) LIKE :signal_pattern")
            params["signal_pattern"] = f"%{query.upper()}%"
        where_sql = " AND ".join(conditions) or "1 = 1"
        join_sql = " ".join(join_parts)
        branches = [
            f"""
            SELECT 'digital' AS signal_type, TO_CHAR(mp.id) AS id, TO_CHAR(mp.id) AS source_id,
                   TO_CHAR(mp.st_id) AS station_id,
                   REGEXP_SUBSTR(mp.name, '^[^/]+') AS owner_name,
                   NVL(mp.code, TO_CHAR(mp.id)) AS code, mp.name,
                   mp.datatype AS data_type, mp.value, mp.qual AS quality,
                   TO_CHAR(mp.chg_time) AS changed_at
            FROM measpoint mp
            {join_sql}
            WHERE {where_sql}
            """,
            f"""
            SELECT 'analog' AS signal_type, TO_CHAR(ma.id) AS id, TO_CHAR(ma.id) AS source_id,
                   TO_CHAR(ma.st_id) AS station_id,
                   REGEXP_SUBSTR(ma.name, '^[^/]+') AS owner_name,
                   NVL(ma.code, TO_CHAR(ma.id)) AS code, ma.name,
                   ma.datatype AS data_type, ma.value, ma.qual AS quality,
                   TO_CHAR(ma.chg_time) AS changed_at
            FROM measanalog ma
            {join_sql.replace('mp.', 'ma.')}
            WHERE {where_sql.replace('mp.', 'ma.')}
            """,
        ]
        inner_sql = (
            "SELECT signal_type, id, source_id, station_id, owner_name, owner_name AS equipment, "
            "code, name, data_type, value, quality, changed_at, COUNT(*) OVER() AS total_count "
            "FROM ("
            + " UNION ALL ".join(branches)
            + ") signal_rows"
        )
        sql = f"""
        SELECT signal_type, id, source_id, station_id, owner_name, equipment, code, name,
               data_type, value, quality, changed_at, total_count
        FROM (
            SELECT ordered_rows.*, ROWNUM AS row_number
            FROM (
                {inner_sql}
                ORDER BY UPPER(name), source_id
            ) ordered_rows
            WHERE ROWNUM <= :upper_bound
        )
        WHERE row_number > :offset
        """
        db = await self._db(profile_id)
        return await db.execute(
            sql,
            {**params, **self._page_params(offset, limit)},
        )

    async def topology(self, profile_id: str, source_id: int, limit: int) -> list[dict[str, Any]]:
        sql = """
        SELECT TO_CHAR(id) AS id,
               TO_CHAR(dev_id) AS source_id,
               TO_CHAR(parent_dev_id) AS target_id,
               TO_CHAR(brk_id) AS breaker_id,
               brk_type AS breaker_type,
               'topology' AS relation_type
        FROM dms_topo_relation_info
        WHERE dev_id = :source_id OR parent_dev_id = :source_id OR brk_id = :source_id
        ORDER BY id
        FETCH FIRST :limit ROWS ONLY
        """
        db = await self._db(profile_id)
        return await db.execute(sql, {"source_id": source_id, "limit": limit})
