"""Worker service: end-to-end inference pipeline that posts events to the API.

The worker reads a video (file path or RTSP URL), runs detection + tracking +
rule engine, and POSTs the resulting violation events to the deployed API via
``POST /events/batch``. Designed to live on a host with GPU/CPU + camera
access while the API stays slim and stateless.
"""
