from typing import Any

from app.modules.job.models import Job

from .base_adapter import JobAdapterBase

from .itjobs_adapter import adapter_itjobs
from .itviec_adapter import adapter_itviec
from .topdev_adapter import adapter_topdev


class JobAdapter:
    @staticmethod
    def calculate_content_hash(
        title: str, company_name: str, description: str, location: str
    ) -> str:
        return JobAdapterBase.calculate_content_hash(
            title, company_name, description, location
        )

    @staticmethod
    def adapter_itjobs(raw_data: dict[str, Any]) -> Job:
        return adapter_itjobs(raw_data)

    @staticmethod
    def adapter_itviec(raw_data: dict[str, Any]) -> Job:
        return adapter_itviec(raw_data)

    @staticmethod
    def adapter_topdev(raw_data: dict[str, Any]) -> Job:
        return adapter_topdev(raw_data)

    @staticmethod
    def to_job(raw_data: dict[str, Any], source: str) -> Job:
        source_lower = source.lower().strip()
        if source_lower == "itjobs":
            return adapter_itjobs(raw_data)
        if source_lower == "itviec":
            return adapter_itviec(raw_data)
        elif source_lower == "topdev":
            return adapter_topdev(raw_data)
        else:
            raise ValueError(f"Unknown crawler source: {source}")
