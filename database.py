import os
import json
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
from shapely import MultiPolygon, wkb
from datetime import datetime, timezone
import aiofiles

SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://heyroute_app:heyroute-db-123@localhost/heyroute"
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

async def get_db():
    async with SessionLocal() as session:
        yield session

async def store_audio_file(file_path: str, file_content: bytes):
    try:
        normalized_file_path = file_path.replace("\\", "/")
        # Save to local storage instead of Supabase
        os.makedirs(os.path.dirname(normalized_file_path), exist_ok=True)
        async with aiofiles.open(normalized_file_path, 'wb') as f:
            await f.write(file_content)
        return {"path": normalized_file_path}
    except Exception as e:
        print(f"Storage Upload Error: {e}")
        return None

async def store_interactions(user_id: str, session_id: str, audio_file_path: str,
    raw_input: str, enhanced_input: str, response: str, conversation_history: list, turn_number: int, intents: dict):
    async with SessionLocal() as db:
        try:
            await db.execute(
                text("""
                INSERT INTO interaction_logs (user_id, session_id, audio_file_path, raw_input, enhanced_input, response, conversation_history, turn_number, intents, created_at)
                VALUES (:u, :s, :a, :r, :e, :res, :c, :t, :i, :ca)
                """),
                {
                    "u": user_id, "s": session_id, "a": audio_file_path, "r": raw_input, "e": enhanced_input,
                    "res": response, "c": json.dumps(conversation_history), "t": turn_number, "i": json.dumps(intents),
                    "ca": datetime.now(timezone.utc)
                }
            )
            await db.commit()
        except Exception as e:
            print(f"Database Insert Error: {e}")

async def store_metrics(user_id: str, session_id: str, save_ms: float, asr_ms: float, cleaning_ms: float, gpt_ms: float, ors_ms: float, intent_detect_ms: float, final_json_ms: float, network_overhead_ms: float, total_turnaround_ms: float):
    async with SessionLocal() as db:
        try:
            await db.execute(
                text("""
                INSERT INTO performance_logs (user_id, session_id, save_ms, asr_ms, cleaning_ms, gpt_ms, ors_ms, intent_detect_ms, final_json_ms, network_overhead_ms, total_turnaround_ms, created_at)
                VALUES (:u, :s, :save, :asr, :clean, :gpt, :ors, :intent, :fj, :net, :tot, :ca)
                """),
                {
                    "u": user_id, "s": session_id, "save": int(save_ms), "asr": int(asr_ms), "clean": int(cleaning_ms),
                    "gpt": int(gpt_ms), "ors": int(ors_ms), "intent": int(intent_detect_ms), "fj": int(final_json_ms),
                    "net": int(network_overhead_ms), "tot": int(total_turnaround_ms), "ca": datetime.now(timezone.utc)
                }
            )
            await db.commit()
        except Exception as e:
            print(f"Error storing metrics: {e}")

async def log_final_json(user_id: str, session_id: str, payload: dict):
    async with SessionLocal() as db:
        try:
            await db.execute(
                text("INSERT INTO final_json_logs (user_id, session_id, json_payload, created_at) VALUES (:u, :s, :p, :c)"),
                {"u": user_id, "s": session_id, "p": json.dumps(payload), "c": datetime.now(timezone.utc)}
            )
            await db.commit()
        except Exception as e:
            print("Final JSON logging failed:", e)

async def log_preference(user_id: str, session_id: str, preference_type: str, preference_value: str, is_accepted: bool):
    async with SessionLocal() as db:
        try:
            await db.execute(
                text("INSERT INTO preference_logs (user_id, session_id, preference_type, preference_value, is_accepted, created_at) VALUES (:u, :s, :pt, :pv, :i, :c)"),
                {"u": user_id, "s": session_id, "pt": preference_type, "pv": preference_value, "i": is_accepted, "c": datetime.now(timezone.utc)}
            )
            await db.commit()
        except Exception as e:
            print("Preference logging failed:", e)

