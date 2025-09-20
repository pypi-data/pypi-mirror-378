"""
Metrics collector that captures Pipecat's built-in metrics and sends them to backend.
Leverages existing TTFB, processing time, and token usage metrics.
"""

import asyncio
import json
import statistics
import time
from collections import defaultdict
from typing import Dict, List, Optional, Any
import aiohttp
from loguru import logger
from env_config import api_config

from pipecat.frames.frames import Frame, MetricsFrame
from pipecat.metrics.metrics import (
    TTFBMetricsData
)
from pipecat.observers.base_observer import BaseObserver, FramePushed


class CallMetricsCollector(BaseObserver):
    """
    Observes and collects metrics from Pipecat's built-in metrics system.
    Aggregates TTFB and TTFT metrics for TTS, STT, and LLM services per call.
    """
    
    def __init__(self, call_id: str):
        super().__init__()
        self.call_id = call_id
        self.ttfb_metrics: Dict[str, List] = defaultdict(list)
        self.processed_metrics: set = set()
        self.first_tts_time: Optional[float] = None
        self.call_start_time = time.time()
    
    async def on_push_frame(self, data: FramePushed):
        """Process incoming frames and extract metrics data."""
        # Only process MetricsFrames
        if not isinstance(data.frame, MetricsFrame):
            return
            
        try:
            for metric in data.frame.data:
                await self._process_metric(metric)
        except Exception as e:
            logger.error(f"Error processing metrics frame: {e}", call_id=self.call_id)
    
    async def _process_metric(self, metric):
        """Process individual metric data."""
        processor_name = getattr(metric, 'processor', 'unknown')
        
        rounded_value = round(metric.value, 6) if hasattr(metric, 'value') else 0
        metric_id = f"{type(metric).__name__}_{processor_name}_{rounded_value}"
        
        # Skip if we've already processed this exact metric
        if metric_id in self.processed_metrics:
            return
        
        self.processed_metrics.add(metric_id)
        
        # Cleanup old metric IDs to prevent memory bloat
        if len(self.processed_metrics) > 500:
            # Convert to list, remove first 100 entries, convert back to set
            metrics_list = list(self.processed_metrics)
            self.processed_metrics = set(metrics_list[100:])
        
        if isinstance(metric, TTFBMetricsData):
            # Time To First Byte metrics - filter out initialization zeros
            if metric.value > 0.0:  # Only track real metrics, skip startup zeros
                service_type = self._extract_service_type(processor_name)
                self.ttfb_metrics[service_type].append(metric.value)
                
                # Capture first TTS occurrence
                if service_type == 'tts' and self.first_tts_time is None:
                    self.first_tts_time = time.time() - self.call_start_time
                    logger.debug(f"First TTS occurred at: {self.first_tts_time:.3f}s", call_id=self.call_id)
                    
                # Use appropriate logging: TTFT for LLM, TTFB for others
                # metric_label = "TTFT" if service_type == 'llm' else "TTFB"
                # logger.debug(f"{metric_label} {service_type}: {metric.value:.3f}s", call_id=self.call_id)
            
    
    def _extract_service_type(self, processor_name: str) -> str:
        """Extract service type from processor name."""
        processor_lower = processor_name.lower()
        
        # Check for generic service patterns 
        if 'sttservice' in processor_lower:
            return 'stt'
        elif 'ttsservice' in processor_lower:
            return 'tts'
        elif 'llmservice' in processor_lower:
            return 'llm'
        else:
            logger.debug(f"No pattern matched in '{processor_lower}' -> returning 'unknown'", call_id=self.call_id)
            return 'unknown'
    
    def get_aggregated_metrics(self) -> Dict[str, Any]:
        """Calculate aggregated metrics for all services."""
        metrics = {}
        
        for service_type, values in self.ttfb_metrics.items():
            if values:
                values_list = list(values)
                metric_name = f'{service_type}_ttft' if service_type == 'llm' else f'{service_type}_ttfb'
                metrics[metric_name] = {
                    'min': round(min(values_list), 6),
                    'max': round(max(values_list), 6),
                    'median': round(statistics.median(values_list), 6),
                }
        
        # Add first TTS occurrence time if captured
        if self.first_tts_time is not None:
            metrics['first_tts_time'] = round(self.first_tts_time, 6)
        
        return metrics
    


# Global metrics collector for current call
_current_metrics_collector: Optional[CallMetricsCollector] = None


def create_metrics_collector(call_id: str) -> CallMetricsCollector:
    """Create a new metrics collector for a call."""
    global _current_metrics_collector
    _current_metrics_collector = CallMetricsCollector(call_id=call_id)
    return _current_metrics_collector


def get_metrics_collector() -> Optional[CallMetricsCollector]:
    """Get the current metrics collector."""
    return _current_metrics_collector


def clear_metrics_collector():
    """Clear the current metrics collector."""
    global _current_metrics_collector
    _current_metrics_collector = None