# ==============================================================================
# Copyright (c) 2026 Hüseyin Üstündağ | HUMAN — AIOps & Critical Systems
# All Rights Reserved. Unauthorized copying, commercial deployment, or 
# modification of this file, via any medium, is strictly prohibited.
# ==============================================================================

import requests
from pydantic import BaseModel, Field
from typing import Optional

class RackTelemetryPayload(BaseModel):
    rack_id: str
    inlet_temp_c: float = Field(..., ge=0, le=60)
    exhaust_temp_c: float = Field(..., ge=0, le=95)
    avg_fan_rpm_pct: float = Field(..., ge=0, le=100)
    power_draw_watts: float = Field(..., ge=0)

    @property
    def delta_t(self) -> float:
        return round(self.exhaust_temp_c - self.inlet_temp_c, 2)

class RedfishTelemetryCollector:
    """
    DMTF Redfish API standardına uygun BMC (iDRAC / iLO / XClarity)
    termal ve güç telemetri toplayıcısı.
    """
    def __init__(self, bmc_host: str, username: str, password: str, verify_ssl: bool = False):
        self.base_url = f"https://{bmc_host}/redfish/v1"
        self.auth = (username, password)
        self.verify_ssl = verify_ssl

    def fetch_thermal_metrics(self, chassis_id: str = "System.Embedded.1") -> Optional[dict]:
        endpoint = f"{self.base_url}/Chassis/{chassis_id}/Thermal"
        try:
            response = requests.get(endpoint, auth=self.auth, verify=self.verify_ssl, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            return {"error": f"Redfish bağlantı hatası ({endpoint}): {exc}"}