async def log_route_details(user_id: str, session_id: str, event_type: str, origin: str, destination: str, option: str, via: str, distance: str, duration: str):
    async with SessionLocal() as db:
        try:
            await db.execute(
                text("INSERT INTO route_logs (user_id, session_id, event_type, origin, destination, route_option, via_road, distance, duration, created_at) VALUES (:u, :s, :e, :o, :d, :ro, :v, :dist, :dur, :c)"),
                {"u": user_id, "s": session_id, "e": event_type, "o": origin, "d": destination, "ro": option, "v": via, "dist": str(distance), "dur": str(duration), "c": datetime.now(timezone.utc)}
            )
            await db.commit()
        except Exception as e:
            print("Route logging failed:", e)

async def log_session_metadata(user_id: str, session_id: str, device: str, network: str):
    async with SessionLocal() as db:
        try:
            await db.execute(
                text("INSERT INTO session_metadata (user_id, session_id, device_model, connection_type, created_at) VALUES (:u, :s, :d, :n, :c)"),
                {"u": user_id, "s": session_id, "d": device, "n": network, "c": datetime.now(timezone.utc)}
            )
            await db.commit()
        except Exception as e:
            print(f"Metadata logging failed: {e}")

async def log_event(user_id: str, session_id: str, event_type: str, response: str, turn_number: int):
    async with SessionLocal() as db:
        try:
            await db.execute(
                text("INSERT INTO user_events (user_id, session_id, event_type, response, turn_number, created_at) VALUES (:u, :s, :e, :r, :t, :c)"),
                {"u": user_id, "s": session_id, "e": event_type, "r": response, "t": turn_number, "c": datetime.now(timezone.utc)}
            )
            await db.commit()
        except Exception as e:
            print("Event logging failed:", e)

async def log_system_error(user_id: str, session_id: str, function_name: str, error_msg: str, error_type: str, payload: dict | None = None):
    async with SessionLocal() as db:
        try:
            await db.execute(
                text("INSERT INTO system_errors (user_id, session_id, function_name, error_message, error_type, error_payload, created_at) VALUES (:u, :s, :f, :m, :et, :p, :c)"),
                {"u": user_id, "s": session_id, "f": function_name, "m": error_msg, "et": error_type, "p": json.dumps(payload or {}), "c": datetime.now(timezone.utc)}
            )
            await db.commit()
        except Exception as e:
            print(f"CRITICAL: Logging failed: {e}")

async def load_polygons(road_name: str):
    async with SessionLocal() as db:
        result = await db.execute(
            text("SELECT geometry FROM avoid_road_polygons WHERE road_name = :r LIMIT 1"),
            {"r": road_name.lower()}
        )
        row = result.fetchone()
        if not row:
            return None
        geom_hex = row[0]
        geom = wkb.loads(bytes.fromhex(geom_hex))
        if geom.geom_type == 'Polygon':
            return MultiPolygon([geom])
        return geom

async def store_polygons(road_name: str, multi_poly: MultiPolygon):
    async with SessionLocal() as db:
        geom_hex = wkb.dumps(multi_poly, hex=True)
        await db.execute(
            text("""
            INSERT INTO avoid_road_polygons (road_name, geometry) VALUES (:r, :g)
            ON CONFLICT (road_name) DO UPDATE SET geometry = :g
            """),
            {"r": road_name.lower(), "g": geom_hex}
        )
        await db.commit()

async def load_saved_places(user_id: str):
    async with SessionLocal() as db:
        try:
            result = await db.execute(
                text("SELECT label, latitude, longitude FROM places WHERE user_id = :u"),
                {"u": user_id}
            )
            return {
                row[0].lower(): {"lat": row[1], "lng": row[2]}
                for row in result.fetchall()
            }
        except Exception as e:
            print(f"Error fetching labels: {e}")
            return {}

async def store_place(user_id: str, label: str, latitude: float, longitude: float):
    async with SessionLocal() as db:
        await db.execute(
            text("""
            INSERT INTO places (user_id, label, latitude, longitude) VALUES (:u, :l, :lat, :lng)
            ON CONFLICT (user_id, label) DO UPDATE SET latitude = :lat, longitude = :lng
            """),
            {"u": user_id, "l": label.lower(), "lat": latitude, "lng": longitude}
        )
        await db.commit()

