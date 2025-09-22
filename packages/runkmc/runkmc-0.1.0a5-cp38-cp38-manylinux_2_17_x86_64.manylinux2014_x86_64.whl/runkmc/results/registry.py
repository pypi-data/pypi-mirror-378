from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime
import uuid

import numpy as np
import pandas as pd

from runkmc.results.paths import SimulationPaths


def compare_values(v1: Any, v2: Any, rtol: float = 1e-5) -> bool:
    """Compare two values with relative tolerance for floats"""
    if isinstance(v1, (int, float)) and isinstance(v2, (int, float)):
        return np.isclose(v1, v2, rtol=rtol, atol=0)
    return v1 == v2


class SimulationRegistry:

    def __init__(self, model_name: str, base_dir: Path | str):
        self.model_name = model_name
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)

        self.registry_path = self.base_dir / "registry.csv"

    def get_registry(self) -> pd.DataFrame:
        """Load the simulation registry from a CSV file"""
        if not self.registry_path.exists():
            return pd.DataFrame()
        try:
            return pd.read_csv(self.registry_path)
        except Exception as e:
            print(f"Error loading registry: {e}")
            return pd.DataFrame()

    def save_registry(self, df: pd.DataFrame) -> None:
        """Save the simulation registry to a CSV file"""
        df.to_csv(self.registry_path, index=False)

    def register_simulation(
        self, params: Dict[str, Any], sim_id: Optional[str] = None
    ) -> SimulationPaths:

        if sim_id is None:
            sim_id = f"sim_{uuid.uuid4()}"
        else:
            self.delete_by_id(sim_id)

        registry_df = self.get_registry()

        new_entry = {
            "id": sim_id,
            "timestamp": datetime.now().isoformat(),
        }
        new_entry.update(params)

        registry_df = pd.concat(
            [registry_df, pd.DataFrame([new_entry])], ignore_index=True
        )
        self.save_registry(registry_df)

        paths = SimulationPaths(self.base_dir, sim_id)
        return paths

    def _matches_params(self, row: pd.Series, search_params: Dict[str, Any]) -> bool:

        for key, value in search_params.items():

            if key not in row:
                return False
            if not compare_values(row[key], value):
                return False
        return True

    def find(
        self, params: Dict[str, Any], valid_only: bool = True
    ) -> List[SimulationPaths]:

        registry_df = self.get_registry()
        if registry_df.empty:
            return []

        all_paths = []
        for _, row in registry_df.iterrows():

            if not self._matches_params(row, params):
                continue

            sim_id = row["id"]
            paths = SimulationPaths(self.base_dir, sim_id)

            if valid_only and not paths.has_results():
                continue

            all_paths.append(paths)

        return all_paths

    def find_by_id(self, sim_id: str) -> Optional[SimulationPaths]:
        """Find a simulation by its ID"""

        registry_df = self.get_registry()

        matching_rows = registry_df[registry_df["id"] == sim_id]
        if matching_rows.empty:
            return None

        paths = SimulationPaths(self.base_dir, sim_id)
        if not paths.exists():
            return None

        return paths

    def _get_latest_sim_id(
        self, params: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:

        registry_df = self.get_registry()
        if registry_df.empty:
            return None

        registry_df["timestamp"] = pd.to_datetime(registry_df["timestamp"])
        registry_df = registry_df.sort_values(by="timestamp", ascending=False)
        if params:
            for _, row in registry_df.iterrows():
                if self._matches_params(row, params):
                    return row["id"]
            return None
        else:
            return registry_df.iloc[0]["id"]

    def get_latest(
        self, params: Optional[Dict[str, Any]] = None
    ) -> Optional[SimulationPaths]:
        """
        Get the latest simulation that matches the given parameters.
        If no parameters are provided, return the latest simulation.
        """

        sim_id = self._get_latest_sim_id(params)
        if sim_id is None:
            return None

        paths = SimulationPaths(self.base_dir, sim_id)
        if not paths.exists():
            return None

        return paths

    def delete_by_id(self, sim_id: str) -> bool:
        """
        Delete a simulation by its ID.
        Returns True if the simulation was deleted, False if it didn't exist.
        """

        paths = SimulationPaths(self.base_dir, sim_id)
        if not paths.exists():
            return False

        paths.delete_data()

        registry_df = self.get_registry()
        registry_df = registry_df[registry_df["id"] != sim_id].reset_index(drop=True)
        self.save_registry(registry_df)

        return True

    def delete_latest(self, params: Optional[Dict[str, Any]] = None) -> bool:
        """
        Delete the latest simulation that matches the given parameters.
        If no parameters are provided, delete the latest simulation.
        """

        sim_id = self._get_latest_sim_id(params)
        return self.delete_by_id(sim_id) if sim_id else False

    def clear_registry(self, delete_files: bool = True) -> None:

        registry_df = self.get_registry()

        if delete_files and not registry_df.empty:
            for _, row in registry_df.iterrows():
                sim_id = row["id"]
                paths = SimulationPaths(self.base_dir, sim_id)
                paths.delete_data()

        self.save_registry(pd.DataFrame())