async def load_most_used_item(table_name: str, select_field: str, user_id: str, destination_label: str, min_usage: int = 2):
    async with SessionLocal() as db:
        result = await db.execute(
            text(f"SELECT {select_field}, usage_count FROM {table_name} WHERE user_id = :u AND destination_label = :d"),
            {"u": user_id, "d": destination_label.lower()}
        )
        rows = result.fetchall()
        if not rows:
            return None
        max_count = max(r[1] for r in rows)
        if max_count < min_usage:
            return None
        top = [r for r in rows if r[1] == max_count]
        if len(top) != 1:
            return None
        return top[0][0]

async def increment_usage(table_name: str, key_field: str, key_value: str, user_id: str, destination_label: str):
    destination_label = destination_label.lower()
    async with SessionLocal() as db:
        result = await db.execute(
            text(f"SELECT usage_count FROM {table_name} WHERE user_id = :u AND destination_label = :d AND {key_field} = :k LIMIT 1"),
            {"u": user_id, "d": destination_label, "k": key_value}
        )
        existing = result.fetchone()
        if existing:
            await db.execute(
                text(f"UPDATE {table_name} SET usage_count = usage_count + 1, last_used = NOW() WHERE user_id = :u AND destination_label = :d AND {key_field} = :k"),
                {"u": user_id, "d": destination_label, "k": key_value}
            )
        else:
            await db.execute(
                text(f"INSERT INTO {table_name} (user_id, destination_label, {key_field}, usage_count, last_used) VALUES (:u, :d, :k, 1, NOW())"),
                {"u": user_id, "d": destination_label, "k": key_value}
            )
        await db.commit()

async def load_most_used_road(user_id: str, destination_label: str):
    return await load_most_used_item("route_familiarity", "major_road", user_id, destination_label)

async def store_route_familiarity(user_id: str, destination_label: str, major_road: str):
    await increment_usage("route_familiarity", "major_road", major_road, user_id, destination_label)

async def load_most_avoided_road(user_id: str, destination_label: str):
    return await load_most_used_item("route_avoidance", "avoided_road", user_id, destination_label)

async def store_route_avoidance(user_id: str, destination_label: str, avoided_road: str):
    await increment_usage("route_avoidance", "avoided_road", avoided_road, user_id, destination_label)

async def load_most_preferred_option(user_id: str, destination_label: str):
    return await load_most_used_item("route_option_preference", "route_option", user_id, destination_label)

async def store_route_option_preference(user_id: str, destination_label: str, route_option: str):
    await increment_usage("route_option_preference", "route_option", route_option, user_id, destination_label)

async def store_trip(user_id: str, origin_coords: any, destination_coords: any, via_road_name: str, route_option: str, avoid_roads: list = None, avoid_features: list = None, origin_name: str = None, destination_name: str = None):
    def format_coords(c):
        if isinstance(c, dict):
            return [c.get("lat"), c.get("lng")]
        return c
    async with SessionLocal() as db:
        try:
            await db.execute(
                text("""
                INSERT INTO trip_history (user_id, origin_coords, destination_coords, origin_name, destination_name, via_road_name, route_option, avoid_roads, avoid_features, created_at)
                VALUES (:u, :oc, :dc, :on, :dn, :v, :ro, :ar, :af, :c)
                """),
                {
                    "u": user_id, "oc": json.dumps(format_coords(origin_coords)), "dc": json.dumps(format_coords(destination_coords)),
                    "on": origin_name, "dn": destination_name, "v": via_road_name, "ro": route_option,
                    "ar": json.dumps(avoid_roads or []), "af": json.dumps(avoid_features or []), "c": datetime.now(timezone.utc)
                }
            )
            await db.commit()
        except Exception as e:
            print(f"Error storing trip: {e}")

async def load_trip_history(user_id: str, limit: int = 10):
    async with SessionLocal() as db:
        try:
            result = await db.execute(
                text("SELECT * FROM trip_history WHERE user_id = :u ORDER BY created_at DESC LIMIT :l"),
                {"u": user_id, "l": limit}
            )
            return [dict(row._mapping) for row in result.fetchall()]
        except Exception as e:
            print(f"Error loading trips: {e}")
            return []
